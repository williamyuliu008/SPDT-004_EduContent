"""P0-C.5 修 6 张元学习 chain_id"""
import json
from pathlib import Path

meta_dir = Path(r"D:\4_data\knowledge_cards\元学习")

FIXES = {
    "meta_009.json": "meta_learning_active_recall",
    "meta_012.json": "meta_learning_error_book",
    "meta_013.json": "meta_learning_deliberate_practice",
    "meta_016.json": "meta_learning_metacognition",
    "meta_018.json": "meta_learning_transfer",
    "meta_020.json": "meta_learning_growth_mindset",
}

for fname, new_chain in FIXES.items():
    p = meta_dir / fname
    if not p.exists():
        print(f"  SKIP: {fname}")
        continue
    data = json.loads(p.read_text(encoding="utf-8"))
    old_chain = data.get("chain_id", "")
    data["chain_id"] = new_chain
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  FIXED: {fname} | {old_chain} -> {new_chain}")

# 验证
print("\n=== 修后 chain_id 分布 ===")
chains = set()
for f in sorted(meta_dir.glob("meta_*.json")):
    d = json.loads(f.read_text(encoding="utf-8"))
    chains.add(d.get("chain_id", ""))
print(f"  唯一 chain_id: {len(chains)}")
print(f"  链列表:")
for c in sorted(chains):
    print(f"    {c}")