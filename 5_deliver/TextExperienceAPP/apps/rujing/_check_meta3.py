import json
meta_path = r'D:/2_products/education/SPDT-004_EduContent/1_ingest/test_data/geo_shanhe_2026/meta.json'
with open(meta_path, 'r', encoding='utf-8') as f:
    meta = json.load(f)
modules = meta.get('modules', [])
print(f'Module count: {len(modules)}')
for i, m in enumerate(modules[:2]):
    print(f'Module {i}: keys = {list(m.keys())}')
    print(f'  Value: {json.dumps(m, ensure_ascii=False, indent=2)[:300]}')
