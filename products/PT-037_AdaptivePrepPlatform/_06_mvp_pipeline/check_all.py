# -*- coding: utf-8 -*-
import json
path = r"D:\92_products\SPDT-004_EduContent\PT-037_AdaptivePrepPlatform\_03_subject_packs\cafa_calligraphy_2026\knowledge\kb_vocab_enhanced.json"
with open(path, "rb") as f:
    raw = f.read()
print(f"File size: {len(raw)} bytes")

with open(path, "r", encoding="utf-8") as f:
    data = json.load(f)

entries = []
for mod_name, mod_data in data["modules"].items():
    for cat_name, items in mod_data.items():
        for item in items:
            if item.get("kb_id", "").startswith("KB_CAFA_S"):
                entries.append(item)

total = len(entries)
with_hp = [e for e in entries if e.get("structured_content", {}).get("historical_period")]
real_bg = [e for e in entries if e.get("structured_content", {}).get("background") and not str(e["structured_content"]["background"]).startswith("LLMResponse") and len(e["structured_content"].get("background", "")) > 50]
with_at = [e for e in entries if e.get("answer_template")]

print(f"Total: {total} | hp:{len(with_hp)} | bg:{len(real_bg)} | at:{len(with_at)}")
print()
print("Entries with background (real content):")
for e in real_bg:
    print(f"  {e['kb_id']} | {e['concept']} | bg_len={len(e['structured_content'].get('background',''))}")

# Find where to resume
last_done = None
for i, e in enumerate(entries):
    if e.get("structured_content", {}).get("historical_period"):
        last_done = i
print(f"\nLast entry with hp: index={last_done} ({entries[last_done]['kb_id']})")
print(f"Resume from index: {last_done + 1}")
