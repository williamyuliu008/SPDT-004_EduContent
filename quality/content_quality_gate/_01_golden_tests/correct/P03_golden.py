import sys, os
sys.path.insert(0, r"D:\6_agent_project\AI_video_edu")
os.chdir(r"D:\6_agent_project\AI_video_edu")
from manim import *
from style_guide import term_card, box_diagram, comparison_table

class P03_Golden(Scene):
    def construct(self):
        # Simulate T01's concept+steps+contrast flow
        card = term_card(title="AI写作工具", keywords=["写邮件", "写报告", "写文案"])
        self.add(card)
        self.wait(0.1)
