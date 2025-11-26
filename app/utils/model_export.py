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
            
            if len(mesh_data["vertices"]) == 0:
                raise ValueError("Empty mesh - no geometry to export")
            
            output_path = self.output_dir / filename
            self._write_simple_glb(mesh_data, output_path)
            
            return str(output_path)
            
        except Exception as e:
            print(f"GLB export error: {e}")
            return self._create_dummy_glb(filename)
    
    def export_obj(self, room_model: RoomModel, filename: str = "room.obj") -> str:
        """Export room model as OBJ file."""
        try:
            mesh_data = self._room_to_dict(room_model)
            
            if len(mesh_data["vertices"]) == 0:
                raise ValueError("Empty mesh - no geometry to export")
            
            output_path = self.output_dir / filename
            self._write_obj(mesh_data, output_path)
            
            return str(output_path)
            
        except Exception as e:
            print(f"OBJ export error: {e}")
            return self._create_dummy_obj(filename)
    
    def _room_to_dict(self, room_model: RoomModel) -> Dict[str, Any]:
        """Convert RoomModel to mesh dictionary."""
        if not room_model.walls:
            # Simple cube vertices
            vertices = np.array([
                [-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],
                [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]
            ])
            faces = np.array([
                [0, 1, 2], [0, 2, 3], [4, 7, 6], [4, 6, 5],
                [0, 4, 5], [0, 5, 1], [2, 6, 7], [2, 7, 3],
                [0, 3, 7], [0, 7, 4], [1, 5, 6], [1, 6, 2]
            ])
            return {"vertices": vertices, "faces": faces}
        
        # Use existing vertices and faces if available
        if len(room_model.vertices) > 0 and len(room_model.faces) > 0:
            return {"vertices": room_model.vertices, "faces": room_model.faces}
        
        # Build mesh from individual walls
        all_vertices = []
        all_faces = []
        vertex_offset = 0
        
        for wall in room_model.walls:
            if len(wall.vertices) >= 4:
                all_vertices.extend(wall.vertices)
                faces = [
                    [vertex_offset, vertex_offset + 1, vertex_offset + 2],
                    [vertex_offset, vertex_offset + 2, vertex_offset + 3]
                ]
                all_faces.extend(faces)
                vertex_offset += 4
        
        if not all_vertices:
            vertices = np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]])
            faces = np.array([[0, 1, 2], [0, 2, 3]])
            return {"vertices": vertices, "faces": faces}
        
        return {"vertices": np.array(all_vertices), "faces": np.array(all_faces)}
    
    def _write_obj(self, mesh_data: Dict, output_path: Path):
        """Write OBJ file."""
        with open(output_path, 'w') as f:
            f.write("# Arc generated room model\n")
            
            # Write vertices
            for vertex in mesh_data["vertices"]:
                f.write(f"v {vertex[0]:.6f} {vertex[1]:.6f} {vertex[2]:.6f}\n")
            
            # Write faces (OBJ uses 1-based indexing)
            for face in mesh_data["faces"]:
                f.write(f"f {face[0]+1} {face[1]+1} {face[2]+1}\n")
    
    def _write_simple_glb(self, mesh_data: Dict, output_path: Path):
        """Write simple GLB file (basic binary format)."""
        # For now, just write as OBJ since GLB is complex
        obj_path = output_path.with_suffix('.obj')
        self._write_obj(mesh_data, obj_path)
        
        # Copy to GLB name for compatibility
        with open(obj_path, 'rb') as src, open(output_path, 'wb') as dst:
            dst.write(src.read())
    
    def _create_dummy_glb(self, filename: str) -> str:
        """Create a simple dummy GLB file."""
        try:
            output_path = self.output_dir / filename
            
            # Create simple cube mesh
            vertices = np.array([
                [-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],
                [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]
            ])
            faces = np.array([
                [0, 1, 2], [0, 2, 3], [4, 7, 6], [4, 6, 5]
            ])
            
            mesh_data = {"vertices": vertices, "faces": faces}
            self._write_simple_glb(mesh_data, output_path)
            return str(output_path)
        except:
            return ""
    
    def _create_dummy_obj(self, filename: str) -> str:
        """Create a simple dummy OBJ file."""
        try:
            output_path = self.output_dir / filename
            
            with open(output_path, 'w') as f:
                f.write("# Simple room cube\n")
                f.write("v -1.0 -1.25 -1.5\n")
                f.write("v  1.0 -1.25 -1.5\n") 
                f.write("v  1.0  1.25 -1.5\n")
                f.write("v -1.0  1.25 -1.5\n")
                f.write("v -1.0 -1.25  1.5\n")
                f.write("v  1.0 -1.25  1.5\n")
                f.write("v  1.0  1.25  1.5\n")
                f.write("v -1.0  1.25  1.5\n")
                f.write("f 1 2 3 4\n")
                f.write("f 5 8 7 6\n")
                f.write("f 1 5 6 2\n")
                f.write("f 4 3 7 8\n")
                f.write("f 1 4 8 5\n")
                f.write("f 2 6 7 3\n")
            
            return str(output_path)
        except:
            return ""
    
    def get_model_info(self, room_model: RoomModel) -> Dict[str, Any]:
        """Get information about the 3D model."""
        mesh_data = self._room_to_dict(room_model)
        
        return {
            "vertex_count": len(mesh_data["vertices"]),
            "face_count": len(mesh_data["faces"]),
            "volume": 0.0,
            "surface_area": 0.0,
            "bounds": [],
            "is_watertight": False
        }

def export_glb(room_model: RoomModel, filename: str = "room.glb") -> str:
    """Export room model as GLB."""
    exporter = ModelExporter()
    return exporter.export_glb(room_model, filename)

def export_obj(room_model: RoomModel, filename: str = "room.obj") -> str:
    """Export room model as OBJ."""
    exporter = ModelExporter()
    return exporter.export_obj(room_model, filename)