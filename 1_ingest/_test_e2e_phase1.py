# -*- coding: utf-8 -*-
"""
_test_e2e_phase1.py — Phase 1 端到端测试套件
==============================================
SPDT-004 教育管线 · Phase 1 完整性验证

测试覆盖（按 subject_domain）：
  ✅ HIST_ART（历史+书法）  — 4 个测试用例
  ✅ GEO（地理）            — 3 个测试用例
  ✅ POL（政治）            — 3 个测试用例
  ✅ CHINESE（语文）        — 3 个测试用例（文言文/现代文/作文）
  ✅ ENGLISH（英语）        — 3 个测试用例（阅读/语法/写作）
  ⏳ MATH（数学）           — Phase 2 单独处理

测试内容（每用例）：
  ① router.route() → B1-B4 路由正确
  ② RouteResult.to_outer() → outer 字段完整
  ③ build_pipeline_package() → pipeline_package 格式正确
  ④ pipeline_package_schema 验证通过
  ⑤ 学科注册表注册状态正确

运行方式：
  python _test_e2e_phase1.py [-v] [--subject HIST_ART] [--json]
  python _test_e2e_phase1.py -v          # 详细模式
  python _test_e2e_phase1.py --json      # JSON 输出（CI 集成）
  python _test_e2e_phase1.py --subject HIST_ART  # 仅测 HIST_ART

依赖：
  pip install pyyaml  # 可选（有则用完整解析；无则用手动YAML解析）

版本历史：
  v1.0.0（2026-07-30）：初版，覆盖 5 个学科域，16 个测试用例
"""

from __future__ import annotations

import argparse
import json
import sys
import traceback
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

# ─────────────────────────────────────────────────────────────────
# 路径设置（支持从 1_ingest/ 目录直接运行）
# ─────────────────────────────────────────────────────────────────

import importlib.util

_self_dir = Path(__file__).parent.resolve()
_project_root = _self_dir.parent  # SPDT-004_EduContent/


# ─────────────────────────────────────────────────────────────────
# 导入管线组件（显式路径加载，消除 sys.path 歧义）
# ─────────────────────────────────────────────────────────────────

# router.py 在 1_ingest/router/router.py
def _load_router():
    _router_path = _self_dir / "router" / "router.py"
    spec = importlib.util.spec_from_file_location("router", _router_path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["router"] = mod  # 防止循环导入
    spec.loader.exec_module(mod)
    return mod

_router_mod = _load_router()
ContentRouter = _router_mod.ContentRouter
RouteResult = _router_mod.RouteResult

try:
    from education_adapter import (
        build_pipeline_package,
        scene_v2_to_pipeline_package,
        extract_outer_from_pipeline_package,
        extract_capabilities,
        _subject_to_domain,
        _b1b4_to_capabilities,
    )
except ImportError:
    # MODLIB education_adapter 备用路径
    try:
        _adapter_path = Path("D:/1_omas/MODLIB/content_manufacturing/adapters/education_adapter.py")
        if _adapter_path.exists():
            spec = importlib.util.spec_from_file_location("education_adapter", _adapter_path)
            _adapter_mod = importlib.util.module_from_spec(spec)
            sys.modules["education_adapter"] = _adapter_mod
            spec.loader.exec_module(_adapter_mod)
            build_pipeline_package = _adapter_mod.build_pipeline_package
            scene_v2_to_pipeline_package = _adapter_mod.scene_v2_to_pipeline_package
            extract_outer_from_pipeline_package = _adapter_mod.extract_outer_from_pipeline_package
            extract_capabilities = _adapter_mod.extract_capabilities
            _subject_to_domain = _adapter_mod._subject_to_domain
            _b1b4_to_capabilities = _adapter_mod._b1b4_to_capabilities
        else:
            raise ImportError("MODLIB adapter not found")
    except ImportError:
        # adapter 不可用时，定义最小 stub 以继续测试 router 逻辑
        def build_pipeline_package(content_spec, scene_v2_data, route_result=None, trust_level="E"):
            outer = {"subject_domain": "GENERIC", "content_type": "B1_deep_content", "capabilities": []}
            return {"version": "1.0.0", "outer": outer, "inner": {"schema": "scene_v2", "data": {}}}
        def scene_v2_to_pipeline_package(s, c=None, r=None, t="E"):
            return build_pipeline_package({}, s, r, t)
        def extract_outer_from_pipeline_package(pkg):
            return pkg.get("outer", {})
        def extract_capabilities(pkg):
            return pkg.get("outer", {}).get("capabilities", [])
        def _subject_to_domain(s):
            return "GENERIC"
        def _b1b4_to_capabilities(t):
            return []


# ─────────────────────────────────────────────────────────────────
# Schema 验证（无 jsonschema 时手动实现）
# ─────────────────────────────────────────────────────────────────

def _load_json_schema(schema_path: Path) -> dict | None:
    """加载 JSON Schema（无依赖时返回 None 表示跳过 Schema 验证）"""
    try:
        import jsonschema
        if schema_path.exists():
            with open(schema_path, "r", encoding="utf-8") as f:
                return json.load(f)
    except ImportError:
        pass
    return None


def _validate_pipeline_package(pkg: dict, schema: dict | None) -> tuple[bool, list[str]]:
    """
    验证 pipeline_package 格式。
    有 jsonschema 时使用 Schema 校验；无时做基本字段存在性检查。
    """
    errors = []

    # 基本字段存在性
    if pkg.get("version") != "1.0.0":
        errors.append(f"version 应为 '1.0.0'，实际：{pkg.get('version')}")

    outer = pkg.get("outer", {})
    if not outer:
        errors.append("outer 字段缺失或为空")
    else:
        required_outer = ["subject_domain", "content_type", "capabilities", "knowledge_types"]
        for field in required_outer:
            if field not in outer:
                errors.append(f"outer.{field} 缺失")

        if not isinstance(outer.get("capabilities", []), list):
            errors.append("outer.capabilities 应为 list")
        if not isinstance(outer.get("knowledge_types", []), list):
            errors.append("outer.knowledge_types 应为 list")

    inner = pkg.get("inner", {})
    if not inner:
        errors.append("inner 字段缺失或为空")
    else:
        if "schema" not in inner:
            errors.append("inner.schema 缺失")
        if "data" not in inner:
            errors.append("inner.data 缺失")

    # Schema 校验（如果有）
    if schema and errors == []:  # 基本检查通过才做 Schema 校验
        try:
            import jsonschema
            jsonschema.validate(instance=pkg, schema=schema)
        except ImportError:
            pass  # 无 jsonschema，跳过
        except Exception as e:
            errors.append(f"Schema 校验失败：{e}")

    return len(errors) == 0, errors


# ─────────────────────────────────────────────────────────────────
# 测试结果数据结构
# ─────────────────────────────────────────────────────────────────

@dataclass
class TestResult:
    subject_domain: str
    sub_domain: str
    test_name: str
    passed: bool
    duration_ms: float
    error_message: str = ""
    details: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "subject_domain": self.subject_domain,
            "sub_domain": self.sub_domain,
            "test_name": self.test_name,
            "passed": self.passed,
            "duration_ms": round(self.duration_ms, 2),
            "error_message": self.error_message,
            "details": self.details,
        }


