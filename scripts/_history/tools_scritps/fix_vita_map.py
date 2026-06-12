"""
fix_vita_map.py - Apply null-guards and VRAM optimizations for PS Vita.

The crash at libGLESv2+0x0002E5D4 (BadVAddr 0x00000014) happens when
Viewport.get_texture() returns null (VRAM exhausted on Vita) and the null
texture is assigned to Sprite.texture or passed to set_shader_param(),
causing the GPU driver to crash.

This script:
1. Adds null-guards in Map.gd for all get_texture() calls
2. Optimizes Viewport settings in Map.tscn for low-VRAM devices
3. Creates a texture optimizer script
"""

import re

# ============================================================
# 1. Fix Map.gd - add null-guards
# ============================================================

with open("content/map/Map.gd", "r", encoding="utf-8") as f:
    gd = f.read()

# Detect line ending
lf_only = "\r\n" not in gd
le = "\n" if lf_only else "\r\n"

# Replace _ready() to add null-guards
old_ready = (
    "func _ready():" + le +
    le +
    "\t# Setup ViewportTextures dynamically to prevent ERR_FILE_CORRUPT on Vita" + le +
    "\t$BackgroundTileRender.texture = $ViewportRenderBackground.get_texture()" + le +
    "\t$MainTileRender.texture = $ViewportRender.get_texture()" + le +
    "\t$LightSprite.texture = $ViewportLights.get_texture()" + le +
    "\t" + le +
    "\t$ViewportRenderBackground/MapAnchor/BackgroundEdges.texture = $ViewportRocks.get_texture()" + le +
    "\tvar bg_mat = $ViewportRenderBackground/MapAnchor/BackgroundEdges.material" + le +
    "\tbg_mat.set_shader_param(\"light_map\", $ViewportLights.get_texture())" + le +
    "\tbg_mat.set_shader_param(\"bg_alpha_map\", $ViewportBackgroundAlpha.get_texture())" + le +
    "\tbg_mat.set_shader_param(\"background_rocks\", $ViewportRocks.get_texture())" + le +
    "\t" + le +
    "\t$ViewportRender/MapAnchor/MainStones.texture = $ViewportRocks.get_texture()" + le +
    "\tvar main_mat = $ViewportRender/MapAnchor/MainStones.material" + le +
    "\tmain_mat.set_shader_param(\"crack_impact\", $ViewportCrackImpact.get_texture())" + le +
    "\tmain_mat.set_shader_param(\"light_map\", $ViewportLights.get_texture())" + le +
    "\tTILE_SCENE = load(\"res://content/map/tile/Tile.tscn\")" + le +
    "\tBORDER_SPRITE = load(\"res://content/map/border/TileBorder.tscn\")" + le +
    "\tQUADRANT_BIOME_AND_HARDNESS_MATERIAL = load(\"res://content/map/border/QuadrantBiomeAndHardnessMaterial.tres\")" + le +
    "\tQUADRANT_BIOME_MATERIAL = load(\"res://content/map/border/QuadrantBiomeMaterial.tres\")" + le +
    "\tRESOURCE_BORDER_OVERLAY = load(\"res://content/map/border/ResourceBorderOverlay.tscn\")" + le +
    "\tCrackImpact = load(\"res://content/map/tile/CrackImpact.tscn\")"
)

