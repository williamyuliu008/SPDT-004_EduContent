"""
PT-030 docx 试卷解析器 v1.0
=========================
输入: D:\9_archive\上海高考试卷\上海高考<学科>1990-2025\*.docx
输出: D:\4_data\rujing_out\真题主库\raw\<年份>_<学科>_raw.json

高难度组件 (宇兄端开发, PT-030 工具链 — 补全 1990-2017 老试卷)

C1 PDF 解析器的 docx 对应版本:
- PDF: pypdf 6.10.2 (文本提取, 字体编码复杂)
- docx: python-docx (XML 结构, 文本清晰)

用法:
  python parse_docx_exam.py <docx_path> [<output_path>]
  python parse_docx_exam.py --batch <dir_path>
"""

import json
import re
import sys
from pathlib import Path
from docx import Document


# 题号正则 (与 PDF 版一致)
QUESTION_NUM_RE = re.compile(
    r"^\s*(?:[（(](?P<num1>\d{1,3})[）)]|(?P<num2>\d{1,3}))[\.、．\s]*",
    re.MULTILINE
)

# 选项标记 (A./A、/A．/A 空格)
OPTION_INLINE_RE = re.compile(
    r"[\s　]+[（(]?([A-D])[）)]?[\s　]*[\.、．]?[\s　]+(?=[^\s　])"
)

# 分值
SCORE_RE = re.compile(r"[(（]?\s*(\d{1,2})\s*分\s*[)）]?")


def extract_text(docx_path: Path) -> tuple[str, list[dict]]:
    """提取 docx 全文 + 段落结构 (docx 用 XML 结构, 比 PDF 干净)"""
    doc = Document(str(docx_path))
    paragraphs = []
    full_text_parts = []
    for i, p in enumerate(doc.paragraphs):
        text = p.text
        if text.strip():
            paragraphs.append({
                "para_no": i,
                "text": text,
                "style": p.style.name if p.style else "Normal"
            })
            full_text_parts.append(text)
    # 也提取表格 (老试卷答案常在表格)
    for ti, table in enumerate(doc.tables):
        for ri, row in enumerate(table.rows):
            for ci, cell in enumerate(row.cells):
                text = cell.text.strip()
                if text:
                    paragraphs.append({
                        "para_no": f"table{ti}_r{ri}_c{ci}",
                        "text": text,
                        "style": "Table"
                    })
                    full_text_parts.append(text)
    full_text = "\n".join(full_text_parts)
    return full_text, paragraphs


def detect_questions(text: str) -> list[dict]:
    """docx 题号识别 (比 PDF 简单 — docx 文本干净, 通常 1-3 位数字独占一行)"""
    questions = []
    seen = set()
    for m in QUESTION_NUM_RE.finditer(text):
        q_no_str = m.group("num1") or m.group("num2")
        if not q_no_str:
            continue
        q_no = int(q_no_str)
        if q_no in seen or q_no > 35:
            continue
        # 前缀校验: 紧邻不应是数字
        ctx_start = max(0, m.start() - 3)
        prefix = text[ctx_start:m.start()]
        if re.search(r"\d" + re.escape(q_no_str), prefix):
            continue
        seen.add(q_no)
        questions.append({
            "q_no": q_no,
            "start": m.start(),
            "end": m.end(),
            "match": m.group(0).strip()[:30]
        })
    questions.sort(key=lambda x: x["start"])
    return questions


def detect_options(text: str) -> list[dict]:
    """docx 选项检测 (用 split 替代 lookahead)"""
    matches = list(OPTION_INLINE_RE.finditer(text))
    if len(matches) < 2:
        return []

    # 验证: 标签应按 A→B→C→D 顺序
    labels = [m.group(1) for m in matches]
    if len(set(labels)) < 2:
        return []

    opts = []
    for i, m in enumerate(matches):
        label = m.group(1)
        content_start = m.end()
        if i + 1 < len(matches):
            content_end = matches[i + 1].start()
        else:
            content_end = len(text)
        content = text[content_start:content_end].strip()
        # 清理: 删分值标记
        content = re.sub(r"[(（]?\s*\d{1,2}\s*分\s*[)）]?", "", content)
        opts.append({"label": label, "text": content[:500]})

    # 去重
    seen_labels = set()
    unique = []
    for o in opts:
        if o["label"] not in seen_labels:
            seen_labels.add(o["label"])
            unique.append(o)
    return unique if len(unique) >= 2 else []


