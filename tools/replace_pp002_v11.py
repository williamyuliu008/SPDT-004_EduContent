"""A: 替换 pp_002 v1.0 → v1.1"""
import sys
from pathlib import Path
sys.path.insert(0, r'D:\2_products\education\SPDT-004_EduContent\tools')
from math_4step_validator import validate_file, load_v12_chains

old = Path(r'D:\4_data\knowledge_cards\数学\4step\parent_problems\pp_002_正方体_找两条相交线_线面垂直.json')
v11 = Path(r'D:\4_data\knowledge_cards\数学\4step\parent_problems\pp_002_正方体_找两条相交线_线面垂直_v11.json')

if old.exists():
    old.unlink()
    print(f"removed v1.0: {old.name}")
v11.rename(v11.parent / 'pp_002_正方体_找两条相交线_线面垂直.json')
print(f"renamed v1.1 → standard name")

# Validate
chains = load_v12_chains()
ok, errors = validate_file(Path(r'D:\4_data\knowledge_cards\数学\4step\parent_problems\pp_002_正方体_找两条相交线_线面垂直.json'), 'parent_problem', set(chains.keys()))
print(f"validator: {'PASS' if ok else 'FAIL'}")
for e in errors:
    print(f"  - {e}")
