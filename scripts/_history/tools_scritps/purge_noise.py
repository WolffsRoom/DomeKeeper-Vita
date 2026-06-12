import os
import re

for root, dirs, files in os.walk('.'):
    for name in files:
        path = os.path.join(root, name)
        
        if name.endswith('.gd'):
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            if 'OpenSimplexNoise' in content or 'NoiseTexture' in content:
                content = content.replace('export (OpenSimplexNoise)', 'export (Resource)')
                content = content.replace('var biome_noise: OpenSimplexNoise', 'var biome_noise: Resource')
                content = content.replace('var hardness_noise: OpenSimplexNoise', 'var hardness_noise: Resource')
                content = content.replace('var viability_large_noise: OpenSimplexNoise', 'var viability_large_noise: Resource')
                content = content.replace('var viability_small_noise: OpenSimplexNoise', 'var viability_small_noise: Resource')
                content = content.replace(': OpenSimplexNoise', ': Resource')
                content = content.replace('OpenSimplexNoise.new()', 'preload("res://MockNoise.gd").new()')
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
        elif name.endswith('.tscn') or name.endswith('.tres'):
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            if 'OpenSimplexNoise' in content or 'NoiseTexture' in content:
                # Add ext_resource for MockNoise if needed
                if 'type="OpenSimplexNoise"' in content:
                    # Find highest ext_resource id
                    ext_matches = re.findall(r'\[ext_resource .*? id=([0-9]+)\]', content)
                    max_id = max([int(x) for x in ext_matches]) if ext_matches else 0
                    mock_id = str(max_id + 1)
                    mock_ext = f'[ext_resource path="res://MockNoise.gd" type="Script" id={mock_id}]\n'
                    
                    # Insert mock_ext after the last ext_resource, or after gd_scene/gd_resource
                    if '[ext_resource' in content:
                        content = re.sub(r'(?=\n\[sub_resource|\n\[node|\n\[resource)', '\n' + mock_ext, content, count=1)
                    else:
                        content = re.sub(r'\]\n', ']\n\n' + mock_ext, content, count=1)
                    
                    # Replace OpenSimplexNoise
                    content = content.replace('type="OpenSimplexNoise"', 'type="Resource"')
                    content = re.sub(r'(\[sub_resource type="Resource" id=[0-9]+\]\n)', r'\1script = ExtResource( ' + mock_id + r' )\n', content)
                    content = re.sub(r'(\[gd_resource type="Resource" .*?\]\n)', r'\1script = ExtResource( ' + mock_id + r' )\n', content)

                # Replace NoiseTexture with ImageTexture
                content = content.replace('type="NoiseTexture"', 'type="ImageTexture"')
                content = re.sub(r'\nnoise = SubResource\( [0-9]+ \)', '', content)
                content = re.sub(r'\nseamless = true', '', content)
                content = re.sub(r'\nperiod = [0-9\.]+', '', content)
                content = re.sub(r'\nwidth = [0-9]+', '', content)
                content = re.sub(r'\nheight = [0-9]+', '', content)
                content = re.sub(r'\npersistence = [0-9\.]+', '', content)
                content = re.sub(r'\nlacunarity = [0-9\.]+', '', content)
                content = re.sub(r'\nseed = [0-9\.\-]+', '', content)
                content = re.sub(r'\noctaves = [0-9\.]+', '', content)
                content = re.sub(r'\nflags = [0-9]+', '', content)
                
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)

print("Purged OpenSimplexNoise and NoiseTexture!")
