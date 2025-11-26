import cv2
import numpy as np
from typing import Dict, Any

class WallDetector:
    def __init__(self):
        self.tf_available = False
        self.model = None
        
        try:
            import tensorflow as tf
            tf.get_logger().setLevel('ERROR')  # Reduce TF logging
            from tensorflow.keras.applications import ResNet50
            from tensorflow.keras.applications.resnet50 import preprocess_input
            
            self.model = ResNet50(weights='imagenet', include_top=False, pooling='avg')
            self.preprocess_input = preprocess_input
            self.tf_available = True
            print("WallDetector initialized with ResNet-50")
        except ImportError:
            print("TensorFlow not available, using OpenCV only")
        except Exception as e:
            print(f"ResNet-50 loading failed: {e}")
        
        self.model_loaded = True
    
    def detect_wall(self, image_path: str) -> Dict[str, Any]:
        try:
            image = cv2.imread(image_path)
            if image is None:
                return {"wall_detected": False, "confidence": 0.0, "error": "Could not load image"}
            
            height, width = image.shape[:2]
            
            # Enhanced edge detection
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Multi-scale edge detection
            edges1 = cv2.Canny(blurred, 50, 150)
            edges2 = cv2.Canny(blurred, 100, 200)
            edges = cv2.bitwise_or(edges1, edges2)
            
            # Detect lines (walls are typically straight)
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=80, minLineLength=30, maxLineGap=10)
            
            # Calculate confidence
            edge_pixels = np.sum(edges > 0)
            total_pixels = height * width
            edge_ratio = edge_pixels / total_pixels
            
            line_confidence = 0.0
            if lines is not None:
                line_confidence = min(len(lines) / 15.0, 1.0)
            
            # ResNet-50 feature analysis if available
            feature_confidence = 0.5
            if self.tf_available and self.model is not None:
                try:
                    img_resized = cv2.resize(image, (224, 224))
                    img_rgb = cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB)
                    img_array = np.expand_dims(img_rgb, axis=0)
                    img_array = self.preprocess_input(img_array.astype(np.float32))
                    
                    features = self.model.predict(img_array, verbose=0)
                    feature_confidence = min(np.mean(np.abs(features)) * 0.2, 1.0)
                except:
                    pass
            
            # Combine confidences
            final_confidence = (edge_ratio * 4 + line_confidence * 3 + feature_confidence * 2) / 9
            final_confidence = min(final_confidence, 1.0)
            
            wall_detected = final_confidence > 0.2
            
            return {
                "wall_detected": wall_detected,
                "confidence": final_confidence,
                "image_size": [width, height],
                "lines_detected": len(lines) if lines is not None else 0,
                "edge_ratio": edge_ratio,
                "processing_method": "resnet50_enhanced" if self.tf_available else "cv_enhanced"
            }
            
        except Exception as e:
            return {"wall_detected": False, "confidence": 0.0, "error": str(e)}