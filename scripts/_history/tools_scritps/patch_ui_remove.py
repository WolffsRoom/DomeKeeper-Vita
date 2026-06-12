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
			elif node is ColorRect:'''

# Replace the block that adds shaders to PanelContainer, Panel, BaseButton, etc.
content = re.sub(r'\t\t\telif node is TextureRect:.*?(?=\t\t\telif node is ColorRect:)', control_block, content, flags=re.DOTALL)


with open('systems/style/Style.gd', 'w', encoding='utf-8') as f:
    f.write(content)

print("Style.gd UI elements removed again!")
