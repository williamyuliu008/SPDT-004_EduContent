"""P-001 视频生成器 v0.1.1 — 全流程: 视频 + TTS + ffmpeg 合成

用法: python build_p001_full.py
依赖: edge-tts, ffmpeg
"""
import sys
import importlib.util
import subprocess
import asyncio
from pathlib import Path

# 加载 ep01 脚本
ROOT = Path(__file__).parent.parent.parent
EP01_PATH = ROOT / "2_structure" / "TextExperience" / "古史_v4_世界风云" / "scripts" / "古史_v4_ep01_帝国的崩塌.py"
spec = importlib.util.spec_from_file_location("ep01_module", EP01_PATH)
ep01 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ep01)
DATA = ep01.get_data()

SCRIPT = [{"year": e['year'], "title": e['title'], "narr": e['description']} for e in DATA['timeline']['events']]
TTS_VOICE = "zh-CN-YunjianNeural"

MEDIA = Path(__file__).parent / "media"
VIDEO_SRC = MEDIA / "videos" / "build_p001_v0_1" / "480p15" / "P001Ep01.mp4"
AUDIO_OUT = MEDIA / "audio" / "ep01_narration.mp3"
FINAL_OUT = MEDIA / "final" / "P001_Ep01_ImperiasCollapse.mp4"


def build_script_text():
    """拼接 SCRIPT 文本 (供 TTS, 加铺垫让时长 ≈ 3 分钟)"""
    parts = []
    parts.append(f"欢迎观看 {DATA['series']} 系列,第 {DATA['ep']} 集。")
    parts.append(f"{DATA['title']}。{DATA['subtitle']}。")
    parts.append(f"这个系列会带你用三分钟,理解一段改变世界的历史。")
    parts.append(f"本集时间跨度:{DATA['time_period']}。")
    parts.append("")
    for i, s in enumerate(SCRIPT, 1):
        parts.append(f"第 {i} 段,{s['year']} 年,{s['title']}。")
        parts.append(s['narr'])
        parts.append(f"这段历史告诉我们,{s['title']}是工业时代战争的一个缩影。")
        parts.append("")
    parts.append(f"五个事件,串起了第一次世界大战的全貌。")
    parts.append(f"这场战争终结了四个帝国,也催生了一个新的时代。")
    parts.append(f"下集,我们将看到这场战争如何重塑整个世界。")
    parts.append("感谢观看,P-001 视频测试 v0.1,W27 阶段产出。")
    return " ".join(parts)


async def gen_tts():
    import edge_tts
    AUDIO_OUT.parent.mkdir(parents=True, exist_ok=True)
    text = build_script_text()
    print(f"[TTS] 文本长度: {len(text)} 字")
    # rate=-18% 让 TTS 慢一点, 撑到 3 分钟
    communicate = edge_tts.Communicate(text, TTS_VOICE, rate="-18%")
    await communicate.save(str(AUDIO_OUT))
    print(f"[TTS] 输出: {AUDIO_OUT} ({AUDIO_OUT.stat().st_size} bytes)")


def merge():
    FINAL_OUT.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg", "-y",
        "-i", str(VIDEO_SRC),
        "-i", str(AUDIO_OUT),
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "128k",
        "-shortest",
        str(FINAL_OUT)
    ]
    print(f"[FFMPEG] {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[FFMPEG ERROR]\n{result.stderr[-1000:]}")
        return False
    print(f"[FFMPEG] OK -> {FINAL_OUT} ({FINAL_OUT.stat().st_size} bytes)")
    return True


def main():
    print("=== P-001 v0.1.1 全流程 ===")
    print(f"[1/3] 检查视频源: {VIDEO_SRC}")
    if not VIDEO_SRC.exists():
        print(f"FAIL: 视频不存在, 请先跑: python -m manim -ql build_p001_v0_1.py P001Ep01")
        sys.exit(1)

    print(f"[2/3] 生成 TTS 配音")
    asyncio.run(gen_tts())

    print(f"[3/3] ffmpeg 合成")
    if not merge():
        sys.exit(1)

    # 验证
    print("\n=== 验证最终产物 ===")
    cmd_probe = ["ffprobe", "-v", "error", "-show_entries",
                 "format=duration:stream=codec_name,codec_type,width,height",
                 "-of", "default=noprint_wrappers=1", str(FINAL_OUT)]
    subprocess.run(cmd_probe)


if __name__ == "__main__":
    main()
