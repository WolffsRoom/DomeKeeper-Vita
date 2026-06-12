import re

with open('stages/manager/StageManager.gd', 'r', encoding='utf-8') as f:
    content = f.read()

broken_func = '''func get_broken_deps(path: String, visited: Dictionary) -> String:
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
		else:
			broken += "NULL:" + dep.get_file() + "\\n"
	return broken'''

content = re.sub(r'func get_broken_deps.*?\treturn broken', broken_func, content, flags=re.DOTALL)

with open('stages/manager/StageManager.gd', 'w', encoding='utf-8') as f:
    f.write(content)

print("StageManager NULL reporting added!")