def detect_score(text: str) -> int | None:
    """docx 分值检测"""
    m = SCORE_RE.search(text)
    return int(m.group(1)) if m else None


def detect_type(stem: str, options: list, score: int | None) -> str:
    """题型识别"""
    if options and len(options) >= 3 and (not score or score < 5):
        return "选择"
    if options and len(options) >= 4 and (score or 0) >= 5 and "提纲" in stem:
        return "提纲"
    if score and score >= 10:
        return "论述"
    if score and score >= 5:
        return "简答"
    if any(kw in stem for kw in ["论述", "评述", "谈谈", "如何理解"]):
        return "论述"
    if any(kw in stem for kw in ["简答", "简要", "概述"]):
        return "简答"
    return "未知"


def parse_docx(docx_path: Path, output_path: Path | None = None) -> dict:
    """主函数: docx → raw JSON"""
    if not docx_path.exists():
        return {"error": f"docx not found: {docx_path}"}

    print(f"解析: {docx_path.name}")
    full_text, paragraphs = extract_text(docx_path)

    questions = detect_questions(full_text)

    # 按题号切分
    results = []
    for i, q in enumerate(questions):
        start = q["start"]
        end = questions[i + 1]["start"] if i + 1 < len(questions) else len(full_text)
        full_stem = full_text[start:end].strip()

        options = detect_options(full_stem)
        score = detect_score(full_stem)
        q_type = detect_type(full_stem, options, score)

        # 题干清洗
        clean_stem = re.sub(r"^\s*\d{1,3}\s*[\.、．\s]+", "", full_stem)
        clean_stem = re.sub(r"[(（]\s*\d{1,2}\s*分\s*[)）]?", "", clean_stem)
        # 删尾部选项
        for opt in options:
            opt_pat = re.compile(rf"[\s　]+[（(]?{opt['label']}[）)]?[\s　]*[\.、．]?[\s　]+", re.MULTILINE)
            m = opt_pat.search(clean_stem)
            if m:
                next_m = opt_pat.search(clean_stem, m.end())
                end_idx = next_m.start() if next_m else len(clean_stem)
                clean_stem = clean_stem[:m.start()] + clean_stem[end_idx:]
        clean_stem = clean_stem.strip()

        results.append({
            "q_no": q["q_no"],
            "type": q_type,
            "score": score,
            "stem": clean_stem[:1500],  # docx 题干可能较长
            "options": options,
        })

    # 输出
    result = {
        "source_file": str(docx_path),
        "total_paragraphs": len(paragraphs),
        "total_chars": len(full_text),
        "questions_detected": len(questions),
        "questions": results,
        "_v1_caveat": "v1.0 docx 基础解析. docx 文本干净, 选项/题号识别比 PDF 简单. 答案/解析留给 C3 双 LLM.",
        "_created": "2026-09-12 by 宇兄窗口 (PT-030 docx 解析器 v1.0)"
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
        print("  python parse_docx_exam.py <docx_path>")
        print("  python parse_docx_exam.py --batch <dir_path>")
        return

    arg = sys.argv[1]
    if arg == "--batch" and len(sys.argv) >= 3:
        dir_path = Path(sys.argv[2])
        docxs = list(dir_path.rglob("*.docx"))
        print(f"批量处理: {len(docxs)} 个 docx")
        for docx in docxs:
            try:
                result = parse_docx(docx)
                if "error" in result:
                    print(f"  ERROR: {docx.name}: {result['error']}")
                else:
                    opt_n = sum(1 for q in result["questions"] if q["options"])
                    print(f"  ✓ {docx.name[:40]}: {result['questions_detected']} 题, {opt_n} 有选项")
            except Exception as e:
                print(f"  ERROR: {docx.name}: {e}")
    else:
        docx_path = Path(arg)
        result = parse_docx(docx_path)
        if "error" in result:
            print(f"ERROR: {result['error']}")
            sys.exit(1)
        print(f"\n结果: 检测到 {result['questions_detected']} 个题号")
        for q in result["questions"][:5]:
            opt_str = ", ".join(o["label"] for o in q["options"])
            print(f"  Q{q['q_no']} [{q['type']}, {q['score']}分] {len(q['options'])} 选项 [{opt_str}]")
        if len(result["questions"]) > 5:
            print(f"  ... 共 {len(result['questions'])} 题")


if __name__ == "__main__":
    main()
