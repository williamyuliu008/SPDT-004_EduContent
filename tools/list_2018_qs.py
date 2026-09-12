"""列 2018 v1.1 20 题的 chain 分布，选 5 道覆盖不同方法的题"""
import json
from pathlib import Path

p = Path(r'C:\4_data\rujing_out\真题主库\2018_上海_历史_真题卡_v1.1_20题.json')
data = json.loads(p.read_text(encoding='utf-8'))
qs = data['questions']
print(f'Total: {len(qs)} questions\n')
for i, q in enumerate(qs, 1):
    chain_id = q.get('knowledge_chain', {}).get('chain_id_alignment', 'N/A')[:40]
    card_id = q['card_id']
    qtype = q.get('meta', {}).get('question_type', 'N/A')
    score = q.get('meta', {}).get('score', '?')
    stem = q.get('content', {}).get('stem', '')[:50]
    print(f'Q{i:2d} {card_id[:25]:25s} [{qtype[:6]:6s} {score}分] {chain_id:40s} | {stem}')
