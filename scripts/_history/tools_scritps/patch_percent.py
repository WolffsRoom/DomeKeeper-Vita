import re

with open('stages/manager/StageManager.gd', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the poll loop to add percentage
new_poll_loop = '''			var err = loader.poll()
			polls += 1
			
			if loadingLabel and is_instance_valid(loader):
				var st = loader.get_stage()
				var total = loader.get_stage_count()
				var pct = 0
				if total > 0:
					pct = (st * 100) / total
				if err == OK:
					loadingLabel.text = "Loading... " + str(pct) + "% (" + str(st) + "/" + str(total) + ")"
			
			if err == ERR_FILE_EOF:'''

content = content.replace('''			var err = loader.poll()
			polls += 1
			if err == ERR_FILE_EOF:''', new_poll_loop)

# Update the error handler to include the stage info
new_error_handler = '''			elif err != OK:
				var st = loader.get_stage()
				var total = loader.get_stage_count()
				var detailed = "ERROR: " + str(err) + " at " + str(st) + "/" + str(total) + "\\n"'''

content = content.replace('''			elif err != OK:
				var detailed = "ERROR: " + str(err) + "\\n"''', new_error_handler)

with open('stages/manager/StageManager.gd', 'w', encoding='utf-8') as f:
    f.write(content)

print("StageManager percentage reporting added!")
