# -*- coding: utf-8 -*-
"""
墨骨山河系列电子书生成器 v2
生成 Word 格式的墨骨山河系列完整读本
python-docx 1.2.0 compatible
"""
from docx import Document
from docx.shared import Pt, Cm, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from lxml import etree


# ── 颜色 ──────────────────────────────────────────────
RED    = RGBColor(0xC0, 0x39, 0x2B)
GOLD   = RGBColor(0xB8, 0x86, 0x0B)
DARK   = RGBColor(0x1A, 0x1A, 0x2E)
MID    = RGBColor(0x2C, 0x3E, 0x50)
GRAY   = RGBColor(0x7F, 0x8C, 0x8D)
GREEN  = RGBColor(0x27, 0xAE, 0x60)
PURPLE = RGBColor(0x8E, 0x44, 0xAD)


# ── 字体工具（直接操作 XML，确保 eastAsia 字体正确）───
def _xml_font(run, ea="宋体", latin="Times New Roman", size=12, bold=False, italic=False, color=None):
    """一次性设置 run 的字体、颜色（通过 XML）"""
    rPr = run._r.get_or_add_rPr()
    # rFonts
    rFonts = rPr.find(qn('w:rFonts'))
    if rFonts is None:
        rFonts = etree.SubElement(rPr, qn('w:rFonts'))
    rFonts.set(qn('w:eastAsia'), ea)
    rFonts.set(qn('w:ascii'), latin)
    rFonts.set(qn('w:hAnsi'), latin)
    rFonts.set(qn('w:cs'), latin)
    # size
    for old in rPr.findall(qn('w:sz')): rPr.remove(old)
    sz = etree.SubElement(rPr, qn('w:sz'))
    sz.set(qn('w:val'), str(int(size * 2)))
    for old in rPr.findall(qn('w:szCs')): rPr.remove(old)
    szCs = etree.SubElement(rPr, qn('w:szCs'))
    szCs.set(qn('w:val'), str(int(size * 2)))
    # bold / italic
    if bold:
        b = etree.SubElement(rPr, qn('w:b'))
    if italic:
        i = etree.SubElement(rPr, qn('w:i'))
    # color
    if color:
        for old in rPr.findall(qn('w:color')): rPr.remove(old)
        c = etree.SubElement(rPr, qn('w:color'))
        c.set(qn('w:val'), str(color))  # RGBColor.__str__ returns hex like 'C0392B'


def _xml_para_style(para, left_cm=0, first_line_cm=None, before_pt=0, after_pt=8, align=None):
    """设置段落格式"""
    pf = para.paragraph_format
    pf.space_before = Pt(before_pt)
    pf.space_after = Pt(after_pt)
    pf.left_indent = Cm(left_cm)
    if first_line_cm:
        pf.first_line_indent = Cm(first_line_cm)
    if align:
        pf.alignment = align


# ── 便捷函数 ──────────────────────────────────────────
def run_para(p, text, ea="宋体", latin="Times New Roman", size=12,
              bold=False, italic=False, color=None, align=None):
    """添加段落并设置格式"""
    r = p.add_run(text)
    _xml_font(r, ea, latin, size, bold, italic, color)
    return r

def add_narrative(doc, text):
    p = doc.add_paragraph()
    _xml_para_style(p, after_pt=10)
    run_para(p, text, size=12, color=MID)
    return p

def add_dialogue(doc, text):
    p = doc.add_paragraph()
    _xml_para_style(p, left_cm=1.0, after_pt=4)
    run_para(p, text, ea="楷体", size=11, color=MID)
    return p

def add_h1(doc, text):
    p = doc.add_heading(text, level=1)
    for r in p.runs:
        _xml_font(r, ea="微软雅黑", latin="Arial", size=18, bold=True, color=DARK)
    return p

def add_h2(doc, text):
    p = doc.add_heading(text, level=2)
    for r in p.runs:
        _xml_font(r, ea="微软雅黑", latin="Arial", size=14, bold=True, color=DARK)
    return p

def add_rule(doc, color_hex="C0392B"):
    p = doc.add_paragraph()
    _xml_para_style(p, before_pt=4, after_pt=4)
    pPr = p._element.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'), 'single')
    bottom.set(qn('w:sz'), '12')
    bottom.set(qn('w:space'), '1')
    bottom.set(qn('w:color'), color_hex)
    pBdr.append(bottom)
    pPr.append(pBdr)
    return p

def add_knowledge_tag(doc, text):
    p = doc.add_paragraph()
    _xml_para_style(p, left_cm=0.5, before_pt=4, after_pt=4)
    r1 = p.add_run("▌ ")
    _xml_font(r1, size=11, color=PURPLE)
    r2 = p.add_run(text)
    _xml_font(r2, size=11, bold=True, color=PURPLE)
    return p

def add_label_line(doc, label, text, label_color, body_color=MID):
    p = doc.add_paragraph()
    _xml_para_style(p, left_cm=0.3, after_pt=5)
    r1 = p.add_run(f"【{label}】")
    _xml_font(r1, size=11, bold=True, color=label_color)
    r2 = p.add_run(text)
    _xml_font(r2, size=11, color=body_color)
    return p

def add_bullet(doc, text, left_cm=0.8, size=11, color=MID):
    p = doc.add_paragraph(style="List Bullet")
    _xml_para_style(p, left_cm=left_cm, after_pt=3)
    r = p.add_run(text)
    _xml_font(r, size=size, color=color)
    return p

