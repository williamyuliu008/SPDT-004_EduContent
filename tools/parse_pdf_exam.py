"""
PT-030 PDF 试卷解析器 v1.0
========================
输入: D:\9_archive\上海高考试卷\上海高考<学科>1990-2025\*.pdf
输出: D:\4_data\rujing_out\真题主库\raw\<年份>_<学科>_raw.json

高难度组件 C1 (宇兄端开发, PT-030 工具链一环)

用法:
  python parse_pdf_exam.py <pdf_path> [<output_path>]
  python parse_pdf_exam.py D:\9_archive\上海高考试卷\上海高考历史1990-2019、24\2018_上海_高考_历史.pdf
  python parse_pdf_exam.py --batch D:\9_archive\上海高考试卷\上海高考历史1990-2019、24\
"""

import json
import re
import sys
from pathlib import Path
from pypdf import PdfReader


# 题号正则: 兼容 "1." "1、" "1．" "1．" "（1）" "(1)" 等格式
QUESTION_NUM_RE = re.compile(
    r"^\s*(?:[（(]?(\d{1,3})[）)]?[\.、．\s]*)",
    re.MULTILINE
)

# 选项正则: A. / A、 / A． / (A) 等
OPTION_RE = re.compile(
    r"\n\s*[（(]?([A-D])[）)]?[\.、．\s]+",
)


def extract_text(pdf_path: Path) -> list[dict]:
    """提取 PDF 每页文本"""
    reader = PdfReader(str(pdf_path))
    pages = []
    for i, page in enumerate(reader.pages):
        try:
            text = page.extract_text() or ""
            pages.append({"page_no": i + 1, "text": text})
        except Exception as e:
            pages.append({"page_no": i + 1, "text": "", "error": str(e)})
    return pages


def detect_questions(text: str) -> list[dict]:
    """粗略题号识别 (返回每题起始位置 + 题号)"""
    questions = []
    for m in QUESTION_NUM_RE.finditer(text):
        q_no = m.group(1)
        questions.append({
            "q_no": int(q_no),
            "start": m.start(),
            "match": m.group(0).strip()[:20]
        })
    return questions


def detect_options(text: str) -> dict[int, list[dict]]:
    """检测每题选项 (A/B/C/D)"""
    options_per_q = {}
    # 按题号切分
    q_matches = list(QUESTION_NUM_RE.finditer(text))
    for i, m in enumerate(q_matches):
        q_no = int(m.group(1))
        end = q_matches[i + 1].start() if i + 1 < len(q_matches) else len(text)
        q_text = text[m.start():end]
        # 检测选项
        opts = []
        for opt_m in OPTION_RE.finditer(q_text):
            opt_label = opt_m.group(1)
            opt_text_start = opt_m.end()
            # 选项结束: 下一选项或题尾
            next_opt = OPTION_RE.search(q_text, opt_text_start)
            opt_text_end = next_opt.start() if next_opt else len(q_text)
            opt_content = q_text[opt_text_start:opt_text_end].strip()
            opts.append({"label": opt_label, "text": opt_content[:200]})
        options_per_q[q_no] = opts
    return options_per_q


def parse_pdf(pdf_path: Path, output_path: Path | None = None) -> dict:
    """主函数: 解析 PDF → 题目结构"""
    if not pdf_path.exists():
        return {"error": f"PDF not found: {pdf_path}"}

    print(f"解析: {pdf_path.name}")
    pages = extract_text(pdf_path)
    full_text = "\n".join(p["text"] for p in pages)

    questions = detect_questions(full_text)
    options = detect_options(full_text)

    # 输出结构
    result = {
        "source_file": str(pdf_path),
        "total_pages": len(pages),
        "total_chars": len(full_text),
        "questions_detected": len(questions),
        "questions": [
            {
                "q_no": q["q_no"],
                "match": q["match"],
                "options": options.get(q["q_no"], []),
                # 完整题干需要进一步 LLM 切分 (留给 C2 切分算法)
                "stem_raw": full_text[q["start"]:q["start"]+500]
            }
            for q in questions
        ],
        "_v1_caveat": "v1.0 仅做基础题号识别 + 选项检测, 完整题干/答案/解析由 LLM (C2 切分算法) 处理",
        "_created": "2026-09-12 by 宇兄窗口 (PT-030 C1 高难度组件)"
    }

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(
            json.dumps(result, ensure_ascii=False, indent=2).encode('utf-8')
        )
        print(f"  写入: {output_path}")
    return result


def main():
    if len(sys.argv) < 2:
        print("用法:")
        print("  python parse_pdf_exam.py <pdf_path> [<output_path>]")
        print("  python parse_pdf_exam.py --batch <dir_path>")
        print("")
        print("示例:")
        print('  python parse_pdf_exam.py "D:\\9_archive\\上海高考试卷\\上海高考历史1990-2019、24\\2018_上海_高考_历史.pdf"')
        return

    arg = sys.argv[1]
    if arg == "--batch" and len(sys.argv) >= 3:
        dir_path = Path(sys.argv[2])
        pdfs = list(dir_path.rglob("*.pdf"))
        print(f"批量处理: {len(pdfs)} 个 PDF")
        for pdf in pdfs:
            try:
                # 写文件到同目录 _raw.json
                out = pdf.parent / f"{pdf.stem}_raw.json"
                parse_pdf(pdf, out)
            except Exception as e:
                print(f"  ERROR: {pdf.name}: {e}")
    else:
        pdf_path = Path(arg)
        # 第二个参数是 output_path (可选)
        if len(sys.argv) >= 3 and not sys.argv[2].startswith("-"):
            output_path = Path(sys.argv[2])
        else:
            output_path = pdf_path.parent / f"{pdf_path.stem}_raw.json"
        result = parse_pdf(pdf_path, output_path)
        if "error" in result:
            print(f"ERROR: {result['error']}")
            sys.exit(1)
        print(f"\n结果: 检测到 {result['questions_detected']} 个题号")
        for q in result["questions"][:5]:
            opts = ", ".join(o["label"] for o in q["options"])
            print(f"  Q{q['q_no']}: {len(q['options'])} 选项 [{opts}]")
        if len(result["questions"]) > 5:
            print(f"  ... 共 {len(result['questions'])} 题")


if __name__ == "__main__":
    main()
