"""
审核修复: 4 板块 PT-030 解析版 back 字段空 + 母题 Qwen 变式
=============================================================
A. PT-030 解析版 back 字段空 → Qwen 推演 back (不覆盖其他字段)
B. 4 板块母题没 Qwen 变式 → 跑 Qwen 推演加变式
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
PANELS = ['立体几何', '解析几何', '导数', '概率统计', '解三角形']
PANEL_DIRS = {
    '立体几何': ['二面角', '线面垂直', '线面平行证明', '线面角', '面面平行证明'],
    '解析几何': ['解析几何'],
    '导数': ['导数'],
    '概率统计': ['概率统计'],
    '解三角形': ['解三角形'],
}

api_key = get_api_key()
ok_a = 0
fail_a = 0
ok_b = 0
fail_b = 0

t_start = time.time()

# === A. PT-030 解析版 back 字段空 ===
print('=' * 70)
print('A. PT-030 解析版 back 字段空 → Qwen 推演 back')
print('=' * 70)
back_empty_files = []
for panel in PANELS:
    for f in PT030.rglob('*.json'):
        if 'llm_gen' in str(f) or 'reclassify' in str(f):
            continue
        try:
            d = json.loads(f.read_text(encoding='utf-8'))
            mod = d.get('module', '')
            if panel in mod and d.get('source_paper') == '解析版' and not d.get('back'):
                back_empty_files.append((f, panel))
        except Exception:
            pass
print(f'4 板块解析版 back 空: {len(back_empty_files)} 张')

for i, (f, panel) in enumerate(back_empty_files, 1):
    t0 = time.time()
    try:
        d = json.loads(f.read_text(encoding='utf-8'))
        stem = d.get('front', '')[:300]
        if not stem:
            fail_a += 1
            continue
        q = {'q_no': 0, 'stem': stem, 'options': d.get('options', [])}
        result = review_one_question(q, f'数学{panel}', api_key, timeout=30)
        if result.get('_review_failed'):
            # 100字 retry
            result = review_one_question({'q_no': 0, 'stem': stem[:100], 'options': []}, f'数学{panel}', api_key, timeout=30)
            if result.get('_review_failed'):
                fail_a += 1
                continue
        # 只填 back, 不覆盖其他
        if result.get('answer'):
            d['back'] = result['answer'][:500]
        if result.get('explanation') and not d.get('back_detail'):
            d['back_detail'] = result['explanation'][:500]
        # 加 provenance
        d['provenance'] = d.get('provenance', {})
        d['provenance']['qwen_back_fill'] = {
            'model': 'qwen-plus',
            'reviewed_at': time.strftime('%Y-%m-%dT%H:%M:%S'),
            'method': 'audit_fix',
        }
        d['maturity'] = 'REVIEWED' if d.get('verdict') == 'TRUE' else 'DRAFT'
        f.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding='utf-8')
        ok_a += 1
        if i % 20 == 0 or i == len(back_empty_files):
            avg = (time.time() - t_start) / i
            eta = (len(back_empty_files) - i) * avg
            print(f'  [A {i}/{len(back_empty_files)}] {avg:.1f}s/张 ETA {eta:.0f}s ok={ok_a} fail={fail_a}', flush=True)
    except Exception as e:
        fail_a += 1

print(f'\n[A] 完成: ok={ok_a} fail={fail_a}')


# === B. 4 板块母题没 Qwen 变式 ===
print('\n' + '=' * 70)
print('B. 4 板块母题没 Qwen 变式')
print('=' * 70)
mother_no_qwen = []
for panel in PANELS:
    if panel == '立体几何':
        for d in PANEL_DIRS['立体几何']:
            mother_dir = KCARDS / d
            if not mother_dir.exists():
                continue
            for f in sorted(mother_dir.glob('K[0-9][0-9].json')):
                if 10 <= int(f.stem[1:]) <= 99:
                    try:
                        data = json.loads(f.read_text(encoding='utf-8'))
                        if not data.get('_qwen_review'):
                            mother_no_qwen.append((f, panel))
                    except Exception:
                        pass
    else:
        mother_dir = KCARDS / panel
        if mother_dir.exists():
            for f in sorted(mother_dir.glob('K[0-9][0-9].json')):
                if 10 <= int(f.stem[1:]) <= 99:
                    try:
                        data = json.loads(f.read_text(encoding='utf-8'))
                        if not data.get('_qwen_review'):
                            mother_no_qwen.append((f, panel))
                    except Exception:
                        pass

print(f'4 板块母题没 Qwen: {len(mother_no_qwen)} 张')

for i, (f, panel) in enumerate(mother_no_qwen, 1):
    t0 = time.time()
    try:
        d = json.loads(f.read_text(encoding='utf-8'))
        stem_source = d.get('back', '') or d.get('front', '')
        if not stem_source:
            fail_b += 1
            continue
        if len(stem_source) > 1500:
            stem_source = stem_source[:1500] + '...'
        q = {'q_no': 0, 'stem': stem_source, 'options': []}
        result = review_one_question(q, f'数学{panel}', api_key, timeout=45)
        if result.get('_review_failed'):
            fail_b += 1
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
            'audit_fix': True,
        }
        d['maturity'] = 'REVIEWED'
        f.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding='utf-8')
        ok_b += 1
        if i % 10 == 0 or i == len(mother_no_qwen):
            print(f'  [B {i}/{len(mother_no_qwen)}] ok={ok_b} fail={fail_b} ({f.parent.name}/{f.name})', flush=True)
    except Exception as e:
        fail_b += 1

print(f'\n[B] 完成: ok={ok_b} fail={fail_b}')

elapsed = time.time() - t_start
print(f'\n=== 总耗时 {elapsed/60:.1f} min ===')
print(f'A 解析版 back 补全: {ok_a} 张')
print(f'B 母题 Qwen 变式:  {ok_b} 张')
