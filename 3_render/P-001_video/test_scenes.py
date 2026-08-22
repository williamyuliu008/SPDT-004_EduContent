"""P-001 视频渲染管线 W27 测试场景 — 3 个最小示例验证 manim 链路

目的:
1. 验证 manim 0.20.1 + ffmpeg 在本机可跑
2. 验证低质量 (-ql) 输出 < 30 秒
3. 为 W28 正式管线做基线
"""
from manim import Scene, Text, Create, Square, Circle, Write, Transform
from manim import BLUE, GREEN, RED, YELLOW, ORIGIN
from manim.constants import PI, UP, DOWN, LEFT, RIGHT


class Example1_SquareToCircle(Scene):
    """示例 1: 方形变圆形 (manim 经典入门)"""
    def construct(self):
        square = Square(color=BLUE)
        circle = Circle(color=GREEN)
        self.play(Create(square))
        self.play(square.animate.rotate(PI / 4))
        self.play(Transform(square, circle))
        self.wait(1)


class Example2_TextWrite(Scene):
    """示例 2: 文字渐显 (字幕/标题用)"""
    def construct(self):
        text1 = Text("P-001 视频管线测试", color=BLUE).scale(0.8)
        text2 = Text("W27 第 1 站", color=GREEN).scale(0.6)
        text2.next_to(text1, DOWN)
        self.play(Write(text1))
        self.play(Write(text2))
        self.wait(2)


class Example3_MultiObject(Scene):
    """示例 3: 多对象协同 (历史叙事/时间轴用)"""
    def construct(self):
        title = Text("示例 3: 多对象", color=YELLOW).scale(0.7).to_edge(UP)
        s1 = Square(color=RED).shift(LEFT * 3)
        s2 = Square(color=GREEN).shift(ORIGIN)
        s3 = Square(color=BLUE).shift(RIGHT * 3)
        self.play(Write(title))
        self.play(Create(s1), Create(s2), Create(s3))
        self.wait(2)

