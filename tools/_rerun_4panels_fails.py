"""
重跑 4 板块 Qwen fail 的卡
=======================
找到所有 _qwen_review 标记的卡, 但实际没升级的 (Qwen hang fail)
"""
import json
import sys
import time
from pathlib import Path
import httpx

sys.path.insert(0, r'D:\Z_学习平台\SPDT-004_EduContent\tools')
from review_qwen import review_one_question, get_api_key, QWEN_ENDPOINT

KCARDS = Path(r'D:\Z_学习平台\knowledge-cards-prod\projects\math\cards')
PT030 = KCARDS / '本地上海' / 'PT030_2026-09-13'
METHODS = KCARDS.parent / 'methods'

# === 找所有 fail 的卡 ===
fails = []  # [(path, type, subject)]

# PT-030: 找 4 板块 + 还没 _qwen_review 标记的
for panel, cfg in {
    '解析几何': ('解析几何', '数学解析几何'),
    '导数': ('导数', '数学导数'),
    '概率统计': ('概率统计', '数学概率统计'),
    '解三角形': ('解三角形', '数学解三角形'),
}.items():
    for f in PT030.rglob('*.json'):
        if 'llm_gen' in str(f):
            continue
        try:
            d = json.loads(f.read_text(encoding='utf-8'))
            mod = d.get('module', '')
            if (panel in mod) and not d.get('provenance', {}).get('qwen_review'):
                # 启发式没匹配重分类后的, 跳过 (用 module 检查)
                fails.append((f, 'pt030', cfg[1], panel))
        except Exception:
            pass

# 方法论: 找 4 板块 + 还没 _qwen_review
for panel in ['解析几何', '导数', '概率统计', '解三角形']:
    method_dir = METHODS / panel
    if not method_dir.exists():
        continue
    for f in method_dir.glob('M_*.json'):
        try:
            d = json.loads(f.read_text(encoding='utf-8'))
            if not d.get('_qwen_review'):
                fails.append((f, 'method', f'数学{panel}', panel))
        except Exception:
            pass

print(f'[rerun] 总 fail: {len(fails)}')

# === 重跑 ===
api_key = get_api_key()
ok = 0
fail_count = 0
t0_total = time.time()
for path, ftype, subject, panel in fails:
    print(f'  [{panel}/{ftype}] {path.name}', flush=True)
    t0 = time.time()
    try:
        if ftype == 'pt030':
            d = json.loads(path.read_text(encoding='utf-8'))
            q = {
                "q_no": d.get('id', '').split('_q')[-1] if 'q' in d.get('id', '') else 0,
                "stem": d.get('front', ''),
                "options": d.get('options', []),
            }
            if not q["stem"]:
                print(f'    SKIP no stem', flush=True)
                continue
            result = review_one_question(q, subject, api_key, timeout=60)
            if result.get('_review_failed'):
                print(f'    ❌ {result.get("_error", "?")[:60]} ({time.time()-t0:.0f}s)', flush=True)
                fail_count += 1
                continue
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
            if result.get('estimated_time_minutes'):
                d['estimated_time_minutes'] = result['estimated_time_minutes']
            d['maturity'] = 'REVIEWED' if d['verdict'] == 'TRUE' else 'DRAFT'
            d['provenance'] = d.get('provenance', {})
            d['provenance']['qwen_review'] = {
                "model": "qwen-plus", "reviewed_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "rerun": True,
            }
            path.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding='utf-8')
            print(f'    ✅ {result.get("verdict")} {len(result.get("variants", []))} 变式 ({time.time()-t0:.0f}s)', flush=True)
            ok += 1
        else:  # method
            d = json.loads(path.read_text(encoding='utf-8'))
            front = d.get('front', '')
            import re
            m = re.search(r'【?例题】?(.+?)(?:[。.]\s*[证明求]|\Z)', front, re.DOTALL)
            stem = m.group(1).strip()[:800] if m else front[:800]
            q = {"q_no": 0, "stem": stem, "options": []}
            result = review_one_question(q, subject, api_key, timeout=60)
            if result.get('_review_failed'):
                print(f'    ❌ {result.get("_error", "?")[:60]} ({time.time()-t0:.0f}s)', flush=True)
                fail_count += 1
                continue
            if result.get('variants'):
                d['qwen_variants'] = result['variants']
            if result.get('key_concepts'):
                d['knowledge_points'] = list(set(d.get('knowledge_points', []) + result['key_concepts']))
            if result.get('common_mistakes'):
                d['common_mistakes'] = list(set(d.get('common_mistakes', []) + result['common_mistakes']))
            d['_qwen_review'] = {
                "model": "qwen-plus", "reviewed_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "rerun": True, "variants_added": len(result.get('variants', [])),
            }
            path.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding='utf-8')
            print(f'    ✅ +{len(result.get("variants", []))} 变式 ({time.time()-t0:.0f}s)', flush=True)
            ok += 1
    except Exception as e:
        print(f'    ❌ ERR {e} ({time.time()-t0:.0f}s)', flush=True)
        fail_count += 1

print(f'\n[rerun] 完成: ok={ok} fail={fail_count} 耗时 {time.time()-t0_total:.0f}s')
