# -*- coding: utf-8 -*-
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def load_ep(ep_num):
    ep_files = {
        1: "古史_v3_ep01_天朝崩塌.py",
        2: "古史_v3_ep02_帝国挽歌.py",
        3: "古史_v3_ep03_觉醒年代.py",
        4: "古史_v3_ep04_共和新生.py",
    }
    ns = {}
    with open(os.path.join(SCRIPT_DIR, ep_files[ep_num]), "r", encoding="utf-8") as f:
        exec(compile(f.read(), ep_files[ep_num], "exec"), ns)
    return ns["get_data"]()


def build_4_segments(ep):
    """生成四段广播剧旁白"""
    seg1 = "%s %s。" % (ep["title"], ep["subtitle"])
    seg1 += ep["timeline"]["overview"].strip()
    # 避免太长，seg1保持在合理长度
    if len(seg1) > 350:
        seg1 = seg1[:340] + "……"

    # seg2: 时间线事件（选最重要的几个）
    events = ep["timeline"]["events"]
    seg2_parts = []
    for ev in events[:5]:
        seg2_parts.append("%s年，%s。%s" % (ev["year"], ev["title"], ev["description"][:80]))
    seg2 = "。".join(seg2_parts)

    # seg3: 艺术问题
    aq = ep["art_question"]
    seg3 = aq["context"].strip()
    if len(seg3) > 400:
        seg3 = seg3[:390] + "……"

    # seg4: 当代回响（三段启示）
    ce = ep["contemporary_echo"]
    seg4_parts = [ce["overview"].strip()]
    for pt in ce["echo_points"]:
        seg4_parts.append("第一点，关于%s。历史关联：%s。当代启示：%s" % (
            pt["modern_issue"],
            pt["historical_connection"].strip(),
            pt["contemporary_reflection"].strip()
        ))
    seg4 = "。".join(seg4_parts)
    if len(seg4) > 600:
        # 截取三段启示的核心内容
        seg4 = "。".join(seg4_parts[:3])
        if len(seg4) > 600:
            seg4 = seg4[:590] + "……"

    return [seg1, seg2, seg3, seg4]


for ep_num in [2, 3, 4]:
    ep = load_ep(ep_num)
    segs = build_4_segments(ep)
    print("=== Ep%d %s ===" % (ep_num, ep["title"]))
    for i, s in enumerate(segs, 1):
        print("[Seg%d] %d字" % (i, len(s)))
        print(s[:80])
        print()
    print()
