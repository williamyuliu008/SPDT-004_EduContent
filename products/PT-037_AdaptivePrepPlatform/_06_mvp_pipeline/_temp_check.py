import json, os

path = r'D:\92_products\SPDT-004_EduContent\PT-037_AdaptivePrepPlatform\_03_subject_packs\cafa_calligraphy_2026\scripts\error_scripts.json'
with open(path, encoding='utf-8') as f:
    data = json.load(f)

scripts = data['scripts']
print(f'scripts总条数: {len(scripts)}')

empty = [s for s in scripts if not s.get('script', {})]
filled = [s for s in scripts if s.get('script', {})]
print(f'有内容: {len(filled)} 条')
print(f'空骨架: {len(empty)} 条\n')

for s in empty:
    sid = s['script_id']
    kb = s['trigger_kb_id']
    qtype = s.get('question_type', '')
    conflict = ''
    q = s.get('question', {})
    if isinstance(q, dict):
        conflict = q.get('conflict', '')
        if isinstance(conflict, dict):
            conflict = conflict.get('conflict', '')
    print(f'{sid} | kb:{kb} | type:{qtype} | conflict:{str(conflict)[:60]}')
