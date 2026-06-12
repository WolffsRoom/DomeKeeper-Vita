import re

with open('stages/manager/StageManager.gd', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the while loop with a single poll or a fixed iteration
new_process = '''func _process(delta):
	if loader:
		if loadingLabel and not loadingLabel.visible:
			loadingLabel.visible = true
		
		# Poll a fixed number of times per frame to guarantee we don't freeze the Vita GPU!
		# OS.get_ticks_msec() can be static during a frame on some consoles.
		var polls = 0
		while polls < 2:
			var err = loader.poll()
			polls += 1
			if err == ERR_FILE_EOF: # Finished
				var scene = loader.get_resource()
				sceneCache[pendingStageName_cache] = scene
				currentStage = scene.instance()
				loader = null
				
				_finish_addNewStage()
				break
			elif err != OK:
				if loadingLabel: loadingLabel.text = "LOAD ERROR: " + str(err)
				loader = null
				break'''

content = re.sub(r'func _process\(delta\):.*?elif err != OK:\s+loader = null\s+break', new_process, content, flags=re.DOTALL)

with open('stages/manager/StageManager.gd', 'w', encoding='utf-8') as f:
    f.write(content)

print("StageManager interactive loading fixed to avoid OS.get_ticks_msec() freeze!")
