"""
4 步法母题配图工具
- 用 matplotlib 画立体几何 SVG
- pp_001: 正方体中位线法
- pp_002: 四棱锥找两条相交线
- 后续母题可加
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, FancyArrowPatch
from pathlib import Path
import numpy as np

# 全局风格：极简白 + 思源宋体
plt.rcParams['font.sans-serif'] = ['Source Han Serif SC', 'Noto Serif CJK SC', 'SimSun']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.facecolor'] = '#FAFAFA'
plt.rcParams['axes.facecolor'] = '#FAFAFA'

OUT_DIR = Path(r'D:\4_data\knowledge_cards\数学\4step\figures')
OUT_DIR.mkdir(parents=True, exist_ok=True)


def draw_cube_with_af_parallel():
    """pp_001: 正方体 ABCD-A1B1C1D1，E、F 分别是 AB、A1B1 中点，证 AF ∥ 面 ECD1"""
    fig, ax = plt.subplots(figsize=(8, 8))

    # 正方体坐标 (略斜投影)
    s = 1.0  # 边长
    dx, dy = 0.5, -0.3  # 透视偏移
    A  = (0, 0)
    B  = (s, 0)
    C  = (s, s)
    D  = (0, s)
    A1 = (A[0]+dx, A[1]+dy)
    B1 = (B[0]+dx, B[1]+dy)
    C1 = (C[0]+dx, C[1]+dy)
    D1 = (D[0]+dx, D[1]+dy)
    E  = ((A[0]+B[0])/2, (A[1]+B[1])/2)
    F  = ((A1[0]+B1[0])/2, (A1[1]+B1[1])/2)

    def draw_segment(p1, p2, **kw):
        ax.plot([p1[0], p2[0]], [p1[1], p2[1]], **kw)

    # 底面
    for p in [(A,B), (B,C), (C,D), (D,A)]:
        draw_segment(*p, color='#333', linewidth=1.5)
    # 顶面
    for p in [(A1,B1), (B1,C1), (C1,D1), (D1,A1)]:
        draw_segment(*p, color='#333', linewidth=1.5)
    # 侧棱
    for p in [(A,A1), (B,B1), (C,C1), (D,D1)]:
        draw_segment(*p, color='#333', linewidth=1.5)

    # 关键线 (高亮)
    draw_segment(A, F, color='#c00', linewidth=2.5, label='AF')
    draw_segment(E, D1, color='#c00', linewidth=2.5, alpha=0.5)
    draw_segment(C, D1, color='#c00', linewidth=2.5, alpha=0.5)
    draw_segment(E, C, color='#c00', linewidth=2.5, alpha=0.5)

    # 中点标记
    for p, name in [(E,'E'), (F,'F'), (A,'A'), (B,'B'), (C,'C'), (D,'D'),
                    (A1,'A₁'), (B1,'B₁'), (C1,'C₁'), (D1,'D₁')]:
        ax.plot(p[0], p[1], 'o', color='#000', markersize=4)
        ax.annotate(name, (p[0]+0.05, p[1]+0.05), fontsize=11)

    ax.set_xlim(-0.5, 2.0)
    ax.set_ylim(-0.5, 2.0)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('正方体中位线法证 AF ∥ 面 ECD1', fontsize=13, pad=10)
    fig.savefig(OUT_DIR / 'pp_001_cube_af_parallel.svg', bbox_inches='tight', dpi=150)
    plt.close(fig)
    print(f'Saved: {OUT_DIR / "pp_001_cube_af_parallel.svg"}')


def draw_square_pyramid():
    """pp_002: 四棱锥 P-ABCD, PA⊥底面 ABCD, 底面正方形, E 是 PC 中点, 证 BD⊥面 PAC"""
    fig, ax = plt.subplots(figsize=(8, 8))

    s = 1.0
    A  = (0, 0)
    B  = (s, 0)
    C  = (s, s)
    D  = (0, s)
    P  = (0.5, -0.2)  # P 在底面外侧（PA 垂直于底面，简化为侧视图）
    E  = ((P[0]+C[0])/2, (P[1]+C[1])/2)

    def draw_segment(p1, p2, **kw):
        ax.plot([p1[0], p2[0]], [p1[1], p2[1]], **kw)

    # 底面
    for p in [(A,B), (B,C), (C,D), (D,A)]:
        draw_segment(*p, color='#333', linewidth=1.5)
    # 侧棱
    for p in [(P,A), (P,B), (P,C), (P,D)]:
        draw_segment(*p, color='#333', linewidth=1, alpha=0.6)
    # 关键线 (高亮)
    draw_segment(B, D, color='#c00', linewidth=2.5)  # BD 要证的线
    draw_segment(P, A, color='#06c', linewidth=2.5)  # PA
    draw_segment(A, C, color='#06c', linewidth=2.5)  # AC
    # 面 PAC
    draw_segment(P, C, color='#06c', linewidth=1, alpha=0.4)
    draw_segment(P, E, color='#06c', linewidth=1, alpha=0.4)
    draw_segment(C, E, color='#06c', linewidth=1, alpha=0.4)

    # 中点/顶点标记
    for p, name in [(A,'A'), (B,'B'), (C,'C'), (D,'D'), (P,'P'), (E,'E')]:
        ax.plot(p[0], p[1], 'o', color='#000', markersize=4)
        ax.annotate(name, (p[0]+0.05, p[1]+0.05), fontsize=11)

    # BD⊥AC 标注
    ax.annotate('BD⊥AC (正方形)', xy=(0.5, 0.5), xytext=(0.3, -0.5),
                fontsize=10, color='#c00', arrowprops=dict(arrowstyle='->', color='#c00'))
    ax.annotate('PA⊥底面 ⇒ PA⊥BD', xy=(0.25, -0.1), xytext=(-0.3, -0.5),
                fontsize=10, color='#06c', arrowprops=dict(arrowstyle='->', color='#06c'))

    ax.set_xlim(-0.5, 1.5)
    ax.set_ylim(-0.6, 1.2)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('四棱锥找两条相交线证 BD⊥面 PAC', fontsize=13, pad=10)
    fig.savefig(OUT_DIR / 'pp_002_square_pyramid.svg', bbox_inches='tight', dpi=150)
    plt.close(fig)
    print(f'Saved: {OUT_DIR / "pp_002_square_pyramid.svg"}')


if __name__ == "__main__":
    draw_cube_with_af_parallel()
    draw_square_pyramid()
    print('All figures saved.')
