"""
ingest_cli.py — SPDT-004 1_ingest CLI 提交入口 v1.0
====================================================

手动创建 Envelope 并投递到 D:/4_data/ingest_queue/。
可立即触发处理（--process）或仅投递等 watcher 自动处理。

详见:
  ENVELOPE_SPEC.md §2.3 Layer 3 接口形式
  ENVELOPE_SPEC.md §4 上游身份矩阵

用法:
  # 创建一个新的 Envelope（交互式）
  python 1_ingest/ingest_cli.py new

  # 立即处理（不依赖 watcher）
  python 1_ingest/ingest_cli.py process <envelope_dir>

  # 列出所有未处理的 Envelope
  python 1_ingest/ingest_cli.py list

  # 看一个 Envelope 的状态
  python 1_ingest/ingest_cli.py status <envelope_dir>
"""
import argparse
import io
import json
import shutil
import sys
import uuid
from datetime import datetime
from pathlib import Path

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

INGEST_QUEUE_DIR = Path("D:/4_data/ingest_queue")
SCHEMA_PATH = Path(__file__).parent / "schemas" / "envelope.schema.json"


def log(msg, level="INFO"):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}][{level}] {msg}")


def cmd_new(args):
    """创建新 Envelope（交互式）"""
    INGEST_QUEUE_DIR.mkdir(parents=True, exist_ok=True)

    ingest_id = str(uuid.uuid4())
    print(f"生成 ingest_id: {ingest_id}")
    print()

    # 必填字段交互式输入
    print("=== Envelope 字段（* 必填）===")
    submitted_by = input("* submitted_by (willi/Mavis/autoclaw): ").strip() or "Mavis"
    source_type = input("* source_type (exam_syllabus/ancient_text/web/expert_notes/mixed): ").strip() or "exam_syllabus"
    priority = input("* priority (P0/P1/P2/P3): ").strip() or "P2"
    print()

    domain = input("  metadata.domain（如 高考历史）: ").strip() or "未指定"
    exam_type = input("  metadata.exam_type (gaokao/cafa/toefl/ielts/other): ").strip() or "gaokao"
    print()

    # 路径输入
    print("源文件路径（可多个，空行结束）:")
    source_paths = []
    while True:
        p = input(f"  path #{len(source_paths) + 1}: ").strip()
        if not p:
            break
        source_paths.append(p)
    print()

    if not source_paths:
        print("❌ 至少要 1 个 source_path")
        return 1

    # 生成 Envelope
    envelope = {
        "envelope_version": "1.0",
        "ingest_id": ingest_id,
        "submitted_at": datetime.now().isoformat(),
        "submitted_by": submitted_by,
        "source_type": source_type,
        "source_paths": source_paths,
        "priority": priority,
        "metadata": {
            "domain": domain,
            "exam_type": exam_type,
        },
    }

    # 落盘
    target_dir = INGEST_QUEUE_DIR / ingest_id
    target_dir.mkdir(parents=True, exist_ok=True)
    (target_dir / "envelope.json").write_text(
        json.dumps(envelope, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    # 复制源文件（如果是本地路径）
    sources_dir = target_dir / "sources"
    sources_dir.mkdir(exist_ok=True)
    copied = 0
    for src in source_paths:
        src_path = Path(src)
        if src_path.exists() and src_path.is_file():
            shutil.copy(src_path, sources_dir / src_path.name)
            copied += 1
            log(f"  复制源: {src_path.name}")
    if copied < len(source_paths):
        log(f"  ⚠️ {len(source_paths) - copied} 个源文件不在本地，需要手动复制到 {sources_dir}", "WARN")

    print()
    print(f"✅ Envelope 创建成功: {target_dir}")
    print(f"   ingest_id: {ingest_id}")
    print(f"   source_type: {source_type}, priority: {priority}")
    print()
    if args.process:
        print("立即处理...")
        return cmd_process(argparse.Namespace(envelope_dir=target_dir))
    else:
        print(f"等 watcher 自动处理（轮询 {INGEST_QUEUE_DIR}）")
        return 0


def cmd_process(args):
    """立即处理一个 Envelope"""
    envelope_dir = Path(args.envelope_dir)
    if not envelope_dir.exists():
        print(f"❌ 目录不存在: {envelope_dir}")
        return 1
    from processor import process_one_envelope_dir
    result = process_one_envelope_dir(envelope_dir)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status") == "completed" else 1


def cmd_list(args):
    """列出所有未处理的 Envelope"""
    if not INGEST_QUEUE_DIR.exists():
        print("队列目录不存在")
        return 0
    total = 0
    pending = 0
    for envelope_path in INGEST_QUEUE_DIR.rglob("envelope.json"):
        total += 1
        envelope_dir = envelope_path.parent
        output_ingested = envelope_dir / "output" / "ingested.json"
        is_done = output_ingested.exists()
        status = "✓ completed" if is_done else "⏳ pending"
        if not is_done:
            pending += 1
        print(f"  {status}  {envelope_dir}")
    print()
    print(f"总计: {total} 个 Envelope, {pending} 个待处理")
    return 0


def cmd_status(args):
    """看一个 Envelope 的状态"""
    envelope_dir = Path(args.envelope_dir)
    envelope_path = envelope_dir / "envelope.json"
    if not envelope_path.exists():
        print(f"❌ Envelope 不存在: {envelope_path}")
        return 1
    envelope = json.loads(envelope_path.read_text(encoding="utf-8"))
    print(json.dumps(envelope, ensure_ascii=False, indent=2))
    print()
    output_ingested = envelope_dir / "output" / "ingested.json"
    output_audit = envelope_dir / "output" / "audit_log.json"
    print(f"ingested.json: {'✓' if output_ingested.exists() else '✗ 待生成'}")
    print(f"audit_log.json: {'✓' if output_audit.exists() else '✗ 待生成'}")
    return 0


def main():
    parser = argparse.ArgumentParser(description="1_ingest CLI 提交入口")
    sub = parser.add_subparsers(dest="command", required=True)

    p_new = sub.add_parser("new", help="创建新 Envelope（交互式）")
    p_new.add_argument("--process", action="store_true", help="创建后立即处理")
    p_new.set_defaults(func=cmd_new)

    p_process = sub.add_parser("process", help="立即处理一个 Envelope")
    p_process.add_argument("envelope_dir", type=Path)
    p_process.set_defaults(func=cmd_process)

    p_list = sub.add_parser("list", help="列出所有 Envelope")
    p_list.set_defaults(func=cmd_list)

    p_status = sub.add_parser("status", help="看一个 Envelope 状态")
    p_status.add_argument("envelope_dir", type=Path)
    p_status.set_defaults(func=cmd_status)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main() or 0)
