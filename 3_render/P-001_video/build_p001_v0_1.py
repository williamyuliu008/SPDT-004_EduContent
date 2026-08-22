"""P-001 视频生成器 v0.1.1 — 演示级（manim 字幕 + edge-tts 配音 + ffmpeg 合成）

W27 第 2-3 天产出。3 分钟测试视频，链路全跑通。

输入: 古史_v4 ep01 (5 段 events)
输出:
  - media/videos/build_p001_v0_1/480p15/P001Ep01.mp4 (无声视频)
  - media/audio/ep01_narration.mp3 (edge-tts 配音)
  - media/final/P001_Ep01_ImperiasCollapse.mp4 (合成)
"""
import sys
import os
import importlib.util
import subprocess
from pathlib import Path

# 加载 submodule 里的 ep01 脚本
EP01_PATH = Path(__file__).parent.parent.parent / "2_structure" / "TextExperience" / "古史_v4_世界风云" / "scripts" / "古史_v4_ep01_帝国的崩塌.py"
spec = importlib.util.spec_from_file_location("ep01_module", EP01_PATH)
ep01 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ep01)
DATA = ep01.get_data()

# 提取全部 5 段叙事（取 events 里的 description）
SCRIPT = []
for ev in DATA['timeline']['events']:
    SCRIPT.append({
        "year": ev['year'],
        "title": ev['title'],
        "narr": ev['description']
    })

# manim 场景
from manim import (
    Scene, Text, Create, Write, FadeIn, FadeOut,
    Square, Circle, Rectangle, Line,
    BLUE, GREEN, RED, YELLOW, WHITE, GREY, BLACK,
    ORIGIN, UP, DOWN, LEFT, RIGHT,
)
from manim.constants import PI

# 古史系列配色
GOLD = "#C9A227"
BRICK = "#8B3A3A"
INK = "#2A2A2A"

# 中文 TTS 语音（edge-tts）
TTS_VOICE = "zh-CN-YunjianNeural"  # 男声, 适合历史叙事


class P001Ep01(Scene):
    """3 分钟测试视频 — 5 段叙事 + 片头片尾"""

    def construct(self):
        self.show_title()
        for i, seg in enumerate(SCRIPT):
            self.show_segment(i, seg, is_last=(i == len(SCRIPT) - 1))
        self.show_outro()

    def show_title(self):
        title = Text(
            f"{DATA['series']} · 第 {DATA['ep']} 集",
            font="Microsoft YaHei",
            color=GOLD
        ).scale(0.7).shift(UP * 1.5)
        subtitle = Text(
            DATA['title'],
            font="Microsoft YaHei",
            color=WHITE
        ).scale(1.2).shift(ORIGIN)
        en_subtitle = Text(
            DATA['subtitle'],
            font="Microsoft YaHei",
            color=GREY
        ).scale(0.5).shift(DOWN * 1.5)
        self.play(Write(title), run_time=2)
        self.play(FadeIn(subtitle), run_time=2)
        self.play(FadeIn(en_subtitle), run_time=2)
        self.wait(15)  # 给 TTS 留 15 秒
        self.play(FadeOut(title), FadeOut(subtitle), FadeOut(en_subtitle), run_time=1)

    def show_segment(self, idx, seg, is_last=False):
        year_block = Rectangle(
            width=4, height=1.2,
            color=BRICK, fill_color=BRICK, fill_opacity=0.8
        ).to_edge(UP, buff=1)
        year_text = Text(
            seg['year'],
            font="Microsoft YaHei",
            color=WHITE
        ).scale(0.8).move_to(year_block.get_center())
        title = Text(
            seg['title'],
            font="Microsoft YaHei",
            color=GOLD
        ).scale(0.9).shift(UP * 0.5)
        narr_lines = self._split_narr(seg['narr'])
        narr_texts = []
        for j, line in enumerate(narr_lines):
            t = Text(
                line,
                font="Microsoft YaHei",
                color=WHITE
            ).scale(0.55).shift(DOWN * (0.8 + j * 0.7))
            narr_texts.append(t)
        deco_line = Line(
            start=LEFT * 5, end=RIGHT * 5,
            color=GOLD, stroke_width=2
        ).shift(DOWN * 0.3)

        # 段号提示
        seg_idx = Text(
            f"[{idx + 1}/{len(SCRIPT)}]",
            font="Microsoft YaHei",
            color=GREY
        ).scale(0.4).to_edge(DOWN, buff=0.3).to_edge(RIGHT, buff=0.3)

        self.play(FadeIn(year_block), Write(year_text), run_time=1.5)
        self.play(Write(title), Create(deco_line), run_time=1.5)
        for t in narr_texts:
            self.play(FadeIn(t), run_time=1.5)
        self.play(FadeIn(seg_idx), run_time=0.5)

        # 给 TTS 留时间（按 3 字/秒 + 缓冲）
        speech_time = self._estimate_speech_time(seg['narr'])
        self.wait(speech_time)

        all_objs = [year_block, year_text, title, deco_line, seg_idx] + narr_texts
        self.play(*[FadeOut(m) for m in all_objs], run_time=1.5)

    def show_outro(self):
        outro = Text(
            "P-001 视频测试 v0.1 · W27",
            font="Microsoft YaHei",
            color=GOLD
        ).scale(0.6)
        self.play(Write(outro), run_time=2)
        self.wait(10)
        self.play(FadeOut(outro), run_time=1)

    def _split_narr(self, text):
        sentences = [s.strip() for s in text.split("。") if s.strip()]
        return [s + "。" for s in sentences]

    def _estimate_speech_time(self, text):
        """估算 TTS 时长 (中文 3.5 字/秒)"""
        chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
        return max(8, chars / 3.5 + 2)


# ============================================================
# TTS 配音生成 + ffmpeg 合成
# ============================================================
def generate_tts():
    """用 edge-tts 生成 ep01 完整配音"""
    import edge_tts
    import asyncio

    # 拼接所有 SCRIPT 文本
    full_text = " ".join([DATA['timeline']['overview']] + [s['narr'] for s in SCRIPT])
    # 清理空白
    full_text = " ".join(full_text.split())

    audio_path = Path(__file__).parent / "media" / "audio" / "ep01_narration.mp3"
    audio_path.parent.mkdir(parents=True, exist_ok=True)

    async def _gen():
        communicate = edge_tts.Communicate(full_text, TTS_VOICE)
        await communicate.save(str(audio_path))

    asyncio.run(_gen())
    print(f"[TTS] Generated: {audio_path} ({audio_path.stat().st_size} bytes)")
    return audio_path


def merge_video_audio(video_path, audio_path, output_path):
    """用 ffmpeg 合成视频+音频"""
    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-i", str(audio_path),
        "-c:v", "copy",
        "-c:a", "aac",
        "-shortest",
        str(output_path)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[FFMPEG ERROR] {result.stderr[-500:]}")
        return None
    print(f"[FFMPEG] Merged: {output_path} ({Path(output_path).stat().st_size} bytes)")
    return output_path


if __name__ == "__main__":
    # 这个文件主要给 manim 调用
    # TTS + 合成由 build_p001_full.sh 完成
    pass