def add_number(doc, text, size=11, color=MID):
    p = doc.add_paragraph(style="List Number")
    _xml_para_style(p, left_cm=0.8, after_pt=3)
    r = p.add_run(text)
    _xml_font(r, size=size, color=color)
    return p

def add_qa(doc, question, options, answer, answer_label=""):
    add_rule(doc, "BDC3C7")
    p = doc.add_paragraph()
    _xml_para_style(p, before_pt=6, after_pt=4)
    r1 = p.add_run("【章节测验】")
    _xml_font(r1, size=11, bold=True, color=RED)
    r2 = p.add_run(question)
    _xml_font(r2, size=11, color=DARK)
    for opt in options:
        add_bullet(doc, opt, left_cm=1.0, size=11)
    p_ans = doc.add_paragraph()
    _xml_para_style(p_ans, left_cm=0.5, after_pt=6)
    label = answer_label if answer_label else "参考答案"
    r = p_ans.add_run(f"{label}：{answer}")
    _xml_font(r, size=11, bold=True, color=GREEN)
    return p_ans


# ══════════════════════════════════════════════════════
#  封面
# ══════════════════════════════════════════════════════
def build_cover(doc):
    for _ in range(3):
        doc.add_paragraph()

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _xml_para_style(p, after_pt=16)
    r = p.add_run("墨 骨 山 河")
    _xml_font(r, ea="微软雅黑", size=44, bold=True, color=DARK)

    p2 = doc.add_paragraph()
    p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _xml_para_style(p2, after_pt=24)
    r2 = p2.add_run("书法史沉浸式备考微剧本系列")
    _xml_font(r2, size=18, color=MID)

    add_rule(doc, "C0392B")

    p3 = doc.add_paragraph()
    p3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _xml_para_style(p3, before_pt=20, after_pt=8)
    r3 = p3.add_run("电子书读本 · 备考版")
    _xml_font(r3, size=14, color=GRAY)

    info = [
        ("配置包", "cafa_calligraphy_2026"),
        ("框架版本", "三层结构 V2（时间线 + 艺术问题 + 当代回响）"),
        ("覆盖时代", "先秦 → 汉 → 魏晋 → 唐 → 宋 → 清"),
        ("收录集数", "全8集 · 本册收录 Ep01/03/06"),
        ("生成日期", "2026-07-14"),
    ]
    for label, value in info:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        _xml_para_style(p, after_pt=4)
        r1 = p.add_run(f"{label}：")
        _xml_font(r1, size=11, color=GRAY)
        r2 = p.add_run(value)
        _xml_font(r2, size=11, color=MID)

    doc.add_page_break()


# ══════════════════════════════════════════════════════
#  系列导言
# ══════════════════════════════════════════════════════
def build_introduction(doc):
    add_h1(doc, "系列导言")
    add_rule(doc, "1A1A2E")

    intro = (
        "《墨骨山河》是一部以书法史为经、王朝兴衰为纬、缝合历史·地理·政治·书法四大学科内核的沉浸式备考微剧本系列。\n\n"
        "本系列以「三层结构」为骨架：\n"
        "① 时间线：前221年（秦）→ 100年（汉）→ 353年（魏晋）→ 687年（唐）→ 1082年（宋）→ 1790年代（清）\n"
        "② 艺术问题：每一集追问一个核心艺术命题\n"
        "③ 当代回响：每一集结尾，叩问「我们今天为什么还在学他们」\n\n"
        "本电子书为「阅读版」，适合学生在互动剧本之前预习使用。每集包含：时代背景、艺术问题、核心戏剧、考点标注、参考答案、章节测验。"
    )
    p = doc.add_paragraph()
    _xml_para_style(p, after_pt=12)
    r = p.add_run(intro)
    _xml_font(r, size=12, color=MID)

    add_h2(doc, "系列时间轴总览")

    timeline = [
        ("Ep01", "前219年", "峄山碑", "李斯", "小篆·书同文"),
        ("Ep02", "100—121年", "说文解字", "许慎", "六书之学"),
        ("Ep03", "353年", "兰亭序", "王羲之", "书写自觉"),
        ("Ep04", "687年", "书谱", "孙过庭", "理论自觉"),
        ("Ep05", "725—755年", "颠张醉素", "张旭·怀素", "表现极限"),
        ("Ep06", "758年", "祭侄文稿", "颜真卿", "技法与情感"),
        ("Ep07", "1082年", "黄州寒食帖", "苏轼", "意对法的突围"),
        ("Ep08", "1790—1888年", "碑学中兴", "阮元·康有为", "取法视野拓展"),
    ]

    tbl = doc.add_table(rows=1, cols=5)
    tbl.style = "Table Grid"
    hdr = tbl.rows[0].cells
    for i, h in enumerate(["集数", "年份", "代表作", "核心人物", "艺术维度"]):
        hdr[i].text = h
        r = hdr[i].paragraphs[0].runs[0]
        _xml_font(r, ea="微软雅黑", size=10, bold=True,
                  color=RGBColor(0xFF, 0xFF, 0xFF))
        # 表头底色
        tc = hdr[i]._tc
        tcPr = tc.get_or_add_tcPr()
        shd = OxmlElement('w:shd')
        shd.set(qn('w:val'), 'clear')
        shd.set(qn('w:color'), 'auto')
        shd.set(qn('w:fill'), '1A1A2E')
        tcPr.append(shd)

    for ep, yr, work, person, art in timeline:
        row = tbl.add_row().cells
        row[0].text = ep
        row[1].text = yr
        row[2].text = work
        row[3].text = person
        row[4].text = art
        for cell in row:
            for r in cell.paragraphs[0].runs:
                _xml_font(r, size=9.5, color=MID)

    doc.add_page_break()


