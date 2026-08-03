# -*- coding: utf-8 -*-
"""生成政治科目 KB 骨架文件"""
import json, os

BASE = r'D:\2_products\education\SPDT-004_EduContent\4_adapt\AdaptivePrepPlatform\_03_subject_packs\political_gaokao_2026'

def write_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def write_yaml(path, text):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)

# 1. meta.json
meta = {
    "pack_id": "political_gaokao_2026",
    "pack_name": "高考思想政治系列知识包",
    "version": "1.0.0",
    "subject": "高考思想政治",
    "exam_type": "高考（上海卷/全国卷）",
    "target": "高三备考学生 · 经济/政治/哲学/法律四模块",
    "platform_version_required": ">=1.0.0",
    "author": "Mavis AI Team",
    "created": "2026-08-02",
    "dependencies": [],
    "statistics": {
        "knowledge_entries": 0,
        "ability_points": 16,
        "chain_count": 16,
        "module_count": 4
    },
    "config": {
        "total_duration_minutes": 120,
        "question_types": [
            {"id": "Q_CHOICE", "name": "选择题", "weight": 0.40, "description": "四选一/四选多，考查基础知识与概念"},
            {"id": "Q_SHORT", "name": "简答题", "weight": 0.30, "description": "基本概念/原理简述"},
            {"id": "Q_ESSAY", "name": "论述题", "weight": 0.30, "description": "理论联系实际，综合论述"}
        ],
        "scoring_weights": {
            "选择题": 0.40,
            "简答题": 0.30,
            "论述题": 0.30
        },
        "cognitive_levels": {
            "Lv1": "识记 / 基本概念和事实",
            "Lv2": "理解 / 基本原理和方法",
            "Lv3": "分析 / 社会现象分析",
            "Lv4": "综合 / 多模块综合论述",
            "Lv5": "评价 / 价值判断与行为选择"
        }
    },
    "activation": {
        "default_active": False,
        "requires_exam_code": "POLI_MANDARIN"
    },
    "modules": [
        {
            "module_id": "M1",
            "name": "经济生活",
            "weight": 0.30,
            "sub_modules": ["商品与货币", "生产与消费", "分配与社会保障", "社会主义市场经济", "经济全球化"],
            "chains": [
                {"chain_id": "POLI_经济_商品货币", "chain_name": "商品与货币", "causal_logic": "商品基本属性 → 货币职能 → 纸币与信用 → 外汇与汇率", "knowledge_points": 0, "chain_tags": ["商品", "货币", "价值尺度", "流通手段", "纸币", "汇率"]},
                {"chain_id": "POLI_经济_生产消费", "chain_name": "生产与消费", "causal_logic": "生产决定消费 → 消费类型 → 消费心理 → 树立正确消费观", "knowledge_points": 0, "chain_tags": ["生产与消费关系", "消费类型", "消费心理", "恩格尔系数"]},
                {"chain_id": "POLI_经济_分配保障", "chain_name": "分配与社保", "causal_logic": "按劳分配 → 多种分配方式 → 税收 → 社会保障", "knowledge_points": 0, "chain_tags": ["按劳分配", "按生产要素分配", "个人所得税", "社会保障制度"]},
                {"chain_id": "POLI_经济_市场经济", "chain_name": "市场经济", "causal_logic": "市场经济特征 → 资源配置 → 国家宏观调控 → 社会主义市场经济", "knowledge_points": 0, "chain_tags": ["市场经济", "宏观调控", "市场失灵", "社会主义市场经济体制"]}
            ]
        },
        {
            "module_id": "M2",
            "name": "政治生活",
            "weight": 0.30,
            "sub_modules": ["国家与公民", "政党制度", "人民代表大会制度", "国际社会"],
            "chains": [
                {"chain_id": "POLI_政治_国家公民", "chain_name": "国家与公民", "causal_logic": "国家性质 → 人民民主专政 → 公民权利义务 → 政治参与", "knowledge_points": 0, "chain_tags": ["国家性质", "人民民主专政", "公民权利", "政治参与"]},
                {"chain_id": "POLI_政治_政党制度", "chain_name": "政党制度", "causal_logic": "政党性质 → 多党合作制度 → 政治协商 → 民主党派作用", "knowledge_points": 0, "chain_tags": ["中国共产党", "多党合作", "政治协商", "民主党派"]},
                {"chain_id": "POLI_政治_人大制度", "chain_name": "人大制度", "causal_logic": "国体与政体 → 人民代表大会 → 民主集中制 → 法治建设", "knowledge_points": 0, "chain_tags": ["人民代表大会", "国体政体", "民主集中制", "依法治国"]},
                {"chain_id": "POLI_政治_国际社会", "chain_name": "国际社会", "causal_logic": "主权国家 → 国际组织 → 时代主题 → 中国的外交政策", "knowledge_points": 0, "chain_tags": ["主权", "国际组织", "和平与发展", "独立自主和平外交"]}
            ]
        },
        {
            "module_id": "M3",
            "name": "哲学常识",
            "weight": 0.25,
            "sub_modules": ["唯物论", "辩证法", "认识论", "历史唯物主义"],
            "chains": [
                {"chain_id": "POLI_哲学_唯物论", "chain_name": "唯物论基础", "causal_logic": "物质概念 → 意识的能动作用 → 一切从实际出发", "knowledge_points": 0, "chain_tags": ["物质", "意识", "主观能动性", "一切从实际出发"]},
                {"chain_id": "POLI_哲学_唯物辩证", "chain_name": "唯物辩证法", "causal_logic": "联系 → 发展 → 矛盾 → 辩证否定", "knowledge_points": 0, "chain_tags": ["联系", "发展", "矛盾", "辩证否定", "量变质变"]},
                {"chain_id": "POLI_哲学_认识实践", "chain_name": "认识与实践", "causal_logic": "实践本质 → 认识发展 → 真理特性 → 认识反作用于实践", "knowledge_points": 0, "chain_tags": ["实践", "认识", "真理", "认识的反复性与无限性"]},
                {"chain_id": "POLI_哲学_历史唯物", "chain_name": "历史唯物主义", "causal_logic": "社会存在 → 生产方式 → 人民群众 → 价值观", "knowledge_points": 0, "chain_tags": ["社会存在", "社会意识", "人民群众", "价值观", "人生价值"]}
            ]
        },
        {
            "module_id": "M4",
            "name": "法律道德",
            "weight": 0.15,
            "sub_modules": ["公民权利义务", "法律基础", "道德与法治"],
            "chains": [
                {"chain_id": "POLI_法律_公民权利", "chain_name": "公民权利义务", "causal_logic": "公民基本权利 → 公民基本义务 → 权利义务关系 → 依法行使权利", "knowledge_points": 0, "chain_tags": ["人身权", "财产权", "政治权利", "公民义务", "法律面前一律平等"]},
                {"chain_id": "POLI_法律_法律基础", "chain_name": "法律基础", "causal_logic": "法律的本质 → 法律体系 → 公民与法律 → 依法办事", "knowledge_points": 0, "chain_tags": ["宪法", "民法", "公民与法律", "依法办事", "程序公正"]}
            ]
        }
    ],
    "cross_pack_links": {
        "history_gaokao": {
            "relation": "历史唯物主义与历史学科联动（社会形态演进）",
            "trigger_chain_ids": ["POLI_哲学_历史唯物"]
        },
        "geography_gaokao": {
            "relation": "经济地理与环境政治联动（可持续发展/生态文明）",
            "trigger_chain_ids": ["POLI_经济_市场经济", "POLI_政治_国际社会"]
        }
    },
    "agent_prompt_patch_files": {"agent1": None, "agent2": None, "agent3": None},
    "status": "v1.0_P0_draft",
    "last_updated": "2026-08-02"
}
write_json(os.path.join(BASE, 'meta.json'), meta)
print('[OK] meta.json')

