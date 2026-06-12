"""
analyze_spritesheets.py
Analisa os spritesheets criticos e suas referencias de AtlasTexture nos .tscn
"""
import os, glob, re
from PIL import Image

vitabuild = r'C:\Users\wolff\Documents\SDKVita\Dome Keeper.v5.0.4\GOGVersion\VitaBuild'

criticos = [
    r'content\dome\miroplayerfarb.png',
    r'content\dome\miroplayergrey.png',
    r'content\dome\playercolo.png',
    r'content\dome\cellar\relic_lock-Sheet+gif.png',
    r'content\gadgets\shield\shieldproperties1_sheet.png',
    r'content\gadgets\shield\shieldproperties2_sheet.png',
    r'content\map\chamber\relic\relic_chamber sprite sheet.png',
    r'content\monster\driller\largesheet.png',
    r'content\monster\driller\sheet.png',
    r'content\monster\worm\sheet.png',
]

# Busca todas as referencias nos .tscn e .tres
print("Carregando referencias de AtlasTexture...")
all_scene_files = []
for ext in ['*.tscn', '*.tres']:
    all_scene_files += glob.glob(os.path.join(vitabuild, '**', ext), recursive=True)

print(f"Total de cenas/recursos: {len(all_scene_files)}")
print()

for rel_path in criticos:
    full_path = os.path.join(vitabuild, rel_path)
    if not os.path.exists(full_path):
        print(f"[NAO ENCONTRADO] {rel_path}")
        continue

    with Image.open(full_path) as img:
        w, h = img.size

    # Nome do arquivo para busca
    filename = os.path.basename(rel_path)
    res_path = 'res://' + rel_path.replace('\\', '/')

    print(f"{'='*60}")
    print(f"Arquivo : {rel_path}")
    print(f"Tamanho : {w}x{h} px")

    # Busca referencia nas cenas
    refs_found = []
    atlas_rects = []

    for scene_file in all_scene_files:
        with open(scene_file, 'r', errors='ignore') as f:
            content = f.read()

        if filename not in content and res_path not in content:
            continue

        rel_scene = os.path.relpath(scene_file, vitabuild)
        refs_found.append(rel_scene)

        # Extrai AtlasTexture rects para estimar frames
        # Formato: region = Rect2( x, y, w, h )
        rects = re.findall(r'region\s*=\s*Rect2\s*\(\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)\s*\)', content)
        if rects:
            atlas_rects.extend(rects)

    if refs_found:
        print(f"Referenciado em:")
        for r in refs_found:
            print(f"  {r}")
    else:
        print(f"Nenhuma referencia encontrada em .tscn/.tres")

    if atlas_rects:
        # Frame size estimado (pega o mais comum)
        from collections import Counter
        sizes = Counter([(r[2], r[3]) for r in atlas_rects])
        most_common = sizes.most_common(3)
        print(f"Tamanhos de frame (AtlasTexture rects): {most_common}")
        print(f"Total de frames referenciados: {len(atlas_rects)}")

        # Estima numero de colunas pelo tamanho do frame mais comum
        if most_common:
            fw = float(most_common[0][0][0])
            fh = float(most_common[0][0][1])
            if fw > 0 and fh > 0:
                cols = round(w / fw)
                rows = round(h / fh)
                print(f"Grade estimada: {cols} colunas x {rows} linhas (frame {fw:.0f}x{fh:.0f})")
    print()
import os, glob, struct

vitabuild = r'C:\Users\wolff\Documents\SDKVita\Dome Keeper.v5.0.4\GOGVersion\VitaBuild'
import_folder = os.path.join(vitabuild, '.import')

# Le todos os .import para mapear png -> stex
png_to_stex = {}
for imp in glob.glob(os.path.join(vitabuild, '**', '*.import'), recursive=True):
    with open(imp, 'r', errors='ignore') as f:
        content = f.read()
    stex_path = None
    for line in content.splitlines():
        if line.startswith('path='):
            # path="res://.import/filename.stex"
            stex_rel = line.split('"')[1].replace('res://', '')
            stex_path = os.path.join(vitabuild, stex_rel.replace('/', os.sep))
    if stex_path:
        src = imp.replace(vitabuild + os.sep, '').replace('.import', '')
        png_to_stex[src] = stex_path

# Lista dos arquivos criticos (>4096px)
criticos = [
    r'content\dome\miroplayerfarb.png',
    r'content\dome\miroplayergrey.png',
    r'content\dome\playercolo.png',
    r'content\dome\cellar\relic_lock-Sheet+gif.png',
    r'content\gadgets\shield\shieldproperties1_sheet.png',
    r'content\gadgets\shield\shieldproperties2_sheet.png',
    r'content\map\chamber\relic\relic_chamber sprite sheet.png',
    r'content\monster\driller\largesheet.png',
    r'content\monster\driller\sheet.png',
    r'content\monster\worm\sheet.png',
    r'content\worlds\world2\Brandon - World 1 - Thomas Revision3.png',
]

print("=== TAMANHO DOS STEX CRITICOS ===\n")
total_stex = 0
for png in criticos:
    stex = png_to_stex.get(png)
    if stex and os.path.exists(stex):
        size = os.path.getsize(stex)
        total_stex += size
        # Le header para pegar dimensoes
        with open(stex, 'rb') as f:
            header = f.read(36)
        if len(header) >= 12:
            # GDST + version + flags + width + height
            try:
                w = struct.unpack_from('<H', header, 8)[0]
                h = struct.unpack_from('<H', header, 10)[0]
            except:
                w = h = 0
        print(f"  {size//1024:6d} KB  {png}")
    else:
        print(f"  NAO ENCONTRADO: {png}")

print(f"\nTotal stex criticos: {total_stex//1024} KB ({total_stex//1024//1024} MB)")

# Total geral de todos os stex
all_stex = glob.glob(os.path.join(import_folder, '*.stex'))
total_all = sum(os.path.getsize(f) for f in all_stex)
print(f"Total todos os stex: {total_all//1024} KB ({total_all//1024//1024} MB)")

