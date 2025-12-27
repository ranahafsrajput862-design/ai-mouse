import cv2
import numpy as np

class ColorTracker:
    def __init__(self):
        self.lower_color = np.array([100, 50, 50])
        self.upper_color = np.array([130, 255, 255])
        self.kernel = np.ones((5, 5), np.uint8)

    def findColor(self, img, draw=True):
        imgHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(imgHSV, self.lower_color, self.upper_color)
        mask = cv2.erode(mask, self.kernel, iterations=1)
        mask = cv2.dilate(mask, self.kernel, iterations=2)
        self.mask = mask
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        maxArea = 0
        bestCnt = None
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > 500:
                if area > maxArea:
                    maxArea = area
                    bestCnt = cnt
                    
        if bestCnt is not None:
            x, y, w, h = cv2.boundingRect(bestCnt)
            cx, cy = x + w // 2, y + h // 2
            if draw:
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.circle(img, (cx, cy), 5, (0, 255, 0), cv2.FILLED)
            return [cx, cy, maxArea]
        return []

    def get_mask(self):
        return self.mask

    def set_hsv(self, hmin, hmax, smin, smax, vmin, vmax):
        hmin = int(max(0, min(179, hmin)))
        hmax = int(max(0, min(179, hmax)))
        smin = int(max(0, min(255, smin)))
        smax = int(max(0, min(255, smax)))
        vmin = int(max(0, min(255, vmin)))
        vmax = int(max(0, min(255, vmax)))
        self.lower_color = np.array([hmin, smin, vmin])
        self.upper_color = np.array([hmax, smax, vmax])
