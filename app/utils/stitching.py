"""Multi-wall stitching for complete room assembly."""

import numpy as np
from typing import List, Dict, Any
from app.utils.geometry import Wall, RoomModel, GeometryProcessor

class RoomStitcher:
    """Stitches multiple wall scans into complete room model."""
    
    def __init__(self):
        self.geometry_processor = GeometryProcessor()
        self.walls: List[Wall] = []
        
    def add_wall(self, wall: Wall):
        """Add a new wall to the room."""
        if wall and wall.confidence > 0.3:  # Only add walls with decent confidence
            self.walls.append(wall)
            print(f"Added wall {wall.id}, total walls: {len(self.walls)}")
    
    def stitch_walls(self, wall_list: List[Wall]) -> RoomModel:
        """Create room model from walls with simplified stitching."""
        if not wall_list:
            return self._empty_room()
        
        try:
            # Use provided walls or internal walls
            walls_to_use = wall_list if wall_list else self.walls
            
            if not walls_to_use:
                return self._empty_room()
            
            # Simple room assembly - just combine all walls
            all_vertices = []
            all_faces = []
            vertex_offset = 0
            
            valid_walls = []
            for wall in walls_to_use:
                if len(wall.vertices) >= 4:
                    valid_walls.append(wall)
                    
                    # Add wall vertices
                    all_vertices.extend(wall.vertices.tolist())
                    
                    # Create faces for this wall (two triangles)
                    faces = [
                        [vertex_offset, vertex_offset + 1, vertex_offset + 2],
                        [vertex_offset, vertex_offset + 2, vertex_offset + 3]
                    ]
                    all_faces.extend(faces)
                    vertex_offset += 4
            
            # Calculate room bounds
            bounds = self._calculate_room_bounds(valid_walls)
            
            # Create room model
            vertices_array = np.array(all_vertices) if all_vertices else np.array([])
            faces_array = np.array(all_faces) if all_faces else np.array([])
            
            return RoomModel(
                walls=valid_walls,
                vertices=vertices_array,
                faces=faces_array,
                bounds=bounds
            )
            
        except Exception as e:
            print(f"Stitching error: {e}")
            # Return basic room with just the walls
            return RoomModel(
                walls=wall_list[:4],  # Limit to 4 walls max
                vertices=np.array([]),
                faces=np.array([]),
                bounds={"width": 4.0, "height": 2.5, "depth": 4.0, "area": 16.0, "volume": 40.0}
            )
    
    def _calculate_room_bounds(self, walls: List[Wall]) -> Dict[str, float]:
        """Calculate overall room dimensions."""
        if not walls:
            return {"width": 0, "height": 0, "depth": 0, "area": 0, "volume": 0}
        
        try:
            # Collect all vertices
            all_vertices = []
            for wall in walls:
                if len(wall.vertices) > 0:
                    all_vertices.extend(wall.vertices.tolist())
            
            if not all_vertices:
                return {"width": 0, "height": 0, "depth": 0, "area": 0, "volume": 0}
            
            vertices = np.array(all_vertices)
            
            # Calculate bounds
            min_coords = np.min(vertices, axis=0)
            max_coords = np.max(vertices, axis=0)
            
            width = float(max_coords[0] - min_coords[0])
            height = float(max_coords[1] - min_coords[1]) 
            depth = float(abs(max_coords[2] - min_coords[2]))
            
            # Ensure reasonable minimum values
            width = max(width, 1.0)
            height = max(height, 1.0) 
            depth = max(depth, 1.0)
            
            return {
                "width": width,
                "height": height,
                "depth": depth,
                "area": width * depth,
                "volume": width * height * depth
            }
            
        except Exception as e:
            print(f"Bounds calculation error: {e}")
            return {"width": 4.0, "height": 2.5, "depth": 4.0, "area": 16.0, "volume": 40.0}
    
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
            try:
                dims = self.geometry_processor.calculate_wall_dimensions(wall.vertices)
                total_area += dims["area"]
                total_confidence += wall.confidence
            except:
                continue
        
        avg_confidence = total_confidence / len(self.walls) if self.walls else 0
        
        return {
            "wall_count": len(self.walls),
            "total_area": total_area,
            "avg_confidence": avg_confidence,
            "room_complete": len(self.walls) >= 2
        }

def stitch_walls(wall_list: List[Wall]) -> RoomModel:
    """Standalone function for wall stitching."""
    stitcher = RoomStitcher()
    return stitcher.stitch_walls(wall_list)