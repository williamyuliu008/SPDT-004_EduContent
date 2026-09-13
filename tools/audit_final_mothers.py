"""
3 张母题没 Qwen 补完 (K10-K18 变式卡)
"""
import json, sys, time
from pathlib import Path
sys.path.insert(0, r'D:\Z_学习平台\SPDT-004_EduContent\tools')
from review_qwen import review_one_question, get_api_key
api_key = get_api_key()

PATHS = [
    r'D:\Z_学习平台\knowledge-cards-prod\projects\math\cards\线面垂直\K10.json',
    r'D:\Z_学习平台\knowledge-cards-prod\projects\math\cards\线面垂直\K16.json',
    r'D:\Z_学习平台\knowledge-cards-prod\projects\math\cards\线面平行证明\K11.json',
]
for p in PATHS:
    name = Path(p).name
    print(f'\n=== {name} ===', flush=True)
    t0 = time.time()
    d = json.loads(open(p, encoding='utf-8').read())
    stem = d.get('back','') or d.get('front','')
    if len(stem) > 1500:
        stem = stem[:1500] + '...'
    if not stem:
        print('  SKIP no stem')
        continue
    q = {'q_no': 0, 'stem': stem, 'options': []}
    result = review_one_question(q, '数学立体几何', api_key, timeout=60)
    if result.get('_review_failed'):
        err = result.get('_error', '?')[:60]
        print(f'  ❌ {err} {time.time()-t0:.0f}s')
        continue
    qwen_variants = result.get('variants', [])
    existing = d.get('derived_variants', [])
    if isinstance(existing, list):
        d['derived_variants'] = existing + [
            {**v, '_qwen_reviewed': True, '_at': time.strftime('%Y-%m-%dT%H:%M:%S')}
            for v in qwen_variants
        ]
    else:
        d['derived_variants'] = [
            {**v, '_qwen_reviewed': True, '_at': time.strftime('%Y-%m-%dT%H:%M:%S')}
            for v in qwen_variants
        ]
    if result.get('key_concepts'):
        d['concepts'] = list(set(d.get('concepts', []) + result['key_concepts']))
    if result.get('common_mistakes'):
        d['common_mistakes'] = list(set(d.get('common_mistakes', []) + result['common_mistakes']))
    d['_qwen_review'] = {
        'model': 'qwen-plus',
        'reviewed_at': time.strftime('%Y-%m-%dT%H:%M:%S'),
        'variants_added': len(qwen_variants),
        'audit_final_v2': True,
    }
    d['maturity'] = 'REVIEWED'
    open(p, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False, indent=2))
    print(f'  ✅ +{len(qwen_variants)} 变式 {time.time()-t0:.0f}s')