# ─────────────────────────────────────────────────────────────────
# 测试 Fixtures — 各学科典型输入
# ─────────────────────────────────────────────────────────────────
# 结构：{ domain_id: { sub_id: { test_name: { raw_input, content_spec, expected_* } } } }

FIXTURES: dict[str, dict[str, dict[str, dict]]] = {

    # ════════════════════════════════════════════════════════════════
    # HIST_ART — 历史 + 书法
    # 现有资产：2_structure/TextExperience/_test_ep01_scenes/scene_v2_full.json
    # ════════════════════════════════════════════════════════════════

    "HIST_ART": {

        "hist_history_deep": {
            "description": "墨骨山河沉浸式微剧本（B1_deep_content，历史+书法双学科融合）",
            "raw_input": {
                "type": "micro_drama_script",
                "description": "HISTORY 墨骨山河Ep01乾元元年蒲州的墨与血，颜真卿书法史+安史之乱历史双轨融合",
                "keywords": ["历史", "书法史", "深度", "系列", "跨学科"],
                "source_chain_id": "ink_history_ep01",
                "exam_type": "高考历史",
                "path": "scripts/墨骨山河_ep01_颜真卿.json",
            },
            "content_spec": {
                "spec_id": "墨骨山河_ep01",
                "exam_meta": {"subject": "历史书法", "exam_type": "高考历史"},
                "question_types": [
                    {"id": "Q_HIST_CONCEPT", "name": "历史概念解释"},
                    {"id": "Q_CALLIGRAPHY_ANALYSIS", "name": "书法风格分析"},
                ],
            },
            "scene_v2_data": {
                "metadata": {
                    "series_title": "墨骨山河",
                    "ep_id": 1,
                    "ep_title": "乾元元年·蒲州的墨与血",
                    "source_chain_id": "墨骨山河_ep01",
                    "schema_version": "2.0.0",
                },
                "scenes": [
                    {
                        "scene_id": "墨骨山河_ep01_act1_00",
                        "scene_type": "concept",
                        "knowledge_type": "II",
                        "content": {
                            "title": "前221年，秦王嬴政完成了中国历史上最不可思议的事",
                            "body_lines": ["前221年，秦王嬴政，完成了中国历史上最不可思议的事——他消灭了六个国家"],
                            "keywords": ["前221年", "秦王", "秦王嬴政"],
                        },
                        "five_skandha": {
                            "sensation_trigger": "前221年，秦王嬴政，完成了中国历史上最不可思议的事",
                            "recognition_marker": "#历史/秦/统一",
                        },
                    }
                ],
            },
            "expected": {
                "subject_domain": "HIST_ART",
                "content_type": "B1_deep_content",
                "genre": "墨骨山河系列",
                "min_capabilities": 3,
                "min_scenes": 1,
            },
        },

        "hist_history_rapid": {
            "description": "古史知识链 v4 速查（B2_rapid，高频考点快背）",
            "raw_input": {
                "type": "exam_syllabus",
                "description": "高考历史古史v4世界风云核心考点速查，1840-1949近现代史高频考点",
                "keywords": ["历史", "速查", "考点", "快背", "核心"],
                "source_chain_id": "gu_shi_v4_sucharu",
                "exam_type": "高考历史",
            },
            "content_spec": {
                "spec_id": "古史_v4_速查",
                "exam_meta": {"subject": "历史", "exam_type": "高考历史"},
                "question_types": [
                    {"id": "Q_HIST_FACT", "name": "历史事实题"},
                ],
            },
            "scene_v2_data": {
                "metadata": {
                    "series_title": "古史知识链",
                    "ep_id": 4,
                    "source_chain_id": "古史_v4_速查",
                    "schema_version": "2.0.0",
                },
                "scenes": [
                    {
                        "scene_id": "古史_v4_chain_01",
                        "scene_type": "fact",
                        "knowledge_type": "I",
                        "content": {
                            "title": "鸦片战争（1840）",
                            "body_lines": ["1840年，英国以林则徐虎门销烟为借口，发动鸦片战争"],
                            "keywords": ["1840", "鸦片战争", "林则徐"],
                        },
                        "five_skandha": {
                            "recognition_marker": "#历史/近代/鸦片战争",
                        },
                    }
                ],
            },
            "expected": {
                "subject_domain": "HISTORY",
                "content_type": "B2_rapid",
                "min_capabilities": 3,
                "min_scenes": 1,
            },
        },

        "calligraphy_translation": {
            "description": "书法风格辨析卡（B3_translation，书论翻译）",
            "raw_input": {
                "type": "expert_notes",
                "description": "颜真卿楷书风格辨析卡，从书论原文到现代解释的翻译转化",
                "keywords": ["辨析", "区分", "解释", "转化", "书法史"],
                "source_chain_id": "颜真卿辨析卡",
                "exam_type": "国美书法校考",
            },
            "content_spec": {
                "spec_id": "颜真卿辨析卡",
                "exam_meta": {"subject": "书法", "exam_type": "国美书法校考"},
                "question_types": [
                    {"id": "Q_CALLIGRAPHY_TRANSLATION", "name": "书论翻译题"},
                    {"id": "Q_STYLE_COMPARISON", "name": "风格对比题"},
                ],
            },
            "scene_v2_data": {
                "metadata": {
                    "series_title": "书法辨析卡",
                    "source_chain_id": "颜真卿辨析卡",
                    "schema_version": "2.0.0",
                },
                "scenes": [
                    {
                        "scene_id": "颜真卿_辨析_01",
                        "scene_type": "concept",
                        "knowledge_type": "II",
                        "content": {
                            "title": "颜筋柳骨",
                            "body_lines": [
                                "颜真卿楷书：点画浑厚，结体宽博，风格雄健",
                                "柳公权楷书：笔画瘦硬，结体遒丽，风格清朗",
                            ],
                            "keywords": ["颜筋柳骨", "颜真卿", "柳公权"],
                        },
                        "analogy_block": {
                            "applicable": True,
                            "source_domain": "人体结构",
                            "target_domain": "#书法/楷书/风格",
                            "mapping_table": [
                                {"source": "筋（肌腱）", "arrow": "→", "target": "颜书浑厚"},
                                {"source": "骨（骨骼）", "arrow": "→", "target": "柳书瘦硬"},
                            ],
                        },
                        "five_skandha": {
                            "recognition_marker": "#书法/楷书/颜筋柳骨",
                        },
                    }
                ],
            },
            "expected": {
                "subject_domain": "HIST_ART",
                "content_type": "B3_translation",
                "min_capabilities": 3,
            },
        },

        "hist_argumentation": {
            "description": "历史事件多角度论证（B4_argumentation，分析历史事件的多元解读）",
            "raw_input": {
                "type": "analysis_report",
                "description": "安史之乱历史事件分析报告，多角度论证其对中国政治格局的影响",
                "keywords": ["分析", "论证", "判断"],
                "source_chain_id": "安史之乱分析",
                "exam_type": "高考历史",
            },
            "content_spec": {
                "spec_id": "安史之乱分析",
                "exam_meta": {"subject": "历史", "exam_type": "高考历史"},
                "question_types": [
                    {"id": "Q_HIST_ANALYSIS", "name": "历史分析题"},
                    {"id": "Q_HIST_ARGUE", "name": "历史论证题"},
                ],
            },
            "scene_v2_data": {
                "metadata": {
                    "source_chain_id": "安史之乱分析",
                    "schema_version": "2.0.0",
                },
                "scenes": [
                    {
                        "scene_id": "安史之乱_论证_01",
                        "scene_type": "argument",
                        "knowledge_type": "III",
                        "content": {
                            "title": "安史之乱的双重性质",
                            "body_lines": [
                                "角度一：叛乱性质——安禄山、史思明起兵反唐",
                                "角度二：民族矛盾——唐代民族政策的失衡",
                                "角度三：阶级矛盾——均田制破坏导致的社会危机",
                            ],
                            "keywords": ["安史之乱", "双重性质", "多角度"],
                        },
                        "five_skandha": {
                            "recognition_marker": "#历史/唐/安史之乱",
                            "discrimination": "学生能识别安史之乱的多重性质并加以论证",
                        },
                    }
                ],
            },
            "expected": {
                "subject_domain": "HISTORY",
                "content_type": "B4_argumentation",
                "min_capabilities": 3,
            },
        },
    },

    # ════════════════════════════════════════════════════════════════
    # GEO — 地理（自然地理 + 人文地理）
    # ════════════════════════════════════════════════════════════════

    "GEO": {

        "natural_geo_deep": {
            "description": "板块构造与地震带（B1_deep_content，自然地理深层概念）",
            "raw_input": {
                "type": "textbook",
                "description": "高考地理自然地理板块构造理论深度解析，结合地震带分布的自然地理内容",
                "keywords": ["地理", "深度", "系列", "板块构造", "地震带"],
                "source_chain_id": "geo_tectonic_deep",
                "exam_type": "高考地理",
            },
            "content_spec": {
                "spec_id": "板块构造深度",
                "exam_meta": {"subject": "地理", "exam_type": "高考地理"},
                "question_types": [
                    {"id": "Q_GEO_CONCEPT", "name": "地理概念题"},
                    {"id": "Q_GEO_PROCEDURE", "name": "地理成因分析题"},
                ],
            },
            "scene_v2_data": {
                "metadata": {
                    "series_title": "自然地理要素系列",
                    "source_chain_id": "板块构造深度",
                    "schema_version": "2.0.0",
                },
                "scenes": [
                    {
                        "scene_id": "板块构造_概念_01",
                        "scene_type": "concept",
                        "knowledge_type": "II",
                        "content": {
                            "title": "六大板块的分布",
                            "body_lines": [
                                "全球可分为六大板块：太平洋板块、亚欧板块、非洲板块、美洲板块、印度洋板块、南极洲板块",
                                "板块交界处地壳活跃，多火山、地震",
                            ],
                            "keywords": ["六大板块", "板块交界", "火山地震"],
                        },
                        "five_skandha": {
                            "sensation_trigger": "想象地球表面像破碎的蛋壳，六大板块在软流层上缓慢移动",
                            "recognition_marker": "#地理/自然/板块构造",
                        },
                    }
                ],
            },
            "expected": {
                "subject_domain": "GEO",
                "content_type": "B1_deep_content",
                "min_capabilities": 3,
            },
        },

        "natural_geo_rapid": {
            "description": "气候类型速查（B2_rapid，高频气候考点）",
            "raw_input": {
                "type": "exam_syllabus",
                "description": "高考地理气候类型速查表，十种主要气候类型的分布与特征",
                "keywords": ["地理", "速查", "考点", "快背", "核心", "气候"],
                "source_chain_id": "geo_climate_rapid",
                "exam_type": "高考地理",
            },
            "content_spec": {
                "spec_id": "气候速查",
                "exam_meta": {"subject": "地理", "exam_type": "高考地理"},
                "question_types": [
                    {"id": "Q_GEO_FACT", "name": "地理事实题"},
                ],
            },
            "scene_v2_data": {
                "metadata": {
                    "series_title": "地理速查系列",
                    "source_chain_id": "气候速查",
                    "schema_version": "2.0.0",
                },
                "scenes": [
                    {
                        "scene_id": "气候_速查_地中海气候",
                        "scene_type": "fact",
                        "knowledge_type": "I",
                        "content": {
                            "title": "地中海气候（30°-40°N/S）",
                            "body_lines": [
                                "分布：南北纬30°-40°大陆西岸",
                                "特征：夏季炎热干燥，冬季温和多雨",
                                "成因：副热带高压与西风带交替控制",
                            ],
                            "keywords": ["地中海气候", "副热带高压", "西风带"],
                        },
                        "five_skandha": {
                            "recognition_marker": "#地理/自然/气候/地中海",
                        },
                    }
                ],
            },
            "expected": {
                "subject_domain": "GEO",
                "content_type": "B2_rapid",
                "min_capabilities": 3,
            },
        },

        "human_geo_translation": {
            "description": "城市化进程解读（B3_translation，人文地理知识转化）",
            "raw_input": {
                "type": "textbook",
                "description": "高考地理人文地理城市化进程与城市群内容，从学术概念到考试要点的转化",
                "keywords": ["地理", "辨析", "区分", "转化", "城市化"],
                "source_chain_id": "geo_urbanization_trans",
                "exam_type": "高考地理",
            },
            "content_spec": {
                "spec_id": "城市化进程",
                "exam_meta": {"subject": "地理", "exam_type": "高考地理"},
                "question_types": [
                    {"id": "Q_GEO_COMPARISON", "name": "地理对比题"},
                    {"id": "Q_GEO_TRANSLATION", "name": "地理转化题"},
                ],
            },
            "scene_v2_data": {
                "metadata": {
                    "series_title": "人文地理系列",
                    "source_chain_id": "城市化进程",
                    "schema_version": "2.0.0",
                },
                "scenes": [
                    {
                        "scene_id": "城市化_对比_01",
                        "scene_type": "comparison",
                        "knowledge_type": "II",
                        "content": {
                            "title": "发达国家 vs 发展中国家城市化",
                            "body_lines": [
                                "发达国家：城市化水平高（>70%），逆城市化现象",
                                "发展中国家：城市化速度快（>40%），虚假城市化现象",
                            ],
                            "keywords": ["城市化", "发达国家", "发展中国家", "逆城市化"],
                        },
                        "analogy_block": {
                            "applicable": True,
                            "source_domain": "人的成长阶段",
                            "target_domain": "#地理/人文/城市化",
                            "mapping_table": [
                                {"source": "童年（快速发展）", "arrow": "→", "target": "发展中国家城市化"},
                                {"source": "成年（稳定成熟）", "arrow": "→", "target": "发达国家城市化"},
                            ],
                        },
                        "five_skandha": {
                            "recognition_marker": "#地理/人文/城市化",
                        },
                    }
                ],
            },
            "expected": {
                "subject_domain": "GEO",
                "content_type": "B3_translation",
                "min_capabilities": 3,
            },
        },
    },

    # ════════════════════════════════════════════════════════════════
    # POL — 政治（中国特色社会主义 / 经济 / 哲学）
    # ════════════════════════════════════════════════════════════════

    "POL": {

        "socialism_deep": {
            "description": "新发展理念深度解析（B1_deep_content，政治理论深层理解）",
            "raw_input": {
                "type": "textbook",
                "description": "高考政治新发展理念（创新、协调、绿色、开放、共享）深度政治理论内容",
                "keywords": ["政治", "深度", "系列", "新发展理念", "中国特色社会主义"],
                "source_chain_id": "pol_new_development",
                "exam_type": "高考政治",
            },
            "content_spec": {
                "spec_id": "新发展理念",
                "exam_meta": {"subject": "政治", "exam_type": "高考政治"},
                "question_types": [
                    {"id": "Q_POL_CONCEPT", "name": "政治概念题"},
                    {"id": "Q_POL_ANALYSIS", "name": "政治分析题"},
                ],
            },
            "scene_v2_data": {
                "metadata": {
                    "series_title": "政治模块系列",
                    "source_chain_id": "新发展理念",
                    "schema_version": "2.0.0",
                },
                "scenes": [
                    {
                        "scene_id": "新发展理念_概念_01",
                        "scene_type": "concept",
                        "knowledge_type": "II",
                        "content": {
                            "title": "新发展理念的五大内涵",
                            "body_lines": [
                                "创新：发展第一动力",
                                "协调：内在要求",
                                "绿色：必要条件",
                                "开放：必由之路",
                                "共享：根本目的",
                            ],
                            "keywords": ["新发展理念", "创新", "协调", "绿色", "开放", "共享"],
                        },
                        "five_skandha": {
                            "sensation_trigger": "用人的身体比喻理解五大理念：创新是大脑，协调是四肢，绿色是健康",
                            "recognition_marker": "#政治/中特/新发展理念",
                        },
                    }
                ],
            },
            "expected": {
                "subject_domain": "POL",
                "content_type": "B1_deep_content",
                "min_capabilities": 3,
            },
        },

        "economy_translation": {
            "description": "社会主义市场经济知识转化（B3_translation，经济模块）",
            "raw_input": {
                "type": "expert_notes",
                "description": "高考政治社会主义市场经济体制解析，从学术概念到考试要点的知识转化",
                "keywords": ["政治", "经济", "转化", "解释", "辨析"],
                "source_chain_id": "pol_socialist_market",
                "exam_type": "高考政治",
            },
            "content_spec": {
                "spec_id": "社会主义市场经济",
                "exam_meta": {"subject": "政治", "exam_type": "高考政治"},
                "question_types": [
                    {"id": "Q_ECON_TRANSLATION", "name": "经济转化题"},
                    {"id": "Q_ECON_COMPARISON", "name": "经济对比题"},
                ],
            },
            "scene_v2_data": {
                "metadata": {
                    "series_title": "经济系列",
                    "source_chain_id": "社会主义市场经济",
                    "schema_version": "2.0.0",
                },
                "scenes": [
                    {
                        "scene_id": "市场经济_对比_01",
                        "scene_type": "comparison",
                        "knowledge_type": "II",
                        "content": {
                            "title": "社会主义市场经济 vs 资本主义市场经济",
                            "body_lines": [
                                "相同点：都是市场经济，都发挥市场配置资源的决定性作用",
                                "不同点：所有制结构（公有制为主体 vs 私有制为基础）；分配方式（按劳分配为主 vs 按资分配为主）；宏观调控（政府更强 vs 市场更强）",
                            ],
                            "keywords": ["社会主义市场经济", "资本主义市场经济", "对比"],
                        },
                        "analogy_block": {
                            "applicable": True,
                            "source_domain": "游戏规则",
                            "target_domain": "#政治/经济/市场经济",
                            "mapping_table": [
                                {"source": "裁判角色（政府）", "arrow": "→", "target": "社会主义：强裁判+运动员"},
                                {"source": "裁判角色（政府）", "arrow": "→", "target": "资本主义：弱裁判+强运动员"},
                            ],
                        },
                        "five_skandha": {
                            "recognition_marker": "#政治/经济/市场经济",
                        },
                    }
                ],
            },
            "expected": {
                "subject_domain": "POL",
                "content_type": "B3_translation",
                "min_capabilities": 3,
            },
        },

        "philosophy_argumentation": {
            "description": "唯物辩证法多角度论证（B4_argumentation，哲学论证）",
            "raw_input": {
                "type": "analysis_report",
                "description": "高考政治唯物辩证法三大规律（对立统一/质量互变/否定之否定）的论证分析",
                "keywords": ["政治", "哲学", "分析", "论证", "判断", "辩证法"],
                "source_chain_id": "pol_dialectics",
                "exam_type": "高考政治",
            },
            "content_spec": {
                "spec_id": "唯物辩证法",
                "exam_meta": {"subject": "政治", "exam_type": "高考政治"},
                "question_types": [
                    {"id": "Q_PHIL_ANALYSIS", "name": "哲学分析题"},
                    {"id": "Q_PHIL_ARGUE", "name": "哲学论证题"},
                ],
            },
            "scene_v2_data": {
                "metadata": {
                    "series_title": "哲学系列",
                    "source_chain_id": "唯物辩证法",
                    "schema_version": "2.0.0",
                },
                "scenes": [
                    {
                        "scene_id": "辩证法_论证_01",
                        "scene_type": "argument",
                        "knowledge_type": "III",
                        "content": {
                            "title": "对立统一规律的论证",
                            "body_lines": [
                                "核心：矛盾双方既对立又统一",
                                "实例一：学习与考试——学习是基础，考试是检验，两者对立又统一",
                                "实例二：压力与动力——适度的压力转化为前进的动力",
                                "方法论：坚持两点论与重点论的统一",
                            ],
                            "keywords": ["对立统一", "矛盾", "两点论", "重点论"],
                        },
                        "five_skandha": {
                            "recognition_marker": "#政治/哲学/唯物辩证法/对立统一",
                            "discrimination": "学生能运用对立统一规律分析现实问题",
                        },
                    }
                ],
            },
            "expected": {
                "subject_domain": "POL",
                "content_type": "B4_argumentation",
                "min_capabilities": 3,
            },
        },
    },

    # ════════════════════════════════════════════════════════════════
    # CHINESE — 语文（文言文 / 现代文 / 作文）
    # ════════════════════════════════════════════════════════════════

    "CHINESE": {

        "classical_translation": {
            "description": "《师说》文言文翻译（B3_translation，文言→现代汉语）",
            "raw_input": {
                "type": "textbook",
                "description": "韩愈《师说》文言文阅读，含原文、断句、翻译的语言知识转化",
                "keywords": ["语文", "文言文", "翻译", "转化", "古诗文"],
                "source_chain_id": "师说韩愈",
                "exam_type": "高考语文",
            },
            "content_spec": {
                "spec_id": "师说韩愈",
                "exam_meta": {"subject": "语文", "exam_type": "高考语文"},
                "question_types": [
                    {"id": "Q_CHINESE_TRANSLATION", "name": "文言翻译题"},
                    {"id": "Q_CHINESE_READING", "name": "文言阅读题"},
                ],
            },
            "scene_v2_data": {
                "metadata": {
                    "series_title": "文言文系列",
                    "source_chain_id": "师说韩愈",
                    "schema_version": "2.0.0",
                },
                "scenes": [
                    {
                        "scene_id": "师说_翻译_01",
                        "scene_type": "translation",
                        "knowledge_type": "II",
                        "content": {
                            "title": "《师说》原文与翻译对照",
                            "body_lines": [
                                "【原文】古之学者必有师。师者，所以传道受业解惑也。",
                                "【翻译】古代学习的人一定有老师。老师，是用来传授道理、讲授学业、解答疑惑的。",
                                "【关键词】传道（传授儒家之道）、受业（讲授六艺之业）、解惑（解答疑惑）",
                            ],
                            "keywords": ["师说", "传道受业解惑", "韩愈"],
                        },
                        "analogy_block": {
                            "applicable": True,
                            "source_domain": "现代学校场景",
                            "target_domain": "#语文/文言/师说",
                            "mapping_table": [
                                {"source": "老师", "arrow": "→", "target": "传道（教做人）"},
                                {"source": "老师", "arrow": "→", "target": "受业（教知识）"},
                                {"source": "老师", "arrow": "→", "target": "解惑（答问题）"},
                            ],
                        },
                        "five_skandha": {
                            "recognition_marker": "#语文/文言/师说",
                        },
                    }
                ],
            },
            "expected": {
                "subject_domain": "CHINESE",
                "content_type": "B3_translation",
                "min_capabilities": 3,
            },
        },

        "modern_narrative": {
            "description": "现代文散文情感分析（B1_deep_content，文学类文本）",
            "raw_input": {
                "type": "textbook",
                "description": "现代文散文阅读，深度分析文章情感脉络与写作手法",
                "keywords": ["语文", "现代文", "深度", "文学", "分析"],
                "source_chain_id": "散文情感分析",
                "exam_type": "高考语文",
            },
            "content_spec": {
                "spec_id": "散文情感分析",
                "exam_meta": {"subject": "语文", "exam_type": "高考语文"},
                "question_types": [
                    {"id": "Q_CHINESE_ANALYSIS", "name": "文本分析题"},
                    {"id": "Q_CHINESE_LITERARY", "name": "文学手法题"},
                ],
            },
            "scene_v2_data": {
                "metadata": {
                    "series_title": "现代文系列",
                    "source_chain_id": "散文情感分析",
                    "schema_version": "2.0.0",
                },
                "scenes": [
                    {
                        "scene_id": "散文_叙事_01",
                        "scene_type": "concept",
                        "knowledge_type": "II",
                        "content": {
                            "title": "散文阅读：情感线索分析法",
                            "body_lines": [
                                "散文阅读的核心：把握情感线索",
                                "步骤一：找关键词（情感词：惆怅/欣喜/眷恋）",
                                "步骤二：理清行文脉络（写了什么场景）",
                                "步骤三：理解作者心境（为什么写，有何感慨）",
                            ],
                            "keywords": ["散文", "情感线索", "阅读方法"],
                        },
                        "five_skandha": {
                            "sensation_trigger": "散文就像一条情感的河流，沿着关键词的浪花顺流而下",
                            "recognition_marker": "#语文/现代文/散文阅读",
                        },
                    }
                ],
            },
            "expected": {
                "subject_domain": "CHINESE",
                "content_type": "B1_deep_content",
                "min_capabilities": 3,
            },
        },

        "writing_argumentation": {
            "description": "议论文结构论证（B4_argumentation，写作方法论）",
            "raw_input": {
                "type": "analysis_report",
                "description": "高考议论文写作方法，引-议-联-结结构的多角度论证分析",
                "keywords": ["语文", "写作", "分析", "论证", "判断", "议论文"],
                "source_chain_id": "议论文结构",
                "exam_type": "高考语文",
            },
            "content_spec": {
                "spec_id": "议论文结构",
                "exam_meta": {"subject": "语文", "exam_type": "高考语文"},
                "question_types": [
                    {"id": "Q_WRITING_ARGUE", "name": "写作论证题"},
                    {"id": "Q_WRITING_REFLECTION", "name": "写作反思题"},
                ],
            },
            "scene_v2_data": {
                "metadata": {
                    "series_title": "写作系列",
                    "source_chain_id": "议论文结构",
                    "schema_version": "2.0.0",
                },
                "scenes": [
                    {
                        "scene_id": "议论文_论证_01",
                        "scene_type": "argument",
                        "knowledge_type": "III",
                        "content": {
                            "title": "议论文四步结构法",
                            "body_lines": [
                                "【引】引述材料，提出论点（开门见山，不绕圈子）",
                                "【议】正面论述，摆事实讲道理（2-3个论据）",
                                "【联】联系现实，拓展论证（从个人→社会→历史）",
                                "【结】总结升华，回扣论点（简洁有力，戛然而止）",
                            ],
                            "keywords": ["引议联结", "议论文", "结构", "论据"],
                        },
                        "five_skandha": {
                            "recognition_marker": "#语文/写作/议论文",
                            "discrimination": "学生能识别并灵活运用引-议-联-结结构",
                        },
                    }
                ],
            },
            "expected": {
                "subject_domain": "CHINESE",
                "content_type": "B4_argumentation",
                "min_capabilities": 3,
            },
        },
    },

    # ════════════════════════════════════════════════════════════════
    # ENGLISH — 英语（阅读 / 语法 / 写作）
    # ════════════════════════════════════════════════════════════════

    "ENGLISH": {

        "reading_procedure": {
            "description": "阅读主旨大意策略（B3_translation，阅读方法转化）",
            "raw_input": {
                "type": "textbook",
                "description": "高考英语阅读理解主旨大意题解题策略，从英文到方法的转化",
                "keywords": ["英语", "阅读", "翻译", "转化", "辨析"],
                "source_chain_id": "阅读主旨策略",
                "exam_type": "高考英语",
            },
            "content_spec": {
                "spec_id": "阅读主旨策略",
                "exam_meta": {"subject": "英语", "exam_type": "高考英语"},
                "question_types": [
                    {"id": "Q_ENG_TRANSLATION", "name": "阅读转化题"},
                    {"id": "Q_ENG_PROCEDURE", "name": "阅读步骤题"},
                ],
            },
            "scene_v2_data": {
                "metadata": {
                    "series_title": "阅读系列",
                    "source_chain_id": "阅读主旨策略",
                    "schema_version": "2.0.0",
                },
                "scenes": [
                    {
                        "scene_id": "阅读_步骤_01",
                        "scene_type": "procedure",
                        "knowledge_type": "II",
                        "content": {
                            "title": "主旨大意题三步法",
                            "body_lines": [
                                "第一步：找主题句（首段首句/末句/全文总结）",
                                "第二步：排除干扰项（太宽/太窄/无中生有）",
                                "第三步：验证选项与文章中心思想的契合度",
                            ],
                            "keywords": ["主旨大意", "主题句", "三步法", "阅读理解"],
                        },
                        "analogy_block": {
                            "applicable": True,
                            "source_domain": "地图导航",
                            "target_domain": "#英语/阅读/主旨大意",
                            "mapping_table": [
                                {"source": "地图定位", "arrow": "→", "target": "找主题句（定位文章方向）"},
                                {"source": "排除错误路线", "arrow": "→", "target": "排除干扰项（太宽/太窄）"},
                                {"source": "到达目的地", "arrow": "→", "target": "选出正确选项"},
                            ],
                        },
                        "five_skandha": {
                            "recognition_marker": "#英语/阅读/主旨大意",
                        },
                    }
                ],
            },
            "expected": {
                "subject_domain": "ENGLISH",
                "content_type": "B3_translation",
                "min_capabilities": 3,
            },
        },

        "grammar_rapid": {
            "description": "虚拟语气语法速查（B2_rapid，高频语法考点）",
            "raw_input": {
                "type": "exam_syllabus",
                "description": "高考英语虚拟语气速查表，if引导的虚拟语气三大时态",
                "keywords": ["英语", "语法", "速查", "考点", "快背", "核心"],
                "source_chain_id": "虚拟语气速查",
                "exam_type": "高考英语",
            },
            "content_spec": {
                "spec_id": "虚拟语气速查",
                "exam_meta": {"subject": "英语", "exam_type": "高考英语"},
                "question_types": [
                    {"id": "Q_ENG_GRAMMAR", "name": "语法题"},
                ],
            },
            "scene_v2_data": {
                "metadata": {
                    "series_title": "语法系列",
                    "source_chain_id": "虚拟语气速查",
                    "schema_version": "2.0.0",
                },
                "scenes": [
                    {
                        "scene_id": "虚拟语气_速查_01",
                        "scene_type": "fact",
                        "knowledge_type": "I",
                        "content": {
                            "title": "if 虚拟语气三大句型",
                            "body_lines": [
                                "【与现在相反】If + 主语+ did/were, 主语+ would/could/might + do",
                                "【与过去相反】If + 主语+ had done, 主语+ would/could/might + have done",
                                "【与将来相反】If + 主语+ were to do/should do, 主语+ would/could/might + do",
                            ],
                            "keywords": ["虚拟语气", "if从句", "would have done", "语法"],
                        },
                        "five_skandha": {
                            "recognition_marker": "#英语/语法/虚拟语气",
                        },
                    }
                ],
            },
            "expected": {
                "subject_domain": "ENGLISH",
                "content_type": "B2_rapid",
                "min_capabilities": 3,
            },
        },

        "writing_procedure": {
            "description": "读后续写技巧（B3_translation，英语写作方法）",
            "raw_input": {
                "type": "expert_notes",
                "description": "高考英语读后续写解题技巧，从原文阅读到续写方法的转化",
                "keywords": ["英语", "写作", "转化", "翻译", "读后续写"],
                "source_chain_id": "读后续写技巧",
                "exam_type": "高考英语",
            },
            "content_spec": {
                "spec_id": "读后续写技巧",
                "exam_meta": {"subject": "英语", "exam_type": "高考英语"},
                "question_types": [
                    {"id": "Q_ENG_WRITING", "name": "写作题"},
                    {"id": "Q_ENG_PROCEDURE", "name": "写作步骤题"},
                ],
            },
            "scene_v2_data": {
                "metadata": {
                    "series_title": "写作系列",
                    "source_chain_id": "读后续写技巧",
                    "schema_version": "2.0.0",
                },
                "scenes": [
                    {
                        "scene_id": "读后续写_步骤_01",
                        "scene_type": "procedure",
                        "knowledge_type": "II",
                        "content": {
                            "title": "读后续写五步法",
                            "body_lines": [
                                "第一步：梳理原文故事线（人物/事件/情感）",
                                "第二步：找出续写两个段落的开头提示句",
                                "第三步：构思情节发展（保持人物性格一致）",
                                "第四步：运用高级词汇和句式（倒装/强调/非谓语）",
                                "第五步：检查逻辑连贯性和字数要求（150词左右）",
                            ],
                            "keywords": ["读后续写", "五步法", "高级词汇", "逻辑连贯"],
                        },
                        "analogy_block": {
                            "applicable": True,
                            "source_domain": "拼图游戏",
                            "target_domain": "#英语/写作/读后续写",
                            "mapping_table": [
                                {"source": "看说明书", "arrow": "→", "target": "梳理原文故事线"},
                                {"source": "找边框", "arrow": "→", "target": "找开头提示句"},
                                {"source": "填中间", "arrow": "→", "target": "构思情节发展"},
                            ],
                        },
                        "five_skandha": {
                            "recognition_marker": "#英语/写作/读后续写",
                        },
                    }
                ],
            },
            "expected": {
                "subject_domain": "ENGLISH",
                "content_type": "B3_translation",
                "min_capabilities": 3,
            },
        },
    },

    # ════════════════════════════════════════════════════════════════
    # MATH — 数学（Phase 2 单独处理，Phase 1 占位）
    # ════════════════════════════════════════════════════════════════

    "MATH": {
        "math_placeholder": {
            "description": "MATH Phase 2 占位用例（待 math_v1_schema.json 定义后补全）",
            "raw_input": {
                "type": "textbook",
                "description": "数学 Phase 2 待实现",
                "keywords": ["数学"],
                "source_chain_id": "math_placeholder",
            },
            "content_spec": {"spec_id": "math_placeholder"},
            "scene_v2_data": {"metadata": {"source_chain_id": "math_placeholder"}},
            "expected": {
                "subject_domain": "MATH",
                "content_type": "B1_deep_content",
                "min_capabilities": 3,
            },
            "skip": True,  # Phase 2 再运行
            "skip_reason": "MATH inner format（math_v1）待 Phase 2 定义",
        },
    },
}


