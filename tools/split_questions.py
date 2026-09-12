"""
PT-030 题目切分算法 v1.0 (C2 高难度组件)
=====================================
输入: D:\4_data\rujing_out\真题主库\raw\<年份>_<学科>_raw.json (C1 输出)
输出: D:\4_data\rujing_out\真题主库\split\<年份>_<学科>_split.json

高难度组件 C2 (宇兄端开发, PT-030 工具链二环)

功能:
- 题号位置切分 (基于 C1 detect_questions)
- 完整题干提取 (从题号到下一题号)
- 选项检测改进 (多模式正则)
- 题型识别 (选择/简答/论述)
- 题目分值识别 (X分)

用法:
  python split_questions.py <raw_json> [<output_json>]
  python split_questions.py --batch D:\4_data\rujing_out\真题主库\raw\
"""

import json
import re
import sys
from pathlib import Path
from typing import Optional


# 多模式题号正则 (兼容 11 种格式)
QUESTION_NUM_PATTERNS = [
    re.compile(r"^\s*(\d{1,3})\s*[\.、．]", re.MULTILINE),  # 1.  1、
    re.compile(r"^\s*[（(](\d{1,3})[）)]\s*[\.、．]?", re.MULTILINE),  # (1) (1).
    re.compile(r"^\s*第\s*(\d{1,3})\s*题", re.MULTILINE),  # 第1题
    re.compile(r"^\s*(\d{1,3})\s*[\.、．]\s*[(（]", re.MULTILINE),  # 1. (
]

# 多模式选项正则 (改进 C1 的 0 选项 bug)
OPTION_PATTERNS = [
    re.compile(r"\n[ \t]*[（(]?([A-D])[）)]?[\.、．][ \t]*(.+?)(?=\n[ \t]*[（(]?[A-D][）)]?[\.、．]|\n[ \t]*\d+[\.、．]|\Z)", re.DOTALL),
    re.compile(r"\n[ \t]*([A-D])[ \t]+(.+?)(?=\n[ \t]*[A-D][ \t]+|\Z)", re.DOTALL),  # A xxx\nB xxx (无 .)
    re.compile(r"^([A-D])\.?\s+(.+?)(?=^[A-D]\.?|\Z)", re.MULTILINE | re.DOTALL),  # 行首 A. xxx
]

# 题型识别
TYPE_SELECT = "选择"
TYPE_SHORT = "简答"
TYPE_ESSAY = "论述"
TYPE_FILL = "填空"
SCORE_RE = re.compile(r"[(（]\s*(\d+)\s*分\s*[)）]")  # (3分) （5分）


def detect_questions_v2(text: str) -> list[dict]:
    """v2 题号识别 - 多模式合并去重"""
    matches = []
    seen_qs = set()
    for pat in QUESTION_NUM_PATTERNS:
        for m in pat.finditer(text):
            q_no = int(m.group(1))
            if q_no in seen_qs:
                continue
            seen_qs.add(q_no)
            matches.append({
                "q_no": q_no,
                "start": m.start(),
                "end": m.end(),
                "match": m.group(0).strip()[:30]
            })
    matches.sort(key=lambda x: x["start"])
    return matches


def detect_options_v2(text: str) -> list[dict]:
    """v2 选项检测 - 多模式 fallback"""
    for pat in OPTION_PATTERNS:
        opts = []
        for m in pat.finditer(text):
            opts.append({
                "label": m.group(1),
                "text": m.group(2).strip()[:500]
            })
        if len(opts) >= 2:  # 至少 2 个选项 (A B C D)
            return opts
    return []


def detect_score(text: str) -> Optional[int]:
    """检测题目分值"""
    m = SCORE_RE.search(text)
    return int(m.group(1)) if m else None


def detect_type(stem: str, options: list) -> str:
    """题型识别 (粗略)"""
    if options and len(options) >= 2:
        return TYPE_SELECT
    if any(kw in stem for kw in ["论述", "分析", "评述", "评析", "谈谈", "如何理解"]):
        return TYPE_ESSAY
    if any(kw in stem for kw in ["简答", "简要", "概述"]):
        return TYPE_SHORT
    if "____" in stem or "_____" in stem:
        return TYPE_FILL
    return TYPE_SELECT  # 默认


