"""
历史 K 卡 → 30s 视频短片生成器 v1.0
===================================
基于 P-001_video 工具链, 把历史 5 张母题 (hp_001-005) → 30 秒科普视频短片.

链路 (复用 P-001):
  SCRIPT (30s = ~100 字) → manim -ql (字幕 mp4) → edge-tts (rate=-12%) → ffmpeg 合成

输出:
  D:\4_data\work\media\renders\history_k_videos\hp_001_史料实证.mp4
"""
import argparse
import asyncio
import json
import os
import subprocess
import sys
from pathlib import Path

OUTPUT_ROOT = Path(r"D:\4_data\work\media\renders\history_k_videos")


# 5 张历史 K 卡 + 30 秒脚本模板
HISTORY_K_CARDS = {
    "hp_001": {
        "id": "hp_001_史料实证判断_史前史",
        "title": "史料实证 · 史前史判断",
        "subtitle": "2018 上海高考历史 Q1",
        "key_insight": "史前史 = 文字之前, 排除神化和传说",
        "narr": "判断史前史的关键是'前'字 —— 文字发明之前的历史。\n"
                "排除选项里的神话说、史诗歌、传说, 这些都属于文字之后的口传史料。\n"
                "史前史的可信度判断,要选有实物遗存可验证的考古证据。"
    },
    "hp_002": {
        "id": "hp_002_时间轴定位_公元前后",
        "title": "时间轴定位 · 公元前后换算",
        "subtitle": "2018 上海高考历史 Q3",
        "key_insight": "公元前 N 年 = (N/100+1) 世纪, 公元前不算 '公元'",
        "narr": "公元前后换算技巧: 公元前 403 年, 处于公元前 5 世纪初。\n"
                "公式是 X 年 = (X/100 + 1) 世纪, 取整数。\n"
                "注意 '公元前' 不等于 '公元', 不要漏掉前字。"
    },
    "hp_003": {
        "id": "hp_003_工业革命与现代化_19世纪末德国",
        "title": "工业革命 · 19 世纪末德国",
        "subtitle": "2018 上海高考历史 Q9",
        "key_insight": "判断'主要原因 vs 必要条件' —— 直接推动 vs 间接基础",
        "narr": "19 世纪末德国工业腾飞的关键原因,是第二次工业革命的内燃机/电力革命。\n"
                "法国大革命、美国独立战争、德国统一, 都是必要条件而非直接推动。\n"
                "判断'主要原因'时, 找直接推动的那一项。"
    },
    "hp_004": {
        "id": "hp_004_史料解读_演讲结构",
        "title": "史料解读 · 演讲结构提取",
        "subtitle": "2018 上海高考历史 Q14",
        "key_insight": "演讲/议论结构 → 抓最末句的号召/结论",
        "narr": "史料解读的演讲/议论结构,关键是抓最末一句。\n"
                "材料说'培养人才办学兴学召集群众', 最终目的是'改造社会'。\n"
                "末句的'号召意图' = 全文的真正目的。"
    },
    "hp_005": {
        "id": "hp_005_经济全球化_阶段时间轴",
        "title": "经济全球化 · 阶段时间轴",
        "subtitle": "2018 上海高考历史 Q20",
        "key_insight": "4 阶段模型: 殖民 → 两次工业革命 → 信息革命 → 互联网",
        "narr": "经济全球化经历 4 阶段: 15-19 世纪殖民扩张, 19 世纪末两次工业革命, 20 世纪战后贸易体系, 21 世纪信息互联网。\n"
                "不同阶段对应不同推动主体 —— 国家/资本/跨国企业/平台。"
    },
}


