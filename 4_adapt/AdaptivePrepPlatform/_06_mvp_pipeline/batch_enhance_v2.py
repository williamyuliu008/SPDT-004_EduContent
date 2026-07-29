# -*- coding: utf-8 -*-
"""
批量增强 kb_vocab.json 中的 KB_CAFA_S* 条目
用法: python batch_enhance_v2.py [start_idx] [count]
"""
import json, sys, os, time
from pathlib import Path

PT_ROOT = Path(__file__).parent.parent
KB_IN  = PT_ROOT / "_03_subject_packs" / "cafa_calligraphy_2026" / "knowledge" / "kb_vocab.json"
KB_OUT = PT_ROOT / "_03_subject_packs" / "cafa_calligraphy_2026" / "knowledge" / "kb_vocab_enhanced.json"

API_KEY = None
API_KEY_PATH = Path("D:/_CEO/bulletin/SECRET_KEY/zhipu_api.txt")
if API_KEY_PATH.exists():
    API_KEY = API_KEY_PATH.read_text(encoding="utf-8").strip()
    os.environ["ZHIPU_API_KEY"] = API_KEY

LLM_MODE = "glm" if API_KEY else "mock"

# ── S010 手动精品内容 ────────────────────────────────────────────────────────
S010_HP = "353年(东晋永和九年)至1082年(北宋元丰五年)，横跨近八百年。第一高峰:王羲之《兰亭序》(353年)，确立行书审美典范。第二高峰:颜真卿《祭侄文稿》(758年)，行书与家国情感融合。第三高峰:苏轼《黄州寒食诗帖》(1082年)，尚意书风之旗帜。"
S010_BG = (
    "【第一·兰亭序】东晋永和九年(353)三月，王羲之与友人谢安、孙绰等四十二人雅集兰亭，临流赋诗。"
    "酒酣兴浓之际，羲之挥毫作序，凡二十八行，三百二十四字。通篇用笔精到，一气呵成。"
    "之字出现二十余次，笔笔姿态不同。唐太宗李世民极度推崇，亲笔摹写，原作随葬昭陵。历代书法家奉为天下第一行书。\n\n"
    "【第二·祭侄文稿】乾元元年(758)，颜真卿侄子颜季明于安史之乱殉国。"
    "两年后寻得遗骸仅头颅一具，悲愤交加之际，颜真卿写下此文稿。"
    "全篇涂改三十余处，焦墨枯笔，情感喷薄，屋漏痕笔法自然流露。"
    "后世评为天下第二行书，誉为无意于书，而书自工。\n\n"
    "【第三·黄州寒食诗帖】元丰三年苏轼因乌台诗案被贬黄州，处境困厄。"
    "元丰五年寒食节，天雨不绝，诗人独处破屋，作寒食二首，后亲笔书写。"
    "全篇笔力沉厚，结体开张，黄庭坚跋曰此书兼颜鲁公、杨少师、李西台笔意。\n\n"
    "【三者共性】皆为书写者人生巅峰状态的情感宣泄之作；情感驱动技法；"
    "既是书法经典，也是历史文献；共同构建中国行书审美坐标系。\n\n"
    "【应试提示】王羲之晚年面临五胡乱华，颜真卿满门忠烈最终殉国，苏轼九死一生贬谪黄州。"
    "这种家国之大悲正是三大行书诞生的情感土壤，也是国美考试的高频深挖点。"
)

S010_TIPS = {
    "scoring_points": [
        "三件作品名称、作者、朝代全写（3分）",
        "第一/二/三位置严格对应，不得颠倒（2分）",
        "苏轼朝代：北宋；颜真卿朝代：唐代；王羲之朝代：东晋（1分）",
        "1-2句艺术特点描述（2分）",
        "说明天下第X行书称号来源（1分）"
    ],
    "common_mistakes": [
        "致命：苏轼写成唐代人（错！苏轼是北宋）直接扣3分",
        "致命：顺序颠倒至少扣2分",
        "常见：只写《兰亭序》一件作品，只得1-2分",
        "细节：颜真卿写成颜真或遗漏真卿全名"
    ],
    "记忆口诀": [
        "位置口诀：兰亭祭侄寒食诗，一二三分清楚",
        "朝代口诀：羲之东晋真卿唐，东坡北宋不能忘",
        "情感线索：兰亭雅集真卿悲，苏轼寒食独自醉"
    ],
    "延伸考点": [
        "为何《祭侄文稿》涂改很多却更珍贵？（考情感真实性与技法自然性）",
        "苏轼为何是尚意书风代表？（考宋代书法美学转型）",
        "王羲之书圣地位如何确立？（考后世接受史）",
        "若选第四大行书选谁？（怀素《自叙帖》、杨凝式《韭花帖》）"
    ]
}