# 2. content_spec.yaml
content_spec = """spec_id: political_gaokao_2026
spec_version: 1.0.0
spec_generated: '2026-08-02T00:00:00+08:00'
domain: education
content_type: B1_deep_content

exam_meta:
  exam_name: 高考思想政治
  exam_code: POLI_SHANGHAI_2026
  subject: 高考思想政治（上海卷）
  total_duration_min: 120
  total_score: 100
  measurement_targets:
    - id: MT1
      name: 识记
      weight: 0.10
      description: 再现国内外重大时事的基本内容
    - id: MT2
      name: 理解
      weight: 0.35
      description: 概括基本概念、原理和方法，辨别区别，阐述联系
    - id: MT3
      name: 分析
      weight: 0.35
      description: 运用知识分析说明社会现象，归纳实质，置疑判断
    - id: MT4
      name: 综合
      weight: 0.10
      description: 综合运用知识进行全面论述，理论联系实际提出方案
    - id: MT5
      name: 评价
      weight: 0.10
      description: 作出正确价值判断和评价，选择正确行为态度

question_types:
  - id: Q_CHOICE
    name: 选择题
    weight: 0.40
    description: 四选一/四选多，考查基础知识与概念
    key_topics:
      - 商品的基本属性
      - 货币的职能
      - 我国的国家性质
      - 人民代表大会制度
      - 矛盾的普遍性与特殊性
      - 实践与认识的关系
  - id: Q_SHORT
    name: 简答题
    weight: 0.30
    description: 基本概念/原理简述
    key_topics:
      - 生产与消费的辩证关系
      - 按劳分配为主体的客观必然性
      - 我国政府的主要职能
      - 矛盾的同一性与斗争性
  - id: Q_ESSAY
    name: 论述题
    weight: 0.30
    description: 理论联系实际，综合论述
    key_topics:
      - 运用唯物辩证法分析社会热点问题
      - 结合社会主义市场经济分析宏观调控
      - 用历史唯物主义观点评价社会现象

modules:
  - module_id: M1
    name: 经济生活
    weight: 0.30
    topics:
      - id: E1
        name: 商品与货币
        level: A
        sub_topics: [商品的基本属性, 货币的本质与职能, 纸币与信用, 外汇与汇率]
      - id: E2
        name: 生产与消费
        level: B
        sub_topics: [生产与消费的辩证关系, 消费类型与消费心理, 树立正确消费观]
      - id: E3
        name: 分配与社会保障
        level: B
        sub_topics: [按劳分配为主体, 多种分配方式并存, 税收的作用, 社会保障制度]
      - id: E4
        name: 社会主义市场经济
        level: C
        sub_topics: [市场经济的基本特征, 国家宏观调控, 社会主义市场经济体制]
      - id: E5
        name: 经济全球化
        level: B
        sub_topics: [经济全球化的表现, 机遇与挑战, 我国的对外开放]
  - module_id: M2
    name: 政治生活
    weight: 0.30
    topics:
      - id: P1
        name: 国家与公民
        level: B
        sub_topics: [我国的国家性质, 人民民主专政, 公民的政治权利和义务, 政治参与]
      - id: P2
        name: 政党制度
        level: C
        sub_topics: [中国共产党的性质, 多党合作制度, 政治协商制度]
      - id: P3
        name: 人民代表大会制度
        level: C
        sub_topics: [国体与政体, 人民代表大会, 民主集中制, 依法治国]
      - id: P4
        name: 国际社会
        level: B
        sub_topics: [主权国家, 国际组织, 和平与发展, 独立自主和平外交政策]
  - module_id: M3
    name: 哲学常识
    weight: 0.25
    topics:
      - id: X1
        name: 唯物论
        level: B
        sub_topics: [哲学的基本问题, 物质的唯一特性, 意识的能动作用, 一切从实际出发]
      - id: X2
        name: 辩证法
        level: C
        sub_topics: [联系的普遍性与客观性, 发展的实质, 矛盾的普遍性与特殊性, 量变与质变, 辩证否定]
      - id: X3
        name: 认识论
        level: C
        sub_topics: [实践的含义与特点, 认识的本质, 真理的客观性, 认识的反复性与无限性]
      - id: X4
        name: 历史唯物主义
        level: C
        sub_topics: [社会存在与社会意识, 生产方式, 人民群众是历史的创造者, 价值观的导向作用]
  - module_id: M4
    name: 法律道德
    weight: 0.15
    topics:
      - id: L1
        name: 公民权利义务
        level: A
        sub_topics: [公民的基本权利, 公民的基本义务, 权利与义务的关系]
      - id: L2
        name: 法律基础
        level: B
        sub_topics: [法律的本质, 宪法是国家的根本法, 公民与法律, 依法办事]

reference_texts:
  - 上海高考思想政治课程标准（2004版）
  - 高中思想政治必修1-4（上海新版教材）
  - 高中思想政治选择性必修1-3

quality_constraints:
  factual_accuracy: expert_reviewed
  cross_check_required: true
  hallucination_threshold: 0.05
  political_accuracy: strict
  description: 政治科目涉及国家政治制度与意识形态，需严格事实核查，所有政治制度表述须与官方表述一致

production_target:
  knowledge_entries_target: 200
  ability_count_target: 16
  coverage_target: 0.85

human_checkpoint:
  - M1_syllabus_confirmed
  - M2_factual_accuracy_verified_by_expert

source: generated_from_shanghai_gaokao_syllabus_2026
"""
write_yaml(os.path.join(BASE, 'content_spec.yaml'), content_spec)
print('[OK] content_spec.yaml')