# ══════════════════════════════════════════════════════
#  单集生成
# ══════════════════════════════════════════════════════
def build_episode(doc, ep):
    # 集标题
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _xml_para_style(p, before_pt=8, after_pt=4)
    r = p.add_run(f"第 {ep['ep_num']} 集")
    _xml_font(r, size=13, bold=True, color=RED)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _xml_para_style(p, after_pt=4)
    r = p.add_run(ep["title"])
    _xml_font(r, ea="微软雅黑", size=32, bold=True, color=DARK)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _xml_para_style(p, after_pt=6)
    r = p.add_run(ep["subtitle"])
    _xml_font(r, size=14, color=MID)

    add_rule(doc, "C0392B")

    # 时代背景
    add_h2(doc, "时代背景")
    add_label_line(doc, "年代", ep["period"], RED)
    add_label_line(doc, "艺术核心问题", ep["art_question"], GOLD, DARK)

    p = doc.add_paragraph()
    _xml_para_style(p, left_cm=0.3, after_pt=10)
    r1 = p.add_run("【艺术洞察】")
    _xml_font(r1, size=11, bold=True, color=GOLD)
    r2 = p.add_run(ep["art_insight"])
    _xml_font(r2, size=11, italic=True, color=GOLD)

    for item in ep["timeline"]:
        add_bullet(doc, item)

    # Act 1
    add_h2(doc, f"Act 1 · {ep['acts'][0]['act_title']}")
    for beat in ep["acts"][0]["beats"]:
        if beat["type"] == "narrative":
            add_narrative(doc, beat["content"])
        elif beat["type"] == "dialogue":
            for line in beat["content"].split("\n"):
                if line.strip():
                    add_dialogue(doc, line.strip())
        elif beat["type"] == "knowledge_check":
            add_qa(doc, beat["question"], beat.get("options", []), beat.get("answer", ""))

    # Act 2
    add_h2(doc, f"Act 2 · {ep['acts'][1]['act_title']}")
    for beat in ep["acts"][1]["beats"]:
        if beat["type"] == "narrative":
            add_narrative(doc, beat["content"])
        elif beat["type"] == "dialogue":
            for line in beat["content"].split("\n"):
                if line.strip():
                    add_dialogue(doc, line.strip())
        elif beat["type"] == "knowledge_check":
            add_qa(doc, beat["question"], beat.get("options", []), beat.get("answer", ""))

    # Act 3
    add_h2(doc, f"Act 3 · {ep['acts'][2]['act_title']}")
    for beat in ep["acts"][2]["beats"]:
        if beat["type"] == "narrative":
            add_narrative(doc, beat["content"])
        elif beat["type"] == "dialogue":
            for line in beat["content"].split("\n"):
                if line.strip():
                    add_dialogue(doc, line.strip())
        elif beat["type"] == "knowledge_check":
            add_qa(doc, beat["question"], beat.get("options", []), beat.get("answer", ""))

    # 当代回响
    add_h2(doc, "当代回响")

    p = doc.add_paragraph()
    _xml_para_style(p, after_pt=8)
    r1 = p.add_run("【核心叩问】")
    _xml_font(r1, size=12, bold=True, color=GREEN)
    r2 = p.add_run(ep["contemporary_question"])
    _xml_font(r2, size=12, color=GREEN)

    p = doc.add_paragraph()
    _xml_para_style(p, after_pt=8)
    r1 = p.add_run("【文化基因】")
    _xml_font(r1, size=11, bold=True, color=GREEN)
    r2 = p.add_run(ep["cultural_genome"])
    _xml_font(r2, size=11, color=GREEN)

    p = doc.add_paragraph()
    _xml_para_style(p, after_pt=4)
    r1 = p.add_run("【思考题】")
    _xml_font(r1, size=11, bold=True, color=GREEN)
    r2 = p.add_run("（无标准答案，旨在引发思考）")
    _xml_font(r2, size=10, color=GRAY)
    for q in ep["reflection_questions"]:
        add_number(doc, q)

    # 考点索引
    add_h2(doc, "本章考点索引")
    for pt, freq in ep["exam_points"]:
        add_knowledge_tag(doc, f"{pt}　考频：{freq}")

    # 关键概念
    if ep.get("concepts"):
        add_h2(doc, "关键概念速查")
        for c in ep["concepts"]:
            add_label_line(doc, c["concept"], c["definition"], PURPLE)

    add_rule(doc, "1A1A2E")
    doc.add_page_break()


