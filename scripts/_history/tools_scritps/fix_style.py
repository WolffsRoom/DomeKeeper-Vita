import re

with open('systems/style/Style.gd', 'r', encoding='utf-8') as f:
    content = f.read()

new_init = '''func init(start_node):
	var stack = [start_node]
	while stack.size() > 0:
		var node = stack.pop_back()
		if not is_instance_valid(node):
			continue
		if node.is_in_group("styled") or node.is_in_group("unstyled"):
			pass
		else:
			if (node is Sprite or node is AnimatedSprite or node is TileMap):
				if node.material:
					if node.material is ShaderMaterial and node.material.get_shader_param("palette") != null:
						node.material.set_shader_param("palette", palette)
						node.add_to_group("styleShaderCallback")
						node.add_to_group("styled")
				else:
					node.material = spriteShader
				if node.get("modulate") and node.modulate != Color.white:
					node.modulate = mapColor(node.modulate)
					node.add_to_group("styleModulateCallback")
					node.add_to_group("styled")
			elif node is CPUParticles2D:
				if node.color_ramp:
					if not styledGradients.has(node.color_ramp):
						updateGradient(node.color_ramp)
						styledGradients.append(node.color_ramp)
					node.add_to_group("styleCpuGradientCallback")
					node.add_to_group("styled")
				elif node.color:
					node.color = mapColor(node.color)
			elif node is Particles2D and node.process_material:
				if node.process_material.get("color_ramp"):
					if not styledGradients.has(node.process_material.color_ramp):
						var gradient = node.process_material.color_ramp.get_gradient()
						updateGradient(gradient)
						styledGradients.append(node.process_material.color_ramp)
					node.add_to_group("styleGradientCallback")
					node.add_to_group("styled")
				elif node.process_material.get("color"):
					node.process_material.color = mapColor(node.process_material.color)
					node.add_to_group("styleParticleColorCallback")
					node.add_to_group("styled")
			elif node is TextureRect:
				if node.material:
					if node.material is ShaderMaterial and node.material.get_shader_param("palette") != null:
						node.material.set_shader_param("palette", palette)
						node.add_to_group("styleShaderCallback")
						node.add_to_group("styled")
				else:
					node.material = spriteShader
			elif node is ColorRect:
				if not node.color.is_equal_approx(OVERLAY_COLOR_IN):
					node.color = mapColor(node.color)
					node.add_to_group("colorRectCallback")
					node.add_to_group("styled")
		for i in range(node.get_child_count()):
			stack.push_back(node.get_child(i))'''

content = re.sub(r'func init\(node\):\n\treturn', new_init, content)

with open('systems/style/Style.gd', 'w', encoding='utf-8') as f:
    f.write(content)

print("Style.gd updated iteratively!")