print("\n=== TOP 20 MAIORES STEX ===\n")
sizes = [(os.path.getsize(f), f) for f in all_stex]
sizes.sort(reverse=True)
for size, path in sizes[:20]:
    print(f"  {size//1024:6d} KB  {os.path.basename(path)}")
import os, glob
folder = r'C:\Users\wolff\Documents\SDKVita\Dome Keeper.v5.0.4\GOGVersion\VitaBuild'
for ext in ['*.shader', '*.gdshader']:
    for path in glob.glob(os.path.join(folder, '**', ext), recursive=True):
        with open(path, 'r', errors='ignore') as f:
            content = f.read()
        if 'void fragment' in content and 'SCREEN_TEXTURE' in content:
            print('=== ' + os.path.relpath(path, folder) + ' ===')
            print(content[:500])
            print()
"""
cleanup_audio_and_duplicates.py
1. Remove arquivos de audio nao referenciados
2. Encontra e remove arquivos duplicados (mesmo conteudo, nomes diferentes)
"""

import os, glob, re, hashlib, shutil

vitabuild = r'C:\Users\wolff\Documents\SDKVita\Dome Keeper.v5.0.4\GOGVersion\VitaBuild'

removed_files = []
removed_size = 0

def remove_file(path, reason):
    global removed_size
    if os.path.exists(path):
        size = os.path.getsize(path)
        removed_size += size
        os.remove(path)
        rel = os.path.relpath(path, vitabuild)
        removed_files.append((size, rel, reason))
        print(f'[REMOVIDO] {size//1024:6d} KB  {rel}  ({reason})')

# -------------------------
# 1. Audio nao referenciado
# -------------------------
print("\n--- 1. Audio nao referenciado ---")

# Coleta todas as referencias
all_refs = set()
for ext in ['*.tscn', '*.tres', '*.gd', '*.import']:
    for path in glob.glob(os.path.join(vitabuild, '**', ext), recursive=True):
        try:
            with open(path, 'r', errors='ignore') as f:
                content = f.read()
            refs = re.findall(r"res://([^\"'\)]+)", content)
            for r in refs:
                r = r.strip().rstrip(']')
                all_refs.add(r.replace('/', os.sep).lower())
        except:
            pass

def is_referenced(path):
    rel = os.path.relpath(path, vitabuild).lower()
    if rel in all_refs:
        return True
    basename = os.path.basename(rel)
    for ref in all_refs:
        if ref.endswith(basename):
            return True
    return False

# Remove audio nao referenciado
for ext in ['*.ogg', '*.wav', '*.mp3']:
    for path in glob.glob(os.path.join(vitabuild, '**', ext), recursive=True):
        if not is_referenced(path):
            remove_file(path, 'audio nao referenciado')
            # Remove .import correspondente
            imp = path + '.import'
            if os.path.exists(imp):
                remove_file(imp, 'import audio nao referenciado')

# -------------------------
# 2. Arquivos duplicados
# -------------------------
print("\n--- 2. Duplicados (mesmo conteudo, nomes diferentes) ---")

# Calcula hash de todos os arquivos
file_hashes = {}
for path in glob.glob(os.path.join(vitabuild, '**', '*'), recursive=True):
    if not os.path.isfile(path):
        continue
    # Ignora .import e .stex (sao derivados)
    if path.endswith('.import') or path.endswith('.stex'):
        continue
    try:
        with open(path, 'rb') as f:
            file_hash = hashlib.md5(f.read()).hexdigest()
        if file_hash not in file_hashes:
            file_hashes[file_hash] = []
        file_hashes[file_hash].append(path)
    except:
        pass

# Encontra duplicatas
duplicates_removed = 0
for hash_val, paths in file_hashes.items():
    if len(paths) > 1:
        # Ordena por tamanho de caminho (mais curto = mais provavel ser o original)
        paths.sort(key=lambda p: (len(p), p))
        original = paths[0]
        duplicatas = paths[1:]
        
        for dup in duplicatas:
            size = os.path.getsize(dup)
            rel_dup = os.path.relpath(dup, vitabuild)
            rel_orig = os.path.relpath(original, vitabuild)
            
            # Nao remove se e .import ou .stex (ja sao derivados)
            if rel_dup.endswith(('.import', '.stex')):
                continue
            
            print(f'[DUPLICADO] {size//1024:6d} KB')
            print(f'  Original: {rel_orig}')
            print(f'  Duplicata: {rel_dup}')
            
            remove_file(dup, 'duplicado')
            duplicates_removed += 1

if duplicates_removed == 0:
    print('  Nenhum duplicado encontrado')

# -------------------------
# RESUMO
# -------------------------
print()
print('=' * 60)
print('RESUMO')
print('=' * 60)
print(f'Arquivos removidos : {len(removed_files)}')
print(f'Espaco liberado    : {removed_size//1024} KB ({removed_size//1024//1024} MB)')
print()

if removed_files:
    print('Top 10 maiores removidos:')
    removed_files.sort(reverse=True)
    for size, rel, reason in removed_files[:10]:
        print(f'  {size//1024:6d} KB  {rel}')

print()
print('Pronto! Reimporte no Godot e gere novo PCK.')
"""
cleanup_vitabuild.py
Remove arquivos nao usados do VitaBuild:
1. .stex orfaos (sem .import correspondente)
2. Arquivos de referencia/concept art nao referenciados em cenas
3. Addons de desenvolvimento
4. Arquivos de audio nao referenciados
"""

import os, glob, re, shutil

vitabuild = r'C:\Users\wolff\Documents\SDKVita\Dome Keeper.v5.0.4\GOGVersion\VitaBuild'
import_folder = os.path.join(vitabuild, '.import')

removed_files = []
removed_size = 0

