import json, re, sys

path = r'D:/2_products/education/SPDT-004_EduContent/5_deliver/TextExperienceAPP/apps/rujing/entry/src/main/resources/rawfile/geo_cards.json'
out_path = r'D:/2_products/education/SPDT-004_EduContent/5_deliver/TextExperienceAPP/apps/rujing/_diag_out.txt'

with open(path, 'r', encoding='utf-8') as f:
    raw = f.read()

lines = raw.split('\n')
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(f'File size: {len(raw)}\n')
    f.write(f'Line count: {len(lines)}\n')
    f.write(f'Line 13 (index 12):\n')
    if len(lines) >= 13:
        l13 = lines[12]
        f.write(f'  Length: {len(l13)}\n')
        # Find control chars in line 13
        for i, c in enumerate(l13):
            code = ord(c)
            if code < 32:
                f.write(f'  Control at col {i}: 0x{code:02X} = {repr(c)}\n')
        # Show char 467
        f.write(f'Char 467: {repr(raw[467])}\n')
    f.write(f'\nAll control chars in file:\n')
    for i, c in enumerate(raw):
        code = ord(c)
        if code < 32 and c not in '\n\t':
            f.write(f'  pos {i}: 0x{code:02X} = {repr(c)}\n')

print('Written to', out_path)
