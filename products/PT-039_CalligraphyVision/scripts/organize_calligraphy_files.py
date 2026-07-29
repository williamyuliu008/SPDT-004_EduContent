import os, shutil

src = r"C:\Users\willi\.mavis\workspace"
dest_root = r"D:\4_data\content\calligraphy_cards"

# 预定义的目录映射
dirs = {
    "cards":         dest_root + "\\cards",
    "extracted_chars": dest_root + "\\extracted_chars",
    "oc9_cheng":     dest_root + "\\oc9_cheng",
    "shupu":         dest_root + "\\shupu",
    "zx_gushisici":  dest_root + "\\zx_gushisici",
    "huaisu_zixu":   dest_root + "\\huaisu_zixu",
    "scripts":       dest_root + "\\scripts",
    "misc":          dest_root + "\\misc",
}

def move(src_file, category):
    src_path = os.path.join(src, src_file)
    if not os.path.exists(src_path):
        return False
    dst_dir = dirs[category]
    dst_path = os.path.join(dst_dir, src_file)
    # 处理重名：加序号
    if os.path.exists(dst_path):
        base, ext = os.path.splitext(src_file)
        counter = 1
        while os.path.exists(dst_path):
            dst_path = os.path.join(dst_dir, f"{base}_{counter}{ext}")
            counter += 1
    shutil.move(src_path, dst_path)
    return True

skipped = []

# --- cards ---
for f in os.listdir(src):
    if f.startswith("rebuilt_card") or f.startswith("existing_card") or f.startswith("card_0"):
        if not move(f, "cards"):
            skipped.append(f)

# --- extracted_chars: jizhi / luoshen / zanzhengqing / shen 等局部特写 ---
for f in os.listdir(src):
    if any(x in f for x in ["jizhi", "luoshen", "lanting", "ming_zhu", "qing_tiebao",
                              "ref_", "card01_", "card02_", "card03_", "card04_", "card05_",
                              "card03_zanzhengqing", "card03_zhaomengfu", "card04_yanzhengqing",
                              "card04_ouyang_detail", "card05_", "xuanmi_preview",
                              "pt039_ep09"]):
        if not move(f, "extracted_chars"):
            skipped.append(f)

# --- oc9_cheng ---
for f in os.listdir(src):
    if f.startswith("oc_") and os.path.exists(os.path.join(src, f)):
        if not move(f, "oc9_cheng"):
            skipped.append(f)

# --- shupu ---
for f in os.listdir(src):
    if "shupu" in f or "shugu" in f or "seg1" in f or "seg2" in f or "seg3" in f:
        if not move(f, "shupu"):
            skipped.append(f)

# --- zx_gushisici ---
for f in os.listdir(src):
    if f.startswith("zx") or "zhangxu" in f or "古诗四帖" in f:
        if not move(f, "zx_gushisici"):
            skipped.append(f)

# --- huaisu_zixu ---
for f in os.listdir(src):
    if "huaisu" in f or "怀素" in f or f.startswith("s1") or f.startswith("s2") or f.startswith("s3") or f.startswith("s4") or f.startswith("s5"):
        if not move(f, "huaisu_zixu"):
            skipped.append(f)

# --- scripts ---
for f in os.listdir(src):
    if f.endswith(".py"):
        if not move(f, "scripts"):
            skipped.append(f)

# --- 扫描图中间件 ---
for f in os.listdir(src):
    if any(x in f for x in ["scan_", "_sm.", "_prev.", "_hi.", "_raw.", "_full.", "_seg", "_edge", "_body", "_left", "_right", "_top"]):
        if not move(f, "shupu"):
            if not move(f, "zx_gushisici"):
                if not move(f, "misc"):
                    skipped.append(f)

# --- misc ---
for f in os.listdir(src):
    if os.path.isfile(os.path.join(src, f)):
        if not move(f, "misc"):
            skipped.append(f)

print("=== 迁移完成 ===")
for d, count in [
    ("cards", len(os.listdir(dirs["cards"]))),
    ("extracted_chars", len(os.listdir(dirs["extracted_chars"]))),
    ("oc9_cheng", len(os.listdir(dirs["oc9_cheng"]))),
    ("shupu", len(os.listdir(dirs["shupu"]))),
    ("zx_gushisici", len(os.listdir(dirs["zx_gushisici"]))),
    ("huaisu_zixu", len(os.listdir(dirs["huaisu_zixu"]))),
    ("scripts", len(os.listdir(dirs["scripts"]))),
    ("misc", len(os.listdir(dirs["misc"]))),
]:
    print(f"  {d}: {count} files")

remaining = os.listdir(src)
print(f"\nWorkspace 剩余文件: {len(remaining)}")
if remaining:
    print("  未移动:", remaining[:20])

if skipped:
    print(f"\n跳过: {skipped}")
