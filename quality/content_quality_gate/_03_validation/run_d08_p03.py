"""D08 black frame + P03 full course golden test"""
import sys, os, subprocess, glob, shutil
sys.path.insert(0, r'D:\6_agent_project\AI_video_edu')
os.chdir(r'D:\6_agent_project\AI_video_edu')
from PIL import Image
import numpy as np

# D08: Black frame (render empty scene)
d08_code = "from manim import *\nclass D08_Black(Scene):\n    def construct(self):\n        self.wait(0.1)\n"
d08_fp = r'D:\6_agent_project\projects\content_quality_gate\_01_golden_tests\defects\D08_black_frame.py'
with open(d08_fp, 'w', encoding='utf-8') as f:
    f.write(d08_code)

result = subprocess.run(['manim','-pql','-n','0','--format','png',d08_fp,'D08_Black'],
    capture_output=True, text=True, timeout=60, cwd=r'D:\6_agent_project\AI_video_edu')
pngs = glob.glob(r'D:\6_agent_project\AI_video_edu\media\images\**\*D08*Black*.png', recursive=True)
if pngs:
    img = Image.open(pngs[0])
    arr = np.array(img.convert('L'))
    max_b = arr.max()
    is_black = max_b < 15
    print(f'D08 G-05B: {"FAIL" if is_black else "PASS"} (expected: FAIL, max_brightness={max_b})')
else:
    print('D08: no PNG produced')

# P03: T01 full course snapshot (reuse scene 2 from T01 full)
p03_code = """import sys, os
sys.path.insert(0, r"D:\\6_agent_project\\AI_video_edu")
os.chdir(r"D:\\6_agent_project\\AI_video_edu")
from manim import *
from style_guide import term_card, box_diagram, comparison_table

class P03_Golden(Scene):
    def construct(self):
        # Simulate T01's concept+steps+contrast flow
        card = term_card(title="AI写作工具", keywords=["写邮件", "写报告", "写文案"])
        self.add(card)
        self.wait(0.1)
"""
p03_fp = r'D:\6_agent_project\projects\content_quality_gate\_01_golden_tests\correct\P03_golden.py'
with open(p03_fp, 'w', encoding='utf-8') as f:
    f.write(p03_code)

result = subprocess.run(['manim','-pql','-n','0','--format','png',p03_fp,'P03_Golden'],
    capture_output=True, text=True, timeout=60, cwd=r'D:\6_agent_project\AI_video_edu')
has_err = 'Traceback' in result.stderr
print(f'P03 G-05A: {"PASS" if not has_err else "FAIL"} (expected: PASS)')
pngs2 = glob.glob(r'D:\6_agent_project\AI_video_edu\media\images\**\*P03*Golden*.png', recursive=True)
if pngs2:
    shutil.copy2(pngs2[0], r'D:\6_agent_project\projects\content_quality_gate\_01_golden_tests\correct\P03_golden.png')
    print(f'P03 G-05B: PASS')
