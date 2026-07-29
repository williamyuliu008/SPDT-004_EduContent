# -*- coding: utf-8 -*-
"""
革与鼎 · 中国古代史卷二 电子书生成器
"""
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from lxml import etree
import os, importlib

BASE = (r"C:\Users\willi\Desktop\我的视野\0713-基于知识库的高阶备考智能体"
        r"\02-设计文档\古史_v2_变与局\scripts")
MD_OUT  = os.path.join(BASE, "变与局_电子书.md")
DOCX_OUT = os.path.join(BASE, "变与局_电子书.docx")

RED    = RGBColor(0x1B, 0x4F, 0x3E)
GOLD   = RGBColor(0xB8, 0x86, 0x0B)
DARK   = RGBColor(0x1A, 0x1A, 0x2E)
MID    = RGBColor(0x2C, 0x3E, 0x50)
GRAY   = RGBColor(0x7F, 0x8C, 0x8D)
GREEN  = RGBColor(0x27, 0xAE, 0x60)
BLUE   = RGBColor(0x1B, 0x4F, 0x3E)
PURPLE = RGBColor(0x8E, 0x44, 0xAD)
TEAL   = RGBColor(0x00, 0x7B, 0x83)


def xf(run, ea="宋体", latin="Times New Roman", size=12,
        bold=False, italic=False, color=None):
    rPr = run._r.get_or_add_rPr()
    rF = rPr.find(qn('w:rFonts'))
    if rF is None: rF = etree.SubElement(rPr, qn('w:rFonts'))
    rF.set(qn('w:eastAsia'), ea)
    rF.set(qn('w:ascii'), latin)
    rF.set(qn('w:hAnsi'), latin)
    rF.set(qn('w:cs'), latin)
    for x in list(rPr.findall(qn('w:sz'))): rPr.remove(x)
    sz = etree.SubElement(rPr, qn('w:sz')); sz.set(qn('w:val'), str(int(size*2)))
    if bold:   etree.SubElement(rPr, qn('w:b'))
    if italic: etree.SubElement(rPr, qn('w:i'))
    if color:
        for x in list(rPr.findall(qn('w:color'))): rPr.remove(x)
        c = etree.SubElement(rPr, qn('w:color'))
        c.set(qn('w:val'), str(color))

def xf_para(para, before=0, after=8, left=0, align=None):
    pf = para.paragraph_format
    pf.space_before = Pt(before); pf.space_after = Pt(after)
    pf.left_indent = Cm(left)
    if align: pf.alignment = align

def add_rule(doc, color_hex="1B4F3E"):
    p = doc.add_paragraph()
    xf_para(p, before=6, after=6)
    pPr = p._element.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    bot = OxmlElement('w:bottom'); bot.set(qn('w:val'), 'single')
    bot.set(qn('w:sz'), '12'); bot.set(qn('w:space'), '1')
    bot.set(qn('w:color'), color_hex)
    pBdr.append(bot); pPr.append(pBdr)
    return p

def p_docx(doc, text, ea="宋体", size=12, bold=False, italic=False,
            color=None, before=0, after=8, left=0, align=None):
    p = doc.add_paragraph()
    xf_para(p, before, after, left, align)
    if text:
        r = p.add_run(text)
        xf(r, ea, size=size, bold=bold, italic=italic, color=color)
    return p

def h_docx(doc, text, level=1, color=None):
    p = doc.add_heading(text, level=level)
    for r in p.runs:
        ea = "微软雅黑" if level <= 2 else "宋体"
        sz = 20 if level == 1 else (14 if level == 2 else 12)
        xf(r, ea=ea, size=sz, bold=True, color=color or DARK)
    return p

def table_header_row(tbl, headers, fill="1A1A2E"):
    row = tbl.rows[0].cells
    for i, h in enumerate(headers):
        row[i].text = h
        r = row[i].paragraphs[0].runs[0]
        xf(r, ea="微软雅黑", size=10, bold=True,
           color=RGBColor(0xFF,0xFF,0xFF))
        tc = row[i]._tc; tcPr = tc.get_or_add_tcPr()
        shd = OxmlElement('w:shd')
        shd.set(qn('w:val'),'clear'); shd.set(qn('w:color'),'auto')
        shd.set(qn('w:fill'), fill); tcPr.append(shd)

