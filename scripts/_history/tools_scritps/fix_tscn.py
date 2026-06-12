import os
import re

def fix_tscn(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    video_ids = []
    new_lines = []
    
    for line in lines:
        match = re.search(r'\[ext_resource .*? type="VideoStream" id=([a-zA-Z0-9]+)\]', line)
        if match:
            video_ids.append(match.group(1))
            continue # skip this line
        new_lines.append(line)
        
    if not video_ids:
        return
        
    final_lines = []
    for line in new_lines:
        skip = False
        for vid in video_ids:
            if re.search(r'stream = ExtResource\(\s*' + vid + r'\s*\)', line):
                skip = True
                break
        if not skip:
            final_lines.append(line)
            
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(final_lines)
    print("Fixed", filepath)

for root, dirs, files in os.walk('.'):
    for file in files:
        if file.endswith('.tscn'):
            fix_tscn(os.path.join(root, file))
