"""Comprehensive Mutation Matrix — 30+ mutations across all gates"""
import sys, os, json, tempfile
sys.path.insert(0, r'D:\6_agent_project\projects\content_quality_gate\_02_compiler\static')
from scene_quality_gate import gate_G01_style_guide, gate_G03_content_nonempty, gate_G04_text_overflow

class Mutation:
    def __init__(self, mid, desc, target, mtype, payload, expected):
        self.mid = mid; self.desc = desc; self.target = target
        self.mtype = mtype; self.payload = payload; self.expected = expected
        self.detected = False; self.detail = ''

def g01_check(mid, code):
    d = tempfile.mkdtemp()
    fp = os.path.join(d, f'{mid}.py')
    with open(fp, 'w', encoding='utf-8') as f: f.write(code)
    ok, v = gate_G01_style_guide(fp)
    return not ok, v[0] if v else ''

def g03_check(mid, data):
    d = tempfile.mkdtemp()
    fp = os.path.join(d, f'{mid}.json')
    with open(fp, 'w', encoding='utf-8') as f: json.dump(data, f)
    ok, issues = gate_G03_content_nonempty(d)
    return not ok, issues[0] if issues else ''

def g04_check(mid, data):
    d = tempfile.mkdtemp()
    fp = os.path.join(d, f'{mid}.json')
    with open(fp, 'w', encoding='utf-8') as f: json.dump(data, f)
    ok, warnings = gate_G04_text_overflow(d)
    return not ok, warnings[0] if warnings else ''

# ====== G-01: Style Guide Violations (6 mutations) ======
M = []
M.append(Mutation('G01-M01','next_to()','G-01','boundary',
    "from manim import *\nclass T(Scene):\n def construct(self):\n  t=Text('x');b=Rectangle();t.next_to(b,DOWN);self.add(t,b)\n",
    'FAIL'))
M.append(Mutation('G01-M02','shift()','G-01','boundary',
    "from manim import *\nclass T(Scene):\n def construct(self):\n  t=Text('x');t.shift(UP);self.add(t)\n",
    'FAIL'))
M.append(Mutation('G01-M03','to_edge()','G-01','boundary',
    "from manim import *\nclass T(Scene):\n def construct(self):\n  t=Text('x');t.to_edge(UP);self.add(t)\n",
    'FAIL'))
M.append(Mutation('G01-M04','arrange()','G-01','boundary',
    "from manim import *\nclass T(Scene):\n def construct(self):\n  a=Text('a');b=Text('b');VGroup(a,b).arrange(DOWN);self.add(a,b)\n",
    'FAIL'))
M.append(Mutation('G01-M05','move_to()','G-01','boundary',
    "from manim import *\nclass T(Scene):\n def construct(self):\n  t=Text('x');t.move_to(ORIGIN);self.add(t)\n",
    'FAIL'))
# Correct code: should NOT trigger G-01
M.append(Mutation('G01-P01','clean style_guide only','G-01','correct',
    "from manim import *\nfrom style_guide import term_card\nclass T(Scene):\n def construct(self):\n  c=term_card('t',['k']);self.add(c)\n",
    'PASS'))

# ====== G-03: Content Emptiness (10 mutations) ======
G03 = [
    ('G03-M01','title empty-concept',{'scene_type':'concept','content':{'title':'','body_lines':['x']}},'FAIL'),
    ('G03-M02','title empty-steps',{'scene_type':'steps','content':{'title':'','steps':['a']}},'FAIL'),
    ('G03-M03','wrong_text empty',{'scene_type':'contrast','content':{'title':'t','wrong_text':'','right_text':'a'}},'FAIL'),
    ('G03-M04','right_text empty',{'scene_type':'contrast','content':{'title':'t','wrong_text':'a','right_text':''}},'FAIL'),
    ('G03-M05','diagram.nodes empty',{'scene_type':'diagram','content':{'title':'t','diagram':{'nodes':[]}}},'FAIL'),
    ('G03-M06','diagram missing',{'scene_type':'diagram','content':{'title':'t','diagram':{}}},'FAIL'),
    ('G03-M07','steps empty',{'scene_type':'steps','content':{'title':'t','steps':[]}},'FAIL'),
    ('G03-M08','body_lines empty concept',{'scene_type':'concept','content':{'title':'t'}},'FAIL'),
    ('G03-M09','body_lines empty summary',{'scene_type':'summary','content':{'title':'t'}},'FAIL'),
    # Correct: has all required fields
    ('G03-P01','all fields present',{'scene_type':'concept','content':{'title':'t','body_lines':['a','b']}},'PASS'),
]
for mid,d,data,exp in G03:
    M.append(Mutation(mid,d,'G-03','boundary' if exp=='FAIL' else 'correct',data,exp))

