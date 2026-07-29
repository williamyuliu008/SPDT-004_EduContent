"""
知识库加载器 — PT-037 MVP
从配置包 JSON/YAML 文件中读取知识条目、模板、剧本、题库
"""

import json
import os
from pathlib import Path
from typing import Optional, Any
from dataclasses import dataclass, field


# ─── 数据类定义 ─────────────────────────────────────────────────────────────

@dataclass
class KnowledgeEntry:
    """单条知识条目"""
    kb_id: str
    concept: str
    definition: str
    tags: list[str] = field(default_factory=list)
    exam_tips: dict = field(default_factory=dict)
    structured_content: dict = field(default_factory=dict)
    cross_pack_links: list[dict] = field(default_factory=list)
    pack_id: str = ""
    answer_template: str = ""
    example_questions: list[str] = field(default_factory=list)


@dataclass
class TranslationEntry:
    """译篆条目（一简对多篆）"""
    kb_id: str
    concept: str
    definition: str
    tags: list[str] = field(default_factory=list)
    exam_tips: dict = field(default_factory=dict)


@dataclass
class PunctuationText:
    """句读翻译文本"""
    text_id: str
    source: str
    category: str
    difficulty: str
    raw_text: str
    punctuated: str = ""
    translation: str = ""
    tags: list[str] = field(default_factory=list)


@dataclass
class ErrorScript:
    """错题剧本"""
    script_id: str
    error_type: str
    question_type: str
    difficulty: str
    trigger_kb_id: str
    question: dict
    script: dict
    meta: dict = field(default_factory=dict)


@dataclass
class Ability:
    """能力清单条目"""
    ability_id: str
    name: str
    question_types: list[str]
    method_破题心法: str
    method_答题手法: str
    scaffolding: dict
    scoring: dict
    priority: int


# ─── 知识库主类 ─────────────────────────────────────────────────────────────

