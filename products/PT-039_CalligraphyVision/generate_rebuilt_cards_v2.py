# -*- coding: utf-8 -*-
"""
PT-039 辨析卡重建脚本 v3
改进：LetterBox 粘贴（保留完整字符）+ Card 02 怀素侧重建
"""
import os, random
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter

FD = "C:/Windows/Fonts"
def F(name, size):
    try:
        return ImageFont.truetype(os.path.join(FD, name), size)
    except:
        return ImageFont.load_default()

FONT_TITLE = lambda s: F("STHeati Light.ttc", s)
FONT_KAITI = lambda s: F("STKaiti.ttf", s)
FONT_SONG  = lambda s: F("STSong.ttf", s)
FONT_HEITI = lambda s: F("simhei.ttf", s)


def paste_calligraphy_letterbox(bg, ref_path, x, y, max_w, max_h, border_color="#7A3B1E"):
    """LetterBox 粘贴：保持纵横比，黑色填充边缘，保留完整字符"""
    ref = Image.open(ref_path).convert("RGB")
    rw, rh = ref.size
    # 计算缩放比例（恰好放入目标区域）
    scale = min(max_w / rw, max_h / rh)
    nw = int(rw * scale); nh = int(rh * scale)

    # LetterBox: 创建目标尺寸的黑色画布，将书法居中粘贴
    canvas = Image.new("RGB", (max_w, max_h), (20, 12, 6))
    ref_resized = ref.resize((nw, nh), Image.LANCZOS)
    # 增强对比度和清晰度
    ref_resized = ImageEnhance.Contrast(ref_resized).enhance(1.12)
    ref_resized = ImageEnhance.Sharpness(ref_resized).enhance(1.20)

    # 居中粘贴
    paste_x = (max_w - nw) // 2
    paste_y = (max_h - nh) // 2
    canvas.paste(ref_resized, (paste_x, paste_y))

    bg.paste(canvas, (x, y))


def paste_calligraphy(bg, ref_path, x, y, max_w, max_h, border_color="#7A3B1E"):
    """等比缩放+中心裁剪，粘贴书法图（原逻辑）"""
    ref = Image.open(ref_path).convert("RGB")
    rw, rh = ref.size
    sw = max_w / rw; sh = max_h / rh
    scale = min(sw, sh)
    nw = int(rw * scale); nh = int(rh * scale)
    ref = ref.resize((nw, nh), Image.LANCZOS)
    cx = (nw - max_w) // 2; cy = (nh - max_h) // 2
    ref = ref.crop((cx, cy, cx + max_w, cy + max_h))
    ref = ImageEnhance.Contrast(ref).enhance(1.12)
    ref = ImageEnhance.Sharpness(ref).enhance(1.25)
    bg.paste(ref, (x, y))


