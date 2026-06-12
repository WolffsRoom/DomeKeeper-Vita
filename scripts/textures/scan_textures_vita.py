# -*- coding: utf-8 -*-
# Extraido e limpo do blob original (fix_stex_pc.py) durante a organizacao do projeto.
# Caminhos absolutos para GOGVersion/VitaBuild estao embutidos no script.

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
