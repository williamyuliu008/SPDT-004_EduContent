# -*- coding: utf-8 -*-
import json
path = r"D:\92_products\SPDT-004_EduContent\PT-037_AdaptivePrepPlatform\_03_subject_packs\cafa_calligraphy_2026\knowledge\kb_vocab_enhanced.json"
with open(path, "rb") as f:
    raw = f.read()

# Find line 648 (1-indexed) bytes
lines = raw.split(b"\n")
line = lines[647]  # 0-indexed
print("Line 648 length:", len(line))
print("Around col 116:", repr(line[111:126]))

# Count quote types
ascii_dq = line.count(b'"')
uc_201c = line.count(b'\xe2\x80\x9c')
uc_201d = line.count(b'\xe2\x80\x9d')
print(f"ASCII double quotes: {ascii_dq}")
print(f"U+201C count: {uc_201c}")
print(f"U+201D count: {uc_201d}")

# Try loading JSON
try:
    with open(path, "r", encoding="utf-8") as f:
        json.load(f)
    print("JSON loads OK")
except json.JSONDecodeError as e:
    print(f"JSON error at: {e}")
