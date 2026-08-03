import json, sys

path = r'D:/2_products/education/SPDT-004_EduContent/5_deliver/TextExperienceAPP/apps/rujing/entry/src/main/resources/rawfile/geo_cards.json'
with open(path, 'r', encoding='utf-8') as f:
    raw = f.read()

# Find and show control chars
for i, c in enumerate(raw):
    code = ord(c)
    if code < 32 and c not in '\n\r\t':
        print(f'Control char at pos {i}: 0x{code:02X} = {repr(c)}')
        start = max(0, i-20)
        print(f'  Context: {repr(raw[start:i+20])}')

# Fix: replace \r that causes issues
fixed = raw.replace('\r', '')
with open(path, 'w', encoding='utf-8') as f:
    f.write(fixed)
print('Fixed and saved')

# Re-check
with open(path, 'r', encoding='utf-8') as f:
    raw2 = f.read()
try:
    obj = json.loads(raw2)
    print('Valid JSON after fix')
    print('Total cards:', len(obj['cards']))
except json.JSONDecodeError as e:
    print('Still invalid:', e)
