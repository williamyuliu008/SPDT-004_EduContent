import sys, os
sys.path.insert(0, r'D:\6_agent_project\AI_video_edu\tools')
from scene_quality_gate import gate_G03_content_nonempty, gate_G04_text_overflow, gate_G01_style_guide

scenes = r'D:\6_agent_project\AI_video_edu\episodes\DRAM_strategy\scenes'
render = r'D:\6_agent_project\AI_video_edu\episodes\DRAM_strategy\render_v4.py'

print('=== G-01 Style Guide ===')
ok, violations = gate_G01_style_guide(render)
print('Result:', 'PASS' if ok else 'FAIL')
for v in violations:
    print(' ', v)

print()
print('=== G-03 Content Non-Empty ===')
ok, issues = gate_G03_content_nonempty(scenes)
print('Result:', 'PASS' if ok else 'FAIL')
for i in issues:
    print(' ', i)

print()
print('=== G-04 Text Length ===')
ok, warnings = gate_G04_text_overflow(scenes)
print('Result:', 'PASS' if ok else 'WARN')
for w in warnings:
    print(' ', w)
