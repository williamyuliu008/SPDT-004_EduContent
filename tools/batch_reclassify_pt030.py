"""
PT-030 K 卡 module 字段重分类 v1.0 (Qwen 重新分类)
==================================================
启发式分类误差大 (60% 分到"解答题/通用/代数"), 用 Qwen 给每题重打 module 标签.

目标字段: module ∈ {集合与函数, 代数, 数列, 解析几何, 导数, 概率统计, 立体几何, 解三角形, 解答题}
- 5 板块 = 解析几何/导数/数列/概率统计/解三角形
- 解答题 = 跨板块综合题
- 集合与函数/代数 = 填空题基础
"""

import json
import sys
import time
from pathlib import Path
import httpx

sys.path.insert(0, r'D:\Z_学习平台\SPDT-004_EduContent\tools')
from review_qwen import get_api_key, QWEN_ENDPOINT

PT030 = Path(r'D:\Z_学习平台\knowledge-cards-prod\projects\math\cards\本地上海\PT030_2026-09-13')
OUTPUT_REPORT = PT030 / 'reclassify_report.json'

RECLASSIFY_PROMPT = """你是上海高考数学题目分类专家。
请根据题目内容, 给这道题分到 1 个最合适的板块:
- 集合与函数 (集合/函数/不等式/对数)
- 代数 (复数/向量/二项式定理)
- 数列 (等差/等比/通项/求和)
- 解析几何 (圆锥曲线/直线与圆/参数方程)
- 导数 (单调性/极值/不等式证明/切线)
- 概率统计 (古典概型/分布列/期望/独立性检验)
- 立体几何 (线面关系/二面角/体积/折叠)
- 解三角形 (正弦定理/余弦定理/面积/外接圆)
- 解答题 (跨板块综合)

【题目】
{stem}

【选项】
{options}

只输出 1 行 JSON: {{"module": "板块名", "reason": "一句话理由"}}
"""


def reclassify_one(kcard_path: Path, api_key: str, timeout: float = 30.0) -> tuple[bool, dict]:
    """用 Qwen 重打 module 标签"""
    try:
        d = json.loads(kcard_path.read_text(encoding='utf-8'))
    except Exception as e:
        return (False, {"error": f"read: {e}"})

    # 跳过已有 _qwen_reclassify
    if d.get('provenance', {}).get('qwen_reclassify'):
        return (True, {"_skip": "already reclassified", "module": d.get('module')})

    stem = d.get('front', '')[:500]
    options = d.get('options', [])
    opt_str = ' | '.join(f"{o.get('label', '')}={o.get('text', '')}" for o in options[:4])
    prompt = RECLASSIFY_PROMPT.format(stem=stem, options=opt_str)

    payload = {
        "model": "qwen-plus",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
        "max_tokens": 200,
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    try:
        with httpx.Client(timeout=timeout) as client:
            r = client.post(QWEN_ENDPOINT, json=payload, headers=headers)
            r.raise_for_status()
            data = r.json()
        content = data["choices"][0]["message"]["content"]
    except httpx.TimeoutException:
        return (False, {"_error": "timeout"})
    except Exception as e:
        return (False, {"_error": str(e)[:200]})

    import re
    m = re.search(r"\{.*\}", content, re.DOTALL)
    if not m:
        return (False, {"_error": f"no JSON: {content[:80]}"})
    try:
        result = json.loads(m.group(0))
    except json.JSONDecodeError as e:
        return (False, {"_error": f"decode: {e}"})

    new_module = result.get('module', d.get('module', '通用'))
    old_module = d.get('module', '?')
    d['module'] = new_module
    d['topic'] = new_module
    d['provenance'] = d.get('provenance', {})
    d['provenance']['qwen_reclassify'] = {
        "old_module": old_module,
        "new_module": new_module,
        "reason": result.get('reason', ''),
        "reclassified_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }
    kcard_path.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding='utf-8')
    return (True, result)


def main():
    api_key = get_api_key()
    if not api_key:
        print("ERROR: API key missing"); sys.exit(1)

    # 列所有 K 卡 (排除 llm_gen)
    files = [f for f in PT030.rglob('*.json') if 'llm_gen' not in str(f)]
    print(f"[reclassify] 总 K 卡: {len(files)}", flush=True)

    report = {
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "total": len(files),
        "ok": 0, "fail": 0, "skip": 0,
        "old_to_new": {},  # {old: {new: count}}
    }
    t_start = time.time()
    for i, f in enumerate(files, 1):
        t0 = time.time()
        ok, result = reclassify_one(f, api_key)
        elapsed = time.time() - t0
        if ok and result.get('_skip'):
            report['skip'] += 1
        elif ok:
            report['ok'] += 1
            old = result.get('_skip', '?')  # skip 表示已有
            if 'new_module' not in result:
                # 这是新分类, 但我们之前没存 old_module, 跳过
                pass
        else:
            report['fail'] += 1
        if i % 20 == 0 or i == len(files):
            avg = (time.time() - t_start) / i
            eta = (len(files) - i) * avg
            print(f"  [{i}/{len(files)}] {elapsed:.0f}s avg={avg:.0f}s ETA={eta:.0f}s ok={report['ok']} skip={report['skip']} fail={report['fail']}", flush=True)

    report['finished_at'] = time.strftime("%Y-%m-%dT%H:%M:%S")
    report['total_elapsed'] = time.time() - t_start

    # 写报告
    OUTPUT_REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"\n报告: {OUTPUT_REPORT}")
    print(f"总耗时 {report['total_elapsed']:.0f}s = {report['total_elapsed']/60:.1f} min")
    print(f"OK {report['ok']} | Skip {report['skip']} | Fail {report['fail']}")


if __name__ == "__main__":
    main()
