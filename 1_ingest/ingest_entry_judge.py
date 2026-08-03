# -*- coding: utf-8 -*-
"""
ingest_entry_judge.py — M0 入口判别器
======================================
对应 SOP v4.0 M0：判断给定素材包是否适用 1_ingest 流水线。

入口判别四判据（C1-C4）：
  C1 产出结构化：最终产出是可定义结构的知识包
  C2 规则可模板化：知识加工规则可被模板化
  C3 受众有共识：目标受众对"好内容"有共识标准
  C4 内容可复用：内容可被后续复用

使用方式：
  judge = IngestEntryJudge()
  decision = judge.judge(raw_input={"path": "...", "type": "exam_syllabus", ...})
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Optional


class ContentType(Enum):
    """素材包内容类型枚举"""
    EXAM_SYLLABUS = "exam_syllabus"            # 考试大纲
    ANCIENT_TEXT_OCR = "ancient_text_ocr"    # 古籍OCR
    TEXTBOOK = "textbook"                      # 教材/教辅
    WEB_SCRAPE = "web_scrape"                 # 网络爬取
    EXPERT_NOTES = "expert_notes"              # 专家口述/备课笔记
    UNKNOWN = "unknown"                       # 未知类型


class EntryVerdict(Enum):
    """入口判定结论"""
    APPLICABLE = "applicable"           # 适用
    NOT_APPLICABLE = "not_applicable"  # 不适用
    NEEDS_HUMAN_REVIEW = "needs_human_review"  # 需人工确认


@dataclass
class CriterionResult:
    """单条判据结果"""
    criterion_id: str          # C1 / C2 / C3 / C4
    criterion_label: str      # 判据名称
    passed: bool
    score: float              # 0.0–1.0
    evidence: list[str] = field(default_factory=list)
    concerns: list[str] = field(default_factory=list)


@dataclass
class EntryDecision:
    """M0 入口判别输出"""
    verdict: EntryVerdict
    content_type: ContentType
    criteria_results: list[CriterionResult] = field(default_factory=list)
    pass_count: int = 0
    total_count: int = 4
    reasons: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    confidence: float = 0.0    # 0.0–1.0 机器置信度

    def to_dict(self) -> dict:
        return {
            "verdict": self.verdict.value,
            "content_type": self.content_type.value,
            "pass_count": self.pass_count,
            "total_count": self.total_count,
            "pass_rate": self.pass_count / self.total_count,
            "confidence": self.confidence,
            "reasons": self.reasons,
            "suggestions": self.suggestions,
            "criteria": [
                {
                    "id": r.criterion_id,
                    "label": r.criterion_label,
                    "passed": r.passed,
                    "score": r.score,
                    "evidence": r.evidence,
                    "concerns": r.concerns,
                }
                for r in self.criteria_results
            ],
        }

    def to_json(self, fp: Optional[Path] = None) -> str:
        text = json.dumps(self.to_dict(), ensure_ascii=False, indent=2)
        if fp:
            Path(fp).parent.mkdir(parents=True, exist_ok=True)
            with open(fp, "w", encoding="utf-8") as f:
                f.write(text)
        return text


class IngestEntryJudge:
    """
    M0 入口判别器

    判别流程：
      1. auto_detect_content_type() — 自动识别素材包内容类型
      2. assess_criteria() — 对四条判据打分
      3. make_decision() — 综合输出 EntryDecision

    四判据评分标准：
      C1 产出结构化（1.0分）：有明确题型/知识点定义 → 0.8
                            有结构但松散 → 0.5
                            无结构 → 0.1
      C2 规则可模板化（1.0分）：规则清晰可枚举 → 0.9
                              部分规则可枚举 → 0.5
                              高度主观 → 0.2
      C3 受众有共识（1.0分）：考试/学术标准明确 → 0.9
                            行业共识存在 → 0.6
                            受众差异大 → 0.3
      C4 内容可复用（1.0分）：跨考试/跨课程可用 → 0.9
                            特定场景可复用 → 0.6
                            单次使用 → 0.2

    判决规则：
      - pass_count >= 3 → APPLICABLE（通过）
      - pass_count == 2 → NEEDS_HUMAN_REVIEW（需人工确认）
      - pass_count <= 1 → NOT_APPLICABLE（不适用）
    """

    # 各内容类型的典型扩展名/路径特征
    CONTENT_TYPE_SIGNATURES: dict[ContentType, list[str]] = {
        ContentType.EXAM_SYLLABUS: [
            "考纲", "大纲", "syllabus", "exam", "招生", "复试", "初试",
            "考试说明", "考试范围",
        ],
        ContentType.ANCIENT_TEXT_OCR: [
            "说文", "书谱", "史记", "汉书", "古文", "ocr", "古籍",
            "碑帖", "金石", "竹简", "帛书",
        ],
        ContentType.TEXTBOOK: [
            "教材", "教科书", "教辅", "教程", "textbook", "教材教辅",
        ],
        ContentType.WEB_SCRAPE: [
            "wiki", "baike", "wikipedia", "百度百科", "维基",
            "scrap", "crawl", "爬取",
        ],
        ContentType.EXPERT_NOTES: [
            "备课", "笔记", "notes", "专家", "口述", "教案",
        ],
    }

    def __init__(self, config_path: Optional[Path] = None):
        self.config = self._load_config(config_path)
        # pass_rate: 通过率阈值（4分中通过几分算通过）
        self.pass_threshold: int = self.config.get("pass_threshold", 3)

    # ─────────────────────────────────────────────────────────────────
    # 公开 API
    # ─────────────────────────────────────────────────────────────────

    def judge(self, raw_input: dict | Path | str) -> EntryDecision:
        """
        入口判别主入口。

        参数：
          raw_input — dict（含 type/description/path 等键）或
                      Path/str（指向素材包目录）

        返回：
          EntryDecision
        """
        # 1. 解析输入
        if isinstance(raw_input, (Path, str)):
            raw_input = self._path_to_dict(raw_input)

        content_type = self._auto_detect_content_type(raw_input)

        # 2. 四条判据评估
        criteria = [
            self._assess_c1_structured_output(raw_input, content_type),
            self._assess_c2_templatable_rules(raw_input, content_type),
            self._assess_c3_audience_consensus(raw_input, content_type),
            self._assess_c4_reusable_content(raw_input, content_type),
        ]

        # 3. 判决
        decision = self._make_decision(criteria, content_type)
        return decision

    # ─────────────────────────────────────────────────────────────────
    # 核心判据评估
    # ─────────────────────────────────────────────────────────────────

    def _assess_c1_structured_output(
        self, raw: dict, ct: ContentType
    ) -> CriterionResult:
        """C1：最终产出是否可定义结构"""
        score = 0.0
        evidence: list[str] = []
        concerns: list[str] = []

        # 题型明确性（考纲类最高）
        if ct == ContentType.EXAM_SYLLABUS:
            if raw.get("question_types") or raw.get("exam_structure"):
                score = 1.0
                evidence.append("发现明确的题型/考核结构")
            elif raw.get("topics") or raw.get("key_points"):
                score = 0.8
                evidence.append("发现知识点列表，结构较清晰")
            else:
                score = 0.6
                evidence.append("考纲类素材，具天然结构")
        # 古籍OCR
        elif ct == ContentType.ANCIENT_TEXT_OCR:
            if raw.get("chapter_list") or raw.get("full_text"):
                score = 0.7
                evidence.append("古籍全文，章节结构可解析")
            else:
                score = 0.4
                concerns.append("OCR文本可能存在断句/识别错误")
        # 教材
        elif ct == ContentType.TEXTBOOK:
            score = 0.6
            evidence.append("教材具章节结构")
            concerns.append("不同版本间可能有内容差异")
        # 网络爬取
        elif ct == ContentType.WEB_SCRAPE:
            score = 0.3
            concerns.append("网页内容结构不固定，需预处理")
        # 专家笔记
        elif ct == ContentType.EXPERT_NOTES:
            score = 0.4
            concerns.append("笔记结构因人而异")
        else:
            score = 0.2
            concerns.append("素材类型未知，结构无法预判")

        passed = score >= 0.6
        return CriterionResult(
            criterion_id="C1",
            criterion_label="产出结构化",
            passed=passed,
            score=score,
            evidence=evidence,
            concerns=concerns,
        )

    def _assess_c2_templatable_rules(
        self, raw: dict, ct: ContentType
    ) -> CriterionResult:
        """C2：知识加工规则是否可模板化"""
        score = 0.0
        evidence: list[str] = []
        concerns: list[str] = []

        # 考纲：题型/评分标准 = 天然规则
        if ct == ContentType.EXAM_SYLLABUS:
            if raw.get("scoring_rules") or raw.get("grading"):
                score = 1.0
                evidence.append("发现明确的评分规则")
            elif raw.get("question_types"):
                score = 0.85
                evidence.append("题型明确，规则可枚举")
            else:
                score = 0.7
                evidence.append("考纲具天然规则性（题型/范围）")
        # 古籍：六书/说文部首 = 规则可枚举
        elif ct == ContentType.ANCIENT_TEXT_OCR:
            if raw.get("script_type") in ("小篆", "隶书", "楷书", "金文"):
                score = 0.8
                evidence.append(f"文字类型「{raw.get('script_type')}」规则明确")
            else:
                score = 0.5
                concerns.append("古籍文字类型不明确，转换规则可能因版本而异")
        # 教材：章节编排 = 规则较清晰
        elif ct == ContentType.TEXTBOOK:
            score = 0.55
            evidence.append("教材有固定编排逻辑")
            concerns.append("不同教材体系可能不兼容")
        # 网络/专家笔记：高度主观
        else:
            score = 0.3
            concerns.append("网络内容/专家笔记高度个性化，规则难以模板化")

        passed = score >= 0.6
        return CriterionResult(
            criterion_id="C2",
            criterion_label="规则可模板化",
            passed=passed,
            score=score,
            evidence=evidence,
            concerns=concerns,
        )

    def _assess_c3_audience_consensus(
        self, raw: dict, ct: ContentType
    ) -> CriterionResult:
        """C3：目标受众是否有"好内容"共识"""
        score = 0.0
        evidence: list[str] = []
        concerns: list[str] = []

        # 考试大纲：考官/考生共识最强
        if ct == ContentType.EXAM_SYLLABUS:
            if raw.get("official_publisher") or raw.get("source") == "官方":
                score = 1.0
                evidence.append("官方发布，评判标准明确")
            else:
                score = 0.85
                evidence.append("考试标准具强共识")
        # 古籍：学界共识存在
        elif ct == ContentType.ANCIENT_TEXT_OCR:
            score = 0.8
            evidence.append("古籍内容经学界长期研究，共识较高")
            concerns.append("部分古籍存在版本争议")
        # 教材：教师/学生共识
        elif ct == ContentType.TEXTBOOK:
            score = 0.65
            evidence.append("教材在特定课程内具共识")
            concerns.append("跨教材版本可能有差异")
        # 网络：大众内容，共识弱
        elif ct == ContentType.WEB_SCRAPE:
            score = 0.35
            concerns.append("网络内容缺乏专业共识，需严格质量校准")
        # 专家笔记
        else:
            score = 0.5
            concerns.append("专家观点可能与主流共识有偏差")

        passed = score >= 0.6
        return CriterionResult(
            criterion_id="C3",
            criterion_label="受众有共识",
            passed=passed,
            score=score,
            evidence=evidence,
            concerns=concerns,
        )

    def _assess_c4_reusable_content(
        self, raw: dict, ct: ContentType
    ) -> CriterionResult:
        """C4：内容是否可被后续复用"""
        score = 0.0
        evidence: list[str] = []
        concerns: list[str] = []

        # 考纲：可跨年度、跨地区复用
        if ct == ContentType.EXAM_SYLLABUS:
            score = 0.95
            evidence.append("考纲具跨年度复用价值")
            concerns.append("部分内容可能随考纲更新而失效")
        # 古籍：永久可用
        elif ct == ContentType.ANCIENT_TEXT_OCR:
            score = 0.9
            evidence.append("古籍内容永久有效，可跨课程复用")
        # 教材：特定课程内复用
        elif ct == ContentType.TEXTBOOK:
            score = 0.6
            evidence.append("教材内容在对应课程内可复用")
            concerns.append("课程更新可能导致教材版本过时")
        # 网络爬取：时效性强
        elif ct == ContentType.WEB_SCRAPE:
            score = 0.25
            concerns.append("网络内容时效性强，复用价值有限")
        else:
            score = 0.4

        passed = score >= 0.6
        return CriterionResult(
            criterion_id="C4",
            criterion_label="内容可复用",
            passed=passed,
            score=score,
            evidence=evidence,
            concerns=concerns,
        )

    # ─────────────────────────────────────────────────────────────────
    # 判决逻辑
    # ─────────────────────────────────────────────────────────────────

    def _make_decision(
        self,
        criteria: list[CriterionResult],
        content_type: ContentType,
    ) -> EntryDecision:
        passed = [c for c in criteria if c.passed]
        pass_count = len(passed)

        reasons: list[str] = []
        suggestions: list[str] = []

        if pass_count >= self.pass_threshold:
            verdict = EntryVerdict.APPLICABLE
            reasons.append(f"通过 {pass_count}/4 条判据")
            reasons.append(f"内容类型「{content_type.value}」适合 1_ingest 流水线")
        elif pass_count == 2:
            verdict = EntryVerdict.NEEDS_HUMAN_REVIEW
            reasons.append(f"通过 {pass_count}/4 条判据，建议人工确认")
            failed = [c for c in criteria if not c.passed]
            for c in failed:
                suggestions.append(f"建议补充或优化：{c.criterion_label}")
        else:
            verdict = EntryVerdict.NOT_APPLICABLE
            reasons.append(f"仅通过 {pass_count}/4 条判据，不适合自动化流水线")

        confidence = pass_count / 4.0

        return EntryDecision(
            verdict=verdict,
            content_type=content_type,
            criteria_results=criteria,
            pass_count=pass_count,
            total_count=4,
            reasons=reasons,
            suggestions=suggestions,
            confidence=confidence,
        )

    # ─────────────────────────────────────────────────────────────────
    # 辅助方法
    # ─────────────────────────────────────────────────────────────────

    def _load_config(self, config_path: Optional[Path]) -> dict:
        if config_path and config_path.exists():
            with open(config_path, encoding="utf-8") as f:
                return json.load(f)
        return {"pass_threshold": 3}

    def _path_to_dict(self, path: Path | str) -> dict:
        """从目录/文件路径提取元信息"""
        p = Path(path)
        result: dict[str, Any] = {
            "path": str(p),
            "name": p.name,
        }
        if p.is_dir():
            result["files"] = [f.name for f in p.iterdir()]
            result["description"] = self._infer_description_from_files(
                result["files"]
            )
        elif p.is_file():
            result["extension"] = p.suffix
            result["description"] = p.stem
        return result

    def _infer_description_from_files(self, files: list[str]) -> str:
        """从文件列表推断描述"""
        names_str = " ".join(files)
        for ct, sigs in self.CONTENT_TYPE_SIGNATURES.items():
            for sig in sigs:
                if sig in names_str:
                    return ct.value
        return ContentType.UNKNOWN.value

    def _auto_detect_content_type(self, raw: dict) -> ContentType:
        """从 raw dict 推断内容类型"""
        # 显式指定
        if raw.get("content_type"):
            try:
                return ContentType(raw["content_type"])
            except ValueError:
                pass

        # 从 description/name 推断
        text = " ".join([
            str(raw.get("description", "")),
            str(raw.get("name", "")),
            str(raw.get("type", "")),
        ]).lower()

        for ct, sigs in self.CONTENT_TYPE_SIGNATURES.items():
            for sig in sigs:
                if sig in text:
                    return ct

        # 从 files 列表推断
        if raw.get("files"):
            text2 = " ".join(raw["files"]).lower()
            for ct, sigs in self.CONTENT_TYPE_SIGNATURES.items():
                for sig in sigs:
                    if sig in text2:
                        return ct

        return ContentType.UNKNOWN


# ─────────────────────────────────────────────────────────────────
# 便捷 CLI 入口
# ─────────────────────────────────────────────────────────────────

def main():
    import argparse

    parser = argparse.ArgumentParser(description="M0 入口判别器")
    parser.add_argument("path", help="素材包路径（目录或JSON文件）")
    parser.add_argument("-o", "--output", help="输出JSON路径")
    args = parser.parse_args()

    judge = IngestEntryJudge()
    raw = json.loads(Path(args.path).read_text(encoding="utf-8")) \
        if Path(args.path).suffix == ".json" \
        else args.path

    decision = judge.judge(raw)

    fp = Path(args.output) if args.output else None
    print(decision.to_json(fp))

    # 打印摘要
    print(f"\n{'='*50}")
    print(f"入口判定：{decision.verdict.value}")
    print(f"内容类型：{decision.content_type.value}")
    print(f"通过率：{decision.pass_count}/{decision.total_count}（{decision.confidence:.0%}）")
    for r in decision.reasons:
        print(f"  → {r}")
    if decision.suggestions:
        print("建议：")
        for s in decision.suggestions:
            print(f"  ⚠ {s}")


if __name__ == "__main__":
    main()
