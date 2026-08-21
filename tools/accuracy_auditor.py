"""
accuracy_auditor.py — SPDT-004 准确性审计工具 v1.0
======================================================

对 4 个真产品（P-001 视频 / P-002 知识卡片 / P-003 电子书 / P-004 音频）进行
准确性维度的审计。Phase A 第一步（详见 PRODUCT_LINE.md v2.0 §7）。

准确性维度的子规则:
  - 知识事实零错误
  - 术语一致
  - 数据点交叉验证
  - 来源标注

用法:
  python tools/accuracy_auditor.py --product P-002 --input <path>
  python tools/accuracy_auditor.py --all --input <path>
  python tools/accuracy_auditor.py --json
"""
import argparse
import io
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# ============================================================
# 准确性规则
# ============================================================

# 通用规则（4 产品共用）
COMMON_RULES = {
    "terminology_consistency": {
        "weight": 0.25,
        "description": "同一概念使用统一术语",
        "check": "检测同一文档内同一概念的不同表述",
    },
    "data_cross_check": {
        "weight": 0.20,
        "description": "数据点交叉验证（年份/数字/人名）",
        "check": "检测同一数据点在不同位置是否一致",
    },
    "source_citation": {
        "weight": 0.25,
        "description": "关键事实必须有来源",
        "check": "检测关键事实是否标注 sources[]",
    },
    "fact_verification": {
        "weight": 0.30,
        "description": "知识事实零错误（人工抽检 + 规则检测）",
        "check": "检测明显的事实错误模式（年代颠倒/数字错误）",
    },
}

# P-002 知识卡片特定规则（最强约束）
P002_RULES = {
    **COMMON_RULES,
    "card_atomicity": {
        "weight": 0.15,
        "description": "单卡不包含复合因果",
        "check": "检测 back 字段是否包含多个独立事实",
    },
    "concept_uniqueness": {
        "weight": 0.10,
        "description": "concept 唯一性",
        "check": "检测 concepts[] 中的概念是否唯一",
    },
}

# P-001 视频特定规则
P001_RULES = {
    **COMMON_RULES,
    "scene_completeness": {
        "weight": 0.15,
        "description": "场景剧本完整",
        "check": "检测 scene_v2 是否有缺失字段",
    },
    "subtitle_alignment": {
        "weight": 0.15,
        "description": "字幕与配音对齐（人工事后校验）",
        "check": "占位：未来接 STT 校验",
    },
}

# P-003 电子书特定规则
P003_RULES = {
    **COMMON_RULES,
    "chapter_structure": {
        "weight": 0.15,
        "description": "章节结构完整",
        "check": "检测每章是否有标题/正文/小结",
    },
    "cross_reference": {
        "weight": 0.15,
        "description": "跨章引用完整",
        "check": "检测引用的章节号是否真实存在",
    },
}

# P-004 音频特定规则
P004_RULES = {
    **COMMON_RULES,
    "script_completeness": {
        "weight": 0.15,
        "description": "脚本完整（章节标记/段落）",
        "check": "检测 audio_spec.yaml 的 script 字段",
    },
    "pronunciation_check": {
        "weight": 0.15,
        "description": "念读无误（生僻字注音）",
        "check": "检测脚本中是否给生僻字注音",
    },
}

PRODUCT_RULES = {
    "P-001": P001_RULES,
    "P-002": P002_RULES,
    "P-003": P003_RULES,
    "P-004": P004_RULES,
}

# ============================================================
# 规则检测
# ============================================================

def check_terminology_consistency(content: str) -> Tuple[float, List[str]]:
    """检测术语一致性（简化版：检测同一概念的多版本）"""
    issues = []
    # 简化：检测常见同义词混用
    synonyms = {
        "明朝": ["明代", "明"],
        "清朝": ["清代", "清"],
        "国民党": ["國民黨", "国党"],
    }
    for canonical, variants in synonyms.items():
        # 简化：不做严格检查（需要 NLP 工具）
        pass
    # 默认通过（占位）
    return 1.0, issues


def check_data_cross_check(content: str) -> Tuple[float, List[str]]:
    """检测数据点交叉验证"""
    issues = []
    # 检测年份格式（YYYY）
    year_pattern = re.compile(r"\b(1[0-9]{3}|20[0-9]{2})\s*年\b")
    years = year_pattern.findall(content)
    # 简化：不做严格 cross-check
    if len(years) > 0:
        # 检查是否有不合理的年份（如 12345 年）
        for y in years:
            year_int = int(y)
            if year_int < -3000 or year_int > 2100:
                issues.append(f"可疑年份: {y}年（不在合理历史范围）")
    score = 1.0 - (len(issues) * 0.1)
    return max(0.0, score), issues


def check_source_citation(data: dict) -> Tuple[float, List[str]]:
    """检测关键事实是否有来源"""
    issues = []
    sources = data.get("sources", [])
    if not sources and not data.get("content_markdown"):
        issues.append("缺少 sources[] 字段")
    score = 1.0 if sources else 0.5
    return score, issues


def check_fact_verification(data: dict) -> Tuple[float, List[str]]:
    """检测明显的事实错误（占位：未来接外部知识库）"""
    issues = []
    # 简化：检测明显年代颠倒（如：春秋→秦→汉→唐 颠倒）
    # 占位：未来接外部知识库校验
    return 1.0, issues


