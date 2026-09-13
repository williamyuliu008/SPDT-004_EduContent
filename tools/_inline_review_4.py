"""
inline review 4 套春考解析版
"""
import json, time, sys
from pathlib import Path

sys.path.insert(0, r'D:\Z_学习平台\SPDT-004_EduContent\tools')
from review_httpx import review_one_question, get_api_key

api_key = get_api_key()
SPLIT_DIR = Path(r'D:\Z_学习平台\SPDT-004_EduContent\PT-030\zhenti\数学\split')
TARGETS = [
    '2019年上海春季高考数学真题（解析版）_split_v11.json',
    '2020年上海春季高考数学真题（解析版）_split_v11.json',
    '2021年上海春季高考数学真题（解析版）_split_v11.json',
    '2022年上海春季高考数学真题（解析版）_split_v11.json',
]
TIMEOUT = 30

t_start = time.time()
for target in TARGETS:
    sp = SPLIT_DIR / target
    if not sp.exists():
        print(f'MISS: {target}')
        continue
    if (sp.parent / f'{sp.stem.replace("_split_v11", "")}_split_v11_reviewed.json').exists():
        print(f'SKIP (已 review): {target}')
        continue
    d = json.loads(sp.read_text(encoding='utf-8'))
    questions = d.get('questions', [])
    print(f'\n=== {target} ({len(questions)} 题) ===', flush=True)
    t0 = time.time()
    reviewed = []
    for i, q in enumerate(questions, 1):
        t_q = time.time()
        r = review_one_question(q, '数学', api_key, timeout=TIMEOUT)
        merged = {**q, **r}
        reviewed.append(merged)
        if i % 5 == 0 or i == len(questions):
            elapsed = time.time() - t0
            ok = sum(1 for r in reviewed if not r.get('_review_failed'))
            print(f'  [{i}/{len(questions)}] {elapsed:.0f}s ok={ok}', flush=True)
    ok = sum(1 for r in reviewed if not r.get('_review_failed'))
    out = sp.parent / f'{sp.stem.replace("_split_v11", "")}_split_v11_reviewed.json'
    out.write_text(json.dumps({
        'subject': '数学',
        'input_file': str(sp),
        'total': len(questions),
        'reviewed': ok,
        'questions': reviewed,
        '_v1_caveat': 'v1.0 glm-4-flash 推演 (inline 4 套春考解析版)',
        '_created': '2026-09-13 雪薇端 inline 4 套'
    }, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'  ✅ {ok}/{len(questions)} → {out.name}', flush=True)

print(f'\n总耗时 {time.time()-t_start:.0f}s = {(time.time()-t_start)/60:.1f} min')
