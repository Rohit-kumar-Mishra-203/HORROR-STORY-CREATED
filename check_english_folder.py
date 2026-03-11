import os
files = [f for f in os.listdir('data/raw_english') if f.endswith('.txt')]
print(f'Total English stories: {len(files)}')
for f in files:
    with open(f'data/raw_english/{f}', encoding='utf-8') as file:
        words = len(file.read().split())
    print(f'  {f}: {words} words')