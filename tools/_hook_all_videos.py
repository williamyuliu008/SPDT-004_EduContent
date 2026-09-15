"""P-CGM.3.5: 自动挂 5 学科 40 张母题视频 → multi_subject_kg_v1.0 概念节点"""
import json
from pathlib import Path
from collections import defaultdict

kg_path = Path(r"D:\2_products\education\SPDT-004_EduContent\knowledge_graphs\multi_subject_kg_v1.0.json")
video_root = Path(r"D:\4_data\work\media\renders")

# 学科映射
SUBJECT_MAP = {
    "语文": ("ch", "C"),
    "英语": ("en", "E"),
    "地理": ("geo", "G"),
    "政治": ("pol", "P"),
    "书法": ("cal", "F"),
}

# 扫所有母题视频
video_map = defaultdict(list)  # pp_id -> [(subject, filename)]
for subj_dir in video_root.glob("*_videos"):
    if not subj_dir.is_dir():
        continue
    subj_name = subj_dir.name.replace("_videos", "")
    if subj_name == "history":
        continue  # 历史 K 卡单独处理
    if subj_name not in SUBJECT_MAP:
        continue
    for f in subj_dir.glob("*_video.mp4"):
        pp_id = f.stem.replace("_video", "")  # ch_001_video.mp4 → ch_001
        video_map[pp_id] = (subj_name, f.name)

print(f"扫到 {sum(1 for v in video_map.values())} 张母题视频")

# 加载 kg
g = json.loads(kg_path.read_text(encoding="utf-8"))

# 给每个概念挂 video_links
for n in g["nodes"]:
    links = []
    for mp_id in n.get("mother_problems", []):
        if mp_id in video_map:
            subj, fn = video_map[mp_id]
            links.append({
                "subject": subj,
                "title": f"{mp_id} 视频",
                "filename": fn,
                "mother_problem": mp_id,
            })
    if links:
        n["video_links"] = links

# 保存
kg_path.write_text(json.dumps(g, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"挂载完成. 有视频概念数: {sum(1 for n in g['nodes'] if n.get('video_links'))}")
for n in g["nodes"]:
    if n.get("video_links"):
        print(f"  {n['id']} ({n['subject']} {n['name']}): {len(n['video_links'])} 个")