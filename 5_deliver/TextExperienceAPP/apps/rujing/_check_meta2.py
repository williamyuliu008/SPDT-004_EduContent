import json
meta_path = r'D:/2_products/education/SPDT-004_EduContent/1_ingest/test_data/geo_shanhe_2026/meta.json'
with open(meta_path, 'r', encoding='utf-8') as f:
    meta = json.load(f)
modules = meta.get('modules', [])
print(f'Module count: {len(modules)}')
for m in modules[:3]:
    print(f'  {m.get("chain_id", "N/A")}: {m.get("chain_name", "N/A")}')
    print(f'    tags: {m.get("chain_tags", [])[:3]}')
    print(f'    causal: {m.get("causal_logic", "")[:60]}')
