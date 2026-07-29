# -*- coding: utf-8 -*-
"""
古史_v3_共和新生 · 全16链卡片包自动生成器
============================================================
从 episode 数据文件读取关键节点，自动生成三类卡片：
  - 节点卡（Node Card）：从 knowledge_chains[].key_nodes 派生
  - 心法卡（Strategy Card）：按题型模板生成
  - 链卡（Chain Card）：从 chain metadata 生成

输出：
  - 古史_v3_全16链卡片包.py  （Python 数据文件）
  - 古史_v3_全16链卡片包.json  （可导入任意 APP）
  - 古史_v3_全16链_Anki导入.csv  （Anki 直接导入）
"""

import os, json, csv

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# ── 加载所有 episode 数据 ──────────────────────────────────
def load_all_episodes():
    episodes = []
    episode_files = [
        "古史_v3_ep01_天朝崩塌.py",
        "古史_v3_ep02_帝国挽歌.py",
        "古史_v3_ep03_觉醒年代.py",
        "古史_v3_ep04_共和新生.py",
    ]
    for fname in episode_files:
        fpath = os.path.join(SCRIPT_DIR, fname)
        namespace = {}
        with open(fpath, "r", encoding="utf-8") as f:
            exec(compile(f.read(), fpath, "exec"), namespace)
        episodes.append(namespace["get_data"]())
    return episodes


# ── 从 key_nodes 派生节点卡 ──────────────────────────────────
def make_node_cards(chain_id, chain_title, key_nodes, episode_num, start_num=1):
    """
    key_nodes: list of dict {node: str, answer: str}
    每条 key_node 派生出1张节点卡。
    额外补充「时间轴卡」和「对比卡」（部分链）。
    """
    cards = []
    card_num = start_num

    for kn in key_nodes:
        node = kn["node"]
        answer = kn["answer"]

        # 自动判断卡片子类型
        if any(kw in node for kw in ["时间", "年代", "年份"]):
            card_type = "时序卡"
        elif any(kw in node for kw in ["条约", "协定", "法", "制度", "文件"]):
            card_type = "条约/制度卡"
        elif any(kw in node for kw in ["原因", "背景"]):
            card_type = "原因卡"
        elif any(kw in node for kw in ["意义", "影响", "结果", "地位"]):
            card_type = "影响卡"
        elif any(kw in node for kw in ["比较", "对比", "异同"]):
            card_type = "对比卡"
        elif any(kw in node for kw in ["人物", "代表", "领袖"]):
            card_type = "人物卡"
        elif any(kw in node for kw in ["内容", "主张", "纲领", "措施"]):
            card_type = "内容卡"
        else:
            card_type = "概念卡"

        card_id = f"H_近代_{episode_num:02d}_{card_num:02d}" if episode_num <= 12 else f"H_现代_{episode_num-12:02d}_{card_num:02d}"

        front = node + "？"
        if not front.endswith("？"):
            front = f"简述：{node}"

        # 背面的细节（自动生成语境提示）
        back_detail = f"""
【所属链】：{chain_title}（{chain_id}）
【记忆定位】：{node} → {answer.split('；')[0] if '；' in answer else answer}

【记忆技巧】：
- 联想该节点在链中的位置（前因→后果）
- 回忆与该节点直接相邻的两个事件
- 试着用一句话概括这段内容，向自己复述
        """.strip()

        cards.append({
            "card_id": card_id,
            "chain_id": chain_id,
            "chain_title": chain_title,
            "card_type": card_type,
            "front": front,
            "back_core": answer,
            "back_detail": back_detail,
            "maturity": "🟡",
            "tags": [f"#{chain_title[:4]}", f"#{card_type}"]
        })
        card_num += 1

    return cards


