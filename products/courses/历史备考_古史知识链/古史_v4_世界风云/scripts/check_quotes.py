# -*- coding: utf-8 -*-
import re, os

BASE = os.path.dirname(os.path.abspath(__file__))

files = [
    "古史_v4_ep01_帝国的崩塌.py",
    "古史_v4_ep02_赤旗与铁幕的升起.py",
    "古史_v4_ep05_帝国的黄昏.py",
    "古史_v4_ep06_新战国时代.py",
]

for fname in files:
    fpath = os.path.join(BASE, fname)
    data = open(fpath, encoding="utf-8").read()
    
    # Find consecutive double quotes (Python syntax killers)
    triples = [(m.start(), m.group()) for m in re.finditer(r'\"{3,}', data)]
    if triples:
        print(f"\n{fname} - triple+ quotes found:")
        for pos, g in triples:
            line_num = data[:pos].count('\n') + 1
            ctx = data[max(0,pos-20):pos+40].replace('\n','\\n')
            print(f"  line {line_num}: ...{ctx}...")
    
    # Try to compile
    try:
        compile(data, fpath, 'exec')
        print(f"{fname}: OK")
    except SyntaxError as e:
        print(f"{fname}: SYNTAX ERROR at line {e.lineno}: {e.msg}")
        if e.text:
            print(f"  {e.text.rstrip()}")