def table_row(tbl, cells, size=10, color=None):
    row = tbl.add_row().cells
    for i, txt in enumerate(cells):
        row[i].text = txt
        for r in row[i].paragraphs[0].runs:
            xf(r, size=size, color=color or MID)


class AncientHistoryV2Renderer:
    def __init__(self):
        self.docx = Document()
        self.md_lines = []
        s = self.docx.sections[0]
        s.page_width = Cm(21); s.page_height = Cm(29.7)
        s.left_margin = s.right_margin = Cm(2.5)
        s.top_margin = s.bottom_margin = Cm(2.5)
        self.docx.styles["Normal"].font.name = "宋体"
        self.docx.styles["Normal"].font.size = Pt(12)

    def cover(self, title_s, title_m, subtitle, meta_lines):
        for _ in range(4): self.docx.add_paragraph()
        p_docx(self.docx, title_s, ea="微软雅黑", size=52, bold=True,
                color=DARK, align=WD_ALIGN_PARAGRAPH.CENTER, after=20)
        if title_m:
            p_docx(self.docx, title_m, ea="宋体", size=18, color=BLUE,
                    align=WD_ALIGN_PARAGRAPH.CENTER, after=12)
        p_docx(self.docx, subtitle, size=18, color=MID,
                align=WD_ALIGN_PARAGRAPH.CENTER, after=20)
        add_rule(self.docx, "1B4F3E")
        for lb, val in meta_lines:
            p_docx(self.docx, f"{lb}：{val}", size=11, color=GRAY,
                    align=WD_ALIGN_PARAGRAPH.CENTER, after=4)
        self.docx.add_page_break()
        self.md_lines.clear()
        self.md_lines.append(f"# {title_s}\n\n")
        if title_m: self.md_lines.append(f"*{title_m}*\n\n")
        self.md_lines.append(f"*{subtitle}*\n\n")
        self.md_lines.append("| 项目 | 内容 |\n|---|---|\n")
        for lb, val in meta_lines:
            self.md_lines.append(f"| {lb} | {val} |\n")
        self.md_lines.append("\n---\n\n")

    def frontmatter(self, title, sections):
        add_rule(self.docx, "1B4F3E")
        h_docx(self.docx, title, 1, RED)
        add_rule(self.docx, "1A1A2E")
        for sec in sections:
            if sec["type"] == "h2":
                h_docx(self.docx, sec["text"], 2, DARK)
            elif sec["type"] == "p":
                p_docx(self.docx, sec["text"], size=12, color=MID, after=10)
            elif sec["type"] == "quote":
                p_docx(self.docx, sec["text"], ea="楷体", size=12, color=GOLD,
                        italic=True, left=1.0, after=6)
        self.docx.add_page_break()
        self.md_lines.append(f"\n# {title}\n\n")
        for sec in sections:
            if sec["type"] == "h2":
                self.md_lines.append(f"\n## {sec['text']}\n\n")
            elif sec["type"] == "p":
                self.md_lines.append(f"{sec['text']}\n\n")
            elif sec["type"] == "quote":
                self.md_lines.append(f"> *{sec['text']}*\n\n")

    def chapter(self, num, title, subtitle, hist_q, hist_insight,
                timeline, acts, ending_text):
        p_docx(self.docx, f"第 {num} 集", size=13, bold=True, color=RED,
                align=WD_ALIGN_PARAGRAPH.CENTER, before=12, after=4)
        p_docx(self.docx, title, ea="微软雅黑", size=34, bold=True,
                color=DARK, align=WD_ALIGN_PARAGRAPH.CENTER, after=6)
        p_docx(self.docx, subtitle, size=13, color=TEAL,
                align=WD_ALIGN_PARAGRAPH.CENTER, after=6)
        p_docx(self.docx, f"◆ {hist_q}", size=12, bold=True, color=GOLD,
                before=8, after=6)
        add_rule(self.docx, "1B4F3E")
        h_docx(self.docx, "时代背景", 2, DARK)
        for item in timeline:
            p_docx(self.docx, f"• {item}", size=11, color=MID, after=3, left=0.5)
        for act in acts:
            h_docx(self.docx, f"Act {act['num']} · {act['title']}", 2, DARK)
            if act.get("intro"):
                p_docx(self.docx, act["intro"], size=12, color=MID,
                        italic=True, before=0, after=8)
            for para in act["paragraphs"]:
                if para["type"] == "narrative":
                    p_docx(self.docx, para["text"], size=12, color=MID, after=10)
                elif para["type"] == "dialogue":
                    for line in para["text"].split("\n"):
                        if line.strip():
                            p_docx(self.docx, line.strip(), ea="楷体", size=11,
                                    color=TEAL, left=1.0, after=4)
                elif para["type"] == "highlight":
                    p_docx(self.docx, para["text"], ea="楷体", size=12,
                            color=GOLD, italic=True, left=0.5, after=8)
                elif para["type"] == "quote":
                    p_docx(self.docx, para["text"], ea="楷体", size=12,
                            color=GOLD, italic=True, left=1.5, after=8)
        if ending_text:
            add_rule(self.docx, "1B4F3E")
            p_docx(self.docx, ending_text, size=12, color=DARK,
                    italic=True, before=6, after=6)
        self.docx.add_page_break()
        self.md_lines.append(f"\n# 第 {num} 集 · {title}\n\n*{subtitle}*\n\n")
        self.md_lines.append(f"> **历史核心问题**：{hist_q}\n\n")
        self.md_lines.append(f"> *{hist_insight}*\n\n")
        self.md_lines.append("## 时代背景\n\n")
        for item in timeline:
            self.md_lines.append(f"- {item}\n")
        for act in acts:
            self.md_lines.append(f"\n### Act {act['num']} · {act['title']}\n\n")
            if act.get("intro"):
                self.md_lines.append(f"*{act['intro']}*\n\n")
            for para in act["paragraphs"]:
                if para["type"] == "narrative":
                    self.md_lines.append(f"{para['text']}\n\n")
                elif para["type"] == "dialogue":
                    lines = para["text"].split("\n")
                    self.md_lines.append("> " + "\n> ".join(l for l in lines if l.strip()) + "\n\n")
                elif para["type"] == "highlight":
                    self.md_lines.append(f"> *{para['text']}*\n\n")
                elif para["type"] == "quote":
                    self.md_lines.append(f"> {para['text']}\n\n")
        if ending_text:
            self.md_lines.append(f"\n---\n\n{ending_text}\n\n")

    def appendix(self, chapters_qa, exam_points, concepts):
        add_rule(self.docx, "1B4F3E")
        h_docx(self.docx, "附录", 1, RED)
        add_rule(self.docx, "1A1A2E")
        h_docx(self.docx, "一、各章章节测验", 2, DARK)
        for ch in chapters_qa:
            p_docx(self.docx, ch["title"], ea="微软雅黑", size=12,
                    bold=True, color=RED, before=8, after=4)
            for item in ch["items"]:
                p_docx(self.docx, item["q"], size=11, bold=True, color=DARK,
                        left=0.3, after=3)
                for opt in item.get("options", []):
                    p_docx(self.docx, opt, size=11, color=MID, left=1.0, after=2)
                p_docx(self.docx, f"→ {item['a']}", size=11, color=GREEN,
                        bold=True, left=0.5, after=6)
        h_docx(self.docx, "二、高频考点总表", 2, DARK)
        tbl = self.docx.add_table(rows=1, cols=3)
        tbl.style = "Table Grid"
        table_header_row(tbl, ["集数·专题", "考点", "考频"])
        for ch_title, points in exam_points:
            p_docx(self.docx, ch_title, ea="微软雅黑", size=11,
                    bold=True, color=RED, before=8, after=4)
            for pt, freq in points:
                table_row(tbl, ["", pt, freq], 10, MID)
        h_docx(self.docx, "三、关键概念速查", 2, DARK)
        for term, definition in concepts:
            p_docx(self.docx, f"【{term}】", size=11, bold=True,
                    color=PURPLE, left=0.3, after=2)
            p_docx(self.docx, definition, size=11, color=MID, after=6, left=0.5)
        self.md_lines.append("\n# 附录\n\n")
        self.md_lines.append("## 一、各章章节测验\n\n")
        for ch in chapters_qa:
            self.md_lines.append(f"### {ch['title']}\n\n")
            for item in ch["items"]:
                self.md_lines.append(f"**{item['q']}**\n\n")
                for opt in item.get("options", []):
                    self.md_lines.append(f"- {opt}\n")
                self.md_lines.append(f"→ *{item['a']}*\n\n")
        self.md_lines.append("\n## 二、高频考点总表\n\n")
        self.md_lines.append("| 集数·专题 | 考点 | 考频 |\n|---|---|---|\n")
        for ch_title, points in exam_points:
            self.md_lines.append(f"**{ch_title}** |\n")
            for pt, freq in points:
                self.md_lines.append(f"| | {pt} | {freq} |\n")
        self.md_lines.append("\n## 三、关键概念速查\n\n")
        for term, definition in concepts:
            self.md_lines.append(f"**【{term}】** {definition}\n\n")

    def save(self):
        s = self.docx.sections[0]
        fp = s.footer.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        fr = fp.add_run("变与局 · 中国古代史卷二 · 高考备考读本")
        xf(fr, size=9, color=GRAY)
        self.docx.save(DOCX_OUT)
        with open(MD_OUT, "w", encoding="utf-8") as f:
            f.writelines(self.md_lines)
        return DOCX_OUT, MD_OUT


