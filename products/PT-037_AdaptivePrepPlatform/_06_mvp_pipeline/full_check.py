# -*- coding: utf-8 -*-
import json
path = r"D:\92_products\SPDT-004_EduContent\PT-037_AdaptivePrepPlatform\_03_subject_packs\cafa_calligraphy_2026\knowledge\kb_vocab_enhanced.json"
with open(path, "r", encoding="utf-8") as f:
    data = json.load(f)

entries = []
for mod_data in data["modules"].values():
    for items in mod_data.values():
        for item in items:
            if item.get("kb_id", "").startswith("KB_CAFA_S"):
                entries.append(item)

with_hp = [e for e in entries if e.get("structured_content", {}).get("historical_period")]
print(f"Total with historical_period: {len(with_hp)}")
for e in with_hp:
    print(f"  {e['kb_id']} ({e['concept']})")
