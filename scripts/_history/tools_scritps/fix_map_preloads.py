import re

with open('content/map/Map.gd', 'r', encoding='utf-8') as f:
    content = f.read()

# Step 1: Convert top-level const preloads to var declarations
# We'll initialize them lazily in _ready()
top_level_preloads = {}
def replace_const_preload(m):
    varname = m.group(1)
    path = m.group(2)
    top_level_preloads[varname] = path
    return 'var ' + varname + ' = null'

content = re.sub(
    r'^const (\w+) = preload\("([^"]+)"\)',
    replace_const_preload,
    content,
    flags=re.MULTILINE
)

# Step 2: Convert ALL remaining inline preload() calls to load()
# This covers preload() inside functions, loops, etc.
content = content.replace('preload(', 'load(')

# Step 3: Add initialization of the top-level vars in _ready()
# Find _ready() function and inject the loads at the start
ready_inits = ''
for varname, path in top_level_preloads.items():
    ready_inits += '\t' + varname + ' = load("' + path + '")\n'

if ready_inits:
    # Find _ready() or create it - Map.gd extends Node2D which has _ready
    # The map already uses onready vars so _ready is implied - but let's check
    if 'func _ready():' in content:
        content = content.replace('func _ready():\n', 'func _ready():\n' + ready_inits)
    elif 'func _ready() ->' in content:
        # unlikely
        pass
    else:
        # Insert a _ready() function before the first func
        first_func = content.find('\nfunc ')
        content = content[:first_func] + '\n\nfunc _ready():\n' + ready_inits + content[first_func:]

with open('content/map/Map.gd', 'w', encoding='utf-8') as f:
    f.write(content)

print('Converted preloads:')
for k, v in top_level_preloads.items():
    print(f'  {k} = load("{v}")')
print(f'Also replaced all inline preload() with load() in function bodies')
