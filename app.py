from flask import Flask, render_template, Response, request, jsonify
import base64
import cv2
import numpy as np
import hand_tracking as ht
import controller as mc
import os

app = Flask(__name__)

wCam, hCam = 640, 480
frameR = 100

tracker = ht.HandTracker()
screen_w, screen_h = 800, 600
try:
    import pyautogui
    screen_w, screen_h = pyautogui.size()[0], pyautogui.size()[1]
except Exception:
    pass

mouse = mc.MouseController(screen_w, screen_h, frameR)

VIDEO_SOURCE = os.environ.get('VIDEO_SOURCE', 'server')
cap = None
if VIDEO_SOURCE == 'server':
    print("Initializing camera...")
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # Use DirectShow on Windows for faster initialization
    if cap.isOpened():
        cap.set(3, wCam)
        cap.set(4, hCam)
        print("Camera initialized successfully!")
    else:
        print("Warning: Could not open camera")

perform_mouse = os.environ.get('PERFORM_MOUSE', 'true').lower() in ('1', 'true', 'yes')

# Gesture state tracking
prev_gesture = None
click_cooldown = 0
current_hand_data = {'found': False, 'cx': 0, 'cy': 0, 'gesture': 'none'}


def generate_frames():
    global prev_gesture, click_cooldown, current_hand_data
    
    while True:
        if cap is None:
            img = np.zeros((hCam, wCam, 3), dtype=np.uint8)
        else:
            success, img = cap.read()
            if not success:
                break
            img = cv2.flip(img, 1)

        # Draw frame boundary
        cv2.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR), (255, 0, 255), 2)
        
        # Get hand gesture
        gesture_info = tracker.getGesture(img)
        
        if gesture_info is not None:
            cx, cy = gesture_info['x'], gesture_info['y']
            gesture = gesture_info['gesture']
            
            # Update current hand data for frontend
            current_hand_data = {
                'found': True,
                'cx': int(cx),
                'cy': int(cy),
                'gesture': gesture,
                'width': wCam,
                'height': hCam
            }
            
            if perform_mouse:
                # Always move mouse
                mouse.move_mouse(cx, cy, wCam, hCam)
                
                # Handle click cooldown
                if click_cooldown > 0:
                    click_cooldown -= 1
                
                # Handle gestures
                if gesture == 'left_click' and click_cooldown == 0:
                    mouse.click('left')
                    click_cooldown = 15  # Prevent multiple clicks
                    
                elif gesture == 'right_click' and click_cooldown == 0:
                    mouse.click('right')
                    click_cooldown = 15
                    
                elif gesture == 'zoom_in':
                    mouse.zoom('in')
                    
                elif gesture == 'zoom_out':
                    mouse.zoom('out')
                
                prev_gesture = gesture
        else:
            current_hand_data = {'found': False, 'cx': 0, 'cy': 0, 'gesture': 'none'}
        
        ret, buffer = cv2.imencode('.jpg', img)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/')
def index():
    response = app.make_response(render_template('index.html'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/frame', methods=['POST'])
def frame():
    global prev_gesture, click_cooldown
    
    try:
        data = request.get_data()
        nparr = np.frombuffer(data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            return jsonify({'error': 'could not decode image'}), 400

        img = cv2.flip(img, 1)
        
        gesture_info = tracker.getGesture(img)
        if gesture_info is None:
            return jsonify({'found': False})
            
        cx, cy = gesture_info['x'], gesture_info['y']
        gesture = gesture_info['gesture']

        try:
            ih, iw = img.shape[:2]
            if perform_mouse:
                mouse.move_mouse(cx, cy, iw, ih)
                
                if click_cooldown > 0:
                    click_cooldown -= 1
                
                if gesture == 'left_click' and click_cooldown == 0:
                    mouse.click('left')
                    click_cooldown = 15
                    
                elif gesture == 'right_click' and click_cooldown == 0:
                    mouse.click('right')
                    click_cooldown = 15
                    
                elif gesture == 'zoom_in' and prev_gesture != 'zoom_in':
                    mouse.zoom('in')
                    
                elif gesture == 'zoom_out' and prev_gesture != 'zoom_out':
                    mouse.zoom('out')
                
                prev_gesture = gesture
        except Exception:
            pass

        return jsonify({
            'found': True, 
            'cx': int(cx), 
            'cy': int(cy), 
            'gesture': gesture
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/set_mouse', methods=['POST'])
def set_mouse():
    global perform_mouse
    try:
        js = request.get_json(force=True)
        perform_mouse = bool(js.get('perform', False))
        return jsonify({'ok': True, 'perform': perform_mouse})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 400


@app.route('/set_hsv', methods=['POST'])
def set_hsv():
    # This endpoint is no longer needed for hand tracking but kept for compatibility
    return jsonify({'ok': True, 'message': 'Hand tracking mode - HSV not applicable'})


@app.route('/hand_position', methods=['GET'])
def hand_position():
    """Returns current hand position and gesture for web UI interaction"""
    return jsonify(current_hand_data)


if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=5000)