def remove_file(path, reason):
    global removed_size
    if os.path.exists(path):
        size = os.path.getsize(path)
        removed_size += size
        os.remove(path)
        rel = os.path.relpath(path, vitabuild)
        removed_files.append((size, rel, reason))
        print(f'[REMOVIDO] {size//1024:6d} KB  {rel}  ({reason})')

def remove_folder(path, reason):
    if os.path.exists(path):
        size = sum(os.path.getsize(f) for f in glob.glob(os.path.join(path, '**', '*'), recursive=True) if os.path.isfile(f))
        shutil.rmtree(path)
        rel = os.path.relpath(path, vitabuild)
        removed_files.append((size, rel, reason))
        print(f'[REMOVIDO] {size//1024:6d} KB  {rel}/  ({reason})')

# -------------------------
# 1. .stex orfaos (sem .import)
# -------------------------
print("\n--- 1. .stex orfaos ---")
# Coleta todos os .stex referenciados por .import
referenced_stex = set()
for imp in glob.glob(os.path.join(vitabuild, '**', '*.import'), recursive=True):
    with open(imp, 'r', errors='ignore') as f:
        content = f.read()
    for line in content.splitlines():
        if line.startswith('path='):
            stex_rel = line.split('"')[1].replace('res://', '').replace('/', os.sep)
            stex_path = os.path.join(vitabuild, stex_rel)
            referenced_stex.add(os.path.normpath(stex_path))

# Remove .stex sem .import
for stex in glob.glob(os.path.join(import_folder, '*.stex')):
    if os.path.normpath(stex) not in referenced_stex:
        remove_file(stex, 'stex orfao')

# -------------------------
# 2. Addon de desenvolvimento
# -------------------------
print("\n--- 2. Addons de desenvolvimento ---")
addons_to_remove = [
    os.path.join(vitabuild, 'addons', 'ridiculous_coding'),
]
for addon in addons_to_remove:
    if os.path.exists(addon):
        remove_folder(addon, 'addon de dev')

# -------------------------
# 3. Arquivos nao referenciados
# -------------------------
print("\n--- 3. Arquivos nao referenciados ---")

# Coleta todos os caminhos referenciados em .tscn, .tres, .gd, .import
print("  Carregando referencias...")
all_refs = set()
for ext in ['*.tscn', '*.tres', '*.gd', '*.import']:
    for path in glob.glob(os.path.join(vitabuild, '**', ext), recursive=True):
        try:
            with open(path, 'r', errors='ignore') as f:
                content = f.read()
            refs = re.findall(r"res://([^\"'\)]+)", content)
            for r in refs:
                r = r.strip().rstrip(']')
                all_refs.add(r.replace('/', os.sep).lower())
            # Tambem extrai paths simples em .import
            refs2 = re.findall(r'"([^"]+\.(png|jpg|jpeg|ogg|wav|mp3|svg))"', content, re.IGNORECASE)
            for r, _ in refs2:
                all_refs.add(r.replace('/', os.sep).lower().replace('res:\\\\', '').replace('res://', ''))
        except:
            pass

def is_referenced(path):
    rel = os.path.relpath(path, vitabuild).lower()
    # Verifica se o arquivo ou qualquer variacao do caminho esta referenciado
    if rel in all_refs:
        return True
    basename = os.path.basename(rel)
    # Busca por nome de arquivo nas refs
    for ref in all_refs:
        if ref.endswith(basename):
            return True
    return False

# Palavras-chave que indicam arquivo de referencia/concept art
reference_keywords = [
    'reference', 'reference_', '_reference', '_ref', 'ref_',
    'concept', 'draft', 'wip', 'old', '_old', 'old_',
    'screenshot', 'size diff', 'positions',
    'brandon -', 'thomas revision',
]

# Pastas que sao claramente de trabalho
work_folders = [
    os.path.join(vitabuild, 'content', 'map', 'decorations', 'fuzzy'),
    os.path.join(vitabuild, 'content', 'map', 'decorations', 'mushroom'),
    os.path.join(vitabuild, 'content', 'map', 'decorations', 'pointy plant'),
    os.path.join(vitabuild, 'content', 'map', 'decorations', 'seaweed'),
    os.path.join(vitabuild, 'content', 'map', 'decorations', 'web'),
    os.path.join(vitabuild, 'content', 'map', 'tile', 'new_rocks'),
    os.path.join(vitabuild, 'content', 'worlds', 'world2', 'newversion+palette'),
    os.path.join(vitabuild, 'content', 'worlds', 'world3', 'new version'),
]

# Remove pastas de trabalho inteiras se nenhum arquivo for referenciado
for folder in work_folders:
    if not os.path.exists(folder):
        continue
    files_in_folder = glob.glob(os.path.join(folder, '**', '*'), recursive=True)
    files_in_folder = [f for f in files_in_folder if os.path.isfile(f)]
    any_referenced = any(is_referenced(f) for f in files_in_folder)
    if not any_referenced:
        remove_folder(folder, 'pasta de trabalho nao referenciada')
    else:
        print(f'  [MANTIDO] {os.path.relpath(folder, vitabuild)} (tem arquivos referenciados)')

# Remove arquivos individuais de referencia nao referenciados
for ext in ['*.png', '*.jpg', '*.jpeg']:
    for path in glob.glob(os.path.join(vitabuild, '**', ext), recursive=True):
        if '.import' in path:
            continue
        name_lower = os.path.basename(path).lower()
        # Verifica se tem keyword de referencia no nome
        has_keyword = any(k in name_lower for k in reference_keywords)
        if has_keyword and not is_referenced(path):
            # Remove o arquivo, seu .import e seu .stex
            remove_file(path, 'arquivo de referencia nao usado')
            imp = path + '.import'
            if os.path.exists(imp):
                # Pega o stex antes de remover o import
                with open(imp, 'r', errors='ignore') as f:
                    imp_content = f.read()
                for line in imp_content.splitlines():
                    if line.startswith('path='):
                        stex_rel = line.split('"')[1].replace('res://', '').replace('/', os.sep)
                        stex_path = os.path.join(vitabuild, stex_rel)
                        remove_file(stex_path, 'stex de referencia nao usado')
                remove_file(imp, 'import de referencia nao usado')

