import os

def optimize_wav_imports():
    count = 0
    for root, dirs, files in os.walk('.'):
        for f in files:
            if f.endswith('.wav.import'):
                filepath = os.path.join(root, f)
                with open(filepath, 'r') as file:
                    content = file.read()
                
                new_content = content.replace('compress/mode=0', 'compress/mode=1')
                new_content = new_content.replace('force/max_rate=false', 'force/max_rate=true')
                new_content = new_content.replace('force/max_rate_hz=44100', 'force/max_rate_hz=22050')
                
                if new_content != content:
                    with open(filepath, 'w') as file:
                        file.write(new_content)
                    count += 1
    
    print(f'Optimized {count} .wav.import files.')

if __name__ == '__main__':
    optimize_wav_imports()
