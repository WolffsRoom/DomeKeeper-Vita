import re

with open('stages/manager/StageManager.gd', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update text to just "Loading..."
content = content.replace('loadingLabel.text = "Loading... / Carregando..."', 'loadingLabel.text = "Loading..."')

# 2. Add AnimationPlayer and Bounce Animation
anim_code = '''	var font = load("res://gui/fonts/FontLarge.tres")
	if font:
		loadingLabel.add_font_override("font", font)
		
	var anim_player = AnimationPlayer.new()
	var anim = Animation.new()
	anim.add_track(Animation.TYPE_VALUE)
	anim.track_set_path(0, ".:rect_position:y")
	anim.length = 1.0
	anim.loop = true
	# Base Y position is roughly viewport height / 2 - 100.
	# We'll use relative anchors, but rect_position animation overrides anchors.
	# Actually, animating rect_position with anchors can be tricky.
	# Better to animate rect_scale for a "Bounce" or "Pulse" effect!
	anim.track_set_path(0, ".:rect_scale")
	anim.track_insert_key(0, 0.0, Vector2(1, 1))
	anim.track_insert_key(0, 0.5, Vector2(1.2, 1.2))
	anim.track_insert_key(0, 1.0, Vector2(1, 1))
	
	anim_player.add_animation("bounce", anim)
	loadingLabel.add_child(anim_player)
	anim_player.play("bounce")'''

content = re.sub(r'\tvar font = load.*?loadingLabel\.add_font_override\("font", font\)', anim_code, content, flags=re.DOTALL)

with open('stages/manager/StageManager.gd', 'w', encoding='utf-8') as f:
    f.write(content)

print("Loading bounce animation added!")
