# -*- coding: utf-8 -*-
"""Fix curly quotes in Python data files"""
import os, glob

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def fix_curly_quotes(content):
    result = []
    for c in content:
        if c == '\u201c' or c == '\u201d':
            result.append('\u300c')  # 「
        else:
            result.append(c)
    return ''.join(result)

for fname in glob.glob(os.path.join(SCRIPT_DIR, "古史_v3_ep*.py")):
    with open(fname, 'r', encoding='utf-8') as f:
        content = f.read()
    fixed = fix_curly_quotes(content)
    try:
        compile(fixed, fname, 'exec')
        print("OK:", os.path.basename(fname))
    except SyntaxError as e:
        print("FAIL:", os.path.basename(fname), str(e)[:200])
    with open(fname, 'w', encoding='utf-8') as f:
        f.write(fixed)
