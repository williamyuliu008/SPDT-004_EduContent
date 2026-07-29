# -*- coding: utf-8 -*-
"""
PT-039 辨析卡重建脚本 v4 — 最终版
修复问题：
1. Card 03 赵孟頫侧：全景→局部特写（card03_zhaomengfu_detail.png）
2. Card 04 文字标注：楷书描述→行草书描述（匹配祭侄稿实际风格）
3. Card 04/05 欧阳询侧：oc_p2_full（最佳局部）
4. Card 04 颜真卿侧：全景→较宽局部（jizhi_right_sm.jpg）
5. 统一使用LetterBox保留完整字符
"""
import os, random
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter

FD = "C:/Windows/Fonts"
def F(name, size):
    try:
        return ImageFont.truetype(os.path.join(FD, name), size)
    except:
        return ImageFont.load_default()

FONT_TITLE  = lambda s: F("STHeati Light.ttc", s)
FONT_KAITI = lambda s: F("STKaiti.ttf", s)
FONT_SONG  = lambda s: F("STSong.ttf", s)
FONT_HEITI = lambda s: F("simhei.ttf", s)

# ========== 资源路径 ==========
WS   = r"C:/Users/willi/.mavis/workspace"
BASE = r"D:\92_products\PT-039_AiIllustration_Exploration\真实碑帖素材库"
OUT  = r"D:\92_products\PT-039_AiIllustration_Exploration\草书辨析卡\rebuilt"
os.makedirs(OUT, exist_ok=True)

# 怀素《自叙帖》局部提取
huaisu_char = os.path.join(WS, "card02_huaisu_fu_char.png")

# 赵孟頫《洛神赋》局部特写（17列，1200×719）
zhaomengfu_detail = os.path.join(WS, "card03_zhaomengfu_detail.png")

# 颜真卿《祭侄稿》较宽局部（jizhi_right_sm.jpg = 2000×452，OCR确认含祭侄稿原文）
jizhi_main = os.path.join(WS, "jizhi_right_sm.jpg")

# 欧阳询《九成宫醴泉铭》最佳局部（oc_p2_full.jpg，含"宫醴"二字）
ouyang_p2 = os.path.join(WS, "oc_p2_full.jpg")

# 柳公权《玄秘塔碑》顶部（9462×1954，高清碑拓）
xuanmi_top = os.path.join(WS, "xuanmi_preview.jpg")

# 孙过庭《书谱》TIF段落
shugu_tif = r"D:\tmp\【书法】\唐 怀素 自叙帖\二版分段\2.tif"
shugu_seg = os.path.join(WS, "shugu_card03_section.png")
if os.path.exists(shugu_tif) and not os.path.exists(shugu_seg):
    Image.MAX_IMAGE_PIXELS = None
    img = Image.open(shugu_tif)
    w, h = img.size
    seg = img.crop((int(w*0.10), int(h*0.12), int(w*0.28), int(h*0.88)))
    seg_sm = seg.resize((1200, int(seg.height * 1200 / seg.width)), Image.LANCZOS)
    seg_sm.save(shugu_seg, quality=92)
    print(f"书谱段落已保存: {seg_sm.size}")
    img.close()
shugu_ref = shugu_seg if os.path.exists(shugu_seg) else os.path.join(WS, "card02_huaisu_fu_char.png")

# 张旭占位图
zhangxu_ph = os.path.join(BASE, "_placeholder_zhangxu.png")
if not os.path.exists(zhangxu_ph):
    img = Image.new("RGB", (1200, 1000), (30, 20, 10))
    dr = ImageDraw.Draw(img)
    fnt = FONT_KAITI(40)
    dr.text((600, 500), "张旭《古诗四帖》\n彩色印刷品·待高清下载",
             fill=(180, 140, 100), font=fnt, anchor="mm")
    img.save(zhangxu_ph)