# -------------------------
# 4. Audio nao referenciado
# -------------------------
print("\n--- 4. Audio nao referenciado ---")
audio_removed = 0
for ext in ['*.ogg', '*.wav', '*.mp3']:
    for path in glob.glob(os.path.join(vitabuild, '**', ext), recursive=True):
        if not is_referenced(path):
            remove_file(path, 'audio nao referenciado')
            audio_removed += 1
            imp = path + '.import'
            if os.path.exists(imp):
                remove_file(imp, 'import audio nao referenciado')

if audio_removed == 0:
    print('  Nenhum audio nao referenciado encontrado')

# -------------------------
# RESUMO
# -------------------------
print()
print('=' * 60)
print('RESUMO')
print('=' * 60)
print(f'Arquivos removidos : {len(removed_files)}')
print(f'Espaco liberado    : {removed_size//1024} KB ({removed_size//1024//1024} MB)')
print()
print('Top 10 maiores removidos:')
removed_files.sort(reverse=True)
for size, rel, reason in removed_files[:10]:
    print(f'  {size//1024:6d} KB  {rel}')
"""
Fix all GDST/StreamTexture .stex files where the WebP blob has a double-prefix bug.

The Godot 3 StreamTexture format stores WebP images as:
  [28:32] = b'WEBP'  (4-byte magic)
  [32:36] = uint32   (size of the RIFF WebP payload that follows)
  [36:]   = RIFF WebP bytes (starting with b'RIFF')

The corrupted files have the WebP prefixed with an extra 'WEBP' at position 28, 
so the layout is:
  [28:32] = b'WEBP'  (ok)
  [32:36] = b'RIFF'  (WRONG - this is read as a 1.3 GB size -> crash on Vita)
  [36:]   = rest of RIFF WebP

Fix: strip the extra 'WEBP' prefix and rebuild the size field correctly.
"""

import struct, os, sys

import_dir = r'C:\Users\wolff\Documents\SDKVita\Dome Keeper.v5.0.4\GOGVersion\VitaBuild\.import'

RIFF_AS_INT = struct.unpack('<I', b'RIFF')[0]  # 0x46464952 = 1179011410

fixed = 0
skipped = 0
errors = 0

stex_files = [f for f in os.listdir(import_dir) if f.endswith('.stex')]
print(f"Scanning {len(stex_files)} .stex files...")

for fn in stex_files:
    fp = os.path.join(import_dir, fn)
    try:
        with open(fp, 'rb') as f:
            data = f.read()
    except Exception as e:
        print(f"  READ ERROR {fn}: {e}")
        errors += 1
        continue

    # Must be a valid GDST with at least 36 bytes and WebP at offset 28
    if len(data) < 36:
        skipped += 1
        continue
    if data[:4] != b'GDST':
        skipped += 1
        continue
    if data[28:32] != b'WEBP':
        skipped += 1
        continue

    # Check if size field [32:36] is 'RIFF' (the bug)
    size_field = struct.unpack_from('<I', data, 32)[0]
    if size_field != RIFF_AS_INT:
        # Already correct or different issue
        skipped += 1
        continue

    # The real RIFF WebP data starts at offset 32 (right after the WEBP magic)
    real_riff_webp = data[32:]
    if real_riff_webp[:4] != b'RIFF':
        print(f"  SKIP {fn}: expected RIFF at offset 32, got {real_riff_webp[:4]}")
        skipped += 1
        continue

    # Rebuild: keep 28-byte GDST header, then WEBP + correct size + RIFF payload
    new_payload_size = len(real_riff_webp)
    new_data_size = 4 + 4 + new_payload_size  # 'WEBP' + size_field + payload

    new_stex = bytearray(data[:28])
    struct.pack_into('<I', new_stex, 24, new_data_size)  # update data_size in header
    new_stex += b'WEBP'
    new_stex += struct.pack('<I', new_payload_size)
    new_stex += real_riff_webp

    try:
        with open(fp, 'wb') as f:
            f.write(bytes(new_stex))
        fixed += 1
    except Exception as e:
        print(f"  WRITE ERROR {fn}: {e}")
        errors += 1

print(f"\nDone! Fixed: {fixed}, Skipped (already ok): {skipped}, Errors: {errors}")
# Hardcoded patch for de_DE.png removed as it is no longer needed and causes corruption.
print("Skipped hardcoded de_DE.png patch.")
import os, glob, re, shutil

# Pasta do VitaBuild (onde aplicamos o fix para o Vita)
folder = r'C:\Users\wolff\Documents\SDKVita\Dome Keeper.v5.0.4\GOGVersion\VitaBuild'

# Extensoes de shader
extensions = ['*.shader', '*.gdshader', '*.tres']

fixed = 0
skipped = 0

