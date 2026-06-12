with open("content/map/Map.gd", "r", encoding="utf-8") as f:
    content = f.read()

# Detect line ending style
lf_only = "\r\n" not in content
le = "\n" if lf_only else "\r\n"

# Fix 1: BORDER_TILE_OFFSETS2 multi-line with unindented continuations
old = ("const BORDER_TILE_OFFSETS2 = [Vector2(0, 0), Vector2(1, 0), Vector2(0, 1), Vector2(1, 1), " + le +
       "Vector2( - 1, 0), Vector2( - 1, 1), Vector2(0, - 1), Vector2(1, - 1), " + le +
       "Vector2(2, 0), Vector2(2, 1), Vector2(0, 2), Vector2(1, 2)" + le +
       "]")
new = ("const BORDER_TILE_OFFSETS2 = [Vector2(0, 0), Vector2(1, 0), Vector2(0, 1), Vector2(1, 1)," + le +
       "\tVector2(-1, 0), Vector2(-1, 1), Vector2(0, -1), Vector2(1, -1)," + le +
       "\tVector2(2, 0), Vector2(2, 1), Vector2(0, 2), Vector2(1, 2)" + le +
       "]")
content = content.replace(old, new)

# Fix 2: NEIGHBOR_TILE_OFFSETS2 multi-line with unindented continuations
old2 = ("const NEIGHBOR_TILE_OFFSETS2 = [Vector2(1, 0), Vector2( - 1, 0), Vector2(0, 1), Vector2(0, - 1), " + le +
        "Vector2(2, 0), Vector2( - 2, 0), Vector2(0, 2), Vector2(0, - 2), " + le +
        "Vector2(1, 1), Vector2( - 1, 1), Vector2(1, - 1), Vector2( - 1, - 1)]")
new2 = ("const NEIGHBOR_TILE_OFFSETS2 = [Vector2(1, 0), Vector2(-1, 0), Vector2(0, 1), Vector2(0, -1)," + le +
        "\tVector2(2, 0), Vector2(-2, 0), Vector2(0, 2), Vector2(0, -2)," + le +
        "\tVector2(1, 1), Vector2(-1, 1), Vector2(1, -1), Vector2(-1, -1)]")
content = content.replace(old2, new2)

# Fix 3: negative dict key with space: "\t- 1: " -> "\t-1: "
content = content.replace("\t- 1: " + '"' + '",', "\t-1: " + '"' + '",')

# Fix 4: tileData() - invalid function call
content = content.replace("\ttileData().position = - mapToWorldOffset", "\ttileData.position = -mapToWorldOffset")

with open("content/map/Map.gd", "w", encoding="utf-8") as f:
    f.write(content)

with open("content/map/Map.gd", "r", encoding="utf-8") as f:
    lines = f.readlines()
for i in [3, 4, 5, 6, 7, 8, 9, 10, 16, 17, 127]:
    print(f"Line {i+1}: {lines[i].rstrip()}")
print("Done!")
