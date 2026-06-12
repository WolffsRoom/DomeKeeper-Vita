import re

# 1. Clean Map.tscn
with open("content/map/Map.tscn", "r", encoding="utf-8") as f:
    tscn = f.read()

# Find all ViewportTexture subresources and their IDs
viewport_textures = {}
for match in re.finditer(r'\[sub_resource type="ViewportTexture" id=(\d+)\]\nviewport_path = NodePath\("([^"]+)"\)', tscn):
    viewport_textures[match.group(1)] = match.group(2)

print("Found ViewportTextures to remove:", viewport_textures)

# Remove the ViewportTexture definitions
tscn = re.sub(r'\[sub_resource type="ViewportTexture" id=\d+\]\nviewport_path = NodePath\("[^"]+"\)\n*', '', tscn)

# Remove their usages
for id in viewport_textures.keys():
    # Remove from textures (e.g. texture = SubResource( 33 ))
    tscn = re.sub(r'texture = SubResource\( ' + id + r' \)\n', '', tscn)
    # Remove from shader params (e.g. shader_param/light_map = SubResource( 13 ))
    tscn = re.sub(r'shader_param/\w+ = SubResource\( ' + id + r' \)\n', '', tscn)

with open("content/map/Map.tscn", "w", encoding="utf-8") as f:
    f.write(tscn)

# 2. Update Map.gd
with open("content/map/Map.gd", "r", encoding="utf-8") as f:
    gd = f.read()

ready_additions = """
	# Setup ViewportTextures dynamically to prevent ERR_FILE_CORRUPT on Vita
	$BackgroundTileRender.texture = $ViewportRenderBackground.get_texture()
	$MainTileRender.texture = $ViewportRender.get_texture()
	$LightSprite.texture = $ViewportLights.get_texture()
	
	$ViewportRenderBackground/MapAnchor/BackgroundEdges.texture = $ViewportRocks.get_texture()
	var bg_mat = $ViewportRenderBackground/MapAnchor/BackgroundEdges.material
	bg_mat.set_shader_param("light_map", $ViewportLights.get_texture())
	bg_mat.set_shader_param("bg_alpha_map", $ViewportBackgroundAlpha.get_texture())
	bg_mat.set_shader_param("background_rocks", $ViewportRocks.get_texture())
	
	$ViewportRender/MapAnchor/MainStones.texture = $ViewportRocks.get_texture()
	var main_mat = $ViewportRender/MapAnchor/MainStones.material
	main_mat.set_shader_param("crack_impact", $ViewportCrackImpact.get_texture())
	main_mat.set_shader_param("light_map", $ViewportLights.get_texture())
"""

# Inject into _ready
gd = gd.replace("func _ready():\n", "func _ready():\n" + ready_additions)

with open("content/map/Map.gd", "w", encoding="utf-8") as f:
    f.write(gd)

print("Applied ViewportTexture fix.")
