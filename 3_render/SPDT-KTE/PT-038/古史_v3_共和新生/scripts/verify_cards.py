# -*- coding: utf-8 -*-
import json, os
from collections import Counter

fname = os.path.join(os.path.expanduser('~'), 'Desktop', '古史_v3_全16链卡片包.json')
with open(fname, 'r', encoding='utf-8') as f:
    pkg = json.load(f)

chains = pkg['chain_cards']
nodes = pkg['node_cards']
strats = pkg['strategy_cards']

print('=== 全16链卡片统计 ===')
for cc in chains:
    n_count = sum(1 for n in nodes if n['chain_id']==cc['chain_id'])
    s_count = sum(1 for s in strats if s['chain_id']==cc['chain_id'])
    print('  %s | %s (%s) -> %d节点+%d心法' % (
        cc['chain_id'], cc['chain_title'][:8], cc['episode_title'][:4], n_count, s_count))
print()
print('总计: %d节点 + %d心法 + %d链 = %d张' % (
    len(nodes), len(strats), len(chains), len(nodes)+len(strats)+len(chains)))
