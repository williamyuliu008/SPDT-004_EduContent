"""
PT-030 批量 llm-review v3 (雪薇端, httpx 直调 GLM)
===================================================
绕开 zhipuai SDK hang, 直接用 review_httpx.review_one_question (httpx 30s timeout).

用法:
    python tools/batch_review_v3.py "D:\\Z_学习平台\\...\\split" --filter 解析版
"""

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from review_httpx import review_one_question, get_api_key


def review_split_file(split_path: Path, subject: str, api_key: str, timeout: float = 30.0) -> tuple[bool, int, int]:
    """跑单套 review, 串行推演每题"""
    reviewed_path = split_path.parent / f"{split_path.stem.replace('_split_v11', '')}_split_v11_reviewed.json"
    if reviewed_path.exists():
        return (True, -1, -1)

    try:
        d = json.loads(split_path.read_text(encoding="utf-8"))
        questions = d.get("questions", [])
    except Exception as e:
        print(f"  ERR read: {e}", flush=True)
        return (False, 0, 0)

    if not questions:
        return (True, 0, 0)

    reviewed = []
    n = len(questions)
    t0 = time.time()
    for i, q in enumerate(questions, 1):
        # stem 截断, 防止某些长题 prompt 过大
        q_copy = dict(q)
        if len(q_copy.get("stem", "")) > 500:
            q_copy["stem"] = q_copy["stem"][:500] + "..."
        result = review_one_question(q_copy, subject, api_key, timeout=timeout)
        merged = {**q, **(result or {})}
        reviewed.append(merged)
        if i % 3 == 0 or i == n:
            elapsed = time.time() - t0
            rate = elapsed / i
            eta = (n - i) * rate
            print(f"    [{i}/{n}] {elapsed:.0f}s (ETA {eta:.0f}s)", flush=True)

    output = {
        "subject": subject,
        "input_file": str(split_path),
        "total": n,
        "reviewed": sum(1 for r in reviewed if not r.get("_review_failed")),
        "questions": reviewed,
        "_v1_caveat": "v1.0 glm-4-flash 推演 (雪薇端 v3: httpx 30s timeout, 绕开 zhipuai SDK hang).",
        "_created": "2026-09-13 by 雪薇端 batch_review_v3 (httpx)",
    }
    reviewed_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    return (True, output["reviewed"], n)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("dir")
    parser.add_argument("--filter", choices=["解析版", "原卷版", "all"], default="all")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--skip-existing", action="store_true", default=True)
    args = parser.parse_args()

    split_dir = Path(args.dir)
    log_path = split_dir / "batch_review_v3.log"
    api_key = get_api_key()
    if not api_key:
        print("ERROR: API key missing")
        sys.exit(1)

    files = list(split_dir.glob("*_split_v11.json"))
    if args.filter == "解析版":
        files = [f for f in files if "解析版" in f.name]
    elif args.filter == "原卷版":
        files = [f for f in files if "原卷版" in f.name]
    files.sort(key=lambda p: p.name)
    if args.limit > 0:
        files = files[:args.limit]

    print(f"[v3] 目录: {split_dir}", flush=True)
    print(f"[v3] 过滤: {args.filter}, 套数: {len(files)}", flush=True)
    print(f"[v3] log: {log_path}", flush=True)

    with open(log_path, "a", encoding="utf-8") as log:
        log.write(f"\n==== {time.strftime('%Y-%m-%d %H:%M:%S')} v3 httpx 批量, 共 {len(files)} 套, timeout={args.timeout}s ====\n")
        log.flush()
        ok, skip, fail, total_rev, total_n = 0, 0, 0, 0, 0
        t_start = time.time()
        for i, f in enumerate(files, 1):
            print(f"\n[{i}/{len(files)}] {f.name}", flush=True)
            log.write(f"\n[{i}/{len(files)}] {f.name}\n")
            log.flush()
            try:
                success, rev, n = review_split_file(f, "数学", api_key, args.timeout)
                if success and rev == -1:
                    skip += 1
                    log.write(f"  SKIP (已 review)\n")
                elif success and n == 0:
                    skip += 1
                    log.write(f"  SKIP (0 题)\n")
                elif success:
                    ok += 1
                    total_rev += rev
                    total_n += n
                    pct = rev / max(n, 1) * 100
                    log.write(f"  OK {rev}/{n} ({pct:.0f}%)\n")
                    print(f"  ✅ {rev}/{n} ({pct:.0f}%)", flush=True)
                else:
                    fail += 1
                    log.write(f"  FAIL\n")
            except Exception as e:
                fail += 1
                log.write(f"  ERR {e}\n")
            log.flush()
        elapsed = time.time() - t_start
        log.write(f"\n==== v3 完成: ok={ok} skip={skip} fail={fail} 推演={total_rev}/{total_n} ({total_rev/max(total_n,1)*100:.1f}%) 耗时={elapsed:.0f}s ====\n")
        log.flush()
        print(f"\n[v3] ✅ ok={ok} skip={skip} fail={fail} 推演={total_rev}/{total_n} 耗时={elapsed:.0f}s", flush=True)


if __name__ == "__main__":
    main()
