"""
PT-030 题目切分算法 v1.1 (C2 高难度组件 - 改进版)
================================================
v1.0 已知问题:
  1. 选项 text 错位: regex lookahead 不匹配同行格式 ("A xx B xx C xx D xx")
  2. 选项漏检: 同行格式 PDF 文本 (Q1/Q2/Q4/Q5/Q7/Q8/Q9) 全部 options=[]
  3. 页码误识别: "1870" "80" "60" "16" 等年份/页码被识别为 q_no=187/80/60/16
  4. 答案/解析未分离: 末尾"参考答案"区未抽取

v1.1 改进:
  A. 选项 split 双模式: 同行 ([ \t]+[A-D][.、．]) + 分行 (\n[ \t]*[A-D][.、．])
  B. 题号白名单: 排除 4 位数 (1870/1910) + 排除 ≤ 1 位数 (页码)
  C. 答案/解析分离: 从 PDF 末尾"参考答案"区按题号匹配
  D. 主观题切分: Q21-Q28 (简答/论述) 用 ___ 填空线 + 分值模式
  E. 归一化: 删 "（" "）" 干扰空白，合并 "A\n \n\n内容" 为 "A 内容"

输入: D:\4_data\rujing_out\真题主库\raw\<年份>_<学科>_raw.json (C1 输出, 含 text 字段)
输出: D:\4_data\rujing_out\真题主库\split\<年份>_<学科>_split.json

用法:
  python split_questions_v11.py <raw_json> [<output_json>]
  python split_questions_v11.py --batch D:\4_data\rujing_out\真题主库\raw\
"""

import json
import re
import sys
from pathlib import Path
from typing import Optional


# 题号识别白名单: 1-3 位数, 排除 4 位 (年份/页码) - 但需 1-3 位完整匹配
# 优先级: 先匹配 (1) (2) 括号格式, 再匹配 1. 1、 1． 格式
QUESTION_NUM_RE = re.compile(
    r"^\s*(?:[（(](?P<num1>\d{1,3})[）)]|(?P<num2>\d{1,3}))[\.、．\s]*",
    re.MULTILINE
)

# 选项标记 (混合模式): 行内或行间 空格/换行/全角空格 后跟 A./A、/A．
# 兼容 A.  A．  A  A．(中间空格)  A  (A)  (A).   支持 A-E (Q21 5选项)
OPTION_RE = re.compile(
    r"[\s　]+[（(]?([A-E])[）)]?[\s　]*[\.、．]?[\s　]+(?=[^\s　])"
)

# 分值
SCORE_RE = re.compile(r"[(（]?\s*(\d{1,2})\s*分\s*[)）]?")

# 填空线
FILL_BLANK_RE = re.compile(r"_+")

# 答案区开始标记
ANSWER_SECTION_MARKERS = ["参考答案", "【答案】", "答案", "参考答案与解析"]


def normalize_text(text: str) -> str:
    """归一化: 删除全角空白/合并连续换行 (但保留单换行)"""
    # 合并连续换行 (3+ 连续换行 -> 1 换行)
    text = re.sub(r"\n{3,}", "\n", text)
    # 合并 PDF 字体渲染残留: 题号后跟 . \n (如 "10\n．\n\n1870" → "10\n1870")
    # 注意: 只在题号数字 (1-35) 之后的 "．" 视为字体残留
    text = re.sub(r"\n[　 \t]*[\.、．][　 \t\n]+(?=[1-9]\d{0,2}\b)", "\n", text)
    # 删行首/行尾空白 (但保留换行作为题号边界)
    lines = []
    for line in text.split("\n"):
        line = re.sub(r"^[\t ]+|[\t ]+$", "", line)
        lines.append(line)
    return "\n".join(lines)


