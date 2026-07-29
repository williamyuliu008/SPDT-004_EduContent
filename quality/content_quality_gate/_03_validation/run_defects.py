"""Run G-01/G-03/G-04 against defect samples D01-D03"""
import sys, os, json, tempfile
sys.path.insert(0, r'D:\6_agent_project\projects\content_quality_gate\_02_compiler\static')
from scene_quality_gate import gate_G01_style_guide, gate_G03_content_nonempty, gate_G04_text_overflow

# D01: 裸Manim API
fp = r'D:\6_agent_project\projects\content_quality_gate\_01_golden_tests\defects\D01_raw_manim.py'
ok, violations = gate_G01_style_guide(fp)
print(f'D01 G-01: {"FAIL" if not ok else "PASS"} (expected: FAIL)')
for v in violations[:3]:
    print(f'  {v}')

# D02: empty wrong_text
data = {'scene_type': 'contrast', 'content': {'title': '测试', 'wrong_text': '', 'right_text': '测试'}}
d = tempfile.mkdtemp()
fp = os.path.join(d, 'test.json')
with open(fp, 'w', encoding='utf-8') as f:
    json.dump(data, f)
ok, issues = gate_G03_content_nonempty(d)
found = any('wrong_text' in i.lower() or 'right_text' in i.lower() or '空' in i for i in issues)
print(f'D02 G-03: {"FAIL" if not ok else "PASS"} (expected: FAIL)')
for i in issues[:3]:
    print(f'  {i}')

# D03: long label
data = {'scene_type': 'diagram', 'content': {'title': '测试', 'diagram': {'nodes': [{'label': '这是一个非常长的标签文本超过了二十个字的限制来测试溢出检测'}]}}}
d2 = tempfile.mkdtemp()
fp2 = os.path.join(d2, 'test.json')
with open(fp2, 'w', encoding='utf-8') as f:
    json.dump(data, f)
ok, warnings = gate_G04_text_overflow(d2)
found = any('超' in w or 'overflow' in w.lower() or 'limit' in w.lower() for w in warnings)
print(f'D03 G-04: {"WARN" if not ok else "PASS"} (expected: WARN)')
for w in warnings[:3]:
    print(f'  {w}')