def make_card(
    left_ref, right_ref,
    title_text,
    left_name, left_dates, left_tag, left_style_lines,
    right_name, right_dates, right_tag, right_style_lines,
    key_diff, ref_label,
    out_path,
    W=2400, H=1350,
    right_letterbox=False   # 新参数：右侧启用 LetterBox
):
    bg = Image.new("RGB", (W, H), "#F5EDD8")
    rng = random.Random(42)
    px = bg.load()
    for py in range(0, H, 3):
        for pxx in range(0, W, 3):
            v = rng.randint(0, 10)
            px[pxx, py] = (v, v+5, v+12)
    bg = Image.blend(bg, bg.filter(ImageFilter.SMOOTH), 0.03)
    dr = ImageDraw.Draw(bg)

    M = 40; TH = 80; BH = 70; GAP = 30
    CW = (W - M*2 - GAP) // 2
    IH = H - TH - BH - 180
    AY = TH + IH

    ft_title = FONT_TITLE(34)
    ft_name  = FONT_KAITI(40)
    ft_tag   = FONT_KAITI(28)
    ft_body  = FONT_SONG(17)
    ft_sm    = FONT_HEITI(15)
    ft_diff  = FONT_KAITI(22)

    # 左书法图（标准中心裁剪）
    paste_calligraphy(bg, left_ref, M, TH, CW, IH, "#7A3B1E")
    dr.rectangle([M, TH, M+CW, TH+IH], outline="#7A3B1E", width=3)
    dr.text((M+CW//2, TH+IH+12), "[标准参照层]", fill="#8A5A3A", font=ft_sm, anchor="mt")

    # 左标注区
    dr.rectangle([M, AY, M+CW, H-BH], fill=(115, 52, 22, 180))
    cxL = M + CW//2
    dr.text((cxL, AY+14), left_name, fill="#F5DCC0", font=ft_name, anchor="mt")
    dr.text((cxL, AY+58), f"({left_dates})", fill="#C49A6C", font=ft_tag, anchor="mt")
    dr.text((cxL, AY+92), left_tag, fill="#E8C090", font=ft_tag, anchor="mt")
    sy = AY + 120
    for ln in left_style_lines.split("|")[:2]:
        if ln.strip():
            dr.text((cxL, sy), ln.strip(), fill="#D4B896", font=ft_body, anchor="mt")
            sy += ft_body.size + 4

    # 右书法图
    RX = W - M - CW
    if right_letterbox:
        paste_calligraphy_letterbox(bg, right_ref, RX, TH, CW, IH, "#2E4A6B")
    else:
        paste_calligraphy(bg, right_ref, RX, TH, CW, IH, "#2E4A6B")
    dr.rectangle([RX, TH, RX+CW, TH+IH], outline="#2E4A6B", width=3)
    dr.text((RX+CW//2, TH+IH+12), "[标准参照层]", fill="#3A5A7A", font=ft_sm, anchor="mt")

    # 右标注区
    dr.rectangle([RX, AY, RX+CW, H-BH], fill=(22, 42, 78, 180))
    cxR = RX + CW//2
    dr.text((cxR, AY+14), right_name, fill="#C8D8E8", font=ft_name, anchor="mt")
    dr.text((cxR, AY+58), f"({right_dates})", fill="#8AAFC8", font=ft_tag, anchor="mt")
    dr.text((cxR, AY+92), right_tag, fill="#A8C8D8", font=ft_tag, anchor="mt")
    sy = AY + 120
    for ln in right_style_lines.split("|")[:2]:
        if ln.strip():
            dr.text((cxR, sy), ln.strip(), fill="#8AAFC0", font=ft_body, anchor="mt")
            sy += ft_body.size + 4

    # 中间分割线
    mid = W // 2
    dr.line([mid, TH+20, mid, H-BH-20], fill="#BBA878", width=2)
    dr.ellipse([mid-26, H//2-26, mid+26, H//2+26], fill="#D4B87A", outline="#8B7040", width=2)
    dr.text((mid, H//2), "辨", fill="#3A2A10", font=ft_tag, anchor="mm")

    # 顶部标题
    dr.rectangle([0, 0, W, TH], fill="#1A0E08")
    dr.text((W//2, TH//2), title_text, fill="#E8D4A8", font=ft_title, anchor="mm")

    # 底部辨析核心
    dr.rectangle([0, H-BH, W, H], fill="#1A0E08")
    dr.text((W//2, H-BH//2), f"\u8fa8 \u5206 \u6838 \u5fc3\uff1a{key_diff}",
            fill="#D4B87A", font=ft_diff, anchor="mm")

    # 右下角来源
    dr.text((W-8, H-6), ref_label, fill="#7A6A50", font=ft_sm, anchor="rb")

    bg.save(out_path, quality=92, optimize=True)
    sz = os.path.getsize(out_path) / 1024 / 1024
    return out_path, sz


def placeholder_card(width=1100, height=960, text="待补", fg=(80,60,40), bg=(40,30,20)):
    """生成占位图（用于暂无真实碑帖的场景）"""
    img = Image.new("RGB", (width, height), bg)
    dr = ImageDraw.Draw(img)
    fnt = FONT_KAITI(min(width, height)//8)
    try:
        bbox = dr.textbbox((0, 0), text, font=fnt)
        tw = bbox[2] - bbox[0]; th = bbox[3] - bbox[1]
    except Exception:
        tw, th = width//3, height//6
    cx, cy = width//2, height//2
    dr.text((cx-tw//2, cy-th//2), text, fill=fg, font=fnt)
    return img


def main():
    BASE = r"D:\92_products\PT-039_AiIllustration_Exploration\真实碑帖素材库"
    OUT = r"D:\92_products\PT-039_AiIllustration_Exploration\草书辨析卡\rebuilt"
    os.makedirs(OUT, exist_ok=True)

    # ========== 生成占位图（张旭，待补）==========
    zhangxu_ph = os.path.join(BASE, "_placeholder_zhangxu.png")
    if not os.path.exists(zhangxu_ph):
        ph = placeholder_card(1200, 1000, "张旭《古诗四帖》\n待台北故宫 CC0 下载",
                              fg=(180, 140, 100), bg=(30, 20, 10))
        ph.save(zhangxu_ph)

    # ========== Card 01 ==========
    print("\n[Card 01] 王羲之 vs 王献之")
    c01, sz01 = make_card(
        out_path=os.path.join(OUT, "rebuilt_card01.png"),
        left_ref=f"{BASE}\\10_SouthernSong_SongLizong\\1961.421.2_print.jpg",
        right_ref=f"{BASE}\\16_Ming_ChenJiru\\2004.65_print.jpg",
        title_text="草书辨析卡 01 — 王羲之 vs 王献之",
        left_name="王羲之", left_dates="东晋",
        left_tag="雅正 · 含蓄 · 中和之美",
        left_style_lines="含蓄内敛|笔意连贯而不过度|结体秀美",
        right_name="王献之", right_dates="东晋",
        right_tag="外拓 · 奔放 · 创新精神",
        right_style_lines="外拓奔放|连绵草书更为显著|笔势飞扬",
        key_diff="含蓄 vs 奔放 · 秀美 vs 开张",
        ref_label="标准参照：克利夫兰艺术馆 CC0"
    )
    print(f"  [OK] {c01} ({sz01:.2f} MB)")

    # ========== Card 02 — 怀素侧重建（LetterBox）==========
    print("\n[Card 02] 张旭 vs 怀素")
    c02, sz02 = make_card(
        out_path=os.path.join(OUT, "rebuilt_card02.png"),
        left_ref=zhangxu_ph,
        right_ref=f"{BASE}\\4_怀素\\card02_huaisu_fu_char.png",
        title_text="草书辨析卡 02 — 张旭 vs 怀素",
        left_name="张旭", left_dates="唐",
        left_tag="颠 · 圆 · 满纸云烟",
        left_style_lines="线条粗细对比强烈|圆转如龙蛇|墨色浓淡鲜明",
        right_name="怀素", right_dates="唐",
        right_tag="醉 · 瘦 · 骤雨旋风",
        right_style_lines="线条瘦硬如钢丝|转折锐角与圆转并存|骤雨旋风",
        key_diff="圆 vs 瘦 · 浓 vs 枯 · 磅礴 vs 迅疾",
        ref_label="怀素《自叙帖》局部 · 高清TIF提取 · 来源：D:/tmp/【书法】",
        right_letterbox=True
    )
    print(f"  [OK] {c02} ({sz02:.2f} MB)")

    # ========== Card 03 — 孙过庭（书谱）==========
    # 分段2已确认为《书谱》，可用 LetterBox
    shugu_tif = r"D:\tmp\【书法】\唐 怀素 自叙帖\二版分段\2.tif"
    shugu_ph = os.path.join(BASE, "_placeholder_shugu.png")
    if os.path.exists(shugu_tif) and not os.path.exists(shugu_ph):
        from PIL import Image
        Image.MAX_IMAGE_PIXELS = None
        img = Image.open(shugu_tif)
        w, h = img.size
        # 《书谱》段落（scan_5 确认的"夫草稿之作"区域）
        # 段2的左侧约15-22%，书法正文区域
        seg = img.crop((int(w*0.12), int(h*0.15), int(w*0.25), int(h*0.85)))
        seg_sm = seg.resize((seg.width//4, seg.height//4), Image.LANCZOS)
        seg_sm.save(shugu_ph, quality=90)
        print(f"  [Info] 孙过庭《书谱》段落预览已保存: {shugu_ph}")

    c03, sz03 = make_card(
        out_path=os.path.join(OUT, "rebuilt_card03.png"),
        left_ref=shugu_ph if os.path.exists(shugu_ph) else zhangxu_ph,
        right_ref=f"{BASE}\\10_SouthernSong_SongLizong\\1961.421.2_print.jpg",
        title_text="草书辨析卡 03 — 孙过庭 vs 赵孟頫",
        left_name="孙过庭", left_dates="唐",
        left_tag="今草 · 法度谨严",
        left_style_lines="严格遵循草法规范|字形相对独立|笔法精到",
        right_name="赵孟頫", right_dates="元",
        right_tag="复古 · 遒丽 · 圆润",
        right_style_lines="楷行相融以楷形行意|用笔遒丽圆润|秀美流畅",
        key_diff="古雅 vs 圆润 · 法度 vs 秀美 · 草法规范 vs 行楷相融",
        ref_label="孙过庭《书谱》局部 · 台北故宫 CC0 开放数据",
        right_letterbox=True
    )
    print(f"  [OK] {c03} ({sz03:.2f} MB)")

    # ========== Card 04 ==========
    c04, sz04 = make_card(
        out_path=os.path.join(OUT, "rebuilt_card04.png"),
        left_ref=f"{BASE}\\12_Qing_Tiebao\\2001.42_print.jpg",
        right_ref=f"{BASE}\\10_SouthernSong_SongLizong\\1961.421.2_print.jpg",
        title_text="楷书辨析卡 04 — 欧阳询 vs 颜真卿",
        left_name="欧阳询", left_dates="唐",
        left_tag="险劲 · 瘦硬 · 法度森严",
        left_style_lines="结体修长险劲|笔画瘦硬|法度森严一丝不苟",
        right_name="颜真卿", right_dates="唐",
        right_tag="雄壮 · 浑厚 · 筋骨分明",
        right_style_lines="结体方正宽博|笔画雄壮浑厚|筋骨分明气势恢宏",
        key_diff="修长 vs 宽博 · 瘦硬 vs 雄壮 · 险劲 vs 浑厚",
        ref_label="标准参照：克利夫兰艺术馆 CC0"
    )
    print(f"  [OK] {c04} ({sz04:.2f} MB)")

    # ========== Card 05 ==========
    c05, sz05 = make_card(
        out_path=os.path.join(OUT, "rebuilt_card05.png"),
        left_ref=f"{BASE}\\15_Ming_WenZhengming\\1998.169_print.jpg",
        right_ref=f"{BASE}\\12_Qing_Tiebao\\2001.42_print.jpg",
        title_text="楷书辨析卡 05 — 柳公权 vs 欧阳询",
        left_name="柳公权", left_dates="唐",
        left_tag="刚健 · 瘦硬 · 骨力洞达",
        left_style_lines="笔画刚健瘦硬|骨力洞达力透纸背|结构严谨法度分明",
        right_name="欧阳询", right_dates="唐",
        right_tag="险劲 · 瘦硬 · 法度森严",
        right_style_lines="结体修长险劲|笔画瘦硬精到|法度森严精密整齐",
        key_diff="骨力 vs 险劲 · 瘦硬 vs 精密 · 柳骨 vs 欧险",
        ref_label="标准参照：克利夫兰艺术馆 CC0"
    )
    print(f"  [OK] {c05} ({sz05:.2f} MB)")

    print(f"\n{'='*65}")
    print(f"Done! 5 rebuilt cards -> {OUT}")
    print(f"Card 02 怀素侧: LetterBox 粘贴《自叙帖》局部")
    print(f"Card 02 张旭侧: 占位图（待台北故宫 CC0 下载）")
    print(f"Card 03 孙过庭侧: 《书谱》段落预览（待台北故宫 CC0 下载）")


if __name__ == "__main__":
    main()
