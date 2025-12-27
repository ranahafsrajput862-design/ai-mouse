import os
import numpy as np

_HAS_PYAUTOGUI = False
try:
    if os.environ.get('DISPLAY'):
        import pyautogui
        _HAS_PYAUTOGUI = True
    else:
        pyautogui = None
except Exception:
    pyautogui = None
    _HAS_PYAUTOGUI = False


class MouseController:
    def __init__(self, screen_w, screen_h, frame_r=100):
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.frame_r = frame_r
        self.plocX, self.plocY = 0, 0
        self.clocX, self.clocY = 0, 0
        self.smoothening = 7
        self.headless = not _HAS_PYAUTOGUI

    def move_mouse(self, x1, y1, w, h):
        x3 = np.interp(x1, (self.frame_r, w - self.frame_r), (0, self.screen_w))
        y3 = np.interp(y1, (self.frame_r, h - self.frame_r), (0, self.screen_h))
        self.clocX = self.plocX + (x3 - self.plocX) / self.smoothening
        self.clocY = self.plocY + (y3 - self.plocY) / self.smoothening

        if not self.headless:
            try:
                pyautogui.moveTo(self.screen_w - self.clocX, self.clocY)
            except Exception:
                pass
        else:
            print(f"[MouseController] headless move to ({int(self.clocX)}, {int(self.clocY)})")

        self.plocX, self.plocY = self.clocX, self.clocY

    def click(self, button='left'):
        if not self.headless:
            try:
                pyautogui.click(button=button)
            except Exception:
                pass
        else:
            print(f"[MouseController] headless {button} click")

    def scroll(self, direction):
        if not self.headless:
            try:
                pyautogui.scroll(direction * 100)
            except Exception:
                pass
        else:
            print(f"[MouseController] headless scroll {direction}")
    
    def zoom(self, zoom_type):
        """Simulate zoom using Ctrl + scroll or Ctrl + +/-"""
        if not self.headless:
            try:
                if zoom_type == 'in':
                    pyautogui.scroll(3)  # Scroll up to zoom in
                else:
                    pyautogui.scroll(-3)  # Scroll down to zoom out
            except Exception:
                pass
        else:
            print(f"[MouseController] headless zoom {zoom_type}")
