"""
Rerun V3: 短 stem 重试 3 张 PT-030 fail
"""
import json, sys, time
sys.path.insert(0, r'D:\Z_学习平台\SPDT-004_EduContent\tools')
from review_qwen import review_one_question, get_api_key

api_key = get_api_key()
PATHS = [
    (r'D:\Z_学习平台\knowledge-cards-prod\projects\math\cards\本地上海\PT030_2026-09-13\2016_解析版\pt030_2016_q20_jx_解析几何.json', '数学解析几何'),
    (r'D:\Z_学习平台\knowledge-cards-prod\projects\math\cards\本地上海\PT030_2026-09-13\2023_解析版\pt030_2023_q18_jx_概率统计.json', '数学概率统计'),
    (r'D:\Z_学习平台\knowledge-cards-prod\projects\math\cards\本地上海\PT030_2026-09-13\2025_原卷版\pt030_2025_q11_yj_解三角形.json', '数学解三角形'),
]
ok = 0
for p, subject in PATHS:
    print(f'\n{p}', flush=True)
    t0 = time.time()
    d = json.loads(open(p, encoding='utf-8').read())
    stem = d.get('front', '')[:200]  # 短 stem
    if not stem:
        print('  SKIP no stem')
        continue
    q = {'q_no': 0, 'stem': stem, 'options': d.get('options', [])}
    result = review_one_question(q, subject, api_key, timeout=45)
    if result.get('_review_failed'):
        print(f'  ❌ short: {result.get("_error","?")[:60]} {time.time()-t0:.0f}s')
        # retry 100字
        result = review_one_question({'q_no':0, 'stem':stem[:100], 'options':[]}, subject, api_key, timeout=45)
        if result.get('_review_failed'):
            print(f'  ❌ retry: {result.get("_error","?")[:60]}')
            continue
    # 升级
    d['verdict'] = 'TRUE' if result.get('verdict')=='可解' else result.get('verdict','PENDING')
    d['difficulty'] = result.get('difficulty', d.get('difficulty','中档'))
    if result.get('explanation'):
        d['back_detail'] = result['explanation'][:500]
    if result.get('key_concepts'):
        d['key_concepts'] = result['key_concepts']
    if result.get('common_mistakes'):
        d['common_mistakes'] = result['common_mistakes']
    if result.get('variants'):
        d['variants'] = result['variants'][:1]
    d['provenance'] = d.get('provenance', {})
    d['provenance']['qwen_review'] = {'model':'qwen-plus', 'reviewed_at':time.strftime('%Y-%m-%dT%H:%M:%S'), 'rerun_v3':True, 'short_stem':True}
    d['maturity'] = 'REVIEWED' if d['verdict']=='TRUE' else 'DRAFT'
    open(p,'w',encoding='utf-8').write(json.dumps(d, ensure_ascii=False, indent=2))
    print(f'  ✅ {result.get("verdict")} {time.time()-t0:.0f}s')
    ok += 1

# M_解三角形_02_余弦定理
mp = r'D:\Z_学习平台\knowledge-cards-prod\projects\math\methods\解三角形\M_解三角形_02_余弦定理.json'
print(f'\n{mp}', flush=True)
t0 = time.time()
md = json.loads(open(mp, encoding='utf-8').read())
front = md.get('front', '')[:500]
import re
m = re.search(r'【?例题】?(.+?)(?:[。.]\s*[证明求]|\Z)', front, re.DOTALL)
stem = m.group(1).strip()[:400] if m else front[:400]
q = {'q_no': 0, 'stem': stem, 'options': []}
result = review_one_question(q, '数学解三角形', api_key, timeout=45)
if result.get('_review_failed'):
    print(f'  ❌ {result.get("_error","?")[:60]} {time.time()-t0:.0f}s')
else:
    if result.get('variants'):
        md['qwen_variants'] = result['variants']
    if result.get('key_concepts'):
        md['knowledge_points'] = list(set(md.get('knowledge_points', []) + result['key_concepts']))
    if result.get('common_mistakes'):
        md['common_mistakes'] = list(set(md.get('common_mistakes', []) + result['common_mistakes']))
    md['_qwen_review'] = {'model':'qwen-plus', 'reviewed_at':time.strftime('%Y-%m-%dT%H:%M:%S'), 'rerun_v3':True, 'variants_added': len(result.get('variants', []))}
    open(mp,'w',encoding='utf-8').write(json.dumps(md, ensure_ascii=False, indent=2))
    print(f'  ✅ +{len(result.get("variants",[]))} 变式 {time.time()-t0:.0f}s')
    ok += 1

print(f'\n=== ok={ok}/4 ===')
