# -*- coding: utf-8 -*-
import os, tokenize, io

fname = os.path.join(os.path.dirname(__file__), "古史_v3_ep01_天朝崩塌.py")
with open(fname, "rb") as f:
    raw = f.read()

# Find all non-ASCII chars and their positions in line 46
lines = raw.decode("utf-8").split("\n")
line46 = lines[45]

print("All non-ASCII chars in line 46:")
for i, c in enumerate(line46):
    if ord(c) > 127:
        print(f"  pos {i}: U+{ord(c):04X} = {c!r}")

# Also print the raw bytes around position 25-45
print("\nBytes around the description key (pos 20-40):")
print(repr(line46[20:60]))
