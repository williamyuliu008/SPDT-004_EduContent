"""Bulk defect verification — D04 through D09 (non-render tests)"""
import sys, os, json, tempfile
sys.path.insert(0, r'D:\6_agent_project\projects\content_quality_gate\_02_compiler\static')
from scene_quality_gate import gate_G03_content_nonempty, gate_G04_text_overflow

results = {}

# D04: diagram.nodes empty
data = {'scene_type': 'diagram', 'content': {'title': '测试', 'diagram': {'nodes': []}}}
d = tempfile.mkdtemp()
with open(os.path.join(d, 'd04.json'), 'w', encoding='utf-8') as f:
    json.dump(data, f)
ok, issues = gate_G03_content_nonempty(d)
results['D04'] = ('FAIL' if not ok else 'PASS', issues[:2])

# D05: steps empty
data = {'scene_type': 'steps', 'content': {'title': '测试', 'steps': []}}
d2 = tempfile.mkdtemp()
with open(os.path.join(d2, 'd05.json'), 'w', encoding='utf-8') as f:
    json.dump(data, f)
ok, issues = gate_G03_content_nonempty(d2)
results['D05'] = ('FAIL' if not ok else 'PASS', issues[:2])

# D06: wrong_text empty for contrast
data = {'scene_type': 'contrast', 'content': {'title': '测试', 'wrong_text': '有内容', 'right_text': ''}}
d3 = tempfile.mkdtemp()
with open(os.path.join(d3, 'd06.json'), 'w', encoding='utf-8') as f:
    json.dump(data, f)
ok, issues = gate_G03_content_nonempty(d3)
results['D06'] = ('FAIL' if not ok else 'PASS', issues[:2])

# D07: title empty
data = {'scene_type': 'concept', 'content': {'title': '', 'body_lines': ['内容']}}
d4 = tempfile.mkdtemp()
with open(os.path.join(d4, 'd07.json'), 'w', encoding='utf-8') as f:
    json.dump(data, f)
ok, issues = gate_G03_content_nonempty(d4)
results['D07'] = ('FAIL' if not ok else 'PASS', issues[:2])

# D09: pixel width > 260 (use 30-char Chinese string)
data = {'scene_type': 'diagram', 'content': {'title': '测试', 'diagram': {'nodes': [{'label': '这是一个极其冗长且过度详细的标签文本用于测试文本溢出检测'}]}}}
d5 = tempfile.mkdtemp()
with open(os.path.join(d5, 'd09.json'), 'w', encoding='utf-8') as f:
    json.dump(data, f)
ok, warnings = gate_G04_text_overflow(d5)
results['D09'] = ('WARN' if not ok else 'PASS', warnings[:2])

for sid, (status, details) in results.items():
    expected = 'FAIL' if sid != 'D09' else 'WARN'
    match = 'OK' if status == expected else 'MISMATCH'
    print(f'{sid}: {status} (expected: {expected}) [{match}]')
    for detail in details:
        print(f'  {detail}')