# ── 内容数据 ────────────────────────────────────────

def build_preface():
    return [
        {"type": "h2", "text": "一、为什么读这套书"},
        {"type": "p", "text": (
            "历史不是用来背的。历史是用来理解的。\n\n"
            "很多人学历史的方法是：记年代、记事件、记意义。背了忘，忘了背，考完就扔。\n\n"
            "《变与局》想做的事，是把历史变回它本来该有的样子——"
            "它是一连串选择，一连串因果，一连串人在特定时刻做的特定决定。\n\n"
            "每一个历史事件的背后，都有一个活生生的人，站在十字路口，"
            "做了一个当时看来'合理'的选择，然后这个选择，"
            "在几十年、几百年后，产生了谁也没想到的后果。\n\n"
            "理解了这个'为什么'，历史就活了。"
        )},
        {"type": "h2", "text": "二、这套书的结构"},
        {"type": "p", "text": (
            "卷二的主题是'制度困局'——从北宋建立到鸦片战争，六集，每一集讲一个关键时刻：\n\n"
            "Ep01 宋的困局：重文抑武，为什么文化最繁荣，军事最弱？\n"
            "Ep02 王安石变法：政府要不要深度介入经济？\n"
            "Ep03 靖康之变：一场外交失误，还是结构性的崩溃？\n"
            "Ep04 蒙古帝国：草原部落，如何变成一个帝国？\n"
            "Ep05 明初制度：绝对集权，是解决方案还是新问题？\n"
            "Ep06 晚清变局：鸦片战争深层原因是什么？\n\n"
            "每一集不是按照朝代顺序流水账——而是围绕一个核心历史问题，"
            "用微剧本的形式，把你放到那个时刻，看那个人如何做决定。"
        )},
        {"type": "h2", "text": "三、关于高考"},
        {"type": "p", "text": (
            "本书不是高考历史考点的简单汇编。\n\n"
            "但它比任何汇编都更有助于备考——因为它让你理解考点背后的'为什么'。\n\n"
            "能讲出故事的历史知识，才记得住。记不住的历史知识，考完就忘。\n\n"
            "附录里，我们把每集的高考高频考点、关键概念和章节测验都整理好了——"
            "你可以先读正文，再翻附录检验；也可以直接用附录备考。"
        )},
        {"type": "quote", "text": "一切历史都是当代史。一切考试，都是对理解力的检验。"},
    ]