S010_AT = (
    "一、名词界定（1句）\n"
    "中国书法史上公认的成就最高的三件行书作品，被誉为天下三大行书。\n\n"
    "二、三件作品（每个写2-3句）\n"
    "第一：王羲之《兰亭序》\n"
    "- 王羲之（字逸少），东晋书法家，有书圣之誉\n"
    "- 永和九年（353年）三月三日，雅集兰亭，临流赋诗，为诗集作序\n"
    "- 艺术特点：用笔精到，之字二十余变；结构秀美，章法疏朗\n"
    "- 地位：天下第一行书，确立行书审美典范\n\n"
    "第二：颜真卿《祭侄文稿》\n"
    "- 颜真卿（字清臣），唐代书法家，楷书四大家之一\n"
    "- 乾元元年（758）为殉国侄子颜季明所作祭文\n"
    "- 艺术特点：涂改自然，焦墨枯笔，屋漏痕笔法，忠愤溢于笔端\n"
    "- 地位：天下第二行书，行书与家国情怀融合之典范\n\n"
    "第三：苏轼《黄州寒食诗帖》\n"
    "- 苏轼（字子瞻，号东坡），北宋文学家、书法家\n"
    "- 元丰五年（1082）被贬黄州后所作寒食诗并亲笔书写\n"
    "- 艺术特点：笔力沉厚，结体开张；尚意书风代表\n"
    "- 地位：天下第三行书，宋代尚意书风之旗帜\n\n"
    "三、总结（1句）\n"
    "三者分别代表东晋风流、唐代忠烈、宋代意韵，构成中国行书最高坐标。\n\n"
    "【失分警示】顺序颠倒扣2分；苏轼朝代写成唐代直接扣3分；只写一件作品最多得2分。"
)

S010_LINKS = [
    {"kb_id": "KB_CAFA_S005", "title": "颜真卿", "pack_id": "cafa_calligraphy_2026", "note": "天下第二行书作者，需与本文综合备考"},
    {"kb_id": "KB_CAFA_S001", "title": "宋四家", "pack_id": "cafa_calligraphy_2026", "note": "苏轼是宋四家之一，整体框架结合记忆"},
    {"kb_id": "KB_CAFA_S002", "title": "王羲之", "pack_id": "cafa_calligraphy_2026", "note": "书圣，天下第一行书作者"},
    {"kb_id": "KB_CAFA_S013", "title": "尚意书风", "pack_id": "cafa_calligraphy_2026", "note": "宋代书法美学，苏轼是尚意提出者"}
]

def get_client():
    if LLM_MODE != "glm":
        return None
    try:
        from openai import OpenAI
        return OpenAI(api_key=API_KEY, base_url="https://open.bigmodel.cn/api/paas/v4/")
    except Exception:
        return None

SYSTEM = (
    "你是中国美术学院书法史论考试专家。请为备考知识库生成JSON格式的增强内容。"
    "只需输出JSON，不要任何其他文字。"
)

def call_glm(client, kb_id, concept, sc_str):
    content = (
        f'KB: {kb_id} | 名词: {concept} | 现有: {sc_str}\n\n'
        '按以下JSON格式输出（全部内容用单行，不要换行符）：'
        '{"hp":"时代背景简述","bg":"100-200字背景，分3段用[SEP]分隔","tips":{"sp":["要点1","要点2"],"err":["错误1"],"mn":["口诀1"],"ext":["考点1"]},"at":"答题模板80字内"}'
    )
    try:
        resp = client.chat.completions.create(
            model="glm-4-flash",
            messages=[
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": content}
            ],
            temperature=0.3,
            timeout=30.0
        )
        raw = resp.choices[0].message.content.strip()
        if raw.startswith("```"):
            lines = raw.split("\n")
            raw = "\n".join(lines[1:-1])
        result = json.loads(raw)
        # Convert short keys to full names
        return {
            "historical_period": result.get("hp", ""),
            "background": result.get("bg", "").replace("[SEP]", "\n\n"),
            "exam_tips": {
                "scoring_points": result.get("tips", {}).get("sp", []),
                "common_mistakes": result.get("tips", {}).get("err", []),
                "记忆口诀": result.get("tips", {}).get("mn", []),
                "延伸考点": result.get("tips", {}).get("ext", [])
            },
            "answer_template": result.get("at", "")
        }
    except Exception as e:
        print(f"  [ERR] {e}")
        return None

