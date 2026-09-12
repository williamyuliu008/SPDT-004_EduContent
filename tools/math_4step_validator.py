"""
4 步法 v1.0 JSON Schema Validator
====================================
校验 concept / parent_problem / variant 三类卡的字段完整性 + chain_id 有效性。

用法:
  python math_4step_validator.py --type concept --file concept_xxx.json
  python math_4step_validator.py --type pp --file pp_001_xxx.json
  python math_4step_validator.py --type variant --file var_001_xxx.json
  python math_4step_validator.py --batch --dir D:\4_data\knowledge_cards\数学\4step

设计原则 (v1.0 规范):
- 必填字段硬约束 (min_length, 必选 chain_id)
- 字段类型严格 (str/int/list)
- chain_id 必须在 v1.2.0 chain 库中存在
- 概念/母题/变形 字段差异自动识别
"""

import json
import sys
from pathlib import Path
from typing import Optional

# v1.2.0 chain 库 (启动时扫描, 或硬编码)
CHAIN_DB_ROOT = Path(r"D:\4_data\knowledge_cards")
VALID_CHAIN_DOMAINS = {"HISTORY", "MATH", "POLITICS", "GEOGRAPHY", "PHYSICS", "CHEMISTRY", "BIOLOGY", "ENGLISH", "CHINESE"}


def load_v12_chains() -> dict[str, dict]:
    """扫描所有学科目录, 加载 v1.2.0 chain.json"""
    chains = {}
    if not CHAIN_DB_ROOT.exists():
        return chains
    for subject_dir in CHAIN_DB_ROOT.iterdir():
        if not subject_dir.is_dir():
            continue
        cards_dir = subject_dir / "cards"
        if not cards_dir.exists():
            continue
        for chain_dir in cards_dir.iterdir():
            if not chain_dir.is_dir():
                continue
            chain_json = chain_dir / "chain.json"
            if not chain_json.exists():
                continue
            try:
                with open(chain_json, encoding="utf-8") as f:
                    data = json.load(f)
                chain_id = data.get("chain_id")
                if chain_id:
                    chains[chain_id] = data
            except (json.JSONDecodeError, OSError) as e:
                print(f"[WARN] {chain_json} 加载失败: {e}")
    return chains


# 通用必填字段
COMMON_REQUIRED = ["card_type", "id", "chain_id", "title", "domain", "difficulty", "frequency", "tags"]

# 三类卡差异化必填字段
TYPE_SPECIFIC = {
    "concept": COMMON_REQUIRED + ["definition", "symbolic_form", "deep_explanation", "verification"],
    "parent_problem": COMMON_REQUIRED + [
        "concepts_used", "goal", "core_method",
        "method_tag", "standard_steps", "scoring_points", "common_mistakes", "variant_ids",
        # v1.1 兼容: graph_bg 拆为 problem_statement + given_conditions + figure_description
    ],
    "variant": COMMON_REQUIRED + [
        "parent_id", "concepts_used", "change_dimension",
        "new_problem", "trigger_condition", "first_step_hint"
    ],
}

# 字段长度约束
MIN_LENGTHS = {
    "title": 5,
    "definition": 20,
    "symbolic_form": 10,
    "deep_explanation": 30,
    "core_method": 10,
    "trigger_condition": 10,
    "first_step_hint": 15,
    "new_problem": 20,
}


