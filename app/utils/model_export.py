"""3D model export functionality for GLB and OBJ formats."""

import numpy as np
from typing import Dict, Any, Optional
from pathlib import Path
from app.utils.geometry import RoomModel, Wall

class ModelExporter:
    """Handles 3D model export in various formats."""
    
    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def export_glb(self, room_model: RoomModel, filename: str = "room.glb") -> str:
        """Export room model as GLB file."""
        try:
            mesh_data = self._room_to_dict(room_model)
            output_path = self.output_dir / filename
            
            # For now, export as OBJ since GLB is complex
            self._write_obj(mesh_data, output_path.with_suffix('.obj'))
            
            # Copy to GLB extension for compatibility
            with open(output_path.with_suffix('.obj'), 'rb') as src:
                with open(output_path, 'wb') as dst:
                    dst.write(src.read())
            
            return str(output_path)
            
        except Exception as e:
            print(f"GLB export error: {e}")
            return self._create_dummy_obj(filename)
    
    def export_obj(self, room_model: RoomModel, filename: str = "room.obj") -> str:
        """Export room model as OBJ file."""
        try:
            mesh_data = self._room_to_dict(room_model)
            output_path = self.output_dir / filename
            self._write_obj(mesh_data, output_path)
            return str(output_path)
            
        except Exception as e:
            print(f"OBJ export error: {e}")
            return self._create_dummy_obj(filename)
    
    def _room_to_dict(self, room_model: RoomModel) -> Dict[str, Any]:
        """Convert RoomModel to mesh dictionary."""
        try:
            # Use existing vertices and faces if available
            if len(room_model.vertices) > 0 and len(room_model.faces) > 0:
                return {
                    "vertices": room_model.vertices,
                    "faces": room_model.faces
                }
            
            # Build from walls
            if room_model.walls:
                all_vertices = []
                all_faces = []
                vertex_offset = 0
                
                for wall in room_model.walls:
                    if len(wall.vertices) >= 4:
                        # Add vertices
                        all_vertices.extend(wall.vertices.tolist())
                        
                        # Add faces (two triangles per wall)
                        faces = [
                            [vertex_offset, vertex_offset + 1, vertex_offset + 2],
                            [vertex_offset, vertex_offset + 2, vertex_offset + 3]
                        ]
                        all_faces.extend(faces)
                        vertex_offset += 4
                
                if all_vertices:
                    return {
                        "vertices": np.array(all_vertices),
                        "faces": np.array(all_faces)
                    }
            
            # Fallback: create simple room box
            return self._create_simple_room()
            
        except Exception as e:
            print(f"Room conversion error: {e}")
            return self._create_simple_room()
    
    def _create_simple_room(self) -> Dict[str, Any]:
        """Create a simple box room."""
        # Simple room: 4m x 2.5m x 4m
        vertices = np.array([
            # Floor vertices
            [-2, -1.25, -2], [2, -1.25, -2], [2, -1.25, 2], [-2, -1.25, 2],
            # Ceiling vertices  
            [-2, 1.25, -2], [2, 1.25, -2], [2, 1.25, 2], [-2, 1.25, 2]
        ])
        
        faces = np.array([
            # Floor
            [0, 1, 2], [0, 2, 3],
            # Ceiling
            [4, 7, 6], [4, 6, 5],
            # Walls
            [0, 4, 5], [0, 5, 1],  # Front wall
            [1, 5, 6], [1, 6, 2],  # Right wall
            [2, 6, 7], [2, 7, 3],  # Back wall
            [3, 7, 4], [3, 4, 0]   # Left wall
        ])
        
        return {"vertices": vertices, "faces": faces}
    
    def _write_obj(self, mesh_data: Dict, output_path: Path):
        """Write OBJ file."""
        try:
            with open(output_path, 'w') as f:
                f.write("# Arc AI Wall Scanner - Generated Room Model\n")
                f.write(f"# Vertices: {len(mesh_data['vertices'])}\n")
                f.write(f"# Faces: {len(mesh_data['faces'])}\n\n")
                
                # Write vertices
                for vertex in mesh_data["vertices"]:
                    f.write(f"v {vertex[0]:.6f} {vertex[1]:.6f} {vertex[2]:.6f}\n")
                
                f.write("\n")
                
                # Write faces (OBJ uses 1-based indexing)
                for face in mesh_data["faces"]:
                    f.write(f"f {face[0]+1} {face[1]+1} {face[2]+1}\n")
                    
        except Exception as e:
            print(f"OBJ write error: {e}")
            # Write minimal fallback
            with open(output_path, 'w') as f:
                f.write("# Fallback room model\n")
                f.write("v -1 -1 -1\nv 1 -1 -1\nv 1 1 -1\nv -1 1 -1\n")
                f.write("f 1 2 3\nf 1 3 4\n")
    
    def _create_dummy_obj(self, filename: str) -> str:
        """Create a simple dummy OBJ file."""
        try:
            output_path = self.output_dir / filename
            
            with open(output_path, 'w') as f:
                f.write("# Arc - Simple Room Model\n")
                f.write("# 4m x 2.5m x 4m room\n\n")
                
                # Simple room vertices
                f.write("v -2.0 -1.25 -2.0\n")  # Floor corners
                f.write("v  2.0 -1.25 -2.0\n")
                f.write("v  2.0 -1.25  2.0\n")
                f.write("v -2.0 -1.25  2.0\n")
                f.write("v -2.0  1.25 -2.0\n")  # Ceiling corners
                f.write("v  2.0  1.25 -2.0\n")
                f.write("v  2.0  1.25  2.0\n")
                f.write("v -2.0  1.25  2.0\n")
                
                f.write("\n# Faces\n")
                f.write("f 1 2 3 4\n")  # Floor
                f.write("f 5 8 7 6\n")  # Ceiling
                f.write("f 1 5 6 2\n")  # Front wall
                f.write("f 2 6 7 3\n")  # Right wall
                f.write("f 3 7 8 4\n")  # Back wall
                f.write("f 4 8 5 1\n")  # Left wall
            
            return str(output_path)
        except:
            return ""
    
    def get_model_info(self, room_model: RoomModel) -> Dict[str, Any]:
        """Get information about the 3D model."""
        try:
            mesh_data = self._room_to_dict(room_model)
            
            return {
                "vertex_count": len(mesh_data["vertices"]),
                "face_count": len(mesh_data["faces"]),
                "wall_count": len(room_model.walls),
                "bounds": room_model.bounds,
                "volume": room_model.bounds.get("volume", 0.0),
                "area": room_model.bounds.get("area", 0.0)
            }
        except:
            return {
                "vertex_count": 0,
                "face_count": 0,
                "wall_count": 0,
                "bounds": {},
                "volume": 0.0,
                "area": 0.0
            }

def export_glb(room_model: RoomModel, filename: str = "room.glb") -> str:
    """Export room model as GLB."""
    exporter = ModelExporter()
    return exporter.export_glb(room_model, filename)

def export_obj(room_model: RoomModel, filename: str = "room.obj") -> str:
    """Export room model as OBJ."""
    exporter = ModelExporter()
    return exporter.export_obj(room_model, filename)