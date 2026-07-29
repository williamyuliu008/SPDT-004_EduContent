# -*- coding: utf-8 -*-
"""
革与鼎 · 中国古代史卷一 电子书生成器
- DOCX + Markdown 双格式输出
- 每集含时代背景、历史核心问题、四个Acts
- 测验/考点/概念速查移至附录
"""
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import os

BASE = (r"C:\Users\willi\Desktop\我的视野\0713-基于知识库的高阶备考智能体"
        r"\02-设计文档\古史_v1_革与鼎\scripts")
MD_OUT = os.path.join(BASE, "革与鼎_电子书.md")
DOCX_OUT = os.path.join(BASE, "革与鼎_电子书.docx")

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
        fr = fp.add_run("革与鼎 · 中国古代史卷一 · 高考备考读本")
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
         "text": "历史不是用来背的。历史是用来理解的。\n\n很多人学历史的方法是：记年代、记事件、记意义。背了忘，忘了背，考完就扔。\n\n这不是学历史，是背书。\n\n《革与鼎》想做的事，是把历史变回它本来该有的样子——它是一连串选择，一连串因果，一连串人在特定时刻做的特定决定。每一个历史事件的背后，都有一个活生生的人，站在十字路口，做了一个当时看来'合理'的选择，然后这个选择，在几十年、几百年后，产生了谁也没想到的后果。\n\n理解了这个'为什么'，历史就活了。背不住的年代，自然就记住了——因为它有意义了。"},
        {"type": "h2", "text": "二、这套书的结构"},
        {"type": "p",
         "text": "卷一的主题是'制度断裂'——从西周分封制到安史之乱，六集，每一集讲一个关键时刻：\n\nEp01 封邦建国：周人为什么要搞分封？\n\nEp02 百家争鸣：乱世为什么产生了思想爆炸？\n\nEp03 天下一统：书同文和废分封，本质上是同一件事。\n\nEp04 汉武雄图：打仗的钱从哪来？\n\nEp05 胡汉之间：拓跋宏为什么要主动汉化？\n\nEp06 盛唐拐点：安史之乱是意外，还是必然？\n\n每一集不是按照朝代顺序流水账——而是围绕一个核心历史问题，用微剧本的形式，把你放到那个时刻，看那个人如何做决定。"},
        {"type": "h2", "text": "三、关于高考"},
        {"type": "p",
         "text": "本书不是高考历史考点的简单汇编。\n\n但它比任何汇编都更有助于备考——因为它让你理解考点背后的'为什么'。\n\n能讲出故事的历史知识，才记得住。记不住的历史知识，考完就忘。\n\n附录里，我们把每集的高考高频考点、关键概念和章节测验都整理好了——你可以先读正文，再翻附录检验；也可以直接用附录备考。\n\n两条路都通。"},
        {"type": "quote",
         "text": "一切历史都是当代史。一切考试，都是对理解力的检验。"},
    ]


def build_epilogue():
    return [
        {"type": "h2", "text": "尾声：六次断裂，一条线索"},
        {"type": "p",
         "text": "从牧野之战到安史之乱，一千八百年。\n\n我们在这六集里，走过了一条奇怪的路径：\n\n周朝用分封制建立秩序，秩序崩溃了；\n\n秦始皇用郡县制重建秩序，秩序又被自己的暴政摧毁了；\n\n汉武帝用独尊儒术加盐铁专营支撑秩序，秩序在外族入侵和内部腐败中衰落了；\n\n北魏用汉化改革融入秩序，改革又被内部的保守势力撕裂了；\n\n唐朝用藩镇制度维持边疆秩序，秩序被藩镇自己引爆的叛乱吞噬了。\n\n每一种秩序，在建立的那一刻，都看起来很完美。\n\n每一种秩序，在崩溃的那一刻，都让后来者惊叹：怎么会没看出来？\n\n历史学家的特权，是事后诸葛亮。但历史的当事人，没有这个特权——他们只能在那一个时刻，凭他们能看到的信息，做他们认为最好的选择。\n\n理解这一点，比记住任何一个具体的历史事件，都更重要。"},
        {"type": "h2", "text": "下一站"},
        {"type": "p",
         "text": "卷一从封邦建国开始，到安史之乱结束。\n\n卷二将从北宋开始，到晚清结束。\n\n卷二的主题依然是'制度困局'——但这次的困局不同：\n\n北宋的问题是：如何让一个文化繁荣的帝国，同时拥有足够的军事实力？\n\n王安石用变法回答这个问题，他的答案是：政府深度介入经济。\n\n司马光反对，他的答案是：政府应该少管，让民间自己来。\n\n这场争论，到今天还在继续。\n\n而历史，正在等待下一批读者。"},
    ]


