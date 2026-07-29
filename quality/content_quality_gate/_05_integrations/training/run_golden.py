import sys, os, subprocess, glob, shutil
sys.path.insert(0, r'D:\6_agent_project\AI_video_edu')
os.chdir(r'D:\6_agent_project\AI_video_edu')

# T01 Golden Test
code = """import sys, os
sys.path.insert(0, r"D:\\6_agent_project\\AI_video_edu")
os.chdir(r"D:\\6_agent_project\\AI_video_edu")
from manim import *
from style_guide import term_card
class T01_Golden(Scene):
    def construct(self):
        card = term_card(title="AI写作工具", keywords=["写邮件", "写报告", "写文案"])
        self.add(card)
        self.wait(0.1)
"""

fp = r'D:\6_agent_project\projects\content_quality_gate\_05_integrations\training\t01_golden.py'
os.makedirs(os.path.dirname(fp), exist_ok=True)
with open(fp, 'w', encoding='utf-8') as f:
    f.write(code)

result = subprocess.run(['manim', '-pql', '-n', '0', '--format', 'png', fp, 'T01_Golden'],
    capture_output=True, text=True, timeout=60, cwd=r'D:\6_agent_project\AI_video_edu')

has_err = 'Traceback' in result.stderr
print(f'T01 Golden: {"PASS" if not has_err else "FAIL"}')

if not has_err:
    pngs = glob.glob(r'D:\6_agent_project\AI_video_edu\media\images\**\*Golden*.png', recursive=True)
    for p in pngs:
        dest = r'D:\6_agent_project\projects\content_quality_gate\_01_golden_tests\correct\T01_golden.png'
        shutil.copy2(p, dest)
        print(f'  Saved: {dest}')
else:
    print(result.stderr[-200:])