# 3. knowledge/kb_meta.json
write_json(os.path.join(BASE, 'knowledge', 'kb_meta.json'), {
    "subject": "高考思想政治",
    "target_exam": "高考（上海卷/全国卷）",
    "difficulty_range": ["初阶", "中阶", "高阶"],
    "total_entries_planned": 200,
    "module_count": 4,
    "chain_count": 16,
    "source": "上海高考思想政治考纲（2004课程标准）+ 高中思想政治教材",
    "created": "2026-08-02",
    "last_updated": "2026-08-02"
})
print('[OK] knowledge/kb_meta.json')

# 4. knowledge/kb_tags.json
write_json(os.path.join(BASE, 'knowledge', 'kb_tags.json'), {
    "version": "1.0.0",
    "last_updated": "2026-08-02",
    "tags": [
        {"tag": "#难度_初阶", "description": "识记级考点，基础概念与事实", "module": "通用"},
        {"tag": "#难度_中阶", "description": "理解级考点，概念辨析与简单应用", "module": "通用"},
        {"tag": "#难度_高阶", "description": "分析综合级考点，复杂推理与综合论述", "module": "通用"},
        {"tag": "#经济_商品货币", "description": "商品与货币相关知识点", "module": "经济生活"},
        {"tag": "#经济_生产分配", "description": "生产与分配相关知识点", "module": "经济生活"},
        {"tag": "#经济_市场经济", "description": "市场经济与宏观调控相关知识点", "module": "经济生活"},
        {"tag": "#经济_全球化", "description": "经济全球化与对外开放相关知识点", "module": "经济生活"},
        {"tag": "#政治_国家公民", "description": "国家性质与公民权利相关知识点", "module": "政治生活"},
        {"tag": "#政治_政党制度", "description": "政党制度与多党合作相关知识点", "module": "政治生活"},
        {"tag": "#政治_人大制度", "description": "人民代表大会制度相关知识点", "module": "政治生活"},
        {"tag": "#政治_国际社会", "description": "国际社会与外交政策相关知识点", "module": "政治生活"},
        {"tag": "#哲学_唯物论", "description": "辩证唯物论相关知识点", "module": "哲学常识"},
        {"tag": "#哲学_辩证法", "description": "唯物辩证法相关知识点", "module": "哲学常识"},
        {"tag": "#哲学_认识论", "description": "认识论相关知识点", "module": "哲学常识"},
        {"tag": "#哲学_历史唯物", "description": "历史唯物主义相关知识点", "module": "哲学常识"},
        {"tag": "#法律_公民权利", "description": "公民基本权利义务相关知识点", "module": "法律道德"},
        {"tag": "#法律_法律基础", "description": "法律基础知识相关知识点", "module": "法律道德"},
        {"tag": "#考频_高频", "description": "高频考点，需重点掌握", "module": "通用"},
        {"tag": "#考频_中频", "description": "中等频率考点", "module": "通用"},
        {"tag": "#时政_国内", "description": "国内时政热点相关知识点", "module": "时事政治"},
        {"tag": "#时政_国际", "description": "国际时政热点相关知识点", "module": "时事政治"}
    ]
})
print('[OK] knowledge/kb_tags.json')

