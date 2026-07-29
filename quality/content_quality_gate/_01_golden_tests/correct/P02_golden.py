import sys, os
sys.path.insert(0, r"D:\6_agent_project\AI_video_edu")
os.chdir(r"D:\6_agent_project\AI_video_edu")
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
