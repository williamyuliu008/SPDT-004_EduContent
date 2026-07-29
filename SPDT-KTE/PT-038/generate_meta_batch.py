# -*- coding: utf-8 -*-
"""生成 ep01/ep02/ep03/ep05/ep06 的 metadata.json"""
import sys, json, os
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

EPISODES = [
    (1, "峄山碑前", "李斯·小篆的秩序与第一道名字"),
    (2, "永和九年那场雨", "王羲之·兰亭序与书法的觉醒"),
    (3, "黄州突围", "苏轼·寒食帖与书法的生命维度"),
    (5, "颠张醉素", "张旭怀素·草书的极限与癫狂"),
    (6, "安史之乱", "颜真卿·忠烈之书与大唐的至暗时刻"),
]

BASE = r"D:\92_products\SPDT-004_EduContent\PT-038_TextExperience"

for ep_num, title, subtitle in EPISODES:
    ep_dir = os.path.join(BASE, f"墨骨山河_ep{ep_num:02d}_test")
    scenes_dir = os.path.join(ep_dir, "scenes")
    manifest_path = os.path.join(scenes_dir, "manifest.json")
    meta_path = os.path.join(ep_dir, "metadata.json")

    if not os.path.exists(manifest_path):
        print(f"SKIP ep{ep_num:02d}: manifest not found")
        continue

    with open(manifest_path, encoding="utf-8") as f:
        manifest = json.load(f)

    timeline = []
    current_time = 0.0

    for i, scene_meta in enumerate(manifest.get("scenes", [])):
        sid = scene_meta.get("scene_id", "")
        scene_file = os.path.join(scenes_dir, f"{sid}.json") if sid else None
        full_scene = {}
        if scene_file and os.path.exists(scene_file):
            with open(scene_file, encoding="utf-8") as f:
                full_scene = json.load(f)

        scene_title = scene_meta.get("title", full_scene.get("content", {}).get("title", ""))
        if len(scene_title) > 50:
            scene_title = scene_title[:50] + "..."

        five_sk = full_scene.get("five_skandha", {})
        color_base = five_sk.get("color_base", scene_meta.get("source_knowledge_nodes", [])[:4])
        if not color_base:
            color_base = scene_meta.get("source_knowledge_nodes", ["#书法"])[:4]
        recognition = five_sk.get("recognition_marker") or (scene_meta.get("source_knowledge_nodes") or ["#书法"])[0]

        dur = scene_meta.get("duration_s") or full_scene.get("scene_info", {}).get("dur") or 30.0

        timeline.append({
            "idx": i,
            "time": round(current_time, 1),
            "scene_name": scene_title,
            "scene_type": full_scene.get("scene_type", scene_meta.get("scene_type", "concept")),
            "chain_ref": f"墨骨山河_ep{ep_num:02d}",
            "five_skandha": {
                "color_base": color_base[:4] if color_base else [],
                "action_prompt": five_sk.get("action_prompt", "口述/复述"),
                "recognition_marker": recognition,
            }
        })
        current_time += max(5.0, min(60.0, dur))

    metadata = {
        "schema_version": "1.0.0",
        "package_id": f"墨骨山河_EP{ep_num:02d}",
        "series_title": "墨骨山河",
        "total_episodes": 1,
        "produced_by": "PT-VFX",
        "produced_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00"),
        "episodes": [{
            "ep": ep_num,
            "title": title,
            "subtitle": subtitle,
            "video_file": f"墨骨山河_ep{ep_num:02d}_pipeline.mp4",
            "duration_seconds": round(current_time, 1),
            "resolution": "1080p",
            "bitrate_kbps": 2000,
            "chains": [f"墨骨山河_ep{ep_num:02d}"],
            "scene_timeline": timeline
        }]
    }

    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    print(f"OK ep{ep_num:02d}: {meta_path}")

print("Done")