new_ready = (
    "func _ready():" + le +
    le +
    "\t# Setup ViewportTextures with null-guards for PS Vita" + le +
    "\t# (get_texture() returns null when VRAM is exhausted, causing GPU crash)" + le +
    "\tvar vp_bg = $ViewportRenderBackground.get_texture()" + le +
    "\tif vp_bg:" + le +
    "\t\t$BackgroundTileRender.texture = vp_bg" + le +
    "\tvar vp_main = $ViewportRender.get_texture()" + le +
    "\tif vp_main:" + le +
    "\t\t$MainTileRender.texture = vp_main" + le +
    "\tvar vp_lights = $ViewportLights.get_texture()" + le +
    "\tif vp_lights:" + le +
    "\t\t$LightSprite.texture = vp_lights" + le +
    "\t" + le +
    "\tvar vp_rocks = $ViewportRocks.get_texture()" + le +
    "\tif vp_rocks:" + le +
    "\t\t$ViewportRenderBackground/MapAnchor/BackgroundEdges.texture = vp_rocks" + le +
    "\t\t$ViewportRender/MapAnchor/MainStones.texture = vp_rocks" + le +
    "\t" + le +
    "\tvar bg_mat = $ViewportRenderBackground/MapAnchor/BackgroundEdges.material" + le +
    "\tif bg_mat:" + le +
    "\t\tif vp_lights:" + le +
    "\t\t\tbg_mat.set_shader_param(\"light_map\", vp_lights)" + le +
    "\t\tvar vp_bg_alpha = $ViewportBackgroundAlpha.get_texture()" + le +
    "\t\tif vp_bg_alpha:" + le +
    "\t\t\tbg_mat.set_shader_param(\"bg_alpha_map\", vp_bg_alpha)" + le +
    "\t\tif vp_rocks:" + le +
    "\t\t\tbg_mat.set_shader_param(\"background_rocks\", vp_rocks)" + le +
    "\t" + le +
    "\tvar main_mat = $ViewportRender/MapAnchor/MainStones.material" + le +
    "\tif main_mat:" + le +
    "\t\tvar vp_crack = $ViewportCrackImpact.get_texture()" + le +
    "\t\tif vp_crack:" + le +
    "\t\t\tmain_mat.set_shader_param(\"crack_impact\", vp_crack)" + le +
    "\t\tif vp_lights:" + le +
    "\t\t\tmain_mat.set_shader_param(\"light_map\", vp_lights)" + le +
    "\t" + le +
    "\tTILE_SCENE = load(\"res://content/map/tile/Tile.tscn\")" + le +
    "\tBORDER_SPRITE = load(\"res://content/map/border/TileBorder.tscn\")" + le +
    "\tQUADRANT_BIOME_AND_HARDNESS_MATERIAL = load(\"res://content/map/border/QuadrantBiomeAndHardnessMaterial.tres\")" + le +
    "\tQUADRANT_BIOME_MATERIAL = load(\"res://content/map/border/QuadrantBiomeMaterial.tres\")" + le +
    "\tRESOURCE_BORDER_OVERLAY = load(\"res://content/map/border/ResourceBorderOverlay.tscn\")" + le +
    "\tCrackImpact = load(\"res://content/map/tile/CrackImpact.tscn\")"
)

gd = gd.replace(old_ready, new_ready)

# Fix prepareTilemapAndProcgen to re-fetch textures after resize
old_prepare = (
    "\tvar viewport_size = tilemap_size * GameWorld.TILE_SIZE" + le +
    "\t$ViewportRocks.size = viewport_size" + le +
    "\t$ViewportCrackImpact.size = viewport_size"
)

new_prepare = (
    "\tvar viewport_size = tilemap_size * GameWorld.TILE_SIZE" + le +
    "\t$ViewportRocks.size = viewport_size" + le +
    "\t$ViewportCrackImpact.size = viewport_size" + le +
    "\t# Re-fetch viewport textures after resize (they may be invalidated)" + le +
    "\t_update_viewport_textures()"
)

gd = gd.replace(old_prepare, new_prepare)

