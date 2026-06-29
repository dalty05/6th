import os

root = r"c:/project/6th/backend"

null_files = []
for dirpath, _, filenames in os.walk(root):
    for fn in filenames:
        if not fn.endswith('.py'):
            continue
        p = os.path.join(dirpath, fn)
        try:
            b = open(p, 'rb').read()
        except Exception:
            continue
        c = b.count(b'\x00')
        if c:
            null_files.append((p, c, len(b)))

print(f"null_files={len(null_files)}")
for p, c, n in sorted(null_files, key=lambda x: x[0]):
    print(p, 'nulls', c, 'bytes', n)

