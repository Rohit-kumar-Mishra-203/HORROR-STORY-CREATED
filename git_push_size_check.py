import os
total = 0
files = []
for root, dirs, filenames in os.walk('.'):
    dirs[:] = [d for d in dirs if d not in [
        'venv', 'saved_model', 'saved_model_english',
        '.git', '__pycache__', 'logs', 'logs_english'
    ]]
    for f in filenames:
        path = os.path.join(root, f)
        size = os.path.getsize(path)
        total += size
        if size > 500000:
            files.append((size, path))

print('Files larger than 500KB:')
for size, path in sorted(files, reverse=True):
    print(f'  {size/1024/1024:.2f} MB → {path}')
print(f'\nTotal size to upload: {total/1024/1024:.2f} MB')