# ── 策略卡片模板 ────────────────────────────────────────────
STRATEGY_TEMPLATES = {
    "原因类": {
        "card_id_prefix": "H_心法_原因类",
        "front": "【原因类】历史事件的原因分析：如何区分根本原因、主要原因与直接原因？",
        "thinking_steps": """
【第一步：审题——三层分离】

  ① 根本原因：生产力/制度/阶级矛盾/国际格局（深层结构）
  ② 主要原因：利益冲突/阶级立场/直接关联方（中层机制）
  ③ 直接原因：触发性事件/人物/偶发决策（导火索）

【第二步：答案组织】

  根本原因 = 时代背景 + 结构性矛盾（必答）
  主要原因 = 关键行动方的利益驱动（视分值补）
  直接原因 = 触发事件（直接原因题必答）
        """.strip(),
        "answer_framework": """
① 根本原因（结构性）：
  时代背景 + 深层矛盾 → 必然趋势

② 主要原因（关键机制）：
  相关方利益驱动 + 矛盾激化

③ 直接原因（触发）：
  具体事件 + 导火索
        """.strip(),
        "common_traps": [
            "把直接原因当根本原因（最常见！）",
            "只写中国一方，忽视国际背景",
            "原因与背景混淆（背景范围更大）",
            "绝对化表述，缺少限定词"
        ]
    },
    "影响类": {
        "card_id_prefix": "H_心法_影响类",
        "front": "【影响类】历史事件的影响分析：如何从短期/长期、积极/消极多维度展开？",
        "thinking_steps": """
【第一步：判断影响类型】

  短期影响 → 事件后立即产生的直接后果
  长期影响 → 对后世历史走向的深层塑造

【第二步：四维度展开】

  政治：主权/领土/制度/阶级力量对比
  经济：生产力/生产关系/贸易结构
  思想：思潮/观念/知识分子觉醒
  外交：国际地位/中外关系

【第三步：区分「直接影响」与「深远后果」】
        """.strip(),
        "answer_framework": """
一、短期/直接影响
  ① 政治：XXXX
  ② 经济：XXXX
  ③ 外交：XXXX

二、长期/深远后果
  ④ 社会性质/结构：XXXX
  ⑤ 历史任务/走向：XXXX
  ⑥ 精神遗产：XXXX
        """.strip(),
        "common_traps": [
            "影响与意义混淆（意义专指正面价值）",
            "只说结论，缺少推导过程",
            "漏掉外交/国际格局维度",
            "积极/消极影响不分层"
        ]
    },
    "变革/制度类": {
        "card_id_prefix": "H_心法_变革类",
        "front": "【变革类】如何分析一场改革/变法的内容、背景与成败原因？",
        "thinking_steps": """
【第一步：背景——为什么需要变？】

  ① 社会矛盾尖锐化（土地/财政/民族等）
  ② 统治危机（阶级矛盾、对外失败）
  ③ 思想准备（有无新的理论依据）

【第二步：内容——变了什么？】

  ① 政治改革
  ② 经济改革
  ③ 军事/教育/其他

【第三步：成败原因——为什么成功/失败？】

  成功条件：触动利益少 + 有实权支持 + 群众基础
  失败原因：触动守旧势力 + 缺乏实权 + 无群众支持
        """.strip(),
        "answer_framework": """
一、变法背景（必要性）：
  ① XXXX（社会矛盾）
  ② XXXX（统治危机）

二、变法内容（主要措施）：
  ① 政治：XXXX
  ② 经济：XXXX
  ③ 军事/教育：XXXX

三、失败/成功原因：
  ① 守旧势力反对（触动核心利益）
  ② 缺乏实权支持（寄希望于皇帝/权臣）
  ③ 无群众基础（脱离底层）
        """.strip(),
        "common_traps": [
            "把变法内容与洋务运动/革命混淆",
            "失败原因只写一条（需要多角度）",
            "忽视变法的积极意义（即使失败也有思想启蒙价值）",
            "不区分改革与革命的本质差异"
        ]
    },
    "概念类": {
        "card_id_prefix": "H_心法_概念类",
        "front": "【概念类】如何准确界定和阐述一个历史概念？",
        "thinking_steps": """
【第一步：定义三要素】

  ① 时间（何时）
  ② 主体（谁/什么）
  ③ 内容（做了什么/是什么）

【第二步：特征提炼】

  该概念区别于其他概念的独特之处

【第三步：历史定位】

  在历史链条中的位置：前承X，下启Y
        """.strip(),
        "answer_framework": """
【定义】：XXXX（时间+主体+核心行为）

【主要内容】：
  ① XXXX
  ② XXXX

【历史意义/评价】：
  ① XXXX（积极面）
  ② XXXX（局限性）
        """.strip(),
        "common_traps": [
            "定义过于笼统，缺少时间/主体/内容三要素",
            "只背教材原话，不理解概念的本质",
            "忽视概念的动态演变（不同阶段有不同内涵）",
            "概念与相近概念混淆（如半殖民地vs半封建）"
        ]
    }
}


