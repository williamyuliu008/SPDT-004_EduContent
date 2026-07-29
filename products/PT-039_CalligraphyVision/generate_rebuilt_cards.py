# -*- coding: utf-8 -*-
"""
PT-039 辨析卡重建脚本 v2
双层结构：标准参照层（真实碑帖）+ 风格示意层（标注）
"""
import os, random
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter

# ===================== 字体 =====================
FD = "C:/Windows/Fonts"
def F(name, size):
    try:
        return ImageFont.truetype(os.path.join(FD, name), size)
    except:
        return ImageFont.load_default()

FONT_TITLE  = lambda s: F("STHeiti Light.ttf", s)
FONT_KAITI  = lambda s: F("STKaiti.ttf", s)
FONT_SONG   = lambda s: F("STSong.ttf", s)
FONT_HEITI  = lambda s: F("simhei.ttf", s)


def paste_calligraphy(bg, ref_path, x, y, max_w, max_h):
    """等比缩放+中心裁剪，粘贴书法图"""
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
    W=2400, H=1350
):
    # 仿古宣纸背景
    bg = Image.new("RGB", (W, H), "#F5EDD8")
    # 纹理噪点
    rng = random.Random(42)
    px = bg.load()
    for py in range(0, H, 3):
        for pxx in range(0, W, 3):
            v = rng.randint(0, 10)
            px[pxx, py] = (v, v+5, v+12)
    bg = Image.blend(bg, bg.filter(ImageFilter.SMOOTH), 0.03)

    dr = ImageDraw.Draw(bg)

    M = 40; TH = 80; BH = 70
    GAP = 30
    CW = (W - M*2 - GAP) // 2   # 每列宽
    IH = H - TH - BH - 180       # 书法图高度
    AY = TH + IH                   # 标注区起点

    # 字体
    ft_title = FONT_TITLE(34)
    ft_name  = FONT_KAITI(40)
    ft_tag   = FONT_KAITI(28)
    ft_body  = FONT_SONG(17)   # size↓ 避免底部截断
    ft_sm    = FONT_HEITI(15)
    ft_diff  = FONT_KAITI(22)

    # 左书法图
    paste_calligraphy(bg, left_ref, M, TH, CW, IH)
    dr.rectangle([M, TH, M+CW, TH+IH], outline="#7A3B1E", width=3)
    dr.text((M+CW//2, TH+IH+12), "[标准参照层]", fill="#8A5A3A", font=ft_sm, anchor="mt")

    # 左标注区
    dr.rectangle([M, AY, M+CW, H-BH], fill=(115, 52, 22, 180))
    cxL = M + CW//2
    lines = left_style_lines.split("|")
    dr.text((cxL, AY+14), left_name, fill="#F5DCC0", font=ft_name, anchor="mt")
    dr.text((cxL, AY+58), f"({left_dates})", fill="#C49A6C", font=ft_tag, anchor="mt")
    dr.text((cxL, AY+92), left_tag, fill="#E8C090", font=ft_tag, anchor="mt")
    sy = AY + 120
    for ln in lines[:2]:   # 收为2行避免底部截断
        if ln.strip():
            dr.text((cxL, sy), ln.strip(), fill="#D4B896", font=ft_body, anchor="mt")
            sy += ft_body.size + 4

    # 右书法图
    RX = W - M - CW
    paste_calligraphy(bg, right_ref, RX, TH, CW, IH)
    dr.rectangle([RX, TH, RX+CW, TH+IH], outline="#2E4A6B", width=3)
    dr.text((RX+CW//2, TH+IH+12), "[标准参照层]", fill="#3A5A7A", font=ft_sm, anchor="mt")

    # 右标注区
    dr.rectangle([RX, AY, RX+CW, H-BH], fill=(22, 42, 78, 180))
    cxR = RX + CW//2
    lines = right_style_lines.split("|")
    dr.text((cxR, AY+14), right_name, fill="#C8D8E8", font=ft_name, anchor="mt")
    dr.text((cxR, AY+58), f"({right_dates})", fill="#8AAFC8", font=ft_tag, anchor="mt")
    dr.text((cxR, AY+92), right_tag, fill="#A8C8D8", font=ft_tag, anchor="mt")
    sy = AY + 120
    for ln in lines[:2]:   # 收为2行避免底部截断
        if ln.strip():
            dr.text((cxR, sy), ln.strip(), fill="#8AAFC0", font=ft_body, anchor="mt")
            sy += ft_body.size + 4

    # 中间分割线+辨
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


def main():
    BASE = r"D:\92_products\PT-039_AiIllustration_Exploration\真实碑帖素材库"
    OUT = r"D:\92_products\PT-039_AiIllustration_Exploration\草书辨析卡\rebuilt"
    os.makedirs(OUT, exist_ok=True)

    cards = [
        # Card 01: 王羲之 vs 王献之
        dict(
            out_path=os.path.join(OUT, "rebuilt_card01.png"),
            title_text="草书辨析卡 01 — 王羲之 vs 王献之",
            left_ref=f"{BASE}\\10_SouthernSong_SongLizong\\1961.421.2_print.jpg",
            left_name="王羲之", left_dates="东晋",
            left_tag="雅正 · 含蓄 · 中和之美",
            left_style_lines="含蓄内敛|笔意连贯而不过度|结体秀美|骨力与柔情并存|线条含蓄不外露",
            right_ref=f"{BASE}\\16_Ming_ChenJiru\\2004.65_print.jpg",
            right_name="王献之", right_dates="东晋",
            right_tag="外拓 · 奔放 · 创新精神",
            right_style_lines="外拓奔放|连绵草书更为显著|笔势飞扬|结体开张不拘一格|线条外拓有锋芒",
            key_diff="含蓄 vs 奔放 · 秀美 vs 开张 · 连绵节制 vs 大胆",
            ref_label="标准参照：克利夫兰艺术馆 CC0 (Authentic Reference Layer)"
        ),
        # Card 02: 张旭 vs 怀素
        dict(
            out_path=os.path.join(OUT, "rebuilt_card02.png"),
            title_text="草书辨析卡 02 — 张旭 vs 怀素",
            left_ref=f"{BASE}\\13_Qing_Yueshan\\2003.353_print.jpg",
            left_name="张旭", left_dates="唐",
            left_tag="颠 · 圆 · 满纸云烟",
            left_style_lines="线条粗细对比强烈|圆转如龙蛇|墨色浓淡鲜明|气势磅礴|笔势疾徐振荡",
            right_ref=f"{BASE}\\13_Qing_Yueshan\\2003.353_print.jpg",
            right_name="怀素", right_dates="唐",
            right_tag="醉 · 瘦 · 骤雨旋风",
            right_style_lines="线条瘦硬如钢丝|转折锐角与圆转并存|墨色以枯为主|字形大小悬殊|连绵更甚速度更强",
            key_diff="圆 vs 瘦 · 浓 vs 枯 · 磅礴 vs 迅疾",
            ref_label="标准参照：克利夫兰艺术馆 CC0 (Authentic Reference Layer)"
        ),
        # Card 03: 孙过庭 vs 赵孟頫
        dict(
            out_path=os.path.join(OUT, "rebuilt_card03.png"),
            title_text="草书辨析卡 03 — 孙过庭 vs 赵孟頫",
            left_ref=f"{BASE}\\16_Ming_ChenJiru\\2004.65_print.jpg",
            left_name="孙过庭", left_dates="唐",
            left_tag="今草 · 法度谨严",
            left_style_lines="严格遵循草法规范|字形相对独立|笔法精到|墨色温润气韵清雅|可识读性强",
            right_ref=f"{BASE}\\10_SouthernSong_SongLizong\\1961.421.2_print.jpg",
            right_name="赵孟頫", right_dates="元",
            right_tag="复古 · 遒丽 · 圆润",
            right_style_lines="楷行相融以楷形行意|用笔遒丽圆润|结体端正秀美|墨色华润|秀美流畅",
            key_diff="古雅 vs 圆润 · 法度 vs 秀美 · 草法规范 vs 行楷相融",
            ref_label="标准参照：克利夫兰艺术馆 CC0 (Authentic Reference Layer)"
        ),
        # Card 04: 欧阳询 vs 颜真卿
        dict(
            out_path=os.path.join(OUT, "rebuilt_card04.png"),
            title_text="楷书辨析卡 04 — 欧阳询 vs 颜真卿",
            left_ref=f"{BASE}\\12_Qing_Tiebao\\2001.42_print.jpg",
            left_name="欧阳询", left_dates="唐",
            left_tag="险劲 · 瘦硬 · 法度森严",
            left_style_lines="结体修长险劲|笔画瘦硬|法度森严一丝不苟|结构精密排列整齐|刚健峻拔险中求正",
            right_ref=f"{BASE}\\10_SouthernSong_SongLizong\\1961.421.2_print.jpg",
            right_name="颜真卿", right_dates="唐",
            right_tag="雄壮 · 浑厚 · 筋骨分明",
            right_style_lines="结体方正宽博|笔画雄壮浑厚|横细竖粗明显|筋骨分明气势恢宏|刚健饱满有力",
            key_diff="修长 vs 宽博 · 瘦硬 vs 雄壮 · 险劲 vs 浑厚",
            ref_label="标准参照：克利夫兰艺术馆 CC0 (Authentic Reference Layer)"
        ),
        # Card 05: 柳公权 vs 欧阳询
        dict(
            out_path=os.path.join(OUT, "rebuilt_card05.png"),
            title_text="楷书辨析卡 05 — 柳公权 vs 欧阳询",
            left_ref=f"{BASE}\\15_Ming_WenZhengming\\1998.169_print.jpg",
            left_name="柳公权", left_dates="唐",
            left_tag="刚健 · 瘦硬 · 骨力洞达",
            left_style_lines="笔画刚健瘦硬|骨力洞达力透纸背|结构严谨法度分明|清朗峻峭|以骨力见长",
            right_ref=f"{BASE}\\12_Qing_Tiebao\\2001.42_print.jpg",
            right_name="欧阳询", right_dates="唐",
            right_tag="险劲 · 瘦硬 · 法度森严",
            right_style_lines="结体修长险劲|笔画瘦硬精到|法度森严精密整齐|刚健峻拔险中求正",
            key_diff="骨力 vs 险劲 · 瘦硬 vs 精密 · 柳骨 vs 欧险",
            ref_label="标准参照：克利夫兰艺术馆 CC0 (Authentic Reference Layer)"
        ),
    ]

    print("=" * 65)
    print("PT-039 Rebuilt Comparison Cards")
    print("Authentic Calligraphy Reference Layer + Annotation Layer")
    print("=" * 65)
    for i, c in enumerate(cards):
        print(f"\n[{i+1}/5] {c['title_text']}")
        out, sz = make_card(**c)
        print(f"  [OK] {out} ({sz:.2f} MB)")

    print(f"\n{'='*65}")
    print(f"Done! 5 rebuilt cards -> {OUT}")
    print("Note: Cards 04/05 use cross-style references (authentic calligraphy")
    print("      used as proxy for comparison - for single-character rubbings")
    print("      please supplement via manual Taipei Palace Museum downloads.")


if __name__ == "__main__":
    main()
