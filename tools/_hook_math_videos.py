"""P-CGM.3.6: 给 math_kg_v1.2 加 video_links (挂数学 31 张母题视频)"""
import json
from pathlib import Path
from collections import defaultdict

kg_path = Path(r"D:\2_products\education\SPDT-004_EduContent\knowledge_graphs\math_kg_v1.2.json")
video_root = Path(r"D:\4_data\work\media\renders\数学_videos")

# 扫数学母题视频
video_map = defaultdict(list)  # pp_id -> [(filename, mother_problem)]
for f in video_root.glob("pp_*_video.mp4"):
    fname = f.name
    pp_id = f.stem.replace("_video", "")  # pp_016_video.mp4 → pp_016
    video_map[pp_id].append((fname, pp_id))

print(f"扫到 {sum(1 for v in video_map.values())} 张数学母题视频")
print(f"唯一 ID: {len(video_map)} 个")

# 加载 kg
g = json.loads(kg_path.read_text(encoding="utf-8"))

# 给每个概念挂 video_links
total_links = 0
for n in g["nodes"]:
    links = []
    for mp_id in n.get("mother_problems", []):
        if mp_id in video_map:
            for fn, real_id in video_map[mp_id]:
                links.append({
                    "subject": "数学",
                    "title": f"{real_id} 视频",
                    "filename": fn,
                    "mother_problem": real_id,
                })
    if links:
        n["video_links"] = links
        total_links += len(links)

# 保存
kg_path.write_text(json.dumps(g, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\n挂载完成. 概念数: {sum(1 for n in g['nodes'] if n.get('video_links'))}, 总视频链接: {total_links}")
for n in g["nodes"]:
    if n.get("video_links"):
        print(f"  {n['id']} ({n['name']}): {len(n['video_links'])} 个视频")