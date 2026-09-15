"""
历史 K 卡扩展 10 集 30s 视频 (v4_ep06-15, 20 世纪后冷战到 AI 时代)
===================================================================
复用 history_k_video_gen 的 manim+edge-tts+ffmpeg 链路, 扩 hp_006-hp_015 共 10 张 K 卡.

主题: 1991 苏联解体 → 2001 9/11 → 2008 金融危机 → 2010 阿拉伯之春 → 2015 巴黎气候 →
2018 中美贸易战 → 2020 新冠 → 2022 俄乌冲突 → 2023 AI 革命 → 2024 全球大选年

链路 (复用 history_k_video_gen):
  SCRIPT (30s = ~100 字) → manim -ql (字幕 mp4) → edge-tts (rate=-12%) → ffmpeg 合成

输出:
  D:\4_data\work\media\renders\history_k_videos\hp_NNN_xxx.mp4
"""
import argparse
import asyncio
import os
import subprocess
import sys
from pathlib import Path

OUTPUT_ROOT = Path(r"D:\4_data\work\media\renders\history_k_videos")


# 10 张扩展 K 卡 + 30 秒脚本模板
HISTORY_K_CARDS_V2 = {
    "hp_006": {
        "id": "hp_006_苏联解体_1991",
        "title": "苏联解体 · 1991",
        "subtitle": "冷战终结 / 地缘重组",
        "key_insight": "内部经济崩溃 > 外部军备竞赛",
        "narr": "1991 年 12 月 25 日, 苏联红旗从克里姆林宫降下。\n"
                "表面是美苏军备竞赛拖垮, 实际是内部计划经济失败。\n"
                "苏联解体不是突然事件, 而是长期经济危机的总爆发。"
    },
    "hp_007": {
        "id": "hp_007_9_11_反恐战争",
        "title": "9·11 与反恐战争",
        "subtitle": "2001 纽约 / 单极时刻",
        "key_insight": "全球化下单一超级大国的不对称挑战",
        "narr": "2001 年 9 月 11 日, 19 名劫机者撞击世贸中心。\n"
                "美国从单极霸权转入长期反恐, 入侵阿富汗和伊拉克。\n"
                "9·11 改变了 21 世纪国际格局, 引发身份政治与文明冲突。"
    },
    "hp_008": {
        "id": "hp_008_全球金融危机_2008",
        "title": "全球金融危机 · 2008",
        "subtitle": "次贷 / 雷曼 / 系统性风险",
        "key_insight": "金融衍生品的杠杆放大效应",
        "narr": "2008 年 9 月 15 日, 雷曼兄弟破产。\n"
                "次级贷款被打包成 CDO 衍生品, 评级机构失职, 风险被严重低估。\n"
                "这场危机揭示了金融全球化的系统性风险。"
    },
    "hp_009": {
        "id": "hp_009_阿拉伯之春_难民危机",
        "title": "阿拉伯之春 · 难民危机",
        "subtitle": "2010-2015 / 数字革命",
        "key_insight": "社交媒体加速社会运动",
        "narr": "2010 年突尼斯小贩自焚, 引爆阿拉伯世界连锁抗议。\n"
                "社交媒体让年轻人快速组织, 利比亚/叙利亚内战引发难民潮。\n"
                "数字时代改变了革命与社会运动的传播方式。"
    },
    "hp_010": {
        "id": "hp_010_巴黎气候协定",
        "title": "巴黎气候协定 · 2015",
        "subtitle": "全球升温 1.5℃ / 共识 vs 执行",
        "key_insight": "全球治理共识与执行力的差距",
        "narr": "2015 年 196 缔约方通过《巴黎协定》, 目标升温 1.5 度以内。\n"
                "但 2024 年全球升温已突破 1.5 度, 共识与执行差距大。\n"
                "气候问题考验全球协作的真实效力。"
    },
    "hp_011": {
        "id": "hp_011_中美贸易战",
        "title": "中美贸易战 · 2018",
        "subtitle": "关税战 / 科技战 / 多极化",
        "key_insight": "多极化的开始",
        "narr": "2018 年特朗普对中国加征关税, 中美进入战略竞争。\n"
                "从关税战升级到科技战, 华为/芯片/AI 全方位博弈。\n"
                "中美贸易战标志着单极时代结束, 多极化正式开始。"
    },
    "hp_012": {
        "id": "hp_012_新冠疫情_2020",
        "title": "新冠疫情 · 2020",
        "subtitle": "全球大流行 / 封国 / 疫苗",
        "key_insight": "全球化的脆弱性",
        "narr": "2020 年 3 月 11 日 WHO 宣布新冠全球大流行。\n"
                "封国封城暴露了全球供应链的脆弱性。\n"
                "但也加速了远程办公、mRNA 疫苗、电商的发展。"
    },
    "hp_013": {
        "id": "hp_013_俄乌冲突_2022",
        "title": "俄乌冲突 · 2022",
        "subtitle": "欧洲二战后最大地缘危机",
        "key_insight": "北约东扩与俄罗斯安全焦虑",
        "narr": "2022 年 2 月 24 日, 俄罗斯全面入侵乌克兰。\n"
                "这场战争是北约 30 年东扩与俄罗斯安全焦虑的总爆发。\n"
                "俄乌冲突标志着冷战结束后欧洲秩序的终结。"
    },
    "hp_014": {
        "id": "hp_014_AI革命_2023",
        "title": "AI 革命 · 2023",
        "subtitle": "GPT / 大模型 / AGI",
        "key_insight": "工业革命级变革",
        "narr": "2022 年 11 月 ChatGPT 发布, 2023 年生成式 AI 爆发。\n"
                "大模型改变教育/医疗/编程/创意产业。\n"
                "AI 革命堪比蒸汽机/电力, 是工业革命级变革。"
    },
    "hp_015": {
        "id": "hp_015_全球大选年_2024",
        "title": "全球大选年 · 2024",
        "subtitle": "76 国 / 民粹 vs 自由",
        "key_insight": "民主制度的再平衡",
        "narr": "2024 年全球 76 国举行大选, 涉及 40 亿人口。\n"
                "美/英/法/印度/印尼 等多国民粹与建制派博弈。\n"
                "这是民主制度面对全球化与身份政治的再平衡。"
    },
}


