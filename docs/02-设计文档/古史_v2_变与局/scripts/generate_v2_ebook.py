# -*- coding: utf-8 -*-
"""
变与局 · 中国古代史卷二 电子书生成器 v2
卷二：变与局 · 从杯酒释兵权到辛亥革命
"""
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import os

BASE = (r"C:\Users\willi\Desktop\我的视野\0713-基于知识库的高阶备考智能体"
        r"\02-设计文档\古史_v2_变与局\scripts")
MD_OUT = os.path.join(BASE, "变与局_电子书.md")
DOCX_OUT = os.path.join(BASE, "变与局_电子书.docx")

RED    = RGBColor(0x8B, 0x00, 0x00)
GOLD   = RGBColor(0xB8, 0x86, 0x0B)
DARK   = RGBColor(0x1A, 0x1A, 0x2E)
MID    = RGBColor(0x2C, 0x3E, 0x50)
GRAY   = RGBColor(0x7F, 0x8C, 0x8D)
GREEN  = RGBColor(0x27, 0xAE, 0x60)
BLUE   = RGBColor(0x14, 0x5A, 0x9E)
PURPLE = RGBColor(0x8E, 0x44, 0xAD)


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
    if bold:
        etree.SubElement(rPr, qn('w:b'))
    if italic:
        etree.SubElement(rPr, qn('w:i'))
    if color:
        for x in list(rPr.findall(qn('w:color'))): rPr.remove(x)
        c = etree.SubElement(rPr, qn('w:color'))
        c.set(qn('w:val'), str(color))

def xf_para(para, before=0, after=8, left=0, align=None):
    pf = para.paragraph_format
    pf.space_before = Pt(before); pf.space_after = Pt(after)
    pf.left_indent = Cm(left)
    if align: pf.alignment = align

def add_rule(doc, color_hex="8B0000"):
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

from lxml import etree


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


def md_h1(lines, t): lines.append(f"\n# {t}\n\n")
def md_h2(lines, t): lines.append(f"\n## {t}\n\n")
def md_h3(lines, t): lines.append(f"\n### {t}\n\n")
def md_p(lines, t): lines.append(f"{t}\n\n")
def md_rule(lines): lines.append("\n---\n\n")
def md_bullet(lines, t): lines.append(f"- {t}\n")
def md_tag(lines, t): lines.append(f"> ▌{t}\n")
def md_quote(lines, t): lines.append(f"> *{t}*\n\n")
def md_empty(lines): lines.append("\n")


class AncientHistoryRenderer:
    def __init__(self):
        self.docx = Document()
        self.md_lines = []
        self._docx = self.docx
        s = self.docx.sections[0]
        s.page_width = Cm(21); s.page_height = Cm(29.7)
        s.left_margin = s.right_margin = Cm(2.5)
        s.top_margin = s.bottom_margin = Cm(2.5)
        self.docx.styles["Normal"].font.name = "宋体"
        self.docx.styles["Normal"].font.size = Pt(12)

    def cover(self, title_s, title_m, subtitle, meta_lines):
        self.docx.add_paragraph()
        self.docx.add_paragraph()
        self.docx.add_paragraph()
        p_docx(self.docx, title_s, ea="微软雅黑", size=52, bold=True,
                color=DARK, align=WD_ALIGN_PARAGRAPH.CENTER, after=20)
        if title_m:
            p_docx(self.docx, title_m, ea="宋体", size=18, color=BLUE,
                    align=WD_ALIGN_PARAGRAPH.CENTER, after=12)
        p_docx(self.docx, subtitle, size=18, color=MID,
                align=WD_ALIGN_PARAGRAPH.CENTER, after=20)
        add_rule(self.docx, "8B0000")
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
        add_rule(self.docx, "8B0000")
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
        # DOCX
        p_docx(self.docx, f"第 {num} 集", size=13, bold=True, color=RED,
                align=WD_ALIGN_PARAGRAPH.CENTER, before=12, after=4)
        p_docx(self.docx, title, ea="微软雅黑", size=34, bold=True,
                color=DARK, align=WD_ALIGN_PARAGRAPH.CENTER, after=6)
        p_docx(self.docx, subtitle, size=13, color=BLUE,
                align=WD_ALIGN_PARAGRAPH.CENTER, after=6)
        p_docx(self.docx, f"◆ {hist_q}", size=12, bold=True, color=GOLD,
                before=8, after=6)
        add_rule(self.docx, "8B0000")

        # 时代背景
        h_docx(self.docx, "时代背景", 2, DARK)
        for item in timeline:
            p_docx(self.docx, f"• {item}", size=11, color=MID, after=3, left=0.5)

        # Acts
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
                                    color=RGBColor(0x14,0x5A,0x9E),
                                    left=1.0, after=4)
                elif para["type"] == "highlight":
                    p_docx(self.docx, para["text"], ea="楷体", size=12,
                            color=GOLD, italic=True, left=0.5, after=8)
                elif para["type"] == "quote":
                    p_docx(self.docx, para["text"], ea="楷体", size=12,
                            color=GOLD, italic=True, left=1.5, after=8)

        if ending_text:
            add_rule(self.docx, "8B0000")
            p_docx(self.docx, ending_text, size=12, color=DARK,
                    italic=True, before=6, after=6)
        self.docx.add_page_break()

        # Markdown
        self.md_lines.append(
            f"\n# 第 {num} 集 · {title}\n\n*{subtitle}*\n\n"
        )
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
        add_rule(self.docx, "8B0000")
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


