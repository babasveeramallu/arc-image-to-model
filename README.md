# Arc - Image to Model Tool

An AI-powered real-time wall and room scanner that converts 2D camera feed into accurate 3D models with material and texture customization.

## 🚀 Quick Start

```bash
# 1. Navigate to project
cd "Arc - Image to Model Tool"

# 2. Start backend
cd backend
.\venv\Scripts\python -m uvicorn app.main:app --reload

# 3. Open in browser
# http://localhost:8000
```

## 📁 Project Structure

```
Arc - Image to Model Tool/
├── backend/
│   ├── app/
│   │   └── main.py           # FastAPI server
│   ├── venv/                 # Python virtual environment
│   └── requirements.txt       # Python dependencies
├── frontend/
│   └── index.html            # Web app (self-contained)
├── models/
│   ├── wall_detector.py      # Wall detection AI
│   ├── element_detector.py   # Element detection AI
│   └── room_stitcher.py      # Room stitching AI
├── docs/
│   └── API.md                # API documentation
├── .gitignore
└── README.md
```

## ✨ Features

- 📷 Real-time camera feed scanning
- 🎯 Wall detection and segmentation
- 🔍 Element detection (outlets, switches, windows, doors)
- 🏠 3D room model generation
- 🎨 Material and texture library (8 options)
- 📊 Live statistics display
- 🔗 REST API endpoints

## 🌐 Access

**Web App:** http://localhost:8000

**API Docs:** http://localhost:8000/docs

**Health Check:** http://localhost:8000/health

## 📝 API Endpoints

- `GET /health` - Health check
- `GET /` - Web app (HTML)
- `POST /api/scan/wall` - Scan and detect walls
- `POST /api/detect/elements` - Detect wall elements
- `POST /api/stitch/rooms` - Stitch multiple walls

## 🔧 Development

Backend is hot-reloading. Edit `backend/app/main.py` and changes apply automatically.

Frontend is in `frontend/index.html`. Refresh browser to see changes.

AI models in `models/` folder ready to improve with TensorFlow/YOLO.

## 📅 Deadline

**Nov 29, 2025 @ 12:30pm CST**

## 📖 Documentation

See `docs/API.md` for complete API documentation.

---

Built for SPA Bhopal Hackathon 2025
