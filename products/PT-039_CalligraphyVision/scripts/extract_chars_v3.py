"""从三大高清碑帖提取辨析卡字符"""
import sys, os
from PIL import Image, ImageEnhance, ImageFilter
sys.stdout.reconfigure(encoding='utf-8')
Image.MAX_IMAGE_PIXELS = None

OUT = r"C:/Users/willi/.mavis/workspace"
os.makedirs(OUT, exist_ok=True)

# ========== 1. 颜真卿《祭侄稿》右：提取「賊」字 ==========
# 祭侄稿右文件(29528×3343)正文在x=7600-8200, y=1400-1900
# 取更宽区域确保完整，旋转90度(LetterBox风格)
fp_yzq = r'D:/tmp/【书法】/颜真卿 祭侄稿/颜真卿 祭侄稿 右　250.tif'
img_yzq = Image.open(fp_yzq)
w_yzq, h_yzq = img_yzq.size
print(f"祭侄稿右: {w_yzq}x{h_yzq}")

# 提取「賊」字区域
x1, x2 = 7000, 8600
y1, y2 = 900, 2300
crop = img_yzq.crop((x1, y1, x2, y2))
crop_yzq = crop.resize((700, int(crop.height * 700 / crop.width)), Image.LANCZOS)
out_yzq = os.path.join(OUT, "card04_yanzhengqing_zei.png")
crop_yzq.save(out_yzq, quality=92)
print(f"颜真卿「賊」: {crop.size}→{crop_yzq.size} → {out_yzq}")

# 提取「原」字区域(稍左)
x1b, x2b = 10500, 12500
y1b, y2b = 0, 1000
crop_b = img_yzq.crop((x1b, y1b, x2b, y2b))
crop_yzq2 = crop_b.resize((700, int(crop_b.height * 700 / crop_b.width)), Image.LANCZOS)
out_yzq2 = os.path.join(OUT, "card04_yanzhengqing_yuan.png")
crop_yzq2.save(out_yzq2, quality=92)
print(f"颜真卿「原」: {crop_b.size}→{crop_yzq2.size} → {out_yzq2}")

# ========== 2. 赵孟頫《洛神赋》：提取「神」字 ==========
# 洛神赋正文区(37812×3543)45-85%范围: x=17015-32140, 全文高3543
# 从已保存的luoshen_body_full.jpg(15125×3543)读取
# OCR在2000px宽图上的坐标[743,169,876,182]是原比例
# 原37812px / 2000px ≈ 18.906 scale
# x_in_body = 17015 + box*18.906
fp_ls = r'D:/tmp/【书法】/元 赵孟頫 行书洛神赋卷/元 赵孟頫 行书洛神赋卷 纸本29x220.9cm.tif'
img_ls = Image.open(fp_ls)
if img_ls.mode == 'CMYK':
    img_ls = img_ls.convert('RGB')
w_ls, h_ls = img_ls.size
print(f"洛神赋: {w_ls}x{h_ls}")

# OCR坐标 (2000px宽参照): y1=169, x1=743, y2=182, x2=876
scale_ocr = w_ls / 2000.0  # = 18.906
body_x0 = int(w_ls * 0.45)  # 17015
body_y0 = 0

x1_ls = body_x0 + int(743 * scale_ocr)   # 约 21504
x2_ls = body_x0 + int(876 * scale_ocr)   # 约 22604
y1_ls = body_y0 + int(169 * scale_ocr)  # 约 3193
y2_ls = body_y0 + int(182 * scale_ocr)  # 约 3440

# 扩padding
pad_ls = int(500 * scale_ocr)  # 约9435原 px
x1_ls = max(0, x1_ls - pad_ls)
x2_ls = min(w_ls, x2_ls + pad_ls)
y1_ls = max(0, y1_ls - pad_ls)
y2_ls = min(h_ls, y2_ls + pad_ls)

crop_ls = img_ls.crop((x1_ls, y1_ls, x2_ls, y2_ls))
# 缩放到合理尺寸
scale_ls_fit = 700 / (x2_ls - x1_ls)
crop_ls_sm = crop_ls.resize((700, int(crop_ls.size[1] * scale_ls_fit)), Image.LANCZOS)
out_ls = os.path.join(OUT, "card03_zhaomengfu_shen.png")
crop_ls_sm.save(out_ls, quality=92)
print(f"赵孟頫「神」: 原始{crop_ls.size}→{crop_ls_sm.size} → {out_ls}")

# ========== 3. 柳公权《玄秘塔碑》：提取「大」字 ==========
# xuanmi_preview.jpg是9462×1953(顶部10%)：字在x=6630-6950,y=420-680
fp_liu = r'D:/tmp/【书法】/唐 柳公权 玄秘塔碑/唐 柳公权 玄秘塔碑165x80.tif'
img_liu = Image.open(fp_liu)
w_liu, h_liu = img_liu.size
print(f"玄秘塔碑: {w_liu}x{h_liu}")

# 「大」字: x=6400-7100, y=300-700
x1_l, x2_l = 6000, 7300
y1_l, y2_l = 200, 800
pad_l = 200
crop_l = img_liu.crop((x1_l-pad_l, y1_l-pad_l, x2_l+pad_l, y2_l+pad_l))
# 旋转90度以LetterBox方式展示（竖幅→横宽）
crop_l_rot = crop_l.rotate(90, expand=True, fillcolor='black')
# 灰度+高对比（黑底白字）
gs = crop_l_rot.convert('L')
gs = ImageEnhance.Contrast(gs).enhance(2.2)
gs = gs.filter(ImageFilter.SHARPEN)
crop_l_fin = gs.convert('RGB')

out_liu = os.path.join(OUT, "card05_liugongquan_da.png")
crop_l_fin.save(out_liu, quality=92)
print(f"柳公权「大」: {crop_l.size}→旋转后{crop_l_rot.size} → {out_liu}")

print("\n=== 全部提取完成 ===")
print("请用images_understand验证各字符图清晰度")
