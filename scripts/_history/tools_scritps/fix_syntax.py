with open("content/map/Map.gd", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("as PackedScene.instance()", ".instance()")

with open("content/map/Map.gd", "w", encoding="utf-8") as f:
    f.write(content)
print("Fixed syntax error in Map.gd")
