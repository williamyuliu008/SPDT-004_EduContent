"""
Qwen3.5-Plus 立体几何专项批量 review v1.0
==========================================
围绕立体几何, 升级质量:
1. PT030 入库的立体几何 K 卡 (8 张) → 加 Qwen 推演 verdict/explanation/variants
2. 1 窗口 4 板块 DRAFT K10-K15 (二面角/线面垂直/线面角/面面平行证明) → 用 Qwen 推演填充 front/back
3. 5 张方法论 M_立体_01~05 → 加 Qwen 推演的变式题 + 新例题

输出: 升级后的 K 卡 (原地修改) + _qwen_review.json 报告
"""

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, r'D:\Z_学习平台\SPDT-004_EduContent\tools')
from review_qwen import review_one_question, get_api_key

KCARDS_DIR = Path(r'D:\Z_学习平台\knowledge-cards-prod\projects\math\cards')
PT030_DIR = KCARDS_DIR / '本地上海' / 'PT030_2026-09-13'
METHODS_DIR = KCARDS_DIR.parent / 'methods' / '立体几何'
LITI_DIRS = ['二面角', '线面垂直', '线面平行证明', '线面角', '面面平行证明']
LITI_QWEN_OUTPUT = METHODS_DIR / 'qwen_review_liti.json'


def upgrade_pt030_kcard(kcard_path: Path, api_key: str) -> tuple[bool, dict]:
    """升级 PT030 立体几何 K 卡: Qwen 推演 verdict/explanation/variants"""
    try:
        d = json.loads(kcard_path.read_text(encoding='utf-8'))
    except Exception as e:
        return (False, {"error": f"read: {e}"})

    # 构造 question
    q = {
        "q_no": d.get('id', '').split('_q')[-1] if 'q' in d.get('id', '') else 0,
        "stem": d.get('front', ''),
        "options": d.get('options', []),
    }
    if not q["stem"]:
        return (False, {"error": "no stem"})

    # Qwen 推演
    result = review_one_question(q, "数学立体几何", api_key, timeout=45)
    if result.get('_review_failed'):
        return (False, result)

    # 升级字段
    d['verdict'] = "TRUE" if result.get('verdict') == '可解' else result.get('verdict', d.get('verdict', 'PENDING'))
    d['difficulty'] = result.get('difficulty', d.get('difficulty', '中档'))
    d['score'] = d.get('score') or 5
    if result.get('explanation'):
        d['back_detail'] = result['explanation']
    if result.get('answer'):
        d['back'] = result['answer'] if d.get('back') in (None, '', '?') else d['back']
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

    # maturity 升级
    d['maturity'] = 'REVIEWED' if d['verdict'] == 'TRUE' else 'DRAFT'

    # 加 Qwen provenance
    d['provenance'] = d.get('provenance', {})
    d['provenance']['qwen_review'] = {
        "model": "qwen-plus",
        "reviewed_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "extracted_by": "batch_review_qwen_liti.py v1.0",
    }

    # 写回
    kcard_path.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding='utf-8')
    return (True, result)


