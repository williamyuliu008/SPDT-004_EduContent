"""
PT-030 .doc 老试卷解析器 v1.0
============================
输入: D:\9_archive\上海高考试卷\上海高考<学科>1990-2025\*.doc
输出: D:\4_data\rujing_out\真题主库\raw\<年份>_<学科>_raw.json

高难度组件 (宇兄端开发, PT-030 工具链 — 补全 1990-2017 老试卷)

.doc 是老 Word 二进制格式, python-docx 不支持。
方案: win32com.client 调本地 Word 16.0 (DCOM) 打开 .doc, 提取文本。

用法:
  python parse_doc_exam.py <doc_path> [<output_path>]
  python parse_doc_exam.py --batch <dir_path>

依赖: Windows + MS Word 16.0 (或更高) + pywin32 (pip install pywin32)
"""

import json
import re
import sys
import time
from pathlib import Path


# 题号正则 (与 PDF/docx 一致)
QUESTION_NUM_RE = re.compile(
    r"^\s*(?:[（(](?P<num1>\d{1,3})[）)]|(?P<num2>\d{1,3}))[\.、．\s]*",
    re.MULTILINE
)
OPTION_INLINE_RE = re.compile(
    r"[\s　]+[（(]?([A-D])[）)]?[\s　]*[\.、．]?[\s　]*(?=[^\s　])"
)
SCORE_RE = re.compile(r"[(（]?\s*(\d{1,2})\s*分\s*[)）]?")


def extract_text_via_word(doc_path: Path) -> str:
    """用 win32com + Word 提取 .doc 文本"""
    import win32com.client

    word = win32com.client.Dispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0  # wdAlertsNone

    try:
        # 绝对路径 + 12 = wdFormatText (纯文本)
        abs_path = str(doc_path.resolve())
        doc = word.Documents.Open(abs_path)
        try:
            text = doc.Content.Text
        finally:
            doc.Close(SaveChanges=False)
    finally:
        word.Quit()

    return text


def detect_questions(text: str) -> list[dict]:
    """doc 题号识别 (.doc 老试卷题号可能在段中, 1990 是 "1." 紧跟题干, 前面是中文标点或 \\x0b)"""
    # Word 文档常用 \\x0b (VT) 作换行符, 不只是 \\n
    # 起始字符: 行首 (^), \\n, \\x0b, 中文标点 (, 。 ；、)
    questions = []
    seen = set()
    pat_line = re.compile(
        r"(?:^|[\n\x0b。；，、])\s*(\d{1,3})\s*[\.、．]\s*",
        re.MULTILINE
    )
    for m in pat_line.finditer(text):
        q_no = int(m.group(1))
        if q_no in seen or q_no > 35:
            continue
        ctx_start = max(0, m.start() - 5)
        prefix = text[ctx_start:m.start()]
        # 排除 "1990年" 等年份片段
        if re.search(r"\d{4}", prefix):
            continue
        seen.add(q_no)
        questions.append({
            "q_no": q_no,
            "start": m.start() + len(m.group(0)) - len(m.group(0).lstrip('\n').lstrip()),
            "end": m.end(),
            "match": m.group(0).strip()[:30]
        })
    questions.sort(key=lambda x: x["start"])
    return questions


def detect_options(text: str) -> list[dict]:
    """doc 选项检测"""
    matches = list(OPTION_INLINE_RE.finditer(text))
    if len(matches) < 2:
        return []
    labels = [m.group(1) for m in matches]
    if len(set(labels)) < 2:
        return []
    opts = []
    for i, m in enumerate(matches):
        label = m.group(1)
        content_start = m.end()
        content_end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        content = text[content_start:content_end].strip()
        content = re.sub(r"[(（]?\s*\d{1,2}\s*分\s*[)）]?", "", content)
        opts.append({"label": label, "text": content[:500]})
    seen_labels = set()
    unique = []
    for o in opts:
        if o["label"] not in seen_labels:
            seen_labels.add(o["label"])
            unique.append(o)
    return unique if len(unique) >= 2 else []


def detect_score(text: str) -> int | None:
    m = SCORE_RE.search(text)
    return int(m.group(1)) if m else None


def detect_type(stem: str, options: list, score: int | None) -> str:
    if options and len(options) >= 3 and (not score or score < 5):
        return "选择"
    if score and score >= 10:
        return "论述"
    if score and score >= 5:
        return "简答"
    return "未知"


def parse_doc(doc_path: Path, output_path: Path | None = None) -> dict:
    """主函数: .doc → raw JSON"""
    if not doc_path.exists():
        return {"error": f"doc not found: {doc_path}"}

    print(f"解析 (Word COM): {doc_path.name}")
    t0 = time.time()
    try:
        full_text = extract_text_via_word(doc_path)
    except Exception as e:
        return {"error": f"Word COM 失败: {e}"}
    elapsed = time.time() - t0
    print(f"  Word 提取耗时: {elapsed:.1f}s, 文本 {len(full_text)} 字符")

    questions = detect_questions(full_text)
    results = []
    for i, q in enumerate(questions):
        start = q["start"]
        end = questions[i + 1]["start"] if i + 1 < len(questions) else len(full_text)
        full_stem = full_text[start:end].strip()
        options = detect_options(full_stem)
        score = detect_score(full_stem)
        q_type = detect_type(full_stem, options, score)
        clean_stem = re.sub(r"^\s*\d{1,3}\s*[\.、．\s]+", "", full_stem)
        clean_stem = re.sub(r"[(（]\s*\d{1,2}\s*分\s*[)）]?", "", clean_stem)
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
            "stem": clean_stem[:1500],
            "options": options,
        })

    result = {
        "source_file": str(doc_path),
        "extract_method": "win32com + Word 16.0",
        "extract_seconds": round(elapsed, 1),
        "total_chars": len(full_text),
        "questions_detected": len(questions),
        "questions": results,
        "_v1_caveat": "v1.0 .doc 老试卷解析 (1990-2017 上海高考历史). Word COM 慢 (~3-5s/文件), 但精度高. 答案/解析留给 C3.",
        "_created": "2026-09-12 by 宇兄窗口 (PT-030 .doc 解析器 v1.0)"
    }

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(
            json.dumps(result, ensure_ascii=False, indent=2).encode('utf-8')
        )
        print(f"  写入: {output_path}")
    return result


def main():
    # 强制 stdout UTF-8 (避免 gbk 编码失败)
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

    if len(sys.argv) < 2:
        print("用法:")
        print("  python parse_doc_exam.py <doc_path>")
        print("  python parse_doc_exam.py --batch <dir_path>")
        return

    arg = sys.argv[1]
    if arg == "--batch" and len(sys.argv) >= 3:
        dir_path = Path(sys.argv[2])
        docs = list(dir_path.rglob("*.doc"))
        print(f"批量处理: {len(docs)} 个 .doc")
        for i, doc in enumerate(docs, 1):
            try:
                result = parse_doc(doc)
                if "error" in result:
                    print(f"  [{i}/{len(docs)}] ERROR: {doc.name}: {result['error']}")
                else:
                    opt_n = sum(1 for q in result["questions"] if q["options"])
                    print(f"  [{i}/{len(docs)}] [OK] {doc.name[:30]}: {result['questions_detected']} 题, {opt_n} 有选项, {result['extract_seconds']}s")
            except Exception as e:
                print(f"  [{i}/{len(docs)}] ERROR: {doc.name}: {e}")
    else:
        doc_path = Path(arg)
        result = parse_doc(doc_path)
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