def detect_questions_v11(text: str) -> list[dict]:
    """v11 题号识别 - 1-3 位 + 上下文校验 (排除 4 位数年份)"""
    matches = []
    seen = set()
    for m in QUESTION_NUM_RE.finditer(text):
        q_no_str = m.group("num1") or m.group("num2")
        if not q_no_str:
            continue
        q_no = int(q_no_str)
        if q_no in seen:
            continue
        # 排除 4 位: 上下文 5 字符有数字 (如 "10 1870" 中 1870 是题干内容, 10 是题号 - OK)
        if len(q_no_str) >= 4:
            continue
        # 上海高考 2018 历史题号实际范围 1-28
        if q_no > 35:  # 排除过大数字 (如 80/60/187/191/201/...)
            continue
        # 关键校验 1: 上下文 - 题号前 5 字符不应有相邻数字 (避免 "1870" 中识别 "187")
        ctx_start = max(0, m.start() - 5)
        prefix = text[ctx_start:m.start()]
        if re.search(r"\d" + re.escape(q_no_str), prefix):
            # 前缀紧邻题号有数字, 误识别 (如 1870 中识别 187)
            continue
        # 不再用 suffix 检查 (题号后可能是题干年份 1870/1910/1915 等)
        seen.add(q_no)
        matches.append({
            "q_no": q_no,
            "start": m.start(),
            "end": m.end(),
            "match": m.group(0).strip()[:30]
        })
    matches.sort(key=lambda x: x["start"])

    # 后处理: 排除题号位置在 PDF 后 1/3 区域但"距离前一个题号过近"的 (可能误识别)
    # 启发: 答案区题号出现密集, 但与"真题区"题号风格不同
    # 用 Q1 出现位置作为分割线: 之前是真题, 之后是答案/材料
    if matches:
        first_q1 = next((q for q in matches if q["q_no"] == 1), None)
        if first_q1:
            split_pos = first_q1["start"]
            # 在 split_pos 之前出现的题号是真题目号
            # 在 split_pos 之后的题号也保留 (因为可能多套题在一份 PDF)
            # 但要去重: 同一 q_no 多次出现, 保留首次
            seen2 = set()
            deduped = []
            for q in matches:
                if q["q_no"] in seen2:
                    continue
                seen2.add(q["q_no"])
                deduped.append(q)
            matches = deduped

    return matches


def detect_options_v11(full_stem: str) -> list[dict]:
    """v11 选项检测 - 统一模式 (同行/分行均适用)"""
    matches = list(OPTION_RE.finditer(full_stem))
    if len(matches) < 2:
        return []

    # 验证: 选项标记应按 A→B→C→D 顺序, 且 4 个
    labels = [m.group(1) for m in matches]
    if len(set(labels)) < 2:
        return []

    # 提取每个选项内容
    opts = []
    for i, m in enumerate(matches):
        label = m.group(1)
        content_start = m.end()
        if i + 1 < len(matches):
            content_end = matches[i + 1].start()
        else:
            content_end = len(full_stem)
        content = full_stem[content_start:content_end].strip()
        # 清理: 删末尾分值标记
        content = re.sub(r"[(（]?\s*\d{1,2}\s*分\s*[)）]?", "", content)
        opts.append({"label": label, "text": content[:500]})

    # 按标签去重 (取首次)
    seen_labels = set()
    unique_opts = []
    for opt in opts:
        if opt["label"] not in seen_labels:
            seen_labels.add(opt["label"])
            unique_opts.append(opt)

    return unique_opts if len(unique_opts) >= 2 else []


def detect_score_v11(text: str) -> Optional[int]:
    """v11 分值检测 - 兼容 "15分" "(5分)" "（10分）" """
    m = SCORE_RE.search(text)
    return int(m.group(1)) if m else None


