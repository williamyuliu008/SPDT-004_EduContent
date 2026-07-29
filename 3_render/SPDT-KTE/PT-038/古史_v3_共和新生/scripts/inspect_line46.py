# -*- coding: utf-8 -*-
import os, sys
# Prevent Windows console from messing with stdout encoding
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

fname = os.path.join(os.path.dirname(__file__), '古史_v3_ep01_\u5929\u671d\u58f4\u57a3.py')
with open(fname, 'r', encoding='utf-8') as f:
    lines = f.readlines()

line = lines[45]
print('LINE 46:')
print(repr(line[:150]))
