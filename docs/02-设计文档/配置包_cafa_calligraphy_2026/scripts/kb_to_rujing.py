"""
KB Vocab → rujing Card Package 转换器
将 cafa_calligraphy_2026/knowledge/kb_vocab.json 转换为 rujing App 可导入的卡片包

用法：
  python kb_to_rujing.py [--output OUTPUT_DIR]

输出：
  cafa_cards.json       — rujing 卡片包
  cafa_chain_narratives.json — 链叙事文本

依赖：Python 3.8+，仅使用标准库
"""

import json
import sys
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any


# ── 链结构定义（8集墨骨山河 × 古汉语基础）───────────────────────────

CHAINS = {
    "CHAIN_CAFA_古汉语基础": {
        "chain_id": "CHAIN_CAFA_古汉语基础",
        "title": "古汉语·文字学基础",
        "chain_type": "CAUSAL",  # 因果链
        "tags": ["#书法", "#古汉语", "#文字学"],
        "episodes": [2],  # 对应 ep02 许慎
    },
    "CHAIN_CAFA_译篆要诀": {
        "chain_id": "CHAIN_CAFA_译篆要诀",
        "title": "古汉语·译篆要诀",
        "chain_type": "ELEMENT",  # 要素链
        "tags": ["#书法", "#古汉语", "#译篆"],
        "episodes": [2],
    },
    "CHAIN_CAFA_句读标志": {
        "chain_id": "CHAIN_CAFA_句读标志",
        "title": "古汉语·句读标志词",
        "chain_type": "ELEMENT",  # 要素链
        "tags": ["#书法", "#古汉语", "#句读"],
        "episodes": [4],
    },
    "CHAIN_CAFA_Ep01_秦篆之源": {
        "chain_id": "CHAIN_CAFA_Ep01_秦篆之源",
        "title": "墨骨山河·Ep01 秦篆之源",
        "chain_type": "TIMELINE",  # 时序链
        "tags": ["#书法", "#书法史", "#秦代"],
        "episodes": [1],
    },
    "CHAIN_CAFA_Ep02_说文解字": {
        "chain_id": "CHAIN_CAFA_Ep02_说文解字",
        "title": "墨骨山河·Ep02 说文解字",
        "chain_type": "TIMELINE",
        "tags": ["#书法", "#书法史", "#东汉"],
        "episodes": [2],
    },
    "CHAIN_CAFA_Ep03_兰亭之雅": {
        "chain_id": "CHAIN_CAFA_Ep03_兰亭之雅",
        "title": "墨骨山河·Ep03 兰亭之雅",
        "chain_type": "TIMELINE",
        "tags": ["#书法", "#书法史", "#魏晋"],
        "episodes": [3],
    },
    "CHAIN_CAFA_Ep04_书谱之道": {
        "chain_id": "CHAIN_CAFA_Ep04_书谱之道",
        "title": "墨骨山河·Ep04 书谱之道",
        "chain_type": "TIMELINE",
        "tags": ["#书法", "#书法史", "#唐代"],
        "episodes": [4],
    },
    "CHAIN_CAFA_Ep05_颠张醉素": {
        "chain_id": "CHAIN_CAFA_Ep05_颠张醉素",
        "title": "墨骨山河·Ep05 颠张醉素",
        "chain_type": "TIMELINE",
        "tags": ["#书法", "#书法史", "#唐代"],
        "episodes": [5],
    },
    "CHAIN_CAFA_Ep06_颜筋柳骨": {
        "chain_id": "CHAIN_CAFA_Ep06_颜筋柳骨",
        "title": "墨骨山河·Ep06 颜筋柳骨",
        "chain_type": "TIMELINE",
        "tags": ["#书法", "#书法史", "#唐代"],
        "episodes": [6],
    },
    "CHAIN_CAFA_Ep07_黄州突围": {
        "chain_id": "CHAIN_CAFA_Ep07_黄州突围",
        "title": "墨骨山河·Ep07 黄州突围",
        "chain_type": "TIMELINE",
        "tags": ["#书法", "#书法史", "#宋代"],
        "episodes": [7],
    },
    "CHAIN_CAFA_Ep08_碑学中兴": {
        "chain_id": "CHAIN_CAFA_Ep08_碑学中兴",
        "title": "墨骨山河·Ep08 碑学中兴",
        "chain_type": "TIMELINE",
        "tags": ["#书法", "#书法史", "#清代"],
        "episodes": [8],
    },
}