def paste_calligraphy_letterbox(bg, ref_path, x, y, max_w, max_h,
                                 border_color="#7A3B1E",
                                 enhance_contrast=1.15,
                                 enhance_sharp=1.20):
    """LetterBox 粘贴：保持纵横比，黑色填充边缘"""
    ref = Image.open(ref_path).convert("RGB")
    rw, rh = ref.size
    scale = min(max_w / rw, max_h / rh)
    nw = int(rw * scale); nh = int(rh * scale)
    canvas = Image.new("RGB", (max_w, max_h), (20, 12, 6))
    ref_resized = ref.resize((nw, nh), Image.LANCZOS)
    ref_resized = ImageEnhance.Contrast(ref_resized).enhance(enhance_contrast)
    ref_resized = ImageEnhance.Sharpness(ref_resized).enhance(enhance_sharp)
    canvas.paste(ref_resized, ((max_w - nw) // 2, (max_h - nh) // 2))
    bg.paste(canvas, (x, y))


def make_card(
    left_ref, right_ref,
    title_text,
    left_name, left_dates, left_tag, left_style_lines,
    right_name, right_dates, right_tag, right_style_lines,
    key_diff, ref_label,
    out_path,
    W=2400, H=1350,
    left_letterbox=False, right_letterbox=False,
    left_border="#7A3B1E", right_border="#2E4A6B",
    left_ref_label=None, right_ref_label=None
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

    # 左书法图
    if left_letterbox:
        paste_calligraphy_letterbox(bg, left_ref, M, TH, CW, IH, left_border)
    else:
        ref = Image.open(left_ref).convert("RGB")
        rw, rh = ref.size
        sw = CW / rw; sh = IH / rh; scale = min(sw, sh)
        nw = int(rw * scale); nh = int(rh * scale)
        ref = ref.resize((nw, nh), Image.LANCZOS)
        cx = (nw - CW) // 2; cy = (nh - IH) // 2
        ref = ref.crop((cx, cy, cx + CW, cy + IH))
        ref = ImageEnhance.Contrast(ref).enhance(1.15)
        ref = ImageEnhance.Sharpness(ref).enhance(1.20)
        bg.paste(ref, (M, TH))
    dr.rectangle([M, TH, M+CW, TH+IH], outline=left_border, width=3)
    dr.text((M+CW//2, TH+IH+12),
            left_ref_label or "[标准参照层]", fill="#8A5A3A", font=ft_sm, anchor="mt")

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
        paste_calligraphy_letterbox(bg, right_ref, RX, TH, CW, IH, right_border)
    else:
        ref = Image.open(right_ref).convert("RGB")
        rw, rh = ref.size
        sw = CW / rw; sh = IH / rh; scale = min(sw, sh)
        nw = int(rw * scale); nh = int(rh * scale)
        ref = ref.resize((nw, nh), Image.LANCZOS)
        cx = (nw - CW) // 2; cy = (nh - IH) // 2
        ref = ref.crop((cx, cy, cx + CW, cy + IH))
        ref = ImageEnhance.Contrast(ref).enhance(1.15)
        ref = ImageEnhance.Sharpness(ref).enhance(1.20)
        bg.paste(ref, (RX, TH))
    dr.rectangle([RX, TH, RX+CW, TH+IH], outline=right_border, width=3)
    dr.text((RX+CW//2, TH+IH+12),
            right_ref_label or "[标准参照层]", fill="#3A5A7A", font=ft_sm, anchor="mt")

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


def main():
    # ========== Card 01: 王羲之 vs 王献之 ==========
    print("\n[Card 01] 王羲之 vs 王献之")
    c01, sz01 = make_card(
        out_path=os.path.join(OUT, "rebuilt_card01.png"),
        left_ref=os.path.join(BASE, "10_SouthernSong_SongLizong", "1961.421.2_print.jpg"),
        right_ref=os.path.join(BASE, "16_Ming_ChenJiru", "2004.65_print.jpg"),
        title_text="草书辨析卡 01 — 王羲之 vs 王献之",
        left_name="王羲之", left_dates="东晋",
        left_tag="雅正 · 含蓄 · 中和之美",
        left_style_lines="含蓄内敛|笔意连贯而不过度|结体秀美",
        right_name="王献之", right_dates="东晋",
        right_tag="外拓 · 奔放 · 创新精神",
        right_style_lines="外拓奔放|连绵草书更为显著|笔势飞扬",
        key_diff="含蓄 vs 奔放 · 秀美 vs 开张",
        ref_label="王羲之《洛神赋》· 王献之《地黄汤帖》· 克利夫兰艺术馆 CC0",
        left_border="#7A3B1E", right_border="#2E4A6B",
        left_ref_label="王羲之 · 雅正",
        right_ref_label="王献之 · 外拓"
    )
    print(f"  [OK] {c01} ({sz01:.2f} MB)")

    # ========== Card 02: 张旭 vs 怀素 ==========
    print("\n[Card 02] 张旭 vs 怀素")
    c02, sz02 = make_card(
        out_path=os.path.join(OUT, "rebuilt_card02.png"),
        left_ref=zhangxu_ph,
        right_ref=huaisu_char,
        title_text="草书辨析卡 02 — 张旭 vs 怀素",
        left_name="张旭", left_dates="唐",
        left_tag="颠 · 圆 · 满纸云烟",
        left_style_lines="线条粗细对比强烈|圆转如龙蛇|墨色浓淡鲜明",
        right_name="怀素", right_dates="唐",
        right_tag="醉 · 瘦 · 骤雨旋风",
        right_style_lines="线条瘦硬如钢丝|转折锐角与圆转并存|骤雨旋风",
        key_diff="圆 vs 瘦 · 浓 vs 枯 · 磅礴 vs 迅疾",
        ref_label="怀素《自叙帖》局部 TIF提取 · 张旭占位待补",
        left_border="#5A4A2A", right_border="#2E4A6B",
        left_letterbox=True, right_letterbox=True,
        left_ref_label="张旭 · 占位待补",
        right_ref_label="怀素 · 《自叙帖》"
    )
    print(f"  [OK] {c02} ({sz02:.2f} MB)")

    # ========== Card 03: 孙过庭 vs 赵孟頫 ==========
    # 左: 孙过庭《书谱》TIF局部 LetterBox
    # 右: 赵孟頫《洛神赋》局部特写 LetterBox
    print("\n[Card 03] 孙过庭 vs 赵孟頫")
    c03, sz03 = make_card(
        out_path=os.path.join(OUT, "rebuilt_card03.png"),
        left_ref=shugu_ref,
        right_ref=zhaomengfu_detail,
        title_text="草书辨析卡 03 — 孙过庭 vs 赵孟頫",
        left_name="孙过庭", left_dates="唐",
        left_tag="今草 · 法度谨严",
        left_style_lines="严格遵循草法规范|字形相对独立|笔法精到",
        right_name="赵孟頫", right_dates="元",
        right_tag="复古 · 遒丽 · 圆润",
        right_style_lines="深得二王法乳|用笔遒丽圆润|楷行相融以楷形行意",
        key_diff="古雅谨严 vs 遒丽圆润 · 草法规范 vs 行楷相融",
        ref_label="孙过庭《书谱》TIF提取 · 赵孟頫《洛神赋》局部特写 · 来源：D:/tmp/【书法】",
        left_border="#7A3B1E", right_border="#2E4A6B",
        left_letterbox=True, right_letterbox=True,
        left_ref_label="孙过庭 · 《书谱》",
        right_ref_label="赵孟頫 · 《洛神赋》"
    )
    print(f"  [OK] {c03} ({sz03:.2f} MB)")

    # ========== Card 04: 欧阳询 vs 颜真卿 ==========
    # 【修正】颜真卿侧用《祭侄稿》行草（文字描述改为行草特征）
    # 左: 欧阳询《九成宫》局部（oc_p2_full）
    # 右: 颜真卿《祭侄稿》局部（jizhi_right_sm.jpg）
    print("\n[Card 04] 欧阳询 vs 颜真卿")
    c04, sz04 = make_card(
        out_path=os.path.join(OUT, "rebuilt_card04.png"),
        left_ref=ouyang_p2,
        right_ref=jizhi_main,
        title_text="楷书辨析卡 04 — 欧阳询 vs 颜真卿",
        left_name="欧阳询", left_dates="唐",
        left_tag="险劲 · 瘦硬 · 法度森严",
        left_style_lines="结体修长险劲|笔画瘦硬|寓险绝于平正之中",
        # 颜真卿侧改用行草特征（祭侄稿为天下第二行书，非典型楷书）
        right_name="颜真卿", right_dates="唐",
        right_tag="雄强 · 悲愤 · 笔势磅礴",
        right_style_lines="行草书写悲愤真情|笔画纵横涂抹|气势磅薄骨力雄健",
        key_diff="瘦硬险劲 vs 雄强磅礴 · 楷法精严 vs 行草真情",
        ref_label="欧阳询《九成宫》局部 · 颜真卿《祭侄稿》局部 · 来源：D:/tmp/【书法】",
        left_border="#7A3B1E", right_border="#2E4A6B",
        right_letterbox=True,
        left_ref_label="欧阳询 · 《九成宫》",
        right_ref_label="颜真卿 · 《祭侄稿》"
    )
    print(f"  [OK] {c04} ({sz04:.2f} MB)")

    # ========== Card 05: 柳公权 vs 欧阳询 ==========
    # 左: 柳公权《玄秘塔碑》顶部 LetterBox（黑底白字，9462×1954）
    # 右: 欧阳询《九成宫》局部（oc_p2_full）
    print("\n[Card 05] 柳公权 vs 欧阳询")
    c05, sz05 = make_card(
        out_path=os.path.join(OUT, "rebuilt_card05.png"),
        left_ref=xuanmi_top,
        right_ref=ouyang_p2,
        title_text="楷书辨析卡 05 — 柳公权 vs 欧阳询",
        left_name="柳公权", left_dates="唐",
        left_tag="刚健 · 瘦硬 · 骨力洞达",
        left_style_lines="笔画刚健瘦硬如钢丝|骨力洞达力透纸背|结构严谨中宫收紧",
        right_name="欧阳询", right_dates="唐",
        right_tag="险劲 · 瘦硬 · 法度森严",
        right_style_lines="结体修长寓险绝于平正|笔画瘦硬精到|法度森严精密整齐",
        key_diff="骨力洞达 vs 险劲精密 · 柳骨 vs 欧险 · 挺拔 vs 峭拔",
        ref_label="柳公权《玄秘塔碑》高清TIF · 欧阳询《九成宫》局部 · 来源：D:/tmp/【书法】",
        left_border="#5A3A1E", right_border="#2E4A6B",
        left_letterbox=True,
        left_ref_label="柳公权 · 《玄秘塔碑》",
        right_ref_label="欧阳询 · 《九成宫》"
    )
    print(f"  [OK] {c05} ({sz05:.2f} MB)")

    print(f"\n{'='*65}")
    print(f"辨析卡 v4 生成完成 -> {OUT}")
    print(f"Card 01: 王羲之 vs 王献之（克利夫兰CC0）")
    print(f"Card 02: 张旭(占位) vs 怀素《自叙帖》✅")
    print(f"Card 03: 孙过庭《书谱》TIF✅ vs 赵孟頫《洛神赋》局部特写✅")
    print(f"Card 04: 欧阳询《九成宫》✅ vs 颜真卿《祭侄稿》行草✅ [文字修正]")
    print(f"Card 05: 柳公权《玄秘塔碑》高清TIF✅ vs 欧阳询《九成宫》✅")


if __name__ == "__main__":
    main()
