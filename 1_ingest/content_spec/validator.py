# -*- coding: utf-8 -*-
"""
content_spec/validator.py — ContentSpec YAML 验证器
====================================================
对应 SOP v4.0 M1 + 内容制造管线执行规范 v1.0 §2.1

功能：
  1. 读取 ContentSpec YAML/JSON 文件
  2. Schema 验证（jsonschema）
  3. 教育领域特定规则检查（exam_meta / question_types / production_target）
  4. 输出验证报告

使用方式：
  result = validate_content_spec("content_spec.yaml")
  if result.is_valid:
      print("ContentSpec 验证通过")
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

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


# ─────────────────────────────────────────────────────────────────
# Schema 路径
# ─────────────────────────────────────────────────────────────────

SCHEMA_DIR = Path(__file__).parent.parent / "schemas"
SPEC_SCHEMA_PATH = SCHEMA_DIR / "content_spec.schema.json"


# ─────────────────────────────────────────────────────────────────
# 验证结果
# ─────────────────────────────────────────────────────────────────

@dataclass
class ValidationResult:
    is_valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    info: dict[str, Any] = field(default_factory=dict)

    def summary(self) -> str:
        status = "✅ 通过" if self.is_valid else "❌ 失败"
        lines = [f"ContentSpec 验证结果：{status}"]
        if self.errors:
            lines.append("\n错误：")
            for e in self.errors:
                lines.append(f"  🔴 {e}")
        if self.warnings:
            lines.append("\n警告：")
            for w in self.warnings:
                lines.append(f"  🟡 {w}")
        if self.info:
            lines.append("\n信息：")
            for k, v in self.info.items():
                lines.append(f"  {k}: {v}")
        return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────
# 验证器
# ─────────────────────────────────────────────────────────────────

class ContentSpecValidator:
    """
    ContentSpec 验证器

    检查维度：
      1. Schema 基础校验（jsonschema）
      2. 教育领域规则（exam_meta 完整性）
      3. question_types 权重和
      4. production_target 合理性
      5. 参考书目 trust 标注
    """

    def __init__(self, schema_path: Optional[Path] = None):
        self.schema_path = schema_path or SPEC_SCHEMA_PATH
        self._schema: Optional[dict] = None

    # ── 公开 API ──────────────────────────────────────────────

    def validate(self, spec: dict | Path | str) -> ValidationResult:
        """
        验证入口。

        参数：
          spec — dict（已解析）/ Path（文件路径）/ str（YAML/JSON 文本）
        """
        # 1. 解析输入
        if isinstance(spec, (Path, str)):
            spec = self._load_spec(Path(spec) if isinstance(spec, Path) else Path(spec))
        if not isinstance(spec, dict):
            return ValidationResult(
                is_valid=False,
                errors=[f"无效的 ContentSpec 类型：{type(spec)}"]
            )

        errors: list[str] = []
        warnings: list[str] = []
        info: dict[str, Any] = {}

        # 2. Schema 校验
        if HAS_JSONSCHEMA and self.schema_path.exists():
            schema_errs = self._validate_schema(spec)
            errors.extend(schema_errs)
        elif not HAS_JSONSCHEMA:
            warnings.append("jsonschema 未安装，跳过 Schema 校验")

        # 3. 教育领域规则检查
        rule_errs, rule_warns, rule_info = self._validate_education_rules(spec)
        errors.extend(rule_errs)
        warnings.extend(rule_warns)
        info.update(rule_info)

        # 4. 参考书目检查
        ref_warns = self._validate_reference_texts(spec)
        warnings.extend(ref_warns)

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            info=info,
        )

    # ── 内部方法 ──────────────────────────────────────────────

    def _load_spec(self, path: Path) -> dict:
        """加载 YAML/JSON 文件"""
        try:
            with open(path, encoding="utf-8") as f:
                content = f.read()
        except UnicodeDecodeError:
            with open(path, encoding="gbk", errors="replace") as f:
                content = f.read()

        if not HAS_YAML:
            return json.loads(content)

        try:
            return yaml.safe_load(content) or {}
        except yaml.YAMLError:
            return json.loads(content)

    def _validate_schema(self, spec: dict) -> list[str]:
        """JSON Schema 校验"""
        errors: list[str] = []
        try:
            with open(self.schema_path, encoding="utf-8") as f:
                schema = json.load(f)
            jsonschema.validate(instance=spec, schema=schema)
        except jsonschema.ValidationError as e:
            errors.append(f"Schema 校验失败：{e.message}")
        except FileNotFoundError:
            errors.append(f"Schema 文件未找到：{self.schema_path}")
        except Exception as e:
            errors.append(f"Schema 校验异常：{e}")
        return errors

    def _validate_education_rules(
        self, spec: dict
    ) -> tuple[list[str], list[str], dict]:
        """教育领域规则检查"""
        errors: list[str] = []
        warnings: list[str] = []
        info: dict[str, Any] = {}

        # exam_meta 完整性
        exam_meta = spec.get("exam_meta", {})
        required_meta = ["exam_name", "subject", "total_score"]
        for field in required_meta:
            if not exam_meta.get(field):
                errors.append(f"exam_meta.{field} 不能为空")

        # question_types 权重和
        qts = spec.get("question_types", [])
        if not qts:
            errors.append("question_types 不能为空")
        else:
            total_weight = sum(qt.get("weight", 0) for qt in qts)
            info["question_types_count"] = len(qts)
            info["weight_sum"] = round(total_weight, 2)
            if abs(total_weight - 1.0) > 0.01:
                errors.append(
                    f"question_types 权重和应接近 1.0，实际：{total_weight:.2f}"
                )
            # 检查题型ID唯一性
            ids = [qt.get("id") for qt in qts]
            if len(ids) != len(set(ids)):
                warnings.append("question_types 存在重复的 ID")

        # production_target 合理性
        prod = spec.get("production_target", {})
        entries_target = prod.get("knowledge_entries_target", 0)
        if entries_target == 0:
            warnings.append("production_target.knowledge_entries_target 未设置")
        elif entries_target < 20:
            warnings.append(
                "knowledge_entries_target < 20（低于 KBC fallback 底线 20）"
            )
        info["knowledge_entries_target"] = entries_target

        # 参考书目
        ref_texts = spec.get("reference_texts", [])
        info["reference_texts_count"] = len(ref_texts)
        if not ref_texts:
            warnings.append("reference_texts 为空（建议至少 2 本参考书目）")

        return errors, warnings, info

    def _validate_reference_texts(self, spec: dict) -> list[str]:
        """参考书目检查"""
        warnings: list[str] = []
        ref_texts = spec.get("reference_texts", [])
        for ref in ref_texts:
            trust = ref.get("trust", "")
            if trust and trust not in ("A", "B", "C", "D", "E"):
                warnings.append(
                    f"参考书目「{ref.get('title', '未知')}」trust 标注异常：{trust}"
                )
        return warnings


# ─────────────────────────────────────────────────────────────────
# 便捷入口
# ─────────────────────────────────────────────────────────────────

def validate(spec_path: Path | str) -> ValidationResult:
    """单函数便捷入口"""
    validator = ContentSpecValidator()
    return validator.validate(Path(spec_path))


def main():
    import argparse

    parser = argparse.ArgumentParser(description="ContentSpec YAML 验证器")
    parser.add_argument("spec", help="ContentSpec 文件路径")
    parser.add_argument("--schema", help="Schema 文件路径（可选）")
    args = parser.parse_args()

    validator = ContentSpecValidator(
        schema_path=Path(args.schema) if args.schema else None
    )
    result = validator.validate(Path(args.spec))
    print(result.summary())


if __name__ == "__main__":
    main()
