# -*- coding: utf-8 -*-
"""生成 political_cards.json（App rawfile 入口包）"""
import json, os

OUT = r'D:\2_products\education\SPDT-004_EduContent\5_deliver\TextExperienceAPP\apps\rujing\entry\src\main\resources\rawfile\political_cards.json'

def write_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# 16条链的配置（chain_id → chain_title）
CHAINS = [
    ('POLI_经济_商品货币', '商品与货币'),
    ('POLI_经济_生产消费', '生产与消费'),
    ('POLI_经济_分配保障', '分配与社保'),
    ('POLI_经济_市场经济', '市场经济'),
    ('POLI_政治_国家公民', '国家与公民'),
    ('POLI_政治_政党制度', '政党制度'),
    ('POLI_政治_人大制度', '人大制度'),
    ('POLI_政治_国际社会', '国际社会'),
    ('POLI_哲学_唯物论', '唯物论基础'),
    ('POLI_哲学_唯物辩证', '唯物辩证法'),
    ('POLI_哲学_认识实践', '认识与实践'),
    ('POLI_哲学_历史唯物', '历史唯物主义'),
    ('POLI_法律_公民权利', '公民权利义务'),
    ('POLI_法律_法律基础', '法律基础'),
    ('POLI_时事_国内热点', '国内时政热点'),
    ('POLI_时事_国际热点', '国际时政热点'),
]

# 为每条链生成 1 个 NODE 卡 + 1 个 STRATEGY 卡
node_cards = []
strategy_cards = []

for i, (chain_id, chain_title) in enumerate(CHAINS):
    num = i + 1

    # NODE 卡：链入门概念
    node_cards.append({
        'card_id': f'POLI_N{num:03d}',
        'chain_id': chain_id,
        'chain_title': chain_title,
        'card_type': 'node',
        'chain_role': 'entry',
        'front': f'{chain_title}：核心概念是什么？',
        'back_core': f'{chain_title}是高考思想政治的重要模块，考查学生运用基本原理分析社会现象的能力。',
        'back_detail': '',
        'tags': ['#' + chain_id.split('_')[1], '#难度_中阶'],
        'difficulty': 2
    })

    # STRATEGY 卡：方法论
    strategy_cards.append({
        'card_id': f'POLI_S{num:03d}',
        'chain_id': chain_id,
        'chain_title': chain_title,
        'card_type': 'strategy',
        'chain_role': 'method',
        'front': f'解答{chain_title}类题目的一般思路是什么？',
        'back_core': 'Step 1: 明确考点所属模块 → Step 2: 提取材料关键词 → Step 3: 调用对应原理 → Step 4: 结合材料分析 → Step 5: 规范表述作答',
        'back_detail': '',
        'tags': ['#方法论', '#难度_高阶'],
        'difficulty': 3
    })

pkg = {
    'interface_version': '3.0',
    'package_id': 'political_gaokao_2026',
    'package_title': '高考思想政治知识包',
    'kb_source': {
        'pack_id': 'political_gaokao_2026',
        'kb_version': '1.0.0',
        'generated_at': '2026-08-02',
        'generator': 'Mavis AI Team'
    },
    'total_chains': 16,
    'total_cards': len(node_cards) + len(strategy_cards),
    'node_cards': node_cards,
    'strategy_cards': strategy_cards,
    'chain_cards': []
}

write_json(OUT, pkg)
print(f'[OK] political_cards.json: {len(node_cards)} node + {len(strategy_cards)} strategy = {pkg["total_cards"]} cards')
