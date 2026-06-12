"""
restore_atlas_stex_v2.py - Restore atlas .stex files with CORRECT Godot-imported dimensions.

Atlas textures must match Godot's import dimensions (respecting size_limit) because
the AtlasTexture coordinates in .tscn files refer to those exact dimensions.
"""

import os
import struct
import io
import re
from PIL import Image

def find_atlas_texture_refs(project_dir):
    """Scan all .tscn files and return set of res:// source texture paths."""
    atlas_paths = set()
    for root, dirs, files in os.walk(project_dir):
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
            ext_resources = {}
            for match in re.finditer(r'\[ext_resource path="([^"]+)" type="[^"]*" id=(\d+)\]', content):
                ext_resources[match.group(2)] = match.group(1)
            for match in re.finditer(r'atlas = ExtResource\( (\d+) \)', content):
                res_id = match.group(1)
                if res_id in ext_resources:
                    atlas_paths.add(ext_resources[res_id])
    return atlas_paths

def read_import_meta(meta_path):
    """Parse .png.import metadata, return dict of params."""
    params = {'size_limit': 0, 'lossy_quality': 0.7}
    with open(meta_path, 'r', encoding='utf-8') as f:
        for line in f:
            m = re.match(r'^size_limit=(\d+)', line)
            if m:
                params['size_limit'] = int(m.group(1))
            m = re.match(r'^compress/lossy_quality=([\d.]+)', line)
            if m:
                params['lossy_quality'] = float(m.group(1))
    return params

def compute_godot_dimensions(src_w, src_h, size_limit):
    """Compute the dimensions Godot would import at given size_limit."""
    if size_limit <= 0:
        return src_w, src_h
    max_dim = max(src_w, src_h)
    if max_dim <= size_limit:
        return src_w, src_h
    scale = size_limit / max_dim
    new_w = max(1, int(src_w * scale))
    new_h = max(1, int(src_h * scale))
    return new_w, new_h

def write_stex28(filepath, width, height, flags, mipmaps, data_type, data_size, image_data):
    """Write Godot 3.x .stex with 28-byte header."""
    with open(filepath, "wb") as f:
        f.write(b"GDST")
        f.write(struct.pack("<I", width))
        f.write(struct.pack("<I", height))
        f.write(struct.pack("<I", flags))
        f.write(struct.pack("<I", mipmaps))
        f.write(struct.pack("<I", data_type))
        f.write(struct.pack("<I", data_size))
        f.write(image_data)

def main():
    project_dir = os.getcwd()
    print(f"Project: {project_dir}")

    print("\nScanning .tscn files for AtlasTexture references...")
    atlas_paths = find_atlas_texture_refs(project_dir)
    print(f"Found {len(atlas_paths)} unique atlas texture paths")

    import_dir = os.path.join(project_dir, ".import")
    restored = 0
    errors = 0
    already_ok = 0

    for res_path in sorted(atlas_paths):
        rel_png_path = res_path.replace("res://", "")
        import_meta = os.path.join(project_dir, rel_png_path + ".import")
        if not os.path.exists(import_meta):
            print(f"  [NO META] {rel_png_path}")
            continue

        with open(import_meta, 'r', encoding='utf-8') as f:
            meta_content = f.read()
        stex_match = re.search(r'path="res://\.import/([^"]+)"', meta_content)
        if not stex_match:
            print(f"  [NO PATH] {rel_png_path}")
            continue

        stex_name = stex_match.group(1)
        stex_path = os.path.join(import_dir, stex_name)
        if not os.path.exists(stex_path):
            print(f"  [NO STEX] {stex_name}")
            continue

        # Read current stex (28-byte header format)
        with open(stex_path, 'rb') as f:
            d = f.read()
        if d[:4] != b'GDST':
            print(f"  [BAD MAGIC] {stex_name}")
            continue
        current_w = struct.unpack('<I', d[4:8])[0]
        current_h = struct.unpack('<I', d[8:12])[0]
        flags = struct.unpack('<I', d[12:16])[0]
        mipmaps = struct.unpack('<I', d[16:20])[0]
        data_type = struct.unpack('<I', d[20:24])[0]
        data_size = struct.unpack('<I', d[24:28])[0]

        source_png_path = os.path.join(project_dir, rel_png_path)
        if not os.path.exists(source_png_path):
            print(f"  [NO SRC] {rel_png_path}")
            continue

        src_img = Image.open(source_png_path)
        src_w, src_h = src_img.size

        # Parse import metadata for size_limit
        size_limit = 0
        for m in re.finditer(r'size_limit=(\d+)', meta_content):
            size_limit = int(m.group(1))
        quality = 0.7
        for m in re.finditer(r'compress/lossy_quality=([\d.]+)', meta_content):
            quality = float(m.group(1))

        # Compute Godot-imported dimensions
        target_w, target_h = compute_godot_dimensions(src_w, src_h, size_limit)

        # If already at correct size, skip
        if current_w == target_w and current_h == target_h:
            already_ok += 1
            continue

        print(f"  RESTORING: {stex_name}")
        print(f"    {current_w}x{current_h} -> {target_w}x{target_h} (src={src_w}x{src_h}, size_limit={size_limit})")

        try:
            if target_w != src_w or target_h != src_h:
                img = src_img.resize((target_w, target_h), Image.LANCZOS)
            else:
                img = src_img

            buf = io.BytesIO()
            img.save(buf, format="WEBP", lossless=False, quality=int(quality * 100))
            buf.seek(0)
            webp_data = buf.read()

            write_stex28(stex_path, target_w, target_h, flags, mipmaps, data_type, len(webp_data), webp_data)
            restored += 1
            print(f"    OK ({len(webp_data)} bytes)")
        except Exception as e:
            errors += 1
            print(f"    ERROR: {e}")

    print(f"\nResults:")
    print(f"  Restored: {restored}")
    print(f"  Already correct: {already_ok}")
    print(f"  Errors: {errors}")

if __name__ == "__main__":
    main()
