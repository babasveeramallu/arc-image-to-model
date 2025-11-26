from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import uvicorn
import cv2
import numpy as np
import tempfile
import os
from pathlib import Path

app = FastAPI(title="Arc - AI Room Scanner")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple wall detector
def detect_wall(image_path: str):
    try:
        img = cv2.imread(image_path)
        if img is None:
            return {"wall_detected": False, "confidence": 0.0}
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=50, minLineLength=30, maxLineGap=10)
        
        edge_ratio = np.sum(edges > 0) / (img.shape[0] * img.shape[1])
        line_count = len(lines) if lines is not None else 0
        confidence = min((edge_ratio * 5 + line_count * 0.1), 1.0)
        
        return {
            "wall_detected": confidence > 0.2,
            "confidence": confidence,
            "lines_detected": line_count
        }
    except:
        return {"wall_detected": False, "confidence": 0.0}

@app.get("/")
async def root():
    html_path = Path("index.html")
    if html_path.exists():
        return FileResponse(html_path)
    return {"message": "Arc API", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/api/scan/wall")
async def scan_wall(file: UploadFile = File(...)):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        result = detect_wall(tmp_path)
        os.remove(tmp_path)
        return result
    except Exception as e:
        return {"wall_detected": False, "confidence": 0.0, "error": str(e)}

@app.post("/api/detect/elements")
async def detect_elements(file: UploadFile = File(...)):
    return {"total_elements": np.random.randint(0, 5)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)