# ── KB条目 → Chain 映射规则 ──────────────────────────────────────

def assign_chain(kb_id: str, tags: List[str]) -> str:
    """根据 kb_id 和 tags 将 KB 条目分配到对应 Chain"""
    # 译篆类
    if "译篆" in str(tags) or kb_id in ["KB_CAFA_011", "KB_CAFA_012", "KB_CAFA_013", "KB_CAFA_014", "KB_CAFA_015"]:
        return "CHAIN_CAFA_译篆要诀"
    # 句读类
    if "句读" in str(tags) or kb_id in ["KB_CAFA_016", "KB_CAFA_017", "KB_CAFA_018"]:
        return "CHAIN_CAFA_句读标志"
    # 文字学基础
    if kb_id in ["KB_CAFA_001", "KB_CAFA_002"]:
        return "CHAIN_CAFA_古汉语基础"
    # 各集
    ep_map = {
        "KB_CAFA_003": "CHAIN_CAFA_Ep06_颜筋柳骨",  # 宋四家（颜真卿关联）
        "KB_CAFA_004": "CHAIN_CAFA_Ep04_书谱之道",  # 书谱
        "KB_CAFA_005": "CHAIN_CAFA_Ep08_碑学中兴",  # 金石学
        "KB_CAFA_006": "CHAIN_CAFA_Ep08_碑学中兴",  # 碑学帖学
        "KB_CAFA_007": "CHAIN_CAFA_Ep03_兰亭之雅",  # 永字八法
        "KB_CAFA_008": "CHAIN_CAFA_Ep08_碑学中兴",  # 南北书派论
        "KB_CAFA_009": "CHAIN_CAFA_Ep07_黄州突围",  # 尚意书风
        "KB_CAFA_010": "CHAIN_CAFA_Ep05_颠张醉素",  # 锥画沙/屋漏痕
    }
    return ep_map.get(kb_id, "CHAIN_CAFA_古汉语基础")


# ── 卡片类型映射 ─────────────────────────────────────────────────

def map_card_type(tags: List[str], answer_template: str) -> str:
    """将 KB 条目标签映射为 rujing CardType"""
    if "译篆" in str(tags):
        return "STRATEGY"  # 译篆是技法心法
    if "句读" in str(tags):
        return "STRATEGY"  # 句读是技法心法
    return "NODE"


# ── 核心转换函数 ──────────────────────────────────────────────────

def kb_entry_to_card(entry: Dict[str, Any], chain_id: str, chain_title: str) -> Dict[str, Any]:
    """将单个 KB 条目转换为 rujing 卡片"""
    kb_id = entry.get("kb_id", "")
    concept = entry.get("concept", "")
    definition = entry.get("definition", "")
    structured = entry.get("structured_content", {})
    exam_tips = entry.get("exam_tips", {})
    answer_template = entry.get("answer_template", "")
    tags = entry.get("tags", [])

    card_type = map_card_type(tags, answer_template)

    # front: 考题式提问
    exam_type = extract_exam_type(tags)
    front = build_front(exam_type, concept)

    # back_core: 核心答案
    back_core = build_back_core(structured, definition)

    # back_detail: 完整解析（包含答题要点+常见错误）
    back_detail = build_back_detail(structured, exam_tips, answer_template, concept)

    # 从标签提取难度
    difficulty = extract_difficulty(tags)

    # 采分点
    scoring_points = exam_tips.get("scoring_points", [])
    common_mistakes = exam_tips.get("common_mistakes", [])

    now = int(datetime.now().timestamp())

    return {
        "card_id": f"CAFA_{kb_id}",
        "chain_id": chain_id,
        "chain_title": chain_title,
        "subject": "书法",  # 对应 rujing Subject.CALLIGRAPHY（值="书法"）
        "card_type": card_type,
        "front": front,
        "back_core": back_core,
        "back_detail": back_detail,
        "maturity": "RAW",  # 新导入的都是生卡
        "tags": tags,
        "difficulty": difficulty,
        "exam_type": exam_type,
        "scoring_points": scoring_points,
        "common_mistakes": common_mistakes,
        "answer_template": answer_template,
        "last_reviewed": 0,
        "created_at": now,
        "updated_at": now,
    }


