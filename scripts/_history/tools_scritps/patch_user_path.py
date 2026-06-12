import re

with open('stages/manager/StageManager.gd', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('if f.open("ux0:load_error.txt", File.WRITE) == OK:', 'if f.open("user://load_error.txt", File.WRITE) == OK:')

with open('stages/manager/StageManager.gd', 'w', encoding='utf-8') as f:
    f.write(content)

print("Changed path to user://load_error.txt")
