"""3D geometry utilities for wall modeling and room construction."""

import numpy as np
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass

@dataclass
class Wall:
    """Represents a single wall with 3D properties."""
    id: str
    vertices: np.ndarray  # 3D vertices
    normal: np.ndarray    # Wall normal vector
    bounds: Dict[str, float]  # 2D bounds in image
    elements: List[Dict]  # Detected elements (outlets, etc.)
    confidence: float
    
@dataclass 
class RoomModel:
    """Complete 3D room model."""
    walls: List[Wall]
    vertices: np.ndarray
    faces: np.ndarray
    bounds: Dict[str, float]

class GeometryProcessor:
    """Handles 3D geometry operations for wall and room modeling."""
    
    def __init__(self, room_height: float = 2.5, wall_thickness: float = 0.1):
        self.room_height = room_height
        self.wall_thickness = wall_thickness
    
    def create_wall_mesh(self, wall_bounds: Dict, depth_map: np.ndarray, 
                        camera_params: Dict = None) -> Wall:
        """Create 3D wall mesh from 2D bounds and depth."""
        
        # Default camera parameters
        if camera_params is None:
            camera_params = {
                "fx": 500, "fy": 500,  # Focal lengths
                "cx": 320, "cy": 240,  # Principal point
                "width": 640, "height": 480
            }
        
        # Extract wall bounds safely
        x_min = max(0, wall_bounds.get("x_min", 0))
        y_min = max(0, wall_bounds.get("y_min", 0))
        x_max = min(camera_params["width"]-1, wall_bounds.get("x_max", camera_params["width"]-1))
        y_max = min(camera_params["height"]-1, wall_bounds.get("y_max", camera_params["height"]-1))
        
        # Sample depth at wall corners (with bounds checking)
        if depth_map is not None and depth_map.size > 0:
            h, w = depth_map.shape
            y_min_safe = max(0, min(y_min, h-1))
            y_max_safe = max(0, min(y_max, h-1))
            x_min_safe = max(0, min(x_min, w-1))
            x_max_safe = max(0, min(x_max, w-1))
            
            depth_tl = float(depth_map[y_min_safe, x_min_safe]) * 3.0 + 1.0  # Scale depth
            depth_tr = float(depth_map[y_min_safe, x_max_safe]) * 3.0 + 1.0
            depth_bl = float(depth_map[y_max_safe, x_min_safe]) * 3.0 + 1.0
            depth_br = float(depth_map[y_max_safe, x_max_safe]) * 3.0 + 1.0
        else:
            depth_tl = depth_tr = depth_bl = depth_br = 2.0
        
        # Convert to 3D coordinates using proper camera projection
        vertices = []
        
        # Top-left
        x_tl = (x_min - camera_params["cx"]) * depth_tl / camera_params["fx"]
        y_tl = -(y_min - camera_params["cy"]) * depth_tl / camera_params["fy"]  # Flip Y
        vertices.append([x_tl, y_tl, -depth_tl])  # Negative Z for forward
        
        # Top-right  
        x_tr = (x_max - camera_params["cx"]) * depth_tr / camera_params["fx"]
        y_tr = -(y_min - camera_params["cy"]) * depth_tr / camera_params["fy"]
        vertices.append([x_tr, y_tr, -depth_tr])
        
        # Bottom-right
        x_br = (x_max - camera_params["cx"]) * depth_br / camera_params["fx"]
        y_br = -(y_max - camera_params["cy"]) * depth_br / camera_params["fy"]
        vertices.append([x_br, y_br, -depth_br])
        
        # Bottom-left
        x_bl = (x_min - camera_params["cx"]) * depth_bl / camera_params["fx"]
        y_bl = -(y_max - camera_params["cy"]) * depth_bl / camera_params["fy"]
        vertices.append([x_bl, y_bl, -depth_bl])
        
        vertices = np.array(vertices)
        
        # Calculate wall normal (cross product of edges)
        if len(vertices) >= 3:
            v1 = vertices[1] - vertices[0]  # Top edge
            v2 = vertices[3] - vertices[0]  # Left edge
            normal = np.cross(v1, v2)
            norm_length = np.linalg.norm(normal)
            if norm_length > 0:
                normal = normal / norm_length
            else:
                normal = np.array([0, 0, 1])
        else:
            normal = np.array([0, 0, 1])
        
        return Wall(
            id=f"wall_{np.random.randint(1000, 9999)}",
            vertices=vertices,
            normal=normal,
            bounds=wall_bounds,
            elements=[],
            confidence=0.8
        )
    
    def create_room_mesh(self, walls: List[Wall]) -> Dict[str, Any]:
        """Create complete room mesh from individual walls."""
        if not walls:
            return {"vertices": np.array([]), "faces": np.array([])}
        
        all_vertices = []
        all_faces = []
        vertex_offset = 0
        
        for wall in walls:
            if len(wall.vertices) >= 4:
                # Add wall vertices
                all_vertices.extend(wall.vertices)
                
                # Create two triangular faces for the wall quad
                faces = [
                    [vertex_offset, vertex_offset + 1, vertex_offset + 2],
                    [vertex_offset, vertex_offset + 2, vertex_offset + 3]
                ]
                all_faces.extend(faces)
                vertex_offset += 4
        
        if not all_vertices:
            # Create a simple box as fallback
            vertices = np.array([
                [-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],  # Back
                [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]       # Front
            ])
            faces = np.array([
                [0, 1, 2], [0, 2, 3],  # Back wall
                [4, 7, 6], [4, 6, 5],  # Front wall
                [0, 4, 5], [0, 5, 1],  # Bottom
                [2, 6, 7], [2, 7, 3],  # Top
                [0, 3, 7], [0, 7, 4],  # Left
                [1, 5, 6], [1, 6, 2]   # Right
            ])
            return {"vertices": vertices, "faces": faces}
        
        return {
            "vertices": np.array(all_vertices),
            "faces": np.array(all_faces)
        }
    
    def calculate_wall_dimensions(self, vertices: np.ndarray) -> Dict[str, float]:
        """Calculate real-world wall dimensions."""
        if len(vertices) < 4:
            return {"width": 0.0, "height": 0.0, "area": 0.0}
        
        # Calculate width (top edge)
        width = np.linalg.norm(vertices[1] - vertices[0])
        
        # Calculate height (left edge)  
        height = np.linalg.norm(vertices[3] - vertices[0])
        
        return {
            "width": float(width),
            "height": float(height), 
            "area": float(width * height)
        }

def create_wall_from_segmentation(segmentation_result: Dict, depth_map: np.ndarray) -> Wall:
    """Create Wall object from segmentation result."""
    processor = GeometryProcessor()
    
    if not segmentation_result.get("wall_detected", False) or segmentation_result.get("bounds") is None:
        # Return simple default wall
        return Wall(
            id="default_wall",
            vertices=np.array([[-1, 1, -2], [1, 1, -2], [1, -1, -2], [-1, -1, -2]]),
            normal=np.array([0, 0, 1]),
            bounds={"x_min": 0, "y_min": 0, "x_max": 100, "y_max": 100},
            elements=[],
            confidence=0.5
        )
    
    return processor.create_wall_mesh(segmentation_result["bounds"], depth_map)