# ══════════════════════════════════════════════════════
#  附录：考点总表
# ══════════════════════════════════════════════════════
def build_appendix(doc):
    add_h1(doc, "附录：本电子书覆盖考点总表")
    add_rule(doc, "1A1A2E")

    all_exam = [
        ("Ep01 李斯·峄山碑", [
            ("秦统一六国（前221年）", "★★★★★"),
            ("书同文政策", "★★★★★"),
            ("小篆三大特征（均匀/对称/圆转）", "★★★★★"),
            ("李斯与峄山刻石", "★★★★"),
            ("六书分类（象形/指事/会意/形声）", "★★★★★"),
        ]),
        ("Ep03 王羲之·兰亭序", [
            ("兰亭雅集时间：353年，永和九年", "★★★★★"),
            ("《兰亭序》天下第一行书", "★★★★★"),
            ("书圣王羲之（唐太宗确立）", "★★★★"),
            ("永字八法（侧勒努趯策掠啄磔）", "★★★★★"),
            ("之字七变", "★★★★"),
            ("魏晋风度与门阀政治", "★★★★"),
        ]),
        ("Ep06 颜真卿·祭侄文稿", [
            ("天下第二行书《祭侄文稿》", "★★★★★"),
            ("篆籀气（圆厚凝重/中锋行笔）", "★★★★★"),
            ("颜筋柳骨", "★★★★"),
            ("安史之乱与颜家牺牲", "★★★"),
            ("三大行书排序", "★★★★"),
        ]),
    ]

    for ep_title, points in all_exam:
        p = doc.add_paragraph()
        _xml_para_style(p, before_pt=10, after_pt=4)
        r = p.add_run(ep_title)
        _xml_font(r, ea="微软雅黑", size=12, bold=True, color=RED)

        tbl = doc.add_table(rows=1, cols=3)
        tbl.style = "Table Grid"
        hdr = tbl.rows[0].cells
        for i, h in enumerate(["考点", "考频", "状态"]):
            hdr[i].text = h
            r = hdr[i].paragraphs[0].runs[0]
            _xml_font(r, ea="微软雅黑", size=10, bold=True, color=RGBColor(0xFF,0xFF,0xFF))
            tc = hdr[i]._tc
            tcPr = tc.get_or_add_tcPr()
            shd = OxmlElement('w:shd')
            shd.set(qn('w:val'), 'clear')
            shd.set(qn('w:color'), 'auto')
            shd.set(qn('w:fill'), '2C3E50')
            tcPr.append(shd)
        for pt, freq in points:
            row = tbl.add_row().cells
            row[0].text = pt
            row[1].text = freq
            row[2].text = "★ 已覆盖"
            for cell in row:
                for r in cell.paragraphs[0].runs:
                    _xml_font(r, size=10, color=MID)


