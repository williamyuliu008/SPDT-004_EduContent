"""P-001 视频批量审计 v0.1 — W29

用法: python batch_audit_p001.py
依赖: accuracy_auditor.py, ffprobe, W28 批量渲染产物
"""
import sys
import json
import subprocess
import importlib.util
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT / "tools"))

# 加载 accuracy_auditor
spec = importlib.util.spec_from_file_location("accuracy_auditor", ROOT / "tools" / "accuracy_auditor.py")
auditor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(auditor)

# W28 报告 + 10 支 mp4
BATCH_DIR = Path(__file__).parent / "media" / "batch" / "w28"
W28_REPORT = BATCH_DIR / "report.json"
OUT_REPORT = BATCH_DIR / "audit_p001.json"

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


def ffprobe_duration(path):
    """ffprobe 拿时长 (秒)"""
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
            capture_output=True, text=True, timeout=10
        )
        return float(result.stdout.strip())
    except Exception as e:
        return None


def build_p001_input(series, name, script_path):
    """构造 P-001 审计输入 dict"""
    full_path = ROOT / script_path
    spec = importlib.util.spec_from_file_location("ep", full_path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    data = m.get_data()

    # 截前 5 events (与 W28 batch_render 一致)
    events = data.get("timeline", {}).get("events", [])[:5]
    data["timeline"]["events"] = events

    # 字幕字符数 (5 段描述 + 段号提示)
    subtitle_chars = 0
    for i, ev in enumerate(events, 1):
        subtitle_chars += len(ev.get("description", ""))
        subtitle_chars += 6  # 段号提示 "第 1 段," 等

    # 找 W28 渲染的 mp4
    mp4_pattern = list((BATCH_DIR / series / "videos" / "videos").rglob(f"*{name}*.mp4"))
    video_path = mp4_pattern[0] if mp4_pattern else None

    input_data = {
        **data,
        "subtitle_chars": subtitle_chars,
        "video_path": str(video_path) if video_path else None,
        "video_duration_sec": ffprobe_duration(video_path) if video_path else None,
    }
    return input_data, data


def main():
    print(f"=== P-001 批量审计 (W29) ===")
    print(f"开始: {datetime.now().strftime('%H:%M:%S')}")

    results = []
    for series, name, path in CANDIDATES:
        try:
            input_data, ep_data = build_p001_input(series, name, path)
            result = auditor.audit_accuracy("P-001", Path(__file__))  # 临时路径, 直接传 dict
            # audit_accuracy 读 .json/.md, 我们用临时 json 文件传 dict
            tmp_json = BATCH_DIR / f"_tmp_{series}_{name}.json"
            tmp_json.write_text(json.dumps(input_data, ensure_ascii=False, indent=2), encoding='utf-8')
            result = auditor.audit_accuracy("P-001", tmp_json)
            tmp_json.unlink()

            results.append({
                "ep": f"{series}_{name}",
                "title": ep_data.get("title", "?"),
                "events": len(ep_data.get("timeline", {}).get("events", [])),
                "video_duration": round(input_data.get("video_duration_sec") or 0, 1),
                "subtitle_chars": input_data["subtitle_chars"],
                "grade": result.get("grade"),
                "score": result.get("total_score"),
                "issues": result.get("issues", []),
            })
            r = results[-1]
            print(f"  [{r['grade']:8s}] {r['score']:.3f} {r['ep']} ({r['video_duration']}s, {r['subtitle_chars']}字)")
            for rule, issue in r['issues'][:3]:
                print(f"      - [{rule}] {issue}")
        except Exception as e:
            print(f"  EXCEPTION {series}_{name}: {e}")
            results.append({"ep": f"{series}_{name}", "error": str(e)})

    # 统计
    by_grade = {}
    for r in results:
        g = r.get("grade", "ERROR")
        by_grade[g] = by_grade.get(g, 0) + 1

    summary = {
        "phase": "W29",
        "total": len(results),
        "by_grade": by_grade,
        "results": results,
    }
    OUT_REPORT.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')

    print(f"\n=== 汇总 ===")
    print(f"  总数: {len(results)}")
    for g, n in by_grade.items():
        print(f"  {g}: {n}")
    print(f"  报告: {OUT_REPORT}")


if __name__ == "__main__":
    main()
