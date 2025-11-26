"""YOLO object detection for outlets, switches, windows, doors."""

import cv2
import numpy as np
from typing import List, Dict, Any
# from ultralytics import YOLO
# import torch

class ElementDetector:
    """Detects wall elements using YOLO."""
    
    def __init__(self, model_path: str = None):
        self.model = None
        self.class_names = {
            0: "outlet",
            1: "light_switch", 
            2: "window",
            3: "door"
        }
        self._load_model(model_path)
    
    def _load_model(self, model_path: str = None):
        """Load YOLO model (disabled for minimal version)."""
        print("Using fallback detection (YOLO disabled)")
        self.model = None
    
    def detect_elements(self, frame: np.ndarray, confidence: float = 0.5) -> Dict[str, Any]:
        """Detect wall elements in frame."""
        if self.model is None:
            return self._fallback_detection(frame)
        
        try:
            # Run inference
            results = self.model(frame, conf=confidence, verbose=False)
            
            detections = []
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        # Extract box data
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        conf = box.conf[0].cpu().numpy()
                        cls = int(box.cls[0].cpu().numpy())
                        
                        # Map to our classes (if available)
                        class_name = self.class_names.get(cls, f"class_{cls}")
                        
                        detections.append({
                            "class": class_name,
                            "bbox": [int(x1), int(y1), int(x2), int(y2)],
                            "confidence": float(conf),
                            "center": [int((x1 + x2) / 2), int((y1 + y2) / 2)]
                        })
            
            return {
                "detections": detections,
                "total_elements": len(detections)
            }
            
        except Exception as e:
            print(f"YOLO detection error: {e}")
            return self._fallback_detection(frame)
    
    def _fallback_detection(self, frame: np.ndarray) -> Dict[str, Any]:
        """Simple template matching fallback."""
        # Mock detection for demo
        h, w = frame.shape[:2]
        
        # Generate some mock detections
        detections = []
        
        # Mock outlet detection (look for rectangular shapes)
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if 500 < area < 5000:  # Reasonable size for outlets/switches
                x, y, w_box, h_box = cv2.boundingRect(contour)
                aspect_ratio = w_box / h_box
                
                if 0.5 < aspect_ratio < 2.0:  # Square-ish shapes
                    detections.append({
                        "class": "outlet" if area < 2000 else "light_switch",
                        "bbox": [x, y, x + w_box, y + h_box],
                        "confidence": 0.6,
                        "center": [x + w_box // 2, y + h_box // 2]
                    })
        
        return {
            "detections": detections[:5],  # Limit to 5 detections
            "total_elements": len(detections[:5])
        }

def detect_objects(frame: np.ndarray) -> Dict[str, Any]:
    """Standalone function for object detection."""
    detector = ElementDetector()
    return detector.detect_elements(frame)