#!/usr/bin/env python3
"""Final fix: remaining CN chars 阳→陽, 阵→陣, 斋→斎"""
import re

filepath = r"F:\Paradox Interactive\Europa Universalis V\mod\Touhou Universalis II\main_menu\localization\japanese\th_map_l_japanese.yml"

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

original = content

cn_to_jp = {
    '阳': '陽',
    '阵': '陣',
    '斋': '斎',
}

def process_line(line):
    if ':' not in line:
        for cn, jp in cn_to_jp.items():
            line = line.replace(cn, jp)
        return line
    colon_idx = line.index(':')
    key = line[:colon_idx]
    rest = line[colon_idx+1:]
    quote_char = None
    for q in ['"', "'"]:
        if q in rest:
            quote_char = q
            break
    if quote_char is None:
        for cn, jp in cn_to_jp.items():
            rest = rest.replace(cn, jp)
        return key + ':' + rest
    first_q = rest.index(quote_char)
    last_q = rest.rindex(quote_char)
    if first_q >= last_q:
        return line
    prefix = rest[:first_q+1]
    inner = rest[first_q+1:last_q]
    suffix = rest[last_q:]
    for cn, jp in cn_to_jp.items():
        inner = inner.replace(cn, jp)
    return key + ':' + prefix + inner + suffix

lines = content.split('\n')
new_lines = [process_line(line) for line in lines]
content = '\n'.join(new_lines)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

changes = sum(1 for a, b in zip(original, content) if a != b)
print(f"Changes: {changes}")
print("Done!")
