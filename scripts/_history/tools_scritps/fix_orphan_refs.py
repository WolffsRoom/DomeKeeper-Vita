import os
import re

# The noise .tres files are now broken - they reference script ExtResource that no longer exists
# Since they are only used by GDScript code via preload(), and the GDScript uses .get_noise_2d()
# which we'll replace with a local function, we need to make them valid empty Resources

noise_tres_files = [
    r'content\map\generation\biome_noise.tres',
    r'content\map\generation\hardness_noise.tres',
    r'content\map\generation\viability_large_noise.tres',
    r'content\map\generation\viability_small_noise.tres',
    r'content\shared\opensimplexnoise.tres',
    r'content\map\tile\noise1.tres',
    r'content\map\tile\noise2.tres',
    r'content\map\tile\noise3.tres',
    r'content\map\tile\noise4.tres',
    r'content\map\tile\noise5.tres',
]

valid_resource = '[gd_resource type=\"Resource\" format=2]\n\n[resource]\n'

for path in noise_tres_files:
    if os.path.exists(path):
        with open(path, 'w', encoding='utf-8') as f:
            f.write(valid_resource)
        print('Cleaned: ' + path)

# Also fix any other .tres that reference MockNoise ext_resource that was removed
for root, dirs, files in os.walk('.'):
    for name in files:
        if name.endswith('.tres'):
            path = os.path.join(root, name)
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            # If the resource block references ext_resource that doesn't exist
            if 'script = ExtResource(' in content and '[ext_resource' not in content:
                # Remove the orphan script reference
                content = re.sub(r'script = ExtResource\( [0-9]+ \)\n', '', content)
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print('Fixed orphan ref: ' + path)

print('Done!')
