# -*- coding: utf-8 -*-
path = r"D:\92_products\SPDT-004_EduContent\PT-037_AdaptivePrepPlatform\_06_mvp_pipeline\batch_enhance.py"
with open(path, "rb") as f:
    content = f.read()
ascii_dq = content.count(b'"')
uc_201c = content.count(b"\xe2\x80\x9c")
uc_201d = content.count(b"\xe2\x80\x9d")
print(f"ASCII double quotes: {ascii_dq}")
print(f"U+201C (curly left) count: {uc_201c}")
print(f"U+201D (curly right) count: {uc_201d}")
# Find lines around 131
lines = content.split(b"\n")
for i in range(128, 140):
    if i < len(lines):
        print(f"Line {i+1}: {repr(lines[i][:60])}")
# Check syntax
print("\nTrying to compile...")
try:
    import ast
    with open(path, "r", encoding="utf-8") as f:
        source = f.read()
    ast.parse(source)
    print("Syntax OK")
except SyntaxError as e:
    print(f"Syntax error at line {e.lineno}: {e.msg}")
    if e.text:
        print(f"  {repr(e.text)}")