for ext in extensions:
    for path in glob.glob(os.path.join(folder, '**', ext), recursive=True):
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            original = f.read()

        # Apenas arquivos que usam SCREEN_TEXTURE e SCREEN_UV juntos
        if 'SCREEN_TEXTURE' not in original or 'SCREEN_UV' not in original:
            skipped += 1
            continue

        content = original

        # Estrategia: substituir SCREEN_UV por _suv (variavel local)
        # e injetar "vec2 _suv = SCREEN_UV;" no inicio do fragment()
        # Isso evita que o engine detecte SCREEN_UV como built-in duas vezes

        # Verifica se ja foi corrigido
        if '_suv = SCREEN_UV' in content:
            print(f'[JA CORRIGIDO] {path}')
            skipped += 1
            continue

        # Para arquivos .tres, o shader esta dentro de code = "..."
        # Precisamos encontrar o bloco de codigo corretamente
        def fix_shader_code(code):
            # Injeta vec2 _suv = SCREEN_UV; no inicio de cada fragment()
            # e substitui usos de SCREEN_UV (que nao sejam a propria declaracao)
            
            # Primeiro: injeta a variavel local no inicio do fragment()
            # Encontra o primeiro { apos void fragment()
            pattern = r'(void\s+fragment\s*\(\s*\)\s*\{)'
            replacement = r'\1\n\tvec2 _suv = SCREEN_UV;'
            code = re.sub(pattern, replacement, code)
            
            # Segundo: substitui todos os SCREEN_UV restantes por _suv
            # Mas NAO substitui dentro da linha que acabamos de injetar
            lines = code.splitlines()
            new_lines = []
            for line in lines:
                if '_suv = SCREEN_UV' in line:
                    # Linha de declaracao, nao mexer
                    new_lines.append(line)
                else:
                    # Substitui SCREEN_UV por _suv
                    new_lines.append(line.replace('SCREEN_UV', '_suv'))
            return '\n'.join(new_lines)

        if path.endswith('.tres'):
            # Extrai e corrige o code = "..." dentro do .tres
            def fix_tres_code(m):
                inner = m.group(1)
                fixed_inner = fix_shader_code(inner)
                return 'code = "' + fixed_inner + '"'
            content = re.sub(r'code\s*=\s*"(.*?)"', fix_tres_code, content, flags=re.DOTALL)
        else:
            content = fix_shader_code(content)

        if content != original:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f'[CORRIGIDO] {path}')
            fixed += 1
        else:
            print(f'[SEM MUDANCA] {path}')
            skipped += 1

print()
print(f'Corrigidos: {fixed}')
print(f'Ignorados:  {skipped}')
import os, glob

folder = r'C:\Users\wolff\Documents\SDKVita\Dome Keeper.v5.0.4\GOGVersion\VitaBuild\.import'
files = glob.glob(os.path.join(folder, '*.stex'))

fixed = 0
skipped = 0

for path in files:
    with open(path, 'rb') as f:
        data = f.read()
    
    # Procura pelo padrão: WEBP????RIFF onde ???? é qualquer tamanho
    # O prefixo a remover é b'WEBP' + 4 bytes de tamanho = 8 bytes
    # Aparece no offset 32
    if len(data) > 40 and data[32:36] == b'WEBP' and data[40:44] == b'RIFF':
        # Remove os 8 bytes extras (WEBP + tamanho)
        new_data = data[:32] + data[40:]
        
        # Recalcula o tamanho no offset 28 (4 bytes little-endian)
        riff_size = len(new_data) - 32
        new_data = new_data[:28] + riff_size.to_bytes(4, 'little') + new_data[32:]
        
        with open(path, 'wb') as f:
            f.write(new_data)
        fixed += 1
    else:
        skipped += 1

print(f"Corrigidos: {fixed}")
print(f"Ignorados (já ok): {skipped}")
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
print('IMPORTANTE: rode o Godot para re-importar as texturas modificadas antes de gerar o PCK.')
"""
resize_miro.py
Redimensiona os 3 arquivos sem referencia para caber no limite de 4096px do Vita.
"""
from PIL import Image
import os

vitabuild = r'C:\Users\wolff\Documents\SDKVita\Dome Keeper.v5.0.4\GOGVersion\VitaBuild'

targets = [
    r'content\dome\miroplayerfarb.png',
    r'content\dome\miroplayergrey.png',
    r'content\dome\playercolo.png',
]

HARD_LIMIT = 4096

for rel in targets:
    path = os.path.join(vitabuild, rel)
    if not os.path.exists(path):
        print(f'[NAO ENCONTRADO] {rel}')
        continue

    with Image.open(path) as img:
        w, h = img.size
        mode = img.mode

    ratio = min(HARD_LIMIT / w, HARD_LIMIT / h)
    new_w = int(w * ratio)
    new_h = int(h * ratio)

    with Image.open(path) as img:
        resized = img.resize((new_w, new_h), Image.LANCZOS)
        resized.save(path, optimize=True)

    print(f'[RESIZED] {w}x{h} -> {new_w}x{new_h} | {rel}')

print()
print('Pronto! Abra o VitaBuild no Godot para re-importar antes de gerar o PCK.')
"""
resize_remaining_spritesheets.py
Redimensiona os 9 spritesheets restantes para caber em 4096px
"""
from PIL import Image
import os

vitabuild = r'C:\Users\wolff\Documents\SDKVita\Dome Keeper.v5.0.4\GOGVersion\VitaBuild'

# Os 9 spritesheets que ainda estão acima de 4096px
targets = [
    r'content\dome\cellar\relic_lock-Sheet+gif.png',
    r'content\gadgets\shield\shieldproperties1_sheet.png',
    r'content\gadgets\shield\shieldproperties2_sheet.png',
    r'content\map\chamber\relic\relic_chamber sprite sheet.png',
    r'content\monster\driller\largesheet.png',
    r'content\monster\driller\sheet.png',
    r'content\monster\worm\sheet.png',
    # Plus 2 mais que faltaram de checagem anterior
    r'content\dome\cellar\spinning_sphere-Sheet.png',
    r'content\dome\collapse\collapse-sheet.png',
]

HARD_LIMIT = 4096

resized = 0
for rel in targets:
    path = os.path.join(vitabuild, rel)
    if not os.path.exists(path):
        print(f'[NAO ENCONTRADO] {rel}')
        continue

    with Image.open(path) as img:
        w, h = img.size

    # Se ja dentro do limite, pula
    if w <= HARD_LIMIT and h <= HARD_LIMIT:
        print(f'[OK] {w}x{h} | {rel}')
        continue

    # Redimensiona mantendo aspecto
    ratio = min(HARD_LIMIT / w, HARD_LIMIT / h)
    new_w = int(w * ratio)
    new_h = int(h * ratio)

    with Image.open(path) as img:
        resized_img = img.resize((new_w, new_h), Image.LANCZOS)
        resized_img.save(path, optimize=True)

    print(f'[RESIZED] {w}x{h} -> {new_w}x{new_h} | {rel}')
    resized += 1

