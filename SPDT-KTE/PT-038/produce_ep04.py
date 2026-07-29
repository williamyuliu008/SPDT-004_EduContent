# -*- coding: utf-8 -*-
"""
ep04 孙过庭·书谱之道 专用生产脚本
跑 TTS → Render → Compose → Metadata
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import os, json, shutil, asyncio, edge_tts, subprocess
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).parent
VF_TOOLS = SCRIPT_DIR.parent / "shared" / "video_factory" / "tools"
RENDERER = VF_TOOLS / "scene_renderer_pillow.py"
COMPOSER = VF_TOOLS / "compose_video.py"
OUTPUT_DIR = SCRIPT_DIR / "墨骨山河_ep04_test"
SCENES_DIR = OUTPUT_DIR / "scenes"
AUDIO_DIR = OUTPUT_DIR / "ep04_audio"
ORGANIZE = SCRIPT_DIR / "organize_flat_frames.py"
SCRIPTS_DIR = Path(r"C:\Users\willi\Desktop\我的视野\0713-基于知识库的高阶备考智能体\02-设计文档\配置包_cafa_calligraphy_2026\scripts")

def log(msg, level="INFO"):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] [{level}] {msg}", flush=True)

def extract_scene_text(scene):
    content = scene.get("content", {})
    for field in ["body_lines", "steps", "points"]:
        lines = content.get(field, [])
        if isinstance(lines, list) and lines:
            joined = "。".join(str(x) for x in lines if x)
            if joined: return joined
    for field in ["quote", "body"]:
        val = content.get(field, "")
        if val and len(val) >= 5: return val.replace("\n", "。")
    events = content.get("timeline_events", [])
    if isinstance(events, list) and events:
        parts = []
        for ev in events:
            yr = ev.get("year", ""); ev_name = ev.get("event", ""); note = ev.get("note", "")
            parts.append(f"{yr}年，{ev_name}，{note}")
        if parts: return "。".join(parts)
    title = content.get("title", scene.get("title", ""))
    if title: return title
    trigger = scene.get("five_skandha", {}).get("sensation_trigger", "")
    if trigger: return trigger.replace("\n", "。")
    return ""

async def _tts_one(text, out_path):
    try:
        comm = edge_tts.Communicate(text, "zh-CN-XiaoxiaoNeural")
        await comm.save(out_path)
    except Exception as e:
        log(f"TTS failed: {e}", "ERROR")

async def stage3_tts():
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    scene_files = sorted([f for f in SCENES_DIR.glob("*.json") if f.name not in ("manifest.json", "scene_v2_full.json")])
    log(f"[TTS] {len(scene_files)} scenes")
    generated = 0
    for sf in scene_files:
        scene_id = sf.stem
        out_file = AUDIO_DIR / f"{scene_id}.mp3"
        if out_file.exists():
            log(f"  EXISTS {scene_id}")
            continue
        try:
            with open(sf, encoding="utf-8") as f:
                scene = json.load(f)
        except:
            log(f"  SKIP bad JSON {scene_id}", "WARN")
            continue
        text = extract_scene_text(scene)
        if len(text.strip()) < 10:
            log(f"  SKIP short {scene_id} ({len(text)} chars)")
            continue
        await _tts_one(text, str(out_file))
        generated += 1
        log(f"  TTS [{generated}] {scene_id} ({len(text)} chars)")
    log(f"[TTS] ✅ {generated} generated")
    _backfill_durations(scene_files)
    return generated

def _backfill_durations(scene_files):
    for sf in scene_files:
        audio_path = AUDIO_DIR / f"{sf.stem}.mp3"
        if not audio_path.exists(): continue
        try:
            result = subprocess.run(
                ["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "csv=p=0", str(audio_path)],
                capture_output=True, text=True, timeout=10
            )
            dur = float(result.stdout.strip())
            dur = max(5, min(60, dur))
        except:
            dur = 30
        with open(sf, encoding="utf-8") as f:
            scene = json.load(f)
        si = scene.get("scene_info", {})
        si["dur"] = round(dur, 1)
        scene["scene_info"] = si
        with open(sf, "w", encoding="utf-8") as f:
            json.dump(scene, f, ensure_ascii=False, indent=2)

def stage4_render():
    log("[Render] Starting...")
    scene_files = sorted([f for f in SCENES_DIR.glob("*.json") if f.name not in ("manifest.json", "scene_v2_full.json")])
    for sf in scene_files:
        scene_id = sf.stem
        audio_path = AUDIO_DIR / f"{scene_id}.mp3"
        out_dir = SCENES_DIR / f"frames_{scene_id}"
        out_dir.mkdir(exist_ok=True)
        result = subprocess.run(
            [sys.executable, str(RENDERER), str(sf), "--output", str(out_dir)],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode != 0:
            log(f"  RENDER FAIL {scene_id}: {result.stderr[:100]}", "ERROR")
        else:
            log(f"  RENDER OK {scene_id}")
    # Organize flat frames
    log("[Render] Organizing frames...")
    subprocess.run([sys.executable, str(ORGANIZE), str(SCENES_DIR)], capture_output=True)
    log("[Render] ✅ Done")

def stage5_compose():
    log("[Compose] Starting...")
    manifest = SCENES_DIR / "manifest.json"
    video_out = OUTPUT_DIR / "video.mp4"
    audio_list = sorted(AUDIO_DIR.glob("*.mp3"))
    log(f"[Compose] {len(audio_list)} audio files, manifest exists: {manifest.exists()}")
    result = subprocess.run(
        [sys.executable, str(COMPOSER), "--manifest", str(manifest), "--scenes", str(SCENES_DIR), "--output", str(video_out)],
        capture_output=True, text=True, timeout=300
    )
    if result.returncode != 0:
        log(f"Compose FAIL: {result.stderr[:200]}", "ERROR")
    else:
        log(f"Compose OK: {video_out}")
    if video_out.exists():
        size_mb = video_out.stat().st_size / 1024 / 1024
        log(f"[Compose] Video: {size_mb:.2f} MB")
    return video_out.exists()

def stage6_metadata():
    log("[Metadata] Generating...")
    video = OUTPUT_DIR / "video.mp4"
    manifest = SCENES_DIR / "manifest.json"
    meta_out = OUTPUT_DIR / "metadata.json"
    if not video.exists() or not manifest.exists():
        log("Cannot generate metadata - missing files", "ERROR")
        return
    with open(manifest, encoding="utf-8") as f:
        mf = json.load(f)
    total_dur = sum(si.get("dur", 30) for si in mf.get("scene_info_list", []) if isinstance(si, dict))
    meta = {
        "title": "墨骨山河 ep04 孙过庭·书谱之道",
        "episode": 4,
        "source_script": "墨骨山河_ep04_孙过庭_书谱之道",
        "scenes": mf.get("scene_count", 0),
        "total_duration_s": round(total_dur, 1),
        "video_size_mb": round(video.stat().st_size / 1024 / 1024, 2),
        "generated_at": datetime.now().isoformat()
    }
    with open(meta_out, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    log(f"[Metadata] ✅ {meta_out}")

async def main():
    log("=" * 60)
    log("EP04 孙过庭·书谱之道 生产线")
    log("=" * 60)
    
    log("[Stage 3] TTS...")
    await stage3_tts()
    
    log("[Stage 4] Render...")
    stage4_render()
    
    log("[Stage 5] Compose...")
    ok = stage5_compose()
    
    log("[Stage 6] Metadata...")
    if ok:
        stage6_metadata()
    
    log("=" * 60)
    log("EP04 完成!")
    log("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