def extract_exam_type(tags: List[str]) -> str:
    """从标签提取考点类型"""
    for tag in tags:
        if "考点类型" in tag:
            return tag.replace("#考点类型/", "")
    return "名词解释"


def extract_difficulty(tags: List[str]) -> str:
    """从标签提取认知层级作为难度"""
    for tag in tags:
        if "认知层级" in tag:
            return tag.replace("#认知层级/", "")
    # 从考频推断
    for tag in tags:
        if "考频" in tag:
            freq = tag.replace("#考频/", "")
            if "⭐⭐⭐⭐⭐" in freq:
                return "L3"
            elif "⭐⭐⭐⭐" in freq:
                return "L2"
            else:
                return "L1"
    return "L2"


def build_front(exam_type: str, concept: str) -> str:
    """生成卡片正面（考题式）"""
    if exam_type == "译篆":
        return f"「{concept.split('：')[1].split('vs')[0].strip() if 'vs' in concept else concept}」的篆书写法是什么？"
    elif exam_type == "句读翻译":
        return f"「{concept}」如何断句？"
    else:
        return f"名词解释：{concept}"


def build_back_core(structured: Dict, definition: str) -> str:
    """生成 back_core：核心答案"""
    if isinstance(structured, dict) and structured:
        # 取第一个主要字段
        first_key = list(structured.keys())[0]
        first_val = structured[first_key]
        if isinstance(first_val, str):
            return f"{first_key}：{first_val}"
        elif isinstance(first_val, dict):
            return f"{first_key}：{str(first_val)[:80]}"
    return definition[:100]


def build_back_detail(structured: Dict, exam_tips: Dict, answer_template: str, concept: str) -> str:
    """生成 back_detail：完整解析"""
    lines = [f"【概念】{concept}"]

    if structured:
        lines.append("【核心内容】")
        for key, val in structured.items():
            if isinstance(val, str):
                lines.append(f"  · {key}：{val}")
            elif isinstance(val, list):
                lines.append(f"  · {key}：")
                for item in val:
                    lines.append(f"    - {item}")
            elif isinstance(val, dict):
                lines.append(f"  · {key}：")
                for k2, v2 in val.items():
                    lines.append(f"    - {k2}：{v2}")

    if exam_tips.get("scoring_points"):
        lines.append("【采分点】")
        for p in exam_tips["scoring_points"]:
            lines.append(f"  ✓ {p}")

    if exam_tips.get("common_mistakes"):
        lines.append("【常见错误】")
        for m in exam_tips["common_mistakes"]:
            lines.append(f"  ✗ {m}")

    if answer_template:
        lines.append(f"【答题模板】{answer_template}")

    return "\n".join(lines)


# ── 链叙事文本生成 ────────────────────────────────────────────────

