# -*- coding: utf-8 -*-
import json, os
from pathlib import Path

PT_ROOT = Path(r"D:\92_products\SPDT-004_EduContent\PT-037_AdaptivePrepPlatform")
KB_PATH_IN  = PT_ROOT / "_03_subject_packs" / "cafa_calligraphy_2026" / "knowledge" / "kb_vocab.json"
API_KEY_PATH = Path(r"D:\_CEO\bulletin\SECRET_KEY\zhipu_api.txt")

if API_KEY_PATH.exists():
    key = API_KEY_PATH.read_text(encoding="utf-8").strip()
    os.environ["ZHIPU_API_KEY"] = key
    print(f"API key: {key[:8]}...")
else:
    print("No API key found, will use mock mode")

with open(KB_PATH_IN, "r", encoding="utf-8") as f:
    data = json.load(f)

entries = []
for mod_name, mod_data in data["modules"].items():
    for cat_name, items in mod_data.items():
        for item in items:
            if item.get("kb_id", "").startswith("KB_CAFA_S"):
                entries.append(item)

print(f"Total KB_CAFA_S entries: {len(entries)}")
print(f"Entry 0: {entries[0]['kb_id']} - {entries[0]['concept']}")
print(f"Entry 1: {entries[1]['kb_id']} - {entries[1]['concept']}")
print(f"Entry 2: {entries[2]['kb_id']} - {entries[2]['concept']}")
print("JSON OK, ready to run batch_enhance.py")
