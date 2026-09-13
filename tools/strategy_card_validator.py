"""
策略卡片 v1.0 验证器
====================
基于 math_4step_validator.py 的设计, 验证策略卡片结构 + 字段.

用法:
  python strategy_card_validator.py <card_json> [<card_json> ...]
  python strategy_card_validator.py --batch <dir_path>
  python strategy_card_validator.py --dir D:\\4_data\\knowledge_cards\\策略\\数学
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any


# 5 核心字段 (两窗口禁区)
CORE_FIELDS = ["card_id", "chain_id", "schema_version", "SOP", "验收标准"]

# 11 扩展字段 (宇兄端可加)
EXTENDED_FIELDS = [
    "source_type", "source_ref", "original_problem_id", "problem_statement",
    "given_conditions", "figure_description", "figure_ref", "figure_type",
    "intuition", "thinking_path", "key_insight"
]

# display_target v3.0 必填
DISPLAY_TARGET_FIELD = "display_target"

# schema 版本
SUPPORTED_VERSIONS = ["v1.0"]

# 学科白名单 (上海文科艺术生)
ALLOWED_SUBJECTS = ["语文", "数学", "英语", "历史", "地理", "政治", "书法", "元学习"]

# source_type 白名单
ALLOWED_SOURCE_TYPES = [
    "教学法", "学科方法论", "元学习", "应试策略", "记忆术", "心理建设"
]


class ValidationError:
    def __init__(self, level: str, field: str, message: str):
        self.level = level  # "error" / "warning" / "info"
        self.field = field
        self.message = message

    def __str__(self):
        icon = {"error": "[E]", "warning": "[W]", "info": "[I]"}.get(self.level, "[?]")
        return f"{icon} {self.field}: {self.message}"


def validate_card(card: dict) -> list[ValidationError]:
    """验证单张策略卡片"""
    errors = []

    # 1. 5 核心字段必填
    for f in CORE_FIELDS:
        if f not in card or not card[f]:
            errors.append(ValidationError("error", f, "5 核心字段必填 (两窗口禁区)"))

    # 2. schema_version 必须支持
    sv = card.get("schema_version", "")
    if sv not in SUPPORTED_VERSIONS:
        errors.append(ValidationError("error", "schema_version", f"不支持 {sv}, 应为 {SUPPORTED_VERSIONS}"))

    # 3. card_id 格式: strategy_<subject>_<3位编号> 或 meta_<3位编号>
    cid = card.get("card_id", "")
    if cid:
        import re
        if not re.match(r"^(strategy_[a-z]+_\d{3}|meta_\d{3})$", cid):
            errors.append(ValidationError("warning", "card_id", f"格式 {cid} 建议 strategy_<subject>_<3位编号> 或 meta_<3位编号>"))

    # 4. chain_id 格式
    chain = card.get("chain_id", "")
    if chain:
        if not re.match(r"^([a-z]+_(strategy|learning)_[a-z_]+|meta_(learning|exam)_[a-z_]+)$", chain):
            errors.append(ValidationError("warning", "chain_id", f"格式 {chain} 建议 <subject>_strategy_<method> 或 meta_<topic>"))

    # 5. display_target 必填 + 元素在白名单
    if DISPLAY_TARGET_FIELD not in card:
        errors.append(ValidationError("error", DISPLAY_TARGET_FIELD, "v3.0 必填"))
    else:
        dt = card[DISPLAY_TARGET_FIELD]
        if not isinstance(dt, list) or not dt:
            errors.append(ValidationError("error", DISPLAY_TARGET_FIELD, "应为非空列表"))
        else:
            for target in dt:
                if target not in ["RUJING", "学习中心"]:
                    errors.append(ValidationError("error", DISPLAY_TARGET_FIELD, f"未知 target {target}"))

    # 6. source_type 必填 + 白名单
    st = card.get("source_type", "")
    if not st:
        errors.append(ValidationError("warning", "source_type", "建议填: 教学法/学科方法论/元学习/..."))
    elif st not in ALLOWED_SOURCE_TYPES:
        errors.append(ValidationError("warning", "source_type", f"非标准 {st}, 应在 {ALLOWED_SOURCE_TYPES}"))

    # 7. 学科范围检查 (从 card_id 推断)
    if cid and cid.startswith("strategy_"):
        parts = cid.split("_")
        if len(parts) >= 2:
            subject_code = parts[1]
            subject_map = {
                "chinese": "语文", "math": "数学", "english": "英语",
                "history": "历史", "geo": "地理", "politics": "政治",
                "calligraphy": "书法", "meta": "元学习"
            }
            subject = subject_map.get(subject_code)
            if subject and subject not in ALLOWED_SUBJECTS:
                errors.append(ValidationError("error", "card_id", f"学科 {subject} 不在白名单 (排除物理化学生物)"))
            elif not subject:
                errors.append(ValidationError("warning", "card_id", f"学科代码 {subject_code} 未知, 应在 {list(subject_map.keys())}"))

    # 8. SOP 长度检查 (5 步内)
    sop = card.get("SOP", "")
    if sop:
        # 只按 "→" 切分, 不按 "." 切 (因为步骤内可能有"国家/企业/个人"等含点字符)
        steps = [s for s in sop.split("→") if s.strip()]
        if len(steps) > 7:
            errors.append(ValidationError("warning", "SOP", f"步骤 {len(steps)} 偏多, 建议 5 步内"))

    # 9. 验收标准检查 (有可量化指标)
    ac = card.get("验收标准", "")
    if ac and not any(kw in ac for kw in ["能", "会", "正确", "通过", "完成", "解决", "答对"]):
        errors.append(ValidationError("info", "验收标准", "建议含可量化动词 (能/会/正确/通过)"))

    # 10. key_insight 一句话
    ki = card.get("key_insight", "")
    if ki and len(ki) > 200:
        errors.append(ValidationError("warning", "key_insight", f"长度 {len(ki)} 偏长, 建议 1 句话"))

    return errors


def validate_file(json_path: Path) -> tuple[str, list[ValidationError]]:
    """验证单张卡片文件"""
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            card = json.load(f)
    except Exception as e:
        return f"ERROR: {e}", [ValidationError("error", "FILE", f"读取失败: {e}")]

    errors = validate_card(card)
    return json_path.name, errors


def main():
    parser = argparse.ArgumentParser(
        description="策略卡片 v1.0 验证器 (宇兄端 ↔ 雪薇端)"
    )
    parser.add_argument("paths", nargs="*", help="单张/多张卡片 JSON 路径")
    parser.add_argument("--batch", help="批量验证目录下所有 JSON")
    parser.add_argument("--dir", help="验证指定目录下所有 JSON")
    args = parser.parse_args()

    targets = []
    if args.paths:
        targets = [Path(p) for p in args.paths]
    elif args.batch:
        targets = list(Path(args.batch).rglob("*.json"))
    elif args.dir:
        targets = list(Path(args.dir).rglob("*.json"))
    else:
        parser.print_help()
        return 1

    if not targets:
        print("未找到 JSON 文件")
        return 1

    total_errors = 0
    total_warnings = 0
    pass_count = 0

    for t in targets:
        name, errors = validate_file(t)
        e_n = sum(1 for e in errors if e.level == "error")
        w_n = sum(1 for e in errors if e.level == "warning")
        total_errors += e_n
        total_warnings += w_n
        if e_n == 0:
            pass_count += 1
            print(f"[PASS] {name}: {len(errors)} 条 (E={e_n}, W={w_n})")
            for e in errors:
                print(f"       {e}")
        else:
            print(f"[FAIL] {name}: {len(errors)} 条 (E={e_n}, W={w_n})")
            for e in errors:
                print(f"       {e}")

    print()
    print(f"汇总: {len(targets)} 张, PASS={pass_count}, FAIL={len(targets)-pass_count}, E={total_errors}, W={total_warnings}")

    if total_errors > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
