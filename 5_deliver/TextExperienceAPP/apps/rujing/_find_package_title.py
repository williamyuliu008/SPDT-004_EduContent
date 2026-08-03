import json, sys

path = r'D:/2_products/education/SPDT-004_EduContent/5_deliver/TextExperienceAPP/apps/rujing/entry/src/main/resources/rawfile/geo_cards.json'

with open(path, 'r', encoding='utf-8') as f:
    raw = f.read()

# Find package_title
idx = raw.find('"package_title"')
if idx >= 0:
    snippet = raw[idx:idx+80]
    print(f'package_title area: {snippet[:80]}')
    
# Find chain_title
idx2 = raw.find('"chain_title"')
if idx2 >= 0:
    snippet2 = raw[idx2:idx2+80]
    print(f'chain_title area: {snippet2[:80]}')

# Find back_core
idx3 = raw.find('"back_core"')
if idx3 >= 0:
    snippet3 = raw[idx3:idx3+100]
    print(f'back_core area: {snippet3[:100]}')