def split_questions(raw: dict) -> list[dict]:
    """主切分逻辑"""
    # 提取 text: 优先 raw["text"], 备选 raw["pages"]
    text = raw.get("text", "")
    if not text and "pages" in raw:
        text = "\n".join(p.get("text", "") for p in raw.get("pages", []))

    # 题号: 优先 raw["questions"] (C1 输出), 否则 v2 重识别
    questions = raw.get("questions", [])
    if not questions and text:
        questions = detect_questions_v2(text)
        # 转换为 raw["questions"] 格式
        questions = [{"q_no": q["q_no"], "start": q["start"], "match": q["match"]} for q in questions]

    if not text or not questions:
        return []

    # 按题号切分完整题干
    results = []
    for i, q in enumerate(questions):
        start = q["start"]
        end = questions[i + 1]["start"] if i + 1 < len(questions) else len(text)
        full_stem = text[start:end].strip()

        # 选项检测 (改进)
        options = detect_options_v2(full_stem)

        # 分值
        score = detect_score(full_stem)

        # 题型
        q_type = detect_type(full_stem, options)

        # 清除题干中残留的"题号"和分值标记
        clean_stem = re.sub(r"^\s*\d+\s*[\.、．]\s*", "", full_stem)
        clean_stem = re.sub(r"[(（]\s*\d+\s*分\s*[)）]", "", clean_stem)
        # 移除尾部选项
        for opt in options:
            opt_pattern = rf"\n[ \t]*[（(]?{opt['label']}[）)]?[\.、．].*?(?=\n[ \t]*[（(]?[A-D][）)]?[\.、．]|\Z)"
            clean_stem = re.sub(opt_pattern, "", clean_stem, flags=re.DOTALL)
        clean_stem = clean_stem.strip()

        results.append({
            "q_no": q["q_no"],
            "type": q_type,
            "score": score,
            "stem": clean_stem[:1000],
            "options": options,
            "_v1_caveat": "题干/答案/解析分离留给 C3 (双 LLM)"
        })

    return results


def split_raw_file(raw_path: Path, output_path: Optional[Path] = None) -> dict:
    """主函数: 单文件切分"""
    if not raw_path.exists():
        return {"error": f"raw not found: {raw_path}"}

    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    questions = split_questions(raw)

    result = {
        "source_raw": str(raw_path),
        "total_questions": len(questions),
        "questions": questions,
        "_v1_caveat": "v1.0 仅做题目切分 + 题干提取, 答案/解析由 C3 双 LLM 处理",
        "_created": "2026-09-12 by 宇兄窗口 (PT-030 C2 高难度组件)"
    }

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(json.dumps(result, ensure_ascii=False, indent=2).encode("utf-8"))
        print(f"  写入: {output_path}")
    return result


def main():
    if len(sys.argv) < 2:
        print("用法:")
        print("  python split_questions.py <raw_json>")
        print("  python split_questions.py --batch <raw_dir>")
        return

    arg = sys.argv[1]
    if arg == "--batch" and len(sys.argv) >= 3:
        raw_dir = Path(sys.argv[2])
        raws = list(raw_dir.rglob("*.json"))
        print(f"批量切分: {len(raws)} 个 raw JSON")
        for raw_path in raws:
            try:
                # 输出到 split/ 目录
                rel = raw_path.relative_to(raw_dir.parent) if raw_path.is_relative_to(raw_dir.parent) else raw_path.name
                out = raw_path.parent.parent / "split" / raw_path.name
                split_raw_file(raw_path, out)
            except Exception as e:
                print(f"  ERROR: {raw_path.name}: {e}")
    else:
        raw_path = Path(arg)
        result = split_raw_file(raw_path)
        if "error" in result:
            print(f"ERROR: {result['error']}")
            sys.exit(1)
        print(f"\n结果: 切分 {result['total_questions']} 题")
        for q in result["questions"][:3]:
            print(f"  Q{q['q_no']} [{q['type']}]: stem 前 80 字符: {q['stem'][:80]}...")


if __name__ == "__main__":
    main()
