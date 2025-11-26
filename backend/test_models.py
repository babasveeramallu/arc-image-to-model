#!/usr/bin/env python
"""Test all model imports and initialization"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    print("Testing model imports...")
    
    from models.wall_detector import WallDetector
    print("[OK] WallDetector imported")
    
    from models.element_detector import ElementDetector
    print("[OK] ElementDetector imported")
    
    from models.room_stitcher import RoomStitcher
    print("[OK] RoomStitcher imported")
    
    print("\nInitializing models...")
    wall_detector = WallDetector()
    print(f"[OK] WallDetector initialized: {wall_detector.model_loaded}")
    
    element_detector = ElementDetector()
    print(f"[OK] ElementDetector initialized: {element_detector.model_loaded}")
    
    room_stitcher = RoomStitcher()
    print("[OK] RoomStitcher initialized")
    
    print("\n[SUCCESS] All models working correctly!")
    
except Exception as e:
    print(f"\n[ERROR] {type(e).__name__}")
    print(f"Message: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
