"""
Qwen3.5-Plus 4 板块批量升级 v1.0 (函数板块 M2 + 概率/解三角)
===========================================================
目标:
- ② 10 张方法论 (解析几何 5 + 导数 5) Qwen 推演 +2 变式/张
- ③ 50 张 PT-030 K 卡 (解析几何 29 + 导数 21) Qwen 升级
- ④ 10 张 K50-K64 母题 (概率 5 + 解三角 5) Qwen 推演 +2 变式/张

输出:
- 升级后的 K 卡 (原地修改)
- 报告: methods/解析几何/qwen_review_function.json
- 报告: methods/导数/qwen_review_function.json
"""

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, r'D:\Z_学习平台\SPDT-004_EduContent\tools')
from review_qwen import review_one_question, get_api_key

KCARDS = Path(r'D:\Z_学习平台\knowledge-cards-prod\projects\math\cards')
PT030 = KCARDS / '本地上海' / 'PT030_2026-09-13'
METHODS_ROOT = KCARDS.parent / 'methods'
PANELS = {
    '解析几何': {'method_dir': METHODS_ROOT / '解析几何', 'mother_dir': KCARDS / '解析几何', 'mother_krange': range(20, 25), 'pt030_module': '解析几何'},
    '导数': {'method_dir': METHODS_ROOT / '导数', 'mother_dir': KCARDS / '导数', 'mother_krange': range(30, 35), 'pt030_module': '导数'},
    '概率统计': {'method_dir': METHODS_ROOT / '概率统计', 'mother_dir': KCARDS / '概率统计', 'mother_krange': range(50, 55), 'pt030_module': '概率统计'},
    '解三角形': {'method_dir': METHODS_ROOT / '解三角形', 'mother_dir': KCARDS / '解三角形', 'mother_krange': range(60, 65), 'pt030_module': '解三角形'},
}


def upgrade_pt030_kcard(kcard_path: Path, subject: str, api_key: str) -> tuple[bool, dict]:
    """PT-030 K 卡升级 (Qwen 推演)"""
    try:
        d = json.loads(kcard_path.read_text(encoding='utf-8'))
    except Exception as e:
        return (False, {"error": f"read: {e}"})

    if d.get('provenance', {}).get('qwen_review'):
        return (True, {"_skip": "already qwen reviewed"})

    q = {
        "q_no": d.get('id', '').split('_q')[-1] if 'q' in d.get('id', '') else 0,
        "stem": d.get('front', ''),
        "options": d.get('options', []),
    }
    if not q["stem"]:
        return (False, {"error": "no stem"})

    result = review_one_question(q, f"数学{subject}", api_key, timeout=45)
    if result.get('_review_failed'):
        return (False, result)

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
        "extracted_by": "batch_review_qwen_4panels.py v1.0",
    }
    kcard_path.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding='utf-8')
    return (True, result)


def upgrade_mother_card(mother_path: Path, subject: str, api_key: str) -> tuple[bool, dict]:
    """母题升级 (加 Qwen 变式)"""
    try:
        d = json.loads(mother_path.read_text(encoding='utf-8'))
    except Exception as e:
        return (False, {"error": f"read: {e}"})

    if d.get('_qwen_review'):
        return (True, {"_skip": "already qwen reviewed", "variants_added": d['_qwen_review'].get('variants_added', 0)})

    stem_source = d.get('back', '') or d.get('front', '')
    if not stem_source:
        return (False, {"error": "no back/stem"})
    if len(stem_source) > 1500:
        stem_source = stem_source[:1500] + "..."

    q = {"q_no": 0, "stem": stem_source, "options": []}
    result = review_one_question(q, f"数学{subject}", api_key, timeout=45)
    if result.get('_review_failed'):
        return (False, result)

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
        d['concepts'] = list(set(d.get('concepts', []) + result['key_concepts']))
    if result.get('common_mistakes'):
        d['common_mistakes'] = list(set(d.get('common_mistakes', []) + result['common_mistakes']))
    d['_qwen_review'] = {
        "model": "qwen-plus", "reviewed_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "variants_added": len(qwen_variants),
    }
    d['maturity'] = 'REVIEWED'
    mother_path.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding='utf-8')
    return (True, result)


def upgrade_methodology(method_path: Path, subject: str, api_key: str) -> tuple[bool, dict]:
    """方法论升级 (加 Qwen 变式)"""
    try:
        d = json.loads(method_path.read_text(encoding='utf-8'))
    except Exception as e:
        return (False, {"error": f"read: {e}"})

    if d.get('_qwen_review'):
        return (True, {"_skip": "already qwen reviewed", "variants_added": len(d.get('qwen_variants', []))})

    front = d.get('front', '')
    import re
    m = re.search(r'【?例题】?(.+?)(?:[。.]\s*[证明求]|\Z)', front, re.DOTALL)
    stem = m.group(1).strip()[:800] if m else front[:800]

    q = {"q_no": 0, "stem": stem, "options": []}
    result = review_one_question(q, f"数学{subject}", api_key, timeout=45)
    if result.get('_review_failed'):
        return (False, result)

    if result.get('variants'):
        d['qwen_variants'] = result['variants']
    if result.get('key_concepts'):
        d['knowledge_points'] = list(set(d.get('knowledge_points', []) + result['key_concepts']))
    if result.get('common_mistakes'):
        d['common_mistakes'] = list(set(d.get('common_mistakes', []) + result['common_mistakes']))
    d['_qwen_review'] = {
        "model": "qwen-plus", "reviewed_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "variants_added": len(result.get('variants', [])),
    }
    method_path.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding='utf-8')
    return (True, result)


