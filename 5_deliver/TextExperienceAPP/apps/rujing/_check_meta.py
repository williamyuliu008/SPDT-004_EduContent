import json
meta_path = r'D:/2_products/education/SPDT-004_EduContent/1_ingest/test_data/geo_shanhe_2026/meta.json'
with open(meta_path, 'r', encoding='utf-8') as f:
    meta = json.load(f)
print('Top-level keys:', list(meta.keys()))
