# -*- coding: utf-8 -*-
# Extraido e limpo do blob original (fix_stex_pc.py) durante a organizacao do projeto.
# Caminhos absolutos para GOGVersion/VitaBuild estao embutidos no script.

"""
REVERT the broken bulk stex fix.

What fix_all_stex.py did INCORRECTLY:
  The correct Godot 3 StreamTexture WebP format is:
    [28:32] = b'WEBP'   <- Godot prefix
    [32:36] = b'RIFF'   <- start of actual RIFF WebP data   ← CORRECT, not a bug!
    [36:N]  = rest of RIFF WebP

  fix_all_stex.py saw 'RIFF' at [32:36] and inserted a size field, producing:
    [28:32] = b'WEBP'
    [32:36] = numeric_size   <- WRONG insertion
    [36:40] = b'RIFF'        <- RIFF WebP pushed +4 bytes

  This broke PC (WebPDecodeRGBA receives garbage before 'RIFF').

This script detects and removes the incorrectly inserted size field,
restoring all files to the original working format.
"""

import struct, os

import_dir = r'C:\Users\wolff\Documents\SDKVita\Dome Keeper.v5.0.4\GOGVersion\VitaBuild\.import'

RIFF_BYTES = b'RIFF'
RIFF_AS_INT = struct.unpack('<I', RIFF_BYTES)[0]  # 1179011410

reverted = 0
skipped = 0
errors = 0

stex_files = [f for f in os.listdir(import_dir) if f.endswith('.stex')]
print(f"Scanning {len(stex_files)} .stex files...")

for fn in stex_files:
    fp = os.path.join(import_dir, fn)
    try:
        with open(fp, 'rb') as f:
            data = f.read()
    except Exception as e:
        print(f"  READ ERROR {fn}: {e}")
        errors += 1
        continue

    # Need at least 40 bytes, GDST header, WEBP at 28
    if len(data) < 40 or data[:4] != b'GDST' or data[28:32] != b'WEBP':
        skipped += 1
        continue

    size_field = struct.unpack_from('<I', data, 32)[0]

    # If [32:36] is already 'RIFF' → already in original format, skip
    if size_field == RIFF_AS_INT:
        skipped += 1
        continue

    # If [32:36] is NOT 'RIFF' but [36:40] IS 'RIFF' → our broken fix was applied
    if data[36:40] != RIFF_BYTES:
        skipped += 1  # Unknown format, don't touch
        continue

    # Revert: remove the incorrectly inserted size field at [32:36]
    # Original: header(28) + 'WEBP'(4) + 'RIFF'(4) + rest
    # Fixed:   header(28) + 'WEBP'(4) + size(4)   + 'RIFF'(4) + rest
    # Revert:  remove size → header(28) + 'WEBP'(4) + 'RIFF'(4) + rest

    riff_and_rest = data[36:]          # 'RIFF' + original RIFF WebP data
    new_data_size = 4 + len(riff_and_rest)  # 'WEBP' + RIFF_data

    new_stex = bytearray(data[:28])    # Keep original 28-byte GDST header
    struct.pack_into('<I', new_stex, 24, new_data_size)  # Update data_size field
    new_stex += b'WEBP'               # Restore 'WEBP' prefix
    new_stex += riff_and_rest         # Restore original RIFF WebP (starts with 'RIFF')

    try:
        with open(fp, 'wb') as f:
            f.write(bytes(new_stex))
        reverted += 1
    except Exception as e:
        print(f"  WRITE ERROR {fn}: {e}")
        errors += 1

print(f"\nDone!  Reverted: {reverted}  |  Skipped (already OK): {skipped}  |  Errors: {errors}")