def upgrade_mother_card(mother_path: Path, api_key: str) -> tuple[bool, dict]:
    """升级 1 窗口 4 板块 K10-K15 母题: 用 Qwen 推演加变式"""
    try:
        d = json.loads(mother_path.read_text(encoding='utf-8'))
    except Exception as e:
        return (False, {"error": f"read: {e}"})

    # 跳过已有 Qwen 推演的
    if d.get('_qwen_review'):
        return (True, {"_skip": "already qwen reviewed", "variants_added": d['_qwen_review'].get('variants_added', 0)})

    # 母题通常 front 是"[CHAIN_xxx] 母题 xx 的完整证明过程是什么？", 不直接给题干
    # 提取题目: 用 back 字段作为题干 (前 1500 字)
    stem_source = d.get('back', '') or d.get('front', '')
    if not stem_source:
        return (False, {"error": "no back/stem"})

    # 截断 stem (防止过长导致 Qwen 慢)
    if len(stem_source) > 1500:
        stem_source = stem_source[:1500] + "..."

    q = {"q_no": 0, "stem": stem_source, "options": []}
    result = review_one_question(q, "数学立体几何", api_key, timeout=45)
    if result.get('_review_failed'):
        return (False, result)

    # 升级母题: 加 variants + Qwen 推演的变式
    qwen_variants = result.get('variants', [])
    existing_variants = d.get('derived_variants', [])
    if isinstance(existing_variants, list):
        d['derived_variants'] = existing_variants + [
            {**v, "_qwen_reviewed": True, "_at": time.strftime("%Y-%m-%dT%H:%M:%S")}
            for v in qwen_variants
        ]
    else:
        d['derived_variants'] = [
            {**v, "_qwen_reviewed": True, "_at": time.strftime("%Y-%m-%dT%H:%M:%S")}
            for v in qwen_variants
        ]

    if result.get('key_concepts'):
        existing_concepts = d.get('concepts', [])
        d['concepts'] = list(set(existing_concepts + result['key_concepts']))

    if result.get('common_mistakes'):
        existing_mistakes = d.get('common_mistakes', [])
        d['common_mistakes'] = list(set(existing_mistakes + result['common_mistakes']))

    d['_qwen_review'] = {
        "model": "qwen-plus",
        "reviewed_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "variants_added": len(qwen_variants),
    }
    d['maturity'] = 'REVIEWED'

    mother_path.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding='utf-8')
    return (True, result)


def upgrade_methodology(method_path: Path, api_key: str) -> tuple[bool, dict]:
    """升级 5 张方法论: 加 Qwen 推演的例题/变式"""
    try:
        d = json.loads(method_path.read_text(encoding='utf-8'))
    except Exception as e:
        return (False, {"error": f"read: {e}"})

    # 方法论 back 是详细讲解, 抽一段作为例题推演
    # 用 front 中提到的"例题"作为题面
    front = d.get('front', '')
    # 提取例题题干
    import re
    m = re.search(r'【?例题】?(.+?)(?:[。.]\s*[证明求]|\Z)', front, re.DOTALL)
    if m:
        stem = m.group(1).strip()[:800]
    else:
        stem = front[:800]

    q = {"q_no": 0, "stem": stem, "options": []}
    result = review_one_question(q, "数学立体几何", api_key, timeout=45)
    if result.get('_review_failed'):
        return (False, result)

    # 升级: 加 variants (变式题) + 升级 knowledge_points
    if result.get('variants'):
        d['qwen_variants'] = result['variants']
    if result.get('key_concepts'):
        existing_kp = d.get('knowledge_points', [])
        d['knowledge_points'] = list(set(existing_kp + result['key_concepts']))
    if result.get('common_mistakes'):
        existing_mistakes = d.get('common_mistakes', [])
        d['common_mistakes'] = list(set(existing_mistakes + result['common_mistakes']))

    d['_qwen_review'] = {
        "model": "qwen-plus",
        "reviewed_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "variants_added": len(result.get('variants', [])),
    }
    method_path.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding='utf-8')
    return (True, result)