def gen_video(hp_id: str, output_dir: Path = OUTPUT_ROOT) -> bool:
    """单张 K 卡 → 30s 视频"""
    if hp_id not in HISTORY_K_CARDS:
        print(f"  ERROR: {hp_id} 不在 5 张 K 卡列表")
        return False

    card = HISTORY_K_CARDS[hp_id]
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. 写 manim 脚本
    manim_script = f'''"""Auto-generated manim scene for {hp_id}"""
from manim import Scene, Text, Write, FadeIn, FadeOut, BLUE, WHITE, ORIGIN, UP, DOWN

GOLD = "#C9A227"
INK = "#2A2A2A"

class HistoryKCard(Scene):
    def construct(self):
        title = Text("{card['title']}", font="Microsoft YaHei", color=GOLD).scale(0.6).shift(UP * 2)
        subtitle = Text("{card['subtitle']}", font="Microsoft YaHei", color=BLUE).scale(0.4).shift(UP * 1.2)
        self.play(Write(title), run_time=1)
        self.play(FadeIn(subtitle), run_time=1)

        insight = Text("{card['key_insight']}", font="Microsoft YaHei", color=WHITE).scale(0.55)
        self.play(Write(insight), run_time=2)
        self.wait(2)

        narr_lines = {repr(card['narr'].split(chr(10)))}
        for line in narr_lines:
            t = Text(line, font="Microsoft YaHei", color=WHITE).scale(0.35).shift(DOWN * 0.5)
            self.play(FadeIn(t), run_time=1.5)
            self.wait(1.5)
            self.play(FadeOut(t), run_time=0.5)

        self.play(FadeOut(title), FadeOut(subtitle), FadeOut(insight), run_time=1)
        self.wait(2)
'''

    manim_path = output_dir / f"{hp_id}_manim.py"
    manim_path.write_text(manim_script, encoding="utf-8")

    # 2. 跑 manim (--media_dir 让输出到 ./videos 而非 ./media/videos)
    print(f"[manim] {hp_id} ...")
    try:
        result = subprocess.run(
            ["python", "-m", "manim", "-ql", "--media_dir", str(output_dir),
             str(manim_path), "HistoryKCard"],
            capture_output=True, text=True, timeout=180,
        )
        if result.returncode != 0:
            print(f"  [manim FAILED] {result.stderr[-300:]}")
            return False
    except subprocess.TimeoutExpired:
        print(f"  [manim TIMEOUT]")
        return False

    # 3. 找 mp4 输出 (--media_dir 模式: <media_dir>/videos/<script>/<quality>/<Scene>.mp4)
    mp4_src = output_dir / "videos" / f"{hp_id}_manim" / "480p15" / "HistoryKCard.mp4"
    if not mp4_src.exists():
        # 备用: 默认 <script_dir>/media/videos/<scene>/<quality>/*.mp4
        candidates = list((output_dir / f"{hp_id}_manim" / "media" / "videos").rglob("HistoryKCard.mp4"))
        if candidates:
            mp4_src = candidates[0]
    if not mp4_src.exists():
        print(f"  [manim mp4 not found: {mp4_src}]")
        return False

    # 4. 生成 TTS
    mp3_out = output_dir / f"{hp_id}_narration.mp3"
    print(f"[TTS] {hp_id} ...")
    try:
        asyncio.run(gen_tts(card["narr"], mp3_out))
    except Exception as e:
        print(f"  [TTS FAILED] {e}")
        return False

    # 5. ffmpeg 合成
    final_out = output_dir / f"{card['id']}.mp4"
    print(f"[ffmpeg] {hp_id} -> {final_out.name}")
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
    """edge-tts 配音"""
    try:
        import edge_tts
    except ImportError:
        print("  ERROR: pip install edge-tts", file=sys.stderr)
        sys.exit(1)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    communicate = edge_tts.Communicate(text, "zh-CN-YunjianNeural", rate="-12%")
    await communicate.save(str(out_path))


def batch(args) -> int:
    rc = 0
    for hp_id in HISTORY_K_CARDS:
        print(f"\n=== {hp_id} ===")
        ok = gen_video(hp_id)
        rc += 0 if ok else 1
    print(f"\n完成 {len(HISTORY_K_CARDS) - rc}/{len(HISTORY_K_CARDS)} 张")
    return rc


def main():
    parser = argparse.ArgumentParser(description="历史 K 卡 → 30s 视频短片生成器")
    sub = parser.add_subparsers(dest="cmd")

    p_gen = sub.add_parser("gen")
    p_gen.add_argument("--hp-id", required=True, choices=list(HISTORY_K_CARDS.keys()))
    p_gen.add_argument("--output", default=str(OUTPUT_ROOT))
    p_gen.set_defaults(func=lambda args: 0 if gen_video(args.hp_id, Path(args.output)) else 1)

    p_batch = sub.add_parser("batch")
    p_batch.set_defaults(func=batch)

    args = parser.parse_args()
    if not hasattr(args, "cmd") or args.cmd is None:
        parser.print_help()
        return 0
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())