# -*- coding: utf-8 -*-
import os

fname = os.path.join(os.path.dirname(__file__), '古史_v3_ep01_天朝崩塌.py')
with open(fname, 'r', encoding='utf-8') as f:
    lines = f.readlines()

line = lines[45]
print('Line 46:')
print(line)
print()
print('Hex dump of first 80 chars:')
for i, c in enumerate(line[:80]):
    if ord(c) < 128:
        print(f'  {i}: ASCII {repr(c)} (0x{ord(c):02X})')
    else:
        print(f'  {i}: U+{ord(c):04X} = {c}')
