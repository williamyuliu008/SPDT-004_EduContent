"""
最终重跑: 33 张 back 仍空 + 3 张母题没 Qwen
"""
import json, sys, time
from pathlib import Path
sys.path.insert(0, r'D:\Z_学习平台\SPDT-004_EduContent\tools')
from review_qwen import review_one_question, get_api_key

api_key = get_api_key()
KCARDS = Path(r'D:\Z_学习平台\knowledge-cards-prod\projects\math\cards')
PT030 = KCARDS / '本地上海' / 'PT030_2026-09-13'
PANELS = ['立体几何', '解析几何', '导数', '概率统计', '解三角形']

# A. 33 张 back 仍空
back_empty = []
for f in PT030.rglob('*.json'):
    if 'llm_gen' in str(f) or 'reclassify' in str(f):
        continue
    try:
        d = json.loads(f.read_text(encoding='utf-8'))
        for panel in PANELS:
            if panel in d.get('module', '') and d.get('source_paper') == '解析版' and not d.get('back'):
                back_empty.append((f, panel))
                break
    except Exception:
        pass

print(f'A. 33 张 back 空 重跑 (60s timeout + 短 stem):', flush=True)
ok_a = 0
for f, panel in back_empty:
    t0 = time.time()
    try:
        d = json.loads(f.read_text(encoding='utf-8'))
        # 用更短 stem
        stem = d.get('front', '')[:150]
        if not stem:
            continue
        q = {'q_no': 0, 'stem': stem, 'options': d.get('options', [])[:2]}
        result = review_one_question(q, f'数学{panel}', api_key, timeout=60)
        if result.get('_review_failed'):
            # retry 80字
            result = review_one_question({'q_no':0, 'stem':stem[:80], 'options':[]}, f'数学{panel}', api_key, timeout=60)
            if result.get('_review_failed'):
                print(f'  ❌ {f.name}: {result.get("_error","?")[:50]}', flush=True)
                continue
        if result.get('answer'):
            d['back'] = result['answer'][:500]
        if result.get('explanation') and not d.get('back_detail'):
            d['back_detail'] = result['explanation'][:500]
        d['provenance'] = d.get('provenance', {})
        d['provenance']['qwen_back_fill_v2'] = {'model':'qwen-plus', 'reviewed_at':time.strftime('%Y-%m-%dT%H:%M:%S'), 'short_stem':True}
        d['maturity'] = 'REVIEWED' if d.get('verdict') == 'TRUE' else 'DRAFT'
        f.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding='utf-8')
        ok_a += 1
    except Exception as e:
        print(f'  ❌ {f.name}: {e}', flush=True)

print(f'\nA. 重跑: ok={ok_a}/{len(back_empty)}')

# B. 3 张母题没 Qwen
mother_no_qwen = []
for panel in PANELS:
    if panel == '立体几何':
        for d in ['二面角', '线面垂直', '线面平行证明', '线面角', '面面平行证明']:
            md = KCARDS / d
            if md.exists():
                for f in sorted(md.glob('K[0-9][0-9].json')):
                    if 10 <= int(f.stem[1:]) <= 99:
                        try:
                            d_data = json.loads(f.read_text(encoding='utf-8'))
                            if not d_data.get('_qwen_review'):
                                mother_no_qwen.append((f, panel))
                        except Exception:
                            pass
    else:
        md = KCARDS / panel
        if md.exists():
            for f in sorted(md.glob('K[0-9][0-9].json')):
                if 10 <= int(f.stem[1:]) <= 99:
                    try:
                        d_data = json.loads(f.read_text(encoding='utf-8'))
                        if not d_data.get('_qwen_review'):
                            mother_no_qwen.append((f, panel))
                    except Exception:
                        pass

print(f'\nB. 3 张母题没 Qwen 重跑 (60s timeout):', flush=True)
ok_b = 0
for f, panel in mother_no_qwen:
    t0 = time.time()
    try:
        d = json.loads(f.read_text(encoding='utf-8'))
        stem = d.get('back','') or d.get('front','')
        if len(stem) > 1500:
            stem = stem[:1500] + '...'
        if not stem:
            continue
        q = {'q_no':0, 'stem':stem, 'options':[]}
        result = review_one_question(q, f'数学{panel}', api_key, timeout=60)
        if result.get('_review_failed'):
            print(f'  ❌ {f.parent.name}/{f.name}: {result.get("_error","?")[:50]}', flush=True)
            continue
        qwen_variants = result.get('variants', [])
        existing = d.get('derived_variants', [])
        if isinstance(existing, list):
            d['derived_variants'] = existing + [
                {**v, '_qwen_reviewed':True, '_at':time.strftime('%Y-%m-%dT%H:%M:%S')}
                for v in qwen_variants
            ]
        else:
            d['derived_variants'] = [
                {**v, '_qwen_reviewed':True, '_at':time.strftime('%Y-%m-%dT%H:%M:%S')}
                for v in qwen_variants
            ]
        if result.get('key_concepts'):
            d['concepts'] = list(set(d.get('concepts',[]) + result['key_concepts']))
        if result.get('common_mistakes'):
            d['common_mistakes'] = list(set(d.get('common_mistakes',[]) + result['common_mistakes']))
        d['_qwen_review'] = {
            'model':'qwen-plus',
            'reviewed_at':time.strftime('%Y-%m-%dT%H:%M:%S'),
            'variants_added':len(qwen_variants),
            'audit_final':True,
        }
        d['maturity'] = 'REVIEWED'
        f.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding='utf-8')
        ok_b += 1
        print(f'  ✅ {f.parent.name}/{f.name} +{len(qwen_variants)} 变式', flush=True)
    except Exception as e:
        print(f'  ❌ {f.parent.name}/{f.name}: {e}', flush=True)

print(f'\nB. 重跑: ok={ok_b}/{len(mother_no_qwen)}')
print(f'\n=== 总完成: A {ok_a} + B {ok_b} ===')
