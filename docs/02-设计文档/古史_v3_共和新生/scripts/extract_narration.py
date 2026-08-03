# -*- coding: utf-8 -*-
"""
提取四集广播剧旁白文本
每集生成3段：卷首语（时间线总述） / 第二幕（艺术问题） / 第三幕（当代回响）
"""

import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def load_episodes():
    episodes = []
    files = [
        "古史_v3_ep01_天朝崩塌.py",
        "古史_v3_ep02_帝国挽歌.py",
        "古史_v3_ep03_觉醒年代.py",
        "古史_v3_ep04_共和新生.py",
    ]
    for fname in files:
        ns = {}
        with open(os.path.join(SCRIPT_DIR, fname), "r", encoding="utf-8") as f:
            exec(compile(f.read(), fname, "exec"), ns)
        episodes.append(ns["get_data"]())
    return episodes


def build_narration(ep):
    """
    构建广播剧旁白脚本。
    每集结构：
      [卷首语]  时间线总述
      [第二幕]  艺术问题（设问 + 背景）
      [第三幕]  当代回响（总述 + 三段当代启示）
    """
    lines = []
    lines.append(f"《共和新生》{ep['ep']} {ep['title']}")
    lines.append(f"——{ep['subtitle']}")
    lines.append("")
    lines.append("【卷首语】")
    lines.append(ep["timeline"]["overview"].strip())
    lines.append("")
    lines.append("【第二幕：艺术问题】")
    aq = ep["art_question"]
    lines.append(aq["question"].strip())
    lines.append("")
    lines.append(aq["context"].strip())
    lines.append("")
    lines.append("【第三幕：当代回响】")
    ce = ep["contemporary_echo"]
    lines.append(ce["overview"].strip())
    lines.append("")
    for pt in ce["echo_points"]:
        lines.append(f"第一点：{pt['modern_issue']}。历史关联：{pt['historical_connection'].strip()}")
        lines.append(f"当代启示：{pt['contemporary_reflection'].strip()}")
        lines.append("")
    return "\n".join(lines)


def main():
    episodes = load_episodes()
    print("已加载 %d 集" % len(episodes))

    scripts = []
    for ep in episodes:
        script = build_narration(ep)
        scripts.append({
            "ep": ep["ep"],
            "title": ep["title"],
            "script": script,
            "char_count": len(script)
        })
        print("Ep%d %s: %d 字" % (ep["ep"], ep["title"], len(script)))

    # 写入文本文件
    combined = []
    for s in scripts:
        combined.append("=" * 50)
        combined.append("第%d集 %s" % (s["ep"], s["title"]))
        combined.append("=" * 50)
        combined.append("")
        combined.append(s["script"])
        combined.append("")
        combined.append("")

    all_text = "\n".join(combined)
    out_path = os.path.join(SCRIPT_DIR, "..", "古史_v3_广播剧旁白原文.txt")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(all_text)
    print("\n旁白原文已写入: %s" % out_path)

    return scripts


if __name__ == "__main__":
    main()
