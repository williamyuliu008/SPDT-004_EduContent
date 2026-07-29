# -*- coding: utf-8 -*-
import sys, json, asyncio, edge_tts, os
sys.stdout.reconfigure(encoding='utf-8')

scenes_dir = r"D:\92_products\SPDT-004_EduContent\PT-038_TextExperience\墨骨山河_ep06_test\scenes"
audio_dir = r"D:\92_products\SPDT-004_EduContent\PT-038_TextExperience\墨骨山河_ep06_test\ep06_audio"
os.makedirs(audio_dir, exist_ok=True)

def extract_text(scene):
    content = scene.get('content', {})
    for field in ['body_lines', 'steps', 'points']:
        lines = content.get(field, [])
        if isinstance(lines, list) and lines:
            joined = '。'.join(str(x) for x in lines if x)
            if joined:
                return joined
    for field in ['quote', 'body']:
        val = content.get(field, '')
        if val and len(val) >= 5:
            return val.replace('\n', '。')
    events = content.get('timeline_events', [])
    if isinstance(events, list) and events:
        parts = []
        for ev in events:
            yr = ev.get('year', '')
            ev_name = ev.get('event', '')
            note = ev.get('note', '')
            parts.append(f'{yr}年，{ev_name}，{note}')
        if parts:
            return '。'.join(parts)
    title = content.get('title', scene.get('title', ''))
    if title:
        return title
    trigger = scene.get('five_skandha', {}).get('sensation_trigger', '')
    if trigger:
        return trigger.replace('\n', '。')
    return ''

scene_files = sorted([
    f for f in os.listdir(scenes_dir)
    if f.endswith('.json') and f not in ('manifest.json', 'scene_v2_full.json')
])

print(f'TTS: {len(scene_files)} scenes')

async def gen_one(text, out):
    try:
        comm = edge_tts.Communicate(text, 'zh-CN-XiaoxiaoNeural')
        await comm.save(out)
        return True
    except Exception as e:
        print(f'  FAIL: {e}')
        return False

async def main():
    for sf in scene_files:
        sid = sf.replace('.json', '')
        out = os.path.join(audio_dir, f'{sid}.mp3')
        if os.path.exists(out):
            print(f'  SKIP {sid}')
            continue
        with open(os.path.join(scenes_dir, sf), encoding='utf-8') as f:
            scene = json.load(f)
        text = extract_text(scene)
        if len(text.strip()) < 10:
            print(f'  SKIP {sid}: text too short ({len(text)} chars)')
            continue
        ok = await gen_one(text, out)
        status = 'OK' if ok else 'FAIL'
        print(f'  TTS [{status}] {sid} ({len(text)} chars)')

asyncio.run(main())
print('Done')