def build_epilogue():
    return [
        {"type": "h2", "text": "尾声：六次困局，一条线索"},
        {"type": "p", "text": (
            "从陈桥驿到虎门海滩，一千年。\n\n"
            "我们在这六集里，走过了另一条奇怪的路径：\n\n"
            "宋朝用重文抑武换文化繁荣——但换来了军事积弱；\n"
            "王安石用政府干预换财政改革——但换来了党争内耗；\n"
            "靖康之变打破了宋朝的北方屏障——但也催生了南宋的文化高峰；\n"
            "蒙古帝国用草原逻辑建立了横跨欧亚的大帝国——但也没能解决草原与农耕的融合问题；\n"
            "明朝用极端集权换内部稳定——但也换来了宦官专权和制度的僵化；\n"
            "清朝在封闭中维持了二百多年——但最终在工业文明的炮火下土崩瓦解。\n\n"
            "每一次制度选择，在当时看来都是'最优解'。\n"
            "每一次'最优解'，都埋下了下一代人要解决的问题。\n\n"
            "历史学的价值，不是告诉我们'正确答案是什么'——"
            "而是告诉我们：每一个时代的人，都是在信息不完全、利益很复杂、未来不确定的情况下，做出他们的选择。\n"
            "理解这一点，比记住任何一个具体的历史事件，都更重要。"
        )},
        {"type": "h2", "text": "最后的话"},
        {"type": "p", "text": (
            "中国古代史到这里就结束了。\n\n"
            "从公元前2070年的夏朝，到公元1840年的鸦片战争，"
            "四千年的历史，我们走过了两条路径——\n"
            "卷一：从分封到郡县，从百家争鸣到安史之乱；\n"
            "卷二：从重文抑武到鸦片战争，从制度困局到文明碰撞。\n\n"
            "这两条路径，有一个共同的主题：\n"
            "在每个时代，人们都在试图回答同一个问题——\n"
            "什么样的秩序，才是好的秩序？\n\n"
            "这个问题，没有终极答案。\n"
            "但它值得每一代人反复追问。\n\n"
            "谢谢你的阅读。"
        )},
        {"type": "quote", "text": "一切历史都是当代史。一切考试，都是对理解力的检验。愿你在理解历史中，找到你自己的答案。"},
    ]


