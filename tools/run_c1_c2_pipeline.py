"""
PT-030 流水线: C1 PDF 解析 → raw/ → C2 切分 → split/
=================================================
"""
import json
import sys
from pathlib import Path
import subprocess

# 配置
RAW_DIR = Path(r'D:\4_data\rujing_out\真题主库\raw')
SPLIT_DIR = Path(r'D:\4_data\rujing_out\真题主库\split')
TOOLS_DIR = Path(r'D:\2_products\education\SPDT-004_EduContent\tools')

PDF_DIR = Path(r'D:\9_archive\上海高考试卷\上海高考历史1990-2019、24')
PY = 'python'

# 找 1 个 PDF 测试
pdfs = list(PDF_DIR.rglob("*.pdf"))
if not pdfs:
    print("ERROR: no PDF found")
    sys.exit(1)

pdf = pdfs[0]
print(f"Test PDF: {pdf.name}")

# Step 1: C1 解析 + 输出
print("\n=== Step 1: C1 PDF 解析 ===")
RAW_DIR.mkdir(parents=True, exist_ok=True)
raw_out = RAW_DIR / (pdf.stem + "_raw.json")

# 临时改 C1 输出: 通过 monkey-patching 或直接调 parse_pdf
sys.path.insert(0, str(TOOLS_DIR))
from parse_pdf_exam import parse_pdf, detect_questions, detect_options, extract_text

result = parse_pdf(pdf, raw_out)
if "error" in result:
    print(f"ERROR: {result['error']}")
    sys.exit(1)
print(f"  写入: {raw_out}")
print(f"  检测: {result['questions_detected']} 个题号")

# Step 2: C2 切分
print("\n=== Step 2: C2 题目切分 ===")
SPLIT_DIR.mkdir(parents=True, exist_ok=True)
split_out = SPLIT_DIR / (pdf.stem + "_split.json")

# 重新加载 raw 并用 C2 切分
raw = json.loads(raw_out.read_text(encoding="utf-8"))

# 重建 text (C1 已存到 questions 中只有 start/match, 需重新提取)
pages = extract_text(pdf)
text = "\n".join(p["text"] for p in pages)
raw["pages"] = pages  # 保存到 raw 供 C2 用
raw["text"] = text

# 重建 questions 含 start (C1 输出可能没 start, 这里补)
from parse_pdf_exam import detect_questions as c1_detect
detected = c1_detect(text)
raw["questions"] = [
    {"q_no": q["q_no"], "start": q["start"], "match": q["match"], "options": q.get("options", [])}
    for q in detected
]

# 用 C2 切分
from split_questions import split_questions
split_result = split_questions(raw)

split_final = {
    "source_raw": str(raw_out),
    "source_pdf": str(pdf),
    "total_questions": len(split_result),
    "questions": split_result,
    "_v1_caveat": "题干切分 OK, 答案/解析留给 C3 (双 LLM)",
    "_created": "2026-09-12 by 宇兄窗口 (PT-030 C1+C2 联合)"
}

split_out.write_bytes(json.dumps(split_final, ensure_ascii=False, indent=2).encode("utf-8"))
print(f"  写入: {split_out}")
print(f"  切分: {len(split_result)} 题")

# 打印前 3 题
print("\n=== 前 3 题预览 ===")
for q in split_result[:3]:
    print(f"\nQ{q['q_no']} [{q['type']}, {q['score']}分]")
    print(f"  题干: {q['stem'][:120]}...")
    print(f"  选项: {len(q['options'])} 个")
    for opt in q['options'][:4]:
        print(f"    {opt['label']}: {opt['text'][:50]}...")

# 更新 raw with text (供后续 C2 单独运行)
raw_out.write_bytes(json.dumps(raw, ensure_ascii=False, indent=2).encode("utf-8"))
print(f"\n  更新 raw (含 pages/text): {raw_out}")
