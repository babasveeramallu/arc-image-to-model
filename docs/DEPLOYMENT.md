# Arc Deployment Guide

## Local Development Setup

### Prerequisites
- Python 3.8 or higher
- Webcam or smartphone camera
- Modern web browser (Chrome, Firefox, Safari)

### Quick Start
```bash
# Clone or download the Arc project
cd arc-wall-scanner

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install minimal dependencies (recommended for testing)
pip install -r requirements_minimal.txt

# OR install full dependencies (includes AI models)
pip install -r requirements.txt

# Start the application
python run.py
```

### Access the Application
1. Open your web browser
2. Navigate to `http://localhost:8000`
3. Grant camera permissions when prompted
4. Start scanning walls!

## Production Deployment

### Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements_minimal.txt .
RUN pip install -r requirements_minimal.txt

COPY . .
EXPOSE 8000

CMD ["python", "run.py"]
```

Build and run:
```bash
docker build -t arc-scanner .
docker run -p 8000:8000 arc-scanner
```

### Cloud Deployment Options

#### 1. Railway.app
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

#### 2. Render.com
1. Connect your GitHub repository
2. Set build command: `pip install -r requirements_minimal.txt`
3. Set start command: `python run.py`
4. Deploy

#### 3. Heroku
```bash
# Install Heroku CLI
heroku create arc-wall-scanner
git push heroku main
```

#### 4. DigitalOcean App Platform
1. Connect GitHub repository
2. Configure build settings
3. Deploy with one click

### Environment Variables
```bash
# Optional configuration
export ARC_HOST=0.0.0.0
export ARC_PORT=8000
export ARC_DEBUG=false
export ARC_MODELS_DIR=/app/models
```

## Mobile Deployment (Advanced)

### Progressive Web App (PWA)
The web interface works on mobile browsers and can be installed as a PWA.

### Native Mobile Apps

#### Using Kivy
```bash
pip install kivy buildozer
buildozer android debug
```

#### Using BeeWare
```bash
pip install briefcase
briefcase create
briefcase build
briefcase package
```

## Performance Optimization

### Server Optimization
```python
# In production, use Gunicorn
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Nginx Configuration
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Load Balancing
```yaml
# docker-compose.yml
version: '3.8'
services:
  arc-app:
    build: .
    ports:
      - "8000-8003:8000"
    deploy:
      replicas: 4
  
  nginx:
    image: nginx
    ports:
      - "80:80"
    depends_on:
      - arc-app
```

## Monitoring and Logging

### Health Checks
```bash
# Check if service is running
curl http://localhost:8000/health
```

### Logging Configuration
```python
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Metrics Collection
```python
# Add to main.py
from prometheus_client import Counter, Histogram
scan_counter = Counter('arc_scans_total', 'Total scans performed')
scan_duration = Histogram('arc_scan_duration_seconds', 'Scan processing time')
```

## Security Considerations

### HTTPS Configuration
```bash
# Generate SSL certificate
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365

# Run with HTTPS
uvicorn app.main:app --host 0.0.0.0 --port 8000 --ssl-keyfile key.pem --ssl-certfile cert.pem
```

### CORS Configuration
```python
# Restrict origins in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

### Rate Limiting
```python
from slowapi import Limiter
limiter = Limiter(key_func=lambda: "global")

@app.post("/scan")
@limiter.limit("10/minute")
async def scan_frame(request: Request, file: UploadFile = File(...)):
    # ... existing code
```

## Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Find process using port 8000
netstat -ano | findstr :8000  # Windows
lsof -i :8000                 # macOS/Linux

# Kill process
taskkill /PID <PID> /F        # Windows
kill -9 <PID>                 # macOS/Linux
```

#### Camera Access Issues
- Ensure HTTPS for production (required for camera access)
- Check browser permissions
- Test with different browsers

#### Memory Issues
```bash
# Monitor memory usage
htop  # Linux/macOS
taskmgr  # Windows

# Reduce memory usage
export OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS=0
```

#### Model Loading Failures
```bash
# Check available disk space
df -h  # Linux/macOS
dir   # Windows

# Clear model cache
rm -rf ~/.cache/torch  # PyTorch models
rm -rf ~/.cache/ultralytics  # YOLO models
```

### Performance Tuning

#### CPU Optimization
```python
# Limit OpenCV threads
cv2.setNumThreads(2)

# Use optimized NumPy
export OPENBLAS_NUM_THREADS=2
```

#### Memory Optimization
```python
# Reduce image resolution for processing
def resize_for_processing(image, max_size=640):
    h, w = image.shape[:2]
    if max(h, w) > max_size:
        scale = max_size / max(h, w)
        new_w, new_h = int(w * scale), int(h * scale)
        return cv2.resize(image, (new_w, new_h))
    return image
```

## Backup and Recovery

### Data Backup
```bash
# Backup scanned models
tar -czf arc_models_backup.tar.gz output/
```

### Configuration Backup
```bash
# Backup configuration
cp app/config.py config_backup.py
```

### Automated Backups
```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
tar -czf "arc_backup_$DATE.tar.gz" output/ app/config.py
```

## Scaling Considerations

### Horizontal Scaling
- Use load balancer (Nginx, HAProxy)
- Stateless application design
- Shared storage for models

### Vertical Scaling
- Increase CPU cores for faster processing
- Add GPU for AI model acceleration
- Increase RAM for larger models

### Database Integration (Future)
```python
# For user data and scan history
from sqlalchemy import create_engine
engine = create_engine('postgresql://user:pass@localhost/arc')
```