def build_all_exam_points():
    return [
        ("Ep01 封邦建国", [
            ("分封制的目的、内容（诸侯权利义务）", "★★★★★"),
            ("宗法制与分封制的关系", "★★★★★"),
            ("礼乐制度的功能和实质", "★★★★"),
            ("分封制崩溃的原因（内因+外因）", "★★★★★"),
            ("分封制 vs 郡县制的根本区别", "★★★★★"),
        ]),
        ("Ep02 百家争鸣", [
            ("百家争鸣出现的历史背景（礼崩乐坏）", "★★★★★"),
            ("孔子及儒家核心思想（仁、礼、中庸）", "★★★★★"),
            ("道家老子、庄子核心思想", "★★★★"),
            ("墨家墨子核心思想（兼爱、尚贤）", "★★★"),
            ("法家韩非子核心思想（法治、耕战）", "★★★★"),
            ("百家争鸣的历史意义", "★★★★★"),
        ]),
        ("Ep03 天下一统", [
            ("秦统一六国的原因", "★★★★★"),
            ("秦始皇巩固统一的措施", "★★★★★"),
            ("郡县制 vs 分封制", "★★★★★"),
            ("秦朝速亡原因（多角度）", "★★★★★"),
            ("秦朝制度创新的历史意义", "★★★★"),
        ]),
        ("Ep04 汉武雄图", [
            ("汉武帝加强中央集权的措施", "★★★★★"),
            ("盐铁专营的背景、内容、影响", "★★★★★"),
            ("丝绸之路的历史意义", "★★★★★"),
            ("汉武帝时期民族关系", "★★★★"),
            ("对汉武帝的历史评价（积极+消极）", "★★★★★"),
        ]),
        ("Ep05 胡汉之间", [
            ("北魏孝文帝改革背景", "★★★★★"),
            ("汉化改革措施（均田制、迁都洛阳等）", "★★★★★"),
            ("均田制的意义", "★★★★"),
            ("北魏汉化改革的历史影响", "★★★★★"),
            ("南北朝对峙时期的民族融合", "★★★★"),
        ]),
        ("Ep06 盛唐拐点", [
            ("开元盛世的表现", "★★★★"),
            ("安史之乱爆发的原因", "★★★★★"),
            ("安史之乱的过程", "★★★★★"),
            ("安史之乱的影响", "★★★★★"),
            ("安史之乱的历史意义", "★★★★★"),
        ]),
    ]


def build_all_concepts():
    return [
        ("分封制", "西周政治制度：天子将土地和人民分封给诸侯，诸侯对天子承担义务（朝贡、服役、出兵），在自己的封地上享有相当大的自治权和世袭权。"),
        ("宗法制", "以血缘关系为基础的政治继承制度。核心是嫡长子继承制——嫡长子拥有继承权，其他儿子降为'别子'，形成大宗和小宗的等级结构，是分封制的制度基础。"),
        ("礼乐制度", "西周配套分封制的社会规范体系：不同等级的人享有不同规格的礼仪、音乐和器物，用以维护政治等级秩序。"),
        ("郡县制", "与分封制相对：地方官员由中央任命，不世袭，有任期，可撤换。秦始皇统一后全面推行，奠定此后两千年中央集权的基础。"),
        ("书同文", "秦始皇推行的文字统一政策：以小篆为标准字体，消除六国文字差异。是中国历史上第一次大规模语言标准化运动，是中华文明延续的重要基础。"),
        ("轴心时代", "德国哲学家雅斯贝尔斯提出的概念，指前800-前200年期间，中国、印度、希腊、以色列四大文明同时出现思想繁荣。百家争鸣是中国轴心时代的核心内容。"),
        ("盐铁专营", "汉武帝推行的经济政策：由政府垄断盐和铁的生产和销售。本质是'寓税于价'——通过垄断必需品经营，向所有人征税，充实国库。是中国历史上最早的'国家垄断资本主义'。"),
        ("丝绸之路", "汉代从长安出发，经河西走廊、西域，通向地中海沿岸的贸易通道。不仅是贸易通道，也是文明交流的通道。"),
        ("均田制", "北魏孝文帝推行的土地制度：国家将无主土地按人口均分给农民耕种，农民向国家缴纳租赋。它稳定了农业生产，是北魏政权获得汉族农民支持的重要原因。"),
        ("安史之乱", "755-763年，安禄山、史思明在范阳起兵发动的叛乱。它是唐朝由盛转衰的转折点，导致藩镇割据、宦官专权、经济破坏，深刻改变了中国此后的政治走向。"),
    ]


