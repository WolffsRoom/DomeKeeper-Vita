import re

with open('stages/manager/StageManager.gd', 'r', encoding='utf-8') as f:
    content = f.read()

recursive_func = '''func get_broken_deps(path: String, visited: Dictionary) -> String:
	if visited.has(path): return ""
	visited[path] = true
	var broken = ""
	var deps = ResourceLoader.get_dependencies(path)
	for dep in deps:
		var tl = ResourceLoader.load_interactive(dep)
		if tl:
			var err = tl.poll()
			while err == OK:
				err = tl.poll()
			if err != ERR_FILE_EOF:
				broken += dep.get_file() + ":" + str(err) + "\\n"
				broken += get_broken_deps(dep, visited)
	return broken

func _startNewStage():'''

content = content.replace('func _startNewStage():', recursive_func)

new_error_handler = '''			elif err != OK:
				var detailed = "ERROR: " + str(err) + "\\n"
				detailed += get_broken_deps("res://" + pendingStageResource_cache, {})
				
				var f = File.new()
				if f.open("ux0:load_error.txt", File.WRITE) == OK:
					f.store_string(detailed)
					f.close()
				
				if loadingLabel:
					loadingLabel.text = detailed
					loadingLabel.rect_scale = Vector2(0.5, 0.5)
				loader = null
				break'''

content = re.sub(r'\t\t\telif err != OK:.*?\t\t\t\tbreak', new_error_handler, content, flags=re.DOTALL)

with open('stages/manager/StageManager.gd', 'w', encoding='utf-8') as f:
    f.write(content)

print("StageManager recursive error reporting added!")
