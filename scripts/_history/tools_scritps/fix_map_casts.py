with open("content/map/Map.gd", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace('load("res://content/map/chamber/gadget/GadgetChamber.tscn")', 'load("res://content/map/chamber/gadget/GadgetChamber.tscn") as PackedScene')
content = content.replace('load("res://content/map/chamber/relic/RelicChamber.tscn")', 'load("res://content/map/chamber/relic/RelicChamber.tscn") as PackedScene')
content = content.replace('load("res://content/map/chamber/nest/NestCave.tscn")', 'load("res://content/map/chamber/nest/NestCave.tscn") as PackedScene')
content = content.replace('load("res://content/map/chamber/relicswitch/RelicSwitchChamber.tscn")', 'load("res://content/map/chamber/relicswitch/RelicSwitchChamber.tscn") as PackedScene')

with open("content/map/Map.gd", "w", encoding="utf-8") as f:
    f.write(content)

print("Fixed load() casts to PackedScene in Map.gd")
