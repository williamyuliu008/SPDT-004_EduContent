# -*- coding: utf-8 -*-
"""
批量增强 kb_vocab_enhanced.json 中的 KB_CAFA_S* 条目
为每个条目补充：
  - structured_content.historical_period
  - structured_content.background
  - exam_tips (扩充版: scoring_points / common_mistakes / 记忆口诀 / 延伸考点)
  - answer_template
  - cross_pack_links (根据 KB_CAFA_S* 之间的关联)

用法: python batch_enhance.py [start_index] [count]
示例: python batch_enhance.py 0 50   # 从第0条开始，增强50条
      python batch_enhance.py        # 全部增强（约137条）
"""
import json, sys, os, time
from pathlib import Path

# ── 路径配置 ────────────────────────────────────────────────────────────────
PT_ROOT = Path(__file__).parent.parent
KB_PATH_IN  = PT_ROOT / "_03_subject_packs" / "cafa_calligraphy_2026" / "knowledge" / "kb_vocab.json"
KB_PATH_OUT = PT_ROOT / "_03_subject_packs" / "cafa_calligraphy_2026" / "knowledge" / "kb_vocab_enhanced.json"

# GLM API key
API_KEY_PATH = Path("D:/_CEO/bulletin/SECRET_KEY/zhipu_api.txt")
if API_KEY_PATH.exists():
    os.environ["ZHIPU_API_KEY"] = API_KEY_PATH.read_text(encoding="utf-8").strip()

LLM_MODE = "glm" if os.environ.get("ZHIPU_API_KEY") else "mock"

# ── 已有跨链接映射（手动维护核心关联）──────────────────────────────────────
CROSS_LINKS_MAP = {
    "KB_CAFA_S001": [
        {"kb_id": "KB_CAFA_S005", "title": "颜真卿", "pack_id": "cafa_calligraphy_2026", "note": "宋四家之一，需结合备考"},
        {"kb_id": "KB_CAFA_S002", "title": "王羲之", "pack_id": "cafa_calligraphy_2026", "note": "书圣，行书奠基者"},
        {"kb_id": "KB_CAFA_S013", "title": "尚意书风", "pack_id": "cafa_calligraphy_2026", "note": "宋代书法美学核心概念"},
    ],
    "KB_CAFA_S002": [
        {"kb_id": "KB_CAFA_S003", "title": "王献之", "pack_id": "cafa_calligraphy_2026", "note": "王羲之子，合称\u201c二王\u201d"},
        {"kb_id": "KB_CAFA_S010", "title": "天下三大行书", "pack_id": "cafa_calligraphy_2026", "note": "兰亭序为天下第一行书"},
    ],
    "KB_CAFA_S003": [
        {"kb_id": "KB_CAFA_S002", "title": "王羲之", "pack_id": "cafa_calligraphy_2026", "note": "王献之父，合称\u201c二王\u201d"},
    ],
    "KB_CAFA_S005": [
        {"kb_id": "KB_CAFA_S010", "title": "天下三大行书", "pack_id": "cafa_calligraphy_2026", "note": "祭侄文稿为天下第二行书"},
        {"kb_id": "KB_CAFA_S001", "title": "宋四家", "pack_id": "cafa_calligraphy_2026", "note": "颜真卿是宋四家之首"},
    ],
    "KB_CAFA_S013": [
        {"kb_id": "KB_CAFA_S005", "title": "宋四家", "pack_id": "cafa_calligraphy_2026", "note": "苏轼是尚意书风代表"},
        {"kb_id": "KB_CAFA_S010", "title": "天下三大行书", "pack_id": "cafa_calligraphy_2026", "note": "苏轼《黄州寒食诗帖》是天下第三行书"},
    ],
}

def get_llm_client():
    """创建 LLM 客户端"""
    if LLM_MODE == "mock":
        return None
    try:
        from openai import OpenAI
        client = OpenAI(
            api_key=os.environ["ZHIPU_API_KEY"],
            base_url="https://open.bigmodel.cn/api/paas/v4/"
        )
        return client
    except ImportError:
        return None

SYSTEM_PROMPT = (
    "你是一位中国美术学院书法史论考试专家，擅长为备考学生整理高质量的名词解释资料。"
    "你的输出必须："
    "1. 内容准确，有学术依据"
    "2. 从应试角度设计：有得分要点、常见失分点、记忆口诀、延伸考点"
    "3. 语言简洁有条理，适合在知识库工具中展示"
    "4. 背景补充要有历史深度，能帮助理解和联想"
    "5. 回答用中文，JSON格式输出，不要有多余文字"
)