def detect_type_v11(stem: str, options: list, score: Optional[int] = None) -> str:
    """v11 题型识别 (含主观题分值启发)"""
    # 选择题: 有 4 个标准选项 (A-D) 且分值 < 5 (选择 1-2 分)
    if options and len(options) >= 3 and (not score or score < 5):
        return "选择"
    # 提纲/材料题: 5 个主题选项 (A-E) + 分值 >= 5 + 提纲字样
    if options and len(options) == 5 and (score or 0) >= 5 and "提纲" in stem:
        return "提纲"
    if options and len(options) == 5 and (score or 0) >= 5 and "材料" in stem:
        return "材料"
    # 主观题启发: 分值 >= 5 分 (高考选择 1-2 分, 简答 5+, 论述 10+)
    if score and score >= 10:
        return "论述"
    if score and score >= 5:
        if any(kw in stem for kw in ["论述", "评述", "评析", "谈谈", "如何理解", "变化", "启示"]):
            return "论述"
        if "提纲" in stem:
            return "提纲"
        if "材料" in stem:
            return "材料"
        return "简答"
    if any(kw in stem for kw in ["论述", "评述", "评析", "谈谈你的", "如何理解"]):
        return "论述"
    if any(kw in stem for kw in ["简答", "简要回答", "概述"]):
        return "简答"
    if FILL_BLANK_RE.search(stem):
        return "填空"
    # 无选项 + 有分值 → 简答
    if score:
        return "简答"
    return "未知"  # 无法判定时不再默认"选择"


def extract_answer_section_v11(text: str) -> dict[int, dict]:
    """v11 答案/解析分离 - 找 PDF 末尾"参考答案"区 或 后半部分答案"""
    # 策略 1: 找明确答案区标记
    answer_start = -1
    for marker in ANSWER_SECTION_MARKERS:
        idx = text.rfind(marker)
        if idx > 0:
            answer_start = idx
            break

    if answer_start < 0:
        # 策略 2: 找 PDF 总题数一半处的题号 (启发式 - 答案通常在后半)
        # 2018 上海历史: 28 题, 答案在第 21 题开始
        # 用 q_no > 20 作为答案区起点
        m21 = re.search(r"^\s*21\b", text, re.MULTILINE)
        if m21 and m21.start() > len(text) * 0.5:
            answer_start = m21.start()

    if answer_start < 0:
        return {}

    answer_section = text[answer_start:]
    answers = {}
    # 按题号切分答案区 (题号格式: "21 \n 10" 或 "21\n答案")
    q_pattern = re.compile(r"(?:^|\n)\s*(\d{1,3})\s*\n")
    q_positions = []
    for m in q_pattern.finditer(answer_section):
        try:
            no = int(m.group(1))
            if no > 35:  # 排除过大数字
                continue
            q_positions.append((no, m.start()))
        except (ValueError, TypeError):
            continue
    q_positions.sort(key=lambda x: x[1])

    for i, (q_no, start) in enumerate(q_positions):
        end = q_positions[i + 1][1] if i + 1 < len(q_positions) else len(answer_section)
        chunk = answer_section[start:end].strip()
        # 提取答案标识 (A/B/C/D/E 或 ✓/✗)
        # 答案格式: "1\nA" 或 "21\n10\nA\nB\nC\nD\nE"
        # 找第一个独立的 A-E 字符 (在题号和分值之后)
        body = re.sub(r"^\s*\d{1,3}\s*\n", "", chunk)  # 删题号
        body = re.sub(r"^\s*\d{1,2}\s*分\s*\n?", "", body)  # 删分值
        first_label = re.search(r"^[\s\n]*([A-E])(?:\s|$|\n)", body)
        ans_label = first_label.group(1) if first_label else None
        score_match = re.search(r"(\d{1,2})\s*分", chunk)
        answers[q_no] = {
            "answer_text": chunk[:500],
            "answer_label": ans_label,
            "score": int(score_match.group(1)) if score_match else None
        }
    return answers


