import json, re

path = r'D:/2_products/education/SPDT-004_EduContent/5_deliver/TextExperienceAPP/apps/rujing/entry/src/main/resources/rawfile/geo_cards.json'
with open(path, 'r', encoding='utf-8') as f:
    raw = f.read()

# Show content around position 467
print(f'File size: {len(raw)}')
print(f'Content around pos 467:')
print(repr(raw[440:520]))

# Check if there are literal \r characters
if '\r' in raw:
    print(f'\nFound {raw.count(chr(13))} CR characters')
    # Find first few
    idx = raw.find('\r')
    while idx != -1 and idx < 600:
        print(f'  CR at pos {idx}: ...{repr(raw[max(0,idx-10):idx+10])}...')
        idx = raw.find('\r', idx+1)
else:
    print('\nNo CR characters found')

# Count lines
lines = raw.split('\n')
print(f'\nLine count: {len(lines)}')
if len(lines) >= 13:
    l13 = lines[12]
    print(f'Line 13 (index 12):')
    print(f'  Length: {len(l13)}')
    print(f'  Repr: {repr(l13[130:150])}')
