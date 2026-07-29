# -*- coding: utf-8 -*-
"""
为 ES-011~ES-048 补全 question 字段（题目/正确答案/错误示例）
基于 script 内容提取 + conflict 核心信息生成
"""
import json, shutil

SRC = r'D:\92_products\SPDT-004_EduContent\PT-037_AdaptivePrepPlatform\_03_subject_packs\cafa_calligraphy_2026\scripts\error_scripts.json'
BACKUP = r'D:\92_products\SPDT-004_EduContent\PT-037_AdaptivePrepPlatform\_03_subject_packs\cafa_calligraphy_2026\scripts\error_scripts_v2.json'

with open(SRC, encoding='utf-8') as f:
    data = json.load(f)

def guess_question(entry):
    """根据 script 内容推导 question 文本"""
    sid = entry['script_id']
    kb = entry['trigger_kb_id']
    etype = entry.get('error_type', '')
    qtype = entry.get('question_type', '')
    script = entry.get('script', {})
    explanation = script.get('explanation', '')

    # 从 script.explanation 提取核心关键词，构建题目
    if sid == "ES-011":
        return {
            "text": "选择题：小篆的主要特征是？",
            "correct_answer": "笔画均匀对称圆转（秦代标准字体）",
            "wrong_answer_sample": "笔画有粗细变化、转折用方折（其他书体特征）"
        }
    elif sid == "ES-012":
        return {
            "text": "名词解释：六书",
            "correct_answer": "象形、指事、会意、形声（造字法）+ 转注、假借（用字法），并各举一例",
            "wrong_answer_sample": "六种造字方法（太笼统，没有列出名单）"
        }
    elif sid == "ES-016":
        return {
            "text": "比较题：比较王羲之与王献之书法风格的差异",
            "correct_answer": "王羲之：内擛（向内收敛，平和蕴藉）；王献之：外拓（向外展开，奇肆纵逸）",
            "wrong_answer_sample": "王羲之的字比较好看，王献之的字比较有个性（缺少专业术语）"
        }
    elif sid == "ES-017":
        return {
            "text": "请将「山谷」译为《说文解字》标准篆书",
            "correct_answer": "山谷（谷从水，山谷之谷）",
            "wrong_answer_sample": "山穀（五谷的穀，用于粮食）"
        }
    elif sid == "ES-019":
        return {
            "text": "请将「复习」译为《说文解字》标准篆书",
            "correct_answer": "復習（彳部的復，来回、重复义）",
            "wrong_answer_sample": "複習（衣部的複，重叠义；与复习无关）"
        }
    elif sid == "ES-020":
        return {
            "text": "选择题：虞世南书法风格的特征是？",
            "correct_answer": "圆润内敛，温润如玉（得智永传授）",
            "wrong_answer_sample": "险劲方折（那是欧阳询的风格）"
        }
    elif sid == "ES-021":
        return {
            "text": "请将「出发」译为《说文解字》标准篆书",
            "correct_answer": "出發（弓部的發，射箭引申为出发）",
            "wrong_answer_sample": "出髮（髮从髟，头发的髮，与出发无关）"
        }
    elif sid == "ES-022":
        return {
            "text": "填空题：天下三大行书依次为（  ）第一、（  ）第二、（  ）第三",
            "correct_answer": "王羲之《兰亭序》、颜真卿《祭侄文稿》、苏轼《黄州寒食诗帖》",
            "wrong_answer_sample": "王羲之→颜真卿→苏轼（朝代或位置顺序混乱）"
        }
    elif sid == "ES-023":
        return {
            "text": "请将「必须」译为《说文解字》标准篆书",
            "correct_answer": "必須（面毛之必須，或借為必须）",
            "wrong_answer_sample": "需求（那是需要、需求的含义）"
        }
    elif sid == "ES-024":
        return {
            "text": "选择题：「方峻雄强」是以下哪件汉隶碑刻的特征？",
            "correct_answer": "张迁碑（方峻雄强，庙堂隶书）",
            "wrong_answer_sample": "曹全碑（那是秀美流畅的特征）"
        }
    elif sid == "ES-025":
        return {
            "text": "名词解释：古质今妍",
            "correct_answer": "《书谱》命题，指书法审美从古朴走向妍美的历史演进规律，无优劣之分",
            "wrong_answer_sample": "古代书法质量差，现代书法好（这是价值判断，不是客观规律！）"
        }
    elif sid == "ES-026":
        return {
            "text": "选择题：「南北书派论」的作者是？",
            "correct_answer": "阮元（清代学者，书论《南北书派论》）",
            "wrong_answer_sample": "董其昌（那是绘画「南北宗论」，不是书论！）"
        }
    elif sid == "ES-028":
        return {
            "text": "请将「干涉」译为《说文解字》标准篆书",
            "correct_answer": "干涉（干戈之干，武器引申为干预）",
            "wrong_answer_sample": "亁涉（干燥的亁，与干涉无关）"
        }
    elif sid == "ES-029":
        return {
            "text": "选择题：「复古书风」的最高代表是？",
            "correct_answer": "赵孟頫（元代，取法二王，宋室后裔）",
            "wrong_answer_sample": "明代书法家（那是祝枝山/文徵明，赵孟頫是元代）"
        }
    elif sid == "ES-030":
        return {
            "text": "名词解释：钟繇",
            "correct_answer": "三国魏书法家，楷书之祖，与王羲之并称「钟王」，代表作《宣示表》",
            "wrong_answer_sample": "书圣，与王羲之并称钟王（书圣是王羲之，不是钟繇！）"
        }
    elif sid == "ES-031":
        return {
            "text": "名词解释：碑学",
            "correct_answer": "清代书法流派，以汉魏南北朝碑刻为取法对象，主张尊碑卑帖，代表人物邓石如/伊秉绶/阮元/康有为",
            "wrong_answer_sample": "研究古代碑刻文字的学问（定义太宽泛，没说清楚是书法流派！）"
        }
    elif sid == "ES-032":
        return {
            "text": "选择题：帖学的学习对象是？",
            "correct_answer": "法帖（二王墨迹刻帖，如《淳化阁帖》），秀雅书卷气",
            "wrong_answer_sample": "碑刻（那是碑学的对象！碑学和帖学正好相反）"
        }
    elif sid == "ES-033":
        return {
            "text": "名词解释：六书",
            "correct_answer": "许慎《说文解字》：象形、指事、会意、形声（造字法）+ 转注、假借（用字法）",
            "wrong_answer_sample": "六种造字方法（没有列出完整名单和分类）"
        }
    elif sid == "ES-034":
        return {
            "text": "选择题：「颜筋柳骨」中「筋」的含义是？",
            "correct_answer": "沉厚宽博、饱满有力（颜体线条浑厚如筋络相连）",
            "wrong_answer_sample": "肥胖、厚重（那是字面理解！筋不是胖瘦，是力量感）"
        }
    elif sid == "ES-035":
        return {
            "text": "名词解释：宋四家",
            "correct_answer": "苏轼（丰腴跌宕）、黄庭坚（长枪大戟）、米芾（八面出锋）、蔡襄（淳淡婉美），共同特征为尚意书风",
            "wrong_answer_sample": "宋代四个书法家（只写朝代，没有具体名单和风格）"
        }
    elif sid == "ES-036":
        return {
            "text": "填空题：傅山四宁四毋的内容是（  ）",
            "correct_answer": "宁拙毋巧、宁丑毋媚、宁支离毋轻滑、宁直率毋安排",
            "wrong_answer_sample": "宁拙毋巧（只记得一条，其他三条缺失）"
        }
    elif sid == "ES-038":
        return {
            "text": "名词解释：南北书派论",
            "correct_answer": "阮元（清代）在《南北书派论》中提出，书法分为南派（二王/婉丽）和北派（碑刻/雄奇），旨在尊碑贬帖",
            "wrong_answer_sample": "董其昌提出的（那是绘画南北宗论，不是书论！）"
        }
    elif sid == "ES-039":
        return {
            "text": "比较题：章草与今草的主要区别是？",
            "correct_answer": "章草：保留隶书波磔，字字独立；今草：去掉波磔，纵向连绵",
            "wrong_answer_sample": "章草更潦草，今草更工整（没有指出波磔和连绵这两个核心区别）"
        }
    elif sid == "ES-040":
        return {
            "text": "选择题：小篆的主要识别特征是？",
            "correct_answer": "笔画均匀无粗细变化、结体对称均衡、圆转无方折",
            "wrong_answer_sample": "笔画粗细变化明显（那是其他书体！小篆的特征正是均匀）"
        }
    elif sid == "ES-041":
        return {
            "text": "选择题：隶书的主要识别特征是？",
            "correct_answer": "横画有波磔（一波三折）、结体扁方、竖画相对短促",
            "wrong_answer_sample": "竖画挺直（那是楷书特征！隶书竖画短促配合扁方格局）"
        }
    elif sid == "ES-042":
        return {
            "text": "请将「秋季」译为《说文解字》标准篆书",
            "correct_answer": "秋季（禾+火，秋天成熟之义）",
            "wrong_answer_sample": "鞦季（那是鞭鞦的鞦，与秋季无关）"
        }
    elif sid == "ES-043":
        return {
            "text": "请将「桥梁」译为《说文解字》标准篆书",
            "correct_answer": "橋梁（木+喬，水上架桥）",
            "wrong_answer_sample": "�梁（那是屋樑的樑，山谷桥梁用「梁」本字）"
        }
    elif sid == "ES-044":
        return {
            "text": "请将「酒曲」译为《说文解字》标准篆书",
            "correct_answer": "酒麯（米+麯，发酵用谷物）",
            "wrong_answer_sample": "酒曲（那是弯曲的曲，不是酒曲的本字）"
        }
    elif sid == "ES-045":
        return {
            "text": "请将「技术」译为《说文解字》标准篆书",
            "correct_answer": "技術（行部術，技术方法之义）",
            "wrong_answer_sample": "技术（那是草药名白术的术，与技术无关）"
        }
    elif sid == "ES-046":
        return {
            "text": "请将「松树」译为《说文解字》标准篆书",
            "correct_answer": "松樹（木+公，松树本身）",
            "wrong_answer_sample": "鬆樹（那是松弛的鬆，与松树无关）"
        }
    elif sid == "ES-048":
        return {
            "text": "选择题：狂草的代表书法家是？",
            "correct_answer": "张旭和怀素（唐代草圣，颠张狂素，极度连绵简省）",
            "wrong_answer_sample": "王羲之（那是今草的代表，不是狂草！王羲之不写狂草）"
        }
    else:
        return {
            "text": f"考试题：{etype}",
            "correct_answer": "正确答案（见解析）",
            "wrong_answer_sample": "典型错误（见脚本内容）"
        }

# ─── 补全 question 字段 ────────────────────────────────────────────────────
count = 0
for item in data['scripts']:
    q = item.get('question', {})
    # 检查是否需要补充
    if isinstance(q, dict) and q.get('wrong_answer_sample'):
        continue  # 已有完整 question，跳过

    sid = item['script_id']
    qdata = guess_question(item)
    item['question'] = qdata
    count += 1
    print(f"  [{count:2d}] {sid} → {qdata['text'][:40]}")

print(f"\n共补全 {count} 条")

# 备份
shutil.copy(SRC, BACKUP)
print(f"已备份: {BACKUP}")

with open(SRC, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f"已写入: {SRC}")