# ════════════════════════════════════════════════
#  内容
# ════════════════════════════════════════════════

def build_preface():
    return [
        {"type": "h2", "text": "一、为什么读这套书"},
        {"type": "p",
         "text": "历史不是用来背的。历史是用来理解的。\n\n很多人学历史的方法是：记年代、记事件、记意义。背了忘，忘了背，考完就扔。\n\n这不是学历史，是背书。\n\n《变与局》想做的事，是把历史变回它本来该有的样子——它是一连串选择，一连串因果，一连串人在特定时刻做的特定决定。每一个历史事件的背后，都有一个活生生的人，站在十字路口，做了一个当时看来'合理'的选择，然后这个选择，在几十年、几百年后，产生了谁也没想到的后果。\n\n理解了这个'为什么'，历史就活了。背不住的年代，自然就记住了——因为它有意义了。"},
        {"type": "h2", "text": "二、这套书的结构"},
        {"type": "p",
         "text": "卷二的主题是'变与局'——从北宋到晚清，六集，每一集讲一个关键时刻：\n\nEp01 宋的困局：重文抑武的帝国，如何在文化繁荣与军事虚弱之间摇摆？\n\nEp02 王安石变法：政府深度介入经济，是救国良方还是饮鸩止渴？\n\nEp03 靖康之变：一个文化鼎盛的王朝，为何在军事失败中走向灭亡？\n\nEp04 蒙古帝国：游牧民族如何建立中国历史上版图最大的王朝？\n\nEp05 明帝国的两难：禁海与下西洋，天朝如何在开放与封闭之间反复横跳？\n\nEp06 晚清变局：洋务运动、戊戌变法、辛亥革命——为何改革总是输给革命？\n\n每一集不是按照朝代顺序流水账——而是围绕一个核心历史问题，用微剧本的形式，把你放到那个时刻，看那个人如何做决定。"},
        {"type": "h2", "text": "三、两卷完整覆盖中国古代史"},
        {"type": "p",
         "text": "卷一《革与鼎》从先秦讲到安史之乱——封邦建国、百家争鸣、秦并天下、汉武雄图、胡汉融合、盛唐拐点。\n\n卷二《变与局》从北宋讲到晚清——宋的困局、王安石变法、靖康之变、蒙古帝国、明帝国的两难、晚清变局。\n\n两卷合在一起，完整覆盖从先秦到1911年的中国古代史。\n\n四千年的制度困局，一以贯之：\n\n每一代人都试图在前人的废墟上，建一套更好的制度。\n\n每一套更好的制度，最终都变成了新的废墟。\n\n然后，下一代人再来。"},
        {"type": "h2", "text": "四、关于高考"},
        {"type": "p",
         "text": "本书不是高考历史考点的简单汇编。\n\n但它比任何汇编都更有助于备考——因为它让你理解考点背后的'为什么'。\n\n能讲出故事的历史知识，才记得住。记不住的历史知识，考完就忘。\n\n附录里，我们把每集的高考高频考点、关键概念和章节测验都整理好了——你可以先读正文，再翻附录检验；也可以直接用附录备考。\n\n两条路都通。"},
        {"type": "quote",
         "text": "一切历史都是当代史。一切考试，都是对理解力的检验。"},
    ]


