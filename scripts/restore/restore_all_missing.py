import os, re, glob, shutil

vitabuild = r'C:\Users\wolff\Documents\SDKVita\Dome Keeper.v5.0.4\GOGVersion\VitaBuild'
original = r'C:\Users\wolff\Documents\SDKVita\Dome Keeper.v5.0.4\GOGVersion\OriginalPCK'

# Find ALL ext_resource references that are missing
missing_refs = set()
for ext in ['*.tscn', '*.tres']:
    for path in glob.glob(os.path.join(vitabuild, '**', ext), recursive=True):
        try:
            with open(path, 'r', errors='ignore') as f:
                content = f.read()
            refs = re.findall(r'ext_resource path="res://([^"]+)"', content)
            for r in refs:
                full = os.path.join(vitabuild, r.replace('/', os.sep))
                if not os.path.exists(full):
                    missing_refs.add(r)
        except:
            pass

restored = 0
not_in_original = 0

for ref in sorted(missing_refs):
    src = os.path.join(original, ref.replace('/', os.sep))
    dst = os.path.join(vitabuild, ref.replace('/', os.sep))
    
    if os.path.exists(src):
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
        size = os.path.getsize(dst)
        print(f'[RESTAURADO] {size//1024:6d} KB  {ref}')
        restored += 1
        
        # Also restore .import if applicable
        src_imp = src + '.import'
        dst_imp = dst + '.import'
        if os.path.exists(src_imp) and not os.path.exists(dst_imp):
            shutil.copy2(src_imp, dst_imp)
            print(f'  + .import')
    else:
        print(f'[NAO NO ORIGINAL] {ref}')
        not_in_original += 1

print(f'\nRestaurados: {restored}')
print(f'Nao encontrados no OriginalPCK: {not_in_original}')
