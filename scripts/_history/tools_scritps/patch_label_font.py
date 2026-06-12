import re

with open('stages/manager/StageManager.gd', 'r', encoding='utf-8') as f:
    content = f.read()

new_label = '''	loadingLabel = Label.new()
	loadingLabel.text = "Loading... / Carregando..."
	loadingLabel.align = Label.ALIGN_CENTER
	loadingLabel.valign = Label.VALIGN_CENTER
	loadingLabel.anchor_left = 0.5
	loadingLabel.anchor_top = 0.5
	loadingLabel.anchor_right = 0.5
	loadingLabel.anchor_bottom = 0.5
	loadingLabel.margin_left = -400
	loadingLabel.margin_top = -100
	loadingLabel.margin_right = 400
	loadingLabel.margin_bottom = 100
	loadingLabel.visible = false
	var font = load("res://gui/fonts/FontLarge.tres")
	if font:
		loadingLabel.add_font_override("font", font)'''

content = re.sub(r'\tloadingLabel = Label\.new\(\).*?loadingLabel\.rect_scale = Vector2\(2, 2\)', new_label, content, flags=re.DOTALL)

with open('stages/manager/StageManager.gd', 'w', encoding='utf-8') as f:
    f.write(content)