print()
print(f'Total redimensionadas: {resized}')
print('Abra o VitaBuild no Godot para re-importar antes de gerar o PCK.')
"""
REVERT the broken bulk stex fix.

What fix_all_stex.py did INCORRECTLY:
  The correct Godot 3 StreamTexture WebP format is:
    [28:32] = b'WEBP'   <- Godot prefix
    [32:36] = b'RIFF'   <- start of actual RIFF WebP data   ← CORRECT, not a bug!
    [36:N]  = rest of RIFF WebP

  fix_all_stex.py saw 'RIFF' at [32:36] and inserted a size field, producing:
    [28:32] = b'WEBP'
    [32:36] = numeric_size   <- WRONG insertion
    [36:40] = b'RIFF'        <- RIFF WebP pushed +4 bytes

  This broke PC (WebPDecodeRGBA receives garbage before 'RIFF').

This script detects and removes the incorrectly inserted size field,
restoring all files to the original working format.
"""

import struct, os

import_dir = r'C:\Users\wolff\Documents\SDKVita\Dome Keeper.v5.0.4\GOGVersion\VitaBuild\.import'

RIFF_BYTES = b'RIFF'
RIFF_AS_INT = struct.unpack('<I', RIFF_BYTES)[0]  # 1179011410

reverted = 0
skipped = 0
errors = 0

stex_files = [f for f in os.listdir(import_dir) if f.endswith('.stex')]
print(f"Scanning {len(stex_files)} .stex files...")

for fn in stex_files:
    fp = os.path.join(import_dir, fn)
    try:
        with open(fp, 'rb') as f:
            data = f.read()
    except Exception as e:
        print(f"  READ ERROR {fn}: {e}")
        errors += 1
        continue

    # Need at least 40 bytes, GDST header, WEBP at 28
    if len(data) < 40 or data[:4] != b'GDST' or data[28:32] != b'WEBP':
        skipped += 1
        continue

    size_field = struct.unpack_from('<I', data, 32)[0]

    # If [32:36] is already 'RIFF' → already in original format, skip
    if size_field == RIFF_AS_INT:
        skipped += 1
        continue

    # If [32:36] is NOT 'RIFF' but [36:40] IS 'RIFF' → our broken fix was applied
    if data[36:40] != RIFF_BYTES:
        skipped += 1  # Unknown format, don't touch
        continue

    # Revert: remove the incorrectly inserted size field at [32:36]
    # Original: header(28) + 'WEBP'(4) + 'RIFF'(4) + rest
    # Fixed:   header(28) + 'WEBP'(4) + size(4)   + 'RIFF'(4) + rest
    # Revert:  remove size → header(28) + 'WEBP'(4) + 'RIFF'(4) + rest

    riff_and_rest = data[36:]          # 'RIFF' + original RIFF WebP data
    new_data_size = 4 + len(riff_and_rest)  # 'WEBP' + RIFF_data

    new_stex = bytearray(data[:28])    # Keep original 28-byte GDST header
    struct.pack_into('<I', new_stex, 24, new_data_size)  # Update data_size field
    new_stex += b'WEBP'               # Restore 'WEBP' prefix
    new_stex += riff_and_rest         # Restore original RIFF WebP (starts with 'RIFF')

    try:
        with open(fp, 'wb') as f:
            f.write(bytes(new_stex))
        reverted += 1
    except Exception as e:
        print(f"  WRITE ERROR {fn}: {e}")
        errors += 1

print(f"\nDone!  Reverted: {reverted}  |  Skipped (already OK): {skipped}  |  Errors: {errors}")
"""
scan_textures_vita.py
Varre todas as imagens do VitaBuild e reporta as que excedem os limites recomendados para o Vita.
NAO modifica nenhum arquivo — apenas analisa e gera relatorio.
"""

import os
import glob

# Tenta importar Pillow
try:
    from PIL import Image
except ImportError:
    print("Pillow nao encontrado. Instalando...")
    os.system("pip install pillow")
    from PIL import Image

# -------------------------
# CONFIGURACAO
# -------------------------
folder = r'C:\Users\wolff\Documents\SDKVita\Dome Keeper.v5.0.4\GOGVersion\VitaBuild'

# Limite absoluto do hardware Vita
HARD_LIMIT = 4096

# Limites recomendados por tipo de pasta/nome
# (palavra-chave no caminho -> (max_w, max_h))
RECOMMENDED = {
    'background'  : (1024, 512),
    'bg'          : (1024, 512),
    'vignette'    : (1024, 512),
    'ui'          : (512, 256),
    'hud'         : (512, 256),
    'tile'        : (512, 512),
    'tileset'     : (512, 512),
    'map'         : (512, 512),
    'palette'     : None,   # None = nao verificar, sao texturas de dados
    'font'        : None,
}
DEFAULT_RECOMMENDED = (512, 512)  # Para qualquer outra textura

# -------------------------
# SCAN
# -------------------------
extensions = ['*.png', '*.jpg', '*.jpeg', '*.webp', '*.bmp', '*.tga']

results_hard   = []  # Acima do limite absoluto 4096
results_over   = []  # Acima do recomendado mas abaixo de 4096
results_ok     = []  # Dentro do recomendado

total = 0
errors = 0

print(f"Varrendo: {folder}")
print("=" * 70)

for ext in extensions:
    for path in glob.glob(os.path.join(folder, '**', ext), recursive=True):
        total += 1
        try:
            with Image.open(path) as img:
                w, h = img.size

            # Determina limite recomendado baseado no caminho
            path_lower = path.lower()
            rec = DEFAULT_RECOMMENDED
            skip = False
            for keyword, limit in RECOMMENDED.items():
                if keyword in path_lower:
                    if limit is None:
                        skip = True
                    else:
                        rec = limit
                    break

            if skip:
                results_ok.append((path, w, h, None))
                continue

            rel_path = os.path.relpath(path, folder)

            if w > HARD_LIMIT or h > HARD_LIMIT:
                results_hard.append((rel_path, w, h, rec))
            elif w > rec[0] or h > rec[1]:
                results_over.append((rel_path, w, h, rec))
            else:
                results_ok.append((rel_path, w, h, rec))

        except Exception as e:
            errors += 1

