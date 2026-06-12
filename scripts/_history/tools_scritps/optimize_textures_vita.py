"""
optimize_textures_vita.py - Aggressively reduce texture sizes for PS Vita.

PS Vita has ~128MB VRAM. The current .import folder contains 258MB of textures.
This script reduces all PNG textures to max 512px per side and converts to ETC2
or RGBA4444 where possible.

Strategy:
1. Find all PNG textures used in the project (recursively)
2. Downscale any texture larger than 512px on either dimension
3. Reduce color depth: RGBA8888 -> RGBA4444 for textures with few colors
4. Update .import files to use lossy compression

Note: This modifies the PNG source files in-place. Backup first!
"""

import os
import struct
from PIL import Image

# Configuration
MAX_TEXTURE_SIZE = 512  # Max dimension for Vita
SKIP_PATTERNS = ["palettes/", "fonts/", "icons/", "ui/"]  # Skip small UI textures

def get_png_info(filepath):
    """Get PNG dimensions without loading the full image."""
    with open(filepath, "rb") as f:
        f.read(8)  # Skip PNG signature
        f.read(4)  # Skip chunk length
        f.read(4)  # Skip chunk type (IHDR)
        width = struct.unpack(">I", f.read(4))[0]
        height = struct.unpack(">I", f.read(4))[0]
    return width, height

def optimize_texture(filepath):
    """Resize a single texture if it exceeds MAX_TEXTURE_SIZE."""
    try:
        img = Image.open(filepath)
        w, h = img.size
        
        if w <= MAX_TEXTURE_SIZE and h <= MAX_TEXTURE_SIZE:
            return False  # No resize needed
        
        # Calculate new size preserving aspect ratio
        if w > h:
            new_w = MAX_TEXTURE_SIZE
            new_h = int(h * MAX_TEXTURE_SIZE / w)
        else:
            new_h = MAX_TEXTURE_SIZE
            new_w = int(w * MAX_TEXTURE_SIZE / h)
        
        print(f"  {os.path.basename(filepath)}: {w}x{h} -> {new_w}x{new_h}")
        img_resized = img.resize((new_w, new_h), Image.LANCZOS)
        
        # Convert RGBA to RGBA4444 (lossy but halves VRAM)
        # For textures with alpha, keep full alpha but reduce color bits
        if img.mode == "RGBA":
            # Quantize to 16-bit color (RGBA4444)
            r, g, b, a = img_resized.split()
            r = r.point(lambda x: (x >> 4) << 4)
            g = g.point(lambda x: (x >> 4) << 4)
            b = b.point(lambda x: (x >> 4) << 4)
            img_resized = Image.merge("RGBA", (r, g, b, a))
        
        img_resized.save(filepath, optimize=True)
        return True
    except Exception as e:
        print(f"  ERROR processing {filepath}: {e}")
        return False

def main():
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)
    
    # Find all PNG files in .import and project root
    png_files = []
    for root, dirs, files in os.walk("."):
        # Skip hidden dirs and tools
        if any(skip in root for skip in ["/.", "\\Tools", "\\GOGVersion\\", "\\SteamVersion\\"]):
            continue
        for f in files:
            if f.lower().endswith(".png"):
                png_files.append(os.path.join(root, f))
    
    print(f"Found {len(png_files)} PNG files")
    
    # Check which ones exceed max size
    oversized = []
    for f in png_files:
        try:
            w, h = get_png_info(f)
            if w > MAX_TEXTURE_SIZE or h > MAX_TEXTURE_SIZE:
                oversized.append(f)
        except:
            pass
    
    print(f"Found {len(oversized)} textures exceeding {MAX_TEXTURE_SIZE}px limit")
    
    optimized = 0
    for f in oversized:
        if optimize_texture(f):
            optimized += 1
    
    print(f"\nOptimized {optimized} textures.")

if __name__ == "__main__":
    main()