# 5. knowledge/kb_abilities.json
write_json(os.path.join(BASE, 'knowledge', 'kb_abilities.json'), {
    "version": "1.0.0",
    "last_updated": "2026-08-02",
    "cognitive_model": "布鲁姆认知层级（上海考纲五级）",
    "abilities": [
        {"id": "AB1", "level": "识记", "bloom_level": 1, "description": "再现基本概念、原理和重大时事", "weight": 0.10},
        {"id": "AB2", "level": "理解", "bloom_level": 2, "description": "概括基本概念，辨别区别，阐述联系", "weight": 0.35},
        {"id": "AB3", "level": "分析", "bloom_level": 4, "description": "运用知识分析说明社会现象", "weight": 0.35},
        {"id": "AB4", "level": "综合", "bloom_level": 5, "description": "综合运用知识进行较为全面深入的论述", "weight": 0.10},
        {"id": "AB5", "level": "评价", "bloom_level": 6, "description": "作出正确价值判断和评价，选择正确行为", "weight": 0.10}
    ],
    "cross_module_abilities": [
        {"id": "CA1", "name": "经济-政治联动分析", "description": "运用政治经济学视角分析社会现象", "requires_modules": ["经济生活", "政治生活"]},
        {"id": "CA2", "name": "哲学-时政联动分析", "description": "用唯物辩证法分析时政热点", "requires_modules": ["哲学常识", "时事政治"]},
        {"id": "CA3", "name": "法律-政治联动分析", "description": "结合法律知识分析政治参与", "requires_modules": ["法律道德", "政治生活"]}
    ]
})
print('[OK] knowledge/kb_abilities.json')