def build_all_exam_points():
    return [
        ("Ep01 宋的困局", [
            ("陈桥兵变和北宋建立", "★★★"),
            ("杯酒释兵权的内容和意义", "★★★★★"),
            ("重文抑武政策的内容和影响", "★★★★★"),
            ("燕云十六州问题", "★★★★"),
            ("檀渊之盟的背景、内容、评价", "★★★★★"),
        ]),
        ("Ep02 王安石变法", [
            ("王安石变法的背景（三冗问题）", "★★★★★"),
            ("王安石变法的主要措施", "★★★★★"),
            ("王安石变法失败的原因", "★★★★★"),
            ("王安石与司马光的争论", "★★★"),
            ("对王安石变法的评价（辩证）", "★★★★★"),
        ]),
        ("Ep03 靖康之变", [
            ("靖康之变的原因（联金灭辽的失误）", "★★★★★"),
            ("北宋灭亡的深层原因", "★★★★★"),
            ("南宋偏安局面的形成", "★★★"),
            ("岳飞的历史地位", "★★★★★"),
            ("绍兴和议的内容", "★★★"),
        ]),
        ("Ep04 蒙古帝国", [
            ("成吉思汗统一蒙古和制度建设", "★★★★"),
            ("蒙古帝国的扩张", "★★★"),
            ("元朝的建立和统治特点", "★★★★"),
            ("元朝的民族等级制度", "★★★★★"),
            ("元朝的统一意义", "★★★"),
        ]),
        ("Ep05 明初制度", [
            ("明朝建立和洪武之治", "★★★"),
            ("废丞相制度的内容和影响", "★★★★★"),
            ("厂卫制度（锦衣卫、东厂）", "★★★★★"),
            ("洪武四大案", "★★★"),
            ("靖难之役", "★★★★"),
            ("明朝强化中央集权的措施", "★★★★★"),
        ]),
        ("Ep06 晚清变局", [
            ("鸦片战争的原因和《南京条约》", "★★★★★"),
            ("洋务运动", "★★★★★"),
            ("甲午战争和《马关条约》", "★★★★★"),
            ("戊戌变法", "★★★★★"),
            ("《辛丑条约》", "★★★★"),
            ("中国半殖民地半封建社会的形成", "★★★★★"),
        ]),
    ]

