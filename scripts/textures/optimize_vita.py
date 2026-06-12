# -*- coding: utf-8 -*-
# Extraido e limpo do blob original (fix_stex_pc.py) durante a organizacao do projeto.
# Caminhos absolutos para GOGVersion/VitaBuild estao embutidos no script.

"""
optimize_vita.py
1. Remove a pasta test/ do VitaBuild
2. Redimensiona texturas de tela cheia para 960x544 (resolucao do Vita)
3. Redimensiona texturas acima de 4096px (limite do hardware)
NAO mexe em spritesheets/AtlasTextures
"""

import os, glob, shutil
from PIL import Image

vitabuild = r'C:\Users\wolff\Documents\SDKVita\Dome Keeper.v5.0.4\GOGVersion\VitaBuild'

# -------------------------
# PASSO 1 — Remove pasta test/
# -------------------------
test_folder = os.path.join(vitabuild, 'test')
if os.path.exists(test_folder):
    shutil.rmtree(test_folder)
    print(f'[REMOVIDO] pasta test/')
else:
    print(f'[JA REMOVIDO] pasta test/ nao existe')

# Remove .import e .stex relacionados a test/
import_folder = os.path.join(vitabuild, '.import')
removed_stex = 0
for imp in glob.glob(os.path.join(vitabuild, '**', '*.import'), recursive=True):
    with open(imp, 'r', errors='ignore') as f:
        content = f.read()
    if 'test/' in content or 'test\\' in content.replace('/', '\\'):
        # Remove o .stex referenciado
        for line in content.splitlines():
            if line.startswith('path='):
                stex_rel = line.split('"')[1].replace('res://', '').replace('/', os.sep)
                stex_path = os.path.join(vitabuild, stex_rel)
                if os.path.exists(stex_path):
                    os.remove(stex_path)
                    removed_stex += 1
        os.remove(imp)

print(f'[REMOVIDO] {removed_stex} .stex de test/')

# -------------------------
# PASSO 2 — Texturas de tela cheia → 960x544
# -------------------------
VITA_W, VITA_H = 960, 544
HARD_LIMIT = 4096

# Texturas que sao tela cheia (redimensiona para 960x544 mantendo aspecto)
fullscreen_keywords = [
    'titlescreen', 'splash', 'splash_screen', 'load.png',
    'freeze-overlay', 'mist.png', 'darkness.png',
    'mushroomcavecolor', 'decoration_plants', 'cavecolors',
]

# Texturas que sao spritesheets (NAO redimensionar — quebraria atlas)
# Identificamos pelo nome ou por serem muito largas e baixas
def is_spritesheet(path, w, h):
    name = os.path.basename(path).lower()
    if 'sheet' in name:
        return True
    # Muito larga e baixa = provavelmente spritesheet
    if w > h * 3:
        return True
    return False

resized = 0
skipped_sheet = 0
skipped_ok = 0

extensions = ['*.png', '*.jpg', '*.jpeg']
for ext in extensions:
    for path in glob.glob(os.path.join(vitabuild, '**', ext), recursive=True):
        # Ignora pasta .import
        if '.import' in path:
            continue
        # Ignora pasta test (ja removida)
        if os.sep + 'test' + os.sep in path:
            continue

        try:
            with Image.open(path) as img:
                w, h = img.size
                mode = img.mode

            # Ja dentro dos limites
            if w <= VITA_W and h <= VITA_H:
                skipped_ok += 1
                continue

            # Spritesheet — nao mexer
            if is_spritesheet(path, w, h):
                skipped_sheet += 1
                continue

            # Acima do limite absoluto do hardware (4096px)
            if w > HARD_LIMIT or h > HARD_LIMIT:
                # Redimensiona para caber em 4096 mantendo aspecto
                ratio = min(HARD_LIMIT / w, HARD_LIMIT / h)
                new_w = int(w * ratio)
                new_h = int(h * ratio)
                reason = 'HARD_LIMIT'
            else:
                # Tela cheia — redimensiona para 960x544 mantendo aspecto
                name_lower = os.path.basename(path).lower()
                is_fullscreen = any(k in name_lower for k in fullscreen_keywords)
                if not is_fullscreen and (w >= 960 or h >= 544):
                    # Redimensiona mantendo aspecto dentro de 960x544
                    ratio = min(VITA_W / w, VITA_H / h)
                    new_w = int(w * ratio)
                    new_h = int(h * ratio)
                    reason = 'VITA_RES'
                else:
                    skipped_ok += 1
                    continue

            # Redimensiona e salva
            with Image.open(path) as img:
                img_resized = img.resize((new_w, new_h), Image.LANCZOS)
                img_resized.save(path, optimize=True)

            rel = os.path.relpath(path, vitabuild)
            print(f'[RESIZE {reason}] {w}x{h} -> {new_w}x{new_h}  |  {rel}')
            resized += 1

        except Exception as e:
            print(f'[ERRO] {path}: {e}')

print()
print(f'Redimensionadas : {resized}')
print(f'Spritesheets ignoradas : {skipped_sheet}')
print(f'Ja ok           : {skipped_ok}')
print()