def build_epilogue():
    return [
        {"type": "h2", "text": "尾声：从改革到革命"},
        {"type": "p",
         "text": "从960年到1911年，将近一千年。\n\n我们在这六集里，走过了一条越来越绝望的路：\n\n北宋用重文抑武解决了藩镇问题，却带来了军事积弱的死局；\n\n王安石用变法试图富国强兵，新旧党争却撕裂了整个士大夫阶层；\n\n明朝用海禁防止倭寇，却催生了走私和走私背后的黑暗力量；\n\n清朝在洋务运动中'中学为体、西学为用'，结果证明体和用都出了问题；\n\n戊戌变法想走日本明治维新的路，被既得利益集团用一场政变堵死了；\n\n1911年，孙中山说：既然所有改革都失败了，那就只剩下一条路了——革命。"},
        {"type": "h2", "text": "两卷的线索"},
        {"type": "p",
         "text": "卷一《革与鼎》的主题是'制度断裂'——每一次制度创新，最终都变成了制度废墟。\n\n卷二《变与局》的主题是'制度困局'——不是没有改革，而是每一次改革，都被更大的困局吞噬。\n\n两卷合在一起，讲述的是同一个故事：\n\n中国人花了四千年，试图建一套能让自己永远稳定运转的制度。\n\n每一次尝试都失败了。\n\n每一次失败，都催生了下一次更大的尝试。\n\n直到1911年，中国人说：这套游戏规则本身，就是问题。\n\n革命，不是为了换一个皇帝。\n\n革命，是为了换一个系统。\n\n这是中国古代史留给近代史的最后一个问题。\n\n也是近代史必须回答的第一个问题。"},
        {"type": "h2", "text": "下一站"},
        {"type": "p",
         "text": "中国古代史到此结束。\n\n近代史，从1919年五四运动，到1949年新中国成立——那又是另一个故事了。\n\n但没有这两卷中国古代史，你不会理解：\n\n为什么1911年的革命者，愿意付出那么大的代价，去推翻一个延续了两千年的制度。\n\n历史学家的特权，是事后诸葛亮。但历史的当事人，没有这个特权——他们只能在那一个时刻，凭他们能看到的信息，做他们认为最好的选择。\n\n理解这一点，比记住任何一个具体的历史事件，都更重要。\n\n而历史，正在等待下一批读者。"},
    ]


def build_all_exam_points():
    return [
        ("Ep01 宋的困局", [
            ("北宋加强中央集权的措施", "★★★★★"),
            ("重文抑武政策的内容和影响", "★★★★★"),
            ("杯酒释兵权的背景和意义", "★★★★★"),
            ("澶渊之盟的背景、内容、影响", "★★★★"),
            ("北宋经济繁荣的表现（交子、商税等）", "★★★★"),
        ]),
        ("Ep02 王安石变法", [
            ("王安石变法的背景", "★★★★★"),
            ("青苗法、募役法、市易法内容及评价", "★★★★★"),
            ("王安石变法失败的原因", "★★★★★"),
            ("新旧党争的过程和影响", "★★★★★"),
            ("宋神宗和宋徽宗的历史评价", "★★★★"),
        ]),
        ("Ep03 靖康之变", [
            ("靖康之变的过程", "★★★★★"),
            ("北宋灭亡的原因", "★★★★★"),
            ("宋金关系的变化", "★★★★★"),
            ("岳飞抗金的背景和意义", "★★★★"),
            ("南宋的建立与偏安", "★★★★"),
        ]),
        ("Ep04 蒙古帝国", [
            ("成吉思汗统一蒙古的过程", "★★★★★"),
            ("蒙古扩张的阶段和结果", "★★★★★"),
            ("元朝统一的历史意义", "★★★★★"),
            ("行省制度的内容和影响", "★★★★★"),
            ("四等人制的内容和影响", "★★★★"),
        ]),
        ("Ep05 明帝国的两难", [
            ("明朝加强中央集权的措施", "★★★★★"),
            ("郑和下西洋的背景、目的、意义", "★★★★★"),
            ("土木堡之变的过程和影响", "★★★★★"),
            ("明朝海禁政策的变化", "★★★★"),
            ("郑和下西洋与新航路开辟的比较", "★★★★"),
        ]),
        ("Ep06 晚清变局", [
            ("鸦片战争的影响", "★★★★★"),
            ("洋务运动的背景、内容、评价", "★★★★★"),
            ("戊戌变法的背景和失败原因", "★★★★★"),
            ("辛亥革命的历史意义", "★★★★★"),
            ("近代中国探索救国道路的历程", "★★★★★"),
        ]),
    ]