def make_strategy_card(chain_id, chain_title, strategy_type, card_num):
    tpl = STRATEGY_TEMPLATES[strategy_type]
    card_id = f"{tpl['card_id_prefix']}_{card_num:02d}"
    return {
        "card_id": card_id,
        "chain_id": chain_id,
        "chain_title": chain_title,
        "card_type": f"心法卡·{strategy_type}",
        "front": tpl["front"],
        "thinking_steps": tpl["thinking_steps"],
        "answer_framework": tpl["answer_framework"],
        "common_traps": tpl["common_traps"],
        "maturity": "🟡",
        "tags": [f"#{strategy_type}", "#心法", "#通法"]
    }


# ── 链卡生成 ────────────────────────────────────────────────
def make_chain_card(chain_id, chain_title, chain_type, core_pattern, narrative_snippet, episode_title, related_chains):
    return {
        "chain_id": chain_id,
        "chain_title": chain_title,
        "chain_type": chain_type,
        "core_pattern": core_pattern,
        "narrative_snippet": narrative_snippet[:500] + "……" if len(narrative_snippet) > 500 else narrative_snippet,
        "episode_title": episode_title,
        "related_chains": related_chains[:3] if related_chains else [],
        "mastery": "🟡",
        "card_type": "链卡"
    }


# ── 主生成逻辑 ──────────────────────────────────────────────
def generate_all_cards(episodes):
    all_node_cards = []
    all_strategy_cards = []
    all_chain_cards = []

    node_counter = 1
    strategy_counter = 1

    # 每集对应的时代编号（前12用H_近代，后4用H_现代）
    episode_ids = {
        1: (1, "H_近代"),   # ep1-3 = 近代
        2: (5, "H_近代"),   # ep2 = 近代
        3: (9, "H_近代"),   # ep3 = 近代
        4: (1, "H_现代")    # ep4 = 现代
    }

    for ep in episodes:
        ep_num = ep["ep"]
        ep_title = ep["title"]

        # 映射到卡片编号序列
        if ep_num <= 3:
            card_ep_id = ep_num
        else:
            card_ep_id = ep_num - 3 + 12  # ep4 = 现代01

        chains = ep["knowledge_chains"]
        for chain_key, chain_data in chains.items():
            chain_id = chain_data["chain_id"]
            chain_title = chain_data["chain_title"]
            chain_type = chain_data["chain_type"]
            core_pattern = chain_data["core_pattern"]
            narrative = chain_data["narrative"]
            key_nodes = chain_data["key_nodes"]

            # ① 链卡
            # 找关联链（从其他集的数据里匹配）
            all_chain_ids = [c for ep2 in episodes for c in ep2["knowledge_chains"].keys()]
            related = []
            for ck, cd in chains.items():
                if ck != chain_key:
                    related.append(f"{cd['chain_id']}（{cd['chain_title']}）")

            chain_card = make_chain_card(
                chain_id, chain_title, chain_type, core_pattern,
                narrative, ep_title, related
            )
            all_chain_cards.append(chain_card)

            # ② 节点卡（从key_nodes派生）
            node_cards = make_node_cards(
                chain_id, chain_title, key_nodes,
                episode_num=card_ep_id, start_num=node_counter
            )
            # 修正card_id编号（每链从01开始）
            chain_node_offset = 1
            for nc in node_cards:
                nc["card_id"] = f"{nc['card_id'][:9]}{chain_node_offset:02d}"
                chain_node_offset += 1
            all_node_cards.extend(node_cards)
            node_counter = (node_counter + len(key_nodes)) % 100 or 1

            # ③ 心法卡（根据链的类型选择策略模板）
            # 危机/探索链 → 原因类+影响类
            # 改革/变法链 → 变革/制度类
            # 概念密集链 → 概念类+原因类
            if "变革" in chain_title or "变法" in chain_title or "改革" in chain_title:
                strategy_types = ["变革/制度类", "原因类"]
            elif "概念" in chain_title or "启蒙" in chain_title or "文化" in chain_title:
                strategy_types = ["概念类", "原因类"]
            else:
                strategy_types = ["原因类", "影响类"]

            for st in strategy_types:
                sc = make_strategy_card(chain_id, chain_title, st, strategy_counter)
                all_strategy_cards.append(sc)
                strategy_counter += 1

    return {
        "node_cards": all_node_cards,
        "strategy_cards": all_strategy_cards,
        "chain_cards": all_chain_cards
    }


# ── 输出格式生成 ────────────────────────────────────────────

