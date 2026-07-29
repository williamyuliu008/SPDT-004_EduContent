# -*- coding: utf-8 -*-
"""
古史卷一·革与鼎  卡片自动生成器
============================================================
从古史_v1 6集 episode Python 数据文件中提取 knowledge_chains，
自动派生三类卡片：节点卡 + 心法卡 + 链卡。

输出：
  - 古史_v1_全12链卡片包.json
  - 古史_v1_全12链_Anki导入.csv
"""

import os, json, csv

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def load_all_episodes():
    episodes = []
    files = [
        "古史_ep01_封邦建国.py",
        "古史_ep02_百家争鸣.py",
        "古史_ep03_天下一统.py",
        "古史_ep04_汉武雄图.py",
        "古史_ep05_胡汉之间.py",
        "古史_ep06_盛唐拐点.py",
    ]
    for fname in files:
        fpath = os.path.join(SCRIPT_DIR, fname)
        try:
            ns = {}
            with open(fpath, encoding="utf-8") as f:
                code = f.read()
            exec(compile(code, fpath, 'exec'), ns)
            ep_data = ns['get_data']()
            episodes.append(ep_data)
        except Exception as e:
            print(f"[WARN] {fname}: {e}")
    return episodes

def derive_node_cards(chain, ep):
    cards = []
    for node in chain.get('key_nodes', []):
        card_id = f"H_古1_{chain['chain_id'].split('_')[-2]}_{chain['chain_id'].split('_')[-1]}_{node['node_id'].split('_')[-1]}"
        front = f"[{chain['chain_id']}] {node['node_title']}"
        back = node.get('content', '')
        if node.get('exam_weight'):
            back += f"\n\n【{node['exam_weight']}考点】"
        cards.append({"card_id": card_id, "type": "node", "front": front, "back": back,
                       "chain_id": chain['chain_id'], "ep": ep.get('episode','?'),
                       "source": ep.get('title','')})
    return cards

def derive_strategy_cards(chain, ep):
    cards = []
    ctype = chain.get('chain_type', '影响类')
    ep_num = ep.get('episode', '?')
    chain_num = chain['chain_id'].split('_')[-1]
    prefix = chain['chain_id'].split('_')[1]

    # 心法1：原因/变革类 → 为什么会发生？
    if ctype in ('原因类', '变革类', '制度类'):
        card_id = f"S_古1_{prefix}_{chain_num}_01"
        front = f"[{chain['chain_id']}] {chain['chain_title']}\n为什么这件事会发生？"
        back = chain.get('cause_summary', chain.get('strategy', '【请补充原因分析】'))
        if chain.get('memorization_tips'):
            back += f"\n\n【记忆技巧】{chain['memorization_tips']}"
        cards.append({"card_id": card_id, "type": "strategy_cause", "front": front, "back": back,
                       "chain_id": chain['chain_id'], "ep": ep_num, "source": ep.get('title','')})

    # 心法2：影响/变革类 → 产生了什么后果？
    if ctype in ('影响类', '变革类'):
        card_id = f"S_古1_{prefix}_{chain_num}_02"
        front = f"[{chain['chain_id']}] {chain['chain_title']}\n这件事产生了什么后果？"
        back = chain.get('impact_summary', '【请补充影响分析】')
        cards.append({"card_id": card_id, "type": "strategy_impact", "front": front, "back": back,
                       "chain_id": chain['chain_id'], "ep": ep_num, "source": ep.get('title','')})

    # 心法3：变革类专属
    if ctype == '变革类':
        card_id = f"S_古1_{prefix}_{chain_num}_03"
        front = f"[{chain['chain_id']}] {chain['chain_title']}\n变革的关键转折点是什么？"
        back = chain.get('strategy', '【请补充变革关键节点】')
        cards.append({"card_id": card_id, "type": "strategy_turning", "front": front, "back": back,
                       "chain_id": chain['chain_id'], "ep": ep_num, "source": ep.get('title','')})

    return cards

def derive_chain_card(chain, ep):
    card_id = f"L_古1_{chain['chain_id'].split('_')[1]}_{chain['chain_id'].split('_')[-1]}"
    front = f"【链卡】{chain['chain_id']} {chain['chain_title']}"
    back = f"类型：{chain.get('chain_type','未知')}\n\n关键节点："
    for n in chain.get('key_nodes', []):
        back += f"\n• {n['node_title']}"
    back += f"\n\n{chain.get('strategy','')}"
    return {"card_id": card_id, "type": "chain", "front": front, "back": back,
            "chain_id": chain['chain_id'], "ep": ep.get('episode','?'), "source": ep.get('title','')}

def generate_csv(cards, out_path):
    with open(out_path, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f)
        w.writerow(['card_id', 'type', 'front', 'back', 'chain_id', 'ep', 'source'])
        for c in cards:
            w.writerow([c['card_id'], c['type'], c['front'], c['back'],
                         c.get('chain_id',''), c.get('ep',''), c.get('source','')])

def main():
    print("=" * 60)
    print("古史卷一·革与鼎  卡片自动生成器")
    print("=" * 60)
    episodes = load_all_episodes()
    print(f"已加载 {len(episodes)} 集")

    all_cards = []
    chain_count = 0
    for ep in episodes:
        for chain in ep.get('knowledge_chains', []):
            all_cards.extend(derive_node_cards(chain, ep))
            all_cards.extend(derive_strategy_cards(chain, ep))
            all_cards.append(derive_chain_card(chain, ep))
            chain_count += 1

    node_cards = [c for c in all_cards if c['type'] == 'node']
    strat_cards = [c for c in all_cards if c['type'].startswith('strategy')]
    chain_cards  = [c for c in all_cards if c['type'] == 'chain']
    print(f"生成节点卡 {len(node_cards)} 张 | 心法卡 {len(strat_cards)} 张 | 链卡 {len(chain_cards)} 张")
    print(f"总链数：{chain_count}，总卡数：{len(all_cards)}")

    # JSON
    json_path = os.path.join(SCRIPT_DIR, "..", "..", "cards", "古史_v1_全12链卡片包.json")
    os.makedirs(os.path.dirname(json_path), exist_ok=True)
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump({"version": "1.0", "series": "革与鼎", "total_chains": chain_count,
                   "total_cards": len(all_cards), "cards": all_cards}, f, ensure_ascii=False, indent=2)
    print(f"[JSON] {json_path} ({os.path.getsize(json_path)//1024} KB)")

    # CSV
    csv_path = os.path.join(SCRIPT_DIR, "..", "..", "cards", "古史_v1_全12链_Anki导入.csv")
    generate_csv(all_cards, csv_path)
    print(f"[Anki CSV] {csv_path} ({os.path.getsize(csv_path)//1024} KB, {len(all_cards)} cards)")

    print("\n[OK] All done!")

if __name__ == '__main__':
    main()
