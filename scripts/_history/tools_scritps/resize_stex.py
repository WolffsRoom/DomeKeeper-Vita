"""
resize_stex.py - Downscale large background/concept art .stex textures for Vita.

Only targets textures that are clearly NOT sprite sheets.
Sprite sheets are kept at original resolution to preserve frame coordinates.

.stex format (Godot 3 StreamTexture):
  Offset 0-3:   "GDST" magic
  Offset 4-7:   width (uint32 LE)
  Offset 8-11:  height (uint32 LE)
  Offset 12-15: flags (uint32 LE)
  Offset 16-19: mipmap data size / offset
  Offset 20-23: data type (1 = WebP)
  Offset 24-27: data length (uint32 LE)
  Offset 28-31: image format string ("WEBP", "PNG ", etc.)
  Offset 32+:   image data (RIFF WEBP ... for WebP)
"""

import os
import struct
import io
from PIL import Image

MAX_SIZE = 512
MAX_AREA = 300000

def is_sprite_sheet(filename):
    name = filename.lower()
    for indicator in ["sheet", "spritesheet", "sprite_sheet", "playercolo", "player_colo"]:
        if indicator in name:
            return True
    return False

def should_resize(filename, width, height):
    if is_sprite_sheet(filename):
        return False
    if width <= MAX_SIZE and height <= MAX_SIZE:
        return False
    if width * height < MAX_AREA:
        return False
    return True

def read_stex(filepath):
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

def resize_stex_image(image_data, data_type, fmt_str, max_size):
    try:
        if data_type == 1:  # WebP
            img = Image.open(io.BytesIO(image_data))
        else:
            return None, 0, 0, None
        
        w, h = img.size
        if w <= max_size and h <= max_size:
            return None, w, h, None
        
        if w > h:
            new_w = max_size
            new_h = max(1, int(h * max_size / w))
        else:
            new_h = max_size
            new_w = max(1, int(w * max_size / h))
        
        img_resized = img.resize((new_w, new_h), Image.LANCZOS)
        buf = io.BytesIO()
        img_resized.save(buf, format="WEBP", lossless=False, quality=85)
        buf.seek(0)
        new_data = buf.read()
        return new_data, new_w, new_h, fmt_str
    except Exception as e:
        return None, 0, 0, None

def main():
    work_dir = ".import"
    resized = 0
    skipped_sheet = 0
    skipped_small = 0
    errors = 0
    total_saved = 0

    for root, dirs, files in os.walk(work_dir):
        for fname in files:
            if not fname.lower().endswith(".stex"):
                continue
            path = os.path.join(root, fname)
            
            result = read_stex(path)
            if result is None:
                continue
            width, height, flags, mip_info, data_type, data_len, fmt_str, image_data = result

            if not should_resize(fname, width, height):
                if width * height >= MAX_AREA:
                    skipped_sheet += 1
                else:
                    skipped_small += 1
                continue

            old_vram = width * height * 4
            print(f"  {fname}")
            print(f"    {width}x{height} = {old_vram/1024/1024:.1f}MB VRAM")

            new_data, new_w, new_h, _ = resize_stex_image(image_data, data_type, fmt_str, MAX_SIZE)
            if new_data is None:
                print(f"    SKIPPED (decode failed)")
                errors += 1
                continue

            old_size = len(image_data)
            new_data_len = len(new_data)
            write_stex(path, new_w, new_h, flags, mip_info, data_type, new_data_len, fmt_str, new_data)
            
            new_vram = new_w * new_h * 4
            saved = old_vram - new_vram
            total_saved += saved
            print(f"    -> {new_w}x{new_h} = {new_vram/1024/1024:.1f}MB (saved {saved/1024/1024:.1f}MB, file {old_size/1024:.0f}K->{new_data_len/1024:.0f}K)")
            resized += 1

    print(f"\nResults:")
    print(f"  Resized: {resized}")
    print(f"  Skipped (sprite sheets): {skipped_sheet}")
    print(f"  Skipped (small enough): {skipped_small}")
    print(f"  Errors: {errors}")
    print(f"  Total VRAM saved: ~{total_saved/1024/1024:.0f} MB")

if __name__ == "__main__":
    main()
