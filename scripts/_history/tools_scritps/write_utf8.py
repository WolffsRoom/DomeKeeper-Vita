content = """[gd_resource type="ShaderMaterial" load_steps=2 format=2]

[ext_resource path="res://content/shared/highlight.shader" type="Shader" id=1]

[resource]
resource_local_to_scene = true
shader = ExtResource( 1 )
"""
with open("content/shared/HighlightShader.material", "wb") as f:
    f.write(content.encode("utf-8"))
print("Wrote HighlightShader.material as pure UTF-8 without BOM.")