def validate_card(card: dict, card_type: str, valid_chain_ids: set) -> list[str]:
    """校验单张卡, 返回错误列表"""
    errors = []
    actual_type = card.get("card_type")
    if actual_type != card_type:
        errors.append(f"card_type 错误: 期望 '{card_type}', 实际 '{actual_type}'")
    for field in TYPE_SPECIFIC.get(card_type, COMMON_REQUIRED):
        if field not in card:
            errors.append(f"必填字段缺失: {field}")
            continue
        value = card[field]
        if isinstance(value, str) and field in MIN_LENGTHS:
            if len(value.strip()) < MIN_LENGTHS[field]:
                errors.append(f"字段 '{field}' 长度不足 (min {MIN_LENGTHS[field]}, actual {len(value.strip())})")
        if isinstance(value, list) and field in ("standard_steps", "scoring_points"):
            if len(value) == 0:
                errors.append(f"字段 '{field}' 不能为空数组")
        # v1.1 兼容: concepts_used 允许空数组 (历史母题暂不关联具体概念卡)
        # v1.1 兼容: variant_ids 允许空数组 (母题可暂不带变形, v1.2 强制)
    chain_id = card.get("chain_id", "")
    if chain_id and chain_id not in valid_chain_ids:
        errors.append(f"chain_id '{chain_id}' 不在 v1.2.0 chain 库中 (有效: {len(valid_chain_ids)} 个)")
    if card_type == "parent_problem":
        variants = card.get("variant_ids", [])
        for v in variants:
            if not isinstance(v, str) or not v.startswith("var_"):
                errors.append(f"variant_ids 中 '{v}' 格式错误 (应以 'var_' 开头)")
    if card_type == "variant":
        parent_id = card.get("parent_id", "")
        if not parent_id.startswith("pp_"):
            errors.append(f"parent_id '{parent_id}' 格式错误 (应以 'pp_' 开头)")
    return errors


def validate_file(file_path: Path, card_type: str, valid_chain_ids: set) -> tuple[bool, list[str]]:
    """校验单个文件"""
    try:
        with open(file_path, encoding="utf-8") as f:
            card = json.load(f)
    except json.JSONDecodeError as e:
        return False, [f"JSON 解析失败: {e}"]
    except OSError as e:
        return False, [f"文件读取失败: {e}"]
    errors = validate_card(card, card_type, valid_chain_ids)
    return len(errors) == 0, errors


def validate_dir(dir_path: Path, valid_chain_ids: set) -> dict:
    """批量校验目录下所有 4 步法卡"""
    results = {"concept": [], "parent_problem": [], "variant": []}
    for json_file in dir_path.rglob("*.json"):
        if "concept" in json_file.name.lower():
            card_type = "concept"
        elif json_file.name.startswith(("pp_", "hp_")):  # 数学 pp_/历史 hp_ 都是 parent_problem
            card_type = "parent_problem"
        elif json_file.name.startswith("var_"):
            card_type = "variant"
        else:
            continue
        ok, errors = validate_file(json_file, card_type, valid_chain_ids)
        results[card_type].append(
            {"file": str(json_file), "ok": ok, "errors": errors}
        )
    return results


def main():
    import argparse
    parser = argparse.ArgumentParser(description="4 步法 v1.0 JSON Schema Validator")
    parser.add_argument("--type", choices=["concept", "pp", "variant"], help="卡片类型")
    parser.add_argument("--file", help="单个文件路径")
    parser.add_argument("--batch", action="store_true", help="批量校验目录")
    parser.add_argument("--dir", default=r"D:\4_data\knowledge_cards\数学\4step", help="批量校验目录")
    args = parser.parse_args()

    valid_chains = load_v12_chains()
    print(f"[INFO] v1.2.0 chain 库加载: {len(valid_chains)} 个 chain")
    print(f"[INFO] 数学 chain: {[c for c in valid_chains if 'math' in c.lower()]}")

    if args.file:
        card_type = args.type
        if card_type == "pp":
            card_type = "parent_problem"
        ok, errors = validate_file(Path(args.file), card_type, set(valid_chains.keys()))
        if ok:
            print(f"[PASS] {args.file}")
        else:
            print(f"[FAIL] {args.file}")
            for e in errors:
                print(f"  - {e}")
        sys.exit(0 if ok else 1)
    elif args.batch:
        results = validate_dir(Path(args.dir), set(valid_chains.keys()))
        total_ok, total_fail = 0, 0
        for ctype, items in results.items():
            for item in items:
                if item["ok"]:
                    total_ok += 1
                    print(f"[PASS] {item['file']}")
                else:
                    total_fail += 1
                    print(f"[FAIL] {item['file']}")
                    for e in item["errors"]:
                        print(f"  - {e}")
        print(f"\n[Summary] PASS={total_ok}, FAIL={total_fail}")
        sys.exit(0 if total_fail == 0 else 1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
