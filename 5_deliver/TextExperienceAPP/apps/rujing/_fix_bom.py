# -*- coding: utf-8 -*-
"""检查并修复 geo_cards.json 控制字符"""
import sys, json, re
sys.stdout.reconfigure(encoding='utf-8')
path = r'D:\2_products\education\SPDT-004_EduContent\5_deliver\TextExperienceAPP\apps\rujing\entry\src\main\resources\rawfile\geo_cards.json'
with open(path, encoding='utf-8') as f:
    content = f.read()
# Remove BOM if present
if content.startswith('\ufeff'):
    content = content[1:]
# Find control characters (except common whitespace)
problem_lines = []
for i, line in enumerate(content.split('\n'), 1):
    for j, c in enumerate(line):
        if ord(c) < 32 and c not in '\t':
            problem_lines.append((i, j, repr(c), line[max(0,j-20):j+20]))
if problem_lines:
    print(f'Found {len(problem_lines)} control chars:')
    for ln, col, char, ctx in problem_lines[:10]:
        print(f'  Line {ln}, col {col}: {char} in ...{ctx}...')
else:
    print('No control chars found')
# Try parse
try:
    json.loads(content)
    print('JSON OK')
except json.JSONDecodeError as e:
    print(f'Error: {e.msg} at char {e.pos}')
    print(f'Context: {repr(content[max(0,e.pos-50):e.pos+50])}')
