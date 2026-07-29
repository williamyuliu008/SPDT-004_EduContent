# -*- coding: utf-8 -*-
import json, os

fname = os.path.join(os.path.expanduser('~'), 'Desktop', '古史_v3_全16链卡片包.json')
with open(fname, 'r', encoding='utf-8') as f:
    pkg = json.load(f)

# 打印几条样本
print('=== 节点卡样本（第一条鸦片战争链） ===')
for nc in pkg['node_cards'][:3]:
    print('ID:', nc['card_id'])
    print('Q:', nc['front'][:60])
    print('A:', nc['back_core'][:80])
    print()

print('=== 心法卡样本（第一条） ===')
sc = pkg['strategy_cards'][0]
print('ID:', sc['card_id'])
print('Q:', sc['front'][:60])
print('Step:', sc['thinking_steps'][:100])
print()

print('=== 链卡样本（第一条） ===')
cc = pkg['chain_cards'][0]
print('Chain:', cc['chain_id'])
print('Type:', cc['chain_type'])
print('Pattern:', cc['core_pattern'][:80])
print('Narrative:', cc['narrative_snippet'][:100])