# ══════════════════════════════════════════════════════
#  主数据
# ══════════════════════════════════════════════════════
EP01 = {
    "ep_num": "01", "title": "峄山碑", "subtitle": "李斯 · 小篆与书同文",
    "period": "秦始皇二十八年（前219年）",
    "art_question": "当书法被国家征用为政治工具时，它自身的技术可能性被拓展了吗？",
    "art_insight": "标准化≠艺术的敌人。小篆在被赋予政治使命的同时，也在形式上达到了某种极致——对称、均匀、不可增删。这不是艺术的死亡，而是书法在特定历史条件下的一种极致形态。",
    "timeline": [
        "前221年：秦灭六国，建立中国历史上第一个中央集权王朝",
        "书同文：废除六国原有文字，以小篆为标准字体",
        "李斯时任丞相，主持文字统一工作",
        "峄山刻石是现存最早的小篆纪功刻石之一",
        "隶书在秦末汉初逐渐流行，与小篆并存"
    ],
    "concepts": [
        {"concept": "小篆", "definition": "笔画均匀圆润，横平竖直，结体严谨对称，具有极强的秩序感。代表：峄山碑、泰山刻石。"},
        {"concept": "书同文", "definition": "秦始皇统一全国文字的政策，以小篆为标准字体，消除六国文字差异。"},
        {"concept": "六书", "definition": "汉字造字的六种方法：象形、指事、会意、形声、转注、假借。"},
    ],
    "acts": [
        {
            "act_title": "秦王的难题",
            "beats": [
                {"type": "narrative", "content": "前221年，秦王嬴政完成了中国历史上最不可思议的事——消灭六个国家，第一次将广袤土地置于同一个君主的统治之下。但这只是开始。\n\n六国的'马'字有七种写法，'车'字有六种形态。政令从咸阳到齐国故地，若当地人不识秦字，诏令便是一纸空文。"},
                {"type": "dialogue", "content": "秦王：六国平了，但六国的'马'字写法各异——怎么统一这些字？\n\n李斯：大王，当废六国异文，以秦篆为标准，天下字同形，此为书同文。"},
                {"type": "knowledge_check",
                 "question": "【连线题】请将秦代统一措施与其意义连线：\nA. 统一度量衡　① 消除货币差异　B. 统一货币　② 消除长度差异　C. 统一车轨　③ 消除文字差异　D. 书同文　④ 消除交通差异",
                 "options": [],
                 "answer": "A-② B-① C-④ D-③（统一度量衡→长度标准；统一货币→消除货币差异；统一车轨→交通标准；书同文→文字统一）"},
                {"type": "narrative",
                 "content": "峄山碑前，李斯亲笔书写，将秦篆的标准形态永久刻入石头。两千二百年后，人们仍能清晰辨认这些字迹——它们几乎是完美的。\n\n完美。这是李斯追求的目标。\n\n这里有一个悖论：正是这种不允许有任何'个人风格'的完美，使得李斯的形式美成了一种独特的美——它不是个人情感的表达，而是人类理性对秩序的追求，在笔墨上的极致呈现。"}
            ]
        },
        {
            "act_title": "峄山碑",
            "beats": [
                {"type": "narrative",
                 "content": "峄山碑立在峄山之巅。李斯写下第一个字——'皇'。\n\n笔画：横、横、横、撇、捺。\n\n五个笔画，每一个都必须精确到毫厘。\n\n横画必须绝对水平——因为这是'皇'，皇在上天之下，横平则天下平。\n\n撇捺必须绝对对称——因为这是'皇'，皇是天下之首，左右均则天地正。\n\n这不是写字。这是立法。"},
                {"type": "knowledge_check",
                 "question": "【选择题】以下哪一项描述最能体现小篆的形式美特征？",
                 "options": ["A. 笔画有粗细变化，字形扁平（隶书特征）", "B. 笔画粗细均匀，横平竖直，结体严谨对称（小篆特征）", "C. 笔画简洁流畅，牵丝引带（行草特征）", "D. 笔画苍茫老辣，金石气十足（碑学特征）"],
                 "answer": "B"},
                {"type": "narrative",
                 "content": "【六书分类】请判断以下四字的六书分类：\n1. '日'（象太阳之形）→象形\n2. '上'（指事符号）→指事（纯符号，无实义部件）\n3. '休'（人倚木旁）→会意（两个实义部件）\n4. '江'（水+工）→形声（'工'是声符）\n\n最易混淆处：'上'是指事，'休'是会意，'江'是形声。"}
            ]
        },
        {
            "act_title": "千年之后",
            "beats": [
                {"type": "narrative",
                 "content": "画面从峄山之巅收回，回到现代。\n\n你坐在书桌前，面前是《峄山碑》的字帖，旁边是历史课本。窗外是键盘敲击的声音。现在的人不需要写毛笔字了，更不需要学峄山碑上的小篆。\n\n那么——你为什么要学它？"},
                {"type": "knowledge_check",
                 "question": "【综合题】请结合秦代'书同文'的历史背景，分析小篆的形式特征及其对后世书法发展的影响。（答题要点：前221年秦统一、书同文政策、小篆三大特征：均匀/对称/圆转、影响与局限）",
                 "options": [],
                 "answer": "要点：①背景（前221年）；②形式特征（均匀/对称/圆转）；③影响（奠定汉字统一基础）；④局限（强制废除六国文字）。"},
                {"type": "narrative",
                 "content": "【当代回响】没有书同文，汉字会不会像古埃及文字一样走向消亡？今天用键盘打字，简体字统一了——这和秦代'书同文'有什么相同和不同？\n\n峄山碑已经在峄山上立了两千二百多年。它上面的小篆字形，今天仍然能被大多数人认出来——这本身就是一个小小的奇迹。"}
            ]
        }
    ],
    "contemporary_question": "今天我们用键盘打字，汉字还在——李斯和小篆的统一之功，值不值得被记住？",
    "cultural_genome": "规范是自由的前提。没有文字的统一，就没有文化的持续传承；没有共同的书写的底座，后来的艺术表达就是无根之木。",
    "reflection_questions": [
        "统一是限制了可能性，还是保全了可能性？",
        "今天我们在写书法时，用的是繁体字。为什么没有书法家用简体字写出一幅'伟大'的作品？",
        "如果李斯来到今天，看到所有人用键盘打字，他会怎么想？"
    ],
    "exam_points": [
        ("秦统一六国（前221年）", "★★★★★"),
        ("书同文政策", "★★★★★"),
        ("小篆三大特征（均匀/对称/圆转）", "★★★★★"),
        ("李斯与峄山刻石", "★★★★"),
        ("六书分类判断（象形/指事/会意/形声）", "★★★★★"),
        ("书法美的多元性（秩序美）", "★★★"),
    ]
}

