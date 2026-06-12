import os, re, glob

vitabuild = r'C:\Users\wolff\Documents\SDKVita\Dome Keeper.v5.0.4\GOGVersion\VitaBuild'

# Find ALL ext_resource references and check if they exist
missing = []
for ext in ['*.tscn', '*.tres']:
    for path in glob.glob(os.path.join(vitabuild, '**', ext), recursive=True):
        try:
            with open(path, 'r', errors='ignore') as f:
                content = f.read()
            refs = re.findall(r'ext_resource path="res://([^"]+)"', content)
            for r in refs:
                full = os.path.join(vitabuild, r.replace('/', os.sep))
                if not os.path.exists(full):
                    scene_rel = os.path.relpath(path, vitabuild)
                    missing.append((scene_rel, r))
        except:
            pass

if missing:
    print(f'Still missing {len(missing)} ext_resources:')
    for scene, ref in sorted(missing):
        print(f'  {scene} -> {ref}')
else:
    print('All ext_resource references are resolved! No missing files.')
