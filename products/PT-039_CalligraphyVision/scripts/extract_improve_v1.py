"""改进PT-039辨析卡图片质量：提取局部特写"""
import os
from PIL import Image, ImageEnhance, ImageFilter

Image.MAX_IMAGE_PIXELS = None
WS = r"C:/Users/willi/.mavis/workspace"
os.makedirs(WS, exist_ok=True)

# ========== 1. 赵孟頫《洛神赋》局部特写 ==========
# 从洛神赋正文区提取一段行书局部（约10-20字）
# luoshen_body_full.jpg = 15125×3543 (正文区45-85%)
# 找一段清晰的行书区域：中部偏右（约50-60%宽度）
print("=== 赵孟頫《洛神赋》局部特写 ===")
luoshen_full = os.path.join(WS, "luoshen_body_full.jpg")
img_l = Image.open(luoshen_full)
w_l, h_l = img_l.size
print(f"洛神赋正文: {w_l}x{h_l}")

# 从正文区中部提取一个宽幅段落（约1/3宽，80%高）
# x: 20%-55% of body (0.20-0.55 of 15125 = 3025-8318)
# 保持宽幅，但有一定高度
x1 = int(w_l * 0.18)
x2 = int(w_l * 0.52)
y1 = int(h_l * 0.05)
y2 = int(h_l * 0.92)
crop_l = img_l.crop((x1, y1, x2, y2))
# 缩放到宽幅展示
crop_l_sm = crop_l.resize((1200, int(crop_l.height * 1200 / crop_l.width)), Image.LANCZOS)
# 增强对比度
crop_l_sm = ImageEnhance.Contrast(crop_l_sm).enhance(1.12)
crop_l_sm = ImageEnhance.Sharpness(crop_l_sm).enhance(1.15)
out_l = os.path.join(WS, "card03_zhaomengfu_detail.png")
crop_l_sm.save(out_l, quality=92)
print(f"赵孟頫局部特写: {crop_l.size} → {crop_l_sm.size} → {out_l}")
img_l.close()

# ========== 2. 颜真卿《祭侄稿》局部特写 ==========
# 从祭侄稿右卷提取情感最丰富的段落
# jizhi_right_sm.jpg = 2000×452 (右卷缩略)
# jizhi_body_full.jpg = 15125×3543
print("\n=== 颜真卿《祭侄稿》局部特写 ===")
jizhi_full = os.path.join(WS, "jizhi_body_full.jpg")
if os.path.exists(jizhi_full):
    img_j = Image.open(jizhi_full)
    w_j, h_j = img_j.size
    print(f"祭侄稿右卷正文: {w_j}x{h_j}")
    # 提取祭侄稿中段（约30-60%宽度，20-80%高度）
    # 这段包含"父陷子死巢倾卵覆"等情绪强烈的文字
    x1j = int(w_j * 0.25)
    x2j = int(w_j * 0.58)
    y1j = int(h_j * 0.10)
    y2j = int(h_j * 0.90)
    crop_j = img_j.crop((x1j, y1j, x2j, y2j))
    crop_j_sm = crop_j.resize((1200, int(crop_j.height * 1200 / crop_j.width)), Image.LANCZOS)
    crop_j_sm = ImageEnhance.Contrast(crop_j_sm).enhance(1.08)
    out_j = os.path.join(WS, "card04_yanzhengqing_detail.png")
    crop_j_sm.save(out_j, quality=92)
    print(f"颜真卿局部特写: {crop_j.size} → {crop_j_sm.size} → {out_j}")
    img_j.close()
else:
    print(f"  祭侄稿全图不存在，使用已有预览图")

# ========== 3. 九成宫醴泉铭（欧阳询）局部 ==========
# oc_p*.jpg 是九成宫醴泉铭的各页局部
# 选择最清晰的一页：oc_p5_full.jpg 或 oc_p6_full.jpg
print("\n=== 欧阳询《九成宫》局部 ===")
oc_pages = [os.path.join(WS, f"oc_p{i}_full.jpg") for i in range(2, 8)]
best_oc = None
best_score = 0
for p in oc_pages:
    if os.path.exists(p):
        img = Image.open(p)
        # 计算图像信息量（用边缘检测粗估）
        import numpy as np
        arr = np.array(img.convert('L'))
        # 计算像素方差（高对比度=高方差）
        score = arr.var()
        if score > best_score:
            best_score = score
            best_oc = p
        print(f"  {os.path.basename(p)}: variance={score:.0f}")
        img.close()

if best_oc:
    img_oc = Image.open(best_oc)
    # 选取中间列（去掉边缘）
    w_oc, h_oc = img_oc.size
    crop_oc = img_oc.crop((w_oc//6, 0, w_oc*5//6, h_oc))
    crop_oc_sm = crop_oc.resize((1100, int(crop_oc.height * 1100 / crop_oc.width)), Image.LANCZOS)
    crop_oc_sm = ImageEnhance.Contrast(crop_oc_sm).enhance(1.12)
    crop_oc_sm = ImageEnhance.Sharpness(crop_oc_sm).enhance(1.20)
    out_oc = os.path.join(WS, "card05_ouyang_detail.png")
    crop_oc_sm.save(out_oc, quality=92)
    print(f"欧阳询最佳局部: {os.path.basename(best_oc)} → {crop_oc_sm.size} → {out_oc}")
    img_oc.close()
else:
    print("  未找到九成宫页面图")

# ========== 4. 九成宫用于Card 04 ==========
# Card 04 欧阳询侧也用相同资源
oc4_pages = [os.path.join(WS, f"oc_p{i}_full.jpg") for i in range(1, 10)]
best_oc4 = None
best_score4 = 0
import numpy as np
for p in oc4_pages:
    if os.path.exists(p):
        img = Image.open(p)
        arr = np.array(img.convert('L'))
        score = arr.var()
        if score > best_score4:
            best_score4 = score
            best_oc4 = p
        img.close()

if best_oc4:
    img_oc4 = Image.open(best_oc4)
    w_oc4, h_oc4 = img_oc4.size
    crop_oc4 = img_oc4.crop((w_oc4//8, 0, w_oc4*7//8, h_oc4))
    crop_oc4_sm = crop_oc4.resize((1100, int(crop_oc4.height * 1100 / crop_oc4.width)), Image.LANCZOS)
    crop_oc4_sm = ImageEnhance.Contrast(crop_oc4_sm).enhance(1.12)
    crop_oc4_sm = ImageEnhance.Sharpness(crop_oc4_sm).enhance(1.20)
    out_oc4 = os.path.join(WS, "card04_ouyang_detail.png")
    crop_oc4_sm.save(out_oc4, quality=92)
    print(f"\nCard04 欧阳询局部: {os.path.basename(best_oc4)} → {crop_oc4_sm.size} → {out_oc4}")
    img_oc4.close()

print("\n=== 局部图提取完成 ===")
