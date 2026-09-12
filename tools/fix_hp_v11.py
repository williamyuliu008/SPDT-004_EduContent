"""给 hp_001-005 加 v1.1 缺失字段"""
import json
from pathlib import Path

HP_DIR = Path(r'D:\4_data\knowledge_cards\历史\4step\parent_problems')
for p in sorted(HP_DIR.glob('hp_*.json')):
    raw = p.read_bytes()
    if raw.startswith(b'\xef\xbb\xbf'):
        raw = raw[3:]
    text = raw.decode('utf-8')
    data = json.loads(text)
    if 'concepts_used' not in data:
        data['concepts_used'] = []  # 历史 v1.1 暂不关联具体概念卡
    if 'variant_ids' not in data:
        data['variant_ids'] = []  # v1.1 暂不带变形
    # 加 _v11 标记
    if '_v11_auto_generated' not in data:
        data['_v11_auto_generated'] = True
    p.write_bytes(json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8'))
    print(f'fixed: {p.name}')
print('DONE')
