import re

# Fix export presets
with open('export_presets.cfg', 'r', encoding='utf-8') as f:
    cfg = f.read()
cfg = re.sub(r'include_filter=".*?"', 'include_filter="*.yaml, *.json, *.txt, *.csv"', cfg)
with open('export_presets.cfg', 'w', encoding='utf-8') as f:
    f.write(cfg)

# Fix Data.gd
with open('systems/data/Data.gd', 'r', encoding='utf-8') as f:
    data_gd = f.read()
    
fix = '''	var err = f.open("res://properties.yaml", File.READ)
	if err != OK:
		print("ERROR: Could not open properties.yaml")
		return'''
		
data_gd = data_gd.replace('	f.open("res://properties.yaml", File.READ)', fix)

with open('systems/data/Data.gd', 'w', encoding='utf-8') as f:
    f.write(data_gd)

print("Fixed export_presets and Data.gd infinite loop!")