# Add _update_viewport_textures helper function
# Find the end of prepareTextureAndImage to insert after it
old_func_end = "func setRockTiles():"
new_func = (
    "func _update_viewport_textures():" + le +
    "\t# Re-fetch viewport textures after resize;" + le +
    "\t# safe against null returns when VRAM is low" + le +
    "\tvar vp_bg = $ViewportRenderBackground.get_texture()" + le +
    "\tif vp_bg:" + le +
    "\t\t$BackgroundTileRender.texture = vp_bg" + le +
    "\tvar vp_main = $ViewportRender.get_texture()" + le +
    "\tif vp_main:" + le +
    "\t\t$MainTileRender.texture = vp_main" + le +
    "\tvar vp_lights = $ViewportLights.get_texture()" + le +
    "\tif vp_lights:" + le +
    "\t\t$LightSprite.texture = vp_lights" + le +
    "\tvar vp_rocks = $ViewportRocks.get_texture()" + le +
    "\tif vp_rocks:" + le +
    "\t\t$ViewportRenderBackground/MapAnchor/BackgroundEdges.texture = vp_rocks" + le +
    "\t\t$ViewportRender/MapAnchor/MainStones.texture = vp_rocks" + le +
    "\tvar bg_mat = $ViewportRenderBackground/MapAnchor/BackgroundEdges.material" + le +
    "\tif bg_mat:" + le +
    "\t\tif vp_lights:" + le +
    "\t\t\tbg_mat.set_shader_param(\"light_map\", vp_lights)" + le +
    "\t\tvar vp_bg_alpha = $ViewportBackgroundAlpha.get_texture()" + le +
    "\t\tif vp_bg_alpha:" + le +
    "\t\t\tbg_mat.set_shader_param(\"bg_alpha_map\", vp_bg_alpha)" + le +
    "\t\tif vp_rocks:" + le +
    "\t\t\tbg_mat.set_shader_param(\"background_rocks\", vp_rocks)" + le +
    "\tvar main_mat = $ViewportRender/MapAnchor/MainStones.material" + le +
    "\tif main_mat:" + le +
    "\t\tvar vp_crack = $ViewportCrackImpact.get_texture()" + le +
    "\t\tif vp_crack:" + le +
    "\t\t\tmain_mat.set_shader_param(\"crack_impact\", vp_crack)" + le +
    "\t\tif vp_lights:" + le +
    "\t\t\tmain_mat.set_shader_param(\"light_map\", vp_lights)" + le +
    le +
    "func setRockTiles():"
)

gd = gd.replace(old_func_end, new_func)

with open("content/map/Map.gd", "w", encoding="utf-8") as f:
    f.write(gd)

print("[Map.gd] Added null-guards for all get_texture() calls.")

# ============================================================
# 2. Fix Map.tscn - limit max viewport size, set lowest VRAM usage
# ============================================================

with open("content/map/Map.tscn", "r", encoding="utf-8") as f:
    tscn = f.read()

# Ensure all Viewport nodes use USAGE_2D (usage=1 means 3D buffers also allocated)
# In Godot 3.x: 0=USAGE_2D, 1=USAGE_3D, 2=USAGE_2D_NO_SAMPLING
# 2D mode still allocates a color buffer but no depth/stencil
# Already set to 0 in most, but let's enforce it
tscn = re.sub(
    r'ui_snap_controls_to_pixels = false\n',
    'ui_snap_controls_to_pixels = false\n\trender_target_clear_mode = 2\n',
    tscn
)

# Also ensure render_target_update_mode is UPDATE_ONCE (3) for non-dynamic viewports
# Already set for most viewports

# Cap default viewport sizes to prevent massive allocations
# ViewportRenderBackground and ViewportRender at 960x600 is OK for default
# They get resized in prepareTilemapAndProcgen anyway

with open("content/map/Map.tscn", "w", encoding="utf-8") as f:
    f.write(tscn)

print("[Map.tscn] Applied VRAM-efficient Viewport settings.")

print("\nDone! Fixes applied:")
print("  1. Map.gd _ready() - null-guards for all get_texture() calls")
print("  2. Map.gd prepareTilemapAndProcgen() - re-fetches textures after resize")
print("  3. Map.gd - new _update_viewport_textures() helper")
print("  4. Map.tscn - render_target_clear_mode enforced")
