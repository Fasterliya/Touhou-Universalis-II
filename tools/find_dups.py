import re
from pathlib import Path

root = Path(r'F:\Paradox Interactive\Europa Universalis V\mod\Touhou Universalis II')
KEY_RE = re.compile(r'^\s+([A-Za-z0-9_]+)\s*:')

for base in [root / 'main_menu' / 'localization', root / 'in_game' / 'localization']:
    for p in sorted(base.rglob('*.yml')):
        seen = {}
        dups = []
        try:
            lines = p.read_text(encoding='utf-8-sig').splitlines()
        except Exception:
            continue
        for i, line in enumerate(lines, 1):
            m = KEY_RE.match(line)
            if m:
                k = m.group(1)
                if k in seen:
                    dups.append((k, seen[k], i))
                else:
                    seen[k] = i
        if dups:
            rel = str(p.relative_to(root))
            for k, a, b in dups:
                print(f'{rel}: duplicate {k} @ {a} & {b}')
