# Arc Workflow Documentation

## Complete Scanning Workflow

### Phase 1: Setup and Initialization

1. **Start Application**
   ```bash
   python app/main.py
   ```

2. **Open Web Interface**
   - Navigate to `http://localhost:8000`
   - Grant camera permissions when prompted

3. **Camera Setup**
   - Click "Start Camera"
   - Position camera to face wall
   - Ensure good lighting and stable position

### Phase 2: Wall Scanning

#### Single Wall Scan
1. **Frame Wall in View**
   - Fill camera view with wall surface
   - Avoid extreme angles
   - Include some context (floor/ceiling edges)

2. **Initiate Scan**
   - Click "Scan Wall" button
   - Wait for processing (2-3 seconds)
   - Check confidence score (>70% recommended)

3. **Review Results**
   - Wall detection status
   - Detected elements (outlets, switches, etc.)
   - 3D preview update

#### Multi-Wall Scanning
1. **Scan First Wall**
   - Follow single wall process
   - Note wall count increment

2. **Move to Adjacent Wall**
   - Physically move to next wall
   - Maintain some overlap with previous wall
   - Look for corner connections

3. **Continue Scanning**
   - Repeat for each wall in room
   - Minimum 3 walls for complete room
   - Maximum 8 walls supported

### Phase 3: Room Assembly

#### Automatic Stitching
1. **Trigger Room Build**
   - Click "Build Room" button
   - System analyzes wall relationships
   - Detects corners and connections

2. **Review Room Model**
   - Check 3D preview
   - Verify wall connections
   - Note any gaps or misalignments

#### Manual Adjustments (Future Feature)
- Adjust wall positions
- Modify corner connections
- Fine-tune dimensions

### Phase 4: Material Application

1. **Select Material**
   - Choose from material library
   - Preview material on walls
   - Apply to individual walls or entire room

2. **Material Types Available**
   - Paint colors (white, beige, gray)
   - Wood textures (oak, dark wood)
   - Brick patterns
   - Wallpaper designs
   - Concrete textures

### Phase 5: Export and Use

#### 3D Model Export
1. **GLB Export**
   - Click "Export GLB"
   - Compatible with web viewers
   - Includes materials and textures

2. **OBJ Export**
   - Click "Export OBJ"
   - Universal 3D format
   - Works with most 3D software

#### File Usage
- **Web Viewing**: Use Three.js or Babylon.js
- **3D Software**: Import into Blender, Maya, 3ds Max
- **AR/VR**: Use in Unity, Unreal Engine
- **CAD**: Import into SketchUp, AutoCAD

## Best Practices

### Camera Positioning
- **Distance**: 3-6 feet from wall
- **Angle**: Perpendicular to wall surface
- **Height**: Chest level for best results
- **Stability**: Use tripod or steady hands

### Lighting Conditions
- **Avoid**: Direct sunlight, harsh shadows
- **Prefer**: Even, diffused lighting
- **Indoor**: Standard room lighting works well
- **Outdoor**: Overcast conditions ideal

### Wall Selection
- **Good Candidates**:
  - Plain painted walls
  - Walls with clear edges
  - Well-lit surfaces
  - Minimal clutter

- **Challenging Cases**:
  - Highly textured walls
  - Very dark or reflective surfaces
  - Walls with many decorations
  - Poor lighting conditions

### Scanning Tips
- **Overlap**: Include 10-20% overlap between adjacent walls
- **Elements**: Ensure outlets/switches are clearly visible
- **Stability**: Keep camera steady during scan
- **Multiple Attempts**: Re-scan if confidence is low

## Troubleshooting Common Issues

### Low Confidence Scores
- **Cause**: Poor lighting, unclear wall edges
- **Solution**: Improve lighting, clean wall surface, adjust angle

### Missing Wall Detection
- **Cause**: Wall too small in frame, poor contrast
- **Solution**: Move closer, improve lighting, try different angle

### Incorrect Element Detection
- **Cause**: Shadows, reflections, similar objects
- **Solution**: Improve lighting, remove distractions

### Room Stitching Failures
- **Cause**: Insufficient wall overlap, inconsistent scale
- **Solution**: Re-scan with more overlap, maintain consistent distance

### Export Issues
- **Cause**: Insufficient geometry, processing errors
- **Solution**: Ensure minimum 3 walls scanned, check for errors

## Quality Metrics

### Wall Detection Quality
- **Confidence**: >70% for reliable results
- **Coverage**: Wall should fill 40-80% of frame
- **Edge Clarity**: Clear wall boundaries visible

### Element Detection Quality
- **Precision**: Minimize false positives
- **Recall**: Detect all visible elements
- **Localization**: Accurate bounding boxes

### Room Model Quality
- **Completeness**: All walls properly connected
- **Accuracy**: Realistic proportions and dimensions
- **Topology**: Closed, manifold geometry

## Performance Expectations

### Processing Times
- **Single Wall Scan**: 2-3 seconds
- **Element Detection**: 1-2 seconds
- **Room Stitching**: 3-5 seconds
- **Model Export**: 5-10 seconds

### Accuracy Targets
- **Wall Detection**: 90%+ success rate
- **Element Detection**: 80%+ precision
- **Dimension Accuracy**: ±10% of actual measurements
- **Room Completeness**: 95%+ for 4-wall rooms

### System Requirements
- **Minimum**: 4GB RAM, integrated graphics
- **Recommended**: 8GB RAM, dedicated GPU
- **Camera**: 720p minimum, 1080p preferred
- **Browser**: Chrome, Firefox, Safari (latest versions)