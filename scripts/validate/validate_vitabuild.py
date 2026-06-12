# -*- coding: utf-8 -*-
# Extraido e limpo do blob original (fix_stex_pc.py) durante a organizacao do projeto.
# Caminhos absolutos para GOGVersion/VitaBuild estao embutidos no script.

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
