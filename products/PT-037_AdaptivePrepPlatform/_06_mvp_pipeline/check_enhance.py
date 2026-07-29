# -*- coding: utf-8 -*-
import json
path = r"D:\92_products\SPDT-004_EduContent\PT-037_AdaptivePrepPlatform\_03_subject_packs\cafa_calligraphy_2026\knowledge\kb_vocab_enhanced.json"
with open(path, "rb") as f:
    raw = f.read()
print(f"File size: {len(raw)} bytes")

# Verify JSON is valid
try:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    print("JSON loads OK")

    entries = []
    for mod_name, mod_data in data["modules"].items():
        for cat_name, items in mod_data.items():
            for item in items:
                if item.get("kb_id", "").startswith("KB_CAFA_S"):
                    entries.append(item)

    total = len(entries)
    with_hp = [e for e in entries if e.get("structured_content", {}).get("historical_period")]
    with_bg = [e for e in entries if e.get("structured_content", {}).get("background")]
    real_bg = [e for e in with_bg if not str(e["structured_content"]["background"]).startswith("LLMResponse") and len(e["structured_content"].get("background", "")) > 50]
    with_at = [e for e in entries if e.get("answer_template")]

    print(f"Total KB_CAFA_S: {total}")
    print(f"With historical_period: {len(with_hp)}")
    print(f"With background field: {len(with_bg)}")
    print(f"With REAL background (>50 chars): {len(real_bg)}")
    print(f"With answer_template: {len(with_at)}")
    print()
    print("Recent entries with background:")
    for e in real_bg[-5:]:
        print(f"  {e['kb_id']}: {e['concept']} | bg_len={len(e['structured_content'].get('background',''))}")
except Exception as ex:
    print(f"ERROR: {ex}")