def build_all_concepts():
    return [
        ("杯酒释兵权", "北宋初年，赵匡胤通过酒宴方式，要求手握兵权的将领交出兵权，改任虚职。本质是用和平方式解决藩镇割据问题，是'强干弱枝'策略的核心步骤。开启了北宋重文抑武的先河。"),
        ("重文抑武", "北宋基本国策：重用文官，抑制武将。背景是五代十国武将乱政的教训。后果：一方面消除了藩镇割据隐患，另一方面导致北宋军事积弱，在对外战争中长期处于劣势。"),
        ("澶渊之盟", "1005年，北宋与辽在澶渊（今河南濮阳）签订的和平条约：北宋每年给辽白银10万两、绢20万匹，换取辽撤兵并承认宋为正统。是北宋用金钱换和平的典型案例，也是后来宋金、宋元关系的预演。"),
        ("王安石变法", "1069-1076年，宋神宗支持下，王安石推行的一系列改革：青苗法（低息贷款）、募役法（雇人服役）、市易法（政府平价）等。目标是富国强兵，缓和社会矛盾。结果因新旧党争、推行过急等原因失败。"),
        ("青苗法", "王安石变法核心措施：每年春荒时节，政府以低于私人高利贷的利率向农民放贷，秋收后还本付息。本意是打击高利贷、帮助农民，但执行中地方官员强行摊派，反而加重了农民负担。"),
        ("新旧党争", "以王安石为代表的'新党'与以司马光为代表的'旧党'之间的政治斗争。贯穿北宋后期，间歇性反复。实质是如何看待政府干预经济、如何看待改革的速度和方式。这场党争消耗了北宋的政治精力，是北宋灭亡的重要原因之一。"),
        ("靖康之变", "1127年，金兵攻破北宋都城开封，掳走宋徽宗、宋钦宗及大量皇族、官员、财宝，北宋灭亡。史称'靖康之变'或'靖康之耻'。是中华文明史上最大的国耻之一，也是南宋偏安格局的直接成因。"),
        ("岳飞", "南宋抗金名将，民族英雄。其'精忠报国'的故事家喻户晓。率领岳家军北伐，多次击败金兵，却在即将收复中原时被宋高宗和秦桧以'莫须有'罪名冤杀。是南宋政治悲剧的标志性人物。"),
        ("行省制度", "元朝创立的行政区划制度：全国设行中书省（行省），代表中央行使地方管理权。是秦朝郡县制之后，中国地方行政制度的又一次重大创新，奠定了明清乃至现代省级行政区划的基础。"),
        ("四等人制", "元朝将全国人民按民族分为四个等级的制度：第一等蒙古人，第二等色目人（西域各族），第三等汉人（原金国境内的汉人和契丹、女真人），第四等南人（原南宋境内汉人）。是元朝民族歧视政策的核心内容，加剧了社会矛盾。"),
        ("郑和下西洋", "1405-1433年，明成祖永乐年间至明宣德年间，三宝太监郑和率领船队七次出使西洋（主要是东南亚、南亚、阿拉伯半岛和东非）。是中国古代规模最大、航程最远的航海活动，也是世界航海史上的壮举。"),
        ("土木堡之变", "1449年，明英宗在宦官王振怂恿下亲征瓦剌，在土木堡（今河北怀来）被俘，明军精锐尽失。是明朝由盛转衰的标志性事件，也是宦官专权危害的典型案例。此后明朝转向战略收缩。"),
        ("鸦片战争", "1840-1842年，英国为打开中国市场、倾销鸦片而发动的侵略战争。中国战败，签订《南京条约》，割让香港，开放五口通商，赔款2100万银元。是中国近代史的开端，也是中国沦为半殖民地半封建社会的起点。"),
        ("洋务运动", "19世纪60-90年代，清朝洋务派以'自强''求富'为口号，引进西方科学技术，创办近代军事工业和民用工业的运动。代表人物：曾国藩、李鸿章、左宗棠、张之洞。甲午战争失败标志着洋务运动破产。"),
        ("戊戌变法", "1898年，光绪帝在康有为、梁启超等维新派推动下，推行的一系列政治、经济、文化改革（史称'百日维新'）。因触动以慈禧太后为代表的守旧派利益，仅维持103天即被镇压，戊戌六君子被杀。是中国近代一次重要的改良尝试。"),
        ("辛亥革命", "1911年，以孙中山为首的革命党人在武昌发动起义，建立中华民国，推翻清朝统治。结束了两千多年的封建君主专制制度，建立了亚洲第一个民主共和国。但革命果实很快被袁世凯窃取，中国陷入军阀混战。"),
    ]


