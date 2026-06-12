import re

with open('stages/manager/StageManager.gd', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the broken string lines
broken_str = 'var detailed = "ERROR: " + str(err) + "\n"\n'
fixed_str = 'var detailed = "ERROR: " + str(err) + "\\n"\n'
content = content.replace(broken_str, fixed_str)

broken_str2 = 'broken += dep.get_file() + ":" + str(err) + "\n"\n'
fixed_str2 = 'broken += dep.get_file() + ":" + str(err) + "\\n"\n'
content = content.replace(broken_str2, fixed_str2)

with open('stages/manager/StageManager.gd', 'w', encoding='utf-8') as f:
    f.write(content)

print("StageManager syntax error fixed for real!")