def main():
    api_key = get_api_key()
    if not api_key:
        print("ERROR: API key missing")
        sys.exit(1)
    print(f"API key: {api_key[:8]}...{api_key[-4:]} (Qwen3.5-Plus)")

    report = {
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "model": "qwen-plus",
        "pt030_liti_kcards": {"total": 0, "ok": 0, "fail": 0, "results": []},
        "mother_cards_draft": {"total": 0, "ok": 0, "fail": 0, "results": []},
        "methodologies": {"total": 0, "ok": 0, "fail": 0, "results": []},
    }
    t_start = time.time()

    # === 1. PT030 立体几何 K 卡 ===
    print("\n=== 1. PT030 立体几何 K 卡 (8 张) ===", flush=True)
    liti_kcards = []
    for f in PT030_DIR.rglob('*.json'):
        if 'llm_gen' in str(f):
            continue
        try:
            d = json.loads(f.read_text(encoding='utf-8'))
            if d.get('module') == '立体几何':
                liti_kcards.append(f)
        except Exception:
            pass
    print(f"找到 {len(liti_kcards)} 张立体几何 K 卡", flush=True)
    report['pt030_liti_kcards']['total'] = len(liti_kcards)
    for f in liti_kcards:
        print(f"  [PT030] {f.parent.name}/{f.name}", flush=True)
        t0 = time.time()
        ok, result = upgrade_pt030_kcard(f, api_key)
        elapsed = time.time() - t0
        if ok:
            report['pt030_liti_kcards']['ok'] += 1
            report['pt030_liti_kcards']['results'].append({
                "file": f.name, "elapsed": elapsed, "verdict": result.get('verdict'),
                "variants": len(result.get('variants', []))
            })
            print(f"    ✅ {elapsed:.0f}s verdict={result.get('verdict')} variants={len(result.get('variants', []))}", flush=True)
        else:
            report['pt030_liti_kcards']['fail'] += 1
            print(f"    ❌ {elapsed:.0f}s {result.get('_error', '?')[:80]}", flush=True)

    # === 2. 1 窗口 4 板块 DRAFT 母题 K10-K15 (去 DRAFT 限制, 所有 24 张都加 Qwen 变式) ===
    print("\n=== 2. 1 窗口 4 板块母题 K10-K15 (不限 DRAFT, 全 24 张加 Qwen 变式) ===", flush=True)
    draft_dirs = ['二面角', '线面垂直', '线面角', '面面平行证明']
    draft_mothers = []
    for d_name in draft_dirs:
        for f in (KCARDS_DIR / d_name).glob('K[0-9][0-9].json'):
            try:
                if 10 <= int(f.stem[1:]) <= 15:
                    draft_mothers.append(f)
            except Exception:
                pass
    print(f"找到 {len(draft_mothers)} 张 K10-K15 母题", flush=True)
    report['mother_cards_draft']['total'] = len(draft_mothers)
    for f in draft_mothers:
        print(f"  [Mother] {f.parent.name}/{f.name}", flush=True)
        t0 = time.time()
        ok, result = upgrade_mother_card(f, api_key)
        elapsed = time.time() - t0
        if ok:
            report['mother_cards_draft']['ok'] += 1
            report['mother_cards_draft']['results'].append({
                "file": f.name, "elapsed": elapsed,
                "variants_added": len(result.get('variants', []))
            })
            print(f"    ✅ {elapsed:.0f}s variants+={len(result.get('variants', []))}", flush=True)
        else:
            report['mother_cards_draft']['fail'] += 1
            print(f"    ❌ {elapsed:.0f}s {result.get('_error', '?')[:80]}", flush=True)

    # === 3. 5 张方法论 ===
    print("\n=== 3. 立体几何 5 张方法论 ===", flush=True)
    method_files = sorted(METHODS_DIR.glob('M_立体_*.json'))
    print(f"找到 {len(method_files)} 张方法论", flush=True)
    report['methodologies']['total'] = len(method_files)
    for f in method_files:
        print(f"  [Method] {f.name}", flush=True)
        t0 = time.time()
        ok, result = upgrade_methodology(f, api_key)
        elapsed = time.time() - t0
        if ok:
            report['methodologies']['ok'] += 1
            report['methodologies']['results'].append({
                "file": f.name, "elapsed": elapsed,
                "variants_added": len(result.get('variants', []))
            })
            print(f"    ✅ {elapsed:.0f}s variants+={len(result.get('variants', []))}", flush=True)
        else:
            report['methodologies']['fail'] += 1
            print(f"    ❌ {elapsed:.0f}s {result.get('_error', '?')[:80]}", flush=True)

    report['finished_at'] = time.strftime("%Y-%m-%dT%H:%M:%S")
    report['total_elapsed'] = time.time() - t_start

    # 写报告
    LITI_QWEN_OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"\n报告写入: {LITI_QWEN_OUTPUT}")
    print(f"\n总耗时 {report['total_elapsed']:.0f}s = {report['total_elapsed']/60:.1f} min")
    print(f"PT030 K 卡: {report['pt030_liti_kcards']['ok']}/{report['pt030_liti_kcards']['total']}")
    print(f"母题升级: {report['mother_cards_draft']['ok']}/{report['mother_cards_draft']['total']}")
    print(f"方法论: {report['methodologies']['ok']}/{report['methodologies']['total']}")


if __name__ == "__main__":
    main()
