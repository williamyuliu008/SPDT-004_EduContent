# -*- coding: utf-8 -*-
import json

with open(r'D:\92_products\SPDT-004_EduContent\PT-037_AdaptivePrepPlatform\_03_subject_packs\cafa_calligraphy_2026\knowledge\kb_vocab_enhanced.json', encoding='utf-8') as f:
    data = json.load(f)

count = 0
example = None

def walk(obj):
    global count, example
    if isinstance(obj, dict):
        sc = obj.get('structured_content', {})
        if isinstance(sc, dict):
            for k, v in sc.items():
                if isinstance(v, str) and len(v) > 50 and not v.startswith('LLMResponse'):
                    count += 1
                    if example is None:
                        example = (obj.get('kb_id', '?'), obj.get('concept', ''), k, v)
        for v in obj.values():
            walk(v)
    elif isinstance(obj, list):
        for i in obj:
            walk(i)

walk(data)
print('Total enhanced:', count)
if example:
    kb_id, concept, key, text = example
    print('First example:')
    print('  kb_id:', kb_id)
    print('  concept:', concept)
    print('  key:', key)
    print('  text:', text[:300])
