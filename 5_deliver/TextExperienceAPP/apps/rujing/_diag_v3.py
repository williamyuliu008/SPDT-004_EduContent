import json

path = r'D:/2_products/education/SPDT-004_EduContent/5_deliver/TextExperienceAPP/apps/rujing/entry/src/main/resources/rawfile/geo_cards.json'
out = r'D:/2_products/education/SPDT-004_EduContent/5_deliver/TextExperienceAPP/apps/rujing/_diag_v3_out.txt'

with open(path, 'r', encoding='utf-8') as f:
    raw = f.read()

lines = raw.split('\n')
print(f'Total lines: {len(lines)}')
print(f'Line 13 length: {len(lines[12]) if len(lines) > 12 else "N/A"}')

# Show lines 11-15
for i in range(10, min(16, len(lines))):
    line = lines[i]
    # Find control chars
    ctrl = [(j, ord(c), repr(c)) for j, c in enumerate(line) if ord(c) < 32 and c not in '\n\t']
    ctrl_str = f' CONTROLS: {ctrl}' if ctrl else ''
    print(f'Line {i+1}: len={len(line)}{ctrl_str}')
    # Show first 60 chars
    preview = line[:80].replace('\r', '\\r')
    print(f'  Preview: {repr(preview)}')
