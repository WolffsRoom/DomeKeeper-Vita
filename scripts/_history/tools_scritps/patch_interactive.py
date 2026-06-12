import re

with open('stages/manager/StageManager.gd', 'r', encoding='utf-8') as f:
    content = f.read()

# Add loader state variables
state_vars = '''var loader: ResourceInteractiveLoader = null
var pendingStageResource_cache: String = ""
var pendingStageName_cache: String = ""
var stage_data_cache: Array = []

func _process(delta):
	if loader:
		if loadingLabel and not loadingLabel.visible:
			loadingLabel.visible = true
		
		# Yield occasionally so main thread can pump AnimationPlayer and draw frames!
		var time_max = 10 
		var t = OS.get_ticks_msec()
		while OS.get_ticks_msec() < t + time_max:
			var err = loader.poll()
			if err == ERR_FILE_EOF: # Finished
				var scene = loader.get_resource()
				sceneCache[pendingStageName_cache] = scene
				currentStage = scene.instance()
				loader = null
				
				_finish_addNewStage()
				break
			elif err != OK:
				loader = null
				break
'''

# Insert after sceneCache
content = content.replace('var sceneCache = {}', 'var sceneCache = {}\n' + state_vars)

# Replace _addNewStage
add_new_stage = '''func _addNewStage():
	var data = initData[pendingStageResource]
	initData.erase(pendingStageResource)
	if pendingStage:
		if loadingLabel: loadingLabel.visible = false
		currentStage = pendingStage
		pendingStage = null
		pendingStageResource_cache = pendingStageResource
		pendingStageName_cache = pendingStageName
		stage_data_cache = data
		pendingStageResource = ""
		pendingStageName = ""
		_finish_addNewStage()
	else:
		if sceneCache.has(pendingStageName):
			if loadingLabel: loadingLabel.visible = false
			currentStage = sceneCache.get(pendingStageName).instance()
			pendingStageResource_cache = pendingStageResource
			pendingStageName_cache = pendingStageName
			stage_data_cache = data
			pendingStageResource = ""
			pendingStageName = ""
			_finish_addNewStage()
		else:
			if loadingLabel: loadingLabel.visible = true
			loader = ResourceLoader.load_interactive("res://" + pendingStageResource)
			pendingStageResource_cache = pendingStageResource
			pendingStageName_cache = pendingStageName
			stage_data_cache = data
			pendingStageResource = ""
			pendingStageName = ""
			set_process(true)

func _finish_addNewStage():
	if loadingLabel: loadingLabel.visible = false
	set_process(false)
	
	currentStage.beforeReady()
	find_node("CurrentStage").add_child(currentStage)
	
	if not currentStage.resuming:
		currentStage.connect("request_end", self, "_stopOldStage")
		currentStage.build(stage_data_cache)
		
	emit_signal("stage_started")
	
	currentStage.beforeStart()
	if currentStage.fadeInTime > 0:
		 / ScreenOverlay.fadeInCallback(currentStage.fadeInTime, self, "_startNewStage")
	else:
		 / ScreenOverlay.setClear()
		_startNewStage()'''

# Replace from func _addNewStage() to before func _startNewStage()
content = re.sub(r'func _addNewStage\(\):.*?func _startNewStage\(\):', add_new_stage + '\n\nfunc _startNewStage():', content, flags=re.DOTALL)

# Add pivot offset to loading label
pivot_code = '''	loadingLabel.margin_bottom = 100
	loadingLabel.rect_pivot_offset = Vector2(400, 100)'''
content = content.replace('	loadingLabel.margin_bottom = 100', pivot_code)

with open('stages/manager/StageManager.gd', 'w', encoding='utf-8') as f:
    f.write(content)

print("StageManager interactive loading and animation fixed!")
