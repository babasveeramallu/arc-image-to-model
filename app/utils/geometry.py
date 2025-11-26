"""3D geometry utilities for wall modeling and room construction."""

import numpy as np
from typing import List, Dict, Any, Tuple
# import trimesh
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
        
        # Extract wall bounds
        x_min, y_min = wall_bounds["x_min"], wall_bounds["y_min"]
        x_max, y_max = wall_bounds["x_max"], wall_bounds["y_max"]
        
        # Sample depth at wall corners
        depth_tl = depth_map[y_min, x_min] if depth_map is not None else 2.0
        depth_tr = depth_map[y_min, x_max] if depth_map is not None else 2.0
        depth_bl = depth_map[y_max, x_min] if depth_map is not None else 2.0
        depth_br = depth_map[y_max, x_max] if depth_map is not None else 2.0
        
        # Convert to 3D coordinates
        vertices = []
        
        # Top-left
        x_tl = (x_min - camera_params["cx"]) * depth_tl / camera_params["fx"]
        y_tl = (y_min - camera_params["cy"]) * depth_tl / camera_params["fy"]
        vertices.append([x_tl, y_tl, depth_tl])
        
        # Top-right  
        x_tr = (x_max - camera_params["cx"]) * depth_tr / camera_params["fx"]
        y_tr = (y_min - camera_params["cy"]) * depth_tr / camera_params["fy"]
        vertices.append([x_tr, y_tr, depth_tr])
        
        # Bottom-right
        x_br = (x_max - camera_params["cx"]) * depth_br / camera_params["fx"]
        y_br = (y_max - camera_params["cy"]) * depth_br / camera_params["fy"]
        vertices.append([x_br, y_br, depth_br])
        
        # Bottom-left
        x_bl = (x_min - camera_params["cx"]) * depth_bl / camera_params["fx"]
        y_bl = (y_max - camera_params["cy"]) * depth_bl / camera_params["fy"]
        vertices.append([x_bl, y_bl, depth_bl])
        
        vertices = np.array(vertices)
        
        # Calculate wall normal
        v1 = vertices[1] - vertices[0]  # Top edge
        v2 = vertices[3] - vertices[0]  # Left edge
        normal = np.cross(v1, v2)
        normal = normal / np.linalg.norm(normal)
        
        return Wall(
            id=f"wall_{np.random.randint(1000, 9999)}",
            vertices=vertices,
            normal=normal,
            bounds=wall_bounds,
            elements=[],
            confidence=0.8
        )
    
    def fit_plane(self, points: np.ndarray) -> Tuple[np.ndarray, float]:
        """Fit plane to 3D points using least squares."""
        if len(points) < 3:
            return np.array([0, 0, 1]), 0.0
        
        # Center the points
        centroid = np.mean(points, axis=0)
        centered = points - centroid
        
        # SVD to find normal
        _, _, vh = np.linalg.svd(centered)
        normal = vh[-1]  # Last row is normal
        
        # Calculate distance from origin
        distance = np.dot(normal, centroid)
        
        return normal, distance
    
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
    
    def create_room_mesh(self, walls: List[Wall]) -> Dict[str, Any]:
        """Create complete room mesh from individual walls."""
        if not walls:
            return {"vertices": np.array([]), "faces": np.array([])}
        
        all_vertices = []
        all_faces = []
        vertex_offset = 0
        
        for wall in walls:
            # Create wall quad
            wall_vertices = wall.vertices
            
            # Add vertices
            all_vertices.extend(wall_vertices)
            
            # Create faces (two triangles per wall)
            faces = [
                [vertex_offset, vertex_offset + 1, vertex_offset + 2],
                [vertex_offset, vertex_offset + 2, vertex_offset + 3]
            ]
            all_faces.extend(faces)
            vertex_offset += 4
        
        if not all_vertices:
            return {"vertices": np.array([]), "faces": np.array([])}
        
        return {
            "vertices": np.array(all_vertices),
            "faces": np.array(all_faces)
        }
    
    def add_element_cutouts(self, mesh: Dict, elements: List[Dict]) -> Dict:
        """Add cutouts for windows and doors."""
        # Simplified - just return original mesh
        return mesh

def create_wall_from_segmentation(segmentation_result: Dict, depth_map: np.ndarray) -> Wall:
    """Create Wall object from segmentation result."""
    processor = GeometryProcessor()
    
    if not segmentation_result["wall_detected"] or segmentation_result["bounds"] is None:
        # Return empty wall
        return Wall(
            id="empty_wall",
            vertices=np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]]),
            normal=np.array([0, 0, 1]),
            bounds={},
            elements=[],
            confidence=0.0
        )
    
    return processor.create_wall_mesh(segmentation_result["bounds"], depth_map)