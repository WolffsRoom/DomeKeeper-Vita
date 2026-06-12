"""
Comprehensive restore: copies ALL files from OriginalPCK that are missing in VitaBuild.
Also scans .gd files for dynamic string references to res:// paths.
"""
import os, re, glob, shutil

vitabuild = r'C:\Users\wolff\Documents\SDKVita\Dome Keeper.v5.0.4\GOGVersion\VitaBuild'
original = r'C:\Users\wolff\Documents\SDKVita\Dome Keeper.v5.0.4\GOGVersion\OriginalPCK'

# --- Phase 1: Collect ALL res:// references from .tscn, .tres, .gd, .import ---
print("=== Phase 1: Scanning all resource references ===")
all_refs = set()
for ext in ['*.tscn', '*.tres', '*.gd', '*.cfg']:
    for path in glob.glob(os.path.join(vitabuild, '**', ext), recursive=True):
        try:
            with open(path, 'r', errors='ignore') as f:
                content = f.read()
            refs = re.findall(r'res://([^"\'\)]+)', content)
            for r in refs:
                # Strip trailing brackets or whitespace if any got captured
                r = r.strip().rstrip(']')
                all_refs.add(r)
        except:
            pass

print(f"  Found {len(all_refs)} unique res:// references")

# --- Phase 2: Find missing files ---
print("\n=== Phase 2: Finding missing files ===")
missing = []
for ref in sorted(all_refs):
    dst = os.path.join(vitabuild, ref.replace('/', os.sep))
    if not os.path.exists(dst):
        src = os.path.join(original, ref.replace('/', os.sep))
        if os.path.exists(src):
            missing.append(ref)

print(f"  {len(missing)} files missing in VitaBuild that exist in OriginalPCK")

# --- Phase 3: Restore ---
print("\n=== Phase 3: Restoring files ===")
total_size = 0
for ref in missing:
    src = os.path.join(original, ref.replace('/', os.sep))
    dst = os.path.join(vitabuild, ref.replace('/', os.sep))
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)
    size = os.path.getsize(dst)
    total_size += size
    print(f'  [RESTORED] {size//1024:6d} KB  {ref}')
    
    # Also restore .import if needed
    src_imp = src + '.import'
    dst_imp = dst + '.import'
    if os.path.exists(src_imp) and not os.path.exists(dst_imp):
        shutil.copy2(src_imp, dst_imp)
        print(f'             + .import')

# --- Phase 4: Verify remaining missing ---
print("\n=== Phase 4: Verification ===")
still_missing = []
for ref in sorted(all_refs):
    dst = os.path.join(vitabuild, ref.replace('/', os.sep))
    if not os.path.exists(dst):
        still_missing.append(ref)

print(f"\n=== SUMMARY ===")
print(f"  Restored: {len(missing)} files ({total_size//1024//1024} MB)")
print(f"  Still missing (not in OriginalPCK): {len(still_missing)}")
if still_missing:
    for ref in still_missing:
        print(f"    {ref}")
