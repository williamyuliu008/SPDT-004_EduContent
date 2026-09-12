"""
PT-030 数学流水线 — 雪薇端 helper v1.0
====================================
绕开宇兄端 split_questions_v11.py main 函数不接收第 2 个参数的 bug,
封装"解析 + 切分 + 落库"端到端, 一条命令搞定.

用法 (雪薇端):
    # 单文件: parse_docx + split
    python tools/math_pipeline.py "E:\\我的数据\\上海高考试卷\\...\\2024年上海高考数学真题（原卷版）.docx"

    # 批量: 解析目录下所有 docx/doc/pdf
    python tools/math_pipeline.py --batch "E:\\我的数据\\上海高考试卷\\上海高考数学1990-2025\\秋考卷（1990-2025）"

    # 干跑: 只跑 C1 (parse), 不跑 C2 (split)
    python tools/math_pipeline.py --parse-only <file>

    # 只跑 C2 (用已有的 raw.json)
    python tools/math_pipeline.py --split-only <raw.json>

依赖:
    pip install pypdf python-docx pywin32
落点:
    raw  -> D:\\Z_学习平台\\SPDT-004_EduContent\\PT-030\\zhenti\\数学\\raw\\
    split -> D:\\Z_学习平台\\SPDT-004_EduContent\\PT-030\\zhenti\\数学\\split\\
"""

import sys
import json
from pathlib import Path

# 让 import pt030_toolkit 工作
_TOOLS_DIR = Path(__file__).parent
sys.path.insert(0, str(_TOOLS_DIR))

from pt030_toolkit.config import RAW_DIR, SPLIT_DIR, ensure_dirs
from split_questions_v11 import split_raw_file_v11


def cmd_parse(src: Path) -> Path:
    """C1 解析 (按扩展名分派). 返回 raw.json 路径"""
    ensure_dirs()
    ext = src.suffix.lower()
    raw_out = RAW_DIR / f"{src.stem}_raw.json"

    if ext == ".pdf":
        from parse_pdf_exam import parse_pdf  # noqa
        # 实际由 cli 调起, 这里用 subprocess
        import subprocess
        r = subprocess.run([sys.executable, str(_TOOLS_DIR / "parse_pdf_exam.py"), str(src), str(raw_out)],
                          capture_output=True, text=True, encoding="utf-8", errors="replace")
        print(r.stdout)
        if r.returncode != 0:
            print(f"ERROR parse_pdf: {r.stderr}", file=sys.stderr)
            sys.exit(1)

    elif ext == ".docx":
        import subprocess
        r = subprocess.run([sys.executable, str(_TOOLS_DIR / "parse_docx_exam.py"), str(src), str(raw_out)],
                          capture_output=True, text=True, encoding="utf-8", errors="replace")
        print(r.stdout)
        if r.returncode != 0:
            print(f"ERROR parse_docx: {r.stderr}", file=sys.stderr)
            sys.exit(1)

    elif ext == ".doc":
        # parse_doc_exam.py 需 win32com + Word, 仅 Windows
        import subprocess
        r = subprocess.run([sys.executable, str(_TOOLS_DIR / "parse_doc_exam.py"), str(src), str(raw_out)],
                          capture_output=True, text=True, encoding="utf-8", errors="replace")
        print(r.stdout)
        if r.returncode != 0:
            print(f"ERROR parse_doc: {r.stderr}", file=sys.stderr)
            sys.exit(1)
    else:
        print(f"ERROR: 不支持的扩展名 {ext}", file=sys.stderr)
        sys.exit(1)

    if not raw_out.exists():
        print(f"ERROR: raw.json 未生成 {raw_out}", file=sys.stderr)
        sys.exit(1)
    return raw_out


def cmd_split(raw_path: Path) -> Path:
    """C2 切分 (绕开 v1.1 main 不收 argv[2] 的 bug, 直接调函数)"""
    ensure_dirs()
    split_out = SPLIT_DIR / f"{raw_path.stem.replace('_raw', '')}_split_v11.json"
    result = split_raw_file_v11(raw_path, split_out)
    if "error" in result:
        print(f"ERROR: {result['error']}", file=sys.stderr)
        sys.exit(1)
    print(f"\n  [math_pipeline] 切分完成: {result['total_questions']} 题, "
          f"{result['questions_with_options']} 有选项, {result['questions_with_answers']} 有答案")
    return split_out


def cmd_pipeline(src: Path):
    """端到端: parse + split"""
    print(f"\n[math_pipeline] 处理: {src.name}")
    raw = cmd_parse(src)
    split = cmd_split(raw)
    print(f"\n[math_pipeline] ✅ 完成: {split}")


def cmd_batch(dir_path: Path, force: bool = False):
    """批量: 解析目录下所有 docx/doc/pdf
    默认跳过已有 split (避免同名不同扩展名覆盖)
    加 --force 强制重跑
    """
    if not dir_path.exists():
        print(f"ERROR: 目录不存在 {dir_path}", file=sys.stderr)
        sys.exit(1)
    files = []
    for ext in ["*.pdf", "*.docx", "*.doc"]:
        files.extend(dir_path.rglob(ext))
    print(f"\n[math_pipeline] 批量: 找到 {len(files)} 个文件 (pdf/docx/doc)")

    # 优先 docx/pdf (识别率高), doc 最后
    priority = {".docx": 0, ".pdf": 1, ".doc": 2}
    files.sort(key=lambda p: (priority.get(p.suffix.lower(), 9), p.name))

    ok, fail, skip = 0, 0, 0
    seen_stems = set()  # 同一 stem 只跑一个, 默认 docx 优先
    for f in files:
        stem = f.stem
        # 同 stem 已跑过 (docx 优先), 跳过 doc
        if not force and stem in seen_stems:
            print(f"\n[math_pipeline] 跳过 (同 stem 已跑): {f.name}")
            skip += 1
            continue
        seen_stems.add(stem)

        # 已有 split 且 total_questions > 0 跳过 (除非 force)
        if not force:
            existing_split = SPLIT_DIR / f"{stem}_split_v11.json"
            if existing_split.exists():
                try:
                    import json
                    d = json.loads(existing_split.read_text(encoding="utf-8"))
                    if d.get("total_questions", 0) > 0:
                        print(f"\n[math_pipeline] 跳过 (已有有效 split): {f.name}")
                        skip += 1
                        continue
                except Exception:
                    pass

        try:
            cmd_pipeline(f)
            ok += 1
        except SystemExit:
            fail += 1
    print(f"\n[math_pipeline] 批量结果: {ok} 成功, {skip} 跳过, {fail} 失败")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    if "--batch" in sys.argv:
        idx = sys.argv.index("--batch")
        if idx + 1 >= len(sys.argv):
            print("ERROR: --batch 缺目录", file=sys.stderr)
            sys.exit(1)
        force = "--force" in sys.argv
        cmd_batch(Path(sys.argv[idx + 1]), force=force)
    elif "--parse-only" in sys.argv:
        idx = sys.argv.index("--parse-only")
        if idx + 1 >= len(sys.argv):
            print("ERROR: --parse-only 缺文件", file=sys.stderr)
            sys.exit(1)
        cmd_parse(Path(sys.argv[idx + 1]))
    elif "--split-only" in sys.argv:
        idx = sys.argv.index("--split-only")
        if idx + 1 >= len(sys.argv):
            print("ERROR: --split-only 缺 raw.json", file=sys.stderr)
            sys.exit(1)
        cmd_split(Path(sys.argv[idx + 1]))
    else:
        # 单文件
        cmd_pipeline(Path(sys.argv[1]))


if __name__ == "__main__":
    main()