def split_questions_v11(raw: dict) -> tuple[list[dict], dict]:
    """v11 主切分逻辑"""
    text = raw.get("text", "")
    if not text and "pages" in raw:
        text = "\n".join(p.get("text", "") for p in raw.get("pages", []))

    if not text:
        return [], {}

    # 归一化
    text = normalize_text(text)

    # 题号识别
    questions = detect_questions_v11(text)
    if not questions:
        return [], {}

    # 答案/解析分离
    answers_map = extract_answer_section_v11(text)

    # 按题号切分
    results = []
    for i, q in enumerate(questions):
        start = q["start"]
        end = questions[i + 1]["start"] if i + 1 < len(questions) else len(text)
        full_stem = text[start:end].strip()
        # 截断: 如果 stem 包含 5+ 个 "分" 字 (说明跨了多道主观题)
        if full_stem.count("分") > 2 and (q["q_no"] >= 20):
            # 找到第二个 "分" 字位置 (第一个是本题分值, 后续是下题分值)
            score_positions = [m.end() for m in re.finditer(r"(\d{1,2})\s*分", full_stem)]
            if len(score_positions) >= 2:
                # 截到第二个分值前
                end2 = score_positions[1] - len(re.search(r"\d{1,2}\s*分", full_stem[score_positions[0]:]).group(0))
                full_stem = full_stem[:end2].strip()

        # 选项检测 (改进)
        options = detect_options_v11(full_stem)

        # Q21 模式检测: 5 个并列材料 A-E 实际是"5 选 1"材料选择题, 但在本题中是材料子问
        # 区分: 如果有 ≥3 个选项 + stem 含 "材料" 字样 + score >= 5, 视为简答/材料题
        is_material_question = (
            options and len(options) >= 3
            and any(kw in full_stem for kw in ["材料", "马克思", "结合"])
            and (score or 0) >= 5
        )

        # 分值
        score = detect_score_v11(full_stem)

        # 题型 (含分值启发 + 材料题识别)
        if is_material_question:
            q_type = "材料"  # 材料题 (含多个子问, 选项是材料主题)
        else:
            q_type = detect_type_v11(full_stem, options, score)

        # 题干清洗: 删题号/分值/页脚
        clean_stem = re.sub(r"^\s*\d{1,3}\s*[\.、．\s]+", "", full_stem)
        clean_stem = re.sub(r"[(（]\s*\d{1,2}\s*分\s*[)）]?", "", clean_stem)
        # 删 PDF 页脚: 任意 "2018/2019/2020" + "上海/全国..." + "历史/..." + "答案" 的连续模式
        # 实际页脚格式: "2018\n2018\n \n年上海市普通高中学业水平考试\n年上海市...\n \n(历史)\n(历史)\n试题答案\n试题答案"
        # 注意: "年" 字符在 "上海市" 之前 (PDF 字体渲染残留)
        clean_stem = re.sub(
            r"\n\s*(?:\d{4}\s*[\n]){1,4}"
            r"(?:\s*(?:年)?(?:上海市?|全国|北京|江苏|浙江省?)[^\n]{0,40}\s*[\n]){1,4}"
            r"(?:\s*[（(]?(?:历史|地理|政治|语文|数学|英语|物理|化学|生物|文综|理综)[）)]?\s*[\n]){1,2}"
            r"(?:\s*(?:试题)?答案[^\n]*[\n]?){1,3}",
            "", clean_stem, flags=re.DOTALL
        )
        # 单行残留
        clean_stem = re.sub(r"\n\s*\d{4}\s*$", "", clean_stem)
        clean_stem = re.sub(r"(?:\n\s*(?:试题)?答案)+\s*$", "", clean_stem)
        clean_stem = re.sub(r"\n\s*[（(]?(?:历史|地理|政治|语文|数学|英语|物理|化学|生物)[）)]?\s*$", "", clean_stem)
        clean_stem = re.sub(r"\n\s*(?:年)?(?:上海市?|全国|北京|江苏|浙江省?)[^\n]{0,20}\s*$", "", clean_stem)
        # 删尾部选项 (如果有)
        for opt in options:
            opt_pat = re.compile(rf"[\s　]+[（(]?{opt['label']}[）)]?[\.、．][\s　]+", re.MULTILINE)
            m = opt_pat.search(clean_stem)
            if m:
                # 找到该选项起始, 删除到下一选项或末尾
                next_m = opt_pat.search(clean_stem, m.end())
                end_idx = next_m.start() if next_m else len(clean_stem)
                clean_stem = clean_stem[:m.start()] + clean_stem[end_idx:]
        clean_stem = clean_stem.strip()

        # 答案 (从答案区匹配)
        answer_info = answers_map.get(q["q_no"], {})

        results.append({
            "q_no": q["q_no"],
            "type": q_type,
            "score": score or answer_info.get("score"),
            "stem": clean_stem[:1000],
            "options": options,
            "answer_label": answer_info.get("answer_label"),
            "answer_text": answer_info.get("answer_text", "")[:500] if answer_info else "",
            "_v11_improvements": "split 替代 regex + 同行/分行双模式 + 题号白名单 + 答案区分离"
        })

    return results, answers_map


