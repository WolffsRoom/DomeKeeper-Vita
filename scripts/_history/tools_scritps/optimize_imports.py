import os

def optimize_imports():
    root_dir = '.'
    count = 0
    
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for file in filenames:
            if file.endswith('.import') and (file.endswith('.png.import') or file.endswith('.jpg.import') or file.endswith('.svg.import') or file.endswith('.webp.import')):
                filepath = os.path.join(dirpath, file)
                
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                new_content = content
                
                # Replace size_limit=0 with size_limit=1024
                if 'size_limit=0' in new_content:
                    new_content = new_content.replace('size_limit=0', 'size_limit=1024')
                
                # For SVGs, scale down
                if file.endswith('.svg.import'):
                    if 'svg/scale=1.0' in new_content:
                        new_content = new_content.replace('svg/scale=1.0', 'svg/scale=0.5')
                    elif 'svg/scale=2.0' in new_content:
                        new_content = new_content.replace('svg/scale=2.0', 'svg/scale=0.5')
                
                if new_content != content:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    count += 1
                    
    print(f"Modificados {count} arquivos de importacao de texturas.")

if __name__ == '__main__':
    optimize_imports()