# ====== G-04: Text Overflow / Boundary Tests (12 mutations) ======
G04 = [
    ('G04-M01','title 16 chars (just over)',{'scene_type':'concept','content':{'title':'1234567890123456','body_lines':['x']}},'WARN'),
    ('G04-M02','title 15 chars (exact limit - PASS)',{'scene_type':'concept','content':{'title':'123456789012345','body_lines':['x']}},'PASS'),
    ('G04-M03','title 14 chars (under limit - PASS)',{'scene_type':'concept','content':{'title':'12345678901234','body_lines':['x']}},'PASS'),
    (\'G04-M04\',\'diagram label 21 ASCII chars (under 260px)\',{\'scene_type\':\'diagram\',\'content\':{\'title\':\'t\',\'diagram\':{\'nodes\':[{\'label\':\'123456789012345678901\'}]}}},\'PASS\'),
    ('G04-M05','diagram label 20 chars (exact)',{'scene_type':'diagram','content':{'title':'t','diagram':{'nodes':[{'label':'12345678901234567890'}]}}},'PASS'),
    ('G04-M06','steps chain 26 chars',{'scene_type':'steps','content':{'title':'t','steps':['12345678901234567890123456']}},'WARN'),
    ('G04-M07','steps chain 25 chars (exact)',{'scene_type':'steps','content':{'title':'t','steps':['1234567890123456789012345']}},'PASS'),
    (\'G04-M08\',\'Chinese 14 chars (=182px, under 260px)\',{\'scene_type\':\'diagram\',\'content\':{\'title\':\'t\',\'diagram\':{\'nodes\':[{\'label\':\'这是一段很长的中文标签文本测\'}]}}},\'PASS\'),
    ('G04-M09','Chinese 10 chars (=130px, under 260px)',{'scene_type':'diagram','content':{'title':'t','diagram':{'nodes':[{'label':'十个字的中文标签文本'}]}}},'PASS'),
    (\'G04-M10\',\'Mixed CJK+ASCII under 260px\',{\'scene_type\':\'diagram\',\'content\':{\'title\':\'t\',\'diagram\':{\'nodes\':[{\'label\':\'CJK+ASCII混合溢出文本测试ABCDEFGH\'}]}}},\'PASS\'),
    ('G04-M11','Very long Chinese 30 chars',{'scene_type':'diagram','content':{'title':'t','diagram':{'nodes':[{'label':'这是一个极其冗长且过度详细的标签文本用于测试严重的文本溢出检测场景'}]}}},'WARN'),
    ('G04-M12','causal_chain all under limit',{'scene_type':'steps','content':{'title':'t','steps':['短步骤1','短步骤2','短步骤3']}},'PASS'),
]
for mid,d,data,exp in G04:
    M.append(Mutation(mid,d,'G-04','boundary' if exp=='WARN' else 'correct',data,exp))

# ====== Combination Mutations (4 mutations: two defects at once) ======
COMBO = [
    ('C01','empty title + long label',{'scene_type':'diagram','content':{'title':'','diagram':{'nodes':[{'label':'这是一个极其冗长的标签'}]}}},['G-03','G-04']),
    ('C02','empty steps + long step',{'scene_type':'steps','content':{'title':'t','steps':['','这是一个极其冗长的步骤描述文本']}},['G-03','G-04']),
    ('C03','empty wrong_text + long title',{'scene_type':'contrast','content':{'title':'1234567890123456','wrong_text':'','right_text':'a'}},['G-03','G-04']),
    ('C04','all fields empty',{'scene_type':'diagram','content':{'title':'','diagram':{}}},['G-03']),
]
for mid,d,data,targets in COMBO:
    M.append(Mutation(mid,d,','.join(targets),'combo',data,'FAIL'))

# ====== Run All ======
results = {'ok':[], 'miss':[], 'false_pos':[]}
for m in M:
    if m.target.startswith('G-01'):
        m.detected, m.detail = g01_check(m.mid, m.payload)
    elif m.target.startswith('G-03') or 'G-03' in m.target:
        m.detected, m.detail = g03_check(m.mid, m.payload)
    elif m.target.startswith('G-04') or 'G-04' in m.target:
        m.detected, m.detail = g04_check(m.mid, m.payload)
    
    # For correct samples: detected should be False
    # For defect samples: detected should be True
    is_correct = m.expected == 'PASS'
    is_ok = (is_correct and not m.detected) or (not is_correct and m.detected)
    
    status = 'ok' if is_ok else ('miss' if not is_correct else 'false_pos')
    results[status].append(m)
    
    tag = m.expected
    print(f'{m.mid} [{m.mtype}] {m.desc}: expected={tag} -> {"DETECTED" if m.detected else "CLEAN"} [{status}]')
    if m.detail and status == 'MISS':
        print(f'  Detail: {m.detail}')

# Summary
total = len(M)
correct = len([m for m in M if m.expected == 'PASS'])
defects = total - correct
caught = len([m for m in M if m.expected != 'PASS' and m.detected])
missed = len([m for m in M if m.expected != 'PASS' and not m.detected])
false_pos = len([m for m in M if m.expected == 'PASS' and m.detected])

print(f'\n{"="*50}')
print(f'Mutation Matrix Results:')
print(f'  Total mutations: {total}')
print(f'  Correct samples: {correct} (all should PASS gate)')
print(f'  Defect samples: {defects} (all should trigger gate)')
print(f'  Defects caught: {caught}/{defects} ({caught/defects*100:.0f}%)')
print(f'  Defects missed: {missed}/{defects}')
print(f'  False positives: {false_pos}/{correct}')
print(f'  Overall accuracy: {(correct-false_pos+caught)/total*100:.1f}%')
