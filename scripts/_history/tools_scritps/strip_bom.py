import os

def remove_bom(path):
    with open(path, 'rb') as f:
        data = f.read()
    if data.startswith(b'\xef\xbb\xbf'):
        print('Removing BOM from ' + path)
        with open(path, 'wb') as f:
            f.write(data[3:])

for root, dirs, files in os.walk('.'):
    for name in files:
        if name.endswith('.tscn') or name.endswith('.tres') or name.endswith('.gd'):
            remove_bom(os.path.join(root, name))
