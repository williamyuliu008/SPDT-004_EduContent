import json, sys

path = r'D:/2_products/education/SPDT-004_EduContent/5_deliver/TextExperienceAPP/apps/rujing/entry/src/main/resources/rawfile/geo_cards.json'

with open(path, 'rb') as f:
    raw_bytes = f.read()

print(f'File size: {len(raw_bytes)}')
print(f'First 20 bytes hex: {raw_bytes[:20].hex()}')

# Try different encodings
encodings = ['utf-8', 'utf-8-sig', 'utf-16', 'utf-16-le', 'utf-16-be', 'gbk', 'gb2312', 'big5']
for enc in encodings:
    try:
        decoded = raw_bytes.decode(enc)
        # Check if first line contains Chinese for geo series
        first_line = decoded.split('\n')[0]
        print(f'{enc}: OK, first 50 chars: {first_line[:80]}')
    except Exception as e:
        print(f'{enc}: FAIL - {e}')