EP03 = {
    "ep_num": "03", "title": "兰亭序", "subtitle": "王羲之 · 永和九年",
    "period": "东晋穆帝永和九年（353年）",
    "art_question": "六书给了汉字名字（许慎），小篆建立了字体规范（李斯）——但书写本身，能不能成为自由的出口？",
    "art_insight": "王羲之是中国书法史上第一个真正意义上的'书法自觉'时刻。他不是在写字，不是在完成政治任务，他是在'书法'。他把书法从'技能'变成了'艺术'。《兰亭序》之所以是天下第一行书，不仅因为技巧，更因为它在一个特殊时刻，把一个特定的人对生命的态度，凝固在了笔墨里。",
    "timeline": [
        "265年：西晋建立，短暂统一",
        "316年：永嘉之乱，西晋亡，北方士族南渡",
        "317年：东晋建立，定都建康（南京），门阀政治开始",
        "353年：永和九年，王羲之邀41位名士雅集于兰亭，即兴书写《兰亭序》",
        "361年：王羲之去世；《兰亭序》真迹被唐太宗殉葬，今存唐人摹本"
    ],
    "concepts": [
        {"concept": "天下第一行书", "definition": "《兰亭序》被称为'天下第一行书'，由唐太宗亲题。三个极致：技法精湛（永字八法）、情感真诚（生死之叹）、审美超越（自然之美）。"},
        {"concept": "永字八法", "definition": "以'永'字概括楷书八种基本笔法：侧（点）、勒（横）、努（竖）、趯（钩）、策（提）、掠（撇）、啄（短撇）、磔（捺）。"},
        {"concept": "魏晋风度", "definition": "门阀政治高压→个体觉醒→艺术自觉。魏晋名士以诗文书法为性情表达，代表了中国文人精神的重要转向。"},
        {"concept": "行书", "definition": "介于楷书和草书之间，兼具可读性和流畅性。魏晋成熟，王羲之是行书成熟的标志性人物。"},
    ],
    "acts": [
        {
            "act_title": "永和九年",
            "beats": [
                {"type": "narrative",
                 "content": "永和九年，三月三日，上巳节。\n\n会稽山阴的兰亭，溪水清澈，惠风和畅。\n\n王羲之坐在溪边，看着四十一人的队伍蜿蜒入座。他已经命人准备好了四十七壶酒。酒壶从上游放入溪水，顺流而下。壶停在谁的面前，谁就饮酒赋诗。\n\n这是东晋名士最风雅的游戏——曲水流觞。"},
                {"type": "narrative",
                 "content": "东晋的门阀政治让真正的人才难以出头。王羲之有济世之志，但只能在山水和书法中寄托情怀。353年的兰亭雅集，是他在这种境遇下，对生命意义的一次集体追问。"},
                {"type": "dialogue",
                 "content": "王羲之看着眼前的名士们——谢安、孙绰、王凝之、王徽之……\n\n他心想：'这世道，哪里还有我们这帮人的位置？'\n\n他选择了书法和山水。每个人都有自己的出路。但今天，他们在兰亭相聚。"},
                {"type": "knowledge_check",
                 "question": "【连线题】请将以下人物与其在兰亭雅集中的角色连线：\nA. 王羲之　① 写了《兰亭后序》\nB. 谢安　② 书写《兰亭序》，主持雅集\nC. 孙绰　③ 王羲之之子，'雪夜访戴'的主人公\nD. 王徽之　④ 雅集参与者中最年长者",
                 "options": [],
                 "answer": "A-② B-④ C-① D-③"}
            ]
        },
        {
            "act_title": "天下第一行书",
            "beats": [
                {"type": "narrative",
                 "content": "王羲之展开蚕茧纸，提起鼠须笔，落笔：\n\n'永和九年，岁在癸丑，暮春之初，会于会稽山阴之兰亭，修禊事也。'\n\n第一句刚落笔，他心中便有一种预感——\n\n这篇文章，和这些字，他会写出这一生最好的。"},
                {"type": "narrative",
                 "content": "他写到中间，停下来，看着纸上的字——\n\n在这篇三百二十四字的《兰亭序》里，'之'字出现了七次。每一个'之'字都不一样。\n\n第一个'之'，笔画紧凑，像一只收拢翅膀的鸟。\n\n第二个'之'，笔画舒展，像一只展开翅膀准备起飞的鸟。\n\n第三个'之'，笔画飞动，像一只正在天空盘旋的鸟。\n\n……\n\n七只鸟，七种姿态，没有一只是重复的。"},
                {"type": "knowledge_check",
                 "question": "【永字八法·连线题】以下笔画与永字八法名称配对：\n① 一（横画）→ a. 侧（点）\n② 丶（点）→ b. 勒（横）\n③ 亅（竖画）→ c. 努（竖）\n④ 𠃌（钩）→ d. 趯（钩）\n⑤ ㇀（提）→ e. 策（提）\n⑥ 丿（长撇）→ f. 掠（撇）\n⑦ 丷（短撇）→ g. 啄（短撇）\n⑧ 磔（捺）→ h. 磔（捺）",
                 "options": [],
                 "answer": "①-b ②-a ③-c ④-d ⑤-e ⑥-f ⑦-g ⑧-h"},
                {"type": "knowledge_check",
                 "question": "【判断正误】\n① 王羲之被后世尊为'书圣'，其书法地位由唐太宗亲自确立\n② 《兰亭序》是行书，被公认为'天下第一行书'\n③ 永字八法是王羲之自己总结的笔法体系\n④ '之'字七变说明同一笔画可以有完全不同的表现形态\n⑤ 王羲之的书法成就与魏晋门阀政治无关",
                 "options": [],
                 "answer": "①○ ②○ ③✗（永字八法是唐代书法理论系统化归纳） ④○ ⑤✗（魏晋风度是时代产物）"},
                {"type": "narrative",
                 "content": "王羲之写到全文最关键的一段：\n\n'夫人之相与，俯仰一世。或取诸怀抱，悟言一室之内；或因寄所托，放浪形骸之外。虽趣舍万殊，静躁不同，当其欣于所遇，暂得于己，快然自足，不知老之将至。'\n\n他写到'不知老之将至'时，笔触突然慢了下来——他真正懂了这句话的意思。"}
            ]
        },
        {
            "act_title": "书写之后",
            "beats": [
                {"type": "narrative",
                 "content": "王羲之写完最后一个字——'文'，放下笔。\n\n他知道，这篇序之所以好，不是因为他想写好——而是因为他根本没有'想'。\n\n后来他又写了几十遍，都不如第一稿——因为第一稿是在酒精和情绪的催化下写成的，最自然，最真实。"},
                {"type": "knowledge_check",
                 "question": "【综合题】请分析《兰亭序》为何能成为'天下第一行书'，并论述魏晋风度对中国书法艺术自觉的贡献。（答题要点：353年兰亭雅集、行书成熟标志、之字七变、魏晋门阀政治与个体觉醒、技法与情感统一）",
                 "options": [],
                 "answer": "要点：①背景（353年，门阀政治）；②艺术特征（行书成熟，之字七变，永字八法完整运用）；③魏晋风度（政治高压→个体觉醒→艺术自觉）；④情感（生死之叹，真诚流露）。"},
                {"type": "narrative",
                 "content": "【当代回响】\n一千七百年过去了。王羲之的'之'字，已经被无数人临摹过。\n\n但每一代人临出来的'之'字，都带着那一代人自己的理解。\n\n'后之视今，亦犹今之视昔。'——王羲之写这句话的时候，他一定想过，一千七百年后，还有人在临摹这些字。"}
            ]
        }
    ],
    "contemporary_question": "《兰亭序》被唐太宗殉葬，真迹已失——但一千七百年后，我们还在临摹它。我们到底在临摹什么？",
    "cultural_genome": "《兰亭序》之所以永恒，不是因为它是'书法范本'，而是因为它说出了人类面对时间流逝时的共同感受——'后之视今，亦犹今之视昔'。这种感受不因时代而异。",
    "reflection_questions": [
        "摹本能替代真迹吗？我们临的，到底是'字'还是'精神'？",
        "王羲之的'自由'建立在什么基础之上？是彻底抛弃规则，还是把规则内化之后忘记了规则？",
        "之字七变告诉我们：同一个笔画可以有完全不同的形态。这是不是意味着——没有'唯一正确的写法'？"
    ],
    "exam_points": [
        ("兰亭雅集时间：353年，永和九年", "★★★★★"),
        ("《兰亭序》天下第一行书", "★★★★★"),
        ("书圣王羲之，地位由唐太宗确立", "★★★★"),
        ("《兰亭序》真迹殉葬昭陵，现存唐摹本", "★★★★"),
        ("永字八法：侧勒努趯策掠啄磔", "★★★★★"),
        ("之字七变：同一笔画的不同表现形态", "★★★★"),
        ("魏晋风度与门阀政治", "★★★★"),
        ("行书成熟于魏晋", "★★★"),
    ]
}

