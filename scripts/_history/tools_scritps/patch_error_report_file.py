import re

with open('stages/manager/StageManager.gd', 'r', encoding='utf-8') as f:
    content = f.read()

new_error_handler = '''			elif err != OK:
				var detailed = "ERROR: " + str(err) + "\n"
				var deps = ResourceLoader.get_dependencies("res://" + pendingStageResource_cache)
				for dep in deps:
					var tl = ResourceLoader.load_interactive(dep)
					if tl:
						var de = tl.poll()
						while de == OK:
							de = tl.poll()
						if de != ERR_FILE_EOF:
							detailed += dep.get_file() + ":" + str(de) + "\n"
				
				# Write to file for easy reading
				var f = File.new()
				if f.open("user://load_error.txt", File.WRITE) == OK:
					f.store_string(detailed)
					f.close()
				
				if loadingLabel:
					loadingLabel.text = detailed
					loadingLabel.rect_scale = Vector2(0.5, 0.5) # Make it fit on screen
				loader = null
				break'''

content = re.sub(r'\t\t\telif err != OK:.*?\t\t\t\tbreak', new_error_handler, content, flags=re.DOTALL)

with open('stages/manager/StageManager.gd', 'w', encoding='utf-8') as f:
    f.write(content)

print("StageManager extended error reporting added with file writing!")
