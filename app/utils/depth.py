"""Depth estimation using MiDaS or simple stereo methods."""

import cv2
import numpy as np
from typing import Optional
# import torch
# import torch.nn.functional as F

class DepthEstimator:
    """Depth estimation using MiDaS model."""
    
    def __init__(self):
        self.model = None
        self.transform = None
        print("DepthEstimator initialized with fallback method")
    
    def _load_model(self):
        """Load MiDaS model (disabled for minimal version)."""
        print("Using fallback depth estimation (MiDaS disabled)")
        self.model = None
    
    def estimate_depth(self, frame: np.ndarray) -> np.ndarray:
        """Returns normalized depth map."""
        if self.model is not None:
            return self._midas_depth(frame)
        else:
            return self._fallback_depth(frame)
    
    def _midas_depth(self, frame: np.ndarray) -> np.ndarray:
        """MiDaS depth estimation (disabled)."""
        return self._fallback_depth(frame)
    
    def _fallback_depth(self, frame: np.ndarray) -> np.ndarray:
        """Simple depth estimation using edge density."""
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        
        # Use Sobel edges as depth proxy
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        edges = np.sqrt(sobelx**2 + sobely**2)
        
        # Blur and normalize
        depth = cv2.GaussianBlur(edges, (15, 15), 0)
        depth = (depth - depth.min()) / (depth.max() - depth.min() + 1e-8)
        
        # Invert so closer objects have higher values
        return 1.0 - depth

def estimate_depth(frame: np.ndarray) -> np.ndarray:
    """Standalone function for depth estimation."""
    estimator = DepthEstimator()
    return estimator.estimate_depth(frame)