EP06 = {
    "ep_num": "06", "title": "祭侄文稿", "subtitle": "颜真卿 · 安史之乱",
    "period": "唐肃宗乾元元年（758年）",
    "art_question": "张旭的答案是'技法消失，情感涌现'。颜真卿的答案是：技法的极致，和情感的极致，同时存在、相互激荡。悲痛没有让他失控，反而让他的技法达到了从未有过的高度。",
    "art_insight": "《祭侄文稿》之所以是天下第二行书，不是因为'悲痛'本身，而是因为颜真卿在最悲痛的时刻，做了一件违反直觉的事：他没有失控，而是让悲痛穿过了他的技法，让技法承载了悲痛。这是书法史上最有力的证据，证明极端情感和极致技艺可以并存。",
    "timeline": [
        "709年：颜真卿生于京兆万年（今陕西西安）",
        "755年：安禄山叛乱，安史之乱爆发",
        "756年：颜杲卿起兵抵抗，城破后骂贼三日，被害",
        "757年：颜季明（颜杲卿之子）被杀，头颅被悬于城门",
        "758年：颜真卿寻回侄子颜季明遗骸，写下《祭侄文稿》",
        "785年：颜真卿被叛将李希烈缢杀，谥号'文忠'"
    ],
    "concepts": [
        {"concept": "天下第二行书", "definition": "《祭侄文稿》与《兰亭序》《黄州寒食诗帖》并称'天下三大行书'。三种极致：规范之美（兰亭）、悲痛之美（祭侄）、旷达之美（寒食）。"},
        {"concept": "篆籀气", "definition": "颜体书法的重要特征：笔画圆厚凝重、中锋行笔、藏而不露。视觉特征：涨墨、绞转、迟涩。"},
        {"concept": "颜筋柳骨", "definition": "唐代楷书两大流派：颜真卿（筋——丰肥圆厚、筋骨内含）和柳公权（骨——瘦硬挺拔、骨骼分明）。"},
        {"concept": "屋漏痕", "definition": "颜真卿提出的笔法意象：笔画如同雨水在墙上流下留下的痕迹，自然、厚重、有力，强调笔画的'重量感'和'时间感'。"},
    ],
    "acts": [
        {
            "act_title": "安史之乱",
            "beats": [
                {"type": "narrative",
                 "content": "乾元元年，蒲州。\n\n颜真卿面前放着两样东西：\n\n一是他侄子颜季明的头骨。\n\n二是他亲手写下的祭文草稿。\n\n两年前，安禄山叛乱，堂兄颜杲卿起兵抵抗，城破后骂贼三日，被割舌断手而死。侄子颜季明被杀，头颅被悬于城门之上。\n\n颜真卿终于找到侄子的遗骸时——只剩一颗头颅。"},
                {"type": "dialogue",
                 "content": "颜真卿提起笔。\n\n他的手在抖。\n\n不是因为紧张，而是因为悲伤。\n\n悲伤入骨，唯有笔墨能盛此痛。"},
                {"type": "knowledge_check",
                 "question": "【连线题】请将以下人物与其在安史之乱中的结局连线：\nA. 颜杲卿　① 被杀，头颅悬于城门\nB. 颜季明　② 起兵抵抗，城破骂贼三日，被害\nC. 颜真卿　③ 寻回侄子遗骸，写《祭侄文稿》",
                 "options": [],
                 "answer": "A-② B-① C-③"}
            ]
        },
        {
            "act_title": "悲痛与笔墨",
            "beats": [
                {"type": "narrative",
                 "content": "颜真卿落笔：\n\n'维乾元元年，岁次戊戌，九月庚午，朔三日壬申，第十三叔银青光禄大夫使持节蒲州诸军事蒲州刺史……祭于亡侄赠赞善大夫季明之灵位。'\n\n他写得很快——不是因为他想快，而是因为他不能慢。慢下来，悲伤就会变成理智。理智，就会修饰。一修饰，就假了。"},
                {"type": "narrative",
                 "content": "写到中间，墨色突然变了——\n\n笔画变粗了，墨汁涨开，在纸上形成了一团深色的墨迹。\n\n这就是《祭侄文稿》里著名的'涨墨'。\n\n这不是失误。这是悲痛太过激烈，笔的控制力在那一刻完全失控——但这种失控，恰好记录了那一刻的真实状态。\n\n再往后，笔画开始绞转、迟涩，像是被什么重物压着一样艰难前行。"},
                {"type": "knowledge_check",
                 "question": "【三大行书连线题】\nA. 兰亭序　① 苏轼　a. 天下第一行书\nB. 祭侄文稿　② 王羲之　b. 天下第二行书\nC. 黄州寒食诗帖　③ 颜真卿　c. 天下第三行书",
                 "options": [],
                 "answer": "A-②-a B-③-b C-①-c"},
                {"type": "knowledge_check",
                 "question": "【判断正误】\n① 《祭侄文稿》被称为'天下第二行书'，是颜真卿最著名的行书作品\n② '颜筋柳骨'指的是颜真卿的楷书和柳公权的行书\n③ '篆籀气'是颜体书法的重要特征，表现为笔画圆厚、中锋行笔\n④ 颜真卿是唐代忠臣，后被叛将李希烈缢杀，谥号'文忠'",
                 "options": [],
                 "answer": "①○ ②✗（颜筋柳骨指两人的楷书） ③○ ④○"}
            ]
        },
        {
            "act_title": "悲痛的意义",
            "beats": [
                {"type": "narrative",
                 "content": "《祭侄文稿》的价值证明了：极端情感和极致技艺不是对立的。\n\n在最极端的时刻，人往往能达到最高的技艺状态。\n\n这种状态，在体育比赛、艺术创作、演讲中都有体现。"},
                {"type": "knowledge_check",
                 "question": "【综合题】请分析《祭侄文稿》为何能成为'天下第二行书'，并论述篆籀气在颜体书法中的表现。（答题要点：758年，安史之乱，颜季明牺牲；涨墨、绞转、迟涩；篆籀气：圆厚凝重、中锋行笔、藏而不露）",
                 "options": [],
                 "answer": "要点：①背景（758年，安史之乱，颜季明牺牲）；②艺术特征（涨墨是悲痛激烈的失控记录，绞转和迟涩是心理外化）；③篆籀气（笔画圆厚凝重、中锋行笔、藏而不露）；④情感价值（技法与情感的极致融合）。"},
                {"type": "narrative",
                 "content": "【当代回响】\n《祭侄文稿》写于极度悲痛中，但它没有失控——反而达到了最高水平。\n\n这说明什么？\n\n真正的悲痛，可以激发最高的技艺——这是艺术创作中'情感与技法辩证关系'的经典案例。"}
            ]
        }
    ],
    "contemporary_question": "《祭侄文稿》被那么多人推崇，只是因为它悲痛吗？还是说，它证明了：真正的悲痛，可以激发最高的技艺？",
    "cultural_genome": "《祭侄文稿》告诉我们：极端情感和极致技艺不是对立的——在最极端的时刻，人往往能达到最高的技艺状态。这种状态，在体育比赛、艺术创作、演讲中都有体现。",
    "reflection_questions": [
        "你有没有过类似经历：在极端情绪下，反而做成了平时做不好的事？",
        "'技法'和'情感'，到底哪个更重要？还是说，它们根本不是对立的关系？",
        "《祭侄文稿》和《兰亭序》都是'天下第一'级别的作品——但它们的情感状态完全不同。技法相通的两个人，可以有完全不同的情感表达吗？"
    ],
    "exam_points": [
        ("天下第二行书《祭侄文稿》（颜真卿）", "★★★★★"),
        ("篆籀气：圆厚凝重、中锋行笔", "★★★★★"),
        ("颜筋柳骨", "★★★★"),
        ("安史之乱与颜家牺牲", "★★★"),
        ("屋漏痕笔法意象", "★★★"),
        ("三大行书排序", "★★★★"),
    ]
}


