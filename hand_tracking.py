import cv2
import mediapipe as mp
from mediapipe import tasks
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import math
import numpy as np

class HandTracker:
    def __init__(self):
        # Download the model if needed
        import urllib.request
        import os
        
        model_path = 'hand_landmarker.task'
        if not os.path.exists(model_path):
            url = 'https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task'
            print("Downloading hand landmarker model...")
            urllib.request.urlretrieve(url, model_path)
            print("Model downloaded successfully!")
        
        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=1,
            min_hand_detection_confidence=0.5,
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.detector = vision.HandLandmarker.create_from_options(options)
        self.prev_distance = None
        self.results = None
        
    def findHands(self, img, draw=True):
        # Convert BGR to RGB
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)
        
        # Detect hands
        self.results = self.detector.detect(mp_image)
        
        # Draw landmarks
        if self.results.hand_landmarks and draw:
            for hand_landmarks in self.results.hand_landmarks:
                # Draw connections
                connections = [
                    (0, 1), (1, 2), (2, 3), (3, 4),  # Thumb
                    (0, 5), (5, 6), (6, 7), (7, 8),  # Index
                    (0, 9), (9, 10), (10, 11), (11, 12),  # Middle
                    (0, 13), (13, 14), (14, 15), (15, 16),  # Ring
                    (0, 17), (17, 18), (18, 19), (19, 20),  # Pinky
                    (5, 9), (9, 13), (13, 17)  # Palm
                ]
                
                h, w, c = img.shape
                for connection in connections:
                    start_idx, end_idx = connection
                    if start_idx < len(hand_landmarks) and end_idx < len(hand_landmarks):
                        start = hand_landmarks[start_idx]
                        end = hand_landmarks[end_idx]
                        cv2.line(img, 
                                (int(start.x * w), int(start.y * h)),
                                (int(end.x * w), int(end.y * h)),
                                (0, 255, 0), 2)
                
                # Draw landmarks
                for landmark in hand_landmarks:
                    cx, cy = int(landmark.x * w), int(landmark.y * h)
                    cv2.circle(img, (cx, cy), 5, (255, 0, 255), cv2.FILLED)
        
        return img
    
    def getPosition(self, img, hand_no=0):
        """Get landmark positions for the specified hand"""
        lm_list = []
        if self.results and self.results.hand_landmarks:
            if len(self.results.hand_landmarks) > hand_no:
                hand = self.results.hand_landmarks[hand_no]
                h, w, c = img.shape
                for id, lm in enumerate(hand):
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lm_list.append([id, cx, cy])
        return lm_list
    
    def fingersUp(self, lm_list):
        """Detect which fingers are up"""
        if len(lm_list) == 0:
            return []
        
        fingers = []
        tip_ids = [4, 8, 12, 16, 20]
        
        # Thumb - check x-axis
        if lm_list[tip_ids[0]][1] > lm_list[tip_ids[0] - 1][1]:
            fingers.append(1)
        else:
            fingers.append(0)
        
        # Other fingers - check y-axis
        for id in range(1, 5):
            if lm_list[tip_ids[id]][2] < lm_list[tip_ids[id] - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)
        
        return fingers
    
    def getDistance(self, p1, p2, lm_list):
        """Calculate distance between two landmarks"""
        if len(lm_list) < max(p1, p2) + 1:
            return 0, None, None
        
        x1, y1 = lm_list[p1][1], lm_list[p1][2]
        x2, y2 = lm_list[p2][1], lm_list[p2][2]
        
        distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        return distance, (x1, y1), (x2, y2)
    
    def getGesture(self, img):
        """
        Detect hand gestures and return:
        - cursor position (index finger tip)
        - gesture type: 'move', 'left_click', 'right_click', 'zoom_in', 'zoom_out'
        """
        img = self.findHands(img)
        lm_list = self.getPosition(img)
        
        if len(lm_list) == 0:
            return None
        
        fingers = self.fingersUp(lm_list)
        
        # Get index finger tip position for cursor
        index_x, index_y = lm_list[8][1], lm_list[8][2]
        
        # Get distance between thumb and index for click detection
        thumb_index_dist, p1, p2 = self.getDistance(4, 8, lm_list)
        
        # Draw cursor
        cv2.circle(img, (index_x, index_y), 15, (255, 0, 255), cv2.FILLED)
        
        gesture_info = {
            'x': index_x,
            'y': index_y,
            'gesture': 'move'
        }
        
        # Gesture detection logic
        # Index finger up only - Move cursor
        if fingers == [0, 1, 0, 0, 0]:
            gesture_info['gesture'] = 'move'
            cv2.putText(img, "Move", (10, 50), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)
        
        # Index and thumb - Left click mode (pinch to click)
        elif fingers == [1, 1, 0, 0, 0]:
            if thumb_index_dist < 40:
                gesture_info['gesture'] = 'left_click'
                cv2.putText(img, "Left Click", (10, 50), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)
                if p1 and p2:
                    cv2.line(img, p1, p2, (0, 0, 255), 3)
            else:
                gesture_info['gesture'] = 'move'
                cv2.putText(img, "Move", (10, 50), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)
        
        # All fingers up - Zoom detection
        elif fingers == [1, 1, 1, 1, 1]:
            # Calculate distance between thumb and pinky for zoom
            thumb_pinky_dist, _, _ = self.getDistance(4, 20, lm_list)
            
            if self.prev_distance is None:
                self.prev_distance = thumb_pinky_dist
            else:
                diff = thumb_pinky_dist - self.prev_distance
                if abs(diff) > 10:  # Increased threshold for more deliberate gestures
                    if diff > 0:
                        gesture_info['gesture'] = 'zoom_in'
                        cv2.putText(img, "Zoom In", (10, 50), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 0), 2)
                    else:
                        gesture_info['gesture'] = 'zoom_out'
                        cv2.putText(img, "Zoom Out", (10, 50), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 0), 2)
                    self.prev_distance = thumb_pinky_dist
        
        # Index, middle, and ring fingers up - Right click
        elif fingers == [0, 1, 1, 1, 0] or fingers == [1, 1, 1, 0, 0]:
            gesture_info['gesture'] = 'right_click'
            cv2.putText(img, "Right Click", (10, 50), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)
            self.prev_distance = None
        
        else:
            self.prev_distance = None
        
        return gesture_info

