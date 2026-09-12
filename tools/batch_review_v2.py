"""
PT-030 批量 llm-review v2 (雪薇端 helper)
==========================================
直接 import glm4_flash_review.call_glm4_flash, 不走 subprocess,
用 threading 控制单题 timeout=10s, 避免 GLM hang 死整个批量.

用法:
    python tools/batch_review_v2.py "D:\\Z_学习平台\\...\\split" --filter 解析版 --limit 10
"""

import argparse
import json
import sys
import time
from pathlib import Path
import concurrent.futures

sys.path.insert(0, str(Path(__file__).parent))

from glm4_flash_review import call_glm4_flash, get_api_key


def review_one_question(q: dict, subject: str, api_key: str) -> dict:
    """推演单题 (同步, GLM 自己 10s 内)"""
    try:
        return call_glm4_flash(q, subject, api_key)
    except Exception as e:
        return {"_review_failed": True, "_error": str(e)[:100]}


def review_split_file(split_path: Path, subject: str, api_key: str) -> tuple[bool, int, int]:
    """跑单套 review, 串行推演每题, 单题 30s timeout"""
    reviewed_path = split_path.parent / f"{split_path.stem.replace('_split_v11', '')}_split_v11_reviewed.json"
    if reviewed_path.exists():
        return (True, -1, -1)  # 跳过

    try:
        d = json.loads(split_path.read_text(encoding="utf-8"))
        questions = d.get("questions", [])
    except Exception as e:
        return (False, 0, 0)

    if not questions:
        return (True, 0, 0)  # 0 题跳过

    reviewed = []
    n = len(questions)
    t0 = time.time()
    for i, q in enumerate(questions, 1):
        # 单题用 future + timeout 30s
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
            fut = ex.submit(review_one_question, q, subject, api_key)
            try:
                result = fut.result(timeout=30)
            except concurrent.futures.TimeoutError:
                result = {"_review_failed": True, "_error": "30s timeout"}
            except Exception as e:
                result = {"_review_failed": True, "_error": str(e)[:100]}
        merged = {**q, **(result or {})}
        reviewed.append(merged)
        if i % 5 == 0 or i == n:
            elapsed = time.time() - t0
            print(f"    [{i}/{n}] 耗时 {elapsed:.1f}s", flush=True)

    # 写 reviewed.json
    output = {
        "subject": subject,
        "input_file": str(split_path),
        "total": n,
        "reviewed": sum(1 for r in reviewed if not r.get("_review_failed")),
        "questions": reviewed,
        "_v1_caveat": "v1.0 glm-4-flash 推演 (雪薇端 v2: threading timeout=30s/题).",
        "_created": "2026-09-12 by 雪薇端 batch_review_v2"
    }
    reviewed_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    return (True, output["reviewed"], n)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("dir", help="split_v11.json 所在目录")
    parser.add_argument("--filter", choices=["解析版", "原卷版", "all"], default="all")
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()

    split_dir = Path(args.dir)
    log_path = split_dir / "batch_review_v2.log"
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

    print(f"[batch_review_v2] 目录: {split_dir}")
    print(f"[batch_review_v2] 过滤: {args.filter}")
    print(f"[batch_review_v2] 待跑: {len(files)} 套")
    print(f"[batch_review_v2] 日志: {log_path}")

    with open(log_path, "a", encoding="utf-8") as log:
        log.write(f"\n==== {time.strftime('%Y-%m-%d %H:%M:%S')} v2 批量开始, 共 {len(files)} 套 ====\n")
        log.flush()
        ok, skip, fail, total_rev, total_n = 0, 0, 0, 0, 0
        t0 = time.time()
        for i, f in enumerate(files, 1):
            print(f"\n[{i}/{len(files)}] {f.name}", flush=True)
            log.write(f"\n[{i}/{len(files)}] {f.name}\n")
            log.flush()
            try:
                success, rev, n = review_split_file(f, "数学", api_key)
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
                    log.write(f"  OK {rev}/{n} ({rev/max(n,1)*100:.0f}%)\n")
                else:
                    fail += 1
                    log.write(f"  FAIL\n")
            except Exception as e:
                fail += 1
                log.write(f"  ERR {e}\n")
            log.flush()
        elapsed = time.time() - t0
        log.write(f"\n==== v2 批量完成: ok={ok} skip={skip} fail={fail} 推演={total_rev}/{total_n} ({total_rev/max(total_n,1)*100:.1f}%) 耗时={elapsed:.1f}s ====\n")
        log.flush()
        print(f"\n[batch_review_v2] ✅ ok={ok} skip={skip} fail={fail} 推演={total_rev}/{total_n} 耗时={elapsed:.1f}s")


if __name__ == "__main__":
    main()
