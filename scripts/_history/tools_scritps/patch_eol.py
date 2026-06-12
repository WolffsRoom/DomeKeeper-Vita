import re

with open('stages/manager/StageManager.gd', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the broken string literal with actual \\n instead of a newline
broken_str = 'var detailed = "ERROR: " + str(err) + "\n"'
fixed_str = 'var detailed = "ERROR: " + str(err) + "\\n"\n'

content = content.replace(broken_str, fixed_str)
content = content.replace('detailed += dep.get_file() + ":" + str(de) + "\n"', 'detailed += dep.get_file() + ":" + str(de) + "\\n"\n')

with open('stages/manager/StageManager.gd', 'w', encoding='utf-8') as f:
    f.write(content)

print("StageManager syntax error fixed!")