def build_all_concepts():
    return [
        ("重文抑武", "宋朝的基本国策：抬高文官地位，压低武官地位。目的是防止武将夺权，代价是军事能力被系统性削弱；但客观上促进了文化繁荣。"),
        ("檀渊之盟", "1004年宋辽签订的和约：宋朝每年给辽白银十万两、绢二十万匹，双方约为兄弟之国。结束了宋辽大规模战争，但使宋朝处于战略守势。"),
        ("王安石变法", "1069-1085年宋神宗支持下的全面改革：青苗法、募役法、农田水利法等。失败原因：执行变形、既得利益抵制、党争。是中国历史上最大的'政府vs市场'争论之一。"),
        ("靖康之变", "1127年金军攻破开封，俘虏宋徽宗、宋钦宗，北宋灭亡。近因是联金灭辽的外交失误，深层原因是北宋军事积弱、政治腐败。"),
        ("成吉思汗", "铁木真于1206年统一蒙古各部，被尊为成吉思汗（拥有四海的强大君主）。他创立的千户制度、怯薛军、驿站制度，奠定了蒙古帝国组织能力的基础。"),
        ("行省制度", "元朝在地方实行的行政制度，设行中书省管理地方。意义：奠定了此后中国行政区划的基础（明清沿用），是元朝最重要的制度遗产。"),
        ("废丞相", "1380年朱元璋废除丞相制度，由皇帝直接管理六部。结束了中国一千多年的丞相制度，但导致皇权极度集中，为宦官专权埋下隐患。"),
        ("靖难之役", "1399-1402年燕王朱棣反对建文帝的战争。是明朝皇室内斗的典型，证明了分封制度的失败，明成祖即位后迁都北京。"),
        ("天朝体制", "清朝的外交体系：以中国为中心的朝贡秩序，无法容纳对等的西方外交体系。是清朝无法应对鸦片战争的根本原因之一。"),
        ("南京条约", "1842年清朝与英国签订的第一个不平等条约：割让香港岛、开放五口通商、赔款2100万银元。是中国沦为半殖民地的开端。"),
        ("半殖民地半封建社会", "鸦片战争后中国社会性质的变化：政治上主权受损（半殖民地），经济上封建经济逐步解体（半封建）。这个状态持续了约110年（1840-1949）。"),
    ]

