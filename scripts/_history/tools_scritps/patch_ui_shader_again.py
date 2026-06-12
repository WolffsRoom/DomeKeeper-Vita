import re

with open('systems/style/Style.gd', 'r', encoding='utf-8') as f:
    content = f.read()

shader_block = '''			elif node is PanelContainer or node is Panel or node is BaseButton or node is Separator or node is Range or node is HSeparator or node is VSeparator or node is OptionButton or node is Popup:
				node.material = spriteShader
				node.add_to_group("styled")'''

content = re.sub(r'\t\t\telif node is PanelContainer.*?node\.add_to_group\("styled"\)', shader_block, content, flags=re.DOTALL)

with open('systems/style/Style.gd', 'w', encoding='utf-8') as f:
    f.write(content)

print("Style.gd UI elements restored to use spriteShader!")
