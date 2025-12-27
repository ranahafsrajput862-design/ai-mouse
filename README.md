# ✋ AI Hand Mouse Controller

Control your computer mouse using hand gestures through your webcam! No physical mouse needed - just use your hand movements to navigate, click, and zoom.

![Python](https://img.shields.io/badge/python-3.7+-blue.svg)
![Flask](https://img.shields.io/badge/flask-2.0+-green.svg)
![OpenCV](https://img.shields.io/badge/opencv-4.0+-red.svg)
![MediaPipe](https://img.shields.io/badge/mediapipe-latest-orange.svg)

## 🌟 Features

- **Real-time Hand Tracking** - Uses Google MediaPipe for accurate hand detection
- **Mouse Movement** - Control cursor with index finger pointing
- **Left Click** - Pinch thumb and index finger together
- **Right Click** - Show three fingers (index, middle, ring)
- **Zoom In/Out** - Spread all fingers wide or bring them together
- **Beautiful UI** - Modern, animated interface with glass-morphism design
- **Privacy First** - All processing happens locally on your device

## 🎮 Hand Gestures

| Gesture | Action | How to Perform |
|---------|--------|----------------|
| 👆 **Move** | Control cursor position | Point with index finger only |
| 🤏 **Left Click** | Perform left mouse click | Thumb + index finger up, then pinch together |
| ✌️ **Right Click** | Perform right mouse click | Show index, middle, and ring fingers together |
| ✋ **Zoom In** | Zoom into content | Spread all 5 fingers wide apart |
| ✋ **Zoom Out** | Zoom out of content | Bring all 5 fingers closer together |

## 📋 Prerequisites

- Python 3.7 or higher
- Webcam
- Windows/Mac/Linux operating system

## 🚀 Installation

### 1. Clone or Download the Repository

```bash
cd ai-mouse-main
```

### 2. Install Required Packages

```bash
pip install -r requirements.txt
```

The required packages are:
- Flask - Web framework
- opencv-python - Computer vision
- mediapipe - Hand tracking
- pyautogui - Mouse control
- numpy - Numerical computations

### 3. Verify Installation

Check if all packages are installed correctly:

```bash
python -c "import flask, cv2, mediapipe, pyautogui, numpy; print('All packages installed successfully!')"
```

## 🎯 Usage

### Starting the Application

1. **Run the application:**

```bash
python app.py
```

2. **Open your web browser and navigate to:**

```
http://localhost:5000
```

3. **Allow camera access when prompted**

4. **Position your hand in front of the camera**
   - Keep hand 1-2 feet away from camera
   - Ensure good lighting
   - Use a clean background for better detection

5. **Start controlling!**
   - The purple box shows the tracking area
   - Green lines show your hand skeleton
   - Text on screen shows the current gesture

### Stopping the Application

Press `Ctrl + C` in the terminal where the app is running.

## 💡 Tips for Best Results

- ✅ **Good Lighting** - Ensure your hand is well-lit
- ✅ **Distance** - Keep hand 1-2 feet from camera
- ✅ **Clear Background** - Solid color backgrounds work best
- ✅ **Stable Position** - Keep camera stable for better tracking
- ✅ **Practice** - Try different gestures to get comfortable

## 🛠️ Troubleshooting

### Camera Not Opening

```bash
# Try specifying camera index
# Edit app.py, line 27:
cap = cv2.VideoCapture(0)  # Try changing 0 to 1 or 2
```

### Hand Not Detected

- Check lighting conditions
- Move hand closer to camera
- Ensure hand is fully visible
- Try different hand positions

### Mouse Not Moving

1. Check if "Mouse Control" toggle is enabled on the interface
2. Verify PyAutoGUI permissions on your system
3. On macOS, grant accessibility permissions in System Preferences

### Port Already in Use

```bash
# Change port in app.py, last line:
app.run(debug=False, host='0.0.0.0', port=5001)  # Use different port
```

## 📁 Project Structure

```
ai-mouse-main/
├── app.py                    # Main Flask application
├── hand_tracking.py          # Hand detection and gesture recognition
├── controller.py             # Mouse control logic
├── color_tracking.py         # Legacy color tracking (not used)
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── templates/
│   └── index.html           # Web interface
└── hand_landmarker.task     # MediaPipe model (auto-downloaded)
```

## 🔧 Configuration

### Adjusting Sensitivity

Edit `hand_tracking.py` to adjust gesture detection:

```python
# Line 171 - Pinch distance for left click
if thumb_index_dist < 40:  # Decrease for tighter pinch, increase for looser

# Line 189 - Zoom sensitivity
if abs(diff) > 10:  # Increase for less sensitivity, decrease for more
```

### Changing Screen Resolution

Edit `app.py`:

```python
# Lines 11-12
wCam, hCam = 640, 480  # Change to your preferred resolution
```

## 🎨 Features

- **Modern UI** with animated gradients and glass-morphism effects
- **Real-time gesture feedback** displayed on video
- **Smooth mouse movement** with interpolation
- **Click cooldown** to prevent accidental double-clicks
- **Responsive design** works on desktop and mobile browsers

## 🔒 Privacy & Security

- All processing happens **locally on your device**
- No video data is sent to any external servers
- Camera feed is only processed in real-time
- No data is stored or recorded

## 🤝 Contributing

Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests
- Improve documentation

## 📝 License

This project is open source and available for educational purposes.

## 🙏 Acknowledgments

- **Google MediaPipe** - Hand tracking technology
- **OpenCV** - Computer vision library
- **Flask** - Web framework

## 📧 Support

If you encounter any issues:
1. Check the troubleshooting section above
2. Ensure all dependencies are installed correctly
3. Verify your camera is working properly
4. Check Python version compatibility

---

**Made with ✋ and ❤️**

Enjoy controlling your computer with hand gestures! 🎉