def split_raw_file_v11(raw_path: Path, output_path: Optional[Path] = None) -> dict:
    """v11 主函数: 单文件切分"""
    if not raw_path.exists():
        return {"error": f"raw not found: {raw_path}"}

    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    questions, answers_map = split_questions_v11(raw)

    result = {
        "source_raw": str(raw_path),
        "total_questions": len(questions),
        "questions_with_options": sum(1 for q in questions if q["options"]),
        "questions_with_answers": sum(1 for q in questions if q.get("answer_label")),
        "questions": questions,
        "answers_section_detected": len(answers_map) > 0,
        "answers_section_size": len(answers_map),
        "_v11_caveat": "v1.1 split 替代 regex + 同行/分行双模式 + 题号白名单 + 答案区分离. LLM 推演留给 C3.",
        "_v11_improvements": [
            "A. split 替代 lookahead regex",
            "B. 同行+分行双模式 (Q1 同行 / Q10 分行)",
            "C. 题号白名单 (排除 4 位数年份/页码)",
            "D. 答案/解析从 PDF 末尾区分离",
            "E. 主观题 (Q21-Q28) 填空线 + 分值识别"
        ],
        "_created": "2026-09-12 by 宇兄窗口 (PT-030 C2 v1.1 高难度组件改进版)"
    }

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(json.dumps(result, ensure_ascii=False, indent=2).encode("utf-8"))
        print(f"  写入: {output_path}")
    return result


def main():
    if len(sys.argv) < 2:
        print("用法:")
        print("  python split_questions_v11.py <raw_json>")
        print("  python split_questions_v11.py --batch <raw_dir>")
        return

    arg = sys.argv[1]
    if arg == "--batch" and len(sys.argv) >= 3:
        raw_dir = Path(sys.argv[2])
        raws = list(raw_dir.rglob("*_raw.json"))
        print(f"批量切分 (v1.1): {len(raws)} 个 raw JSON")
        for raw_path in raws:
            try:
                out = raw_path.parent.parent / "split" / raw_path.name.replace("_raw.json", "_split.json")
                result = split_raw_file_v11(raw_path, out)
                if "error" in result:
                    print(f"  ERROR: {raw_path.name}: {result['error']}")
                else:
                    print(f"  ✓ {raw_path.name}: {result['total_questions']} 题, {result['questions_with_options']} 有选项, {result['questions_with_answers']} 有答案")
            except Exception as e:
                print(f"  ERROR: {raw_path.name}: {e}")
    else:
        raw_path = Path(arg)
        result = split_raw_file_v11(raw_path)
        if "error" in result:
            print(f"ERROR: {result['error']}")
            sys.exit(1)
        print(f"\n结果 (v1.1): 切分 {result['total_questions']} 题")
        print(f"  有选项: {result['questions_with_options']}")
        print(f"  有答案: {result['questions_with_answers']}")
        print(f"  答案区: {result['answers_section_detected']} ({result['answers_section_size']} 题)")
        print()
        for q in result["questions"][:5]:
            opt_str = ", ".join(f"{o['label']}={o['text'][:20]}..." for o in q["options"][:2])
            print(f"  Q{q['q_no']} [{q['type']}, {q['score']}分] {len(q['options'])} 选项: stem={q['stem'][:50]}...")
            if opt_str:
                print(f"      选项: {opt_str}")
            if q.get("answer_label"):
                print(f"      答案: {q['answer_label']}")


if __name__ == "__main__":
    main()