def generate_chain_narratives() -> Dict[str, str]:
    """生成链叙事文本（来自 micro_dramas.json 系列索引）"""
    narratives = {
        "CHAIN_CAFA_古汉语基础": (
            "古汉语是书法史论阅读的基础，也是国美书法校考「句读与翻译」题型的核心考点。"
            "本链聚焦文字学根基：许慎《说文解字》与六书理论。"
            "掌握六书，才能理解汉字的字形演变；理解《说文解字》，才能在译篆题中写出正确的篆形。"
            "【学习提示】先记六书名称与定义，再理解转注假借与造字法的区别，最后用真题练习。"
        ),
        "CHAIN_CAFA_译篆要诀": (
            "译篆题是国美书法校考的特色题型，要求将简体字按《说文解字》标准译为小篆。"
            "难点在于「一简对多篆」：同一个简体字在不同词义下对应不同篆形。"
            "本链收录高频混淆字：斗/鬥、发/髮/發、复/複/復、尘/塵、云/雲。"
            "【答题要点】看清语境，判断词义，再按《说文》部首写出正篆。禁止写简化字。"
        ),
        "CHAIN_CAFA_句读标志": (
            "文言文断句的核心是找到标志词。「者…也」判断句、「夫」发语词、「曰」「云」引语词、"
            "「也」「矣」句末语气词——这些是断句的黄金线索。"
            "本链从孙过庭《书谱》原文中提炼高频句读标志词。"
            "【学习提示】先熟记标志词，再做真题练习。注意同一词在不同位置有不同用法。"
        ),
        "CHAIN_CAFA_Ep01_秦篆之源": (
            "公元前221年，秦始皇统一六国，建立中国第一个中央集权王朝。"
            "「书同文」是帝国统一的文化基石——废除六国文字，以小篆为标准字体。"
            "峄山碑是现存最早的小篆纪功刻石之一，书法史上关于秩序与美的问题，在这一刻开始。"
        ),
        "CHAIN_CAFA_Ep02_说文解字": (
            "东汉许慎用三十年写成《说文解字》，以小篆为基准，首创540部首体系，归纳六书理论。"
            "这部书不只是字典——它是整个中国文字学的起点，也是后世书法家理解汉字字形的根本依据。"
        ),
        "CHAIN_CAFA_Ep03_兰亭之雅": (
            "永和九年，王羲之与友人会于会稽山阴之兰亭，曲水流觞，一气呵成《兰亭序》。"
            "这部作品被誉为「天下第一行书」，不仅是技法的胜利，更是生命哲学的流淌。"
            "「后之览者，亦将有感于斯文」——王羲之写下这句话时，书法已经成为一种生命表达。"
        ),
        "CHAIN_CAFA_Ep04_书谱之道": (
            "孙过庭以草书写成《书谱》，既是理论著作，又是草书墨迹——中国书法史上罕见的双重经典。"
            "「古质而今妍」「五乖五合」「达其情性，形其哀乐」——这些命题到今天依然有效。"
        ),
        "CHAIN_CAFA_Ep05_颠张醉素": (
            "张旭和怀素以癫狂闻名——旭素合称，是草书史上的两座高峰。"
            "张旭「古木盘涡」，怀素「骤雨旋风」。他们的草书不是放弃技法，而是彻底掌握了技法之后的自由。"
        ),
        "CHAIN_CAFA_Ep06_颜筋柳骨": (
            "颜真卿是中国书法史上绕不过的名字。安史之乱中他起兵抵抗，家族三十余人遇难。"
            "《祭侄文稿》是悲痛到了极致的笔墨——不是写字，是用生命在写。"
            "与柳公权的「柳骨」并称「颜筋柳骨」，构成楷书史上的双峰。"
        ),
        "CHAIN_CAFA_Ep07_黄州突围": (
            "元丰三年，苏轼因乌台诗案被贬黄州。在人生的至暗时刻，他写下了《黄州寒食诗帖》。"
            "「也拟哭途穷，死灰吹不起」——这首诗的结尾，恰好是书法史上最动人的一笔。"
            "《黄州寒食诗帖》被称为「天下第三行书」，是「尚意」书风的最高代表。"
        ),
        "CHAIN_CAFA_Ep08_碑学中兴": (
            "清代乾隆年间，阮元提出「南北书派论」，包世臣推波助澜，康有为写成《广艺舟双楫》。"
            "「尊碑卑帖」——他们号召书法家向被遗忘了一千年的碑刻学习，复兴篆隶古法。"
            "这场碑学运动，深刻改变了清末民国的书法审美与取法方向。"
        ),
    }
    return narratives


# ── 主函数 ────────────────────────────────────────────────────────

