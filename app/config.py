"""Configuration settings for Arc application."""

import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent.parent
MODELS_DIR = BASE_DIR / "app" / "models"
STATIC_DIR = BASE_DIR / "app" / "static"
TEXTURES_DIR = STATIC_DIR / "textures"

# Camera settings
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CAMERA_FPS = 30

# AI Model settings
YOLO_MODEL_PATH = MODELS_DIR / "yolov8n.pt"
DEPTH_MODEL_PATH = MODELS_DIR / "midas_small.onnx"

# Detection classes
DETECTION_CLASSES = {
    0: "outlet",
    1: "light_switch", 
    2: "window",
    3: "door"
}

# Wall detection thresholds
WALL_CONFIDENCE_THRESHOLD = 0.3
DEPTH_SCALE_FACTOR = 1000.0
MIN_WALL_AREA = 10000

# 3D Model settings
WALL_THICKNESS = 0.1  # meters
DEFAULT_ROOM_HEIGHT = 2.5  # meters

# Server settings
HOST = "0.0.0.0"
PORT = 8000
DEBUG = True