def gen_video(hp_id: str, output_dir: Path = OUTPUT_ROOT) -> bool:
    """单张 K 卡 → 30s 视频"""
    if hp_id not in HISTORY_K_CARDS_V2:
        print(f"  ERROR: {hp_id} 不在 v2 列表")
        return False

    card = HISTORY_K_CARDS_V2[hp_id]
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. 写 manim 脚本 (与 history_k_video_gen 完全一致)
    manim_script = f'''"""Auto-generated manim scene for {hp_id}"""
from manim import Scene, Text, Write, FadeIn, FadeOut, BLUE, WHITE, ORIGIN, UP, DOWN

GOLD = "#C9A227"
INK = "#2A2A2A"

class HistoryKCard(Scene2):
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

    # 修正 import: Scene2 → Scene (上面只是测试用)
    manim_script = manim_script.replace("Scene2", "Scene")

    manim_path = output_dir / f"{hp_id}_manim.py"
    manim_path.write_text(manim_script, encoding="utf-8")

    # 2. 跑 manim (--media_dir 让输出到 ./videos)
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

    # 3. 找 mp4 输出
    mp4_src = output_dir / "videos" / f"{hp_id}_manim" / "480p15" / "HistoryKCard.mp4"
    if not mp4_src.exists():
        candidates = list((output_dir / f"{hp_id}_manim" / "media" / "videos").rglob("HistoryKCard.mp4"))
        if candidates:
            mp4_src = candidates[0]
    if not mp4_src.exists():
        print(f"  [manim mp4 not found]")
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
    for hp_id in HISTORY_K_CARDS_V2:
        print(f"\n=== {hp_id} ===")
        ok = gen_video(hp_id)
        rc += 0 if ok else 1
    print(f"\n完成 {len(HISTORY_K_CARDS_V2) - rc}/{len(HISTORY_K_CARDS_V2)} 张")
    return rc


def main():
    parser = argparse.ArgumentParser(description="历史 K 卡 v2 → 30s 视频扩展 (10 张)")
    sub = parser.add_subparsers(dest="cmd")

    p_gen = sub.add_parser("gen")
    p_gen.add_argument("--hp-id", required=True, choices=list(HISTORY_K_CARDS_V2.keys()))
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