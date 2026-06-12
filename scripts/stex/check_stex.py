import struct, os, io

# Compare header sizes between working and broken stex files
with open('.import/electricity sprite.png-559e496c5a534629ec09e618226ec16d.stex', 'rb') as f:
    d_bad = f.read()

for f in os.listdir('.import'):
    if 'de_DE' in f and f.endswith('.stex'):
        with open(os.path.join('.import', f), 'rb') as fh:
            d_de = fh.read()
        break

with open('.import/titlescreen.png-d0df210e8aca1db5125cdac6864ca1e9.stex', 'rb') as f:
    d_title = f.read()

print("de_DE bytes 28-31:", repr(d_de[28:32]), "is RIFF?", d_de[28:32] == b'RIFF')
print("electricity sprite bytes 28-31:", repr(d_bad[28:32]), "is RIFF?", d_bad[28:32] == b'RIFF')
print("titlescreen bytes 28-31:", repr(d_title[28:32]), "is RIFF?", d_title[28:32] == b'RIFF')

# Check: total = 28 + data_len?
for label, d in [("de_DE", d_de), ("electricity", d_bad), ("titlescreen", d_title)]:
    dlen = struct.unpack('<I', d[24:28])[0]
    total = len(d)
    expected_28 = 28 + dlen
    expected_32 = 32 + dlen
    print(f"{label}: total={total}, 28+dlen={expected_28}, 32+dlen={expected_32}, match_28={total==expected_28} match_32={total==expected_32}")