def build_prompt(kb_id, concept, definition, existing_sc):
    """构建 LLM 增强 prompt"""
    sc_str = json.dumps(existing_sc, ensure_ascii=False, indent=2) if existing_sc else "{}"
    return {
        "role": "user",
        "content": (
            f"请为以下书法史名词解释生成增强内容，用于备考知识库。\n\n"
            f"知识ID: {kb_id}\n"
            f"名词: {concept}\n"
            f"现有定义: {definition}\n"
            f"现有结构化内容:\n{sc_str}\n\n"
            f"请生成以下JSON字段（只输出JSON，不要其他文字）：\n"
            f'{{"historical_period": "...(时代背景简述，一句话)", '
            f'"background": "...(200-400字的背景补充，'
            f'含历史背景、艺术分析、情感线索、易混辨析，'
            f'用\\n\\n分段，第一段历史背景，第二段艺术分析，第三段应试提示)", '
            f'"exam_tips": {{'
            f'"scoring_points": ["要点1","要点2","..."],'
            f'"common_mistakes": ["错误1","错误2","..."],'
            f'"记忆口诀": ["口诀1","口诀2","..."],'
            f'"延伸考点": ["考点1","考点2","..."]'
            f'}}, '
            f'"answer_template": "...(答题模板，80-150字)"}}\n'
        )
    }

def call_glm(client, messages, model="glm-4-flash"):
    """调用 GLM API，带超时保护"""
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.3,
            timeout=15.0,  # 15秒超时保护
        )
        return resp.choices[0].message.content
    except Exception as e:
        print(f"  [GLM ERROR] {e}")
        return None

