# -*- coding: utf-8 -*-
"""
scan_stex_format.py
Varre os .stex de um projeto e reporta o formato WebP de cada um:
  A = WEBP seguido direto de RIFF  -> CORRETO (PC e fork Vita)
  B = WEBP + u32(tamanho) + RIFF   -> QUEBRADO (gera 'Error unpacking WEBP image')
Uso: python scan_stex_format.py [caminho_da_pasta_.import]
Para CONSERTAR a variante B, use stex/revert_all_stex.py.
"""
import os, struct, sys

IMPORT_DIR = sys.argv[1] if len(sys.argv) > 1 else \
    r'C:\Users\wolff\Documents\SDKVita\Dome Keeper.v5.0.4\GOGVersion\VitaBuild\.import'

RIFF = struct.unpack('<I', b'RIFF')[0]
A = B = other = nonwebp = 0
bad = []
for fn in os.listdir(IMPORT_DIR):
    if not fn.endswith('.stex'):
        continue
    with open(os.path.join(IMPORT_DIR, fn), 'rb') as f:
        d = f.read(44)
    if len(d) < 40 or d[:4] != b'GDST' or d[28:32] != b'WEBP':
        nonwebp += 1
        continue
    if d[32:36] == b'RIFF':
        A += 1
    elif struct.unpack_from('<I', d, 32)[0] != RIFF and d[36:40] == b'RIFF':
        B += 1
        bad.append(fn)
    else:
        other += 1

print('Pasta:', IMPORT_DIR)
print('Variante A (WEBP+RIFF, correto)      :', A)
print('Variante B (WEBP+size+RIFF, QUEBRADO):', B)
print('Nao-webp (PNG/outros)                :', nonwebp)
print('Outros/desconhecido                  :', other)
for b in bad:
    print('  QUEBRADO:', b)
