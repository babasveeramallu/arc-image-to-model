"""Camera handling for real-time frame capture."""

import cv2
import numpy as np
from typing import Optional, Tuple
import threading
import time

class CameraHandler:
    """Handles camera input with threading for smooth frame capture."""
    
    def __init__(self, camera_id: int = 0, width: int = 640, height: int = 480):
        self.camera_id = camera_id
        self.width = width
        self.height = height
        self.cap: Optional[cv2.VideoCapture] = None
        self.frame: Optional[np.ndarray] = None
        self.running = False
        self.thread: Optional[threading.Thread] = None
        
    def start(self) -> bool:
        """Start camera capture."""
        try:
            self.cap = cv2.VideoCapture(self.camera_id)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            
            if not self.cap.isOpened():
                return False
                
            self.running = True
            self.thread = threading.Thread(target=self._capture_loop)
            self.thread.daemon = True
            self.thread.start()
            return True
            
        except Exception as e:
            print(f"Camera start error: {e}")
            return False
    
    def _capture_loop(self):
        """Continuous frame capture loop."""
        while self.running and self.cap:
            ret, frame = self.cap.read()
            if ret:
                self.frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            time.sleep(0.01)  # ~100 FPS max
    
    def get_frame(self) -> Optional[np.ndarray]:
        """Returns latest RGB frame from camera."""
        return self.frame.copy() if self.frame is not None else None
    
    def stop(self):
        """Stop camera capture."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
        if self.cap:
            self.cap.release()
            
    def __del__(self):
        self.stop()

def get_frame() -> np.ndarray:
    """Simple function to get a single frame (for testing)."""
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()
    
    if ret:
        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    else:
        # Return dummy frame if camera fails
        return np.zeros((480, 640, 3), dtype=np.uint8)