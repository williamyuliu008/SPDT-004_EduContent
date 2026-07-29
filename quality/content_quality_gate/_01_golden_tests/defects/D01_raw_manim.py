"""Defect Sample D01 — 裸Manim定位API（违反R-001）"""
import sys, os
sys.path.insert(0, r"D:\6_agent_project\AI_video_edu")
os.chdir(r"D:\6_agent_project\AI_video_edu")
from manim import *

class D01_Defect(Scene):
    def construct(self):
        title = Text('测试', font='Microsoft YaHei', font_size=40)
        box = RoundedRectangle(width=5, height=1, corner_radius=0.1)
        box.to_corner(UL)
        title.next_to(box, DOWN, buff=0.3)  # <-- R-001 VIOLATION: 裸Manim定位
        self.add(box, title)
        self.wait(0.1)
