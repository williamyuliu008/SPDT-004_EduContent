# -*- coding: utf-8 -*-
"""Generate metadata.json for ep08 (许慎·说文解字)"""
import json, os
from datetime import datetime

scenes_dir = r"D:\92_products\SPDT-004_EduContent\PT-038_TextExperience\墨骨山河_ep08_test\scenes"
manifest_path = os.path.join(scenes_dir, "manifest.json")

with open(manifest_path, encoding='utf-8') as f:
    manifest = json.load(f)

scenes = manifest['scenes']
timeline = []
current_time = 0.0

for i, scene_meta in enumerate(scenes):
    sid = scene_meta['scene_id']
    scene_file_path = os.path.join(scenes_dir, f"{sid}.json")
    full_scene = {}
    if os.path.exists(scene_file_path):
        with open(scene_file_path, encoding='utf-8') as f:
            full_scene = json.load(f)

    title = scene_meta.get('title', full_scene.get('content', {}).get('title', ''))
    if len(title) > 50:
        title = title[:50] + '...'
    
    five_sk = full_scene.get('five_skandha', {})
    color_base = five_sk.get('color_base', scene_meta.get('source_knowledge_nodes', ['#古汉语/说文解字'])[:4])
    recognition = five_sk.get('recognition_marker') or (scene_meta.get('source_knowledge_nodes') or ['#古汉语/说文解字'])[0]

    entry = {
        "idx": i,
        "time": round(current_time, 1),
        "scene_name": title,
        "scene_type": full_scene.get('scene_type', scene_meta.get('scene_type', 'concept')),
        "chain_ref": "墨骨山河_ep08",
        "five_skandha": {
            "color_base": color_base[:4] if color_base else [],
            "action_prompt": five_sk.get('action_prompt', '口述/复述'),
            "recognition_marker": recognition
        }
    }
    timeline.append(entry)
    current_time += 30.0

total_duration = current_time

metadata = {
    "schema_version": "1.0.0",
    "package_id": "墨骨山河_EP08",
    "series_title": "墨骨山河",
    "total_episodes": 1,
    "produced_by": "PT-VFX",
    "produced_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00"),
    "source_episodes_dir": scenes_dir,
    "episodes": [
        {
            "ep": 8,
            "title": "说文解字",
            "subtitle": "许慎·六书之学与汉字的终极命名",
            "video_file": "墨骨山河_ep08_pipeline.mp4",
            "audio_file": "",
            "duration_seconds": round(total_duration, 1),
            "resolution": "1080p",
            "bitrate_kbps": 2000,
            "chains": ["墨骨山河_ep08"],
            "cards_file": "",
            "scene_timeline": timeline
        }
    ]
}

out_path = r"D:\92_products\SPDT-004_EduContent\PT-038_TextExperience\墨骨山河_ep08_test\metadata.json"
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(metadata, f, ensure_ascii=False, indent=2)

print(f"ep08 metadata.json written: {out_path}")
print(f"Total scenes: {len(timeline)}, estimated duration: {total_duration}s")