def build_all_qa():
    return [
        {
            "title": "Ep01 宋的困局 章节测验",
            "items": [
                {"q": "【名词解释】重文抑武", "options": [], "a": "宋朝的基本国策：抬高文官地位，压低武官地位，用文官主导军事。目的是防止武将夺权，代价是军事能力被系统性削弱；但客观上促进了文化繁荣（科举大兴、文人阶层崛起）。"},
                {"q": "【判断正误】① 杯酒释兵权是赵匡胤解除武将兵权的手段② 宋朝的文化繁荣与重文抑武政策无关③ 檀渊之盟使宋辽之间再无战争④ 重文抑武导致军事积弱是宋朝制度的必然结果", "options": [], "a": "①○ ②✗ ③✗ ④○"},
                {"q": "【综合题】分析重文抑武政策对宋朝的影响。", "options": [], "a": "积极影响：①促进文化繁荣（宋词、宋画、宋瓷、科技）②社会相对稳定（无大规模武将夺权）③科举制度完善，人才选拔机制优化。消极影响：①军事积弱，对辽、夏、金始终处于守势②武将地位低下，缺乏优秀军事将领③军费开支庞大，加重财政负担④形成'积弱积贫'的双重困境。"}
            ]
        },
        {
            "title": "Ep02 王安石变法 章节测验",
            "items": [
                {"q": "【名词解释】王安石变法", "options": [], "a": "1069-1085年，宋神宗支持王安石推行的全面改革：青苗法、募役法、农田水利法、市易法等。目的是解决三冗问题、增加财政收入。失败原因：执行层面问题（强行摊派）、既得利益集团抵制、新旧党争。"},
                {"q": "【填空题】王安石变法的三大目标：解决①___问题②___问题③___问题。", "options": [], "a": "①冗官 ②冗兵 ③冗费"},
                {"q": "【判断正误】①王安石变法得到了朝廷所有官员的支持②司马光完全反对变法的理念③变法失败后新法被全部废除④戊戌变法和王安石变法有相似之处", "options": [], "a": "①✗ ②✗ ③✗ ④○"},
                {"q": "【综合题】评析王安石变法的历史意义。", "options": [], "a": "积极：①首次系统性地用政府力量干预经济②客观上促进了商品经济和农业发展③提出了「资源」与「市场」的矛盾关系——「开源」与「节流」之争，反映了千古治理难题：政府应该干预还是放任？消极：①执行层面问题严重②触动既得利益，引发激烈党争③开启了北宋后期的政治内耗④部分措施在短期内加重了百姓负担。"},
            ]
        },
        {
            "title": "Ep03 靖康之变 章节测验",
            "items": [
                {"q": "【名词解释】靖康之变", "options": [], "a": "1127年，金军攻破北宋都城开封，俘虏宋徽宗、宋钦宗，北宋灭亡。这是中国历史上最惨烈的亡国事件之一，两个皇帝被俘，皇室被洗劫，大量文化财富被毁。近因是宋金联灭辽的战略失误，深层原因是北宋军事积弱、政治腐败。"},
                {"q": "【判断正误】①靖康之变完全是宋徽宗的个人失误②岳飞被害与靖康之变有间接关系③南宋偏安政策的根源是靖康之变④岳飞主张北伐迎回二帝", "options": [], "a": "①✗ ②○ ③○ ④○"},
                {"q": "【综合题】分析靖康之变的深层原因和历史影响。", "options": [], "a": "深层原因：①政治腐败（三冗问题长期未解决）②军事积弱（重文抑武导致战斗力低下）③外交失误（联金灭辽暴露军事实力）④党争内耗（朝廷精力消耗在内部斗争）。历史影响：①南宋偏安，经济重心南移完成②岳飞被害，南宋军事力量受损③理学兴起，中国文化重心转向④为蒙古崛起提供了空间。"}
            ]
        },
        {
            "title": "Ep04 蒙古帝国 章节测验",
            "items": [
                {"q": "【名词解释】行省制度", "options": [], "a": "元朝在地方实行的行政制度：设行中书省（行省）管理地方。它奠定了此后中国行政区划的基础，是元朝最重要的制度遗产，明清两代沿用并完善。"},
                {"q": "【判断正误】①成吉思汗统一蒙古各部在1206年②元朝实行四等人民族等级制度③成吉思汗的制度创新仅限于军事征服④行省制度对后世没有影响", "options": [], "a": "①○ ②○ ③✗ ④✗"},
                {"q": "【综合题】评析元朝统一的历史意义。", "options": [], "a": "积极：①结束长期分裂局面，实现全国统一②促进了民族融合（驿站制度、行省制度）③促进东西方经济文化交流（丝绸之路空前畅通）④推动了中国与世界的联系。局限：①民族等级制度造成严重社会不平等②统治者未能有效融合农耕文明③赋税和劳役沉重，激化社会矛盾。"}
            ]
        },
        {
            "title": "Ep05 明初制度 章节测验",
            "items": [
                {"q": "【名词解释】靖难之役", "options": [], "a": "1399-1402年，燕王朱棣以'清君侧'为名反对建文帝的战争。建文帝战败失踪，朱棣即位（明成祖），迁都北京。是明朝皇室内斗的典型，证明了分封制度的失败。"},
                {"q": "【填空题】明太祖朱元璋在位期间通过三大案强化皇权：①___案②___案③___案。", "options": [], "a": "①胡惟庸案 ②空印案/郭桓案 ③蓝玉案"},
                {"q": "【判断正误】①废丞相加强了皇权②锦衣卫是司法机构③靖难之役是地方藩王挑战中央的典型④明成祖迁都北京是为了加强北方防御", "options": [], "a": "①○ ②✗ ③○ ④○"},
                {"q": "【综合题】评析明朝废除丞相制度的影响。", "options": [], "a": "积极：①结束了相权与皇权的长期博弈②皇权空前强化，有利于政策统一执行③推动内阁制度形成，提高行政效率。消极：①皇帝工作负担过重②内阁首辅权力日增，形成新的权力中心③宦官借助皇权干预政治（司礼监）④缺乏有效权力制衡机制，皇帝决策失误无法纠正。"}
            ]
        },
        {
            "title": "Ep06 晚清变局 章节测验",
            "items": [
                {"q": "【名词解释】半殖民地半封建社会", "options": [], "a": "鸦片战争后，中国社会性质发生变化：政治上主权受损，被迫开放，被迫签订不平等条约（半殖民地）；经济上封建经济逐步解体，出现资本主义萌芽（半封建）。这个状态从1840年持续到1949年。"},
                {"q": "【判断正误】①鸦片战争的根本原因是鸦片贸易②《南京条约》是中国近代史第一个不平等条约③洋务运动是一次政治改革④戊戌变法失败后清朝再也没有进行过改革", "options": [], "a": "①✗ ②○ ③✗ ④✗"},
                {"q": "【综合题】评析近代中国仁人志士探索国家出路的努力（洋务运动→戊戌变法）。", "options": [], "a": "洋务运动（技术改革）：①学习西方技术，建立近代企业②客观上促进了中国近代化③但只学技术不改革制度，甲午战争证明其局限性。戊戌变法（政治改革）：①要求君主立宪，发展工商业②触动了清朝权力核心，被慈禧镇压③失败证明自上而下的改革路径在中国走不通④但其思想遗产（民主、科学）深刻影响了后世。总体规律：器物改革→制度改革的递进，改革与革命的相互替代。"}
            ]
        },
    ]


