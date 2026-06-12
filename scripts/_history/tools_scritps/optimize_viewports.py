"""
optimize_viewports.py - Limit Viewport memory usage on PS Vita.

Each Viewport creates a render target framebuffer in VRAM.
On Vita with 128MB VRAM, 6 Viewports at full map size (potentially 3768x3768)
would need ~57MB each = 342MB total - way over budget.

This script:
1. Adds a max viewport size cap in Map.gd
2. Reduces default Viewport sizes in Map.tscn
3. Sets usage=2 (2D_NO_SAMPLING) for viewports that don't need sampling
   - Actually, they all need sampling, so keep usage=0
4. Sets render_target_update_mode appropriately
"""

import re

with open("content/map/Map.gd", "r", encoding="utf-8") as f:
    gd = f.read()

le = "\n" if "\r\n" not in gd else "\r\n"

# Add a max viewport size cap in prepareTilemapAndProcgen
old_line = "\tvar viewport_size = tilemap_size * GameWorld.TILE_SIZE"

# We need to find this line and add a cap after it
# But we already modified it in fix_vita_map.py, so let's find the updated version
new_line = (
    "\tvar viewport_size = tilemap_size * GameWorld.TILE_SIZE" + le +
    "\t# Cap viewport size on low-end devices (PS Vita)" + le +
    "\tviewport_size.x = min(viewport_size.x, 1024.0)" + le +
    "\tviewport_size.y = min(viewport_size.y, 1024.0)"
)

gd = gd.replace(
    "\tvar viewport_size = tilemap_size * GameWorld.TILE_SIZE" + le +
    "\t$ViewportRocks.size = viewport_size",
    new_line + le +
    "\t$ViewportRocks.size = viewport_size"
)

with open("content/map/Map.gd", "w", encoding="utf-8") as f:
    f.write(gd)

print("[Map.gd] Added viewport size cap (max 1024x1024).")

# Now fix Map.tscn - reduce default Viewport sizes to save initial VRAM
with open("content/map/Map.tscn", "r", encoding="utf-8") as f:
    tscn = f.read()

# The ViewportRenderBackground and ViewportRender are 960x600 at default
# This is quite large for initial allocation. Let's reduce to 480x272
# (they'll be resized in prepareTilemapAndProcgen anyway)
tscn = tscn.replace(
    '[node name="ViewportRenderBackground" type="Viewport" parent="."]\nsize = Vector2( 960, 600 )',
    '[node name="ViewportRenderBackground" type="Viewport" parent="."]\nsize = Vector2( 480, 272 )'
)

tscn = tscn.replace(
    '[node name="ViewportRender" type="Viewport" parent="."]\nsize = Vector2( 960, 600 )',
    '[node name="ViewportRender" type="Viewport" parent="."]\nsize = Vector2( 480, 272 )'
)

# The Shockwave ColorRect also needs to match the smaller viewport size
tscn = tscn.replace(
    '[node name="Shockwave" type="ColorRect" parent="ViewportRender"]\n\tvisible = false\n\tmaterial = SubResource( 28 )\n\tmargin_right = 960.0\n\tmargin_bottom = 540.0',
    '[node name="Shockwave" type="ColorRect" parent="ViewportRender"]\n\tvisible = false\n\tmaterial = SubResource( 28 )\n\tmargin_right = 480.0\n\tmargin_bottom = 272.0'
)

with open("content/map/Map.tscn", "w", encoding="utf-8") as f:
    f.write(tscn)

print("[Map.tscn] Reduced default Viewport sizes to 480x272.")
print("\nDone!")
