import re

with open('stages/manager/StageManager.gd', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add _ready
ready_func = '''
var loadingLabel: Label

func _ready():
	loadingLabel = Label.new()
	loadingLabel.text = "Loading... / Carregando..."
	loadingLabel.align = Label.ALIGN_CENTER
	loadingLabel.valign = Label.VALIGN_BOTTOM
	loadingLabel.anchor_top = 1.0
	loadingLabel.anchor_bottom = 1.0
	loadingLabel.anchor_left = 1.0
	loadingLabel.anchor_right = 1.0
	loadingLabel.margin_left = -300
	loadingLabel.margin_top = -60
	loadingLabel.margin_right = -20
	loadingLabel.margin_bottom = -20
	loadingLabel.visible = false
	loadingLabel.rect_scale = Vector2(2, 2)
	var canvas = get_node_or_null("Canvas")
	if canvas:
		canvas.add_child(loadingLabel)

'''

# Insert after variable declarations (e.g. after sceneCache)
content = content.replace('var sceneCache = {}', 'var sceneCache = {}\n' + ready_func)

# 2. Patch _removeOldStage
remove_old = '''func _removeOldStage():
	currentStage.end()
	currentStage.emit_signal("ended")
	find_node("CurrentStage").remove_child(currentStage)
	currentStage.queue_free()
	
	if pendingStageName:
		if loadingLabel: loadingLabel.visible = true
		yield(get_tree(), "idle_frame")
		yield(get_tree(), "idle_frame")
		_addNewStage()
	elif pausedStages.size() > 0:
		pendingStage = pausedStages.pop_back()
		pendingStage.resuming = true
		_addNewStage()'''

# We need to replace the original _removeOldStage with regex because there might be trailing spaces
content = re.sub(r'func _removeOldStage\(\):.*?(?=func _addNewStage\(\):)', remove_old + '\n\n', content, flags=re.DOTALL)

# 3. Patch _addNewStage
add_new = '''func _addNewStage():
	if loadingLabel: loadingLabel.visible = false'''
content = content.replace('func _addNewStage():', add_new)

with open('stages/manager/StageManager.gd', 'w', encoding='utf-8') as f:
    f.write(content)

print("Loading screen added to StageManager!")
