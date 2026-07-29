# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

"""
production_batch.py — 夜间批量生产管线 v0.1
=============================================
执行 ep01-ep06 全量生产（Stage 1-5），无需人工干预。

步骤：
  1. Adapter: acts[] → episodes[] 格式转换
  2. Orchestrator: 对每集执行五阶段管线
  3. 汇总报告

用法（本地）:
  python production_batch.py

用法（cron/后台）:
  python production_batch.py --skip adapter  # adapter 已跑过，跳过

输出目录:
  D:\\92_products\\SPDT-004_EduContent\\PT-038_TextExperience\\墨骨山河_epXX_test/

Author: PT-VFX
Date:   2026-07-20
Version: 0.1.0
"""

import os
import sys
import json
import shutil
import asyncio
import edge_tts
import subprocess
import argparse
from pathlib import Path
from datetime import datetime

# ── 路径配置 ──────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).parent
VIDEO_FACTORY_ROOT = SCRIPT_DIR.parent / "shared" / "video_factory"
VF_TOOLS = VIDEO_FACTORY_ROOT / "tools"
ADAPTER_SCRIPT = VF_TOOLS / "PT038_converter" / "acts_to_episodes_adapter.py"
CONVERTER_SCRIPT = VF_TOOLS / "PT038_converter" / "converter.py"
RENDERER_SCRIPT = VF_TOOLS / "scene_renderer_pillow.py"
COMPOSER_SCRIPT = VF_TOOLS / "compose_video.py"
OUTPUT_ROOT = SCRIPT_DIR  # PT-038_TextExperience/
SCRIPTS_DIR = Path(r"C:\Users\willi\Desktop\我的视野\0713-基于知识库的高阶备考智能体\02-设计文档\配置包_cafa_calligraphy_2026\scripts")

# ── 日志 ──────────────────────────────────────────────────────────────────
def log(msg, level="INFO"):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] [{level}] {msg}", flush=True)

def log_err(msg):
    log(msg, "ERROR")

# ── EPISODE 清单 ─────────────────────────────────────────────────────────
# key: 集号, value: (源文件名(含adapter前), 输出目录名, 标题, 副标题)
EPISODES = [
    (1, "墨骨山河_ep01_李斯",           "墨骨山河_ep01_test", "峄山碑前",    "李斯·小篆的秩序与第一道名字"),
    (2, "墨骨山河_ep02_王羲之_兰亭序",  "墨骨山河_ep02_test", "永和九年那场雨", "王羲之·兰亭序与书法的觉醒"),
    (3, "墨骨山河_ep03_苏轼_黄州突围",  "墨骨山河_ep03_test", "黄州突围",    "苏轼·寒食帖与书法的生命维度"),
    (5, "墨骨山河_ep05_张旭怀素_颠张醉素", "墨骨山河_ep05_test", "颠张醉素", "张旭怀素·草书的极限与癫狂"),
    (6, "墨骨山河_ep06_颜真卿_安史之乱", "墨骨山河_ep06_test", "安史之乱",    "颜真卿·忠烈之书与大唐的至暗时刻"),
]

