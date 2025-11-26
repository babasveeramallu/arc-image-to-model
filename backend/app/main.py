from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
import sys
import tempfile
from dotenv import load_dotenv
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from models.wall_detector import WallDetector
from models.element_detector import ElementDetector
from models.room_stitcher import RoomStitcher

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Arc - Image to Model API",
    description="AI-powered wall and room scanner API",
    version="0.1.0"
)

# Initialize AI models
wall_detector = WallDetector()
element_detector = ElementDetector()
room_stitcher = RoomStitcher()

# Add CORS middleware to allow requests from frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (HTML, CSS, JS)
frontend_path = Path(__file__).parent.parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Arc API"}

# Serve HTML frontend
@app.get("/")
async def root():
    html_path = Path(__file__).parent.parent.parent / "frontend" / "index.html"
    if html_path.exists():
        return FileResponse(html_path, media_type="text/html")
    return {
        "message": "Arc - Image to Model API",
        "version": "0.1.0",
        "endpoints": {
            "health": "/health",
            "api_docs": "/docs",
            "scan_wall": "/api/scan/wall",
            "detect_elements": "/api/detect/elements",
            "stitch_rooms": "/api/stitch/rooms"
        }
    }

# Wall scanning endpoint
@app.post("/api/scan/wall")
async def scan_wall(file: UploadFile = File(...)):
    """
    Scan an image and detect wall surfaces
    """
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        # Run wall detection
        result = wall_detector.detect_wall(tmp_path)
        
        # Clean up temp file
        os.remove(tmp_path)
        
        return result
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )

# Element detection endpoint
@app.post("/api/detect/elements")
async def detect_elements(file: UploadFile = File(...)):
    """
    Detect wall elements (outlets, switches, windows, doors)
    """
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        # Run element detection
        result = element_detector.detect_elements(tmp_path)
        
        # Clean up temp file
        os.remove(tmp_path)
        
        return result
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )

# Room stitching endpoint
@app.post("/api/stitch/rooms")
async def stitch_rooms(wall_data: list | None = None):
    """
    Stitch multiple wall scans into a complete room model
    """
    try:
        if not wall_data:
            wall_data = []
        
        # Run room stitching
        result = room_stitcher.stitch_walls(wall_data)
        
        return result
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
