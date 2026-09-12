"""
PT-030 toolkit 统一 CLI 入口
=============================
雪薇端调用:
    export PYTHONPATH=/path/to/SPDT-004_EduContent/tools:$PYTHONPATH
    cd /path/to/SPDT-004_EduContent

    # 查看所有子命令
    python -m pt030_toolkit.cli --help
    python -m pt030_toolkit.cli info

    # C1 解析
    python -m pt030_toolkit.cli parse-pdf <pdf_path> [--output <raw.json>]
    python -m pt030_toolkit.cli parse-docx <docx_path> [--output <raw.json>]
    python -m pt030_toolkit.cli parse-doc <doc_path> [--output <raw.json>]
    python -m pt030_toolkit.cli parse-batch <dir_path>  # 自动识别 PDF/docx/doc

    # C2 切分
    python -m pt030_toolkit.cli split <raw.json> [--output <split.json>]

    # C1+C2 一体化流水线
    python -m pt030_toolkit.cli pipeline <pdf_or_docx> [--output <split.json>]

    # C3 双 LLM 协作
    python -m pt030_toolkit.cli llm-gen <theme> [--count 5] [--output questions.json]
    python -m pt030_toolkit.cli llm-review <parent_problem.json> [--output reviewed.json]

设计原则:
- 不打包 (no pip install), 通过 PYTHONPATH 复用
- 内部 import 现有 tools/ 脚本 (不重写代码)
- 路径走 config.yaml + 环境变量 (跨机兼容)
"""

import argparse
import sys
import subprocess
from pathlib import Path

# 让 pt030_toolkit.cli 能 import tools/ 下的脚本
_TOOLS_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(_TOOLS_DIR))

from pt030_toolkit.config import (
    RAW_DIR, SPLIT_DIR, info as config_info, ensure_dirs
)
from pt030_toolkit import __version__


def _run_script(script_name: str, args: list, cwd: Path | None = None) -> int:
    """运行 tools/<script_name>.py 脚本, 转发 stdout/stderr/exitcode"""
    script_path = _TOOLS_DIR / script_name
    if not script_path.exists():
        print(f"ERROR: 脚本不存在 {script_path}", file=sys.stderr)
        return 1
    cmd = [sys.executable, str(script_path)] + args
    print(f"$ {' '.join(cmd)}", file=sys.stderr)
    return subprocess.call(cmd, cwd=cwd or _TOOLS_DIR.parent)


def cmd_parse_pdf(args) -> int:
    out = args.output or str(RAW_DIR / f"{Path(args.path).stem}_raw.json")
    return _run_script("parse_pdf_exam.py", [args.path, out])


def cmd_parse_docx(args) -> int:
    out = args.output or str(RAW_DIR / f"{Path(args.path).stem}_raw.json")
    return _run_script("parse_docx_exam.py", [args.path, out])


def cmd_parse_doc(args) -> int:
    out = args.output or str(RAW_DIR / f"{Path(args.path).stem}_raw.json")
    return _run_script("parse_doc_exam.py", [args.path, out])


def cmd_parse_batch(args) -> int:
    """批量解析目录下所有 PDF/docx/doc"""
    from pathlib import Path
    dir_path = Path(args.path)
    if not dir_path.exists():
        print(f"ERROR: 目录不存在 {dir_path}", file=sys.stderr)
        return 1
    ensure_dirs()
    # 找所有支持的格式
    files = []
    for ext in ["*.pdf", "*.docx", "*.doc"]:
        files.extend(dir_path.rglob(ext))
    print(f"找到 {len(files)} 个文件 (PDF/docx/doc)")
    rc_total = 0
    for f in files:
        ext = f.suffix.lower()
        if ext == ".pdf":
            rc = cmd_parse_pdf(argparse.Namespace(path=str(f), output=None))
        elif ext == ".docx":
            rc = cmd_parse_docx(argparse.Namespace(path=str(f), output=None))
        elif ext == ".doc":
            rc = cmd_parse_doc(argparse.Namespace(path=str(f), output=None))
        else:
            continue
        rc_total = max(rc_total, rc)
    return rc_total


