# -*- coding: utf-8 -*-
import sys, json
sys.stdout.reconfigure(encoding='utf-8')
path = r'D:\2_products\education\SPDT-004_EduContent\5_deliver\TextExperienceAPP\apps\rujing\entry\src\main\resources\rawfile\geo_cards.json'
with open(path, encoding='utf-8') as f:
    content = f.read()
if content.startswith('\ufeff'):
    content = content[1:]
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print('BOM stripped and written back')
try:
    json.loads(content)
    print('JSON OK')
except json.JSONDecodeError as e:
    print(f'Error at char {e.pos}: {e.msg}')
    pos = e.pos
    line_no = content[:pos].count('\n') + 1
    print(f'Line {line_no}')
    print(repr(content[max(0,pos-80):pos+80]))