def build_all_qa():
    return [
        {
            "title": "Ep01 宋的困局 章节测验",
            "items": [
                {"q": "【名词解释】杯酒释兵权", "options": [], "a": "北宋初年，赵匡胤通过酒宴方式，要求手握兵权的石守信等将领交出兵权，改任虚职。本质是用和平方式解决藩镇割据隐患，是'强干弱枝'策略的核心步骤。开启了北宋重文抑武的先河，代价是削弱了边防力量。"},
                {"q": "【比较题】重文抑武政策对北宋有何利弊？", "options": [], "a": "利：消除藩镇割据隐患，政治稳定，文化繁荣（宋代科技、文学、艺术均达到历史高峰）。弊：军事积弱，在对辽、金、西夏的战争中长期处于守势，最终导致靖康之变和北宋灭亡。"},
                {"q": "【判断正误】① 杯酒释兵权发生在宋太祖赵匡胤时期② 澶渊之盟是北宋向辽缴纳岁币的开始③ 重文抑武政策消除了所有内乱风险④ 北宋的经济繁荣与其军事政策无关", "options": [], "a": "①○ ②○ ③✗ ④✗"},
                {"q": "【综合题】分析北宋经济繁荣与军事积弱之间的关系。", "options": [], "a": "关系：①重文抑武政策将大量优秀人才吸引到文科，军事人才匮乏②经济繁荣使朝廷有财力维持庞大官僚体系，却无动力改革军事③岁币外交（澶渊之盟）用金钱换和平，代价是财政负担转嫁百姓④经济发展与军事衰弱的矛盾，最终在靖康之变中以最惨烈的方式爆发。"},
            ]
        },
        {
            "title": "Ep02 王安石变法 章节测验",
            "items": [
                {"q": "【名词解释】王安石变法", "options": [], "a": "1069-1076年，宋神宗支持下，王安石推行的一系列改革：青苗法（低息贷款）、募役法（雇人服役）、市易法（政府平价）等。目标是富国强兵、缓和社会矛盾。失败原因：新旧党争激烈、推行过急、地方执行走样。是北宋历史上最重要的改革事件，也是中国古代经济思想的重要实践。"},
                {"q": "【连线题】请将变法措施与其内容连线：\nA. 青苗法 ① 政府雇人服役，农民可出钱代役\nB. 募役法 ② 政府向农民发放低息贷款\nC. 市易法 ③ 政府平价收购滞销商品，稳定物价\nD. 农田水利法 ④ 鼓励民间兴修水利", "options": [], "a": "A-② B-① C-③ D-④"},
                {"q": "【判断正误】① 王安石变法得到了所有士大夫的支持② 新旧党争始于宋神宗时期③ 司马光属于'新党'代表④ 变法失败后新法被全部废除", "options": [], "a": "①✗ ②✗ ③✗ ④✗"},
                {"q": "【综合题】评析王安石变法的历史意义。", "options": [], "a": "意义：①首次系统性地将政府干预经济理论付诸实践，是中国古代经济思想的高峰②揭示了'政府与市场'这一永恒命题③新旧党争成为北宋政治内耗的主线，加速了北宋衰落。评价：变法方向具有合理性，但执行中操之过急、用人失当，最终走向反面。"},
            ]
        },
        {
            "title": "Ep03 靖康之变 章节测验",
            "items": [
                {"q": "【名词解释】靖康之变", "options": [], "a": "1127年，金兵攻破北宋都城开封，掳走宋徽宗、宋钦宗及大量皇族、官员、技艺人员和财宝，北宋灭亡。史称'靖康之变'或'靖康之耻'。是中华文明史上最大的国耻之一，直接导致南宋偏安格局的形成，岳飞的抗金故事也因此有了历史背景。"},
                {"q": "【填空题】岳飞抗金发生在___（朝代），他被以___罪名冤杀，该事件反映出南宋初年___与___的政治矛盾。", "options": [], "a": "南宋；'莫须有'（或许有罪）；主战派（岳飞）与主和派（秦桧、宋高宗）"},
                {"q": "【判断正误】① 靖康之变是北宋末年政治腐败的必然结果② 岳飞是南宋唯一抗金名将③ 北宋灭亡后宋高宗在临安建立了南宋④ 宋金关系一直处于战争状态", "options": [], "a": "①○ ②✗ ③○ ④✗"},
                {"q": "【综合题】分析北宋灭亡的根本原因。", "options": [], "a": "根本原因：①重文抑武国策导致军事长期积弱②北宋末年政治腐败，蔡京等'六贼'误国③宋徽宗联金灭辽的决策失误，暴露了北宋军力虚弱的真相。直接原因：金兵南下的军事打击。核心教训：一个文化上高度繁荣的帝国，若军事上长期自我削弱，最终必然付出惨重代价。"},
            ]
        },
        {
            "title": "Ep04 蒙古帝国 章节测验",
            "items": [
                {"q": "【名词解释】行省制度", "options": [], "a": "元朝创立的行政区划制度：全国设行中书省（行省），代表中央在地方行使管理权。行省制度的创新：①打破山川形便的传统行政区划原则②行省官员拥有相当大的地方自主权，但军政大权归中央③奠定了明清乃至现代省级行政区划的基础，是中国地方行政史上的重大创新。"},
                {"q": "【比较题】比较元朝四等人制与金朝的民族制度。", "options": [], "a": "相同点：均按民族/族群划分等级，主体民族（汉人）地位较低。不同点：金朝主要是女真人与汉人的二元对立；元朝是更复杂的四等人制（蒙古→色目→汉人→南人），且将原南宋汉人（南人）置于最低等级，反映了元朝征服南宋后对南方汉族更为歧视的态度。"},
                {"q": "【判断正误】① 成吉思汗统一蒙古后建立了元朝② 行省制度是元朝独创③ 四等人制消除了民族矛盾④ 元朝的统一结束了中国长期的分裂局面", "options": [], "a": "①✗ ②✗ ③✗ ④○"},
                {"q": "【综合题】评析元朝行省制度的历史影响。", "options": [], "a": "积极影响：①奠定省级行政区划基础，影响延续至今②加强了中央对地方的控制③促进了边疆地区的管辖（西藏正式纳入中国版图）。消极影响：①行省权力过大，中央难以有效监督②民族分化政策加剧社会矛盾。是元朝统治的重要工具，也是中国古代地方行政的重要遗产。"},
            ]
        },
        {
            "title": "Ep05 明帝国的两难 章节测验",
            "items": [
                {"q": "【名词解释】郑和下西洋", "options": [], "a": "1405-1433年，明成祖永乐年间至明宣德年间，三宝太监郑和率领船队七次出使西洋（主要是东南亚、南亚、阿拉伯半岛和东非）。是中国古代规模最大、航程最远的航海活动，展示了中国当时的航海技术和国家实力。但宣德之后明朝实行海禁，郑和的航海记录被毁，郑和下西洋成为绝响。"},
                {"q": "【比较题】郑和下西洋与欧洲新航路开辟有何本质区别？", "options": [], "a": "目的不同：郑和下西洋以政治目的为主（宣扬国威、寻求朝贡），经济目的为辅；欧洲新航路开辟以经济目的为主（寻求黄金、贸易、殖民地）。结果不同：中国放弃航海，欧洲开启殖民扩张时代。根本原因：郑和航海是政府行为，服务于朝贡体系；欧洲航海是商业行为，服务于资本积累。"},
                {"q": "【判断正误】① 郑和下西洋发生在明成祖时期② 土木堡之变导致明军精锐尽失③ 明朝海禁政策是一贯不变的④ 郑和的航海记录保存完好", "options": [], "a": "①○ ②○ ③✗ ④✗"},
                {"q": "【综合题】分析明朝海禁政策的历史影响。", "options": [], "a": "影响：①海禁初期有防御倭寇的必要性②但长期海禁阻断中外贸易，导致走私猖獗（倭寇问题本质是贸易问题）③使中国错失了大航海时代的机遇④最终在鸦片战争后被西方坚船利炮打破。教训：闭关锁国不能解决根本问题，只会让差距越拉越大。"},
            ]
        },
        {
            "title": "Ep06 晚清变局 章节测验",
            "items": [
                {"q": "【名词解释】洋务运动", "options": [], "a": "19世纪60-90年代，清朝洋务派以'自强''求富'为口号，引进西方科学技术，创办近代军事工业（江南制造总局等）和民用工业（轮船招商局等）的运动。代表人物：曾国藩、李鸿章、左宗棠、张之洞。甲午战争失败标志着洋务运动破产，证明'中学为体、西学为用'的路走不通。"},
                {"q": "【填空题】1898年的戊戌变法仅维持了___天，因___发动政变而失败，历史上称这六位遇害的维新人士为'___'。", "options": [], "a": "103天；慈禧太后；戊戌六君子"},
                {"q": "【判断正误】① 鸦片战争是中国近代史的开端② 洋务运动彻底解决了清朝的军事问题③ 戊戌变法失败说明改革在中国走不通④ 辛亥革命推翻了两千多年的封建制度", "options": [], "a": "①○ ②✗ ③✗ ④○"},
                {"q": "【综合题】评析近代中国救国道路的探索历程。", "options": [], "a": "历程：①鸦片战争后，林则徐、魏源提出'师夷长技以制夷'（思想萌芽）②洋务运动'自强求富'（技术层面）③戊戌变法'君主立宪'（制度层面）——均以失败告终④辛亥革命推翻帝制（政治层面），建立共和。规律：①从技术到制度到思想的层层递进②每一次尝试失败，都推动下一次更彻底的探索③最终证明：在半殖民地半封建社会条件下，任何改良都不能救中国，只有彻底革命才能开辟新路。"},
            ]
        },
    ]


