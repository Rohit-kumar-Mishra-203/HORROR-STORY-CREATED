import os

raw_dir = 'data/raw'
files = [f for f in os.listdir(raw_dir) if f.endswith('.txt')]
print(f'Total files: {len(files)}')
print()

for filename in sorted(files):
    filepath = os.path.join(raw_dir, filename)
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    words = len(content.split())
    hindi = sum(1 for c in content if 0x0900 <= ord(c) <= 0x097F)
    total = len(content.replace(' ', '').replace('\n', ''))
    ratio = (hindi / total * 100) if total > 0 else 0

    bad = [c for c in content if not (
        0x0900 <= ord(c) <= 0x097F or
        c in ' \n\r।?!,\'-\"' or
        0x0030 <= ord(c) <= 0x0039
    )]
    unique_bad = list(set(bad))[:3]

    status = '✅' if ratio > 75 and not bad else '❌'
    print(f'{status} {filename}: {words} words, {ratio:.0f}% Hindi, bad chars: {unique_bad}')