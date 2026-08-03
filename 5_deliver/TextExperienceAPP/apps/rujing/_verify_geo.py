import json

path = r'D:/2_products/education/SPDT-004_EduContent/5_deliver/TextExperienceAPP/apps/rujing/entry/src/main/resources/rawfile/geo_cards.json'

with open(path, 'r', encoding='utf-8') as f:
    raw = f.read()

# Check BOM
if raw.startswith('\ufeff'):
    print('BOM detected!')
else:
    print('NO BOM - OK')

# Check control chars
ctrl = [(i, ord(c), repr(c)) for i, c in enumerate(raw) if ord(c) < 32 and c not in '\n\t']
if ctrl:
    print(f'Control chars found: {ctrl}')
else:
    print('No control chars - OK')

# Validate JSON
try:
    obj = json.loads(raw)
    print(f'Valid JSON: {obj["total_cards"]} cards, {obj["total_chains"]} chains')
    print(f'Package title: {obj["package_title"]}')
    for c in obj['node_cards'][:4]:
        print(f'  [{c["card_id"]}] chain={c["chain_title"]} title={c["front"][:20]}...')
except json.JSONDecodeError as e:
    print(f'JSON Error: {e}')
