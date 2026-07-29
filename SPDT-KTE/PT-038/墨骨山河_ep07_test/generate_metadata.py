# -*- coding: utf-8 -*-
"""Generate metadata.json for ep07 (阮元·碑学中兴)"""
import json, os, glob
from datetime import datetime

ep = "墨骨山河_ep07"
audio_dir = r"D:\92_products\SPDT-004_EduContent\PT-038_TextExperience\墨骨山河_ep07_test\ep07_audio"
scenes_dir = r"D:\92_products\SPDT-004_EduContent\PT-038_TextExperience\墨骨山河_ep07_test\scenes"
manifest_path = os.path.join(scenes_dir, "manifest.json")

with open(manifest_path, encoding='utf-8') as f:
    manifest = json.load(f)

# Get audio files
audio_files = {}
for af in os.listdir(audio_dir):
    if af.endswith('.mp3'):
        key = af.replace('.mp3', '').replace('_', '_')
        audio_files[key] = os.path.join(audio_dir, af)

# Build scene timeline from FULL scene JSON files (not just manifest)
scenes = manifest['scenes']
timeline = []
current_time = 0.0

for i, scene_meta in enumerate(scenes):
    sid = scene_meta['scene_id']
    # Load full scene JSON for five_skandha data
    scene_file_path = os.path.join(scenes_dir, f"{sid}.json")
    full_scene = {}
    if os.path.exists(scene_file_path):
        with open(scene_file_path, encoding='utf-8') as f:
            full_scene = json.load(f)

    scene_file = None
    for k, v in audio_files.items():
        if sid in k:
            scene_file = os.path.basename(v)
            break
    
    title = scene_meta.get('title', full_scene.get('content', {}).get('title', ''))
    if len(title) > 50:
        title = title[:50] + '...'
    
    five_sk = full_scene.get('five_skandha', {})
    color_base = five_sk.get('color_base', scene_meta.get('source_knowledge_nodes', ['#书法/清'])[:4])
    recognition = five_sk.get('recognition_marker') or (scene_meta.get('source_knowledge_nodes') or ['#书法/清'])[0]

    entry = {
        "idx": i,
        "time": round(current_time, 1),
        "scene_name": title,
        "scene_type": full_scene.get('scene_type', scene_meta.get('scene_type', 'concept')),
        "chain_ref": "墨骨山河_ep07",
        "five_skandha": {
            "color_base": color_base[:4] if color_base else [],
            "action_prompt": five_sk.get('action_prompt', '口述/复述'),
            "recognition_marker": recognition
        }
    }
    timeline.append(entry)
    # Estimate scene duration (30s per scene default)
    current_time += 30.0

total_duration = current_time

metadata = {
    "schema_version": "1.0.0",
    "package_id": "墨骨山河_EP07",
    "series_title": "墨骨山河",
    "total_episodes": 1,
    "produced_by": "PT-VFX",
    "produced_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00"),
    "source_episodes_dir": scenes_dir,
    "episodes": [
        {
            "ep": 7,
            "title": "碑学中兴",
            "subtitle": "阮元与书法的版图重划",
            "video_file": "墨骨山河_ep07_pipeline.mp4",
            "audio_file": "",
            "duration_seconds": round(total_duration, 1),
            "resolution": "1080p",
            "bitrate_kbps": 2000,
            "chains": ["墨骨山河_ep07"],
            "cards_file": "",
            "scene_timeline": timeline
        }
    ]
}

out_path = r"D:\92_products\SPDT-004_EduContent\PT-038_TextExperience\墨骨山河_ep07_test\metadata.json"
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(metadata, f, ensure_ascii=False, indent=2)

print(f"metadata.json written: {out_path}")
print(f"Total scenes: {len(timeline)}, estimated duration: {total_duration}s")
