"""P-001 批量渲染器 v0.1 — 10 支历史素材批量测试

W28 任务: 验证渲染管线稳定性, 10 支 ≥ 80% 成功率 (A 止损点)
用法: python batch_render.py
"""
import sys
import subprocess
import importlib.util
import asyncio
import shutil
import json
import time
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent.parent.parent
MEDIA = Path(__file__).parent / "media"
BATCH_OUT = MEDIA / "batch" / "w28"
REPORT = BATCH_OUT / "report.json"

# 10 支候选 (古史 v4 ep01-06 + v3 ep01-04)
CANDIDATES = [
    ("v4", "ep01_帝国的崩塌", "2_structure/TextExperience/古史_v4_世界风云/scripts/古史_v4_ep01_帝国的崩塌.py"),
    ("v4", "ep02_赤旗与铁幕的升起", "2_structure/TextExperience/古史_v4_世界风云/scripts/古史_v4_ep02_赤旗与铁幕的升起.py"),
    ("v4", "ep03_大十字", "2_structure/TextExperience/古史_v4_世界风云/scripts/古史_v4_ep03_大十字.py"),
    ("v4", "ep04_冷战铁幕", "2_structure/TextExperience/古史_v4_世界风云/scripts/古史_v4_ep04_冷战铁幕.py"),
    ("v4", "ep05_帝国的黄昏", "2_structure/TextExperience/古史_v4_世界风云/scripts/古史_v4_ep05_帝国的黄昏.py"),
    ("v4", "ep06_新战国时代", "2_structure/TextExperience/古史_v4_世界风云/scripts/古史_v4_ep06_新战国时代.py"),
    ("v3", "ep01_天朝崩塌", "2_structure/TextExperience/古史_v3_共和新生/scripts/古史_v3_ep01_天朝崩塌.py"),
    ("v3", "ep02_帝国挽歌", "2_structure/TextExperience/古史_v3_共和新生/scripts/古史_v3_ep02_帝国挽歌.py"),
    ("v3", "ep03_觉醒年代", "2_structure/TextExperience/古史_v3_共和新生/scripts/古史_v3_ep03_觉醒年代.py"),
    ("v3", "ep04_共和新生", "2_structure/TextExperience/古史_v3_共和新生/scripts/古史_v3_ep04_共和新生.py"),
]

# 通用化: 截前 5 events (长篇也保持 3-4 分钟)
MAX_EVENTS = 5


def load_data(script_path):
    spec = importlib.util.spec_from_file_location("ep", script_path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.get_data()


def make_render_code(data, ep_tag, max_events=MAX_EVENTS):
    """从 data dict 生成可被 manim 渲染的 scene code"""
    events = data.get('timeline', {}).get('events', [])[:max_events]
    script = [{"year": e['year'], "title": e['title'], "narr": e['description']} for e in events]
    # 纯英文 class 名
    safe_name = "".join(c if c.isalnum() or c == "_" else "_" for c in ep_tag)
    if safe_name[0].isdigit():
        safe_name = "ep_" + safe_name

    return f'''"""动态生成: {ep_tag}"""
import sys
sys.path.insert(0, r"{Path(__file__).parent}")

SCRIPT = {script!r}
TITLE = {data['title']!r}
SUBTITLE = {data['subtitle']!r}
SERIES = {data['series']!r}
EP = {data['ep']!r}
TAG = {ep_tag!r}

from build_p001_v0_1 import P001Ep01, SCRIPT as _S
from manim.constants import UP, DOWN, LEFT, RIGHT
from manim import WHITE, GREY, ORIGIN

SCRIPT = _S
class {safe_name}(P001Ep01):
    def construct(self):
        self.show_title()
        for i, seg in enumerate(SCRIPT):
            self.show_segment(i, seg, is_last=(i == len(SCRIPT) - 1))
        self.show_outro()
'''


def render_one(ep_tag, series, name, script_path):
    """渲染 1 支 ep, 返回 (success: bool, duration: float, error: str)"""
    start = time.time()
    full_path = ROOT / script_path
    if not full_path.exists():
        return False, 0, f"script not found: {script_path}"

    try:
        data = load_data(full_path)
    except Exception as e:
        return False, 0, f"load_data failed: {e}"

    # 动态生成渲染代码
    work_dir = BATCH_OUT / series
    work_dir.mkdir(parents=True, exist_ok=True)
    render_file = work_dir / f"{name}.py"
    render_file.write_text(make_render_code(data, ep_tag), encoding='utf-8')

    # manim 渲染
    output_dir = work_dir / "videos"
    output_dir.mkdir(parents=True, exist_ok=True)
    safe_class = "".join(c if c.isalnum() or c == "_" else "_" for c in ep_tag)
    if safe_class[0].isdigit():
        safe_class = "ep_" + safe_class
    cmd = ["python", "-m", "manim", "-ql", "--media_dir", str(output_dir),
           str(render_file), safe_class]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)

    if result.returncode != 0:
        return False, time.time() - start, f"manim exit {result.returncode}: {result.stderr[-300:]}"

    # 找到输出 mp4
    mp4_files = list((output_dir / "videos").rglob("*.mp4"))
    if not mp4_files:
        return False, time.time() - start, "no mp4 output"

    mp4 = mp4_files[0]
    return True, time.time() - start, str(mp4.relative_to(ROOT))


def main():
    BATCH_OUT.mkdir(parents=True, exist_ok=True)
    print(f"=== W28 批量渲染: 10 支 ep ===")
    print(f"开始: {datetime.now().strftime('%H:%M:%S')}")

    results = []
    for i, (series, name, path) in enumerate(CANDIDATES, 1):
        ep_tag = f"{series}_{name}"
        print(f"\n[{i}/10] {ep_tag}")
        try:
            ok, elapsed, info = render_one(ep_tag, series, name, path)
            size_mb = 0
            if ok:
                mp4_path = ROOT / info
                size_mb = mp4_path.stat().st_size / 1024 / 1024
                print(f"  OK  {elapsed:.1f}s  {size_mb:.1f}MB  {info}")
            else:
                print(f"  ERR {elapsed:.1f}s  {info[:200]}")
            results.append({"ep": ep_tag, "ok": ok, "elapsed": round(elapsed, 1), "size_mb": round(size_mb, 1), "info": info})
        except Exception as e:
            print(f"  EXCEPTION: {e}")
            results.append({"ep": ep_tag, "ok": False, "elapsed": 0, "error": str(e)})

    # 统计
    success = sum(1 for r in results if r['ok'])
    rate = success / len(results) * 100
    total_time = sum(r['elapsed'] for r in results)

    summary = {
        "phase": "W28",
        "total": len(results),
        "success": success,
        "rate_pct": rate,
        "total_elapsed_sec": round(total_time, 1),
        "results": results,
        "decision": "PASS" if rate >= 80 else "FAIL (A 止损点未达)"
    }
    REPORT.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')

    print(f"\n=== 汇总 ===")
    print(f"  成功: {success}/{len(results)} = {rate:.0f}%")
    print(f"  总耗时: {total_time:.1f}s")
    print(f"  决定: {summary['decision']}")
    print(f"  报告: {REPORT}")


if __name__ == "__main__":
    main()
