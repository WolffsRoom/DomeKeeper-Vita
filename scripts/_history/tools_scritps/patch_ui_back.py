import re

with open('systems/style/Style.gd', 'r', encoding='utf-8') as f:
    content = f.read()

control_block = '''			elif node is TextureRect:
				if node.material:
					if node.material is ShaderMaterial and node.material.get_shader_param("palette") != null:
						node.material.set_shader_param("palette", palette)
						node.add_to_group("styleShaderCallback")
						node.add_to_group("styled")
				else:
					node.material = spriteShader
			elif node is PanelContainer or node is Panel or node is BaseButton or node is Separator or node is Range or node is HSeparator or node is VSeparator or node is OptionButton or node is Popup:
				node.material = spriteShader
			elif node is ColorRect:'''

content = content.replace('''			elif node is TextureRect:
				if node.material:
					if node.material is ShaderMaterial and node.material.get_shader_param("palette") != null:
						node.material.set_shader_param("palette", palette)
						node.add_to_group("styleShaderCallback")
						node.add_to_group("styled")
				else:
					node.material = spriteShader
			elif node is ColorRect:''', control_block)

with open('systems/style/Style.gd', 'w', encoding='utf-8') as f:
    f.write(content)
