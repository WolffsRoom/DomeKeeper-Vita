"""
restore_atlas_stex.py - Restore .stex files for atlas textures that were wrongly resized.

Some textures are used as AtlasTexture sources in .tscn files, meaning they have
absolute pixel coordinates for sprite frames. These must NOT be resized.

This script finds all such textures by scanning for AtlasTexture definitions in .tscn
files, then re-generates the .stex files at their ORIGINAL dimensions from the source PNGs.
"""

import os
import struct
import io
import re
from PIL import Image

# Read all .tscn files and find AtlasTexture -> ExtResource mappings
def find_atlas_texture_refs(project_dir):
    """Scan all .tscn files and return set of source texture paths."""
    atlas_paths = set()
    
    for root, dirs, files in os.walk(project_dir):
        # Skip .import, Tools, other versions
        parts = root.replace('\\', '/').split('/')
        skip = False
        for p in parts:
            if p.startswith('.') or p in ('Tools',):
                skip = True
                break
        if skip:
            continue
        
        for f in files:
            if not f.endswith('.tscn'):
                continue
            
            filepath = os.path.join(root, f)
            with open(filepath, 'r', encoding='utf-8', errors='replace') as fp:
                try:
                    content = fp.read()
                except:
                    continue
            
            # Find all [ext_resource] lines
            ext_resources = {}
            for match in re.finditer(r'\[ext_resource path="([^"]+)" type="[^"]*" id=(\d+)\]', content):
                ext_resources[match.group(2)] = match.group(1)
            
            # Find all AtlasTexture sub_resources with atlas = ExtResource(N)
            for match in re.finditer(r'atlas = ExtResource\( (\d+) \)', content):
                res_id = match.group(1)
                if res_id in ext_resources:
                    atlas_paths.add(ext_resources[res_id])
    
    return atlas_paths

def read_stex(filepath):
    """Read .stex file; return (width, height, flags, data) or None."""
    with open(filepath, "rb") as f:
        magic = f.read(4)
        if magic != b"GDST":
            return None
        width = struct.unpack("<I", f.read(4))[0]
        height = struct.unpack("<I", f.read(4))[0]
        flags = struct.unpack("<I", f.read(4))[0]
        mip_info = struct.unpack("<I", f.read(4))[0]
        data_type = struct.unpack("<I", f.read(4))[0]
        data_len = struct.unpack("<I", f.read(4))[0]
        fmt_str = f.read(4)
        image_data = f.read()
    return (width, height, flags, mip_info, data_type, data_len, fmt_str, image_data)

def write_stex(filepath, width, height, flags, mip_info, data_type, data_len, fmt_str, image_data):
    with open(filepath, "wb") as f:
        f.write(b"GDST")
        f.write(struct.pack("<I", width))
        f.write(struct.pack("<I", height))
        f.write(struct.pack("<I", flags))
        f.write(struct.pack("<I", mip_info))
        f.write(struct.pack("<I", data_type))
        f.write(struct.pack("<I", data_len))
        f.write(fmt_str)
        f.write(image_data)

def get_source_png_path(res_path):
    """Convert res:// path to actual file path."""
    return res_path.replace("res://", "")

def encode_as_stex(source_image_path, original_width, original_height):
    """Encode a source PNG as GDST+WebP .stex content."""
    try:
        img = Image.open(source_image_path)
        w, h = img.size
        
        # Always use original dimensions (restore to full size)
        restore_w = original_width
        restore_h = original_height
        
        # Resize to original dimensions if needed
        if w != restore_w or h != restore_h:
            img = img.resize((restore_w, restore_h), Image.LANCZOS)
        
        # Encode as WebP
        buf = io.BytesIO()
        img.save(buf, format="WEBP", lossless=False, quality=90)
        buf.seek(0)
        webp_data = buf.read()
        
        return (restore_w, restore_h, webp_data)
    except Exception as e:
        print(f"    ERROR: {e}")
        return None

def main():
    project_dir = os.getcwd()
    print(f"Project: {project_dir}")
    
    # Step 1: Find all atlas texture paths
    print("\nScanning .tscn files for AtlasTexture references...")
    atlas_paths = find_atlas_texture_refs(project_dir)
    print(f"Found {len(atlas_paths)} unique atlas texture paths")
    
    # Step 2: For each atlas texture, check if it was resized and restore
    import_dir = os.path.join(project_dir, ".import")
    restored = 0
    errors = 0
    already_ok = 0
    
    for res_path in sorted(atlas_paths):
        # Find the .import metadata file
        rel_png_path = get_source_png_path(res_path)
        # The .import file sits next to the PNG
        import_meta = os.path.join(project_dir, rel_png_path + ".import")
        if not os.path.exists(import_meta):
            print(f"  [NO META] {rel_png_path}")
            continue
        
        # Read the import metadata to get the .stex destination
        with open(import_meta, 'r', encoding='utf-8') as f:
            meta = f.read()
        match = re.search(r'path="res://\.import/([^"]+)"', meta)
        if not match:
            print(f"  [NO PATH] {rel_png_path}")
            continue
        
        stex_name = match.group(1)
        stex_path = os.path.join(import_dir, stex_name)
        
        if not os.path.exists(stex_path):
            print(f"  [NO STEX] {stex_name}")
            continue
        
        # Read current .stex to check dimensions
        stex_data = read_stex(stex_path)
        if stex_data is None:
            print(f"  [BAD STEX] {stex_name}")
            continue
        
        current_w, current_h = stex_data[0], stex_data[1]
        
        # Read source PNG to get original dimensions
        source_png_path = os.path.join(project_dir, rel_png_path)
        if not os.path.exists(source_png_path):
            print(f"  [NO SRC] {rel_png_path}")
            continue
        
        src_img = Image.open(source_png_path)
        orig_w, orig_h = src_img.size
        
        # If current dimensions already match original, skip
        if current_w == orig_w and current_h == orig_h:
            already_ok += 1
            continue
        
        print(f"  RESTORING: {stex_name}")
        print(f"    {current_w}x{current_h} -> {orig_w}x{orig_h}")
        
        # Re-encode from source PNG at original size
        result = encode_as_stex(source_png_path, orig_w, orig_h)
        if result is None:
            errors += 1
            continue
        
        new_w, new_h, webp_data = result
        # Write new .stex (keep original flags/metadata except dimensions)
        write_stex(stex_path, new_w, new_h, 
                   stex_data[2], stex_data[3], stex_data[4], 
                   len(webp_data), stex_data[6], webp_data)
        restored += 1
        print(f"    OK ({len(webp_data)} bytes written)")
    
    print(f"\nResults:")
    print(f"  Restored: {restored}")
    print(f"  Already correct: {already_ok}")
    print(f"  Errors: {errors}")

if __name__ == "__main__":
    main()