def mock_gen(kb_id, concept):
    return {
        "historical_period": f"{concept}相关历史时期",
        "background": f"【背景】{concept}需要补充详细历史背景和艺术分析（需启用GLM）",
        "exam_tips": {"scoring_points": [f"{concept}的定义和历史地位"], "common_mistakes": ["与其他概念混淆"], "记忆口诀": [], "延伸考点": []},
        "answer_template": f"{concept}是书法史上重要概念...\n\n【答题框架】\n1. 定义\n2. 历史背景\n3. 艺术特点\n4. 地位影响"
    }

def main():
    start_idx = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    max_count = int(sys.argv[2]) if len(sys.argv) > 2 else 9999

    with open(KB_OUT, "r", encoding="utf-8") as f:
        data = json.load(f)
    print(f"[INFO] Loaded from existing enhanced file: {KB_OUT}")

    all_entries = []
    for mod_data in data["modules"].values():
        for items in mod_data.values():
            for item in items:
                if item.get("kb_id", "").startswith("KB_CAFA_S"):
                    all_entries.append(item)

    total = len(all_entries)
    to_process = all_entries[start_idx:start_idx + max_count]
    print(f"[total={total}] processing index {start_idx} ~ {start_idx + len(to_process) - 1}, mode={LLM_MODE}")

    client = get_client()
    done = 0

    for i, entry in enumerate(to_process):
        kb_id = entry.get("kb_id", "")
        concept = entry.get("concept", "")
        sc = entry.get("structured_content", {})

        idx = start_idx + i
        print(f"[{idx+1}/{start_idx + len(to_process)}] {kb_id}: {concept}")

        # S010 special case
        if kb_id == "KB_CAFA_S010":
            sc["historical_period"] = S010_HP
            sc["background"] = S010_BG
            entry["exam_tips"] = S010_TIPS
            entry["answer_template"] = S010_AT
            entry["cross_pack_links"] = S010_LINKS
            print("  [MANUAL S010 APPLIED]")
        else:
            # Skip if already has real background
            bg = sc.get("background", "")
            if bg and not str(bg).startswith("LLMResponse") and len(str(bg)) > 50:
                print(f"  [SKIP] has real background len={len(str(bg))}")
                continue

            sc_str = json.dumps(sc, ensure_ascii=False)
            result = None
            if client:
                result = call_glm(client, kb_id, concept, sc_str)
                if result:
                    print(f"  [GLM OK] hp={str(result.get('historical_period',''))[:30]}...")
                else:
                    print("  [GLM FAIL] using mock")
                    result = mock_gen(kb_id, concept)
            else:
                result = mock_gen(kb_id, concept)

            if result.get("historical_period"):
                sc["historical_period"] = result["historical_period"]
            if result.get("background"):
                sc["background"] = result["background"]
            tips_new = result.get("exam_tips", {})
            if isinstance(tips_new, dict):
                existing = entry.get("exam_tips", {})
                if isinstance(existing, dict):
                    for k, v in tips_new.items():
                        if k not in existing:
                            existing[k] = v
                else:
                    entry["exam_tips"] = tips_new
            if result.get("answer_template") and not entry.get("answer_template"):
                entry["answer_template"] = result["answer_template"]

        done += 1
        if done % 5 == 0:
            with open(KB_OUT, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"  [SAVED] {done} entries processed")

        if LLM_MODE == "glm":
            time.sleep(0.3)

    with open(KB_OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\n[DONE] {done} entries saved to {KB_OUT}")

if __name__ == "__main__":
    main()