# ── S010 专项增强（手动精品内容）────────────────────────────────────────────
MANUAL_S010 = {
    "kb_id": "KB_CAFA_S010",
    "concept": "天下三大行书",
    "historical_period": "353年(东晋永和九年)至1082年(北宋元丰五年)，横跨近八百年。第一高峰:王羲之《兰亭序》(353年)，确立行书审美典范。第二高峰:颜真卿《祭侄文稿》(758年)，行书与家国情感融合。第三高峰:苏轼《黄州寒食诗帖》(1082年)，尚意书风之旗帜。",
    "background": (
        "【第一·兰亭序】东晋永和九年(353)三月，王羲之与友人谢安、孙绰等四十二人雅集兰亭，临流赋诗。"
        "酒酣兴浓之际，羲之挥毫作序，凡二十八行，三百二十四字。"
        "通篇用笔精到，一气呵成。"之"字出现二十余次，笔笔姿态不同。"
        "唐太宗李世民极度推崇，亲笔摹写，原作随葬昭陵。历代书法家奉为"天下第一行书"。\n\n"
        "【第二·祭侄文稿】乾元元年(758)，颜真卿侄子颜季明于安史之乱殉国。"
        "两年后寻得遗骸仅头颅一具，悲愤交加之际，颜真卿写下此文稿。"
        "全篇涂改三十余处，焦墨枯笔，情感喷薄，"屋漏痕"笔法自然流露。"
        "后世评为"天下第二行书"，誉为"无意于书，而书自工"。\n\n"
        "【第三·黄州寒食诗帖】元丰三年苏轼因"乌台诗案"被贬黄州，处境困厄。"
        "元丰五年寒食节，天雨不绝，诗人独处破屋，作寒食二首，后亲笔书写。"
        "全篇笔力沉厚，结体开张，黄庭坚跋曰"此书兼颜鲁公、杨少师、李西台笔意"。\n\n"
        "【三者共性】①皆为书写者人生巅峰状态的情感宣泄之作；②情感驱动技法；"
        "③既是书法经典，也是历史文献；④共同构建中国行书审美坐标系。"
        "理解三大行书，本质上是理解中国书法的"情感本体论"。\n\n"
        "【应试提示】王羲之晚年面临五胡乱华，颜真卿满门忠烈最终殉国，苏轼九死一生贬谪黄州。"
        "这种"家国之大悲"正是三大行书诞生的情感土壤，也是国美考试的高频深挖点。"
    ),
    "exam_tips": {
        "scoring_points": [
            "三件作品名称、作者、朝代全写（3分）",
            "第一/二/三位置严格对应，不得颠倒（2分）",
            "苏轼朝代：北宋；颜真卿朝代：唐代；王羲之朝代：东晋（1分）",
            "1-2句艺术特点描述（2分）",
            "说明"天下第X行书"称号来源（1分）"
        ],
        "common_mistakes": [
            "致命：苏轼写成唐代人（错！苏轼是北宋）直接扣3分",
            "致命：顺序颠倒至少扣2分",
            "常见：只写《兰亭序》一件作品，只得1-2分",
            "细节：颜真卿写成"颜真"或遗漏"真卿"全名"
        ],
        "记忆口诀": [
            "位置口诀："兰亭祭侄寒食诗，一二三分清楚"",
            "朝代口诀："羲之东晋真卿唐，东坡北宋不能忘"",
            "情感线索："兰亭雅集真卿悲，苏轼寒食独自醉""
        ],
        "延伸考点": [
            "为何《祭侄文稿》涂改很多却更珍贵？（考情感真实性与技法自然性）",
            "苏轼为何是"尚意"书风代表？（考宋代书法美学转型）",
            "王羲之"书圣"地位如何确立？（考后世接受史）",
            "若选"第四大行书"选谁？（怀素《自叙帖》、杨凝式《韭花帖》）"
        ]
    },
    "answer_template": (
        "一、名词界定（1句）\n"
        "中国书法史上公认的成就最高的三件行书作品，被誉为"天下三大行书"。\n\n"
        "二、三件作品（每个写2-3句）\n"
        "第一：王羲之《兰亭序》\n"
        "- 王羲之（字逸少），东晋书法家，有"书圣"之誉\n"
        "- 永和九年（353年）三月三日，雅集兰亭，临流赋诗，为诗集作序\n"
        "- 艺术特点：用笔精到，"之"字二十余变；结构秀美，章法疏朗\n"
        "- 地位："天下第一行书"，确立行书审美典范\n\n"
        "第二：颜真卿《祭侄文稿》\n"
        "- 颜真卿（字清臣），唐代书法家，楷书四大家之一\n"
        "- 乾元元年（758）为殉国侄子颜季明所作祭文\n"
        "- 艺术特点：涂改自然，焦墨枯笔，"屋漏痕"笔法，忠愤溢于笔端\n"
        "- 地位："天下第二行书"，行书与家国情怀融合之典范\n\n"
        "第三：苏轼《黄州寒食诗帖》\n"
        "- 苏轼（字子瞻，号东坡），北宋文学家、书法家\n"
        "- 元丰五年（1082）被贬黄州后所作寒食诗并亲笔书写\n"
        "- 艺术特点：笔力沉厚，结体开张；"尚意"书风代表\n"
        "- 地位："天下第三行书"，宋代尚意书风之旗帜\n\n"
        "三、总结（1句）\n"
        "三者分别代表东晋风流、唐代忠烈、宋代意韵，构成中国行书最高坐标。\n\n"
        "【失分警示】顺序颠倒扣2分；苏轼朝代写成唐代直接扣3分；只写一件作品最多得2分。"
    ),
    "cross_pack_links": [
        {"kb_id": "KB_CAFA_S005", "title": "颜真卿", "pack_id": "cafa_calligraphy_2026",
         "note": "天下第二行书作者，需与本文综合备考"},
        {"kb_id": "KB_CAFA_S001", "title": "宋四家", "pack_id": "cafa_calligraphy_2026",
         "note": "苏轼是宋四家之一，整体框架结合记忆"},
        {"kb_id": "KB_CAFA_S002", "title": "王羲之", "pack_id": "cafa_calligraphy_2026",
         "note": "书圣，天下第一行书作者"},
        {"kb_id": "KB_CAFA_S013", "title": "尚意书风", "pack_id": "cafa_calligraphy_2026",
         "note": "宋代书法美学，苏轼是尚意提出者"}
    ]
}


def mock_enhance(kb_id, concept, definition, existing_sc):
    """Mock 模式：生成占位内容"""
    return {
        "historical_period": f"{concept}相关历史时期概述",
        "background": f"【背景】{concept}的背景内容（需启用GLM或手动补充）",
        "exam_tips": {
            "scoring_points": [f"{concept}的基本定义和历史地位"],
            "common_mistakes": ["与其他相似概念混淆"],
            "记忆口诀": [f"{concept[0]}字诀：..."],
            "延伸考点": ["与其他知识点的联系"]
        },
        "answer_template": f"{concept}是...\n\n【答题框架】\n1. 定义：...\n2. 历史背景：...\n3. 艺术特点：...\n4. 地位影响：..."
    }

