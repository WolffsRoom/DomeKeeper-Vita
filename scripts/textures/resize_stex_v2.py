import struct, os, io
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

def read_stex28(filepath):
    """Read Godot 3.x .stex file with 28-byte header (no format string)."""
    with open(filepath, "rb") as f:
        magic = f.read(4)
        if magic != b"GDST":
            return None
        width = struct.unpack("<I", f.read(4))[0]
        height = struct.unpack("<I", f.read(4))[0]
        flags = struct.unpack("<I", f.read(4))[0]
        mipmaps = struct.unpack("<I", f.read(4))[0]
        data_type = struct.unpack("<I", f.read(4))[0]
        data_size = struct.unpack("<I", f.read(4))[0]
        image_data = f.read()
    return (width, height, flags, mipmaps, data_type, data_size, image_data)

def read_stex(filepath):
    """Read .stex file; try 28-byte first, then fall back to 32-byte."""
    with open(filepath, "rb") as f:
        magic = f.read(4)
        if magic != b"GDST":
            return None
        width = struct.unpack("<I", f.read(4))[0]
        height = struct.unpack("<I", f.read(4))[0]
        flags = struct.unpack("<I", f.read(4))[0]
        mipmaps = struct.unpack("<I", f.read(4))[0]
        data_type = struct.unpack("<I", f.read(4))[0]
        data_size = struct.unpack("<I", f.read(4))[0]
        # Determine if 28-byte or 32-byte header
        remaining = f.read()
        expected_28 = 28 + data_size
        expected_32 = 32 + data_size
        actual_size = len(remaining)
        # Read format string (4 bytes) if 32-byte header
        if len(remaining) == data_size + 4:
            fmt_str = remaining[:4]
            image_data = remaining[4:]
            is_32byte = True
        elif len(remaining) == data_size:
            fmt_str = None
            image_data = remaining
            is_32byte = False
        else:
            # Can't determine, try to detect WebP magic
            if remaining[:4] == b"RIFF":
                fmt_str = None
                image_data = remaining
                is_32byte = False
            elif remaining[4:8] == b"RIFF":  # 4 bytes offset
                fmt_str = remaining[:4]
                image_data = remaining[4:]
                is_32byte = True
            else:
                fmt_str = None
                image_data = remaining
                is_32byte = False
    return (width, height, flags, mipmaps, data_type, data_size, fmt_str, image_data, is_32byte)

def write_stex28(filepath, width, height, flags, mipmaps, data_type, data_size, image_data):
    """Write Godot 3.x .stex file with 28-byte header (no format string)."""
    with open(filepath, "wb") as f:
        f.write(b"GDST")
        f.write(struct.pack("<I", width))
        f.write(struct.pack("<I", height))
        f.write(struct.pack("<I", flags))
        f.write(struct.pack("<I", mipmaps))
        f.write(struct.pack("<I", data_type))
        f.write(struct.pack("<I", data_size))
        f.write(image_data)

def resize_stex_image_28(image_data, data_type, max_size):
    """Resize WebP image data and return new data, dimensions."""
    try:
        if data_type != 1:  # WebP only
            return None, 0, 0
        img = Image.open(io.BytesIO(image_data))
        w, h = img.size
        if w <= max_size and h <= max_size:
            return None, w, h
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
        return new_data, new_w, new_h
    except Exception as e:
        return None, 0, 0

def main():
    work_dir = ".import"
    resized = 0
    fixed_header = 0
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
            width, height, flags, mipmaps, data_type, data_size, fmt_str, image_data, is_32byte = result
            
            # STEP 1: If this file has a 32-byte header, fix it to 28-byte first
            if is_32byte:
                print(f"  [FIX HEADER] {fname}")
                # Rewrite as 28-byte header, keeping all data intact
                write_stex28(path, width, height, flags, mipmaps, data_type, data_size, image_data)
                fixed_header += 1
                continue  # Re-check next pass
            
            # STEP 2: Check if should resize
            if not should_resize(fname, width, height):
                if width * height >= MAX_AREA:
                    skipped_sheet += 1
                else:
                    skipped_small += 1
                continue

            old_vram = width * height * 4
            print(f"  [RESIZE] {fname}")
            print(f"    {width}x{height} = {old_vram/1024/1024:.1f}MB VRAM")

            new_data, new_w, new_h = resize_stex_image_28(image_data, data_type, MAX_SIZE)
            if new_data is None:
                print(f"    SKIPPED (decode failed)")
                errors += 1
                continue

            old_file_size = data_size
            new_data_len = len(new_data)
            write_stex28(path, new_w, new_h, flags, mipmaps, data_type, new_data_len, new_data)

            new_vram = new_w * new_h * 4
            saved = old_vram - new_vram
            total_saved += saved
            print(f"    -> {new_w}x{new_h} = {new_vram/1024/1024:.1f}MB (saved {saved/1024/1024:.1f}MB, file {old_file_size/1024:.0f}K->{new_data_len/1024:.0f}K)")
            resized += 1

    print(f"\nResults:")
    print(f"  Headers fixed (32-byte -> 28-byte): {fixed_header}")
    print(f"  Resized: {resized}")
    print(f"  Skipped (sprite sheets): {skipped_sheet}")
    print(f"  Skipped (small enough): {skipped_small}")
    print(f"  Errors: {errors}")
    print(f"  Total VRAM saved: ~{total_saved/1024/1024:.0f} MB")

if __name__ == "__main__":
    main()