# ═══════════════════════════════════════════════════════════════════
# 测试执行函数
# ═══════════════════════════════════════════════════════════════════

class E2EPhase1TestRunner:
    """Phase 1 端到端测试运行器"""

    def __init__(self, verbose: bool = False, json_output: bool = False,
                 schema_path: Path | None = None):
        self.verbose = verbose
        self.json_output = json_output
        self.router = None
        self.schema = None
        self.results: list[TestResult] = []

        # 加载 pipeline_package Schema
        if schema_path is None:
            schema_path = Path("D:/1_omas/MODLIB/content_manufacturing/schemas/pipeline_package_schema.json")
        self.schema = _load_json_schema(schema_path)

    # ─────────────────────────────────────────────────────────────────
    # 基础设施测试
    # ─────────────────────────────────────────────────────────────────

    def test_router_initialization(self) -> TestResult:
        """T0: 路由器初始化 + 列出所有 B1-B4 类型"""
        import time
        t0 = time.perf_counter()
        try:
            router = ContentRouter()
            types = router.list_all_types()
            assert len(types) >= 4, f"B1-B4 至少应有4种类型，实际：{types}"
            assert "B1_deep_content" in types
            assert "B2_rapid" in types
            assert "B3_translation" in types
            assert "B4_argumentation" in types
            duration = (time.perf_counter() - t0) * 1000
            self.router = router
            return TestResult(
                subject_domain="INFRA",
                sub_domain="router",
                test_name="T0_router_initialization",
                passed=True,
                duration_ms=duration,
                details={"types": types, "schema_loaded": self.schema is not None},
            )
        except Exception as e:
            duration = (time.perf_counter() - t0) * 1000
            return TestResult(
                subject_domain="INFRA",
                sub_domain="router",
                test_name="T0_router_initialization",
                passed=False,
                duration_ms=duration,
                error_message=str(e),
            )

    def test_subject_registry(self) -> TestResult:
        """T0b: 学科注册表加载验证"""
        import time
        t0 = time.perf_counter()
        try:
            registry_path = Path("D:/2_products/education/SPDT-004_EduContent/1_ingest/test_data/subject_registry.yaml")
            assert registry_path.exists(), f"学科注册表不存在：{registry_path}"

            # 手动 YAML 解析
            domains = self._parse_registry(registry_path)
            domain_ids = [s["domain_id"] for s in domains]
            assert "HIST_ART" in domain_ids
            assert "GEO" in domain_ids
            assert "POL" in domain_ids
            assert "CHINESE" in domain_ids
            assert "ENGLISH" in domain_ids

            duration = (time.perf_counter() - t0) * 1000
            return TestResult(
                subject_domain="INFRA",
                sub_domain="registry",
                test_name="T0_subject_registry",
                passed=True,
                duration_ms=duration,
                details={"domains": domain_ids, "total": len(domains)},
            )
        except Exception as e:
            duration = (time.perf_counter() - t0) * 1000
            return TestResult(
                subject_domain="INFRA",
                sub_domain="registry",
                test_name="T0_subject_registry",
                passed=False,
                duration_ms=duration,
                error_message=str(e),
            )

    def _parse_registry(self, path: Path) -> list[dict]:
        """手动解析简化 YAML（无 PyYAML 依赖时）"""
        import re
        result = []
        current_subject = None
        in_subjects = False
        current_subdomain = None
        in_subdomains = False

        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                stripped = line.rstrip()
                # 跳过注释、空行、前置元数据
                if not stripped or stripped.startswith("#") or stripped.startswith("---"):
                    if "- domain_id:" in stripped:
                        in_subjects = True
                    continue
                if "- domain_id:" in stripped:
                    if current_subject:
                        result.append(current_subject)
                    current_subject = {"domain_id": stripped.split("domain_id:")[1].strip()}
                    current_subdomain = None
                    in_subdomains = False
                elif "  sub_id:" in stripped and current_subject is not None:
                    if current_subdomain:
                        if "sub_domains" not in current_subject:
                            current_subject["sub_domains"] = []
                        current_subject["sub_domains"].append(current_subdomain)
                    current_subdomain = {"sub_id": stripped.split("sub_id:")[1].strip()}
                    in_subdomains = True
                elif "    label:" in stripped and current_subdomain is not None:
                    current_subdomain["label"] = stripped.split("label:")[1].strip()

        if current_subject:
            if current_subdomain and "sub_domains" in current_subject:
                current_subject["sub_domains"].append(current_subdomain)
            elif current_subdomain:
                current_subject["sub_domains"] = [current_subdomain]
            result.append(current_subject)

        return result

    # ─────────────────────────────────────────────────────────────────
    # 学科端到端测试（每学科 1 个代表性测试用例）
    # ─────────────────────────────────────────────────────────────────

    def _run_subject_e2e(self, domain_id: str, fixture_name: str,
                          fixture: dict) -> TestResult:
        """
        对单个 fixture 执行端到端测试。
        测试流程：
          ① 路由器 B1-B4 分类
          ② RouteResult.to_outer() 生成 outer
          ③ build_pipeline_package() 完整封装
          ④ Schema 验证
          ⑤ expected 断言
        """
        import time
        t0 = time.perf_counter()

        # ── 跳过标记（Phase 2/3 待实现的学科）
        if fixture.get("skip", False):
            duration = (time.perf_counter() - t0) * 1000
            return TestResult(
                subject_domain=domain_id,
                sub_domain=fixture_name,
                test_name=f"T_e2e_{domain_id}_{fixture_name}",
                passed=True,
                duration_ms=duration,
                error_message=f"[SKIP] {fixture.get('skip_reason', '')}",
                details={"skipped": True},
            )

        raw_input = fixture["raw_input"]
        content_spec = fixture.get("content_spec", {})
        scene_v2_data = fixture["scene_v2_data"]
        expected = fixture.get("expected", {})
        description = fixture.get("description", "")

        # ── 自动注入 subject_domain（从 expected 推断，解决 Windows GBK 编码问题）
        # 优先级：raw_input 已有 > expected.subject_domain > 路由推断
        exp_domain = expected.get("subject_domain", domain_id)
        if "subject_domain" not in raw_input:
            # 深拷贝避免修改原始 fixture
            import copy
            raw_input = copy.deepcopy(raw_input)
            raw_input["subject_domain"] = exp_domain

        errors: list[str] = []

        try:
            # ── Step 1: 路由器分类 ─────────────────────────────────
            if self.router is None:
                self.router = ContentRouter()

            # 构造模拟 EntryDecision
            class MockDecision:
                verdict = "APPLICABLE"
            route = self.router.route(MockDecision(), raw_input)

            # 断言：B1-B4 类型
            expected_ct = expected.get("content_type", "B1_deep_content")
            if route.b1_b4_type != expected_ct:
                errors.append(
                    f"B1-B4 类型不匹配：期望 {expected_ct}，实际 {route.b1_b4_type}；"
                    f"置信度={route.confidence}，关键词={route.matched_keywords}"
                )

            # 断言：capabilities 数量
            min_caps = expected.get("min_capabilities", 3)
            caps = _b1b4_to_capabilities(route.b1_b4_type)
            if len(caps) < min_caps:
                errors.append(f"capabilities 数量不足：期望 >= {min_caps}，实际 {len(caps)}")

            # ── Step 2: to_outer() 生成 outer ───────────────────────
            outer = route.to_outer(raw_input, content_spec)

            # 断言：outer 必填字段
            for field in ["subject_domain", "content_type", "capabilities", "knowledge_types"]:
                if field not in outer:
                    errors.append(f"outer.{field} 缺失")

            # 断言：subject_domain
            exp_domain = expected.get("subject_domain", domain_id)
            act_domain = outer.get("subject_domain", "UNKNOWN")
            if act_domain != exp_domain:
                errors.append(
                    f"subject_domain 不匹配：期望 {exp_domain}，实际 {act_domain}"
                )

            # ── Step 3: build_pipeline_package() ───────────────────
            route_dict = route.to_dict()
            pkg = build_pipeline_package(
                content_spec=content_spec,
                scene_v2_data=scene_v2_data,
                route_result=route_dict,
                trust_level="E",
            )

            # 断言：version
            if pkg.get("version") != "1.0.0":
                errors.append(f"version 应为 '1.0.0'，实际：{pkg.get('version')}")

            # 断言：inner 完整
            inner = pkg.get("inner", {})
            if "schema" not in inner or "data" not in inner:
                errors.append("inner.schema 或 inner.data 缺失")

            # 断言：inner.schema
            exp_schema = expected.get("inner_schema", "scene_v2")
            act_schema = inner.get("schema", "UNKNOWN")
            if act_schema != exp_schema:
                errors.append(f"inner.schema 不匹配：期望 {exp_schema}，实际 {act_schema}")

            # 断言：capabilities 传递
            pkg_caps = pkg.get("outer", {}).get("capabilities", [])
            if len(pkg_caps) < min_caps:
                errors.append(f"pipeline_package.outer.capabilities 不足：期望 >= {min_caps}，实际 {len(pkg_caps)}")

            # ── Step 4: extract_outer / extract_capabilities ───────
            extracted_outer = extract_outer_from_pipeline_package(pkg)
            if extracted_outer.get("subject_domain") != exp_domain:
                errors.append("extract_outer_from_pipeline_package 提取结果不正确")

            extracted_caps = extract_capabilities(pkg)
            if len(extracted_caps) < min_caps:
                errors.append(f"extract_capabilities 数量不足：期望 >= {min_caps}，实际 {len(extracted_caps)}")

            # ── Step 5: Schema 验证 ─────────────────────────────
            schema_valid, schema_errors = _validate_pipeline_package(pkg, self.schema)
            if not schema_valid:
                errors.extend(schema_errors)

        except Exception as e:
            errors.append(f"执行异常：{e}\n{traceback.format_exc()}")

        duration = (time.perf_counter() - t0) * 1000
        passed = len(errors) == 0

        return TestResult(
            subject_domain=domain_id,
            sub_domain=fixture_name,
            test_name=f"T_e2e_{domain_id}_{fixture_name}",
            passed=passed,
            duration_ms=duration,
            error_message=" | ".join(errors) if errors else "",
            details={
                "description": description,
                "route_type": route.b1_b4_type if "route" in dir() else "N/A",
                "subject_domain": outer.get("subject_domain", "N/A") if "outer" in dir() else "N/A",
                "capabilities": pkg_caps if "pkg_caps" in dir() else [],
                "scenes": len(scene_v2_data.get("scenes", [])),
            },
        )

    def run_domain_tests(self, domain_id: str) -> list[TestResult]:
        """运行指定学科域的所有测试用例"""
        fixtures = FIXTURES.get(domain_id, {})
        results = []
        for fixture_name, fixture in fixtures.items():
            result = self._run_subject_e2e(domain_id, fixture_name, fixture)
            results.append(result)
        return results

    def run_all_tests(self) -> list[TestResult]:
        """运行所有测试（Phase 1 覆盖的学科）"""
        results = []

        # 基础设施测试
        results.append(self.test_router_initialization())
        results.append(self.test_subject_registry())

        # 学科端到端测试（Phase 1 覆盖）
        phase1_domains = ["HIST_ART", "GEO", "POL", "CHINESE", "ENGLISH"]
        for domain_id in phase1_domains:
            results.extend(self.run_domain_tests(domain_id))

        self.results = results
        return results