# -------------------------
# RELATORIO
# -------------------------
print(f"\nTotal de imagens escaneadas : {total}")
print(f"Erros ao abrir             : {errors}")
print()

print("=" * 70)
print(f"🔴 ACIMA DO LIMITE ABSOLUTO (>{HARD_LIMIT}px): {len(results_hard)}")
print("=" * 70)
for path, w, h, rec in results_hard:
    print(f"  {w}x{h}  →  recomendado {rec[0]}x{rec[1]}  |  {path}")

print()
print("=" * 70)
print(f"🟡 ACIMA DO RECOMENDADO PARA O VITA: {len(results_over)}")
print("=" * 70)
for path, w, h, rec in results_over:
    print(f"  {w}x{h}  →  recomendado {rec[0]}x{rec[1]}  |  {path}")

print()
print("=" * 70)
print(f"✅ DENTRO DO RECOMENDADO: {len(results_ok)}")
print("=" * 70)

# Salva relatorio em arquivo
report_path = r'C:\Users\wolff\Documents\SDKVita\Dome Keeper.v5.0.4\texture_report.txt'
with open(report_path, 'w', encoding='utf-8') as f:
    f.write(f"RELATORIO DE TEXTURAS - VITA\n")
    f.write(f"Pasta: {folder}\n")
    f.write(f"Total: {total} | Erros: {errors}\n\n")

    f.write(f"=== ACIMA DO LIMITE ABSOLUTO (>{HARD_LIMIT}px): {len(results_hard)} ===\n")
    for path, w, h, rec in results_hard:
        f.write(f"  {w}x{h} -> recomendado {rec[0]}x{rec[1]} | {path}\n")

    f.write(f"\n=== ACIMA DO RECOMENDADO: {len(results_over)} ===\n")
    for path, w, h, rec in results_over:
        f.write(f"  {w}x{h} -> recomendado {rec[0]}x{rec[1]} | {path}\n")

    f.write(f"\n=== DENTRO DO RECOMENDADO: {len(results_ok)} ===\n")
    for path, w, h, rec in results_ok:
        if rec:
            f.write(f"  {w[0] if isinstance(w, tuple) else w}x{h} | {path}\n")

print(f"\nRelatorio salvo em: {report_path}")
"""
validate_vitabuild.py
Valida o VitaBuild completo antes de gerar o PCK para o Vita.
Verifica shaders, texturas, stex, arquivos faltando e potenciais problemas de RAM.
"""

import os, glob, re, struct

vitabuild = r'C:\Users\wolff\Documents\SDKVita\Dome Keeper.v5.0.4\GOGVersion\VitaBuild'

PASS = "[OK]    "
WARN = "[AVISO] "
FAIL = "[ERRO]  "

issues = []
warnings = []
passes = []

def log_pass(msg):
    passes.append(msg)
    print(f"{PASS} {msg}")

def log_warn(msg):
    warnings.append(msg)
    print(f"{WARN} {msg}")

def log_fail(msg):
    issues.append(msg)
    print(f"{FAIL} {msg}")

print("=" * 70)
print("VALIDACAO DO VITABUILD")
print(f"Pasta: {vitabuild}")
print("=" * 70)

# -------------------------
# 1. Pasta test/ removida
# -------------------------
print("\n--- 1. Pasta test/ ---")
test_folder = os.path.join(vitabuild, 'test')
if os.path.exists(test_folder):
    log_fail("Pasta test/ ainda existe — deve ser removida (consome RAM desnecessaria)")
else:
    log_pass("Pasta test/ removida")

# -------------------------
# 2. Shaders — SCREEN_UV corrigido
# -------------------------
print("\n--- 2. Shaders SCREEN_UV ---")
shader_issues = 0
shader_ok = 0
for ext in ['*.shader', '*.gdshader', '*.tres']:
    for path in glob.glob(os.path.join(vitabuild, '**', ext), recursive=True):
        with open(path, 'r', errors='ignore') as f:
            content = f.read()
        if 'SCREEN_TEXTURE' in content and 'SCREEN_UV' in content:
            if '_suv = SCREEN_UV' not in content:
                rel = os.path.relpath(path, vitabuild)
                log_fail(f"Shader nao corrigido: {rel}")
                shader_issues += 1
            else:
                shader_ok += 1

if shader_issues == 0:
    log_pass(f"Todos os {shader_ok} shaders com SCREEN_UV corrigidos")

# -------------------------
# 3. Shaders — SCREEN_UV_USED duplo nos .material
# -------------------------
print("\n--- 3. Arquivos .material ---")
mat_issues = 0
for path in glob.glob(os.path.join(vitabuild, '**', '*.material'), recursive=True):
    with open(path, 'r', errors='ignore') as f:
        content = f.read()
    if 'SCREEN_UV' in content and '_suv = SCREEN_UV' not in content:
        rel = os.path.relpath(path, vitabuild)
        log_warn(f"Material com SCREEN_UV nao verificado: {rel}")
        mat_issues += 1
if mat_issues == 0:
    log_pass("Nenhum .material problemático encontrado")

# -------------------------
# 4. Texturas acima de 4096px
# -------------------------
print("\n--- 4. Texturas acima de 4096px ---")
try:
    from PIL import Image
    hard_limit_issues = 0
    for ext in ['*.png', '*.jpg', '*.jpeg']:
        for path in glob.glob(os.path.join(vitabuild, '**', ext), recursive=True):
            if '.import' in path:
                continue
            try:
                with Image.open(path) as img:
                    w, h = img.size
                if w > 4096 or h > 4096:
                    rel = os.path.relpath(path, vitabuild)
                    log_fail(f"Textura acima de 4096px: {w}x{h} | {rel}")
                    hard_limit_issues += 1
            except:
                pass
    if hard_limit_issues == 0:
        log_pass("Nenhuma textura acima de 4096px")
