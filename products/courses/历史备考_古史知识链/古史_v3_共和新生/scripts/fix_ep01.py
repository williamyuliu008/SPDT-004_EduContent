# -*- coding: utf-8 -*-
"""Check and fix the specific problematic line in ep01"""
import os

fname = os.path.join(os.path.dirname(__file__), "古史_v3_ep01_天朝崩塌.py")
with open(fname, "r", encoding="utf-8") as f:
    lines = f.readlines()

line46 = lines[45]
print("Line 46 raw bytes:", line46[:200].encode("utf-8"))
print()

# Find ASCII " chars and their positions
for i, c in enumerate(line46):
    if c == '"':
        print(f"  ASCII quote at pos {i}: context = {repr(line46[max(0,i-5):i+6])}")
