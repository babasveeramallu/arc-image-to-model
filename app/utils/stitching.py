"""Multi-wall stitching for complete room assembly."""

import numpy as np
from typing import List, Dict, Any
from app.utils.geometry import Wall, RoomModel, GeometryProcessor
# import trimesh

class RoomStitcher:
    """Stitches multiple wall scans into complete room model."""
    
    def __init__(self):
        self.geometry_processor = GeometryProcessor()
        self.walls: List[Wall] = []
        self.corner_threshold = 0.1  # Threshold for corner detection
        
    def add_wall(self, wall: Wall):
        """Add a new wall to the room."""
        self.walls.append(wall)
    
    def stitch_walls(self, wall_list: List[Wall]) -> RoomModel:
        """Automatically merge multiple wall planes into 3D room model."""
        if not wall_list:
            return self._empty_room()
        
        # Update internal wall list
        self.walls = wall_list
        
        # Find corners and connections
        connections = self._find_wall_connections()
        
        # Align walls at corners
        aligned_walls = self._align_walls_at_corners(connections)
        
        # Create room mesh
        room_mesh = self.geometry_processor.create_room_mesh(aligned_walls)
        
        # Calculate room bounds
        bounds = self._calculate_room_bounds(aligned_walls)
        
        return RoomModel(
            walls=aligned_walls,
            vertices=room_mesh.vertices if room_mesh.vertices is not None else np.array([]),
            faces=room_mesh.faces if room_mesh.faces is not None else np.array([]),
            bounds=bounds
        )
    
    def _find_wall_connections(self) -> List[Dict[str, Any]]:
        """Find which walls connect at corners."""
        connections = []
        
        for i, wall1 in enumerate(self.walls):
            for j, wall2 in enumerate(self.walls[i+1:], i+1):
                connection = self._check_wall_connection(wall1, wall2)
                if connection["connected"]:
                    connections.append({
                        "wall1_idx": i,
                        "wall2_idx": j,
                        "connection_type": connection["type"],
                        "angle": connection["angle"]
                    })
        
        return connections
    
    def _check_wall_connection(self, wall1: Wall, wall2: Wall) -> Dict[str, Any]:
        """Check if two walls are connected."""
        # Calculate angle between wall normals
        dot_product = np.dot(wall1.normal, wall2.normal)
        angle = np.arccos(np.clip(dot_product, -1.0, 1.0))
        angle_degrees = np.degrees(angle)
        
        # Check if walls are perpendicular (corner)
        if 80 <= angle_degrees <= 100:
            return {
                "connected": True,
                "type": "corner",
                "angle": angle_degrees
            }
        
        # Check if walls are parallel (opposite walls)
        elif angle_degrees < 10 or angle_degrees > 170:
            return {
                "connected": True,
                "type": "parallel", 
                "angle": angle_degrees
            }
        
        return {
            "connected": False,
            "type": "none",
            "angle": angle_degrees
        }
    
    def _align_walls_at_corners(self, connections: List[Dict]) -> List[Wall]:
        """Align walls at detected corners."""
        aligned_walls = self.walls.copy()
        
        for connection in connections:
            if connection["connection_type"] == "corner":
                wall1_idx = connection["wall1_idx"]
                wall2_idx = connection["wall2_idx"]
                
                # Simple alignment - adjust wall positions to meet at corner
                wall1 = aligned_walls[wall1_idx]
                wall2 = aligned_walls[wall2_idx]
                
                # Find closest vertices between walls
                min_dist = float('inf')
                closest_v1, closest_v2 = 0, 0
                
                for i, v1 in enumerate(wall1.vertices):
                    for j, v2 in enumerate(wall2.vertices):
                        dist = np.linalg.norm(v1 - v2)
                        if dist < min_dist:
                            min_dist = dist
                            closest_v1, closest_v2 = i, j
                
                # Align vertices if they're close enough
                if min_dist < self.corner_threshold:
                    # Average the positions
                    avg_pos = (wall1.vertices[closest_v1] + wall2.vertices[closest_v2]) / 2
                    aligned_walls[wall1_idx].vertices[closest_v1] = avg_pos
                    aligned_walls[wall2_idx].vertices[closest_v2] = avg_pos
        
        return aligned_walls
    
    def _calculate_room_bounds(self, walls: List[Wall]) -> Dict[str, float]:
        """Calculate overall room dimensions."""
        if not walls:
            return {"width": 0, "height": 0, "depth": 0, "area": 0, "volume": 0}
        
        # Collect all vertices
        all_vertices = []
        for wall in walls:
            all_vertices.extend(wall.vertices)
        
        if not all_vertices:
            return {"width": 0, "height": 0, "depth": 0, "area": 0, "volume": 0}
        
        vertices = np.array(all_vertices)
        
        # Calculate bounds
        min_coords = np.min(vertices, axis=0)
        max_coords = np.max(vertices, axis=0)
        
        width = max_coords[0] - min_coords[0]
        height = max_coords[1] - min_coords[1] 
        depth = max_coords[2] - min_coords[2]
        
        return {
            "width": float(width),
            "height": float(height),
            "depth": float(depth),
            "area": float(width * depth),
            "volume": float(width * height * depth)
        }
    
    def _empty_room(self) -> RoomModel:
        """Return empty room model."""
        return RoomModel(
            walls=[],
            vertices=np.array([]),
            faces=np.array([]),
            bounds={"width": 0, "height": 0, "depth": 0, "area": 0, "volume": 0}
        )
    
    def get_room_statistics(self) -> Dict[str, Any]:
        """Get statistics about the current room."""
        if not self.walls:
            return {"wall_count": 0, "total_area": 0, "avg_confidence": 0}
        
        total_area = 0
        total_confidence = 0
        
        for wall in self.walls:
            dims = self.geometry_processor.calculate_wall_dimensions(wall.vertices)
            total_area += dims["area"]
            total_confidence += wall.confidence
        
        return {
            "wall_count": len(self.walls),
            "total_area": total_area,
            "avg_confidence": total_confidence / len(self.walls),
            "room_complete": len(self.walls) >= 3
        }

def stitch_walls(wall_list: List[Wall]) -> RoomModel:
    """Standalone function for wall stitching."""
    stitcher = RoomStitcher()
    return stitcher.stitch_walls(wall_list)