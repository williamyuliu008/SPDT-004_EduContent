# -*- coding: utf-8 -*-
"""
router.py — 内容形态路由器（M0 后置路由）
===============================================
对应 SOP v4.0 M0 入口路由器 · 教育领域 B1-B4 形态判定
Phase 1 扩展：生成 pipeline_package outer 字段

集成关系：
  ingest_entry_judge.py（M0） → router.py（M0 后置） → content_type.yaml（路由规则）
                                              ↓
                               EntryDecision + content_type.yaml
                                              ↓
                               content_spec.content_type（B1/B2/B3/B4）
                                              ↓
                               route.to_outer() → pipeline_package.outer 字段

使用方式：
  from router import ContentRouter

  judge = IngestEntryJudge()
  router = ContentRouter()

  decision = judge.judge(raw_input)
  if decision.verdict == EntryVerdict.APPLICABLE:
      route = router.route(decision, raw_input)
      print(route.target_module)  # TextExperience
      print(route.genre)          # 墨骨山河系列

      # Phase 1: 生成外层接口
      outer = route.to_outer(raw_input, content_spec)
      # → 用于 build_pipeline_package() 组装完整 pipeline_package
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


# ─────────────────────────────────────────────────────────────────
# 路由结果
# ─────────────────────────────────────────────────────────────────

@dataclass
class RouteResult:
    """B1-B4 路由决策"""
    b1_b4_type: str          # "B1_deep_content" / "B2_rapid" / "B3_translation" / "B4_argumentation"
    label: str                # "B1 深度长内容"
    description: str
    target_modules: list[str]
    pipeline_stage: str
    genre: str
    matched_keywords: list[str] = field(default_factory=list)
    confidence: float = 0.0   # 0.0-1.0
    routing_note: str = ""

    def to_dict(self) -> dict:
        return {
            "b1_b4_type": self.b1_b4_type,
            "label": self.label,
            "description": self.description,
            "target_modules": self.target_modules,
            "pipeline_stage": self.pipeline_stage,
            "genre": self.genre,
            "matched_keywords": self.matched_keywords,
            "confidence": self.confidence,
            "routing_note": self.routing_note,
        }

    # ─────────────────────────────────────────────────────────────────
    # Phase 1 新增：外层接口生成（pipeline_package outer 字段）
    # ─────────────────────────────────────────────────────────────────

    def to_outer(self, raw_input: dict, content_spec: Optional[dict] = None) -> dict:
        """
        将 RouteResult 转换为 pipeline_package outer 字段。

        这是 Phase 1 外层接口显式化的关键方法——
        从 B1-B4 路由决策直接生成管线外层元数据，
        用于后续 build_pipeline_package() 组装完整的 pipeline_package。

        参数：
          raw_input     — 原始输入（从中提取 subject_domain / source_chain_id）
          content_spec  — ContentSpec（可选；用于推断 knowledge_types）

        返回：
          pipeline_package outer 字段 dict
        """
        from datetime import datetime, timezone

        # 推断 subject_domain
        subject_domain = self._infer_subject_domain(raw_input)
        subject_detail = raw_input.get("description", "")[:50] or self.genre

        # 推断 knowledge_types（从 content_spec 或 raw_input）
        knowledge_types = self._infer_knowledge_types_from_input(raw_input, content_spec)

        # capabilities（从 B1-B4 推断）
        capabilities = self._b1b4_to_capabilities(self.b1_b4_type)

        # source_chain_id
        path_field = raw_input.get("path", "")
        type_field = raw_input.get("type", "")
        spec_id = raw_input.get("spec_id", type_field or "unknown")
        source_chain_id = f"{spec_id}_{self.b1_b4_type}_{int(self.confidence * 100)}"

        return {
            "subject_domain": subject_domain,
            "subject_detail": subject_detail,
            "content_type": self.b1_b4_type,
            "content_type_detail": self.label,
            "knowledge_types": knowledge_types,
            "capabilities": capabilities,
            "source_chain_id": source_chain_id,
            "content_spec_id": spec_id,
            "trust_level": self._infer_trust_level(raw_input),
            "produced_by": f"1_ingest.router ({self.pipeline_stage})",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "render_outputs": [],      # 3_render 追加
            "quality_score": None,     # 4_adapt 追加
            "adaptive_notes": None,    # 4_adapt 追加
            # 路由附加信息（进入路由元数据，不影响 Schema 校验）
            "_route_confidence": self.confidence,
            "_matched_keywords": self.matched_keywords,
            "_genre": self.genre,
            "_target_modules": self.target_modules,
        }

    def _infer_subject_domain(self, raw_input: dict) -> str:
        """
        从 raw_input 推断 subject_domain。

        优先级：
          1. raw_input["subject_domain"] 显式指定（测试 fixture / 外部调用）
          2. 从 description + type 字段中的学科关键词推断
          3. 缺省返回 "GENERIC"

        注意：在 Windows GBK 环境下，YAML/JSON 文件中的中文字符串会被正确解码，
              但 Python 源代码中的字符串字面量（如 fixture 的 description 字段）
              可能受编码影响。因此优先使用显式指定。
        """
        # 优先级1：显式指定
        explicit = raw_input.get("subject_domain")
        if explicit and isinstance(explicit, str):
            return explicit

        # 优先级2：从内容推断
        desc = raw_input.get("description", "").lower()
        type_field = raw_input.get("type", "").lower()
        combined = desc + " " + type_field

        domain_map = [
            ("书法", "HIST_ART"),
            ("历史", "HISTORY"),
            ("地理", "GEO"),
            ("政治", "POL"),
            ("数学", "MATH"),
            ("化学", "CHEM"),
            ("物理", "PHYS"),
            ("生物", "BIO"),
            ("语文", "CHINESE"),
            ("英语", "ENGLISH"),
            ("古汉语", "CHINESE"),
            ("考纲", "GENERIC"),
        ]
        for kw, domain in domain_map:
            if kw in combined:
                return domain
        return "GENERIC"

    def _infer_trust_level(self, raw_input: dict) -> str:
        """从 raw_input.type 推断 trust_level"""
        type_map = {
            "exam_syllabus": "E",
            "textbook": "D",
            "ancient_text_ocr": "E",
            "expert_notes": "D",
            "web_scrape": "C",
        }
        return type_map.get(raw_input.get("type", ""), "E")

    def _infer_knowledge_types_from_input(
        self, raw_input: dict, content_spec: Optional[dict] = None
    ) -> list[str]:
        """从 raw_input 和 content_spec 推断知识类型"""
        # 优先从 content_spec 的 question_types 推断
        if content_spec:
            qts = content_spec.get("question_types", [])
            k_types: set[str] = set()
            for qt in qts:
                qt_id = (qt.get("id", "") + qt.get("name", "")).upper()
                if "TRANSDUCTION" in qt_id or "TRANSLATION" in qt_id or "PROC" in qt_id:
                    k_types.add("K_PROCEDURE")
                elif "TERM" in qt_id or "CONCEPT" in qt_id or "EXPLAIN" in qt_id:
                    k_types.add("K_CONCEPT")
                elif "ANALYSIS" in qt_id or "ARGUE" in qt_id:
                    k_types.add("K_METACOG")
                else:
                    k_types.add("K_CONCEPT")
            if k_types:
                return list(k_types)

        # 从 raw_input 推断
        desc = raw_input.get("description", "").lower()
        if any(kw in desc for kw in ["辨析", "翻译", "步骤", "流程"]):
            return ["K_PROCEDURE", "K_CONCEPT"]
        elif any(kw in desc for kw in ["分析", "论证", "判断"]):
            return ["K_METACOG", "K_CONCEPT"]
        return ["K_CONCEPT"]

    def _b1b4_to_capabilities(self, b1_b4_type: str) -> list[str]:
        """B1-B4 → capabilities"""
        cap_map = {
            "B1_deep_content":  ["needs_narrative", "needs_analogy", "needs_visual"],
            "B2_rapid":         ["needs_visual", "needs_procedure", "needs_interactive"],
            "B3_translation":   ["needs_translation", "needs_comparison", "needs_visual"],
            "B4_argumentation":  ["needs_reflection", "needs_comparison", "needs_narrative"],
        }
        return cap_map.get(b1_b4_type, cap_map["B1_deep_content"])


# ─────────────────────────────────────────────────────────────────
# 内容形态路由器
# ─────────────────────────────────────────────────────────────────

class ContentRouter:
    """
    B1-B4 内容形态路由器

    工作流程：
      1. 读取 content_type.yaml 路由规则
      2. 对入口决策的 raw_input 进行关键词匹配
      3. 按最具体匹配优先（most_specific）返回 RouteResult
      4. 无匹配时返回 default_fallback（B1_deep_content）

    与 ingest_entry_judge 的集成：
      judge = IngestEntryJudge()
      decision = judge.judge(raw_input)
      if decision.verdict == EntryVerdict.APPLICABLE:
          route = router.route(decision, raw_input)
    """

    def __init__(self, config_path: Optional[Path] = None):
        if config_path is None:
            config_path = Path(__file__).parent / "content_type.yaml"
        self.config = self._load_yaml(config_path)

        self.content_types: dict = self.config.get("content_types", {})
        self.routing_rules: dict = self.config.get("routing_rules", {})

        # 路由决策
        self.keyword_priority: bool = self.routing_rules.get("keyword_priority", True)
        self.default_fallback: str = self.routing_rules.get("default_fallback", "B1_deep_content")
        self.conflict_resolution: str = self.routing_rules.get("conflict_resolution", "most_specific")

    def _load_yaml(self, path: Path) -> dict:
        """加载 YAML 配置文件（支持 Python 3.11+ PyYAML 或手动解析）"""
        try:
            import yaml
            with open(path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except ImportError:
            return self._manual_yaml_parse(path)

    def _manual_yaml_parse(self, path: Path) -> dict:
        """手动解析简化 YAML（无 PyYAML 依赖时）"""
        result = {"content_types": {}, "routing_rules": {}}
        current_section = None
        current_type = None

        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.rstrip()
                # 跳过注释和空行
                if not line or line.startswith("#"):
                    continue
                if line.startswith("content_types:") or line.startswith("routing_rules:"):
                    current_section = line.split(":")[0].strip()
                    continue
                # content_type 名称行
                if line.startswith(" ") and ":" in line and not line.strip().startswith("-"):
                    indent = len(line) - len(line.lstrip())
                    if indent == 2:
                        name = line.strip().rstrip(":")
                        current_type = name
                        if current_type not in result["content_types"]:
                            result["content_types"][current_type] = {}
                    elif indent == 4 and current_type:
                        key, _, val = line.strip().partition(":")
                        key = key.strip()
                        val = val.strip()
                        if val:
                            result["content_types"][current_type][key] = val
                # routing_rules 简单键值
                if current_section == "routing_rules" and ":" in line and not line.strip().startswith("-"):
                    key, _, val = line.partition(":")
                    result["routing_rules"][key.strip()] = val.strip()

        return result

    def route(self, decision, raw_input: dict) -> RouteResult:
        """
        执行 B1-B4 路由。

        参数：
          decision — EntryDecision（M0 入口决策）
          raw_input — 原始输入字典

        返回：
          RouteResult（B1-B4 路由结果）
        """
        # 从 raw_input 提取关键词
        keywords = self._extract_keywords(raw_input)

        # 关键词匹配
        scores: dict[str, tuple[int, list[str]]] = {}
        for b1_type, type_config in self.content_types.items():
            type_keywords = type_config.get("indicators", {}).get("keywords", [])
            matched = [kw for kw in keywords if kw in type_keywords]
            scores[b1_type] = (len(matched), matched)

        if scores:
            # 最具体匹配优先
            best_type = max(scores, key=lambda k: scores[k][0])
            match_count, matched_keywords = scores[best_type]
        else:
            best_type = self.default_fallback
            match_count, matched_keywords = 0, []

        # 计算置信度
        confidence = min(1.0, match_count / 3) if match_count > 0 else 0.5

        type_config = self.content_types.get(best_type, {})
        label = type_config.get("label", best_type)
        description = type_config.get("description", "")
        target_modules = type_config.get("target_modules", [])
        pipeline_stage = type_config.get("pipeline_stage", "")
        genre = type_config.get("genre", "")

        note = ""
        if match_count == 0:
            note = f"无关键词匹配，使用缺省路由：{self.default_fallback}"
        else:
            note = f"关键词匹配 {match_count} 项：{' / '.join(matched_keywords)}"

        return RouteResult(
            b1_b4_type=best_type,
            label=label,
            description=description,
            target_modules=target_modules,
            pipeline_stage=pipeline_stage,
            genre=genre,
            matched_keywords=matched_keywords,
            confidence=confidence,
            routing_note=note,
        )

    def _extract_keywords(self, raw_input: dict) -> list[str]:
        """从 raw_input 提取关键词"""
        keywords: list[str] = []

        # 显式 keywords 字段
        if "keywords" in raw_input:
            kw = raw_input["keywords"]
            if isinstance(kw, list):
                keywords.extend(kw)
            elif isinstance(kw, str):
                keywords.append(kw)

        # description / title 字段（中文分词粗略提取）
        for field_name in ["description", "title", "name", "exam_name", "path"]:
            val = raw_input.get(field_name, "")
            if val and isinstance(val, str):
                keywords.extend(self._simple_tokenize(val))

        # content_type 字段
        if "content_type" in raw_input:
            ct = raw_input["content_type"]
            if isinstance(ct, str):
                keywords.append(ct)

        return list(set(keywords))

    def _simple_tokenize(self, text: str) -> list[str]:
        """简单中文分词（基于 2-4 字词匹配）"""
        words: list[str] = []
        # 常见 2-4 字词
        patterns = [
            "历史", "书法史", "书论", "深度", "系列", "跨学科",
            "速查", "考点", "快背", "核心", "要点",
            "辨析", "区分", "解释", "转化", "翻译",
            "分析", "论证", "判断", "推荐", "薄弱点",
            "考纲", "大纲", "复试", "初试",
            "知识链", "墨骨", "山河", "系列",
        ]
        for word in patterns:
            if word in text:
                words.append(word)
        return words

    def list_all_types(self) -> list[str]:
        """列出所有支持的 B1-B4 类型"""
        return list(self.content_types.keys())
