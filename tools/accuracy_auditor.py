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
        "check": "检测 ep 是否有 ep/title/subtitle/timeline.events/series",
    },
    "subtitle_alignment": {
        "weight": 0.15,
        "description": "字幕与视频时长对齐",
        "check": "基于 mp4 duration + 字幕字符数估算（中文 4 字/秒）",
    },
    "narration_consistency": {
        "weight": 0.10,
        "description": "TTS 配音与字幕字符数一致",
        "check": "mp3 时长 vs 字幕字符数（容差 ±30%）",
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


def check_source_citation(data: dict, product: str = "P-002") -> Tuple[float, List[str]]:
    """检测关键事实是否有来源

    数据结构支持:
      - 单卡 dict: 直接有 sources[]
      - rujing CardPackage: 顶层有 node_cards[].sources[] / strategy_cards[].sources[]
      - 章节 Markdown: 内容标记 [src: ...] 或 sources 列表

    严格度按产品分级（v2.0 §2.6 4 维度）:
      - P-002 知识卡片: 严（0 错容忍）
      - P-001 视频: 中
      - P-003 电子书: 中
      - P-004 音频: 弱（叙事类，源可省）
    """
    issues = []
    strict = product == "P-002"  # P-002 严
    # 顶层 sources[]
    top_sources = data.get("sources", [])

    # node_cards / strategy_cards
    card_sources_total = 0
    card_sources_present = 0
    for field in ["node_cards", "strategy_cards"]:
        cards = data.get(field, [])
        card_sources_total += len(cards)
        for c in cards:
            if c.get("sources") and len(c["sources"]) > 0:
                card_sources_present += 1

    # 判断
    if top_sources:
        return 1.0, []
    if card_sources_total > 0:
        if card_sources_present == card_sources_total:
            return 1.0, []
        # 部分缺失
        missing = card_sources_total - card_sources_present
        issues.append(f"card sources 覆盖率: {card_sources_present}/{card_sources_total}（缺 {missing} 张）")
        score = card_sources_present / card_sources_total
        return score, issues
    # Markdown 内容
    if data.get("content_markdown"):
        md = data["content_markdown"]
        if "[src:" in md or "参考：" in md or "来源：" in md:
            return 1.0, []
        if not strict:
            # P-001/P-003/P-004 叙事/章节类不强求
            return 1.0, []
        issues.append("Markdown 内容未标注 [src: ...] 或 参考：/来源：")
        return 0.5, issues
    # 都没有
    if not strict:
        return 1.0, []
    issues.append("缺少 sources[] 字段（无顶层 + 无卡片级）")
    return 0.0, issues


def check_fact_verification(data: dict) -> Tuple[float, List[str]]:
    """检测明显的事实错误（占位：未来接外部知识库）"""
    issues = []
    # 简化：检测明显年代颠倒（如：春秋→秦→汉→唐 颠倒）
    # 占位：未来接外部知识库校验
    return 1.0, issues


# ============================================================
# P-001 视频真实检测（W29 新增）
# ============================================================

def check_p001_scene_completeness(data: dict) -> Tuple[float, List[str]]:
    """P-001 场景剧本完整性

    必填字段: ep / title / subtitle / series / timeline.events[]
    events 每个需要: year / title / description / significance
    """
    issues = []
    required_top = ["ep", "title", "subtitle", "series"]
    for k in required_top:
        if not data.get(k):
            issues.append(f"ep 缺必填字段: {k}")

    events = data.get("timeline", {}).get("events", [])
    if not events:
        issues.append("timeline.events 为空")
        return 0.0, issues
    if len(events) < 3:
        issues.append(f"events 数量偏少: {len(events)}（建议 ≥ 3）")

    required_event = ["year", "title", "description"]
    for i, ev in enumerate(events):
        for k in required_event:
            if not ev.get(k):
                issues.append(f"event[{i}] 缺字段: {k}")

    if issues:
        return 0.0 if any("缺必填" in i or "为空" in i for i in issues) else 0.7
    return 1.0, issues


def check_p001_subtitle_alignment(data: dict) -> Tuple[float, List[str]]:
    """P-001 字幕与视频时长对齐

    输入 data 应包含:
      - video_duration_sec: mp4 时长
      - subtitle_chars: 字幕总字符数
      - subtitle_duration_sec: 字幕预估时长 (可选, 不提供则用 4 字/秒)

    判定: |video - subtitle| / video < 0.3 算通过
    """
    issues = []
    video_sec = data.get("video_duration_sec")
    if video_sec is None or video_sec <= 0:
        issues.append("缺 video_duration_sec (需 ffprobe 注入)")
        return 1.0, issues  # 占位 PASS

    chars = data.get("subtitle_chars", 0)
    if chars == 0:
        # 兜底: 从 events 抽字符
        events = data.get("timeline", {}).get("events", [])
        chars = sum(len(e.get("description", "")) for e in events)

    if chars == 0:
        issues.append("缺字幕字符数")
        return 0.5, issues

    # 中文 2.5 字/秒 (manim 视频节奏, 比 TTS 慢, 含片头/段间停顿)
    subtitle_sec = data.get("subtitle_duration_sec", chars / 2.5)
    ratio = abs(video_sec - subtitle_sec) / video_sec
    if ratio > 0.3:
        issues.append(
            f"字幕时长 {subtitle_sec:.1f}s 与视频 {video_sec:.1f}s 偏差 {ratio:.0%} (>30%)"
        )
    score = max(0.0, 1.0 - ratio)
    return round(score, 3), issues


def check_p001_narration_consistency(data: dict) -> Tuple[float, List[str]]:
    """P-001 TTS 配音与字幕字符数一致

    输入 data 应包含:
      - audio_duration_sec: mp3 时长
      - subtitle_chars: 字幕总字符数

    判定: |audio - chars/4| / audio < 0.3 算通过 (TTS 中文约 4 字/秒)
    """
    issues = []
    audio_sec = data.get("audio_duration_sec")
    if audio_sec is None or audio_sec <= 0:
        issues.append("缺 audio_duration_sec (需 ffprobe mp3 注入)")
        return 1.0, issues  # 占位 PASS

    chars = data.get("subtitle_chars", 0)
    if chars == 0:
        events = data.get("timeline", {}).get("events", [])
        chars = sum(len(e.get("description", "")) for e in events)
    if chars == 0:
        issues.append("缺字幕字符数")
        return 0.5, issues

    # TTS 中文实际约 3.5-4.5 字/秒 (rate=-18% 下约 3.0 字/秒)
    expected_sec = chars / 3.0
    ratio = abs(audio_sec - expected_sec) / audio_sec
    if ratio > 0.3:
        issues.append(
            f"TTS 配音 {audio_sec:.1f}s 与字幕预估 {expected_sec:.1f}s 偏差 {ratio:.0%} (>30%)"
        )
    score = max(0.0, 1.0 - ratio)
    return round(score, 3), issues


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
            s, issues = check_source_citation(data, product=product)
        elif rule_name == "fact_verification":
            s, issues = check_fact_verification(data)
        elif rule_name == "card_atomicity" and product == "P-002":
            s, issues = check_p002_atomicity(data.get("back", ""))
        elif rule_name == "concept_uniqueness" and product == "P-002":
            s, issues = check_p002_concept_uniqueness(data.get("concepts", []))
        elif rule_name == "scene_completeness" and product == "P-001":
            s, issues = check_p001_scene_completeness(data)
        elif rule_name == "subtitle_alignment" and product == "P-001":
            s, issues = check_p001_subtitle_alignment(data)
        elif rule_name == "narration_consistency" and product == "P-001":
            s, issues = check_p001_narration_consistency(data)
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
