"""
提取 v3 所有 episode 的 chain narrative，生成链叙事 JSON
"""
import json, os, sys, re

# 搜索所有 v3 episode Python 文件
scripts_dir = r"D:\92_products\SPDT-004_EduContent\PT-038_TextExperience\历史_v3_墨山行\scripts"
meta_dir = r"D:\92_products\SPDT-004_EduContent\PT-038_TextExperience\历史_v3_墨山行"
output_path = r"D:\92_products\SPDT-001_Harmony\apps\rujing\entry\src\main\resources\rawfile"

# 从每个 episode py 提取 knowledge_chains
chains = {}

ep_files = sorted([f for f in os.listdir(scripts_dir) if f.startswith("历史_v3_ep") and f.endswith(".py")])

for ep_file in ep_files:
    ep_path = os.path.join(scripts_dir, ep_file)
    print(f"Processing: {ep_file}")
    
    with open(ep_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找 knowledge_chains 块
    kc_start = content.find('knowledge_chains')
    if kc_start < 0:
        print("  No knowledge_chains found, skipping")
        continue
    
    # 提取 knowledge_chains 内容 - 找到字典开始
    brace_start = content.find('{', kc_start)
    if brace_start < 0:
        continue
    
    # 尝试逐个解析 chain_0X 条目
    # 使用正则提取 chain_id, chain_title, narrative
    chain_blocks = re.findall(r'"chain_id":\s*"([^"]+)".*?"chain_title":\s*"([^"]+)".*?"narrative":\s*"""\s*(.*?)""",', content, re.DOTALL)
    
    for chain_id, chain_title, narrative in chain_blocks:
        # 清理 narrative
        narrative = narrative.strip()
        chains[chain_id] = {
            "chain_id": chain_id,
            "chain_title": chain_title,
            "narrative": narrative
        }
        print(f"  Extracted: {chain_id} ({chain_title}) - {len(narrative)} chars")

# Also try to load meta.json for additional chain info
meta_path = os.path.join(meta_dir, "meta.json")
if os.path.exists(meta_path):
    print(f"\nLoading meta.json...")
    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)
    print(f"  Meta keys: {list(meta.keys())}")
    
    # Check episodes array for chain info
    episodes = meta.get('episodes', [])
    for ep in episodes:
        ep_num = ep.get('ep', '?')
        ep_title = ep.get('title', '?')
        kc = ep.get('knowledge_chains', [])
        if kc:
            print(f"  Ep {ep_num} ({ep_title}): {len(kc)} chains")
            for chain in kc:
                cid = chain.get('chain_id', '')
                ctitle = chain.get('chain_title', '')
                if cid and cid not in chains:
                    chains[cid] = {
                        "chain_id": cid,
                        "chain_title": ctitle,
                        "narrative": ""
                    }
                    print(f"    Meta-only: {cid} ({ctitle})")

# 输出
result = list(chains.values())
print(f"\nTotal chains extracted: {len(result)}")

# 写入 JSON
os.makedirs(output_path, exist_ok=True)
out_file = os.path.join(output_path, "chain_narratives.json")
with open(out_file, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f"Written to: {out_file}")
print(f"File size: {os.path.getsize(out_file)} bytes")
