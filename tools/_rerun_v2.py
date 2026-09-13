"""
最终重跑 4 张 fail (60s timeout)
"""
import json, sys, time
from pathlib import Path

sys.path.insert(0, r'D:\Z_学习平台\SPDT-004_EduContent\tools')
from review_qwen import review_one_question, get_api_key

fails = [
    (r'D:\Z_学习平台\knowledge-cards-prod\projects\math\cards\本地上海\PT030_2026-09-13\2016_解析版\pt030_2016_q20_jx_解析几何.json', 'pt030', '数学解析几何'),
    (r'D:\Z_学习平台\knowledge-cards-prod\projects\math\cards\本地上海\PT030_2026-09-13\2023_解析版\pt030_2023_q18_jx_概率统计.json', 'pt030', '数学概率统计'),
    (r'D:\Z_学习平台\knowledge-cards-prod\projects\math\cards\本地上海\PT030_2026-09-13\2025_原卷版\pt030_2025_q11_yj_解三角形.json', 'pt030', '数学解三角形'),
    (r'D:\Z_学习平台\knowledge-cards-prod\projects\math\methods\解三角形\M_解三角形_02_余弦定理.json', 'method', '数学解三角形'),
]
api_key = get_api_key()
ok = 0
for path, ftype, subject in fails:
    path = Path(path)
    print(f'\n=== {path.name} ({ftype}) ===', flush=True)
    t0 = time.time()
    if ftype == 'pt030':
        d = json.loads(path.read_text(encoding='utf-8'))
        # 截断 stem 防长
        stem = d.get('front', '')[:300]
        if not stem:
            print('  SKIP no stem'); continue
        q = {"q_no": 0, "stem": stem, "options": d.get('options', [])}
        result = review_one_question(q, subject, api_key, timeout=60)
        if result.get('_review_failed'):
            print(f'  ❌ {result.get("_error", "?")[:80]} {time.time()-t0:.0f}s'); continue
        d['verdict'] = "TRUE" if result.get('verdict') == '可解' else result.get('verdict', d.get('verdict', 'PENDING'))
        d['difficulty'] = result.get('difficulty', d.get('difficulty', '中档'))
        if result.get('explanation'):
            d['back_detail'] = result['explanation']
        if result.get('answer') and d.get('back') in (None, '', '?'):
            d['back'] = result['answer']
        if result.get('key_concepts'):
            d['key_concepts'] = result['key_concepts']
        if result.get('common_mistakes'):
            d['common_mistakes'] = result['common_mistakes']
        if result.get('variants'):
            d['variants'] = result['variants']
        if result.get('knowledge_tags'):
            d['knowledge_points'] = list(set(d.get('knowledge_points', []) + result['knowledge_tags']))
        d['maturity'] = 'REVIEWED' if d['verdict'] == 'TRUE' else 'DRAFT'
        d['provenance'] = d.get('provenance', {})
        d['provenance']['qwen_review'] = {"model": "qwen-plus", "reviewed_at": time.strftime("%Y-%m-%dT%H:%M:%S"), "rerun_v2": True}
        path.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f'  ✅ {result.get("verdict")} +{len(result.get("variants", []))} 变式 {time.time()-t0:.0f}s', flush=True)
        ok += 1
    else:
        d = json.loads(path.read_text(encoding='utf-8'))
        front = d.get('front', '')[:500]
        import re
        m = re.search(r'【?例题】?(.+?)(?:[。.]\s*[证明求]|\Z)', front, re.DOTALL)
        stem = m.group(1).strip()[:500] if m else front[:500]
        q = {"q_no": 0, "stem": stem, "options": []}
        result = review_one_question(q, subject, api_key, timeout=60)
        if result.get('_review_failed'):
            print(f'  ❌ {result.get("_error", "?")[:80]} {time.time()-t0:.0f}s'); continue
        if result.get('variants'):
            d['qwen_variants'] = result['variants']
        if result.get('key_concepts'):
            d['knowledge_points'] = list(set(d.get('knowledge_points', []) + result['key_concepts']))
        if result.get('common_mistakes'):
            d['common_mistakes'] = list(set(d.get('common_mistakes', []) + result['common_mistakes']))
        d['_qwen_review'] = {"model": "qwen-plus", "reviewed_at": time.strftime("%Y-%m-%dT%H:%M:%S"), "rerun_v2": True, "variants_added": len(result.get('variants', []))}
        path.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f'  ✅ +{len(result.get("variants", []))} 变式 {time.time()-t0:.0f}s', flush=True)
        ok += 1
print(f'\n[rerun_v2] ok={ok}/4')
