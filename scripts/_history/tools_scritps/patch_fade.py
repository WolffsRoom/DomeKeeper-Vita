import re

with open('stages/manager/StageManager.gd', 'r', encoding='utf-8') as f:
    content = f.read()

fix_code = '''	currentStage.beforeStart()
	
	if pendingStageName != "":
		return
		
	if currentStage.fadeInTime > 0:'''

content = content.replace('	currentStage.beforeStart()\n	if currentStage.fadeInTime > 0:', fix_code)

with open('stages/manager/StageManager.gd', 'w', encoding='utf-8') as f:
    f.write(content)

print("StageManager fade overlap bug fixed!")
