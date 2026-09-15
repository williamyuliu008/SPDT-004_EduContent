"""
P-CGM.3: 母题 → 30s 视频生成器 (通用工具)
============================================
基于母题 JSON (含 thinking_path + standard_steps + key_insight) 自动生成 30s 视频短片.

复用 history_k_video_gen 的 manim + edge-tts + ffmpeg 链路, 但自动从母题 JSON 提取内容.

链路:
  母题 JSON → 30s SCRIPT (100 字) → manim Scene → edge-tts → ffmpeg 合成

输出:
  D:/4_data/work/media/renders/<subject>_videos/<pp_id>_<主题>.mp4
"""
import argparse
import asyncio
import json
import re
import subprocess
import sys
from pathlib import Path

KB_ROOT = Path(r"D:\4_data\knowledge_cards")
OUTPUT_ROOT = Path(r"D:\4_data\work\media\renders")


def build_script_from_pp(pp: dict) -> dict:
    """从母题 JSON 提取 30s 脚本字段"""
    title = pp.get("title", "母题讲解")
    pp_id = pp.get("id", "")
    insight = pp.get("key_insight", "")[:60]
    thinking = pp.get("thinking_path", "")
    steps = pp.get("standard_steps", [])
    domain = pp.get("domain", "")

    # 思考路径转 1-2 行
    thinking_lines = re.split(r"[→\.\n]", thinking)
    thinking_lines = [l.strip() for l in thinking_lines if l.strip() and len(l.strip()) > 3][:3]

    # 标准步骤取前 2-3 步
    steps_short = []
    for s in steps[:3]:
        s = re.sub(r"^\d+\.\s*", "", str(s))
        if len(s) > 5:
            steps_short.append(s[:30])

    # 拼 narr (~100 字)
    narr_parts = []
    if thinking_lines:
        narr_parts.append(thinking_lines[0])
    if steps_short:
        narr_parts.append("步骤: " + "; ".join(steps_short[:2]))
    if insight:
        narr_parts.append("关键洞察: " + insight)

    narr = " ".join(narr_parts)[:200]

    return {
        "id": pp_id,
        "title": title,
        "subtitle": domain or pp.get("subject", ""),
        "key_insight": insight or "母题解题",
        "narr": narr or "母题: " + title,
    }


def gen_video_for_pp(pp_path: Path, output_dir: Path) -> bool:
    """单张母题 → 30s 视频"""
    pp = json.loads(pp_path.read_text(encoding="utf-8"))
    script = build_script_from_pp(pp)

    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. 写 manim 脚本
    manim_script = f'''"""Auto-generated manim scene for {script['id']}"""
from manim import Scene, Text, Write, FadeIn, FadeOut, BLUE, WHITE, ORIGIN, UP, DOWN

GOLD = "#C9A227"

class MotherProblemCard(Scene):
    def construct(self):
        title = Text("{script['title']}", font="Microsoft YaHei", color=GOLD).scale(0.55).shift(UP * 2)
        subtitle = Text("{script['subtitle']}", font="Microsoft YaHei", color=BLUE).scale(0.35).shift(UP * 1.2)
        self.play(Write(title), run_time=1)
        self.play(FadeIn(subtitle), run_time=1)

        insight = Text("{script['key_insight']}", font="Microsoft YaHei", color=WHITE).scale(0.5)
        self.play(Write(insight), run_time=2)
        self.wait(2)

        narr_lines = {repr(script['narr'].split(chr(10)))}
        for line in narr_lines:
            t = Text(line, font="Microsoft YaHei", color=WHITE).scale(0.32).shift(DOWN * 0.5)
            self.play(FadeIn(t), run_time=1.5)
            self.wait(1.5)
            self.play(FadeOut(t), run_time=0.5)

        self.play(FadeOut(title), FadeOut(subtitle), FadeOut(insight), run_time=1)
        self.wait(2)
'''
    manim_path = output_dir / f"{pp['id']}_manim.py"
    manim_path.write_text(manim_script, encoding="utf-8")

    # 2. 跑 manim
    print(f"[manim] {pp['id']} ...", flush=True)
    try:
        result = subprocess.run(
            ["python", "-m", "manim", "-ql", "--media_dir", str(output_dir),
             str(manim_path), "MotherProblemCard"],
            capture_output=True, text=True, timeout=180,
        )
        if result.returncode != 0:
            print(f"  [manim FAILED] {result.stderr[-300:]}")
            return False
    except subprocess.TimeoutExpired:
        print(f"  [manim TIMEOUT]")
        return False

    # 3. 找 mp4
    mp4_src = output_dir / "videos" / f"{pp['id']}_manim" / "480p15" / "MotherProblemCard.mp4"
    if not mp4_src.exists():
        candidates = list((output_dir / f"{pp['id']}_manim" / "media" / "videos").rglob("MotherProblemCard.mp4"))
        if candidates:
            mp4_src = candidates[0]
    if not mp4_src.exists():
        print(f"  [manim mp4 not found]")
        return False

    # 4. TTS
    mp3_out = output_dir / f"{pp['id']}_narration.mp3"
    print(f"[TTS] {pp['id']} ...", flush=True)
    try:
        asyncio.run(gen_tts(script["narr"], mp3_out))
    except Exception as e:
        print(f"  [TTS FAILED] {e}")
        return False

    # 5. ffmpeg 合成
    final_out = output_dir / f"{pp['id']}_video.mp4"
    print(f"[ffmpeg] {pp['id']} ...", flush=True)
    cmd = [
        "ffmpeg", "-y",
        "-i", str(mp4_src),
        "-i", str(mp3_out),
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "128k",
        "-shortest",
        str(final_out),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  [ffmpeg FAILED] {result.stderr[-500:]}")
        return False

    print(f"  OK: {final_out} ({final_out.stat().st_size} bytes)")
    return True


async def gen_tts(text: str, out_path: Path) -> None:
    try:
        import edge_tts
    except ImportError:
        print("  ERROR: pip install edge-tts", file=sys.stderr)
        sys.exit(1)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    communicate = edge_tts.Communicate(text, "zh-CN-YunjianNeural", rate="-12%")
    await communicate.save(str(out_path))


def batch_subject(args) -> int:
    """跑批某学科所有母题"""
    subject = args.subject
    pp_dir = KB_ROOT / subject / "4step" / "parent_problems"
    if not pp_dir.exists():
        print(f"  ERROR: {pp_dir} 不存在")
        return 1

    output_dir = OUTPUT_ROOT / f"{subject}_videos"

    pp_files = sorted(pp_dir.glob("*.json"))
    print(f"=== {subject} ({len(pp_files)} 张母题) ===")

    rc = 0
    for pp_file in pp_files:
        ok = gen_video_for_pp(pp_file, output_dir)
        rc += 0 if ok else 1
    print(f"\n完成 {len(pp_files) - rc}/{len(pp_files)} 张")
    return rc


def main():
    parser = argparse.ArgumentParser(description="母题 → 30s 视频通用生成器")
    parser.add_argument("--subject", required=True,
                        choices=["数学", "语文", "英语", "历史", "地理", "政治", "书法"],
                        help="学科")
    args = parser.parse_args()
    return batch_subject(args)


if __name__ == "__main__":
    sys.exit(main())