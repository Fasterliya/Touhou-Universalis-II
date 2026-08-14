import sys

files = [
    r'F:\Paradox Interactive\Europa Universalis V\mod\Touhou Universalis II\main_menu\localization\english\th_map_l_english.yml',
    r'F:\Paradox Interactive\Europa Universalis V\mod\Touhou Universalis II\main_menu\localization\simp_chinese\th_map_l_simp_chinese.yml',
    r'F:\Paradox Interactive\Europa Universalis V\mod\Touhou Universalis II\main_menu\localization\korean\th_culture_l_korean.yml',
]
for f in files:
    data = open(f, 'rb').read()
    if data[:3] == b'\xef\xbb\xbf':
        data = data[3:]
    text = data.decode('utf-8')
    before = sum(text.count(c) for c in '\u201c\u201d\u2018\u2019')
    text = text.replace('\u201c', '"').replace('\u201d', '"')
    text = text.replace('\u2018', "'").replace('\u2019', "'")
    open(f, 'wb').write(b'\xef\xbb\xbf' + text.encode('utf-8'))
    print(f.split('localization\\')[1], 'curly replaced:', before)
