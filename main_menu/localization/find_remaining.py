# -*- coding: utf-8 -*-
import re

src_path = "F:/Paradox Interactive/Europa Universalis V/mod/Touhou Universalis II/main_menu/localization/simp_chinese/th_map_l_simp_chinese.yml"
dst_path = "F:/Paradox Interactive/Europa Universalis V/mod/Touhou Universalis II/main_menu/localization/english/th_map_l_english.yml"
ex_path = "F:/Paradox Interactive/Europa Universalis V/mod/Touhou Universalis II/main_menu/localization/find_remaining.py"

# Read existing script
with open("F:/tmp/trans_script.py", "r", encoding="utf-8") as f:
    sc = f.read()

T = {}
for line in sc.split("\n"):
    if line.strip().startswith("a("):
        try:
            inner = line.strip()
            inner = inner[inner.index("(")+1:inner.rindex(")")]
            cn = inner[:inner.index(",")].strip().strip('"').strip("'")
            en = inner[inner.index(",")+1:].strip().strip('"').strip("'")
            T[cn] = en
        except:
            pass

print(f"Existing translations: {len(T)}")

# Read English YAML
with open(dst_path, "r", encoding="utf-8") as f:
    content = f.read()

all_cn = set()
for line in content.split("\n"):
    if ":" in line:
        parts = line.split(":", 1)
        val = parts[1].strip().strip('"').strip("'").split("##")[0].strip()
        if val and any('一' <= c <= '鿿' for c in val):
            all_cn.add(val)

print(f"Total Chinese values: {len(all_cn)}")

untranslated = sorted(all_cn - set(T.keys()))
print(f"Untranslated: {len(untranslated)}")

# Print the first 50 to verify
for v in untranslated[:50]:
    print(repr(v))
