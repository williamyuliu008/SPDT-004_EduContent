# -*- coding: utf-8 -*-
import os, glob

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

EP_FILES = [
    '古史_v3_ep01_天朝崩塌.py',
    '古史_v3_ep02_帝国挽歌.py',
    '古史_v3_ep03_觉醒年代.py',
    '古史_v3_ep04_共和新生.py',
]

def fix_inner_quotes(content):
    result = []
    i = 0
    n = len(content)
    
    while i < n:
        c = content[i]
        
        # Triple-quoted string: keep as-is but convert inner curly quotes
        if content[i:i+3] in ('"""', "'''"):
            quote = content[i:i+3]
            result.append(quote)
            i += 3
            while i < n:
                if content[i:i+3] == quote[:3]:
                    result.append(content[i:i+3])
                    i += 3
                    break
                # Convert inner curly quotes to Chinese bracket
                if content[i] == '"':
                    result.append('\u300c')  # replace with U+300C
                else:
                    result.append(content[i])
                i += 1
            continue
        
        # Double-quoted single-line string
        if c == '"':
            result.append(c)
            i += 1
            while i < n:
                c2 = content[i]
                if c2 == '\\':
                    result.append(c2)
                    if i + 1 < n:
                        result.append(content[i+1])
                        i += 2
                    continue
                if c2 == '"':
                    result.append(c2)
                    i += 1
                    break
                result.append(c2)
                i += 1
            continue
        
        # Single-quoted string
        if c == "'":
            result.append(c)
            i += 1
            while i < n:
                c2 = content[i]
                if c2 == '\\':
                    result.append(c2)
                    if i + 1 < n:
                        result.append(content[i+1])
                        i += 2
                    continue
                if c2 == "'":
                    result.append(c2)
                    i += 1
                    break
                result.append(c2)
                i += 1
            continue
        
        result.append(c)
        i += 1
    
    return ''.join(result)


for fname in EP_FILES:
    fpath = os.path.join(SCRIPT_DIR, fname)
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    fixed = fix_inner_quotes(content)
    
    try:
        compile(fixed, fname, 'exec')
        print('OK:', fname)
    except SyntaxError as e:
        print('FAIL:', fname, str(e)[:150])
    
    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(fixed)
