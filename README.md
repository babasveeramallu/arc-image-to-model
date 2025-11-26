# Arc — Python Real-Time Wall & Room Scanner AI Tool

Arc uses AI to scan walls in real-time, detect elements (outlets, switches, windows, doors), and create 3D room models.

## Quick Start

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app/main.py
```

Open http://localhost:8000 in your browser.

## Features

- Real-time wall scanning via webcam/phone camera
- AI-powered element detection (outlets, switches, windows, doors)
- Depth estimation and 3D wall modeling
- Multi-wall stitching for complete rooms
- Material/texture application
- GLB/OBJ export

## Architecture

- **FastAPI** backend with WebRTC camera support
- **YOLOv8** for object detection
- **MiDaS** for depth estimation
- **OpenCV** for wall segmentation
- **Three.js** for 3D visualization
- **Trimesh** for 3D model generation

## API Endpoints

- `POST /scan` - Process camera frame
- `POST /detect_objects` - Detect wall elements
- `POST /stitch` - Merge multiple walls
- `GET /export/glb` - Export 3D model