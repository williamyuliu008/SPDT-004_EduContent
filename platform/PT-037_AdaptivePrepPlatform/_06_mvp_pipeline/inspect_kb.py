# -*- coding: utf-8 -*-
import sys, json
sys.path.insert(0, '_01_platform_core')
from knowledge_base.knowledge_base import KnowledgeBase

kb = KnowledgeBase.from_pack('_03_subject_packs/cafa_calligraphy_2026')

print("=== 书法史知识条目 ===")
s_entries = [(k, v) for k, v in kb._kb_entries.items()]
for k, v in s_entries[:25]:
    tags = ','.join(v.tags[:3]) if v.tags else ''
    print(f"  {k}  {v.concept}  [标签:{tags}]")
print(f"共 {len(s_entries)} 条")

print("\n=== 译篆条目 ===")
t_entries = list(kb._translation_entries.items())[:10]
for k, v in t_entries:
    defn = v.definition[:40] if v.definition else ''
    print(f"  {k}  {v.concept}  {defn}")
print(f"共 {len(kb._translation_entries)} 条")

print("\n=== 句读文本 ===")
for k, v in list(kb._punctuation_texts.items())[:5]:
    print(f"  {k}  [{v.difficulty}]  {v.source}  |  {v.raw_text[:30]}")
print(f"共 {len(kb._punctuation_texts)} 条")

print("\n=== 错题剧本 ===")
for k, v in list(kb._error_scripts.items())[:5]:
    conflict = str(v.script.get('conflict', ''))[:40]
    print(f"  {k}  {v.error_type}  |  {conflict}")
print(f"共 {len(kb._error_scripts)} 条")
