"""修 hp_005 core_method 长度"""
import json
from pathlib import Path
p = Path(r'D:\4_data\knowledge_cards\历史\4step\parent_problems\hp_005_阶段时间线_经济全球化.json')
raw = p.read_bytes()
if raw.startswith(b'\xef\xbb\xbf'):
    raw = raw[3:]
data = json.loads(raw.decode('utf-8'))
data['core_method'] = "阶段时间线填空法（按 4 阶段模型匹配）"
p.write_bytes(json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8'))
print('fixed hp_005 core_method length')
