import re
from pathlib import Path

root = Path(r'F:\Paradox Interactive\Europa Universalis V\mod\Touhou Universalis II')
LANGS = ['english', 'simp_chinese', 'japanese', 'korean', 'russian']
SUFFIX = {'english': '_l_english.yml', 'simp_chinese': '_l_simp_chinese.yml',
          'japanese': '_l_japanese.yml', 'korean': '_l_korean.yml', 'russian': '_l_russian.yml'}
HEADER = {'l_english', 'l_simp_chinese', 'l_japanese', 'l_korean', 'l_russian'}
KEY_RE = re.compile(r'^\s*([A-Za-z0-9_]+)\s*:')

def keys_of(path):
    out = set()
    try:
        lines = path.read_text(encoding='utf-8-sig').splitlines()
    except Exception:
        return out
    for line in lines:
        m = KEY_RE.match(line)
        if m and m.group(1) not in HEADER:
            out.add(m.group(1))
    return out

for base_dir in [root / 'main_menu' / 'localization', root / 'in_game' / 'localization']:
    stems = set()
    per_lang = {l: {} for l in LANGS}
    for p in base_dir.rglob('*_l_*.yml'):
        for l, suf in SUFFIX.items():
            if p.name.endswith(suf):
                stem = p.name[: -len(suf)]
                per_lang[l][stem] = keys_of(p)
                stems.add(stem)
    print(f'=== {base_dir.name} ===')
    for stem in sorted(stems):
        union = set()
        for l in LANGS:
            if stem in per_lang[l]:
                union |= per_lang[l][stem]
        row = []
        for l in LANGS:
            ks = per_lang[l].get(stem)
            if ks is None:
                row.append(f'{l}=MISSING-FILE')
            else:
                miss = len(union - ks)
                extra = len(ks - union)
                row.append(f'{l}:{len(ks)}-{miss}+{extra}')
        print(f'  {stem}: ' + ' '.join(row))
