# -*- coding: utf-8 -*-
import json, os

d = r"D:\92_products\SPDT-004_EduContent\PT-038_TextExperience\墨骨山河_ep08_test\scenes"
for sf in os.listdir(d):
    if not sf.endswith('.json'):
        continue
    with open(os.path.join(d, sf), encoding='utf-8') as f:
        scene = json.load(f)
    stype = scene.get('scene_type', '?')
    print(f"{sf}: type={stype}, keys={list(scene.keys())}")
    content = scene.get('content', {})
    if isinstance(content, dict):
        for k, v in content.items():
            print(f"  content.{k}: {str(v)[:80]}")
