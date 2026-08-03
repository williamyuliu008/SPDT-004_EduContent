# -*- coding: utf-8 -*-
"""
ingest_raw_material.py — 原材料预处理器
==========================================
对应 SOP v4.0 M2 预处理阶段（质量校准之前）。

职责：
  将多种原始素材（PDF/古籍OCR/网络URL/Markdown）统一转换为
  结构化的 RawKnowledgeEntry 列表，输出给 ingest_quality_calibrator。

输入类型：
  - PDF（考纲）     → pdfplumber 提取文本 + 表格
  - Markdown        → 标题/列表/表格结构解析
  - OCR（古籍）     → pytesseract + 语言模型校正
  - URL（网络）     → 爬取 + 去广告 + 正文提取

输出：
  list[RawKnowledgeEntry]（送入双Agent校准器）
"""

from __future__ import annotations

import json
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional, Callable

import yaml


# ─────────────────────────────────────────────────────────────────
# 数据结构
# ─────────────────────────────────────────────────────────────────

class RawMaterialType(Enum):
    PDF = "pdf"
    MARKDOWN = "markdown"
    OCR_IMAGE = "ocr_image"
    OCR_TEXT = "ocr_text"
    WEB_URL = "web_url"
    JSON = "json"
    UNKNOWN = "unknown"


@dataclass
class RawKnowledgeEntry:
    """原材料预处理输出单元"""
    raw_id: str                          # RAW_前缀唯一ID
    source_type: RawMaterialType
    source_path: str                     # 原始文件路径或URL
    source_title: str                    # 自动提取的标题
    text_content: str                    # 清洗后的纯文本
    structured_hints: dict[str, Any]     # 结构化线索（供后续解析参考）
    estimated_trust: str                 # A/B/C/D/E 可信度初估
    extracted_at: str                    # ISO时间戳
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "raw_id": self.raw_id,
            "source_type": self.source_type.value,
            "source_path": self.source_path,
            "source_title": self.source_title,
            "text_content": self.text_content,
            "structured_hints": self.structured_hints,
            "estimated_trust": self.estimated_trust,
            "extracted_at": self.extracted_at,
            "metadata": self.metadata,
        }


# ─────────────────────────────────────────────────────────────────
# 核心处理器
# ─────────────────────────────────────────────────────────────────

