import re

with open('systems/style/Style.gd', 'r', encoding='utf-8') as f:
    content = f.read()

new_ui_block = '''			elif node is PanelContainer or node is Panel or node is BaseButton or node is Separator or node is Range or node is HSeparator or node is VSeparator or node is OptionButton or node is Popup:
				var original = Color("544E68")
				var target = mapColor(original)
				var tint = Color(target.r / original.r, target.g / original.g, target.b / original.b, 1.0)
				node.self_modulate = tint
				node.add_to_group("styled")'''

content = re.sub(r'\t\t\telif node is PanelContainer.*?node\.material = spriteShader', new_ui_block, content, flags=re.DOTALL)

with open('systems/style/Style.gd', 'w', encoding='utf-8') as f:
    f.write(content)

print("Style.gd UI elements modified to use self_modulate tinting instead of shaders!")
