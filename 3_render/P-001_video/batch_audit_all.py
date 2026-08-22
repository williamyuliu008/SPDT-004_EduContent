"""4 真产品联合审计 v0.1 — W30 v3.0 上半场准出门

P-001 视频 / P-002 知识卡 / P-003 电子书 / P-004 音频 各跑 1 个 P0 样本
"""
import sys
import json
import subprocess
import importlib.util
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT / "tools"))
spec = importlib.util.spec_from_file_location("accuracy_auditor", ROOT / "tools" / "accuracy_auditor.py")
auditor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(auditor)

OUT_REPORT = ROOT / "3_render" / "P-001_video" / "media" / "batch" / "w30_audit_all.json"


def ffprobe_duration(path):
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
            capture_output=True, text=True, timeout=10
        )
        return float(result.stdout.strip())
    except Exception:
        return None


def audit_p001():
    """P-001 视频 P0 样本: v0.1.1 ep01 (含配音)"""
    video_path = ROOT / "3_render" / "P-001_video" / "media" / "final" / "P001_Ep01_ImperiasCollapse.mp4"
    audio_path = ROOT / "3_render" / "P-001_video" / "media" / "audio" / "ep01_narration.mp3"
    ep_script = ROOT / "2_structure" / "TextExperience" / "古史_v4_世界风云" / "scripts" / "古史_v4_ep01_帝国的崩塌.py"

    spec_ep = importlib.util.spec_from_file_location("ep", ep_script)
    m = importlib.util.module_from_spec(spec_ep)
    spec_ep.loader.exec_module(m)
    data = m.get_data()

    events = data.get("timeline", {}).get("events", [])[:5]
    subtitle_chars = sum(len(e.get("description", "")) for e in events) + 30  # +铺垫

    input_data = {
        **data,
        "events": events,
        "subtitle_chars": subtitle_chars,
        "video_duration_sec": ffprobe_duration(video_path),
        "audio_duration_sec": ffprobe_duration(audio_path),
        "video_path": str(video_path),
        "audio_path": str(audio_path),
    }
    tmp = ROOT / "3_render" / "P-001_video" / "media" / "batch" / "_tmp_p001.json"
    tmp.parent.mkdir(parents=True, exist_ok=True)
    tmp.write_text(json.dumps(input_data, ensure_ascii=False, indent=2), encoding='utf-8')
    result = auditor.audit_accuracy("P-001", tmp)
    tmp.unlink()
    return {
        "product": "P-001 视频",
        "sample": "v0.1.1 ep01 帝国的崩塌 (含配音)",
        "video_duration_sec": input_data["video_duration_sec"],
        "audio_duration_sec": input_data["audio_duration_sec"],
        "subtitle_chars": subtitle_chars,
        "result": result,
    }


def audit_p002():
    """P-002 知识卡 P0 样本: K01.json (2026-08-19_一切从实际出发)"""
    card_path = Path("D:/4_data/knowledge_cards/政治/cards/2026-08-19_一切从实际出发/K01.json")
    if not card_path.exists():
        return {"product": "P-002 知识卡", "error": f"sample not found: {card_path}"}
    result = auditor.audit_accuracy("P-002", card_path)
    return {
        "product": "P-002 知识卡",
        "sample": "K01.json (2026-08-19_一切从实际出发)",
        "result": result,
    }


def audit_p003():
    """P-003 电子书 P0 样本: 古史_v3 卡片示范_可读版.md"""
    ebook_path = ROOT / "2_structure" / "TextExperience" / "古史_v3_共和新生" / "scripts" / "古史_v3_卡片示范_可读版.md"
    if not ebook_path.exists():
        return {"product": "P-003 电子书", "error": f"sample not found: {ebook_path}"}
    result = auditor.audit_accuracy("P-003", ebook_path)
    return {
        "product": "P-003 电子书",
        "sample": "古史_v3_卡片示范_可读版.md",
        "result": result,
    }


def audit_p004():
    """P-004 音频 P0 样本: 古史 v3 ep01.mp3 + ep 脚本"""
    audio_path = ROOT / "2_structure" / "TextExperience" / "古史_v3_共和新生" / "audio" / "Ep01_天朝崩塌.mp3"
    ep_script = ROOT / "2_structure" / "TextExperience" / "古史_v3_共和新生" / "scripts" / "古史_v3_ep01_天朝崩塌.py"
    if not audio_path.exists() or not ep_script.exists():
        return {"product": "P-004 音频", "error": f"sample not found: {audio_path}"}

    spec_ep = importlib.util.spec_from_file_location("ep", ep_script)
    m = importlib.util.module_from_spec(spec_ep)
    spec_ep.loader.exec_module(m)
    data = m.get_data()
    events = data.get("timeline", {}).get("events", [])
    subtitle_chars = sum(len(e.get("description", "")) for e in events)

    input_data = {
        **data,
        "subtitle_chars": subtitle_chars,
        "audio_duration_sec": ffprobe_duration(audio_path),
        "audio_path": str(audio_path),
    }
    tmp = ROOT / "3_render" / "P-001_video" / "media" / "batch" / "_tmp_p004.json"
    tmp.parent.mkdir(parents=True, exist_ok=True)
    tmp.write_text(json.dumps(input_data, ensure_ascii=False, indent=2), encoding='utf-8')
    result = auditor.audit_accuracy("P-004", tmp)
    tmp.unlink()
    return {
        "product": "P-004 音频",
        "sample": "古史 v3 ep01 天朝崩塌",
        "audio_duration_sec": input_data["audio_duration_sec"],
        "subtitle_chars": subtitle_chars,
        "result": result,
    }


def main():
    print("=== 4 真产品联合审计 (W30 v3.0 上半场准出门) ===")
    print(f"开始: {datetime.now().strftime('%H:%M:%S')}")

    audits = []
    for fn in [audit_p001, audit_p002, audit_p003, audit_p004]:
        try:
            a = fn()
            r = a.get("result", {})
            print(f"  [{r.get('grade', 'ERROR'):10s}] {a['product']} - {a.get('sample', '?')}")
            print(f"      score: {r.get('total_score', '?')}, issues: {r.get('issue_count', '?')}")
            for rule, issue in r.get("issues", [])[:3]:
                print(f"        - [{rule}] {issue}")
            audits.append(a)
        except Exception as e:
            print(f"  EXCEPTION {fn.__name__}: {e}")
            audits.append({"product": fn.__name__, "error": str(e)})

    # 统计
    grades = [a.get("result", {}).get("grade", "ERROR") for a in audits if "result" in a]
    summary = {
        "phase": "W30 v3.0 上半场",
        "by_grade": {g: grades.count(g) for g in set(grades)},
        "all_gold": all(g == "GOLD" for g in grades),
        "audits": audits,
    }
    OUT_REPORT.parent.mkdir(parents=True, exist_ok=True)
    OUT_REPORT.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')

    print(f"\n=== 汇总 ===")
    for g, n in summary["by_grade"].items():
        print(f"  {g}: {n}/4")
    print(f"  v3.0 上半场 GOLD 判定: {'✅ PASS' if summary['all_gold'] else '❌ FAIL'}")
    print(f"  报告: {OUT_REPORT}")


if __name__ == "__main__":
    main()
