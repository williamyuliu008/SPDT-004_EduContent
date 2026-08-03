import json, sys

path = r'D:/2_products/education/SPDT-004_EduContent/5_deliver/TextExperienceAPP/apps/rujing/entry/src/main/resources/rawfile/geo_cards.json'
with open(path, 'r', encoding='utf-8') as f:
    raw = f.read()

if raw.startswith('\ufeff'):
    print('BOM DETECTED')
else:
    print('NO BOM')

try:
    obj = json.loads(raw)
    print('Valid JSON')
    print('Total cards:', len(obj['cards']))
    print('Total chains:', obj['total_chains'])
    for c in obj['cards'][:4]:
        print(f'  - [{c["id"]}] chain={c["chain_title"]} title={c["title"]}')
        print(f'    content length: {len(c["content"])} chars')
except json.JSONDecodeError as e:
    print('JSON Error:', e)
    sys.exit(1)
