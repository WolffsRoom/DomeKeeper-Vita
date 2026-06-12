import os
import re

def clean_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'MockNoise' not in content:
        return False
    
    original = content
    
    # Remove orphan [sub_resource type="Resource" id=X]\nscript = ExtResource( Y )\n\n blocks
    # These are OpenSimplexNoise remnants - completely unused
    content = re.sub(r'\[sub_resource type="Resource" id=[0-9]+\]\nscript = ExtResource\( [0-9]+ \)\n\n', '', content)
    content = re.sub(r'\[sub_resource type="Resource" id=[0-9]+\]\nscript = ExtResource\( [0-9]+ \)\n', '', content)
    
    # Now remove all MockNoise ext_resource lines
    content = re.sub(r'\[ext_resource path="res://MockNoise\.gd" type="Script" id=[0-9]+\]\n', '', content)
    
    # Fix load_steps count if changed
    removed_resources = (original.count('[sub_resource type="Resource"') - content.count('[sub_resource type="Resource"'))
    removed_ext = (original.count('[ext_resource path="res://MockNoise') - content.count('[ext_resource path="res://MockNoise'))
    total_removed = removed_resources + removed_ext
    
    if total_removed > 0:
        # Update load_steps
        def fix_load_steps(m):
            current = int(m.group(1))
            new_val = current - total_removed
            return m.group(0).replace('load_steps=' + str(current), 'load_steps=' + str(new_val))
        content = re.sub(r'\[gd_scene load_steps=([0-9]+)', fix_load_steps, content)
    
    if content != original:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Cleaned {path} (removed {total_removed} MockNoise resources)")
        return True
    return False

for root, dirs, files in os.walk('.'):
    for name in files:
        if name.endswith('.tscn') or name.endswith('.tres'):
            clean_file(os.path.join(root, name))

print("Done!")
