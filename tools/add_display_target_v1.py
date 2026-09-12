"""给 56 张 v1.1 4步法卡加 display_target 字段 (雪薇端默认 ["学习中心"])"""
import json
import sys
from pathlib import Path

KB_ROOTS = [
    Path(r'D:\4_data\knowledge_cards\数学\4step'),
    Path(r'D:\4_data\knowledge_cards\历史\4step'),
]

DEFAULT_DISPLAY_TARGET = ['学习中心']  # 雪薇端默认 (v1.0 协作说明拍板)

total = 0
updated = 0
skipped = 0
for root in KB_ROOTS:
    for json_file in root.rglob('*.json'):
        try:
            data = json.loads(json_file.read_text(encoding='utf-8'))
        except json.JSONDecodeError:
            continue
        total += 1
        if 'display_target' in data:
            skipped += 1
            continue
        data['display_target'] = DEFAULT_DISPLAY_TARGET
        data['_v30_display_target_added'] = '2026-09-12 by 宇兄窗口 A2 任务'
        # 用 utf-8 无 BOM 写回
        json_file.write_bytes(json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8'))
        updated += 1

print(f'Total scanned: {total}')
print(f'Updated: {updated}')
print(f'Skipped (already has field): {skipped}')
print(f'display_target 默认值: {DEFAULT_DISPLAY_TARGET} (雪薇端, 拍板)')
