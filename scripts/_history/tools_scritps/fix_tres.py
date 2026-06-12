import os
import re

for root, dirs, files in os.walk('.'):
    for name in files:
        if name.endswith('.tres'):
            path = os.path.join(root, name)
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if script = ExtResource is incorrectly placed right after [gd_resource]
            match = re.search(r'(\[gd_resource type="Resource" .*?\]\n)(script = ExtResource\( [0-9]+ \)\n)', content)
            if match:
                script_line = match.group(2)
                # Remove it from the top
                content = content.replace(script_line, '', 1)
                # Add it right after [resource]
                content = content.replace('[resource]\n', '[resource]\n' + script_line)
                
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print("Fixed " + path)
