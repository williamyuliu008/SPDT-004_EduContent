"""
修复 v1.1 新母题文件的 BOM 和字段名错误
- 去掉 UTF-8 BOM
- variant_ids_pending -> variant_ids: []
"""

import json
import re
from pathlib import Path

KB = Path(r'D:\4_data\knowledge_cards\数学\4step\parent_problems')
new_files = sorted(KB.glob('pp_*.json'))[-10:]  # pp_006-pp_015
for p in new_files:
    raw = p.read_bytes()
    if raw.startswith(b'\xef\xbb\xbf'):
        raw = raw[3:]
    text = raw.decode('utf-8')
    new_text = re.sub(
        r'"variant_ids_pending":\s*"v1\.1 补 3 变形[^"]*"',
        '"variant_ids": []',
        text
    )
    p.write_bytes(new_text.encode('utf-8'))
    print('fixed:', p.name)
print('ALL DONE')
