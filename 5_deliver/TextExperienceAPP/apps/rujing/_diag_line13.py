import json

path = r'D:/2_products/education/SPDT-004_EduContent/5_deliver/TextExperienceAPP/apps/rujing/entry/src/main/resources/rawfile/geo_cards.json'
with open(path, 'r', encoding='utf-8') as f:
    raw = f.read()

lines = raw.split('\n')
print(f'Total lines: {len(lines)}')
if len(lines) >= 13:
    line13 = lines[12]  # 0-indexed
    print(f'Line 13 length: {len(line13)}')
    print(f'Line 13 repr: {repr(line13[130:150])}')
    # Check for control chars
    for i, c in enumerate(line13):
        code = ord(c)
        if code < 32 and c not in '\n\t':
            print(f'  Control at col {i}: 0x{code:02X}')