except ImportError:
    log_warn("Pillow nao instalado — pulando verificacao de tamanho de texturas")

# -------------------------
# 5. .stex corrompidos (prefixo duplo para PC)
# -------------------------
print("\n--- 5. Formato dos .stex ---")
import_folder = os.path.join(vitabuild, '.import')
stex_files = glob.glob(os.path.join(import_folder, '*.stex'))
stex_corrupt_pc = 0
stex_ok = 0
stex_webp_vita = 0

for path in stex_files:
    try:
        with open(path, 'rb') as f:
            data = f.read(48)
        if len(data) < 40:
            continue
        # Verifica prefixo duplo WEBP (formato Vita)
        if data[32:36] == b'WEBP' and data[40:44] == b'RIFF':
            stex_webp_vita += 1
        elif data[32:36] == b'RIFF':
            stex_ok += 1
        elif data[32:36] == b'WEBP' and data[40:44] == b'WEBP':
            stex_corrupt_pc += 1
    except:
        pass

total_stex = len(stex_files)
if stex_corrupt_pc > 0:
    log_fail(f"{stex_corrupt_pc} .stex com prefixo duplo corrompido")
if stex_webp_vita > 0:
    log_pass(f"{stex_webp_vita}/{total_stex} .stex no formato Vita (WEBP prefix)")
if stex_ok > 0:
    log_pass(f"{stex_ok}/{total_stex} .stex no formato padrao (RIFF direto)")

# -------------------------
# 6. Estimativa de RAM das texturas
# -------------------------
print("\n--- 6. Estimativa de uso de RAM ---")
total_stex_size = sum(os.path.getsize(f) for f in stex_files if os.path.exists(f))
print(f"  Total .stex em disco: {total_stex_size // 1024} KB ({total_stex_size // 1024 // 1024} MB)")
print(f"  Total arquivos .stex: {total_stex}")

# Top 10 maiores
sizes = [(os.path.getsize(f), f) for f in stex_files if os.path.exists(f)]
sizes.sort(reverse=True)
print(f"\n  Top 10 maiores .stex:")
top_total = 0
for size, path in sizes[:10]:
    top_total += size
    print(f"    {size//1024:6d} KB  {os.path.basename(path)}")
print(f"\n  Top 10 somam: {top_total//1024} KB ({top_total//1024//1024} MB)")

if total_stex_size > 50 * 1024 * 1024:
    log_warn(f"Total de stex acima de 50MB em disco — RAM descomprimida pode ser alta")
else:
    log_pass(f"Tamanho total de stex dentro do esperado")

# -------------------------
# 7. Arquivos .import sem .stex correspondente
# -------------------------
print("\n--- 7. .import sem .stex ---")
missing_stex = 0
import_files = glob.glob(os.path.join(vitabuild, '**', '*.import'), recursive=True)
for imp in import_files:
    with open(imp, 'r', errors='ignore') as f:
        content = f.read()
    for line in content.splitlines():
        if line.startswith('path='):
            stex_rel = line.split('"')[1].replace('res://', '').replace('/', os.sep)
            stex_path = os.path.join(vitabuild, stex_rel)
            if not os.path.exists(stex_path):
                rel = os.path.relpath(imp, vitabuild)
                log_warn(f"stex faltando: {os.path.basename(stex_path)} | import: {rel}")
                missing_stex += 1
            break

if missing_stex == 0:
    log_pass(f"Todos os {len(import_files)} .import tem .stex correspondente")

# -------------------------
# 8. project.godot — configuracoes Vita
# -------------------------
print("\n--- 8. project.godot ---")
project_file = os.path.join(vitabuild, 'project.godot')
if os.path.exists(project_file):
    with open(project_file, 'r', errors='ignore') as f:
        proj = f.read()

    checks = {
        'vram_compression/import_etc=true': 'ETC1 habilitado',
        'quality/depth/hdr=false': 'HDR desabilitado',
        'vram_compression/import_s3tc=false': 'S3TC desabilitado',
    }
    for key, desc in checks.items():
        if key in proj:
            log_pass(desc)
        else:
            log_warn(f"Nao encontrado: {key} ({desc})")
else:
    log_fail("project.godot nao encontrado")

# -------------------------
# 9. Arquivos de localizacao faltando
# -------------------------
print("\n--- 9. Flags de localizacao ---")
flags_folder = os.path.join(vitabuild, 'systems', 'localization', 'flags')
if os.path.exists(flags_folder):
    flags = glob.glob(os.path.join(flags_folder, '*.png'))
    log_pass(f"{len(flags)} flags de localizacao encontradas")
    # Verifica de_DE especificamente (que estava faltando no log)
    de_de = os.path.join(flags_folder, 'de_DE.png')
    if os.path.exists(de_de):
        log_pass("de_DE.png presente")
    else:
        log_fail("de_DE.png faltando (causou erro no log do Vita)")
else:
    log_warn("Pasta de flags nao encontrada")

# -------------------------
# RESUMO FINAL
# -------------------------
print()
print("=" * 70)
print("RESUMO")
print("=" * 70)
print(f"  ERROS   : {len(issues)}")
print(f"  AVISOS  : {len(warnings)}")
print(f"  OK      : {len(passes)}")
print()

if issues:
    print("ERROS A CORRIGIR:")
    for i in issues:
        print(f"  {FAIL} {i}")
    print()

if warnings:
    print("AVISOS:")
    for w in warnings:
        print(f"  {WARN} {w}")
    print()

if not issues:
    print("VitaBuild pronto para gerar PCK!")
else:
    print("Corrija os erros antes de gerar o PCK.")