class KnowledgeBase:
    """
    书法配置包知识库加载器。

    用法:
        kb = KnowledgeBase.from_pack("D:\\...\\cafa_calligraphy_2026")
        entry = kb.get_entry("KB_CAFA_S001")
        texts = kb.get_texts_by_difficulty("Lv3")
    """

    def __init__(
        self,
        pack_root: str | Path,
        pack_id: str = "cafa_calligraphy_2026"
    ):
        self.pack_root = Path(pack_root)
        self.pack_id = pack_id
        self._kb_entries: dict[str, KnowledgeEntry] = {}
        self._translation_entries: dict[str, TranslationEntry] = {}
        self._punctuation_texts: dict[str, PunctuationText] = {}
        self._error_scripts: dict[str, ErrorScript] = {}
        self._abilities: dict[str, Ability] = {}
        self._meta: dict = {}
        self._tags: dict = {}
        self._load_all()

    @classmethod
    def from_pack(cls, pack_path: str | Path, pack_id: str = "cafa_calligraphy_2026"):
        return cls(pack_path, pack_id)

    @classmethod
    def from_relative(cls, relative_to: str | Path = None):
        """从 PT-037 目录相对路径加载默认书法包"""
        if relative_to is None:
            relative_to = Path(__file__).parent.parent.parent.parent
        pack_path = relative_to / "_03_subject_packs" / "cafa_calligraphy_2026"
        return cls(pack_path)

    def _load_all(self):
        """加载所有数据"""
        self._load_meta()
        self._load_tags()
        self._load_kb_vocab()
        self._load_punctuation_library()
        self._load_error_scripts()
        self._load_abilities()

    # ─── 加载方法 ────────────────────────────────────────────────────────────

    def _load_meta(self):
        p = self.pack_root / "meta.json"
        if p.exists():
            with open(p, "r", encoding="utf-8") as f:
                self._meta = json.load(f)

    def _load_tags(self):
        p = self.pack_root / "knowledge" / "tags.json"
        if p.exists():
            with open(p, "r", encoding="utf-8") as f:
                self._tags = json.load(f)

    def _load_kb_vocab(self):
        # 优先使用增强后的知识库
        # pack_root = cafa_calligraphy_2026/ 或 cafa_calligraphy_2026/knowledge/
        kb_dir = self.pack_root / "knowledge" if (self.pack_root / "knowledge").exists() else self.pack_root
        p_enhanced = kb_dir / "kb_vocab_enhanced.json"
        p = p_enhanced if p_enhanced.exists() else (kb_dir / "kb_vocab.json")
        if not p.exists():
            return

        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)

        def _classify_and_load(item):
            """根据 kb_id 前缀决定存到哪个库"""
            if not isinstance(item, dict) or "kb_id" not in item:
                return
            kb_id = item["kb_id"]

            # KB_CAFA_Q* → 句读文本，不进知识库（由 _load_punctuation_library 独立处理）
            if kb_id.startswith("KB_CAFA_Q"):
                return
            # KB_CAFA_T* → 译篆条目
            if kb_id.startswith("KB_CAFA_T"):
                self._parse_translation_entry(item)
            # KB_CAFA_S* / 其他 → 书法史知识条目
            else:
                self._parse_entry(item)

        # 递归扫描所有列表
        def _deep_scan(obj):
            if isinstance(obj, list):
                for item in obj:
                    if isinstance(item, dict) and "kb_id" in item:
                        _classify_and_load(item)
                    else:
                        _deep_scan(item)
            elif isinstance(obj, dict):
                for v in obj.values():
                    _deep_scan(v)

        _deep_scan(data)

    def _parse_entry(self, entry_data: dict):
        if not isinstance(entry_data, dict) or "kb_id" not in entry_data:
            return
        kb_id = entry_data.get("kb_id", "")
        tags = entry_data.get("tags", [])
        exam_tips = entry_data.get("exam_tips", {})
        cross_links = entry_data.get("cross_pack_links", [])

        entry = KnowledgeEntry(
            kb_id=kb_id,
            concept=entry_data.get("concept", ""),
            definition=entry_data.get("definition", ""),
            tags=tags,
            exam_tips=exam_tips,
            structured_content=entry_data.get("structured_content", {}),
            cross_pack_links=cross_links,
            pack_id=self.pack_id,
            answer_template=entry_data.get("answer_template", ""),
            example_questions=entry_data.get("example_questions", [])
        )
        self._kb_entries[kb_id] = entry

    def _parse_translation_entry(self, entry_data: dict):
        if not isinstance(entry_data, dict) or "kb_id" not in entry_data:
            return
        kb_id = entry_data.get("kb_id", "")
        entry = TranslationEntry(
            kb_id=kb_id,
            concept=entry_data.get("concept", ""),
            definition=entry_data.get("definition", ""),
            tags=entry_data.get("tags", []),
            exam_tips=entry_data.get("exam_tips", {})
        )
        self._translation_entries[kb_id] = entry

    def _load_punctuation_library(self):
        p = self.pack_root / "scripts" / "punctuation_library.json"
        if not p.exists():
            return

        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)

        for text_data in data.get("texts", []):
            text_id = text_data.get("text_id", "")
            pt = PunctuationText(
                text_id=text_id,
                source=text_data.get("source", ""),
                category=text_data.get("category", ""),
                difficulty=text_data.get("difficulty", "Lv2"),
                raw_text=text_data.get("raw_text", ""),
                punctuated=text_data.get("punctuated", ""),
                translation=text_data.get("translation", ""),
                tags=text_data.get("tags", [])
            )
            self._punctuation_texts[text_id] = pt

    def _load_error_scripts(self):
        p = self.pack_root / "scripts" / "error_scripts.json"
        if not p.exists():
            return

        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)

        for script_data in data.get("scripts", []):
            script_id = script_data.get("script_id", "")
            es = ErrorScript(
                script_id=script_id,
                error_type=script_data.get("error_type", ""),
                question_type=script_data.get("question_type", ""),
                difficulty=script_data.get("difficulty", "Lv2"),
                trigger_kb_id=script_data.get("trigger_kb_id", ""),
                question=script_data.get("question", {}),
                script=script_data.get("script", {}),
                meta=script_data.get("meta", {})
            )
            self._error_scripts[script_id] = es

    def _load_abilities(self):
        p = self.pack_root / "capability" / "ability_list.json"
        if not p.exists():
            return

        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)

        for ab_data in data.get("abilities", []):
            ability_id = ab_data.get("ability_id", "")
            ab = Ability(
                ability_id=ability_id,
                name=ab_data.get("name", ""),
                question_types=ab_data.get("question_types", []),
                method_破题心法=ab_data.get("破题心法", ""),
                method_答题手法=ab_data.get("答题手法", ""),
                scaffolding=ab_data.get("scaffolding", {}),
                scoring=ab_data.get("scoring", {}),
                priority=ab_data.get("priority", 3)
            )
            self._abilities[ability_id] = ab

    # ─── 查询接口 ────────────────────────────────────────────────────────────

    def get_entry(self, kb_id: str) -> Optional[KnowledgeEntry]:
        return self._kb_entries.get(kb_id)

    def get_translation(self, kb_id: str) -> Optional[TranslationEntry]:
        return self._translation_entries.get(kb_id)

    def get_error_script(self, script_id: str) -> Optional[ErrorScript]:
        return self._error_scripts.get(script_id)

    def get_error_script_by_kb(self, kb_id: str) -> list[ErrorScript]:
        return [
            es for es in self._error_scripts.values()
            if es.trigger_kb_id == kb_id
        ]

    def get_texts_by_difficulty(self, difficulty: str) -> list[PunctuationText]:
        return [
            pt for pt in self._punctuation_texts.values()
            if pt.difficulty == difficulty
        ]

    def get_texts_by_category(self, category: str) -> list[PunctuationText]:
        return [
            pt for pt in self._punctuation_texts.values()
            if pt.category == category
        ]

    def search_entries_by_tag(self, tag: str) -> list[KnowledgeEntry]:
        return [
            e for e in self._kb_entries.values()
            if tag in e.tags
        ]

    def get_top_starred_entries(self, min_stars: int = 4) -> list[KnowledgeEntry]:
        """获取高星级（考频高）的知识条目"""
        results = []
        for entry in self._kb_entries.values():
            for tag in entry.tags:
                if tag.startswith("#考频/"):
                    star_count = tag.count("⭐")
                    if star_count >= min_stars:
                        results.append(entry)
                        break
        # 按 kb_id 排序保证确定性
        results.sort(key=lambda e: e.kb_id)
        return results

    def get_high_priority_abilities(self) -> list[Ability]:
        return sorted(
            [a for a in self._abilities.values()],
            key=lambda a: -a.priority
        )

    def get_all_entries(self) -> list[KnowledgeEntry]:
        return list(self._kb_entries.values())

    def get_ability(self, ability_id: str) -> Optional[Ability]:
        return self._abilities.get(ability_id)

    def summary(self) -> dict:
        """返回知识库摘要"""
        return {
            "pack_id": self.pack_id,
            "pack_name": self._meta.get("pack_name", ""),
            "version": self._meta.get("version", ""),
            "total_kb_entries": len(self._kb_entries),
            "total_translation_entries": len(self._translation_entries),
            "total_punctuation_texts": len(self._punctuation_texts),
            "total_error_scripts": len(self._error_scripts),
            "total_abilities": len(self._abilities),
            "modules": [
                m.get("name", "")
                for m in self._meta.get("modules", [])
            ]
        }
