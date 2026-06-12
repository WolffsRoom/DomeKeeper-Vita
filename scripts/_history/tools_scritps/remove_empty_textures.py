import re

with open("content/map/Map.tscn", "r", encoding="utf-8") as f:
    content = f.read()

# Remove empty ImageTexture subresources
content = re.sub(r'\[sub_resource type="ImageTexture" id=\d+\]\n+', '', content)

# Remove the shader_param assignments that use these removed ImageTextures
# The ImageTextures were id: 10, 12, 15, 17, 19, 25, 27, 35
ids_to_remove = ["10", "12", "15", "17", "19", "25", "27", "35"]
for id in ids_to_remove:
    content = re.sub(r'shader_param/\w+ = SubResource\( ' + id + r' \)\n', '', content)

# Fix load_steps - we removed 8 sub_resources, so load_steps should decrease by 8
# But Godot doesn't actually strictly enforce load_steps matching exact count in 3.x, it's just a hint.
# To be safe, we'll let it be, or we can parse and decrease it.
match = re.search(r'load_steps=(\d+)', content)
if match:
    old_steps = int(match.group(1))
    new_steps = old_steps - 8
    content = content.replace(f'load_steps={old_steps}', f'load_steps={new_steps}')

with open("content/map/Map.tscn", "w", encoding="utf-8") as f:
    f.write(content)

print("Removed empty ImageTextures and their assignments from Map.tscn.")
