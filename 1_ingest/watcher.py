"""
watcher.py — SPDT-004 1_ingest 自动轮询 v1.0
==============================================

每 N 秒轮询 D:/4_data/ingest_queue/，发现新 Envelope 目录自动调用 processor.py 处理。

详见:
  ENVELOPE_SPEC.md §2.4 Layer 4 触发方式
"""
import argparse
import io
import sys
import time
from datetime import datetime
from pathlib import Path

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

INGEST_QUEUE_DIR = Path("D:/4_data/ingest_queue")
PROCESSED_LOG = Path("D:/4_data/ingest_queue/.processed.log")


def log(msg, level="INFO"):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}][{level}] {msg}", flush=True)


def load_processed() -> set:
    """加载已处理过的 Envelope ID"""
    if not PROCESSED_LOG.exists():
        return set()
    return set(line.strip() for line in PROCESSED_LOG.read_text(encoding="utf-8").splitlines() if line.strip())


def mark_processed(ingest_id: str, status: str):
    """记录已处理"""
    PROCESSED_LOG.parent.mkdir(parents=True, exist_ok=True)
    with PROCESSED_LOG.open("a", encoding="utf-8") as f:
        f.write(f"{datetime.now().isoformat()}\t{ingest_id}\t{status}\n")


def is_processed(envelope_dir: Path) -> bool:
    """检查是否已处理：output/ingested.json 存在 = 已处理"""
    output_dir = envelope_dir / "output"
    return (output_dir / "ingested.json").exists()


def process_pending():
    """扫描 ingest_queue/，处理所有未处理的 Envelope"""
    if not INGEST_QUEUE_DIR.exists():
        INGEST_QUEUE_DIR.mkdir(parents=True, exist_ok=True)
        log(f"创建 ingest_queue 目录: {INGEST_QUEUE_DIR}")
        return 0

    processed_count = 0
    # 找所有 envelope.json
    for envelope_path in INGEST_QUEUE_DIR.rglob("envelope.json"):
        envelope_dir = envelope_path.parent
        if is_processed(envelope_dir):
            continue
        log(f"发现新 Envelope: {envelope_dir}")
        # 调用 processor
        try:
            from processor import process_one_envelope_dir
            result = process_one_envelope_dir(envelope_dir)
            status = result.get("status", "unknown")
            ingest_id = result.get("ingest_id", envelope_dir.name)
            mark_processed(ingest_id, status)
            processed_count += 1
            log(f"  -> {status}")
        except Exception as e:
            log(f"  [ERROR] {e}", "ERROR")
            mark_processed(envelope_dir.name, f"error: {e}")
    return processed_count


def main():
    parser = argparse.ArgumentParser(description="1_ingest 自动轮询 watcher")
    parser.add_argument("--interval", type=int, default=60, help="轮询间隔（秒）")
    parser.add_argument("--once", action="store_true", help="只跑一次（不循环）")
    parser.add_argument("--dry-run", action="store_true", help="只看不处理")
    args = parser.parse_args()

    log(f"=== 1_ingest watcher 启动 ===")
    log(f"  队列: {INGEST_QUEUE_DIR}")
    log(f"  间隔: {args.interval}s")
    log(f"  模式: {'once' if args.once else 'loop'} / {'dry-run' if args.dry_run else 'real'}")

    if args.once:
        count = process_pending() if not args.dry_run else 0
        log(f"=== 完成: 处理 {count} 个 ===")
        return 0

    # 循环模式
    cycle = 0
    while True:
        cycle += 1
        log(f"--- 第 {cycle} 轮 ---")
        try:
            count = process_pending()
            if count > 0:
                log(f"  本轮处理 {count} 个")
        except KeyboardInterrupt:
            log("  用户中断，退出")
            return 0
        except Exception as e:
            log(f"  [ERROR] {e}", "ERROR")
        time.sleep(args.interval)


if __name__ == "__main__":
    sys.exit(main() or 0)