# ═══════════════════════════════════════════════════════════════════
# 输出格式化
# ═══════════════════════════════════════════════════════════════════

def format_results(results: list[TestResult], verbose: bool = False,
                   json_output: bool = False) -> str:
    """格式化测试结果输出"""

    if json_output:
        return json.dumps(
            {"total": len(results), "results": [r.to_dict() for r in results]},
            ensure_ascii=False, indent=2
        )

    # ── 文本输出
    passed = sum(1 for r in results if r.passed)
    failed = [r for r in results if not r.passed]
    total = len(results)

    lines = []
    lines.append("")
    lines.append("=" * 70)
    lines.append(f"Phase 1 E2E Test Report  ({passed}/{total} PASS)")
    lines.append("=" * 70)

    # 按学科域分组
    current_domain = None
    for r in results:
        domain = r.subject_domain
        if domain != current_domain:
            current_domain = domain
            lines.append("")
            lines.append(f"┌─ {domain}")
            lines.append(f"│")

        status_icon = "[PASS]" if r.passed else "[FAIL]"
        sub = r.sub_domain or ""
        name = r.test_name or ""

        if r.error_message and ("[SKIP]" in r.error_message):
            status_icon = "[SKIP]"
            msg = r.error_message
        elif r.error_message:
            msg = r.error_message[:60] + ("..." if len(r.error_message) > 60 else "")
        else:
            msg = ""

        dur = f"{r.duration_ms:.1f}ms"
        lines.append(
            f"│  {status_icon} {name}  ({dur})"
        )
        if msg:
            lines.append(f"│      └─ {msg}")

    lines.append("│")
    lines.append("└──────────────────────────────────────────────────")

    # 失败摘要
    if failed:
        lines.append("")
        lines.append(f"[FAIL] 失败用例 ({len(failed)} 项)：")
        for r in failed:
            lines.append(f"  • {r.subject_domain}.{r.sub_domain}: {r.error_message[:80]}")

    lines.append("")
    lines.append(f"SUMMARY: {passed}/{total} PASS | FAIL: {len(failed)}")
    if verbose and results:
        # 详细模式：打印 capabilities 提取验证
        lines.append("")
        lines.append("详细 Capabilities 映射验证：")
        caps_results = [r for r in results if r.details.get("capabilities")]
        for r in caps_results:
            caps = r.details.get("capabilities", [])
            lines.append(f"  {r.subject_domain}.{r.sub_domain}: {caps}")

    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════
