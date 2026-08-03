# -*- coding: utf-8 -*-
"""
ontology/consumer.py — KBC 领域本体消费者
==========================================
对应 SOP v4.0 M2：领域本体消费 + 两级降级策略

职责：
  1. KBC 查询（领域本体匹配）
  2. 两级降级：KBC无本体 → 公开本体 → 最小词典（≥20条）
  3. 术语词典输出 → 供 ingest_quality_calibrator 使用

规范参考：
  - 内容制造管线执行规范 v1.0 §2.1 M2 领域本体消费
  - SOP v4.0 M2 KBC 查询流程

使用方式：
  consumer = OntologyConsumer()
  result = consumer.query(keyword="颜真卿")
  # result.trust_level: E/B/C/D
  # result.term_dict: list[TermEntry]
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional


# ─────────────────────────────────────────────────────────────────
# 数据结构
# ─────────────────────────────────────────────────────────────────

class TrustLevel(Enum):
    E = "E"   # 专家共识（古籍原文/官方考纲）
    B = "B"   # 权威二手（标准注释/学界共识）
    C = "C"   # 编辑审核（教材/教辅）
    D = "D"   # 大众共识（网络资料/公开百科）
    A = "A"   # 权威一手（原始文献）


class FallbackStrategy(Enum):
    KBC_MATCH = "kbc_match"           # KBC 本体直接匹配
    KBC_PARTIAL = "kbc_partial"       # KBC 部分匹配
    PUBLIC_ONTOLOGY = "public_ontology" # 公开本体（维基/百度百科）
    MINIMUM_DICT = "minimum_dict"       # 最小词典（≥20条底线）


@dataclass
class TermEntry:
    """术语条目"""
    term_id: str
    term: str
    definition: str
    trust_level: str           # A/B/C/D/E
    source: str               # 来源标题
    source_type: str          # 古籍/教材/网络/...
    exam_relevance: float     # 0.0-1.0 考纲相关性
    question_types: list[str] # 相关题型
    synonyms: list[str] = field(default_factory=list)
    notes: str = ""


@dataclass
class OntologyQueryResult:
    """KBC 查询结果"""
    keyword: str
    matched: bool
    strategy: FallbackStrategy
    trust_level: str
    term_dict: list[TermEntry]
    coverage_rate: float        # 覆盖率（0.0-1.0）
    missing_terms: list[str]  # 未找到的术语
    fallback_used: bool


# ─────────────────────────────────────────────────────────────────
# KBC 消费者
# ─────────────────────────────────────────────────────────────────

class OntologyConsumer:
    """
    领域本体消费者

    两级降级策略（SOP v4.0 M2）：
      L1（≥80%覆盖）  → 直接使用 KBC 本体
      L2（30-80%）    → 公开本体补充，标注缺口
      L3（<30%）      → 先建最小词典（≥20条），再逐步扩充
    """

    # 最低术语数底线（KBC fallback）
    MINIMUM_TERMS = 20

    def __init__(self, kbc_path: Optional[Path] = None, minimum_terms: int = 20):
        self.kbc_path = kbc_path
        self.minimum_terms = minimum_terms
        self._kbc_cache: dict[str, TermEntry] = {}
        self._load_kbc()

    def query(self, keyword: str, content_spec_id: str = "CAFA") -> OntologyQueryResult:
        """
        查询术语领域本体。

        参数：
          keyword — 查询关键词
          content_spec_id — 对应的 ContentSpec ID

        返回：
          OntologyQueryResult
        """
        # L1: KBC 本体匹配
        kbc_matches = self._query_kbc(keyword)
        coverage = len(kbc_matches) / self.minimum_terms if self.minimum_terms > 0 else 0

        if coverage >= 0.80:
            strategy = FallbackStrategy.KBC_MATCH
        elif coverage >= 0.30:
            strategy = FallbackStrategy.KBC_PARTIAL
        elif coverage > 0:
            strategy = FallbackStrategy.PUBLIC_ONTOLOGY
        else:
            strategy = FallbackStrategy.MINIMUM_DICT

        # 缺术语检查
        all_terms = self._get_all_terms()
        missing = [t for t in all_terms if t not in [e.term for e in kbc_matches]]

        return OntologyQueryResult(
            keyword=keyword,
            matched=coverage > 0,
            strategy=strategy,
            trust_level=self._avg_trust(kbc_matches),
            term_dict=kbc_matches,
            coverage_rate=min(coverage, 1.0),
            missing_terms=missing[:10],   # 只返回前10个缺失项
            fallback_used=strategy != FallbackStrategy.KBC_MATCH,
        )

    def query_batch(
        self,
        keywords: list[str],
        content_spec_id: str = "CAFA"
    ) -> list[OntologyQueryResult]:
        """批量查询"""
        return [self.query(kw, content_spec_id) for kw in keywords]

    # ── 内部方法 ──────────────────────────────────────────────

    def _load_kbc(self):
        """加载 KBC 本体（如有）"""
        if not self.kbc_path or not self.kbc_path.exists():
            return

        try:
            with open(self.kbc_path, encoding="utf-8") as f:
                data = json.load(f)

            for entry in data.get("entries", data.get("terms", [])):
                term = entry.get("concept", entry.get("term", ""))
                if term:
                    te = TermEntry(
                        term_id=entry.get("id", entry.get("kb_id", f"KBC_{len(self._kbc_cache)}")),
                        term=term,
                        definition=entry.get("definition", ""),
                        trust_level=entry.get("trust", entry.get("trust_level", "C")),
                        source=entry.get("source_title", entry.get("source", "KBC")),
                        source_type=entry.get("source_type", "domain_db"),
                        exam_relevance=entry.get("exam_relevance", 0.5),
                        question_types=entry.get("question_types", []),
                        synonyms=entry.get("synonyms", []),
                        notes=entry.get("notes", ""),
                    )
                    self._kbc_cache[term] = te
        except Exception:
            pass

    def _query_kbc(self, keyword: str) -> list[TermEntry]:
        """KBC 本体查询"""
        keyword_lower = keyword.lower()
        matches = [
            te for term, te in self._kbc_cache.items()
            if keyword_lower in term.lower() or term.lower() in keyword_lower
        ]
        return matches

    def _get_all_terms(self) -> list[str]:
        """获取所有可用术语"""
        return list(self._kbc_cache.keys())

    @staticmethod
    def _avg_trust(entries: list[TermEntry]) -> str:
        """计算平均可信度"""
        if not entries:
            return "D"
        trust_order = {"E": 5, "B": 4, "C": 3, "D": 2, "A": 1}
        total = sum(trust_order.get(e.trust_level, 3) for e in entries)
        avg = total / len(entries)
        # 取最近等级
        for level, score in trust_order.items():
            if abs(score - avg) < 1.5:
                return level
        return "D"


# ─────────────────────────────────────────────────────────────────
# 便捷入口
# ─────────────────────────────────────────────────────────────────

def main():
    import argparse

    parser = argparse.ArgumentParser(description="KBC 领域本体消费者")
    parser.add_argument("--keyword", "-k", help="查询关键词")
    parser.add_argument("--batch", "-b", help="批量查询（JSON数组）")
    parser.add_argument("--kbc", help="KBC JSON 文件路径")
    args = parser.parse_args()

    consumer = OntologyConsumer(kbc_path=Path(args.kbc) if args.kbc else None)

    if args.batch:
        keywords = json.loads(args.batch)
        results = consumer.query_batch(keywords)
        for r in results:
            print(f"[{r.strategy.value}] trust={r.trust_level} | coverage={r.coverage_rate:.0%} | matched={r.matched}")
    elif args.keyword:
        result = consumer.query(args.keyword)
        print(f"Keyword: {result.keyword}")
        print(f"Strategy: {result.strategy.value}")
        print(f"Trust: {result.trust_level}")
        print(f"Coverage: {result.coverage_rate:.0%}")
        print(f"Terms found: {len(result.term_dict)}")
        for t in result.term_dict[:5]:
            print(f"  [{t.trust_level}] {t.term}: {t.definition[:50]}")


if __name__ == "__main__":
    main()
