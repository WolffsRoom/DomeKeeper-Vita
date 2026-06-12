import struct, os

# Compare file structure to understand mip_info
for f in sorted(os.listdir('.import')):
    if f.endswith('.stex'):
        path = os.path.join('.import', f)
        with open(path, 'rb') as fh:
            d = fh.read()
        w, h = struct.unpack('<II', d[4:12])
        flags = struct.unpack('<I', d[12:16])[0]
        mip_info = struct.unpack('<I', d[16:20])[0]
        dtype = struct.unpack('<I', d[20:24])[0]
        dlen = struct.unpack('<I', d[24:28])[0]
        total = len(d)
        # After main data, is there extra data? total - 32 - dlen
        extra = total - 32 - dlen
        if extra > 0 or f.startswith('titlescreen') or f.startswith('de_DE') or ('electricity' in f):
            print(f"{f}: {w}x{h} fl={flags:#x} mip={mip_info:#x}({mip_info}) dtype={dtype} dlen={dlen} total={total} extra_after_data={extra}")
            if 'sheet' in f.lower() and 'sheet' not in f:
                pass
