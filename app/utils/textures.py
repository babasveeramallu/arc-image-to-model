"""Material and texture management system."""

import cv2
import numpy as np
from typing import Dict, List, Any, Optional
from pathlib import Path
import json

class TextureLibrary:
    """Manages texture library and material application."""
    
    def __init__(self, textures_dir: str = "app/static/textures"):
        self.textures_dir = Path(textures_dir)
        self.textures_dir.mkdir(parents=True, exist_ok=True)
        self.materials = self._load_materials()
        self._create_default_textures()
    
    def _load_materials(self) -> Dict[str, Dict]:
        """Load material definitions."""
        return {
            "white_paint": {
                "name": "White Paint",
                "type": "paint",
                "color": [255, 255, 255],
                "roughness": 0.8,
                "metallic": 0.0,
                "file": "white_paint.jpg"
            },
            "beige_paint": {
                "name": "Beige Paint", 
                "type": "paint",
                "color": [245, 230, 211],
                "roughness": 0.8,
                "metallic": 0.0,
                "file": "beige_paint.jpg"
            },
            "gray_paint": {
                "name": "Gray Paint",
                "type": "paint", 
                "color": [169, 169, 169],
                "roughness": 0.8,
                "metallic": 0.0,
                "file": "gray_paint.jpg"
            },
            "brick_red": {
                "name": "Red Brick",
                "type": "brick",
                "color": [200, 90, 84],
                "roughness": 0.9,
                "metallic": 0.0,
                "file": "brick_red.jpg"
            },
            "wood_oak": {
                "name": "Oak Wood",
                "type": "wood",
                "color": [222, 184, 135],
                "roughness": 0.7,
                "metallic": 0.0,
                "file": "wood_oak.jpg"
            },
            "wood_dark": {
                "name": "Dark Wood",
                "type": "wood",
                "color": [101, 67, 33],
                "roughness": 0.6,
                "metallic": 0.0,
                "file": "wood_dark.jpg"
            },
            "wallpaper_floral": {
                "name": "Floral Wallpaper",
                "type": "wallpaper",
                "color": [232, 212, 241],
                "roughness": 0.9,
                "metallic": 0.0,
                "file": "wallpaper_floral.jpg"
            },
            "concrete": {
                "name": "Concrete",
                "type": "concrete",
                "color": [128, 128, 128],
                "roughness": 0.95,
                "metallic": 0.0,
                "file": "concrete.jpg"
            }
        }
    
    def _create_default_textures(self):
        """Create default texture images if they don't exist."""
        for material_id, material in self.materials.items():
            texture_path = self.textures_dir / material["file"]
            
            if not texture_path.exists():
                self._generate_texture(material, texture_path)
    
    def _generate_texture(self, material: Dict, output_path: Path):
        """Generate a simple procedural texture."""
        size = 256
        texture = np.zeros((size, size, 3), dtype=np.uint8)
        
        # Base color
        color = material["color"]
        texture[:, :] = color
        
        # Add texture based on type
        if material["type"] == "brick":
            self._add_brick_pattern(texture, color)
        elif material["type"] == "wood":
            self._add_wood_grain(texture, color)
        elif material["type"] == "wallpaper":
            self._add_floral_pattern(texture, color)
        elif material["type"] == "concrete":
            self._add_concrete_texture(texture, color)
        else:  # paint
            self._add_paint_texture(texture, color)
        
        # Save texture
        cv2.imwrite(str(output_path), cv2.cvtColor(texture, cv2.COLOR_RGB2BGR))
    
    def _add_brick_pattern(self, texture: np.ndarray, base_color: List[int]):
        """Add brick pattern to texture."""
        h, w = texture.shape[:2]
        brick_h, brick_w = 32, 64
        
        for y in range(0, h, brick_h):
            for x in range(0, w, brick_w):
                # Offset every other row
                offset = brick_w // 2 if (y // brick_h) % 2 else 0
                x_pos = (x + offset) % w
                
                # Draw brick outline
                cv2.rectangle(texture, (x_pos, y), (x_pos + brick_w - 2, y + brick_h - 2), 
                            [c - 20 for c in base_color], 2)
    
    def _add_wood_grain(self, texture: np.ndarray, base_color: List[int]):
        """Add wood grain pattern."""
        h, w = texture.shape[:2]
        
        # Create wood grain lines
        for i in range(0, h, 8):
            noise = np.random.randint(-10, 10, w)
            y_line = i + noise
            y_line = np.clip(y_line, 0, h - 1)
            
            for x in range(w):
                if 0 <= y_line[x] < h:
                    texture[y_line[x], x] = [c - 15 for c in base_color]
    
    def _add_floral_pattern(self, texture: np.ndarray, base_color: List[int]):
        """Add simple floral pattern."""
        h, w = texture.shape[:2]
        
        # Add random dots as flowers
        for _ in range(50):
            x, y = np.random.randint(0, w), np.random.randint(0, h)
            cv2.circle(texture, (x, y), 3, [c + 20 for c in base_color], -1)
    
    def _add_concrete_texture(self, texture: np.ndarray, base_color: List[int]):
        """Add concrete texture."""
        # Add random noise
        noise = np.random.randint(-20, 20, texture.shape)
        texture = np.clip(texture.astype(int) + noise, 0, 255).astype(np.uint8)
    
    def _add_paint_texture(self, texture: np.ndarray, base_color: List[int]):
        """Add subtle paint texture."""
        # Very subtle noise for paint
        noise = np.random.randint(-5, 5, texture.shape)
        texture = np.clip(texture.astype(int) + noise, 0, 255).astype(np.uint8)
    
    def get_available_materials(self) -> Dict[str, Dict]:
        """Get list of available materials."""
        return self.materials
    
    def get_material(self, material_id: str) -> Optional[Dict]:
        """Get specific material by ID."""
        return self.materials.get(material_id)
    
    def apply_texture(self, wall_mesh, material_id: str) -> Dict[str, Any]:
        """Apply texture to wall mesh (simplified)."""
        material = self.get_material(material_id)
        
        if not material:
            return {"success": False, "error": "Material not found"}
        
        # In a full implementation, this would:
        # 1. Load the texture image
        # 2. Apply UV mapping to the mesh
        # 3. Set material properties
        
        texture_path = self.textures_dir / material["file"]
        
        return {
            "success": True,
            "material": material,
            "texture_path": str(texture_path),
            "applied_to": "wall_mesh"
        }
    
    def create_material_preview(self, material_id: str, size: int = 128) -> Optional[np.ndarray]:
        """Create small preview image of material."""
        material = self.get_material(material_id)
        if not material:
            return None
        
        texture_path = self.textures_dir / material["file"]
        
        if texture_path.exists():
            # Load and resize existing texture
            texture = cv2.imread(str(texture_path))
            texture = cv2.cvtColor(texture, cv2.COLOR_BGR2RGB)
            return cv2.resize(texture, (size, size))
        else:
            # Generate preview
            preview = np.zeros((size, size, 3), dtype=np.uint8)
            preview[:, :] = material["color"]
            return preview

def apply_texture(wall_mesh, texture_path: str) -> Dict[str, Any]:
    """Standalone function to apply texture to wall mesh."""
    library = TextureLibrary()
    
    # Find material by texture path
    for material_id, material in library.materials.items():
        if material["file"] in texture_path:
            return library.apply_texture(wall_mesh, material_id)
    
    return {"success": False, "error": "Texture not found"}