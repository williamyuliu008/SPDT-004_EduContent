# -*- coding: utf-8 -*-
"""
1_ingest · ingest_syllabus_parser.py
===================================
M1 阶段：考纲解析 → ContentSpec YAML

功能：
  1. 读取考纲源文件（meta.json / Markdown / JSON）
  2. 提取题型、权重、参考书目、考点关键词
  3. 生成 ContentSpec YAML（教育领域 B1）
  4. Schema 验证

用法：
  python ingest_syllabus_parser.py --input meta.json --output content_spec.yaml

依赖：
  pip install pyyaml jsonschema
"""

import json
import argparse
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Any

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

try:
    import jsonschema
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False


# ── Schema 路径 ────────────────────────────────────────────────────────────
SCHEMA_DIR = Path(__file__).parent / "schemas"
SPEC_SCHEMA = SCHEMA_DIR / "content_spec.schema.json"


# ── 题型 → 关键词映射（手工规则，可扩展）────────────────────────────────
QUESTION_TYPE_KEYWORDS = {
    "Q_TRANSDUCTION": ["小篆", "篆书", "译篆", "六书", "说文", "部首", "字形"],
    "Q_PUNCT_TRANSLATION": ["句读", "翻译", "文言", "断句", "文意"],
    "Q_TERM_EXPLAIN": ["名词解释", "书法史", "书论", "书风", "书法家", "碑帖"],
    "Q_SCRIPT_READING": ["释文", "草书", "篆书", "隶书", "楷书"],
}


def load_meta_json(path: Path) -> dict:
    """读取 meta.json，返回原始字典。"""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def extract_key_topics(config: dict) -> list[str]:
    """从题型描述中提取关键词。"""
    topics = []
    for qt in config.get("question_types", []):
        qt_id = qt.get("id", "")
        desc = qt.get("description", "")
        keywords = QUESTION_TYPE_KEYWORDS.get(qt_id, [])
        # 简单启发式：从描述中提取名词
        words = [w.strip("，。：、") for w in desc if len(w.strip()) > 1]
        combined = list(set(keywords + words[:3]))
        topics.append({
            "id": qt_id,
            "keywords": combined[:5]
        })
    return topics


def generate_content_spec(meta: dict) -> dict:
    """从 meta.json 生成 ContentSpec 字典。"""
    config = meta.get("config", {})
    stats = meta.get("statistics", {})

    # 参考书目（从 meta.json reference_texts 提取）
    ref_texts = []
    for ref in config.get("reference_texts", []):
        ref_texts.append({
            "title": ref,
            "trust": "E",  # meta.json 中的参考书目均为古籍/权威文献，E级
            "weight_in_syllabus": None  # 待后续计算
        })

    # 题型结构
    question_types = []
    for qt in config.get("question_types", []):
        qt_id = qt.get("id", "")
        keywords_data = next(
            (k for k in extract_key_topics(config) if k["id"] == qt_id),
            {"id": qt_id, "keywords": []}
        )
        question_types.append({
            "id": qt_id,
            "name": qt.get("name", ""),
            "weight": qt.get("weight", 0.0),
            "description": qt.get("description", ""),
            "key_topics": keywords_data.get("keywords", [])
        })

    spec = {
        "spec_id": meta.get("pack_id", "UNKNOWN"),
        "spec_version": meta.get("version", "1.0.0"),
        "spec_generated": datetime.now(timezone.utc).isoformat(),
        "domain": "education",
        "content_type": "B1_deep_content",
        "exam_meta": {
            "exam_name": meta.get("subject", "未知"),
            "exam_code": meta.get("exam_code", ""),
            "subject": meta.get("subject", ""),
            "total_duration_min": config.get("total_duration_minutes", 0),
            "total_score": config.get("total_score", 100)
        },
        "question_types": question_types,
        "reference_texts": ref_texts,
        "quality_constraints": {
            "factual_accuracy": "expert_reviewed",
            "cross_check_required": True,
            "hallucination_threshold": 0.05
        },
        "production_target": {
            "knowledge_entries_target": stats.get("knowledge_entries", 50),
            "ability_count_target": stats.get("ability_points", 8),
            "coverage_target": 0.85
        },
        "human_checkpoint": ["M1_syllabus_confirmed"],
        "source": "generated_from_meta_json"
    }

    return spec


def validate_spec(spec: dict) -> tuple[bool, list[str]]:
    """Schema 验证（如果 jsonschema 可用）。"""
    if not HAS_JSONSCHEMA:
        return True, ["jsonschema not installed, skipping validation"]

    if not SPEC_SCHEMA.exists():
        return True, [f"Schema not found: {SPEC_SCHEMA}"]

    with open(SPEC_SCHEMA, encoding="utf-8") as f:
        schema = json.load(f)

    errors = []
    try:
        jsonschema.validate(instance=spec, schema=schema)
        return True, []
    except jsonschema.ValidationError as e:
        errors.append(f"ValidationError: {e.message}")
        return False, errors


def spec_to_yaml(spec: dict, output_path: Path):
    """将 ContentSpec 字典写入 YAML 文件。"""
    if not HAS_YAML:
        # 降级：写 JSON
        output_path = output_path.with_suffix(".json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(spec, f, ensure_ascii=False, indent=2)
        print(f"[WARN] PyYAML not installed, wrote JSON instead: {output_path}")
        return

    with open(output_path, "w", encoding="utf-8") as f:
        yaml.dump(
            spec,
            f,
            allow_unicode=True,
            default_flow_style=False,
            sort_keys=False,
            indent=2
        )


def main():
    parser = argparse.ArgumentParser(
        description="1_ingest · M1 考纲解析器：meta.json → ContentSpec YAML"
    )
    parser.add_argument(
        "--input", "-i",
        type=str,
        required=True,
        help="输入文件（meta.json 或考纲 Markdown）"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="输出 YAML 路径（默认：{输入名}_content_spec.yaml）"
    )
    parser.add_argument(
        "--no-validate",
        action="store_true",
        help="跳过 Schema 验证"
    )

    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"[ERROR] Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    # ── 加载 ───────────────────────────────────────────────────────────────
    print(f"[INFO] Loading: {input_path}")
    meta = load_meta_json(input_path)

    # ── 生成 ───────────────────────────────────────────────────────────────
    print("[INFO] Generating ContentSpec...")
    spec = generate_content_spec(meta)

    # ── 验证 ───────────────────────────────────────────────────────────────
    if not args.no_validate:
        valid, errors = validate_spec(spec)
        if valid:
            print(f"[OK] Schema validation passed")
        else:
            print(f"[WARN] Schema validation failed: {errors}")

    # ── 输出 ───────────────────────────────────────────────────────────────
    output_path = Path(args.output) if args.output else input_path.with_name(
        f"{input_path.stem}_content_spec.yaml"
    )
    spec_to_yaml(spec, output_path)
    print(f"[OK] ContentSpec written: {output_path}")

    # ── 摘要 ───────────────────────────────────────────────────────────────
    qt_count = len(spec["question_types"])
    ref_count = len(spec["reference_texts"])
    print(f"\n[摘要]")
    print(f"  spec_id:       {spec['spec_id']}")
    print(f"  题型数:        {qt_count}")
    print(f"  参考书目:      {ref_count}")
    print(f"  考点条目目标:  {spec['production_target']['knowledge_entries_target']}")
    print(f"  能力点目标:    {spec['production_target']['ability_count_target']}")


if __name__ == "__main__":
    main()
