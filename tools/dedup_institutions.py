import re

path = r'F:\Paradox Interactive\Europa Universalis V\mod\Touhou Universalis II\main_menu\setup\start\08_institutions.txt'

data = open(path, 'rb').read()
has_bom = data[:3] == b'\xef\xbb\xbf'
text = data[3:].decode('utf-8') if has_bom else data.decode('utf-8')

lines = text.splitlines(keepends=True)
# Drop whole-line blocks of the form: ^th_... = {  ...  }
# where the block body contains no institution assignment (empty th_ placeholders).
out = []
i = 0
removed = 0
while i < len(lines):
    m = re.match(r'^\s*(th_[a-z0-9_]+)\s*=\s*\{\s*\n$', lines[i])
    if m:
        j = i + 1
        depth = 1
        while j < len(lines) and depth > 0:
            open_b = lines[j].count('{')
            close_b = lines[j].count('}')
            depth += open_b - close_b
            j += 1
        body = ''.join(lines[i + 1:j - 1])
        if not body.strip():
            removed += 1
            i = j
            continue
    out.append(lines[i])
    i += 1

new_text = ''.join(out)
open(path, 'wb').write((b'\xef\xbb\xbf' if has_bom else b'') + new_text.encode('utf-8'))
print('removed empty th_ blocks:', removed)
print('lines:', len(lines), '->', len(out))
