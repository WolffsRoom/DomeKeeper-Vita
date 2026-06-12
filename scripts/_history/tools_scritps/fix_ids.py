import os
import re

for root, dirs, files in os.walk('.'):
    for name in files:
        path = os.path.join(root, name)
        
        if name.endswith('.tscn') or name.endswith('.tres'):
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            if 'MockNoise.gd' in content:
                # Find all IDs to make sure MockNoise is unique
                all_ids = [int(x) for x in re.findall(r'id=([0-9]+)\]', content)]
                if len(all_ids) > 0:
                    max_id = max(all_ids)
                    
                    # Find the current MockNoise id
                    mock_match = re.search(r'\[ext_resource path="res://MockNoise.gd" type="Script" id=([0-9]+)\]', content)
                    if mock_match:
                        current_mock_id = mock_match.group(1)
                        # Check if it's duplicated (appears more than once in the file)
                        if content.count('id=' + current_mock_id + ']') > 1:
                            new_mock_id = str(max_id + 1)
                            # Replace the ext_resource ID
                            content = content.replace(f'id={current_mock_id}]', f'id={new_mock_id}]', 1)
                            # Replace all script = ExtResource( current_mock_id ) with new_mock_id
                            content = content.replace(f'script = ExtResource( {current_mock_id} )', f'script = ExtResource( {new_mock_id} )')
                            with open(path, 'w', encoding='utf-8') as f:
                                f.write(content)
                                print(f"Fixed duplicate ID in {path}")