class RawMaterialPreprocessor:
    """
    原材料预处理器

    使用方式：
      preprocessor = RawMaterialPreprocessor()
      entries = preprocessor.preprocess("/path/to/material")
    """

    def __init__(self, trust_levels_config: Optional[Path] = None):
        self.trust_levels = self._load_trust_config(trust_levels_config)
        self._preprocessors: dict[RawMaterialType, Callable] = {
            RawMaterialType.PDF: self._process_pdf,
            RawMaterialType.MARKDOWN: self._process_markdown,
            RawMaterialType.OCR_TEXT: self._process_ocr_text,
            RawMaterialType.OCR_IMAGE: self._process_ocr_image,
            RawMaterialType.WEB_URL: self._process_web_url,
            RawMaterialType.JSON: self._process_json,
        }

    # ─────────────────────────────────────────────────────────────
    # 公开 API
    # ─────────────────────────────────────────────────────────────

    def preprocess(
        self,
        raw_source: Path | str | dict,
        force_type: Optional[RawMaterialType] = None,
    ) -> list[RawKnowledgeEntry]:
        """
        预处理入口。

        参数：
          raw_source — 文件路径 / URL字符串 / dict（直接传入结构化数据）
          force_type  — 强制指定类型（绕过自动检测）

        返回：
          list[RawKnowledgeEntry]
        """
        # 1. 自动检测类型
        if force_type:
            mat_type = force_type
        elif isinstance(raw_source, dict):
            mat_type = RawMaterialType.JSON
        elif isinstance(raw_source, (Path, str)):
            raw_str = str(raw_source)
            # 内联 JSON 字符串检测（以 { 或 [ 开头）
            if raw_str.strip().startswith(('{', '[')):
                mat_type = RawMaterialType.JSON
                try:
                    raw_source = json.loads(raw_str)
                except json.JSONDecodeError:
                    mat_type = RawMaterialType.UNKNOWN
            else:
                mat_type = self._detect_type(raw_str)
        else:
            mat_type = RawMaterialType.UNKNOWN

        # 2. 执行对应处理器
        processor = self._preprocessors.get(mat_type, self._process_unknown)
        entries = processor(raw_source)

        # 3. 统一后处理
        entries = self._postprocess(entries)
        return entries

    def preprocess_batch(
        self, sources: list[Path | str | dict]
    ) -> list[RawKnowledgeEntry]:
        """批量预处理"""
        result: list[RawKnowledgeEntry] = []
        for src in sources:
            result.extend(self.preprocess(src))
        return result

    # ─────────────────────────────────────────────────────────────
    # 各类型处理器
    # ─────────────────────────────────────────────────────────────

    def _process_pdf(self, raw: Path | str) -> list[RawKnowledgeEntry]:
        """PDF 提取（考纲 PDF）"""
        path = Path(raw)
        entries: list[RawKnowledgeEntry] = []

        try:
            import pdfplumber
        except ImportError:
            return self._fallback_error(
                raw, "pdfplumber not installed. Run: pip install pdfplumber"
            )

        try:
            with pdfplumber.open(path) as pdf:
                for i, page in enumerate(pdf.pages):
                    text = page.extract_text() or ""
                    tables = page.extract_tables()

                    if text.strip():
                        entries.append(RawKnowledgeEntry(
                            raw_id=f"RAW_PDF_{uuid.uuid4().hex[:8]}",
                            source_type=RawMaterialType.PDF,
                            source_path=str(path),
                            source_title=self._extract_title_from_text(text) or path.stem,
                            text_content=text,
                            structured_hints={
                                "page_num": i + 1,
                                "total_pages": len(pdf.pages),
                                "tables_count": len(tables),
                                "tables": [
                                    self._table_to_str(t) for t in tables
                                ] if tables else [],
                            },
                            estimated_trust="C",
                            extracted_at=datetime.now().isoformat(),
                            metadata={"file": path.name, "size_bytes": path.stat().st_size},
                        ))

            # 尝试提取元数据
            if hasattr(pdf, "metadata") and pdf.metadata:
                if entries:
                    entries[0].metadata["pdf_meta"] = pdf.metadata

        except Exception as e:
            return self._fallback_error(raw, f"PDF processing error: {e}")

        return entries

    def _process_markdown(self, raw: Path | str) -> list[RawKnowledgeEntry]:
        """Markdown 结构解析"""
        path = Path(raw)
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            content = path.read_text(encoding="gbk", errors="replace")

        # 提取标题层级
        headings = []
        for line in content.splitlines():
            m = re.match(r'^(#{1,6})\s+(.+)', line)
            if m:
                level = len(m.group(1))
                text = m.group(2).strip()
                headings.append({"level": level, "text": text})

        # 提取列表项（潜在考点）
        list_items = []
        for line in content.splitlines():
            m = re.match(r'^[-*+]\s+(.+)', line.strip())
            if m:
                list_items.append(m.group(1).strip())

        # 提取表格
        tables = self._extract_markdown_tables(content)

        # 估算信任级别
        trust = self._estimate_trust_from_markdown(content)

        return [RawKnowledgeEntry(
            raw_id=f"RAW_MD_{uuid.uuid4().hex[:8]}",
            source_type=RawMaterialType.MARKDOWN,
            source_path=str(path),
            source_title=headings[0]["text"] if headings else path.stem,
            text_content=self._clean_markdown(content),
            structured_hints={
                "headings": headings,
                "list_items": list_items,
                "tables_count": len(tables),
                "tables": tables,
                "word_count": len(content),
            },
            estimated_trust=trust,
            extracted_at=datetime.now().isoformat(),
            metadata={"file": path.name},
        )]

    def _process_ocr_text(self, raw: Path | str) -> list[RawKnowledgeEntry]:
        """
        古籍纯文本 OCR 预处理。
        重点：繁简转换、古籍专有名词校正、说文部首标注。
        """
        path = Path(raw)
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            content = path.read_text(encoding="gbk", errors="replace")

        # 1. 繁→简 转换（基于字符映射）
        simplified = self._tc_to_sc(content)

        # 2. 常见OCR错误校正
        corrected = self._ocr_corrector(simplified)

        # 3. 检测是否为《说文解字》类古籍
        is_shuowen = any(kw in corrected for kw in ["540部", "六书", "说文", "从某", "某声"])

        # 4. 段落拆分（古籍通常无换行）
        paragraphs = self._split_ancient_text(corrected)

        entries: list[RawKnowledgeEntry] = []
        for i, para in enumerate(paragraphs):
            if len(para) < 10:
                continue
            entries.append(RawKnowledgeEntry(
                raw_id=f"RAW_OCR_{uuid.uuid4().hex[:8]}",
                source_type=RawMaterialType.OCR_TEXT,
                source_path=str(path),
                source_title=f"{path.stem} 第{i+1}段",
                text_content=para,
                structured_hints={
                    "para_index": i,
                    "total_paras": len(paragraphs),
                    "is_shuowen_style": is_shuowen,
                    "contains_radical_info": "部首" in para or "从某" in para,
                    "contains_liushu": "六书" in para,
                },
                estimated_trust="B" if is_shuowen else "C",
                extracted_at=datetime.now().isoformat(),
                metadata={
                    "file": path.name,
                    "original_encoding": "gbk" if "?" in content[:10] else "utf-8",
                },
            ))

        return entries if entries else self._fallback_error(raw, "No paragraphs extracted")

    def _process_ocr_image(self, raw: Path | str) -> list[RawKnowledgeEntry]:
        """图片 OCR（古籍影印件）"""
        path = Path(raw)

        try:
            import pytesseract
        except ImportError:
            return self._fallback_error(
                raw, "pytesseract not installed. Run: pip install pytesseract"
            )

        try:
            from PIL import Image
        except ImportError:
            return self._fallback_error(
                raw, "Pillow not installed. Run: pip install pillow"
            )

        try:
            img = Image.open(path)
            text = pytesseract.image_to_string(img, lang='chi_sim+chi_tra')
            return [RawKnowledgeEntry(
                raw_id=f"RAW_IMGOCR_{uuid.uuid4().hex[:8]}",
                source_type=RawMaterialType.OCR_IMAGE,
                source_path=str(path),
                source_title=path.stem,
                text_content=text.strip(),
                structured_hints={"ocr_confidence": "low"},  # 未配置 tesseract 置信度
                estimated_trust="D",     # 图片 OCR 默认较低
                extracted_at=datetime.now().isoformat(),
                metadata={"image_size": img.size, "image_mode": img.mode},
            )]
        except Exception as e:
            return self._fallback_error(raw, f"OCR error: {e}")

    def _process_web_url(self, raw: str) -> list[RawKnowledgeEntry]:
        """
        网络 URL 爬取。
        流程：fetch → 去广告/导航 → 正文提取 → 结构化 → 可信度初估
        """
        import urllib.request
        import urllib.error

        url = str(raw)

        try:
            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36"
                    )
                },
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                html = resp.read()
                # 优先尝试 utf-8，fallback gb18030
                try:
                    text = html.decode("utf-8")
                except UnicodeDecodeError:
                    text = html.decode("gb18030", errors="replace")

        except urllib.error.URLError as e:
            return self._fallback_error(raw, f"URL fetch error: {e}")
        except Exception as e:
            return self._fallback_error(raw, f"Network error: {e}")

        # 正文提取（简单规则：去 script/style/nav，去除空行）
        clean_text = self._extract_main_content(text)

        # 标题提取
        title_m = re.search(r'<title>([^<]+)</title>', text, re.IGNORECASE)
        title = title_m.group(1).strip() if title_m else url

        # 可信度初估（域名判断）
        trust = self._estimate_trust_from_url(url)

        return [RawKnowledgeEntry(
            raw_id=f"RAW_URL_{uuid.uuid4().hex[:8]}",
            source_type=RawMaterialType.WEB_URL,
            source_path=url,
            source_title=title,
            text_content=clean_text,
            structured_hints={
                "domain": self._extract_domain(url),
                "url_path_depth": url.count('/') - 3,
            },
            estimated_trust=trust,
            extracted_at=datetime.now().isoformat(),
            metadata={"content_length": len(clean_text)},
        )]

    def _process_json(self, raw: dict | Path | str) -> list[RawKnowledgeEntry]:
        """JSON 结构化数据（dict / Path指向的.json文件 / 内联JSON字符串）"""
        entries: list[RawKnowledgeEntry] = []

        # 如果是文件路径，先读取内容
        if isinstance(raw, (Path, str)):
            raw_path = Path(raw) if isinstance(raw, Path) else Path(raw)
            if raw_path.suffix.lower() == ".json" and raw_path.exists():
                try:
                    with open(raw_path, encoding="utf-8") as f:
                        raw = json.load(f)
                except UnicodeDecodeError:
                    try:
                        with open(raw_path, encoding="gbk", errors="replace") as f:
                            raw = json.load(f)
                    except Exception:
                        return self._fallback_error(raw, f"JSON parse error: {raw_path}")
                # 注入文件路径供后续使用
                if isinstance(raw, dict):
                    raw["_source_path"] = str(raw_path)
            else:
                # 不是 .json 文件，按 dict 处理
                source_path = str(raw_path)
                return [RawKnowledgeEntry(
                    raw_id=f"RAW_JSON_{uuid.uuid4().hex[:8]}",
                    source_type=RawMaterialType.JSON,
                    source_path=source_path,
                    source_title=raw_path.stem,
                    text_content=str(raw),
                    structured_hints={},
                    estimated_trust="E",
                    extracted_at=datetime.now().isoformat(),
                    metadata={},
                )]

        if isinstance(raw, list):
            items = raw
            source_path = "<inline_json>"
        elif isinstance(raw, dict):
            # 已知数组字段：items / knowledge_entries / entries
            items = raw.get(
                "items", raw.get("knowledge_entries", raw.get("entries", [raw]))
            )
            source_path = raw.get("_source_path", "<inline_json>")
        else:
            items = [raw]
            source_path = "<inline_json>"

        for i, item in enumerate(items):
            if isinstance(item, dict):
                text = item.get("definition", item.get("content", item.get("text", str(item))))
                title = item.get("concept", item.get("name", item.get("title", f"Item_{i}")))
                trust = item.get("trust", item.get("estimated_trust", "D"))

                entries.append(RawKnowledgeEntry(
                    raw_id=f"RAW_JSON_{uuid.uuid4().hex[:8]}",
                    source_type=RawMaterialType.JSON,
                    source_path=source_path,
                    source_title=str(title),
                    text_content=str(text),
                    structured_hints={
                        "original_keys": list(item.keys()),
                        "index": i,
                    },
                    estimated_trust=str(trust),
                    extracted_at=datetime.now().isoformat(),
                    metadata=item,
                ))

        return entries if entries else self._fallback_error(raw, "No items in JSON")

    def _process_unknown(self, raw: Any) -> list[RawKnowledgeEntry]:
        return self._fallback_error(raw, f"Unknown source type: {type(raw)}")

    # ─────────────────────────────────────────────────────────────
    # 工具方法
    # ─────────────────────────────────────────────────────────────

    def _detect_type(self, path_str: str) -> RawMaterialType:
        """根据路径推断素材类型"""
        path_lower = path_str.lower()
        if path_lower.endswith(".pdf"):
            return RawMaterialType.PDF
        if path_lower.endswith((".md", ".markdown")):
            return RawMaterialType.MARKDOWN
        if path_lower.endswith((".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".gif")):
            return RawMaterialType.OCR_IMAGE
        if path_lower.endswith((".txt", ".ocr")):
            return RawMaterialType.OCR_TEXT
        if path_lower.startswith("http://") or path_lower.startswith("https://"):
            return RawMaterialType.WEB_URL
        if path_lower.endswith(".json"):
            return RawMaterialType.JSON
        return RawMaterialType.UNKNOWN

    def _load_trust_config(self, config_path: Optional[Path]) -> dict:
        if config_path and config_path.exists():
            with open(config_path, encoding="utf-8") as f:
                return yaml.safe_load(f)
        # 内置默认值
        return {
            "trust_levels": {
                "A": {"weight": 1.0},
                "B": {"weight": 0.85},
                "C": {"weight": 0.7},
                "D": {"weight": 0.45},
                "E": {"weight": 0.2},
            }
        }

    def _postprocess(
        self, entries: list[RawKnowledgeEntry]
    ) -> list[RawKnowledgeEntry]:
        """统一后处理：去重 + 过滤极短内容"""
        seen_texts: set[str] = set()
        result: list[RawKnowledgeEntry] = []

        for entry in entries:
            # 过滤极短内容
            if len(entry.text_content.strip()) < 5:
                continue
            # 简单去重（按文本前50字符）
            short_sig = entry.text_content[:50].strip()
            if short_sig in seen_texts:
                continue
            seen_texts.add(short_sig)
            result.append(entry)

        return result

    def _fallback_error(
        self, raw: Any, error_msg: str
    ) -> list[RawKnowledgeEntry]:
        return [RawKnowledgeEntry(
            raw_id=f"RAW_ERR_{uuid.uuid4().hex[:8]}",
            source_type=RawMaterialType.UNKNOWN,
            source_path=str(raw),
            source_title="ERROR",
            text_content="",
            structured_hints={},
            estimated_trust="E",
            extracted_at=datetime.now().isoformat(),
            metadata={"error": error_msg},
        )]

    # ─── 古籍 OCR 专用 ────────────────────────────────────────

    def _tc_to_sc(self, text: str) -> str:
        """繁体→简体 转换（覆盖常见书法/古籍用字）"""
        # 简版映射（高频字）
        tc_map = {
            "書": "书", "學": "学", "說": "说", "文": "文",
            "字": "字", "解": "解", "從": "从", "聲": "声",
            "雲": "云", "雲": "云", "餘": "余", "餘": "余",
            "裏": "里", "裡": "里", "後": "后", "萬": "万",
            "與": "与", "為": "为", "稱": "称", "號": "号",
            "見": "见", "間": "间", "長": "长", "門": "门",
            "義": "义", "點": "点", "類": "类",
        }
        for tc, sc in tc_map.items():
            text = text.replace(tc, sc)
        return text

    def _ocr_corrector(self, text: str) -> str:
        """常见 OCR 错误自动校正"""
        corrections = [
            # 数字混淆
            ("０", "0"), ("１", "1"), ("２", "2"), ("３", "3"),
            ("４", "4"), ("５", "5"), ("６", "6"), ("７", "7"),
            ("８", "8"), ("９", "9"),
            # 常见误识别
            ("一丨", "一|"), ("丨一", "|一"),
        ]
        for wrong, correct in corrections:
            text = text.replace(wrong, correct)
        return text

    def _split_ancient_text(self, text: str) -> list[str]:
        """古籍文本按句子/段拆分"""
        # 按常见古籍断句符拆分
        sentences = re.split(r'[。；！？】』」』\n]+', text)
        # 再合并为段落（每3-5句一段）
        paragraphs: list[str] = []
        chunk: list[str] = []
        for sent in sentences:
            sent = sent.strip()
            if not sent:
                continue
            chunk.append(sent)
            if len(chunk) >= 4:
                paragraphs.append("".join(chunk))
                chunk = []
        if chunk:
            paragraphs.append("".join(chunk))
        return paragraphs

    # ─── Markdown 专用 ─────────────────────────────────────────

    def _extract_markdown_tables(self, md: str) -> list[list[list[str]]]:
        """提取 Markdown 表格（返回 列表[行[列]]）"""
        tables: list[list[list[str]]] = []
        lines = md.splitlines()
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            # 检测表格行（至少2个 |）
            if line.count("|") >= 3 and not line.startswith("#"):
                rows = []
                while i < len(lines) and lines[i].strip().count("|") >= 2:
                    rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                    i += 1
                # 跳过分隔行（如 |---|---|）
                if rows and all(
                    all(c in ("-", "") for c in row)
                    for row in rows if len(row) == 1
                ):
                    pass
                else:
                    tables.append(rows)
            else:
                i += 1
        return tables

    def _estimate_trust_from_markdown(self, content: str) -> str:
        """从 Markdown 内容判断可信度"""
        if any(kw in content for kw in ["官方", "考纲", "教育部", "中国美术学院"]):
            return "C"
        if any(kw in content for kw in ["Wikipedia", "维基", "来源不明"]):
            return "D"
        return "C"

    # ─── Web 专用 ─────────────────────────────────────────────

    def _extract_main_content(self, html: str) -> str:
        """简单正文提取（去 script/style/nav/footer）"""
        # 去 HTML 标签
        text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<nav[^>]*>.*?</nav>', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<footer[^>]*>.*?</footer>', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<[^>]+>', '', text)
        # 去多余空白
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r' {2,}', ' ', text)
        return text.strip()

    def _extract_domain(self, url: str) -> str:
        m = re.search(r'https?://([^/]+)', url)
        return m.group(1) if m else url

    def _estimate_trust_from_url(self, url: str) -> str:
        """从域名判断可信度"""
        domain = self._extract_domain(url).lower()
        if any(kw in domain for kw in ["gov.cn", "edu.cn", "org.cn", "ac.cn"]):
            return "C"
        if any(kw in domain for kw in ["wikipedia", "baike.baidu", "wiki"]):
            return "D"
        if any(kw in domain for kw in ["zhihu", "weibo", "blog", "tieba"]):
            return "E"
        return "E"

    # ─── 通用 ─────────────────────────────────────────────────

    def _extract_title_from_text(self, text: str) -> Optional[str]:
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        # 取第一行作为标题（如果是短行）
        if lines and len(lines[0]) < 80:
            return lines[0]
        return None

    def _clean_markdown(self, md: str) -> str:
        """去除 Markdown 标记，保留纯文本"""
        text = re.sub(r'#{1,6}\s+', '', md)
        text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
        text = re.sub(r'[*_`~]{1,3}', '', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()

    def _table_to_str(self, table: list[list[str]]) -> str:
        """表格→字符串（用于存储在 structured_hints）"""
        if not table:
            return ""
        rows = [" | ".join(row) for row in table]
        return "\n".join(rows)


# ─────────────────────────────────────────────────────────────────
# 便捷 CLI 入口
# ─────────────────────────────────────────────────────────────────

def main():
    import argparse

    parser = argparse.ArgumentParser(description="原材料预处理器")
    parser.add_argument("source", help="素材路径（文件/URL/JSON字符串）")
    parser.add_argument("-t", "--type", choices=["pdf", "md", "ocr", "url", "json"],
                        help="强制指定类型")
    parser.add_argument("-o", "--output", help="输出JSON路径")
    args = parser.parse_args()

    preprocessor = RawMaterialPreprocessor()

    # JSON 内联处理
    if args.source.startswith("{"):
        raw = json.loads(args.source)
    else:
        raw = args.source

    force_type = None
    if args.type:
        type_map = {
            "pdf": RawMaterialType.PDF,
            "md": RawMaterialType.MARKDOWN,
            "ocr": RawMaterialType.OCR_TEXT,
            "url": RawMaterialType.WEB_URL,
            "json": RawMaterialType.JSON,
        }
        force_type = type_map.get(args.type)

    entries = preprocessor.preprocess(raw, force_type=force_type)

    output = [e.to_dict() for e in entries]
    text = json.dumps(output, ensure_ascii=False, indent=2)

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(text, encoding="utf-8")
        print(f"Output: {args.output} ({len(entries)} entries)")
    else:
        print(text[:2000])  # 截断显示
        if len(text) > 2000:
            print(f"\n... [{len(entries)} entries total]")


if __name__ == "__main__":
    main()
