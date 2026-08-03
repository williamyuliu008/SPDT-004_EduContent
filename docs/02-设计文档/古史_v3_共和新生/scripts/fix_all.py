# -*- coding: utf-8 -*-
"""
Fix the "inner quote" problem in Python data files.
In the description/definition/narrative strings, we used curly-style quotes
that look like U+201C/U+201D but are actually ASCII quotes inside ASCII-quoted strings.
This script converts those inner quotes to Chinese 【】 brackets.
"""
import os, glob, re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Files that need fixing (all four episodes)
EP_FILES = [
    "古史_v3_ep01_天朝崩塌.py",
    "古史_v3_ep02_帝国挽歌.py",
    "古史_v3_ep03_觉醒年代.py",
    "古史_v3_ep04_共和新生.py",
]

def fix_inner_quotes(content):
    """
    For each string value in a Python dict, scan for unescaped ASCII double quotes
    that appear INSIDE the string (not at the string boundary), and replace them.
    
    Strategy: Split the file into token-like regions:
    - Python string literals: "..." or '...' 
    - Everything else (keep as-is)
    
    Inside string literals, convert ASCII double quotes to Chinese 【】.
    We need to handle: "..." (single-line) and """...""" (multi-line/triple-quoted)
    """
    result = []
    i = 0
    n = len(content)
    
    while i < n:
        c = content[i]
        
        # Check for triple-quoted string
        if content[i:i+3] in ('"""', "'''"):
            quote = content[i:i+3]
            result.append(quote)
            i += 3
            # Find closing triple quote
            while i < n:
                if content[i:i+3] == quote[:3]:
                    result.append(content[i:i+3])
                    i += 3
                    break
                # Replace inner ASCII double quotes with 【】
                if content[i] == '"':
                    result.append('\u300c')  # 「
                else:
                    result.append(content[i])
                i += 1
            continue
        
        # Check for single-quoted string
        if c in ('"', "'"):
            quote_char = c
            result.append(c)
            i += 1
            while i < n:
                c2 = content[i]
                if c2 == '\\':
                    # Escape sequence: copy both chars
                    result.append(c2)
                    if i + 1 < n:
                        result.append(content[i+1])
                        i += 2
                    else:
                        i += 1
                    continue
                if c2 == quote_char:
                    result.append(c2)
                    i += 1
                    break
                # Inner ASCII double quote in a single-quoted string: keep as-is
                result.append(c2)
                i += 1
            continue
        
        result.append(c)
        i += 1
    
    return ''.join(result)


for fname in EP_FILES:
    fpath = os.path.join(SCRIPT_DIR, fname)
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()
    
    fixed = fix_inner_quotes(content)
    
    # Validate
    try:
        compile(fixed, fname, "exec")
        print(f"OK: {fname}")
    except SyntaxError as e:
        print(f"FAIL: {fname} -> {e}")

    with open(fpath, "w", encoding="utf-8") as f:
        f.write(fixed)