def main():
    api_key = get_api_key()
    if not api_key:
        print("ERROR: API key missing"); sys.exit(1)
    print(f"API key: {api_key[:8]}...{api_key[-4:]} (Qwen3.5-Plus)")

    all_report = {
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "model": "qwen-plus",
        "panels": {},
    }
    t_start = time.time()

    for panel, cfg in PANELS.items():
        print(f"\n{'='*60}\n【{panel}】开始\n{'='*60}", flush=True)
        panel_report = {"methods": {"total": 0, "ok": 0, "fail": 0}, "mothers": {"total": 0, "ok": 0, "fail": 0}, "pt030_kcards": {"total": 0, "ok": 0, "fail": 0}}

        # ② 方法论
        method_files = sorted(cfg['method_dir'].glob('M_*.json')) if cfg['method_dir'].exists() else []
        panel_report["methods"]["total"] = len(method_files)
        print(f"[{panel}] 方法论: {len(method_files)} 张", flush=True)
        for f in method_files:
            t0 = time.time()
            ok, result = upgrade_methodology(f, panel, api_key)
            elapsed = time.time() - t0
            if ok:
                panel_report["methods"]["ok"] += 1
                print(f"  ✅ {f.name} {elapsed:.0f}s", flush=True)
            else:
                panel_report["methods"]["fail"] += 1
                print(f"  ❌ {f.name} {elapsed:.0f}s {result.get('_error', '?')[:60]}", flush=True)

        # ④ 母题
        mother_files = []
        if cfg['mother_dir'].exists():
            for f in cfg['mother_dir'].glob('K[0-9][0-9].json'):
                try:
                    if int(f.stem[1:]) in cfg['mother_krange']:
                        mother_files.append(f)
                except Exception:
                    pass
        panel_report["mothers"]["total"] = len(mother_files)
        print(f"[{panel}] 母题 K{cfg['mother_krange'].start}-K{cfg['mother_krange'].stop-1}: {len(mother_files)} 张", flush=True)
        for f in mother_files:
            t0 = time.time()
            ok, result = upgrade_mother_card(f, panel, api_key)
            elapsed = time.time() - t0
            if ok:
                panel_report["mothers"]["ok"] += 1
                print(f"  ✅ {f.name} {elapsed:.0f}s", flush=True)
            else:
                panel_report["mothers"]["fail"] += 1
                print(f"  ❌ {f.name} {elapsed:.0f}s {result.get('_error', '?')[:60]}", flush=True)

        # ③ PT-030 K 卡
        pt030_files = []
        for f in PT030.rglob('*.json'):
            if 'llm_gen' in str(f):
                continue
            try:
                d = json.loads(f.read_text(encoding='utf-8'))
                if d.get('module') == cfg['pt030_module']:
                    pt030_files.append(f)
            except Exception:
                pass
        panel_report["pt030_kcards"]["total"] = len(pt030_files)
        print(f"[{panel}] PT-030 K 卡: {len(pt030_files)} 张", flush=True)
        for f in pt030_files:
            t0 = time.time()
            ok, result = upgrade_pt030_kcard(f, panel, api_key)
            elapsed = time.time() - t0
            if ok:
                panel_report["pt030_kcards"]["ok"] += 1
                print(f"  ✅ {f.parent.name}/{f.name} {elapsed:.0f}s", flush=True)
            else:
                panel_report["pt030_kcards"]["fail"] += 1
                print(f"  ❌ {f.parent.name}/{f.name} {elapsed:.0f}s {result.get('_error', '?')[:60]}", flush=True)

        all_report["panels"][panel] = panel_report

    all_report["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    all_report["total_elapsed"] = time.time() - t_start

    # 写总报告
    report_path = METHODS_ROOT / '解析几何' / 'qwen_review_function.json'
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(all_report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"\n报告: {report_path}")
    print(f"总耗时 {all_report['total_elapsed']:.0f}s = {all_report['total_elapsed']/60:.1f} min")
    for p, r in all_report['panels'].items():
        print(f"  [{p}] 方法论 {r['methods']['ok']}/{r['methods']['total']} | 母题 {r['mothers']['ok']}/{r['mothers']['total']} | PT030 {r['pt030_kcards']['ok']}/{r['pt030_kcards']['total']}")


if __name__ == "__main__":
    main()
