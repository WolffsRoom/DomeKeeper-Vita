import re

with open('systems/style/Style.gd', 'r', encoding='utf-8') as f:
    content = f.read()

label_block = '''			elif node is Label or node is RichTextLabel:
				if node.has_color_override("font_color"):
					node.add_color_override("font_color", mapColor(node.get_color("font_color")))
			elif node is TextureRect:'''

content = content.replace('			elif node is TextureRect:', label_block)

with open('systems/style/Style.gd', 'w', encoding='utf-8') as f:
    f.write(content)
