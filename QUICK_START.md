# Arc - Quick Start Guide

## 🚀 Get Started in 3 Minutes

### 1. Install Dependencies
```bash
pip install -r requirements_basic.txt
```

### 2. Run the Application
```bash
python run.py
```

### 3. Open in Browser
Navigate to: **http://localhost:8000**

## 📱 How to Use

1. **Start Camera** - Click "Start Camera" and allow permissions
2. **Scan Wall** - Point camera at wall and click "Scan Wall"  
3. **Build Room** - Scan multiple walls, then click "Build Room"
4. **Export Model** - Click "Export GLB" or "Export OBJ"

## ✅ What Works

- ✅ Real-time camera feed
- ✅ Wall detection using computer vision
- ✅ Element detection (outlets, switches)
- ✅ 3D room model generation
- ✅ Material/texture application
- ✅ GLB/OBJ export
- ✅ Mobile camera support
- ✅ Progressive web app

## 🔧 System Requirements

- Python 3.8+
- Webcam or smartphone camera
- Modern browser (Chrome, Firefox, Safari)
- 4GB RAM minimum

## 📁 Project Structure

```
arc/
├── app/
│   ├── main.py              # FastAPI server + web UI
│   ├── config.py            # Configuration settings
│   └── utils/               # AI/ML processing modules
├── docs/                    # Complete documentation
├── output/                  # Exported 3D models
└── run.py                   # Simple launcher
```

## 🎯 Key Features

- **Real-time Processing**: 10-15 FPS wall scanning
- **AI Detection**: Computer vision + fallback methods
- **3D Modeling**: Automatic room assembly
- **Material Library**: 8 built-in textures
- **Export Formats**: GLB, OBJ support
- **Cross-platform**: Works on desktop and mobile

## 🔍 Troubleshooting

**Camera not working?**
- Check browser permissions
- Try different browser
- Ensure HTTPS for mobile

**Low detection confidence?**
- Improve lighting
- Move closer to wall
- Ensure wall fills 40-80% of frame

**Export failed?**
- Scan at least 2 walls
- Check output/ directory permissions

## 📚 Full Documentation

- [Architecture](docs/ARCHITECTURE.md) - Technical details
- [API Reference](docs/API_REFERENCE.md) - REST endpoints
- [Deployment](docs/DEPLOYMENT.md) - Production setup
- [Workflow](docs/WORKFLOW.md) - Complete usage guide

## 🚀 Next Steps

1. **Scan your first room** - Start with a simple rectangular room
2. **Try different materials** - Apply textures to walls
3. **Export and view** - Use exported models in 3D software
4. **Deploy to cloud** - Follow deployment guide for production

**Ready to scan? Run `python run.py` and start building 3D models!**