def main():
    episode_modules = [
        "古史_v2_ep01_宋的困局",
        "古史_v2_ep02_王安石变法",
        "古史_v2_ep03_靖康之变",
        "古史_v2_ep04_蒙古帝国",
        "古史_v2_ep05_明初制度",
        "古史_v2_ep06_晚清变局",
    ]
    ep_datas = []
    for mod_name in episode_modules:
        path = os.path.join(BASE, mod_name + ".py")
        spec = importlib.util.spec_from_file_location(mod_name, path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        ep_datas.append(mod.get_data())

    r = AncientHistoryV2Renderer()
    r.cover(
        title_s="变 与 局",
        title_m="中国古代史卷二",
        subtitle="从北宋建立到鸦片战争：制度困局与突围的六次尝试",
        meta_lines=[
            ("系列", "变与局"),
            ("配置包", "cafa_ancient_history_v2"),
            ("框架", "三层结构（王朝兴衰 + 历史核心问题 + 当代启示）"),
            ("收录集数", "全6集 · 完整版"),
            ("输出格式", "DOCX + Markdown 双格式"),
            ("生成日期", "2026-07-14"),
        ]
    )
    r.frontmatter("序言", build_preface())
    for ep in ep_datas:
        r.chapter(
            num=ep["episode"],
            title=ep["title"],
            subtitle=ep["subtitle"],
            hist_q=ep["historical_question"],
            hist_insight=ep["art_insight"],
            timeline=ep["timeline"],
            acts=ep["acts"],
            ending_text=ep["ending"]
        )
    r.frontmatter("尾声", build_epilogue())
    r.appendix(
        chapters_qa=build_all_qa(),
        exam_points=build_all_exam_points(),
        concepts=build_all_concepts()
    )
    docx_out, md_out = r.save()
    print(f"DOCX: {docx_out}")
    print(f"MD:   {md_out}")

if __name__ == "__main__":
    main()