def main():
    # 解析参数
    start_idx = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    max_count = int(sys.argv[2]) if len(sys.argv) > 2 else 9999

    # 加载知识库（从原始文件读取）
    with open(KB_PATH_IN, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 收集所有 KB_CAFA_S* 条目（保持原顺序）
    all_entries = []
    for mod_name, mod_data in data["modules"].items():
        for cat_name, items in mod_data.items():
            for item in items:
                if item.get("kb_id", "").startswith("KB_CAFA_S"):
                    all_entries.append(item)

    total = len(all_entries)

    # ── 先处理 S010 专项内容 ───────────────────────────────────────────────
    if start_idx == 0:
        for entry in all_entries:
            if entry.get("kb_id") == MANUAL_S010["kb_id"]:
                sc = entry["structured_content"]
                sc["historical_period"] = MANUAL_S010["historical_period"]
                sc["background"] = MANUAL_S010["background"]
                entry["exam_tips"] = MANUAL_S010["exam_tips"]
                entry["answer_template"] = MANUAL_S010["answer_template"]
                entry["cross_pack_links"] = MANUAL_S010["cross_pack_links"]
                print(f"[MANUAL] 已注入 S010 精品内容: {entry['concept']}")
                with open(KB_PATH_OUT, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                print(f"[MANUAL] S010 已保存")
                break

    to_process = all_entries[start_idx:start_idx + max_count]
    print(f"[batch_enhance] 总条目: {total} | 本次处理: {start_idx} ~ {start_idx + len(to_process) - 1}")
    print(f"[batch_enhance] LLM 模式: {LLM_MODE}")

    client = get_llm_client()
    save_every = 5  # 每处理 N 条保存一次
    saved_count = 0

    for i, entry in enumerate(to_process):
        kb_id = entry.get("kb_id", "")
        concept = entry.get("concept", "")
        definition = entry.get("definition", "")
        existing_sc = entry.get("structured_content", {})

        idx = start_idx + i
        print(f"\n[{idx+1}/{start_idx + len(to_process)}] {kb_id}: {concept}")

        # 检查是否已有真实 background（跳过已增强条目）
        bg = existing_sc.get("background", "")
        if bg and not str(bg).startswith("LLMResponse") and len(str(bg)) > 50:
            print(f"  [SKIP] 已有真实background，长度={len(str(bg))}")
            continue

        # 检查是否已有 historical_period 和 answer_template
        has_hp = bool(existing_sc.get("historical_period"))
        has_at = bool(entry.get("answer_template"))
        print(f"  historical_period: {'有' if has_hp else '无'} | answer_template: {'有' if has_at else '无'}")

        if LLM_MODE == "glm" and client:
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                build_prompt(kb_id, concept, definition, existing_sc)
            ]
            raw = call_glm(client, messages)
            if raw:
                # 尝试解析 JSON
                try:
                    # 去掉可能的 markdown 代码块
                    cleaned = raw.strip()
                    if cleaned.startswith("```"):
                        lines = cleaned.split("\n")
                        cleaned = "\n".join(lines[1:-1])
                    result = json.loads(cleaned)
                    enhanced = result
                    print(f"  [GLM OK] 历史脉络: {result.get('historical_period','')[:40]}...")
                except json.JSONDecodeError as e:
                    print(f"  [JSON PARSE ERROR] {e}")
                    print(f"  Raw: {raw[:200]}")
                    enhanced = mock_enhance(kb_id, concept, definition, existing_sc)
            else:
                enhanced = mock_enhance(kb_id, concept, definition, existing_sc)
        else:
            enhanced = mock_enhance(kb_id, concept, definition, existing_sc)

        # 应用增强结果
        if enhanced.get("historical_period"):
            entry["structured_content"]["historical_period"] = enhanced["historical_period"]

        if enhanced.get("background"):
            entry["structured_content"]["background"] = enhanced["background"]

        if enhanced.get("exam_tips"):
            # 合并 exam_tips（保留现有 scoring_points/common_mistakes，追加新的）
            existing_tips = entry.get("exam_tips", {})
            if not isinstance(existing_tips, dict):
                existing_tips = {}
            new_tips = enhanced["exam_tips"]
            for key in ["scoring_points", "common_mistakes", "记忆口诀", "延伸考点"]:
                if key in new_tips and key not in existing_tips:
                    existing_tips[key] = new_tips[key]
            entry["exam_tips"] = existing_tips

        if enhanced.get("answer_template") and not entry.get("answer_template"):
            entry["answer_template"] = enhanced["answer_template"]

        # 添加跨链接
        if kb_id in CROSS_LINKS_MAP and not entry.get("cross_pack_links"):
            entry["cross_pack_links"] = CROSS_LINKS_MAP[kb_id]

        saved_count += 1
        if saved_count % save_every == 0:
            with open(KB_PATH_OUT, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"  [AUTO-SAVED] ({saved_count} 条已保存)")

        # GLM rate limit 保护（缩短间隔加快速度）
        if LLM_MODE == "glm":
            time.sleep(0.3)

    # 最终保存
    with open(KB_PATH_OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n[FINISHED] 共处理 {saved_count} 条，文件已保存到:\n  {KB_PATH_OUT}")

if __name__ == "__main__":
    main()
