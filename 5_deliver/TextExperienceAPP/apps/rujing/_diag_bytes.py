import json

path = r'D:/2_products/education/SPDT-004_EduContent/5_deliver/TextExperienceAPP/apps/rujing/entry/src/main/resources/rawfile/geo_cards.json'
with open(path, 'rb') as f:
    raw_bytes = f.read()

print(f'File size: {len(raw_bytes)} bytes')
print(f'First 3 bytes: {raw_bytes[:3].hex()}')

# Check around char 467
start = max(0, 467-30)
end = min(len(raw_bytes), 467+30)
print(f'Around char 467:')
print(f'  Bytes hex: {raw_bytes[start:end].hex()}')
print(f'  Bytes: {raw_bytes[start:end]}')

# Try utf-8 decode with error handling
try:
    decoded = raw_bytes.decode('utf-8')
    print('UTF-8 decode: OK')
except UnicodeDecodeError as e:
    print(f'UTF-8 Error: {e}')
    # Show the problematic area
    start = max(0, e.start-20)
    end = min(len(raw_bytes), e.start+20)
    print(f'  Around error: {raw_bytes[start:end]}')
