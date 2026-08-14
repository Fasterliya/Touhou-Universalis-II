import re
from pathlib import Path

root = Path(r'F:\Paradox Interactive\Europa Universalis V\mod\Touhou Universalis II')
KEY_RE = re.compile(r'^\s+([A-Za-z0-9_]+)\s*:')

FILES = [
    root / 'main_menu' / 'localization' / 'english' / 'th_culture_l_english.yml',
    root / 'main_menu' / 'localization' / 'japanese' / 'th_culture_l_japanese.yml',
    root / 'main_menu' / 'localization' / 'russian' / 'th_culture_l_russian.yml',
    root / 'main_menu' / 'localization' / 'simp_chinese' / 'th_culture_l_simp_chinese.yml',
    root / 'in_game' / 'localization' / 'simp_chinese' / 'th_gensokyo_io_l_simp_chinese.yml',
]

for p in FILES:
    lines = p.read_text(encoding='utf-8-sig').splitlines(keepends=True)
    seen = set()
    removed = 0
    out = []
    for line in lines:
        m = KEY_RE.match(line)
        if m:
            k = m.group(1)
            if k in seen:
                removed += 1
                continue  # drop duplicate occurrence (values verified identical)
            seen.add(k)
        out.append(line)
    if removed:
        # preserve original BOM
        data = ''.join(out).encode('utf-8')
        p.write_bytes(b'\xef\xbb\xbf' + data)
        print(f'{p.relative_to(root)}: removed {removed} duplicate line(s)')
    else:
        print(f'{p.relative_to(root)}: no duplicates')