# 6. knowledge/kb_vocab.json（骨架）
write_json(os.path.join(BASE, 'knowledge', 'kb_vocab.json'), {
    "version": "1.0.0",
    "last_updated": "2026-08-02",
    "total_entries": 3,
    "entries": [
        {
            "id": "POLI_E001",
            "term": "商品",
            "definition": "用于交换的劳动产品，具有使用价值和价值两个基本属性。",
            "module": "经济生活",
            "chain_id": "POLI_经济_商品货币",
            "tags": ["#经济_商品货币", "#难度_初阶"],
            "example": "农民生产的粮食用于出售时即为商品，自家消费则不是商品。"
        },
        {
            "id": "POLI_E002",
            "term": "货币的职能",
            "definition": "价值尺度、流通手段、贮藏手段、支付手段、世界货币。其中价值尺度和流通手段是基本职能。",
            "module": "经济生活",
            "chain_id": "POLI_经济_商品货币",
            "tags": ["#经济_商品货币", "#难度_中阶", "#考频_高频"],
            "example": "商店里商品标价（价值尺度）；用人民币购买商品（流通手段）。"
        },
        {
            "id": "POLI_P001",
            "term": "人民民主专政",
            "definition": "我国的国体。工人阶级领导的、以工农联盟为基础的人民民主专政的社会主义国家。对人民实行民主，对极少数敌人实行专政。",
            "module": "政治生活",
            "chain_id": "POLI_政治_国家公民",
            "tags": ["#政治_国家公民", "#难度_中阶", "#考频_高频"],
            "example": "我国宪法规定：中华人民共和国是工人阶级领导的、以工农联盟为基础的人民民主专政的社会主义国家。"
        }
    ]
})
print('[OK] knowledge/kb_vocab.json（骨架，3个示例条目）')

print('\n=== 政治科目 KB 骨架全部生成完毕 ===')
