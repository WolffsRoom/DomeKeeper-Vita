# -*- coding: utf-8 -*-
# Extraido e limpo do blob original (fix_stex_pc.py) durante a organizacao do projeto.
# Caminhos absolutos para GOGVersion/VitaBuild estao embutidos no script.

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
