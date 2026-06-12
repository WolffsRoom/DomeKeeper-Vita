import struct, os

IMPORT_DIR = '.import'
FIXED = 0
SKIPPED = 0
ERRORS = 0

for f in sorted(os.listdir(IMPORT_DIR)):
    if not f.endswith('.stex'):
        continue
    path = os.path.join(IMPORT_DIR, f)
    with open(path, 'rb') as fh:
        d = bytearray(fh.read())
    if len(d) < 32:
        continue
    if d[:4] != b'GDST':
        continue

    data_type = struct.unpack('<I', d[20:24])[0]
    data_size = struct.unpack('<I', d[24:28])[0]
    total = len(d)
    byte28_31 = bytes(d[28:32])

    # Expected format string for this data type
    expected_fmt = None
    if data_type == 1:  # Lossy (WebP)
        expected_fmt = b'WEBP'
    elif data_type == 0:  # Lossless (PNG)
        expected_fmt = b'PNG '

    # If bytes 28-31 match the expected format string, strip it
    if expected_fmt and byte28_31 == expected_fmt:
        # The format string is embedded in the reported data_size.
        # Strip it: remove bytes 28-31, update data_size, shrink file.
        actual_data = bytes(d[32:])  # Real image data after format string
        actual_size = len(actual_data)

        # Rebuild: 28-byte header + actual image data
        header = bytes(d[:24])
        new_data_size = data_size - 4  # or just len(actual_data), same thing
        header += struct.pack('<I', new_data_size)
        new_data = bytearray(header + actual_data)

        with open(path, 'wb') as fh:
            fh.write(new_data)
        FIXED += 1
        if FIXED <= 3:
            print(f'FIXED: {f} {struct.unpack("<I",d[4:8])[0]}x{struct.unpack("<I",d[8:12])[0]} old_dlen={data_size} -> new_dlen={new_data_size}')
    else:
        SKIPPED += 1

print(f'\nFixed: {FIXED}, Skipped: {SKIPPED}, Errors: {ERRORS}')
