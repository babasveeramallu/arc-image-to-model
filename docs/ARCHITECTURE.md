# Arc Architecture Documentation

## System Overview

Arc is a real-time AI-powered wall and room scanning tool that uses computer vision and machine learning to create 3D models from camera input.

## Architecture Components

### 1. Frontend (Web Interface)
- **Technology**: HTML5, JavaScript, WebRTC
- **Features**: 
  - Real-time camera feed
  - Live scanning interface
  - 3D model preview
  - Material selection
  - Export controls

### 2. Backend (FastAPI)
- **Framework**: FastAPI with async support
- **Endpoints**: REST API for scanning, processing, export
- **Real-time**: WebSocket support for live updates

### 3. AI/ML Pipeline

#### Camera Input
- **WebRTC**: Browser camera access
- **OpenCV**: Desktop camera handling
- **Threading**: Smooth frame capture at 30 FPS

#### Wall Segmentation
- **Method**: Classical CV + edge detection
- **Fallback**: RANSAC plane fitting
- **Output**: Binary mask + contours

#### Depth Estimation
- **Primary**: MiDaS neural network
- **Fallback**: Sobel edge-based depth proxy
- **Output**: Normalized depth map

#### Object Detection
- **Model**: YOLOv8n for outlets/switches/windows/doors
- **Fallback**: Template matching
- **Classes**: 4 categories (outlet, switch, window, door)

#### 3D Reconstruction
- **Geometry**: Camera projection to 3D coordinates
- **Meshing**: Trimesh for 3D model generation
- **Stitching**: Multi-wall alignment and merging

### 4. Data Flow

```
Camera Frame → Segmentation → Depth Estimation → Object Detection
     ↓              ↓              ↓                ↓
   RGB Image    Wall Mask      Depth Map       Element Boxes
     ↓              ↓              ↓                ↓
     └──────────────┴──────────────┴────────────────┘
                           ↓
                    3D Wall Creation
                           ↓
                    Room Stitching
                           ↓
                    Model Export (GLB/OBJ)
```

## Key Algorithms

### Wall Detection
1. **Edge Detection**: Canny edge detection
2. **Contour Analysis**: Find largest rectangular contour
3. **Plane Fitting**: RANSAC for robust plane estimation
4. **Confidence**: Based on edge density and contour quality

### Depth Estimation
1. **MiDaS**: Pre-trained monocular depth estimation
2. **Preprocessing**: Resize to 384x384, normalize
3. **Post-processing**: Interpolate back to original size
4. **Fallback**: Sobel gradient magnitude as depth proxy

### Room Stitching
1. **Corner Detection**: Analyze wall normal angles
2. **Alignment**: Minimize vertex distance at corners
3. **Topology**: Build connected mesh structure
4. **Validation**: Check for closed room geometry

## Performance Considerations

### Real-time Processing
- **Target**: 10-15 FPS processing
- **Threading**: Separate capture and processing threads
- **Optimization**: Resize frames for faster inference

### Memory Management
- **Frame Buffers**: Circular buffer for smooth playback
- **Model Caching**: Keep AI models loaded in memory
- **Cleanup**: Automatic temporary file removal

### Scalability
- **Async**: FastAPI async endpoints
- **Batching**: Process multiple frames together
- **Caching**: Cache segmentation results

## Technology Stack

### Core Dependencies
- **FastAPI**: Web framework
- **OpenCV**: Computer vision
- **NumPy**: Numerical computing
- **Trimesh**: 3D mesh processing
- **PyTorch**: Deep learning (MiDaS)
- **Ultralytics**: YOLO object detection

### Optional Dependencies
- **TensorFlow**: Alternative ML backend
- **Open3D**: Advanced 3D processing
- **Matplotlib**: Visualization
- **Pillow**: Image processing

## Deployment Architecture

### Local Development
```
Browser ←→ FastAPI Server ←→ AI Models
   ↑           ↑                ↑
WebRTC    Port 8000         Local Files
```

### Production Deployment
```
Load Balancer ←→ FastAPI Instances ←→ Model Server
      ↑               ↑                    ↑
   HTTPS/WSS     Container Cluster    GPU Instances
```

## Error Handling

### Graceful Degradation
- **Camera Failure**: Show error message, allow file upload
- **AI Model Failure**: Fall back to classical CV methods
- **Network Issues**: Cache results locally

### Validation
- **Input**: Validate image format and size
- **Processing**: Check for valid segmentation results
- **Output**: Verify 3D model integrity

## Security Considerations

### Data Privacy
- **Local Processing**: No images sent to external servers
- **Temporary Files**: Automatic cleanup after processing
- **User Control**: Clear data on session end

### Input Validation
- **File Types**: Restrict to image formats
- **File Size**: Limit upload size
- **Content**: Basic image validation