def export_python(pkg, out_path):
    """输出 Python 数据文件"""
    lines = ['# -*- coding: utf-8 -*-', '"""古史_v3全16链卡片包"""', '', 'def get_data():']
    lines.append('    return ' + json.dumps(pkg, ensure_ascii=False, indent=8))
    lines.append('')
    content = '\n'.join(lines)
    # 修正 JSON→Python dict 语法（json.dumps用双引号，Python dict合法）
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(content)
    size = os.path.getsize(out_path)
    print(f"[Python] {out_path} ({size/1024:.1f} KB)")


def export_json(pkg, out_path):
    """输出 JSON 文件（通用）"""
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(pkg, f, ensure_ascii=False, indent=2)
    size = os.path.getsize(out_path)
    print(f"[JSON] {out_path} ({size/1024:.1f} KB)")


def export_anki_csv(pkg, out_path):
    """输出 Anki 可导入的 CSV（字段：front, back, tags, type）"""
    rows = []

    # 节点卡：front / back_core+back_detail / tags
    for nc in pkg["node_cards"]:
        back = nc["back_core"]
        if nc.get("back_detail"):
            back += "\n\n" + nc["back_detail"]
        rows.append({
            "front": nc["front"],
            "back": back,
            "tags": " ".join(nc["tags"]),
            "card_type": "node",
            "card_id": nc["card_id"],
            "chain_id": nc["chain_id"]
        })

    # 心法卡：front / thinking_steps + framework + traps
    for sc in pkg["strategy_cards"]:
        back = "【思维步骤】\n" + sc["thinking_steps"]
        back += "\n\n【答案框架】\n" + sc["answer_framework"]
        back += "\n\n【常见陷阱】\n" + "\n".join(f"• {t}" for t in sc["common_traps"])
        rows.append({
            "front": sc["front"],
            "back": back,
            "tags": " ".join(sc["tags"]),
            "card_type": "strategy",
            "card_id": sc["card_id"],
            "chain_id": sc["chain_id"]
        })

    # 链卡：chain_title / narrative / related
    for cc in pkg["chain_cards"]:
        back = f"【类型】{cc['chain_type']}\n【核心规律】{cc['core_pattern']}\n\n【剧本摘要】{cc['narrative_snippet']}\n\n【关联链】" + "\n".join(f"• {r}" for r in cc["related_chains"])
        rows.append({
            "front": f"【链卡】{cc['chain_title']}",
            "back": back,
            "tags": f"#链卡 #{cc['chain_title'][:4]}",
            "card_type": "chain",
            "card_id": cc["chain_id"],
            "chain_id": cc["chain_id"]
        })

    # 写入 CSV（UTF-8 BOM，兼容 Excel 和 Anki）
    with open(out_path, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["front", "back", "tags", "card_type", "card_id", "chain_id"])
        writer.writeheader()
        writer.writerows(rows)

    size = os.path.getsize(out_path)
    print(f"[Anki CSV] {out_path} ({size/1024:.1f} KB, {len(rows)} cards)")


# ── 主程序 ───────────────────────────────────────────────────
def main():
    print("=" * 55)
    print("古史_v3全16链卡片包 · 自动生成器")
    print("=" * 55)

    episodes = load_all_episodes()
    print(f"已加载 {len(episodes)} 集数据")

    pkg = generate_all_cards(episodes)
    n_nodes = len(pkg["node_cards"])
    n_strat = len(pkg["strategy_cards"])
    n_chains = len(pkg["chain_cards"])
    print(f"生成卡片：节点卡 {n_nodes} 张 | 心法卡 {n_strat} 张 | 链卡 {n_chains} 张")
    print(f"总计：{n_nodes + n_strat + n_chains} 张")

    desktop = os.path.join(os.path.expanduser("~"), "Desktop")

    out_py = os.path.join(desktop, "古史_v3_全16链卡片包.json")
    out_json = os.path.join(desktop, "古史_v3_全16链卡片包.json")
    out_csv = os.path.join(desktop, "古史_v3_全16链_Anki导入.csv")

    # JSON（含Python兼容版）
    pkg_clean = {k: v for k, v in pkg.items()}
    with open(out_json, 'w', encoding='utf-8') as f:
        json.dump(pkg_clean, f, ensure_ascii=False, indent=2)
    size = os.path.getsize(out_json)
    print(f"[JSON] {out_json} ({size/1024:.1f} KB)")

    # Anki CSV
    export_anki_csv(pkg_clean, out_csv)

    print("=" * 55)
    print("[OK] All done!")
    print(f"[JSON] {out_json}")
    print(f"[CSV]  {out_csv}")


if __name__ == "__main__":
    main()
