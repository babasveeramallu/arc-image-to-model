"""Wall segmentation using classical computer vision."""

import cv2
import numpy as np
from typing import Dict, Any, List, Tuple
# from sklearn.cluster import RANSAC
# from sklearn.linear_model import LinearRegression

class WallSegmenter:
    """Segments walls from camera frames."""
    
    def __init__(self):
        self.min_wall_area = 10000
        self.edge_threshold_low = 50
        self.edge_threshold_high = 150
    
    def segment_wall(self, frame: np.ndarray) -> Dict[str, Any]:
        """Segment wall from frame using edge detection and plane fitting."""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            
            # Apply Gaussian blur
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Edge detection
            edges = cv2.Canny(blurred, self.edge_threshold_low, self.edge_threshold_high)
            
            # Morphological operations to connect edges
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
            edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Find largest contour (likely the wall)
            wall_mask = np.zeros_like(gray)
            wall_contour = None
            
            if contours:
                # Sort by area
                contours = sorted(contours, key=cv2.contourArea, reverse=True)
                
                for contour in contours:
                    area = cv2.contourArea(contour)
                    if area > self.min_wall_area:
                        # Check if contour is roughly rectangular (wall-like)
                        epsilon = 0.02 * cv2.arcLength(contour, True)
                        approx = cv2.approxPolyDP(contour, epsilon, True)
                        
                        if len(approx) >= 4:  # At least 4 corners
                            wall_contour = contour
                            cv2.fillPoly(wall_mask, [contour], 255)
                            break
            
            # Extract wall plane normal (simplified)
            plane_normal = self._estimate_plane_normal(wall_contour, frame.shape)
            
            # Calculate wall bounds
            bounds = self._get_wall_bounds(wall_contour) if wall_contour is not None else None
            
            return {
                "mask": wall_mask,
                "contours": [wall_contour] if wall_contour is not None else [],
                "plane_normal": plane_normal,
                "bounds": bounds,
                "wall_detected": wall_contour is not None,
                "confidence": self._calculate_confidence(wall_mask, edges)
            }
            
        except Exception as e:
            print(f"Wall segmentation error: {e}")
            return self._empty_result(frame.shape[:2])
    
    def _estimate_plane_normal(self, contour, image_shape) -> List[float]:
        """Estimate wall plane normal vector."""
        if contour is None:
            return [0.0, 0.0, 1.0]  # Default facing camera
        
        # Fit line to contour points
        points = contour.reshape(-1, 2)
        
        if len(points) < 10:
            return [0.0, 0.0, 1.0]
        
        try:
            # Simple line fitting without RANSAC
            if len(points) >= 2:
                # Fit line using least squares
                A = np.vstack([points[:, 0], np.ones(len(points))]).T
                slope, _ = np.linalg.lstsq(A, points[:, 1], rcond=None)[0]
                
                # Convert to normal vector
                angle = np.arctan(slope)
                normal = [np.sin(angle), -np.cos(angle), 0.1]
                
                # Normalize
                norm = np.linalg.norm(normal)
                return [n / norm for n in normal]
            
        except:
            pass
        
        return [0.0, 0.0, 1.0]
    
    def _get_wall_bounds(self, contour) -> Dict[str, int]:
        """Get bounding rectangle of wall."""
        if contour is None:
            return None
        
        x, y, w, h = cv2.boundingRect(contour)
        return {
            "x_min": int(x),
            "y_min": int(y), 
            "x_max": int(x + w),
            "y_max": int(y + h),
            "width": int(w),
            "height": int(h)
        }
    
    def _calculate_confidence(self, mask: np.ndarray, edges: np.ndarray) -> float:
        """Calculate wall detection confidence."""
        if mask is None:
            return 0.0
        
        # Ratio of wall pixels to total pixels
        wall_pixels = np.sum(mask > 0)
        total_pixels = mask.shape[0] * mask.shape[1]
        coverage = wall_pixels / total_pixels
        
        # Edge density in wall region
        wall_edges = np.sum((mask > 0) & (edges > 0))
        edge_density = wall_edges / (wall_pixels + 1)
        
        # Combine metrics
        confidence = min(coverage * 2 + edge_density * 0.5, 1.0)
        return float(confidence)
    
    def _empty_result(self, shape: Tuple[int, int]) -> Dict[str, Any]:
        """Return empty segmentation result."""
        return {
            "mask": np.zeros(shape, dtype=np.uint8),
            "contours": [],
            "plane_normal": [0.0, 0.0, 1.0],
            "bounds": None,
            "wall_detected": False,
            "confidence": 0.0
        }

def segment_wall(frame: np.ndarray) -> Dict[str, Any]:
    """Standalone function for wall segmentation."""
    segmenter = WallSegmenter()
    return segmenter.segment_wall(frame)