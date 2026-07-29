# -*- coding: utf-8 -*-
"""
为所有 KB_CAFA_S* 条目：
1. 规范化 exam_tips 的 key 名（中文 → 英文，兼容稳定）
2. 添加 example_questions（典型试题），基于 concept + scoring_points 规则生成
"""
import json
from pathlib import Path

KB_PATH = Path(r"D:\92_products\SPDT-004_EduContent\PT-037_AdaptivePrepPlatform\_03_subject_packs\cafa_calligraphy_2026\knowledge\kb_vocab_enhanced.json")

with open(KB_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

# ── 基于 scoring_points 生成典型试题 ─────────────────────────────────────────
def make_example_questions(concept, tips):
    """根据已有 scoring_points 生成典型试题示例"""
    sp = tips.get("scoring_points", []) or tips.get("scoring_points", "")
    if isinstance(sp, str):
        sp = [sp]
    q_list = []

    # 题型1: 名词解释（几乎所有条目都有）
    q_list.append(
        f"名词解释：{concept}。\n"
        f"【参考答案要点】{sp[0] if sp else '需结合定义、历史背景和艺术特点作答'}"
    )

    # 题型2: 判断/填空（若 scoring_points 包含朝代/时间/位置信息）
    for pt in sp:
        if any(k in pt for k in ["朝代", "年代", "时间", "第一", "第二", "第三", "首位", "创始人", "提出者"]):
            q_list.append(
                f"填空题：请补充以下关于「{concept}」的信息：{pt.split('（')[0] if '（' in pt else pt[:30]}……"
            )
            break

    # 题型3: 比较题（若涉及两人/两派/两体）
    if "与" in concept or "和" in concept or "vs" in concept.lower() or "比较" in concept:
        parts = [p.strip() for p in concept.replace("与", "||").replace("和", "||").split("||")]
        if len(parts) >= 2:
            q_list.append(
                f"比较题：比较{parts[0]}与{parts[1]}的异同。\n"
                f"【参考答案】需从历史背景、技法特点、艺术成就三方面展开对比。"
            )

    # 题型4: 论述题（若考频高或有延伸考点）
    ext_keys = ["extended_topics", "延伸考点", "\u5ef6\u4f38\u8003\u70b9"]
    ext = None
    for k in ext_keys:
        if tips.get(k):
            ext = tips[k]
            break
    if ext and isinstance(ext, list) and len(ext) > 0:
        q_list.append(
            f"论述题：试述{concept}在书法史上的地位与影响。\n"
            f"【参考答案要点】{ext[0] if ext else '需结合历史脉络和艺术特征展开论述'}"
        )

    return q_list[:3]  # 最多3道典型题

# ── 规范化 exam_tips key ──────────────────────────────────────────────────────
KEY_MAP = {
    "记忆口诀": "mnemonics",
    "延伸考点": "extended_topics",
    "scoring_points": "scoring_points",
    "common_mistakes": "common_mistakes",
}

def normalize_tips(tips):
    """将 exam_tips 中的中文 key 映射为英文 key"""
    if not tips or not isinstance(tips, dict):
        return tips
    normalized = {}
    for k, v in tips.items():
        new_k = KEY_MAP.get(k, k)
        normalized[new_k] = v
    return normalized

# ── 批量处理 ────────────────────────────────────────────────────────────────
count = 0
for mod_data in data["modules"].values():
    for items in mod_data.values():
        for item in items:
            if not item.get("kb_id", "").startswith("KB_CAFA_S"):
                continue

            # 1. 规范化 exam_tips
            raw_tips = item.get("exam_tips", {})
            if raw_tips and isinstance(raw_tips, dict):
                item["exam_tips"] = normalize_tips(raw_tips)

            # 2. 添加 example_questions（跳过已有的）
            if not item.get("example_questions"):
                concept = item.get("concept", "")
                tips = item.get("exam_tips", {})
                item["example_questions"] = make_example_questions(concept, tips)
                count += 1

print(f"[done] 规范化了 {count} 条的 exam_tips 并添加了 example_questions")

with open(KB_PATH, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f"[saved] {KB_PATH}")
