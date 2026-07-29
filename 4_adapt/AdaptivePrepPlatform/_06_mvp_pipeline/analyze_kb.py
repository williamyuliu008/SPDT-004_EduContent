# -*- coding: utf-8 -*-
import json
import sys

path = r'D:\92_products\SPDT-004_EduContent\PT-037_AdaptivePrepPlatform\_03_subject_packs\cafa_calligraphy_2026\knowledge\kb_vocab_enhanced.json'
with open(path, 'r', encoding='utf-8') as f:
    data = json.load(f)

entries = []
for mod in data['modules'].values():
    for item in mod.values():
        for e in item:
            if e.get('kb_id', '').startswith('KB_CAFA_S'):
                entries.append(e)

print(f'总书法史条目: {len(entries)}')
has_bg = [e for e in entries if e.get('structured_content', {}).get('background')]
real_bg = [e for e in has_bg if not str(e['structured_content']['background']).startswith('LLMResponse') and len(e['structured_content'].get('background', '')) > 50]
mock_bg = [e for e in has_bg if str(e['structured_content']['background']).startswith('LLMResponse') or len(e['structured_content'].get('background', '')) <= 50]
print(f'有background字段: {len(has_bg)}')
print(f'真实background (>50字): {len(real_bg)}')
print(f'mock/空background: {len(mock_bg)}')

if real_bg:
    e = real_bg[0]
    bg = e['structured_content']['background']
    print(f'\n真实样例 ({e["kb_id"]}):\n{bg[:200]}')
if mock_bg:
    e = mock_bg[0]
    bg = e['structured_content']['background']
    print(f'\nmock样例 ({e["kb_id"]}):\n{repr(bg[:150])}')

# 检查各条目有哪些字段
print('\n\n=== 字段统计 ===')
fields = {}
for e in entries[:5]:
    sc = e.get('structured_content', {})
    print(f'\n{e["kb_id"]} 字段: {list(sc.keys())}')
    print(f'  exam_tips: {type(e.get("exam_tips")).__name__}')
    print(f'  answer_template: {type(e.get("answer_template")).__name__}')
    print(f'  cross_pack_links: {type(e.get("cross_pack_links")).__name__}')