def main():
    import os, importlib

    scripts_dir = BASE
    episode_modules = [
        ("古史_v2_ep01_宋的困局", "宋的困局"),
        ("古史_v2_ep02_王安石变法", "王安石变法"),
        ("古史_v2_ep03_靖康之变", "靖康之变"),
        ("古史_v2_ep04_蒙古帝国", "蒙古帝国"),
        ("古史_v2_ep05_明帝国的两难", "明帝国的两难"),
        ("古史_v2_ep06_晚清变局", "晚清变局"),
    ]

    ep_datas = []
    for mod_name, title in episode_modules:
        path = os.path.join(scripts_dir, mod_name + ".py")
        spec = importlib.util.spec_from_file_location(mod_name, path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        ep_datas.append(mod.get_data())

    r = AncientHistoryRenderer()

    r.cover(
        title_s="变 与 局",
        title_m="中国古代史卷二",
        subtitle="从杯酒释兵权到辛亥革命：改革与困局的一千年",
        meta_lines=[
            ("系列", "变与局"),
            ("配置包", "cafa_ancient_history_v2"),
            ("框架", "三层结构（王朝兴衰 + 历史核心问题 + 当代启示）"),
            ("收录集数", "全6集 · 完整版"),
            ("历史跨度", "960年（北宋）至1911年（晚清）"),
            ("主题", "从杯酒释兵权到辛亥革命"),
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