# ══════════════════════════════════════════════════════
#  主程序
# ══════════════════════════════════════════════════════
OUTPUT_PATH = (
    r"C:\Users\willi\Desktop\我的视野\0713-基于知识库的高阶备考智能体"
    r"\02-设计文档\配置包_cafa_calligraphy_2026\scripts\墨骨山河_电子书.docx"
)

def main():
    doc = Document()
    section = doc.sections[0]
    section.page_width  = Cm(21)
    section.page_height = Cm(29.7)
    section.left_margin   = Cm(2.5)
    section.right_margin  = Cm(2.5)
    section.top_margin    = Cm(2.5)
    section.bottom_margin = Cm(2.5)
    section.footer_distance = Cm(1.0)

    doc.styles["Normal"].font.name = "宋体"
    doc.styles["Normal"].font.size = Pt(12)

    build_cover(doc)
    build_introduction(doc)

    for ep_data in [EP01, EP03, EP06]:
        build_episode(doc, ep_data)

    build_appendix(doc)

    # 页脚
    footer = section.footer
    fp = footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    fr = fp.add_run("墨骨山河 · 书法史沉浸式备考微剧本系列 · 备考读本")
    _xml_font(fr, size=9, color=GRAY)

    doc.save(OUTPUT_PATH)
    print(f"[OK] Ebook generated: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
