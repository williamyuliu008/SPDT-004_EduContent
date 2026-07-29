"""P02 Golden Test — T02 Prompt Engineering (box_diagram)"""
import sys, os, subprocess, glob, shutil
sys.path.insert(0, r'D:\6_agent_project\AI_video_edu')
os.chdir(r'D:\6_agent_project\AI_video_edu')

code = """import sys, os
sys.path.insert(0, r"D:\\6_agent_project\\AI_video_edu")
os.chdir(r"D:\\6_agent_project\\AI_video_edu")
from manim import *
from style_guide import box_diagram
class P02_Golden(Scene):
    def construct(self):
        boxes = [
            {'label': '1. 角色', 'subtitle': '告诉AI它是谁'},
            {'label': '2. 任务', 'subtitle': '告诉AI做什么'},
            {'label': '3. 约束', 'subtitle': '告诉AI怎么做'},
        ]
        edges = [{'from':0,'to':1,'label':'+'},{'from':1,'to':2,'label':'+'}]
        diagram = box_diagram(title='Prompt = 角色+任务+约束', boxes=boxes, edges=edges)
        self.add(diagram)
        self.wait(0.1)
"""

fp = r'D:\6_agent_project\projects\content_quality_gate\_01_golden_tests\correct\P02_golden.py'
with open(fp, 'w', encoding='utf-8') as f:
    f.write(code)

result = subprocess.run(['manim','-pql','-n','0','--format','png',fp,'P02_Golden'],
    capture_output=True, text=True, timeout=60, cwd=r'D:\6_agent_project\AI_video_edu')

has_err = 'Traceback' in result.stderr
print(f'P02 G-05A: {"PASS" if not has_err else "FAIL"}')
if has_err: print(result.stderr[-200:])

if not has_err:
    pngs = glob.glob(r'D:\6_agent_project\AI_video_edu\media\images\**\*P02*Golden*.png', recursive=True)
    for p in pngs:
        dest = r'D:\6_agent_project\projects\content_quality_gate\_01_golden_tests\correct\P02_golden.png'
        shutil.copy2(p, dest)
        sz = os.path.getsize(dest)
        print(f'P02 G-05B: PASS ({sz//1024}KB PNG)')
else:
    print('P02 G-05B: SKIP (no PNG)')