def cmd_split(args) -> int:
    out = args.output or str(SPLIT_DIR / f"{Path(args.path).stem.replace('_raw', '')}_split_v11.json")
    return _run_script("split_questions_v11.py", [args.path, out])


def cmd_pipeline(args) -> int:
    """C1+C2 一体化: PDF/docx/doc → raw.json → split_v11.json"""
    src = Path(args.path)
    if not src.exists():
        print(f"ERROR: 文件不存在 {src}", file=sys.stderr)
        return 1
    ensure_dirs()

    ext = src.suffix.lower()
    # Step 1: 解析
    raw_out = RAW_DIR / f"{src.stem}_raw.json"
    if ext == ".pdf":
        rc = cmd_parse_pdf(argparse.Namespace(path=str(src), output=str(raw_out)))
    elif ext == ".docx":
        rc = cmd_parse_docx(argparse.Namespace(path=str(src), output=str(raw_out)))
    elif ext == ".doc":
        rc = cmd_parse_doc(argparse.Namespace(path=str(src), output=str(raw_out)))
    else:
        print(f"ERROR: 不支持的文件格式 {ext}", file=sys.stderr)
        return 1
    if rc != 0:
        return rc

    # Step 2: 切分
    if not raw_out.exists():
        print(f"ERROR: raw.json 未生成 {raw_out}", file=sys.stderr)
        return 1
    split_out = SPLIT_DIR / f"{src.stem.replace('_raw', '')}_split_v11.json"
    return cmd_split(argparse.Namespace(path=str(raw_out), output=str(split_out)))


def cmd_llm_gen(args) -> int:
    """C3.1: GLM-5 出题 (给定主题/知识点, 生成 N 个母题候选)"""
    out = args.output or str(RAW_DIR.parent / "llm_gen" / f"{args.theme}_gen.json")
    return _run_script("glm5_question_gen.py", [args.theme, "--count", str(args.count), "--output", out])


def cmd_llm_review(args) -> int:
    """C3.2: glm-4-flash 推演验证 (对母题生成答案/解析)"""
    out = args.output or str(args.path.replace(".json", "_reviewed.json"))
    return _run_script("glm4_flash_review.py", [args.path, "--output", out])


def cmd_info(args) -> int:
    """打印当前路径配置"""
    print(config_info())
    return 0


def cmd_version(args) -> int:
    print(f"pt030_toolkit v{__version__}")
    return 0


