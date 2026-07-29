# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

"""
patch_ep08_audio.py — 补充 ep08 缺音频场景的 TTS
====================================================
原因：orchestrator 只从 body_lines/steps/body 提取文本，
      漏了 quote / timeline_events / evolution_stages 等字段。

补充场景：
  act1_02  (word_evolution): body_lines空，用 title + sensation_trigger
  act3_09  (quote_highlight): content.quote 字段未提取
  act3_10  (timeline):       content.timeline_events 未提取
  act3_11  (quote_highlight): content.quote 字段未提取

Author: PT-VFX
Date:   2026-07-20
"""

import os, sys, json, asyncio
import edge_tts

EP08_ROOT = r"D:\92_products\SPDT-004_EduContent\PT-038_TextExperience\墨骨山河_ep08_test"
AUDIO_DIR = os.path.join(EP08_ROOT, "ep08_audio")
SCENES_DIR = os.path.join(EP08_ROOT, "scenes", "scenes")

os.makedirs(AUDIO_DIR, exist_ok=True)


def extract_text(scene: dict) -> str:
    """从 scene JSON 提取 TTS 文本，兼容多种 content 结构。"""
    content = scene.get("content", {})

    # 1. 优先：body_lines（非空列表）
    body_lines = content.get("body_lines", [])
    if isinstance(body_lines, list) and body_lines:
        lines = [str(x) for x in body_lines if x]
        if lines:
            return "。".join(lines)

    # 2. quote 字段（quote_highlight / narrative 场景）
    quote = content.get("quote", "")
    if quote and len(quote) >= 5:
        return quote.replace("\n", "。")

    # 3. steps 字段（steps 场景）
    steps = content.get("steps", [])
    if isinstance(steps, list) and steps:
        return "。".join(f"第{i+1}步，{s}" for i, s in enumerate(steps) if s)

    # 4. timeline_events 字段
    events = content.get("timeline_events", [])
    if isinstance(events, list) and events:
        parts = []
        for ev in events:
            year = ev.get("year", "")
            event = ev.get("event", "")
            note = ev.get("note", "")
            parts.append(f"{year}年，{event}，{note}")
        if parts:
            return "。".join(parts)

    # 5. evolution_stages 字段
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

    # 6. title（兜底）
    title = content.get("title", scene.get("title", ""))
    if title:
        return title

    # 7. five_skandha.sensation_trigger（兜底）
    trigger = scene.get("five_skandha", {}).get("sensation_trigger", "")
    if trigger:
        return trigger.replace("\n", "。")

    return ""


async def generate_tts(text: str, out_path: str) -> bool:
    """用 edge-tts 生成 MP3。"""
    try:
        communicate = edge_tts.Communicate(text, "zh-CN-XiaoxiaoNeural")
        await communicate.save(out_path)
        size = os.path.getsize(out_path)
        print(f"  [OK] {os.path.basename(out_path)} ({len(text)} chars, {size//1024}KB)")
        return True
    except Exception as e:
        print(f"  [FAIL] {os.path.basename(out_path)}: {e}")
        return False


async def main():
    # 需要补充的场景
    missing = [
        "墨骨山河_ep08_act1_02",
        "墨骨山河_ep08_act3_09",
        "墨骨山河_ep08_act3_10",
        "墨骨山河_ep08_act3_11",
    ]

    # 找到 scenes 目录（直接 scenes/ 或 scenes/scenes/）
    scenes_base = os.path.join(EP08_ROOT, "scenes")
    # scenes/ 下应有 manifest.json；若不在，试试 scenes/scenes/
    manifest = os.path.join(scenes_base, "manifest.json")
    if not os.path.exists(manifest):
        scenes_base = os.path.join(EP08_ROOT, "scenes", "scenes")

    results = []
    for sid in missing:
        scene_path = None
        for root, dirs, files in os.walk(scenes_base):
            fname = f"{sid}.json"
            if fname in files:
                scene_path = os.path.join(root, fname)
                break

        if not scene_path or not os.path.exists(scene_path):
            print(f"  [WARN] scene file not found: {sid}")
            results.append((sid, False, "file not found"))
            continue

        with open(scene_path, encoding="utf-8") as f:
            scene = json.load(f)

        text = extract_text(scene)
        if not text or len(text.strip()) < 5:
            print(f"  [WARN] {sid}: no text extracted from content={str(scene.get('content', ''))[:80]}")
            results.append((sid, False, "text empty"))
            continue

        out_path = os.path.join(AUDIO_DIR, f"{sid}.mp3")
        ok = await generate_tts(text, out_path)
        results.append((sid, ok, text[:60]))

    # 汇总
    print("\n--- PATCH RESULT ---")
    ok_count = sum(1 for _, ok, _ in results if ok)
    for sid, ok, text in results:
        status = "[OK]" if ok else "[FAIL]"
        print(f"  {status} {sid}: {text[:60]}...")
    print(f"\nTotal: {ok_count}/{len(results)} succeeded")


if __name__ == "__main__":
    asyncio.run(main())