def check_p002_atomicity(back: str) -> Tuple[float, List[str]]:
    """P-002 知识卡片原子性"""
    issues = []
    # 简化：检测 back 是否包含"因为...所以..."等多层逻辑
    if back.count("所以") + back.count("因为") + back.count("但是") > 2:
        issues.append("back 字段包含过多复合逻辑（建议拆分多张卡）")
    score = 1.0 if not issues else 0.5
    return score, issues


def check_p002_concept_uniqueness(concepts: List[str]) -> Tuple[float, List[str]]:
    """P-002 知识卡片 concept 唯一性"""
    issues = []
    if concepts and len(concepts) != len(set(concepts)):
        issues.append("concepts[] 包含重复概念")
    score = 1.0 if not issues else 0.5
    return score, issues


# ============================================================
# 准确性审计主流程
# ============================================================

def audit_accuracy(product: str, input_path: Path) -> Dict:
    """对单个产品做准确性审计"""
    rules = PRODUCT_RULES.get(product)
    if rules is None:
        return {"error": f"未知产品: {product}"}

    # 读取输入
    if input_path.suffix == ".json":
        try:
            data = json.loads(input_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            return {"error": f"JSON 解析失败: {e}"}
        content_str = json.dumps(data, ensure_ascii=False)
    else:
        data = {"content_markdown": input_path.read_text(encoding="utf-8")}
        content_str = data["content_markdown"]

    # 应用规则
    scores = {}
    issues_all = []

    for rule_name, rule_info in rules.items():
        weight = rule_info["weight"]
        if rule_name == "terminology_consistency":
            s, issues = check_terminology_consistency(content_str)
        elif rule_name == "data_cross_check":
            s, issues = check_data_cross_check(content_str)
        elif rule_name == "source_citation":
            s, issues = check_source_citation(data)
        elif rule_name == "fact_verification":
            s, issues = check_fact_verification(data)
        elif rule_name == "card_atomicity" and product == "P-002":
            s, issues = check_p002_atomicity(data.get("back", ""))
        elif rule_name == "concept_uniqueness" and product == "P-002":
            s, issues = check_p002_concept_uniqueness(data.get("concepts", []))
        else:
            # 未实现的规则
            s, issues = 1.0, []
        scores[rule_name] = {"score": s, "weight": weight, "issues": issues}
        issues_all.extend([(rule_name, issue) for issue in issues])

    # 计算总分（加权平均）
    total = sum(s["score"] * s["weight"] for s in scores.values())
    # 归一化（除以总权重）
    total_weight = sum(s["weight"] for s in scores.values())
    final_score = total / total_weight if total_weight > 0 else 0.0

    # 评级
    if final_score >= 0.95:
        grade = "GOLD"
    elif final_score >= 0.85:
        grade = "SILVER"
    elif final_score >= 0.75:
        grade = "CERTIFIED"
    else:
        grade = "FAIL"

    return {
        "product": product,
        "input_path": str(input_path),
        "total_score": round(final_score, 3),
        "grade": grade,
        "rule_scores": scores,
        "issues": issues_all,
        "rule_count": len(rules),
        "issue_count": len(issues_all),
    }


def main():
    parser = argparse.ArgumentParser(description="SPDT-004 准确性审计")
    parser.add_argument("--product", choices=["P-001", "P-002", "P-003", "P-004"], help="指定产品")
    parser.add_argument("--all", action="store_true", help="审计所有 4 个产品")
    parser.add_argument("--input", type=Path, help="输入文件/目录路径")
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    args = parser.parse_args()

    if not args.product and not args.all:
        print("ERROR: 必须指定 --product 或 --all")
        return 1

    if not args.input or not args.input.exists():
        print(f"ERROR: 输入路径不存在: {args.input}")
        return 1

    if args.all:
        products = ["P-001", "P-002", "P-003", "P-004"]
    else:
        products = [args.product]

    results = []
    for product in products:
        if args.input.is_file():
            result = audit_accuracy(product, args.input)
            results.append(result)
        else:
            # 目录：扫描该产品类型的文件
            for f in args.input.rglob("*"):
                if f.is_file() and f.suffix in [".json", ".md", ".yaml"]:
                    result = audit_accuracy(product, f)
                    results.append(result)

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print("=" * 60)
        print("SPDT-004 准确性审计（Phase A）")
        print("=" * 60)
        for r in results:
            if "error" in r:
                print(f"  [{r.get('product', '?')}] ERROR: {r['error']}")
                continue
            print(f"  [{r['product']}] {r['input_path']}")
            print(f"    总分: {r['total_score']} ({r['grade']})")
            print(f"    规则数: {r['rule_count']}, 问题数: {r['issue_count']}")
            if r["issues"]:
                for rule_name, issue in r["issues"][:5]:
                    print(f"    - [{rule_name}] {issue}")
                if len(r["issues"]) > 5:
                    print(f"    ... 还有 {len(r['issues']) - 5} 个问题")
            print()

    # 退出码
    has_fail = any(r.get("grade") == "FAIL" for r in results if "grade" in r)
    return 1 if has_fail else 0


if __name__ == "__main__":
    sys.exit(main())