def build_all_qa():
    return [
        {
            "title": "Ep01 封邦建国 章节测验",
            "items": [
                {"q": "【名词解释】分封制", "options": [], "a": "西周政治制度：天子将土地和人民分封给诸侯，诸侯对天子承担义务，在封地上享有相当大的自治权和世袭权，'以藩屏周'。"},
                {"q": "【比较题】分封制和郡县制的根本区别是什么？", "options": [], "a": "根本区别在于政治合法性的来源：分封制的合法性来自血缘（宗法），郡县制的合法性来自制度（中央授权）。前者天然具有分裂倾向，后者天然具有统一趋向。"},
                {"q": "【判断正误】① 分封制和宗法制互为表里② 礼乐制度只是文化制度，与政治无关③ 周朝分封的诸侯中姬姓占多数④ 郡县制消除了所有地方分裂风险", "options": [], "a": "①○ ②✗ ③○ ④✗"},
                {"q": "【综合题】分析周朝分封制崩溃的原因，并说明其与郡县制的关系。", "options": [], "a": "原因：①诸侯实力增强后挑战周天子权威（内因）②犬戎攻破镐京，周天子权威被武力公然挑战（外因）。关系：郡县制是秦始皇在吸收分封制教训基础上设计的，用官僚任命制代替世袭制，从根本上消除了诸侯割据的制度基础——但郡县制也带来新问题（信息不对称、中央控制力有限等），这个博弈延续两千年。"}
            ]
        },
        {
            "title": "Ep02 百家争鸣 章节测验",
            "items": [
                {"q": "【连线题】请将各家与其核心主张连线：\nA. 儒家 ① 兼爱、尚贤\nB. 道家 ② 无为而治\nC. 墨家 ③ 仁义礼乐\nD. 法家 ④ 法治、耕战", "options": [], "a": "A-③ B-② C-① D-④"},
                {"q": "【名词解释】轴心时代", "options": [], "a": "德国哲学家雅斯贝尔斯提出的概念，指前800-前200年期间，中国、印度、希腊、以色列四大文明同时出现思想繁荣。百家争鸣是中国轴心时代的核心内容，奠定了中国思想文化的基础。"},
                {"q": "【判断正误】① 百家争鸣只发生在春秋时期② 孔子周游列国是为了传播儒家思想③ 法家思想适合和平年代治国④ 汉武帝'独尊儒术'标志着百家争鸣结束", "options": [], "a": "①✗ ②○ ③✗ ④○"},
                {"q": "【综合题】论述百家争鸣出现的时代背景，并分析其历史意义。", "options": [], "a": "背景：①周朝礼乐秩序崩溃，诸侯僭越，周天子权威衰落（政治背景）②社会生产力发展，阶级关系变化（经济背景）③私学兴起，知识分子阶层形成（文化背景）。意义：①奠定了中国思想文化的基础②各派思想成为中国传统文化的源头③百家争鸣中的制度思考（如法家郡县制）深刻影响后世政治制度建设。"}
            ]
        },
        {
            "title": "Ep03 天下一统 章节测验",
            "items": [
                {"q": "【名词解释】书同文", "options": [], "a": "秦始皇推行的文字统一政策：以小篆为标准字体，消除六国文字差异，是中国历史上第一次大规模语言标准化运动。它不仅是技术统一，更是文化认同的构建，为中华文明延续提供了关键的文化基础。"},
                {"q": "【填空题】秦始皇统一六国后，丞相___（人名）反对分封制，建议推行郡县制，被秦始皇采纳。", "options": [], "a": "李斯"},
                {"q": "【判断正误】① 书同文和废分封本质都是标准化② 秦朝速亡完全是因为暴政③ 郡县制消除了所有地方分裂风险④ 秦制遗产只有消极影响", "options": [], "a": "①○ ②✗ ③✗ ④✗"},
                {"q": "【综合题】评析秦始皇的历史功过。", "options": [], "a": "功：①统一六国，建立中国历史上第一个中央集权王朝②推行郡县制、书同文、统一度量衡，奠定两千年制度基础③修筑长城、灵渠等重大工程。过：①严刑峻法，超出社会承受能力②过度劳役（长城、阿房宫、骊山陵）③继承人选择失误（赵高矫诏）。评价：应辩证看待，秦始皇的制度创新对中华文明有深远积极意义，但其暴政是秦朝速亡的直接原因。"}
            ]
        },
        {
            "title": "Ep04 汉武雄图 章节测验",
            "items": [
                {"q": "【名词解释】盐铁专营", "options": [], "a": "汉武帝推行的经济政策：由政府垄断盐和铁的生产和销售。本质是'寓税于价'——通过垄断必需品经营，向所有人征税，充实国库以支撑对匈奴战争。是为对付匈奴 War 而设计的财政方案，也是中国历史上最早的'国家垄断资本主义'。"},
                {"q": "【连线题】请将历史人物与其主要贡献连线：\nA. 张骞 ① 漠北大战，破匈奴\nB. 卫青 ② 出使西域，开通丝绸之路\nC. 霍去病 ③ 独尊儒术\nD. 董仲舒 ④ 收复河套地区", "options": [], "a": "A-② B-④ C-① D-③"},
                {"q": "【判断正误】① 汉武帝登基时年仅16岁② 丝绸之路是汉武帝主动开辟的贸易路线③ 盐铁专营只增加了政府收入④ 汉武帝的战争政策得到所有人的支持", "options": [], "a": "①○ ②✗ ③✗ ④✗"},
                {"q": "【综合题】分析汉武帝的历史功过。", "options": [], "a": "功：①打击匈奴，开疆拓土②开通丝绸之路，促进东西方交流③独尊儒术，统一思想，确立中华文化主脉。过：①穷兵黩武，耗尽文景积蓄②盐铁专营加重百姓负担③晚年巫蛊之祸，造成宫廷动荡。评价：汉武帝是中国历史上最雄才大略的皇帝之一，但也是透支国力最严重的皇帝之一；其功过均有深刻的历史影响。"}
            ]
        },
        {
            "title": "Ep05 胡汉之间 章节测验",
            "items": [
                {"q": "【名词解释】均田制", "options": [], "a": "北魏孝文帝推行的土地制度：国家将无主土地按人口均分给农民耕种，农民向国家缴纳租赋并承担劳役。它稳定了农业生产，缓和了社会矛盾，是北魏政权获得汉族农民支持的重要原因，也为后来隋唐的均田制提供了蓝本。"},
                {"q": "【填空题】北魏孝文帝在___年迁都___，随后推行全面汉化改革。", "options": [], "a": "494年；洛阳"},
                {"q": "【判断正误】① 北魏是鲜卑族建立的政权② 孝文帝改革遭到所有鲜卑贵族反对③ 北魏汉化改革奠定了隋唐基础④ 北魏之后，鲜卑族完全消失了", "options": [], "a": "①○ ②✗ ③○ ④✗"},
                {"q": "【综合题】评析北魏孝文帝汉化改革的历史意义。", "options": [], "a": "意义：①促进民族融合，奠定隋唐盛世的人口和文化基础②加速鲜卑族封建化，推动社会进步③将儒家文化传播到北方，推动文化交流。局限：①过于激进，引发鲜卑保守派反弹②在孝文帝死后改革中断。总体评价：孝文帝改革是魏晋南北朝时期最具进步意义的历史事件之一，为中华多元一体格局的形成奠定了基础。"}
            ]
        },
        {
            "title": "Ep06 盛唐拐点 章节测验",
            "items": [
                {"q": "【名词解释】安史之乱", "options": [], "a": "755-763年，安禄山、史思明在范阳起兵发动的叛乱。它是唐朝由盛转衰的转折点，导致藩镇割据（河北三镇半独立）、宦官专权、财政崩溃，深刻改变了中国此后的政治走向，是中国历史上最重要的事件之一。"},
                {"q": "【填空题】开元盛世的缔造者是唐玄宗___（年号），他在位前期政治清明，后期因宠信___而导致朝政混乱。", "options": [], "a": "开元；杨贵妃（杨国忠）"},
                {"q": "【判断正误】① 安史之乱是唐玄宗个人失误导致的意外事件② 马嵬驿兵变中杨贵妃被杀③ 安史之乱后唐朝藩镇问题得到彻底解决④ 安史之乱没有改变唐朝的政治制度", "options": [], "a": "①✗ ②○ ③✗ ④✗"},
                {"q": "【综合题】分析安史之乱爆发的深层原因及其历史影响。", "options": [], "a": "原因：①藩镇制度（边疆将领拥兵自重）②唐玄宗晚年怠政用人失误（重用安禄山）③政治腐败（杨国忠误国）——根本上是唐朝扩张政策与中央控制力之间的结构性矛盾。影响：①唐朝由盛转衰，藩镇割据②宦官专权开始（以宦官制衡武将）③经济破坏，人口锐减④政治格局改变，中国转向内向⑤民族关系紧张，对外政策从开放转向保守。"}
            ]
        },
    ]


def main():
    import os, importlib

    scripts_dir = BASE
    episode_modules = [
        ("古史_ep01_封邦建国", "封邦建国"),
        ("古史_ep02_百家争鸣", "百家争鸣"),
        ("古史_ep03_天下一统", "天下一统"),
        ("古史_ep04_汉武雄图", "汉武雄图"),
        ("古史_ep05_胡汉之间", "胡汉之间"),
        ("古史_ep06_盛唐拐点", "盛唐拐点"),
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
        title_s="革 与 鼎",
        title_m="中国古代史卷一",
        subtitle="从封邦建国到安史之乱：制度演变的六次断裂",
        meta_lines=[
            ("系列", "革与鼎"),
            ("配置包", "cafa_ancient_history_v1"),
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