# ── Stage 1: Adapter ─────────────────────────────────────────────────────
def stage1_adapter(ep_num: int, script_name: str) -> bool:
    """格式适配：acts[] → episodes[]。"""
    src = SCRIPTS_DIR / f"{script_name}.json"
    if not src.exists():
        log_err(f"  源脚本不存在: {src}")
        return False

    adapted_dir = SCRIPTS_DIR / "_adapted"
    adapted_dir.mkdir(exist_ok=True)
    out = adapted_dir / f"{script_name}.json"

    log(f"[Stage 1] Adapter: ep{ep_num:02d} {src.name}")
    result = subprocess.run(
        [sys.executable, str(ADAPTER_SCRIPT), str(src)],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    if result.returncode != 0:
        log_err(f"  Adapter failed: {result.stderr[:200]}")
        return False
    log(f"[Stage 1]  ✅ Adapted → {out.name}")
    return True

# ── Stage 2: Converter ────────────────────────────────────────────────────
def stage2_converter(ep_num: int, script_name: str) -> tuple[bool, Path]:
    """PT038_converter: 微剧本 → scene JSON。"""
    adapted = SCRIPTS_DIR / "_adapted" / f"{script_name}.json"
    output_dir = OUTPUT_ROOT / f"墨骨山河_ep{ep_num:02d}_test"
    scenes_dir = output_dir / "scenes"
    scenes_dir.mkdir(parents=True, exist_ok=True)

    log(f"[Stage 2] Converter: ep{ep_num:02d}")
    result = subprocess.run(
        [sys.executable, str(CONVERTER_SCRIPT),
         "--input", str(adapted),
         "--output", str(scenes_dir)],
        cwd=str(VF_TOOLS),
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=120
    )
    if result.returncode != 0:
        log_err(f"  Converter failed: {result.stderr[:300]}")
        return False, scenes_dir

    # 数 scene 数量
    scene_files = [f for f in scenes_dir.glob("*.json")
                   if f.name not in ("manifest.json", "scene_v2_full.json")]
    log(f"[Stage 2]  ✅ {len(scene_files)} scenes → {scenes_dir}")
    return True, scenes_dir

# ── Stage 3: TTS (edge-tts) ──────────────────────────────────────────────
def extract_scene_text(scene: dict) -> str:
    """从 scene JSON 提取 TTS 文本，支持多种 content 结构。"""
    content = scene.get("content", {})

    for field in ["body_lines", "steps", "points"]:
        lines = content.get(field, [])
        if isinstance(lines, list) and lines:
            joined = "。".join(str(x) for x in lines if x)
            if joined:
                return joined

    for field in ["quote", "body"]:
        val = content.get(field, "")
        if val and len(val) >= 5:
            return val.replace("\n", "。")

    events = content.get("timeline_events", [])
    if isinstance(events, list) and events:
        parts = []
        for ev in events:
            yr = ev.get("year", "")
            ev_name = ev.get("event", "")
            note = ev.get("note", "")
            parts.append(f"{yr}年，{ev_name}，{note}")
        if parts:
            return "。".join(parts)

    stages = content.get("evolution_stages", [])
    if isinstance(stages, list) and stages:
        parts = []
        for st in stages:
            if isinstance(st, dict):
                era = st.get("era", "")
                desc = st.get("description", st.get("name", ""))
                parts.append(f"{era}：{desc}")
            elif st:
                parts.append(str(st))
        if parts:
            return "。".join(parts)

    title = content.get("title", scene.get("title", ""))
    if title:
        return title

    trigger = scene.get("five_skandha", {}).get("sensation_trigger", "")
    if trigger:
        return trigger.replace("\n", "。")
    return ""


async def _tts_one(text: str, out_path: str):
    try:
        comm = edge_tts.Communicate(text, "zh-CN-XiaoxiaoNeural")
        await comm.save(out_path)
    except Exception as e:
        log_err(f"  TTS failed: {e}")


async def stage3_tts(scenes_dir: Path, ep_num: int) -> tuple[int, int]:
    """TTS 生成，返回 (生成数, 跳过数)。"""
    audio_dir = OUTPUT_ROOT / f"墨骨山河_ep{ep_num:02d}_test" / f"ep{ep_num:02d}_audio"
    audio_dir.mkdir(parents=True, exist_ok=True)

    scene_files = sorted([
        f for f in scenes_dir.glob("*.json")
        if f.name not in ("manifest.json", "scene_v2_full.json")
    ])

    log(f"[Stage 3] TTS: {len(scene_files)} scenes")
    generated = skipped = 0

    for sf in scene_files:
        scene_id = sf.stem
        out_file = audio_dir / f"{scene_id}.mp3"

        if out_file.exists():
            skipped += 1
            continue

        try:
            with open(sf, encoding="utf-8") as f:
                scene = json.load(f)
        except Exception:
            skipped += 1
            continue

        text = extract_scene_text(scene)
        if len(text.strip()) < 10:
            log(f"  SKIP {scene_id}: text too short ({len(text)} chars)")
            skipped += 1
            continue

        await _tts_one(text, str(out_file))
        generated += 1
        log(f"  TTS [{generated}] {scene_id} ({len(text)} chars)")

    log(f"[Stage 3]  ✅ {generated} generated, {skipped} skipped")

    # Q10 修复：测量实际音频时长，回填 scene_info.dur
    _backfill_durations(scenes_dir, audio_dir)

    return generated, skipped


def _backfill_durations(scenes_dir: Path, audio_dir: Path):
    """用 ffprobe 测量音频时长，回填 scene JSON 的 scene_info.dur（解决 Q10）。"""
    try:
        import subprocess
    except ImportError:
        return

    scene_files = sorted([
        f for f in scenes_dir.glob("*.json")
        if f.name not in ("manifest.json", "scene_v2_full.json")
    ])
    updated = 0
    for sf in scene_files:
        audio_path = audio_dir / f"{sf.stem}.mp3"
        if not audio_path.exists():
            continue

        r = subprocess.run(
            ["ffprobe", "-v", "quiet", "-show_entries",
             "format=duration", "-of", "csv=p=0", str(audio_path)],
            capture_output=True, text=True
        )
        try:
            dur = float(r.stdout.strip())
        except (ValueError, AttributeError):
            dur = 30.0

        # 回填 scene_info.dur（限制最大60s，最小5s）
        dur = max(5.0, min(60.0, dur))

        try:
            with open(sf, encoding="utf-8") as f:
                scene = json.load(f)
            scene["scene_info"] = scene.get("scene_info", {})
            scene["scene_info"]["dur"] = round(dur, 2)
            with open(sf, "w", encoding="utf-8") as f:
                json.dump(scene, f, ensure_ascii=False, indent=2)
            updated += 1
        except Exception:
            pass

    if updated:
        log(f"[Q10 Fix]  Backfilled {updated} scene durations (5-60s range)")

# ── Stage 4: Render ───────────────────────────────────────────────────────
def stage4_render(scenes_dir: Path, ep_num: int) -> bool:
    """scene_renderer_pillow 渲染帧序列。"""
    frames_dir = OUTPUT_ROOT / f"墨骨山河_ep{ep_num:02d}_test" / f"ep{ep_num:02d}_frames"
    frames_dir.mkdir(parents=True, exist_ok=True)

    log(f"[Stage 4] Render: ep{ep_num:02d}")
    # scene_renderer_pillow.py: target=scenes_dir, --output=frames_dir
    result = subprocess.run(
        [sys.executable, str(RENDERER_SCRIPT),
         str(scenes_dir),          # positional: scene JSON directory
         "--output", str(frames_dir),
         "--fps", "15"],
        cwd=str(VF_TOOLS),
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=600
    )
    if result.returncode != 0:
        log_err(f"  Render failed: {result.stderr[-200:]}")
        return False

    # reorganize subdirs if needed
    _reorganize(frames_dir)

    n_frames = sum(1 for _ in frames_dir.rglob("*.png"))
    log(f"[Stage 4]  ✅ {n_frames} frames → {frames_dir}")
    return True

def _reorganize(frames_dir: Path):
    """将 flat PNG 重排为 frames_scene_ID 子目录。"""
    for f in frames_dir.glob("*.png"):
        prefix = f.stem.rsplit("_f", 1)[0]
        subdir = frames_dir / f"frames_{prefix}"
        subdir.mkdir(exist_ok=True)
        dst = subdir / f.name
        if not dst.exists():
            import shutil
            shutil.move(str(f), str(dst))

# ── Stage 5: Compose ───────────────────────────────────────────────────────
def stage5_compose(ep_num: int) -> tuple[bool, Path]:
    """compose_video 合成 MP4。"""
    ep_dir = OUTPUT_ROOT / f"墨骨山河_ep{ep_num:02d}_test"
    frames_dir = ep_dir / f"ep{ep_num:02d}_frames"
    audio_dir = ep_dir / f"ep{ep_num:02d}_audio"
    scenes_dir = ep_dir / "scenes"
    output_mp4 = ep_dir / f"墨骨山河_ep{ep_num:02d}_pipeline.mp4"

    log(f"[Stage 5] Compose: ep{ep_num:02d}")
    result = subprocess.run(
        [sys.executable, str(COMPOSER_SCRIPT),
         str(frames_dir),
         "--audio", str(audio_dir),
         "--scenes", str(scenes_dir),
         "--output", str(output_mp4),
         "--fps", "15"],
        cwd=str(VF_TOOLS),
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=600
    )
    if result.returncode != 0 and "DONE" not in result.stdout:
        log_err(f"  Compose failed: {result.stderr[-200:]}")
        return False, output_mp4

    if output_mp4.exists():
        size_mb = output_mp4.stat().st_size / 1024 / 1024
        log(f"[Stage 5]  ✅ {output_mp4.name} ({size_mb:.2f} MB)")
    return True, output_mp4

# ── Stage 6: Metadata ─────────────────────────────────────────────────────
def stage6_metadata(ep_num: int, title: str, subtitle: str) -> bool:
    """生成 metadata.json（含完整 five_skandha）。"""
    ep_dir = OUTPUT_ROOT / f"墨骨山河_ep{ep_num:02d}_test"
    scenes_dir = ep_dir / "scenes"
    manifest_path = scenes_dir / "manifest.json"
    meta_path = ep_dir / "metadata.json"

    if not manifest_path.exists():
        log_err(f"  manifest.json not found: {manifest_path}")
        return False

    with open(manifest_path, encoding="utf-8") as f:
        manifest = json.load(f)

    timeline = []
    current_time = 0.0

    for i, scene_meta in enumerate(manifest["scenes"]):
        sid = scene_meta["scene_id"]
        scene_file = scenes_dir / f"{sid}.json"
        full_scene = {}
        if scene_file.exists():
            with open(scene_file, encoding="utf-8") as f:
                full_scene = json.load(f)

        scene_title = scene_meta.get("title", full_scene.get("content", {}).get("title", ""))
        if len(scene_title) > 50:
            scene_title = scene_title[:50] + "..."

        five_sk = full_scene.get("five_skandha", {})
        color_base = five_sk.get("color_base", scene_meta.get("source_knowledge_nodes", ["#书法"] or ["#书法"])[:4])
        recognition = five_sk.get("recognition_marker") or (scene_meta.get("source_knowledge_nodes") or ["#书法"])[0]

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
        current_time += 30.0

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

    log(f"[Stage 6]  ✅ metadata.json")
    return True

# ── 主流程 ────────────────────────────────────────────────────────────────
def produce_episode(ep_num: int, script_name: str, title: str, subtitle: str,
                   skip_adapter: bool = False) -> dict:
    """单集全量生产。"""
    ep_dir = OUTPUT_ROOT / f"墨骨山河_ep{ep_num:02d}_test"
    scenes_dir = ep_dir / "scenes"

    results = {
        "ep_num": ep_num,
        "title": title,
        "stages": {},
        "status": "ok",
        "video": None,
        "errors": []
    }

    # Stage 1: Adapter
    if not skip_adapter:
        ok = stage1_adapter(ep_num, script_name)
        results["stages"]["adapter"] = "ok" if ok else "fail"
        if not ok:
            results["status"] = "fail"
            results["errors"].append("adapter")
            return results

    # Stage 2: Converter
    ok, scenes_dir = stage2_converter(ep_num, script_name)
    results["stages"]["converter"] = "ok" if ok else "fail"
    if not ok:
        results["status"] = "fail"
        results["errors"].append("converter")
        return results

    # Stage 3: TTS (async)
    log(f"[Stage 3] TTS: ep{ep_num:02d}")
    n_gen, n_skip = asyncio.run(stage3_tts(scenes_dir, ep_num))
    results["stages"]["tts"] = f"ok({n_gen}g/{n_skip}s)"

    # Stage 4: Render
    ok = stage4_render(scenes_dir, ep_num)
    results["stages"]["render"] = "ok" if ok else "fail"
    if not ok:
        results["status"] = "partial"
        results["errors"].append("render")

    # Stage 5: Compose
    ok, video_path = stage5_compose(ep_num)
    results["stages"]["compose"] = "ok" if ok else "fail"
    results["video"] = str(video_path) if video_path.exists() else None
    if not ok:
        results["status"] = "partial"
        results["errors"].append("compose")

    # Stage 6: Metadata
    ok = stage6_metadata(ep_num, title, subtitle)
    results["stages"]["metadata"] = "ok" if ok else "fail"

    return results


def run_all(skip_adapter: bool = False) -> list[dict]:
    """批量生产所有集。"""
    results = []
    for ep_num, script_name, out_dir, title, subtitle in EPISODES:
        ep_dir = OUTPUT_ROOT / f"墨骨山河_ep{ep_num:02d}_test"
        if ep_dir.exists() and (ep_dir / f"墨骨山河_ep{ep_num:02d}_pipeline.mp4").exists():
            log(f"[SKIP] ep{ep_num:02d} already has video, skipping")
            results.append({
                "ep_num": ep_num, "title": title,
                "status": "skipped", "stages": {}, "video": str(ep_dir / f"墨骨山河_ep{ep_num:02d}_pipeline.mp4")
            })
            continue

        log(f"\n{'='*60}")
        log(f"  START: ep{ep_num:02d} — {title}")
        log(f"{'='*60}")
        r = produce_episode(ep_num, script_name, title, subtitle, skip_adapter)
        results.append(r)
        log(f"  DONE: ep{ep_num:02d} status={r['status']}")

    return results


def main():
    parser = argparse.ArgumentParser(description="夜间批量生产管线 v0.1")
    parser.add_argument("--skip-adapter", action="store_true",
                        help="跳过 adapter（已跑过，直接用 _adapted 文件）")
    args = parser.parse_args()

    log(f"=== PRODUCTION BATCH START: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
    results = run_all(skip_adapter=args.skip_adapter)

    # 汇总
    log(f"\n{'='*60}")
    log("  SUMMARY")
    log(f"{'='*60}")
    ok_count = sum(1 for r in results if r["status"] == "ok")
    partial_count = sum(1 for r in results if r["status"] == "partial")
    skip_count = sum(1 for r in results if r["status"] == "skipped")
    for r in results:
        stages = " | ".join(f"{k}={v}" for k, v in r.get("stages", {}).items())
        log(f"  ep{r['ep_num']:02d} [{r['status']}] {r['title']}: {stages}")
        if r.get("errors"):
            log(f"    ERRORS: {', '.join(r['errors'])}")
        if r.get("video"):
            log(f"    VIDEO: {r['video']}")

    log(f"\n  Total: {len(results)} | ok={ok_count} partial={partial_count} skipped={skip_count}")
    log(f"=== PRODUCTION BATCH END ===")

    # 保存报告
    report_path = OUTPUT_ROOT / "production_batch_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump({
            "generated_at": datetime.now().isoformat(),
            "results": results,
            "summary": {
                "total": len(results),
                "ok": ok_count,
                "partial": partial_count,
                "skipped": skip_count
            }
        }, f, ensure_ascii=False, indent=2)
    log(f"Report: {report_path}")


if __name__ == "__main__":
    main()
