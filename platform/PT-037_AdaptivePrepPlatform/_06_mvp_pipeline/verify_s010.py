# -*- coding: utf-8 -*-
import json
path = r"D:\92_products\SPDT-004_EduContent\PT-037_AdaptivePrepPlatform\_03_subject_packs\cafa_calligraphy_2026\knowledge\kb_vocab_enhanced.json"
with open(path, "r", encoding="utf-8") as f:
    data = json.load(f)

for mod_data in data["modules"].values():
    for items in mod_data.values():
        for item in items:
            if item.get("kb_id") == "KB_CAFA_S010":
                print("KB_CAFA_S010 found!")
                print("=" * 60)
                sc = item["structured_content"]
                print(f"historical_period: {sc.get('historical_period','')[:80]}...")
                print(f"background len: {len(sc.get('background',''))}")
                print(f"background preview: {sc.get('background','')[:150]}...")
                print(f"\nexam_tips keys: {list(item.get('exam_tips',{}).keys())}")
                print(f"answer_template len: {len(item.get('answer_template',''))}")
                print(f"answer_template preview: {item.get('answer_template','')[:100]}...")
                print(f"\ncross_pack_links: {item.get('cross_pack_links',[])}")
                break
        else:
            continue
        break
