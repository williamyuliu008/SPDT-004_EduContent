"""
PT-030 批量 llm-review 雪薇端 helper v1.0
========================================
对指定目录下所有 split_v11.json 跑 glm4_flash_review.py,
跳过已有 reviewed.json, 写日志到 batch_review.log

用法:
    python tools/batch_llm_review.py "D:\\Z_学习平台\\SPDT-004_EduContent\\PT-030\\zhenti\\数学\\split" --filter 解析版
    python tools/batch_llm_review.py "..." --filter 原卷版
    python tools/batch_llm_review.py "..." --all
    python tools/batch_llm_review.py "..." --force  # 强制重跑已有 reviewed
"""

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path


def run_one(split_path: Path, log_file) -> tuple[bool, int, int]:
    """跑单套 review, 返回 (成功, 推演数, 总数)"""
    reviewed_path = split_path.parent / f"{split_path.stem.replace('_split_v11', '')}_split_v11_reviewed.json"
    if reviewed_path.exists():
        return (True, -1, -1)  # 跳过

    # 读 split 拿题数
    try:
        d = json.loads(split_path.read_text(encoding="utf-8"))
        n = d.get("total_questions", 0)
    except Exception as e:
        log_file.write(f"  ERR read {split_path.name}: {e}\n")
        return (False, 0, 0)
    if n == 0:
        return (True, 0, 0)  # 0 题跳过

    # 调 glm4_flash_review.py
    t0 = time.time()
    try:
        r = subprocess.run(
            [sys.executable, str(Path(__file__).parent / "glm4_flash_review.py"),
             str(split_path), "--subject", "数学"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=240,  # 4 min/套 上限 (22 题 × 5-10s)
        )
        elapsed = time.time() - t0
        if r.returncode != 0:
            log_file.write(f"  FAIL {split_path.name}: {r.stderr[:200]}\n")
            return (False, 0, n)
    except subprocess.TimeoutExpired:
        log_file.write(f"  TIMEOUT {split_path.name} (180s)\n")
        return (False, 0, n)

    # 读 reviewed
    if not reviewed_path.exists():
        log_file.write(f"  NO_OUTPUT {split_path.name}\n")
        return (False, 0, n)
    try:
        rd = json.loads(reviewed_path.read_text(encoding="utf-8"))
        rev = rd.get("reviewed", 0)
        total = rd.get("total", 0)
        log_file.write(f"  OK  {split_path.name}: {rev}/{total} ({rev/max(total,1)*100:.0f}%) {elapsed:.1f}s\n")
        log_file.flush()
        return (True, rev, total)
    except Exception as e:
        log_file.write(f"  ERR read reviewed {split_path.name}: {e}\n")
        return (False, 0, n)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("dir", help="split_v11.json 所在目录")
    parser.add_argument("--filter", choices=["解析版", "原卷版", "all"], default="all")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--limit", type=int, default=0, help="最多跑 N 套 (0=无限)")
    args = parser.parse_args()

    split_dir = Path(args.dir)
    log_path = split_dir / "batch_review.log"

    # 列文件
    files = list(split_dir.glob("*_split_v11.json"))
    # 过滤
    if args.filter == "解析版":
        files = [f for f in files if "解析版" in f.name]
    elif args.filter == "原卷版":
        files = [f for f in files if "原卷版" in f.name]
    # 排序
    files.sort(key=lambda p: p.name)
    if args.limit > 0:
        files = files[:args.limit]

    # 跳过已有 reviewed (除非 --force)
    if not args.force:
        todo = []
        for f in files:
            r = f.parent / f"{f.stem.replace('_split_v11', '')}_split_v11_reviewed.json"
            if not r.exists():
                todo.append(f)
        files = todo

    print(f"[batch_review] 目录: {split_dir}")
    print(f"[batch_review] 过滤: {args.filter}")
    print(f"[batch_review] 待跑: {len(files)} 套")
    print(f"[batch_review] 日志: {log_path}")

    with open(log_path, "a", encoding="utf-8") as log:
        log.write(f"\n==== {time.strftime('%Y-%m-%d %H:%M:%S')} 批量 review 开始, 共 {len(files)} 套 ====\n")
        log.flush()
        ok, skip, fail, total_rev, total_n = 0, 0, 0, 0, 0
        t0 = time.time()
        for i, f in enumerate(files, 1):
            print(f"\n[{i}/{len(files)}] {f.name}", flush=True)
            log.write(f"\n[{i}/{len(files)}] {f.name}\n")
            log.flush()
            success, rev, n = run_one(f, log)
            if success and rev == -1:
                skip += 1
            elif success:
                ok += 1
                total_rev += rev
                total_n += n
            else:
                fail += 1
        elapsed = time.time() - t0
        log.write(f"\n==== 批量 review 完成: ok={ok} skip={skip} fail={fail} 推演={total_rev}/{total_n} ({total_rev/max(total_n,1)*100:.1f}%) 耗时={elapsed:.1f}s ====\n")
        log.flush()
        print(f"\n[batch_review] ✅ 完成: ok={ok} skip={skip} fail={fail} 推演={total_rev}/{total_n} 耗时={elapsed:.1f}s")


if __name__ == "__main__":
    main()
