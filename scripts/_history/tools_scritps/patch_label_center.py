import re

with open('stages/manager/StageManager.gd', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the anchor setup
content = re.sub(r'loadingLabel\.anchor_top = 1\.0.*?loadingLabel\.margin_bottom = -20', '''loadingLabel.anchor_top = 0.5
	loadingLabel.anchor_bottom = 0.5
	loadingLabel.anchor_left = 0.5
	loadingLabel.anchor_right = 0.5
	loadingLabel.margin_left = -300
	loadingLabel.margin_top = -60
	loadingLabel.margin_right = 300
	loadingLabel.margin_bottom = 60''', content, flags=re.DOTALL)

with open('stages/manager/StageManager.gd', 'w', encoding='utf-8') as f:
    f.write(content)

print("Loading screen moved to center!")