def main() -> int:
    # 先单独解析 --version / --help (避免 subparsers 互斥)
    if len(sys.argv) >= 2 and sys.argv[1] in ("--version", "-v"):
        print(f"pt030_toolkit v{__version__}")
        return 0
    if len(sys.argv) == 1 or (len(sys.argv) == 2 and sys.argv[1] in ("--help", "-h")):
        # 无子命令或仅 --help, 显示帮助
        return _print_help()

    parser = argparse.ArgumentParser(
        prog="pt030",
        description="PT-030 真题处理工具包 v1.0 (宇兄端 ↔ 雪薇端 跨机协作)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=False,  # 自己处理 --help
        epilog="""
示例:
  python -m pt030_toolkit.cli info
  python -m pt030_toolkit.cli pipeline path/to/exam.pdf
  python -m pt030_toolkit.cli parse-pdf path/to/exam.pdf
  python -m pt030_toolkit.cli llm-gen "函数与极限"
  python -m pt030_toolkit.cli llm-review path/to/parent_problem.json
        """
    )

    subparsers = parser.add_subparsers(dest="command", title="子命令")

    # version (子命令)
    sub = subparsers.add_parser("version", help="显示版本号")
    sub.set_defaults(func=cmd_version)

    # info
    sub = subparsers.add_parser("info", help="显示当前路径配置")
    sub.set_defaults(func=cmd_info)

    # parse-pdf
    sub = subparsers.add_parser("parse-pdf", help="C1 PDF 解析")
    sub.add_argument("path", help="PDF 文件路径")
    sub.add_argument("--output", "-o", help="输出 JSON 路径 (默认: RAW_DIR/<stem>_raw.json)")
    sub.set_defaults(func=cmd_parse_pdf)

    # parse-docx
    sub = subparsers.add_parser("parse-docx", help="docx 解析")
    sub.add_argument("path", help="docx 文件路径")
    sub.add_argument("--output", "-o", help="输出 JSON 路径")
    sub.set_defaults(func=cmd_parse_docx)

    # parse-doc
    sub = subparsers.add_parser("parse-doc", help=".doc 老试卷解析 (需 win32com + Word)")
    sub.add_argument("path", help=".doc 文件路径")
    sub.add_argument("--output", "-o", help="输出 JSON 路径")
    sub.set_defaults(func=cmd_parse_doc)

    # parse-batch
    sub = subparsers.add_parser("parse-batch", help="批量解析目录下所有 PDF/docx/doc")
    sub.add_argument("path", help="目录路径")
    sub.set_defaults(func=cmd_parse_batch)

    # split
    sub = subparsers.add_parser("split", help="C2 题目切分 (v1.1)")
    sub.add_argument("path", help="raw.json 路径")
    sub.add_argument("--output", "-o", help="输出 JSON 路径")
    sub.set_defaults(func=cmd_split)

    # pipeline
    sub = subparsers.add_parser("pipeline", help="C1+C2 一体化流水线")
    sub.add_argument("path", help="PDF/docx/doc 文件路径")
    sub.set_defaults(func=cmd_pipeline)

    # llm-gen (C3.1)
    sub = subparsers.add_parser("llm-gen", help="C3.1 GLM-5 出题")
    sub.add_argument("theme", help="主题/知识点 (如 '函数与极限')")
    sub.add_argument("--count", "-c", type=int, default=5, help="出题数量 (默认 5)")
    sub.add_argument("--output", "-o", help="输出 JSON 路径")
    sub.set_defaults(func=cmd_llm_gen)

    # llm-review (C3.2)
    sub = subparsers.add_parser("llm-review", help="C3.2 glm-4-flash 推演验证")
    sub.add_argument("path", help="parent_problem.json 路径")
    sub.add_argument("--output", "-o", help="输出 JSON 路径")
    sub.set_defaults(func=cmd_llm_review)

    args = parser.parse_args()

    if not hasattr(args, "func"):
        # 无子命令时, 显示帮助
        return _print_help()
    return args.func(args)


def _print_help() -> int:
    """打印 CLI 帮助 (手动实现, 避免 subparsers 互斥)"""
    help_text = f"""pt030_toolkit v{__version__} - PT-030 真题处理工具包

用法: python -m pt030_toolkit.cli <command> [options]

子命令:
  version                          显示版本号
  info                             显示当前路径配置
  parse-pdf <pdf> [--output o]     C1 PDF 解析
  parse-docx <docx> [--output o]   docx 解析
  parse-doc <doc> [--output o]     .doc 老试卷解析 (需 win32com + Word)
  parse-batch <dir>                批量解析目录下所有 PDF/docx/doc
  split <raw.json> [--output o]    C2 题目切分 (v1.1)
  pipeline <pdf/docx/doc>          C1+C2 一体化流水线
  llm-gen <theme> [--count 5]      C3.1 GLM-5 出题 (实际 glm-4-flash)
  llm-review <json>                C3.2 glm-4-flash 推演验证

路径配置:
  环境变量优先级 > config.yaml > 代码默认 D:\\4_data\\
  常用环境变量: PT030_RAW_DIR, PT030_SPLIT_DIR, PT030_ZHENTI_DIR, PT030_CONFIG

跨机使用 (雪薇端):
  1. git pull
  2. export PYTHONPATH=/path/to/SPDT-004_EduContent/tools:$PYTHONPATH
  3. cp tools/pt030_toolkit/config.yaml.example tools/pt030_toolkit/config.yaml
     # 或 export PT030_RAW_DIR=你的路径
  4. pip install pypdf python-docx pyyaml zhipuai pywin32
  5. python -m pt030_toolkit.cli info   # 验证

详细文档: tools/pt030_toolkit/README.md
"""
    print(help_text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
