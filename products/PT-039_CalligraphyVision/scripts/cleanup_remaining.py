import os, shutil

ws = r"C:\Users\willi\.mavis\workspace"
dest = r"D:\4_data\content\calligraphy_cards"

def safe_move(src_path, dst_path):
    if os.path.exists(dst_path):
        base, ext = os.path.splitext(os.path.basename(dst_path))
        counter = 1
        while os.path.exists(dst_path):
            dst_path = os.path.join(os.path.dirname(dst_path), f"{base}_{counter}{ext}")
            counter += 1
    shutil.move(src_path, dst_path)
    return dst_path

# ep09_frames
for f in os.listdir(os.path.join(ws, "ep09_frames")):
    src = os.path.join(ws, "ep09_frames", f)
    dst = os.path.join(dest, "ep09_frames", f)
    safe_move(src, dst)
    print(f"moved: ep09_frames/{f}")

# pt039_cards (rename to avoid rebuilt_card conflict)
for f in os.listdir(os.path.join(ws, "pt039_cards")):
    src = os.path.join(ws, "pt039_cards", f)
    dst = os.path.join(dest, "pt039_cards", f"pt039_{f}")
    safe_move(src, dst)
    print(f"moved: pt039_cards/pt039_{f}")

# .hvigor/build.log (delete)
hvigor_log = os.path.join(ws, ".hvigor", "outputs", "build-logs", "build.log")
if os.path.exists(hvigor_log):
    os.remove(hvigor_log)
    print("deleted: .hvigor build.log")

# Report what's left
remaining = []
for item in os.listdir(ws):
    p = os.path.join(ws, item)
    if os.path.isdir(p):
        count = len(os.listdir(p))
        remaining.append(f"[DIR] {item}/ ({count} items)")
    else:
        remaining.append(f"[FILE] {item}")

print(f"\nWorkspace 剩余 {len(remaining)} 项:")
for r in remaining:
    print(" ", r)