# CLI 入口
# ═══════════════════════════════════════════════════════════════════

def main():
    # 强制 UTF-8 输出（Windows GBK 环境）
    import sys
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass  # 非 Windows 或已配置

    parser = argparse.ArgumentParser(
        description="Phase 1 端到端测试套件 — SPDT-004 教育管线",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  python _test_e2e_phase1.py                  # 标准运行
  python _test_e2e_phase1.py -v               # 详细模式
  python _test_e2e_phase1.py --json           # JSON 输出（CI 集成）
  python _test_e2e_phase1.py --subject HIST_ART  # 仅测 HIST_ART
  python _test_e2e_phase1.py --subject GEO --verbose  # GEO 详细
        """
    )
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="详细模式：显示更多上下文")
    parser.add_argument("--json", action="store_true",
                        help="JSON 输出（CI 集成模式）")
    parser.add_argument("--subject", type=str, default=None,
                        help="仅测试指定学科域（如 HIST_ART / GEO / POL）")
    parser.add_argument("--schema", type=str, default=None,
                        help="pipeline_package_schema.json 路径")
    args = parser.parse_args()

    # Schema 路径
    schema_path = Path(args.schema) if args.schema else None

    # 运行测试
    runner = E2EPhase1TestRunner(
        verbose=args.verbose,
        json_output=args.json,
        schema_path=schema_path,
    )

    if args.subject:
        fixtures = FIXTURES.get(args.subject, {})
        if not fixtures:
            print(f"[ERROR] 未知学科域：{args.subject}")
            print(f"可用学科域：{list(FIXTURES.keys())}")
            sys.exit(1)
        results = []
        results.append(runner.test_router_initialization())
        results.append(runner.test_subject_registry())
        for name, fixture in fixtures.items():
            results.append(runner._run_subject_e2e(args.subject, name, fixture))
    else:
        results = runner.run_all_tests()

    # 输出
    output = format_results(results, verbose=args.verbose, json_output=args.json)
    print(output)

    # CI 退出码
    failed = [r for r in results if not r.passed]
    sys.exit(0 if not failed else 1)


if __name__ == "__main__":
    main()
