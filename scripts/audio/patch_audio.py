import re
import os
import shutil

# Restore original Audio.gd so patches don't stack and corrupt the file
src = r'C:\Users\wolff\Documents\SDKVita\Dome Keeper.v5.0.4\GOGVersion\OriginalPCK\systems\audio\Audio.gd'
target = r'C:\Users\wolff\Documents\SDKVita\Dome Keeper.v5.0.4\GOGVersion\VitaBuild\systems\audio\Audio.gd'
if os.path.exists(src):
    shutil.copy2(src, target)

with open(target, 'r', encoding='utf-8') as f:
    content = f.read()

# Enable VITA_DISABLE_MUSIC to prevent crashes when missing music
content = re.sub(r'const VITA_DISABLE_MUSIC:\s*=\s*false', 'const VITA_DISABLE_MUSIC: = true', content)

# Replace preloads with strings for .ogg music and stingers
content = re.sub(r'preload\("res://content/music/(.*?\.ogg)"\)', r'"res://content/music/\1"', content)
content = re.sub(r'preload\("res://content/sounds/stingers/(.*?\.ogg)"\)', r'"res://content/sounds/stingers/\1"', content)

# Patch dynamic load calls
content = content.replace(
    '.stream = miningMusic[i % miningMusic.size()]',
    '.stream = load(miningMusic[i % miningMusic.size()])'
)
content = content.replace(
    '.stream = m_battle[0]',
    '.stream = load(m_battle[0])'
)

# Fix intro / ending assignments
content = content.replace(
    '.stream = get("m_intro_" + GameWorld.lastKeeperId)',
    '.stream = load(get("m_intro_" + GameWorld.lastKeeperId))'
)
content = content.replace(
    '.stream = get("m_ending_" + GameWorld.lastKeeperId)',
    '.stream = load(get("m_ending_" + GameWorld.lastKeeperId))'
)
content = content.replace(
    '.stream = get("m_game_over_" + GameWorld.lastKeeperId)',
    '.stream = load(get("m_game_over_" + GameWorld.lastKeeperId))'
)

# Fix loop assignments
content = content.replace(
    '.stream = get("m_intro_loop_" + GameWorld.lastKeeperId)',
    '.stream = load(get("m_intro_loop_" + GameWorld.lastKeeperId))'
)
content = content.replace(
    '.stream = get("m_ending_loop_" + GameWorld.lastKeeperId)',
    '.stream = load(get("m_ending_loop_" + GameWorld.lastKeeperId))'
)
content = content.replace(
    '.stream = get("m_game_over_loop_" + GameWorld.lastKeeperId)',
    '.stream = load(get("m_game_over_loop_" + GameWorld.lastKeeperId))'
)

# Fix string comparisons properly
content = content.replace(
    '$Music.stream == get("m_intro_" + GameWorld.lastKeeperId)',
    '$Music.stream and $Music.stream.resource_path == get("m_intro_" + GameWorld.lastKeeperId)'
)
content = content.replace(
    '$Music.stream == get("m_ending_" + GameWorld.lastKeeperId)',
    '$Music.stream and $Music.stream.resource_path == get("m_ending_" + GameWorld.lastKeeperId)'
)
content = content.replace(
    '$Music.stream == get("m_game_over_" + GameWorld.lastKeeperId)',
    '$Music.stream and $Music.stream.resource_path == get("m_game_over_" + GameWorld.lastKeeperId)'
)

with open(target, 'w', encoding='utf-8') as f:
    f.write(content)

print("Audio.gd patched successfully with VITA_DISABLE_MUSIC!")
