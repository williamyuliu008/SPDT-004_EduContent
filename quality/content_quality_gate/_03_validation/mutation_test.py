"""Mutation Testing Framework — verify compiler catches injected defects"""
import sys, os, json, tempfile, subprocess, glob
sys.path.insert(0, r'D:\6_agent_project\projects\content_quality_gate\_02_compiler\static')
from scene_quality_gate import gate_G01_style_guide, gate_G03_content_nonempty, gate_G04_text_overflow

# Use P01 as base (correct: term_card "AI写作工具")
# Apply 5 mutations, each should be caught by at least one gate

mutations = []
results = {}

# M1: Empty title
m1 = json.dumps({'scene_type': 'concept', 'content': {'title': '', 'body_lines': ['写邮件', '写报告']}})
mutations.append(('M1', 'Empty title', m1, 'G-03'))

# M2: Title overflow (>15 chars)
m2 = json.dumps({'scene_type': 'concept', 'content': {'title': '这是一个超级长的标题文本测试溢出检测系统', 'body_lines': ['内容']}})
mutations.append(('M2', 'Title overflow 18 chars', m2, 'G-04'))

# M3: Missing body_lines and no teaching_boxes
m3 = json.dumps({'scene_type': 'concept', 'content': {'title': '测试'}})
mutations.append(('M3', 'No body_lines', m3, 'G-03'))

# M4: Diagram with missing nodes
m4 = json.dumps({'scene_type': 'diagram', 'content': {'title': '测试', 'diagram': {}}})
mutations.append(('M4', 'Diagram no nodes', m4, 'G-03'))

# M5: steps with one extremely long step
m5 = json.dumps({'scene_type': 'steps', 'content': {'title': '测试', 'steps': ['步骤一', '这是一个极其冗长且过度详细的步骤描述文本用于测试溢出检测']}})
mutations.append(('M5', 'Steps overflow', m5, 'G-04'))

for mid, desc, mjson, target in mutations:
    d = tempfile.mkdtemp()
    fp = os.path.join(d, f'mutation_{mid}.json')
    with open(fp, 'w', encoding='utf-8') as f:
        f.write(mjson)
    
    detected = False
    detail = ''
    
    if target == 'G-03':
        ok, issues = gate_G03_content_nonempty(d)
        detected = not ok
        detail = issues[0] if issues else 'no issues'
    elif target == 'G-04':
        ok, warnings = gate_G04_text_overflow(d)
        detected = not ok
        detail = warnings[0] if warnings else 'no warnings'
    
    results[mid] = detected
    print(f'{mid} [{desc}]: target={target} -> {"CAUGHT" if detected else "MISSED"}')
    if detail:
        print(f'  {detail}')

# Also test M6: raw Manim code (G-01)
d = tempfile.mkdtemp()
m6_fp = os.path.join(d, 'm6_raw.py')
with open(m6_fp, 'w', encoding='utf-8') as f:
    f.write("from manim import *\nclass M6(Scene):\n    def construct(self):\n        t=Text('x')\n        b=Rectangle()\n        t.next_to(b, DOWN)\n        self.add(t,b)\n")
ok, violations = gate_G01_style_guide(m6_fp)
results['M6'] = not ok
print(f'M6 [Raw .next_to()]: target=G-01 -> {"CAUGHT" if not ok else "MISSED"}')
for v in violations[:2]:
    print(f'  {v}')

detected = sum(1 for v in results.values() if v)
total = len(results)
print(f'\nMutation Detection Rate: {detected}/{total} ({detected/total*100:.0f}%)')
