import json, re

path = r'D:/2_products/education/SPDT-004_EduContent/5_deliver/TextExperienceAPP/apps/rujing/entry/src/main/resources/rawfile/geo_cards.json'

with open(path, 'r', encoding='utf-8') as f:
    raw = f.read()

print(f'Original size: {len(raw)}')

# Strip all control characters except \n and \t
# JSON spec: control chars are U+0000 to U+001F except \t(\u0009), \n(\u000A), \r(\u000D)
# But \r inside a string value is invalid JSON per RFC 8259
fixed = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', raw)
# Also strip lone \r if present (they come from Windows line endings inside strings)
fixed = fixed.replace('\r', '')

print(f'Fixed size: {len(fixed)}')

# Validate
try:
    obj = json.loads(fixed)
    print('JSON valid!')
    print(f'  Cards: {len(obj["cards"])}')
    print(f'  Chains: {obj["total_chains"]}')
    for c in obj['cards'][:4]:
        print(f'  - [{c["id"]}] chain={c["chain_title"]} title={c["title"]}')
except json.JSONDecodeError as e:
    print(f'Still invalid: {e}')
    sys.exit(1)

# Save with no BOM, no \r, Unix line endings
with open(path, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(obj, f, ensure_ascii=False, indent=2)
print('Saved!')