def main():
    # 解析参数
    output_dir = Path(__file__).parent
    if "--output" in sys.argv:
        idx = sys.argv.index("--output")
        output_dir = Path(sys.argv[idx + 1])

    # KB Vocab 路径（使用绝对路径避免编码问题）
    KB_VOCAB_PATH = Path(r"C:\Users\willi\Desktop\我的视野\0713-基于知识库的高阶备考智能体\02-设计文档\配置包_cafa_calligraphy_2026\knowledge\kb_vocab.json")
    if not KB_VOCAB_PATH.exists():
        print(f"ERROR: kb_vocab.json not found at {KB_VOCAB_PATH}")
        sys.exit(1)

    with open(KB_VOCAB_PATH, "r", encoding="utf-8") as f:
        kb_data = json.load(f)

    entries = kb_data.get("entries", [])
    print(f"读取到 {len(entries)} 个 KB 条目")

    # 初始化链元数据
    chain_ids_seen = set()
    chains_meta = {}  # chain_id → {cards: [], chain_data: {}}

    # 转换每条 KB 条目
    cards = []
    for entry in entries:
        kb_id = entry.get("kb_id", "")
        tags = entry.get("tags", [])
        chain_id = assign_chain(kb_id, tags)
        chain_title = CHAINS.get(chain_id, {}).get("title", chain_id)

        card = kb_entry_to_card(entry, chain_id, chain_title)
        cards.append(card)

        if chain_id not in chain_ids_seen:
            chain_ids_seen.add(chain_id)
            chains_meta[chain_id] = {
                "cards": [],
                "chain_data": CHAINS.get(chain_id, {
                    "chain_id": chain_id,
                    "title": chain_title,
                    "chain_type": "CAUSAL",
                    "tags": [],
                    "episodes": [],
                })
            }
        chains_meta[chain_id]["cards"].append(card["card_id"])

    print(f"生成 {len(cards)} 张卡片，分配到 {len(chains_meta)} 条链")

    # 生成 rujing 卡片包
    package = {
        "schema_version": "1.0",
        "pack_id": "cafa_calligraphy_2026",
        "pack_title": "国美书法校考·墨骨山河系列",
        "total_cards": len(cards),
        "total_chains": len(chains_meta),
        "generated_at": datetime.now().isoformat(),
        "node_cards": cards,
    }

    # 生成链叙事
    narratives_map = generate_chain_narratives()
    chain_narratives = {}
    for chain_id, narrative in narratives_map.items():
        if chain_id in chains_meta:
            chain_narratives[chain_id] = narrative

    # 输出文件
    cards_out = output_dir / "cafa_cards.json"
    narratives_out = output_dir / "cafa_chain_narratives.json"

    with open(cards_out, "w", encoding="utf-8") as f:
        json.dump(package, f, ensure_ascii=False, indent=2)
    print(f"✓ 卡片包 → {cards_out}")

    with open(narratives_out, "w", encoding="utf-8") as f:
        json.dump(chain_narratives, f, ensure_ascii=False, indent=2)
    print(f"✓ 链叙事 → {narratives_out}")

    # 生成链元数据摘要
    chains_out = output_dir / "cafa_chains_meta.json"
    chains_summary = {}
    for chain_id, meta in chains_meta.items():
        chain_data = meta["chain_data"]
        chains_summary[chain_id] = {
            "chain_id": chain_id,
            "title": chain_data.get("title", chain_id),
            "chain_type": chain_data.get("chain_type", "CAUSAL"),
            "tags": chain_data.get("tags", []),
            "card_ids": meta["cards"],
            "card_count": len(meta["cards"]),
        }

    with open(chains_out, "w", encoding="utf-8") as f:
        json.dump(chains_summary, f, ensure_ascii=False, indent=2)
    print(f"✓ 链元数据 → {chains_out}")

    # 打印摘要
    print("\n── 链分配摘要 ──────────────────")
    for chain_id, meta in chains_meta.items():
        title = chains_summary[chain_id]["title"]
        count = len(meta["cards"])
        print(f"  {title}: {count} 张卡片")

    print(f"\n完成。共 {len(cards)} 张卡片，{len(chains_meta)} 条链。")


if __name__ == "__main__":
    main()
