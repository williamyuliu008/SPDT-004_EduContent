# -*- coding: utf-8 -*-
"""
PT-037 自适应备考智能体平台 — Flask API Server
启动后端服务，供 gui.html 调用
"""

import json, sys, os, traceback
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# ─── 项目路径 ────────────────────────────────────────────────────────────────
PT_ROOT = Path(__file__).parent.parent
CORE    = PT_ROOT / "_01_platform_core"
sys.path.insert(0, str(CORE))

# 自动加载 API key
_api_key_path = Path("D:/_CEO/bulletin/SECRET_KEY/zhipu_api.txt")
if _api_key_path.exists():
    os.environ["ZHIPU_API_KEY"] = _api_key_path.read_text(encoding="utf-8").strip()

# ─── Flask App ───────────────────────────────────────────────────────────────
app = Flask(__name__, static_folder=".", static_url_path="")
CORS(app)

# ─── 全局 Agent 实例（懒加载） ───────────────────────────────────────────────
_agents = {}

def get_agents():
    if not _agents:
        from llm.llm_wrapper import create_llm_client
        from knowledge_base.knowledge_base import KnowledgeBase
        from agent_conductor.agent_conductor import AgentConductor, UserState
        from agent_coach.agent_coach import AgentCoach
        from agent_auditor.agent_auditor import AgentAuditor

        llm_mode = "glm" if os.environ.get("ZHIPU_API_KEY") else "mock"
        pack_path = PT_ROOT / "_03_subject_packs" / "cafa_calligraphy_2026"
        # 使用 cafa_calligraphy_2026/ 根目录，让 KnowledgeBase 正确加载:
        #   knowledge/kb_vocab.json (或 kb_vocab_enhanced.json)
        #   scripts/error_scripts.json
        #   scripts/punctuation_library.json
        kb_path = pack_path

        _agents["llm"]      = create_llm_client(mode=llm_mode)
        _agents["kb"]       = KnowledgeBase.from_pack(kb_path)
        _agents["conductor"]= AgentConductor(_agents["llm"], _agents["kb"])
        _agents["coach"]    = AgentCoach(_agents["llm"], _agents["kb"])
        _agents["auditor"]  = AgentAuditor(_agents["llm"], _agents["kb"])
        _agents["state"]    = UserState(
            user_id="gui_user",
            S_score=50.0,
            C_cognitive_load=3.0,
            F_fatigue=0.3,
            I_interest=6.0,
            pack_id="cafa_calligraphy_2026"
        )
    return _agents


# ─── API 路由 ────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory(".", "gui.html")

@app.route("/kb")
def kb_browser():
    return send_from_directory(".", "kb_browser.html")

@app.route("/api/status")
def api_status():
    """健康检查 + 状态"""
    try:
        agents = get_agents()
        kb = agents["kb"]
        summary = kb.summary()
        state = agents["state"]
        return jsonify({
            "ok": True,
            "llm_mode": "glm" if os.environ.get("ZHIPU_API_KEY") else "mock",
            "kb": {
                "total_kb_entries": summary["total_kb_entries"],
                "total_translation_entries": summary["total_translation_entries"],
                "total_punctuation_texts": summary["total_punctuation_texts"],
                "total_error_scripts": summary["total_error_scripts"],
            },
            "user_state": state.summary(),
        })
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route("/api/decide", methods=["POST"])
def api_decide():
    """Agent5 调度决策"""
    try:
        agents = get_agents()
        state = agents["state"]
        decision = agents["conductor"].decide(state)
        return jsonify({
            "ok": True,
            "action_type": decision.action_type,
            "target_agent": decision.target_agent,
            "priority": decision.priority,
            "reasoning": decision.reasoning,
            "scaffold_level": decision.scaffold_level,
            "duration_minutes": decision.duration_minutes,
            "content_spec": decision.content_spec,
        })
    except Exception as e:
        return jsonify({"ok": False, "error": str(e), "trace": traceback.format_exc()}), 500

@app.route("/api/question", methods=["POST"])
def api_question():
    """Agent4 生成训练题"""
    try:
        agents = get_agents()
        coach = agents["coach"]
        state = agents["state"]
        body = request.get_json() or {}
        focus_kb_id = body.get("focus_kb_id")
        difficulty = body.get("difficulty", "Lv3")
        pack_id = body.get("pack_id", state.pack_id)

        q = coach.generate_question(
            focus_kb_id=focus_kb_id,
            difficulty=difficulty,
            pack_id=pack_id
        )
        if "error" in q:
            return jsonify({"ok": False, "error": q["error"]}), 500
        return jsonify({"ok": True, "question": q})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e), "trace": traceback.format_exc()}), 500

@app.route("/api/grade", methods=["POST"])
def api_grade():
    """Agent4 评分"""
    try:
        agents = get_agents()
        coach = agents["coach"]
        kb = agents["kb"]
        body = request.get_json() or {}
        q = body.get("question", {})
        user_answer = body.get("answer", "")
        entry = kb.get_entry(q.get("kb_id")) if q.get("kb_id") else None

        grading = coach.grade_answer(q, user_answer, entry)

        # 更新用户状态
        state = agents["state"]
        is_correct = grading.get("correct", False)
        ability_id = q.get("ability_id", "A5")
        decision_dur = body.get("duration_minutes", 5)
        state.update_from_answer(is_correct, ability_id)
        state.tick(decision_dur)

        return jsonify({
            "ok": True,
            "grading": grading,
            "user_state": state.summary(),
        })
    except Exception as e:
        return jsonify({"ok": False, "error": str(e), "trace": traceback.format_exc()}), 500

@app.route("/api/audit", methods=["POST"])
def api_audit():
    """Agent2 知识审计"""
    try:
        agents = get_agents()
        auditor = agents["auditor"]
        kb = agents["kb"]
        body = request.get_json() or {}
        kb_id = body.get("kb_id", "KB_CAFA_S001")
        entry = kb.get_entry(kb_id)
        if not entry:
            return jsonify({"ok": False, "error": f"知识点 {kb_id} 不存在"}), 404
        audit = auditor.audit_entry(entry)
        return jsonify({"ok": True, "audit": audit})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e), "trace": traceback.format_exc()}), 500

@app.route("/api/kb/summary")
def api_kb_summary():
    """知识库总览"""
    try:
        agents = get_agents()
        kb = agents["kb"]
        summary = kb.summary()
        return jsonify({"ok": True, "summary": summary})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route("/api/kb/entries")
def api_kb_entries():
    """知识库条目列表（分页）"""
    try:
        agents = get_agents()
        kb = agents["kb"]
        category = request.args.get("category", "knowledge")  # knowledge | translation | punctuation
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 10))

        if category == "knowledge":
            entries = [kb.get_entry(k) for k in kb.kb_ids if k.startswith("KB_CAFA_S")]
        elif category == "translation":
            entries = [kb.get_entry(k) for k in kb.kb_ids if k.startswith("KB_CAFA_T")]
        elif category == "punctuation":
            entries = kb.punctuation_texts
        else:
            entries = []

        total = len(entries)
        start = (page - 1) * limit
        page_entries = entries[start:start + limit]

        return jsonify({
            "ok": True,
            "entries": page_entries,
            "total": total,
            "page": page,
            "limit": limit,
        })
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route("/api/batch_questions", methods=["POST"])
def api_batch_questions():
    """批量预生成题目（GUI 预加载用）"""
    try:
        agents = get_agents()
        coach = agents["coach"]
        kb = agents["kb"]
        body = request.get_json() or {}
        count = min(int(body.get("count", 5)), 20)
        pack_id = body.get("pack_id", "cafa_calligraphy_2026")

        questions = []
        # 随机抽取知识点
        kb_ids = [k for k in kb._kb_entries.keys() if k.startswith("KB_CAFA_S")]
        import random
        for _ in range(count):
            focus_kb_id = random.choice(kb_ids) if kb_ids else None
            scaffold = random.choice(["Lv1", "Lv2", "Lv3"])
            q = coach.generate_question(
                focus_kb_id=focus_kb_id,
                difficulty=scaffold,
                pack_id=pack_id
            )
            if "error" not in q:
                questions.append(q)

        return jsonify({"ok": True, "questions": questions})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e), "trace": traceback.format_exc()}), 500


@app.route("/api/reset", methods=["POST"])
def api_reset():
    """重置用户状态"""
    try:
        from agent_conductor.agent_conductor import UserState
        agents = get_agents()
        agents["state"] = UserState(
            user_id="gui_user",
            S_score=50.0,
            C_cognitive_load=3.0,
            F_fatigue=0.3,
            I_interest=6.0,
            pack_id="cafa_calligraphy_2026"
        )
        return jsonify({"ok": True, "user_state": agents["state"].summary()})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

# ─── 知识库看板 API ─────────────────────────────────────────────────────────

@app.route("/api/kb/all")
def api_kb_all():
    """返回所有知识条目（按分类组织，供看板使用）"""
    try:
        kb = get_agents()["kb"]

        categories = []

        # ── 分类1：书法史·名词解释（KB_CAFA_S*）────────────────────────────
        s_entries = [(k, v) for k, v in kb._kb_entries.items() if k.startswith("KB_CAFA_S")]
        # 按标签中的"模块"排序
        dynasty_order = ["先秦","秦汉","魏晋","隋唐","宋代","元代","明代","清代","书法理论"]
        def dynasty_sort(item):
            _, v = item
            for i, d in enumerate(dynasty_order):
                for tag in (v.tags or []):
                    if d in tag:
                        return i
            return 999
        s_entries.sort(key=dynasty_sort)

        def _render_tips(tips):
            """将 exam_tips 字典渲染为格式化字符串"""
            if not tips:
                return ""
            if isinstance(tips, str):
                return "\n".join(f"• {l.strip()}" for l in tips.split("\n") if l.strip())
            if not isinstance(tips, dict):
                return ""
            parts = []
            # 得分要点
            sp = tips.get("scoring_points", [])
            if sp:
                items = sp if isinstance(sp, list) else [sp]
                parts.append("【得分要点】\n• " + "\n• ".join(items))
            # 常见失分
            cm = tips.get("common_mistakes", [])
            if cm:
                items = cm if isinstance(cm, list) else [cm]
                parts.append("【常见失分】\n• " + "\n• ".join(items))
            # 记忆口诀（兼容中文/英文 key）
            mn_keys = ["mnemonics", "memory_tips", "记忆口诀", "记忆口诀"]
            for k in mn_keys:
                if tips.get(k):
                    items = tips[k] if isinstance(tips[k], list) else [tips[k]]
                    parts.append("【记忆口诀】\n• " + "\n• ".join(items))
                    break
            # 延伸考点（兼容中文/英文 key）
            ext_keys = ["extended_topics", "延伸考点", "延伸考点"]
            for k in ext_keys:
                if tips.get(k):
                    items = tips[k] if isinstance(tips[k], list) else [tips[k]]
                    parts.append("【延伸考点】\n• " + "\n• ".join(items))
                    break
            return "\n\n".join(parts)

        def s_entry_to_algo(kb_id, entry):
            sc = entry.structured_content or {}
            tabs = {}

            # ── Tab1: 知识简介 ───────────────────────────────────────────────
            # definition + historical_period 合并为系统性的完整介绍
            intro_lines = []
            if entry.definition:
                intro_lines.append(entry.definition)
            if sc.get("historical_period"):
                intro_lines.append("\n" + sc["historical_period"])
            # structured_content 里其他核心字段也纳入简介
            for key in ["定性", "核心贡献", "本义", "部首", "字体基准", "部首体系",
                         "核心理论", "艺术特征", "学书阶段", "基本信息"]:
                if sc.get(key):
                    intro_lines.append(f"\n{key}：{sc[key]}")
            if intro_lines:
                tabs["1-知识简介"] = "".join(intro_lines).strip()

            # ── Tab2: 典型试题 ────────────────────────────────────────────
            # example_questions 字段 + answer_template（作为标准答题示范）
            eq_lines = []
            for q in (entry.example_questions or []):
                eq_lines.append(f"• {q}")
            if entry.answer_template:
                eq_lines.append("\n【标准答题示范】\n" + entry.answer_template.strip())
            if eq_lines:
                tabs["2-典型试题"] = "\n".join(eq_lines).strip()

            # ── Tab3: 应试技巧 ────────────────────────────────────────────
            tips_str = _render_tips(entry.exam_tips)
            if tips_str:
                tabs["3-应试技巧"] = tips_str

            # ── Tab4: 背景延伸 ───────────────────────────────────────────
            # background + cross_pack_links 合并
            bg_parts = []
            bg = sc.get("background", "")
            if bg and not str(bg).startswith("LLMResponse") and len(str(bg)) > 20:
                bg_parts.append(bg.strip())
            if entry.cross_pack_links:
                links = []
                for l in entry.cross_pack_links:
                    title = l.get("title", "")
                    note = l.get("note", "")
                    kb = l.get("kb_id", "")
                    link_str = f"→ {title}"
                    if note:
                        link_str += f"\n  注：{note}"
                    if kb:
                        link_str += f" [{kb}]"
                    links.append(link_str)
                if links:
                    bg_parts.append("【相关知识点】\n" + "\n\n".join(links))
            if bg_parts:
                tabs["4-背景延伸"] = "\n\n".join(bg_parts).strip()

            # 标签：考频、考点类型
            freq_tag = next((t for t in (entry.tags or []) if "考频" in t), "")
            type_tag = next((t for t in (entry.tags or []) if "考点类型" in t), "")
            tags = [t for t in (entry.tags or []) if t.startswith("#")]
            tags = [freq_tag, type_tag] + [t for t in tags if t != freq_tag and t != type_tag]

            return {
                "id": kb_id,
                "name": entry.concept,
                "tags": tags,
                "tabs": tabs,
                "definition": entry.definition,
                "exam_tips": entry.exam_tips,
            }

        # 分成朝代子分类
        dynasty_groups = {}
        for kb_id, entry in s_entries:
            dynasty = "其他"
            for d in dynasty_order:
                if any(d in tag for tag in (entry.tags or [])):
                    dynasty = d
                    break
            dynasty_groups.setdefault(dynasty, []).append((kb_id, entry))

        calligraphy_cats = []
        for d in dynasty_order + ["其他"]:
            items = dynasty_groups.get(d, [])
            if not items:
                continue
            algos = [s_entry_to_algo(k, v) for k, v in items]
            calligraphy_cats.append({
                "dynasty": d,
                "count": len(algos),
                "algos": algos
            })

        categories.append({
            "name": "书法史·名词解释",
            "count": len(s_entries),
            "sub_cats": calligraphy_cats
        })

        # ── 分类2：译篆对照（KB_CAFA_T*）──────────────────────────────────
        t_entries = [(k, v) for k, v in kb._translation_entries.items()]
        def t_entry_to_algo(kb_id, entry):
            tabs = {}
            if entry.definition:
                tabs["1-释义"] = entry.definition
            if entry.tags:
                tabs["3-字形解析"] = "\n".join(entry.tags)
            return {
                "id": kb_id,
                "name": entry.concept,
                "tags": [t for t in (entry.tags or [])],
                "tabs": tabs,
                "definition": entry.definition,
                "exam_tips": entry.exam_tips,
            }
        categories.append({
            "name": "译篆对照",
            "count": len(t_entries),
            "algos": [t_entry_to_algo(k, v) for k, v in t_entries[:50]]  # 限制50条防过大
        })

        # ── 分类3：句读速查 ──────────────────────────────────────────────
        # 从 kb_punct_ref.json 加载句读标志词速查表
        _punct_ref_path = PT_ROOT / "_03_subject_packs" / "cafa_calligraphy_2026" / "knowledge" / "kb_punct_ref.json"
        if not _punct_ref_path.exists():
            _punct_ref_path = PT_ROOT / "_03_subject_packs" / "cafa_calligraphy_2026" / "kb_punct_ref.json"
        punct_ref_data = []
        if _punct_ref_path.exists():
            try:
                punct_ref_data = json.loads(_punct_ref_path.read_text(encoding="utf-8"))
            except Exception:
                pass

        def _render_punct_ref_section(section):
            """将句读速查的每个部分渲染为格式化字符串"""
            parts = []
            if section.get("section_type") == "head_markers" or section.get("section_type") == "tail_markers":
                for sub in (section.get("subsections") or []):
                    sub_title = sub.get("subsection_title", "")
                    sub_desc = sub.get("description", "")
                    markers = sub.get("markers", [])
                    examples = sub.get("examples", [])

                    lines = [f"【{sub_title}】"]
                    if sub_desc:
                        lines.append(sub_desc)
                    if markers:
                        lines.append("")
                        for m in markers:
                            word = m.get("word", "")
                            func = m.get("function", "")
                            note = m.get("note", "")
                            note_str = f"（{note}）" if note else ""
                            lines.append(f"  ▸ {word} → {func}{note_str}")
                    if examples:
                        lines.append("")
                        lines.append("  例：")
                        for ex in examples:
                            raw = ex.get("raw", "")
                            punct = ex.get("punct", "")
                            explain = ex.get("explain", "")
                            lines.append(f"    原文：{raw}")
                            lines.append(f"    断句：{punct}")
                            if explain:
                                lines.append(f"    要点：{explain}")
                    parts.append("\n".join(lines))

            elif section.get("section_type") == "fixed_structures":
                structures = section.get("structures", [])
                for s in structures:
                    st = s.get("structure", "")
                    brk = s.get("break_position", "")
                    mean = s.get("meaning", "")
                    ex_raw = s.get("example_raw", "")
                    ex_punct = s.get("example_punct", "")
                    note = s.get("exam_note", "")
                    parts.append(
                        f"【{st}】\n"
                        f"  断点：{brk}  含义：{mean}\n"
                        f"  原文：{ex_raw}\n"
                        f"  断句：{ex_punct}\n"
                        f"  要点：{note}"
                    )

            elif section.get("section_type") == "special_techniques":
                for t in (section.get("techniques") or []):
                    title = t.get("technique_title", "")
                    desc = t.get("description", "")
                    raw = t.get("example_raw", "")
                    punct = t.get("example_punct", "")
                    steps = t.get("step_by_step", [])
                    note = t.get("exam_note", "")
                    lines = [f"【{title}】"]
                    if desc:
                        lines.append(desc)
                    lines.append(f"\n  原文：{raw}")
                    lines.append(f"  断句：{punct}")
                    if steps:
                        lines.append("  步骤：")
                        for i, step in enumerate(steps, 1):
                            lines.append(f"    {i}. {step}")
                    if note:
                        lines.append(f"\n  考场提示：{note}")
                    parts.append("\n".join(lines))

            elif section.get("section_type") == "exam_traps":
                for trap in (section.get("traps") or []):
                    title = trap.get("trap_title", "")
                    wrong = trap.get("wrong_case", "")
                    right = trap.get("right_case", "")
                    rule = trap.get("rule", "")
                    lines = [f"【{title}】"]
                    if wrong:
                        lines.append(f"  ✗ 错误：{wrong}")
                    if right:
                        lines.append(f"  ✓ 正确：{right}")
                    if rule:
                        lines.append(f"\n  规律：{rule}")
                    parts.append("\n".join(lines))

            elif section.get("practice"):
                p = section["practice"]
                steps = p.get("steps", [])
                answer = p.get("answer", "")
                translation = p.get("translation", "")
                lines = [f"【{p.get('title', '实战演练')}】"]
                lines.append(f"\n  原文（无标点）：\n  {p.get('raw', '')}")
                if steps:
                    lines.append("\n  拆解步骤：")
                    for s in steps:
                        lines.append(f"    {s['step']}. {s['action']}：{s['findings']}")
                        if s.get("draft"):
                            lines.append(f"       → {s['draft']}")
                lines.append(f"\n  【参考答案】\n  {answer}")
                if translation:
                    lines.append(f"\n  【参考译文】\n  {translation}")
                parts.append("\n".join(lines))

            return "\n\n".join(parts)

        def punct_ref_to_algo(item):
            kb_id = item.get("ref_id", "")
            title = item.get("title", "")
            intro = item.get("intro", "")
            sections = item.get("sections") or []
            section_type = item.get("section_type", "")
            tabs = {}

            # 第一Tab：总览/介绍
            if intro and item.get("ref_id") == "PunctRef_001":
                tabs["1-使用说明"] = intro
            elif intro:
                tabs["1-本节导学"] = intro

            # 如果有嵌套的 sections 数组（只有总览条），渲染每个 section
            for section in sections:
                section_title = section.get("title", "")
                if not section_title:
                    continue
                short = section_title.replace("一、", "").replace("二、", "").replace("三、", "").replace("四、", "").replace("五、", "").replace("六、", "")
                tab_key = f"Tab/{short[:6]}"
                rendered = _render_punct_ref_section(section)
                if rendered:
                    tabs[tab_key] = rendered

            # 如果有 practice 字段，单独作为"实战"Tab
            if item.get("practice"):
                tabs["实战/真题演练"] = _render_punct_ref_section(item)

            # 如果没有嵌套 sections 且有 section_type，说明内容直接在 item 上
            if not sections and section_type and not item.get("practice"):
                rendered = _render_punct_ref_section(item)
                short_title = title.replace("一、", "").replace("二、", "").replace("三、", "").replace("四、", "").replace("五、", "").replace("六、", "")
                short_title = short_title[:12]
                if rendered:
                    tabs[f"Tab/{short_title}"] = rendered

            return {
                "id": kb_id,
                "name": title,
                "tags": ["#考点类型/句读", "#古汉语", "#速查表"],
                "tabs": tabs,
                "raw_text": intro,
            }

        # 句读速查条目
        punct_ref_algos = [punct_ref_to_algo(item) for item in punct_ref_data]
        punct_ref_cat = {
            "name": "句读速查",
            "count": len(punct_ref_algos),
            "algos": punct_ref_algos,
            "is_punct_ref": True,
        }
        categories.append(punct_ref_cat)

        # ── 分类3b：句读范本（QT-*）────────────────────────────────────
        # 重命名：原来叫"句读练习"，现改为"句读范本"，供对照练习
        qt_entries = list(kb._punctuation_texts.values())
        def qt_to_algo(text):
            kb_id = text.text_id
            tabs = {}
            if text.raw_text:
                tabs["1-原文"] = text.raw_text
            if text.punctuated:
                tabs["2-标点后"] = text.punctuated
            if text.translation:
                tabs["3-译文"] = text.translation
            return {
                "id": kb_id,
                "name": text.source,
                "tags": [f"#考点类型/句读", f"#难度/{text.difficulty}"],
                "tabs": tabs,
                "raw_text": text.raw_text,
                "punctuated": text.punctuated,
                "translation": text.translation,
            }
        categories.append({
            "name": "句读范本",
            "count": len(qt_entries),
            "algos": [qt_to_algo(v) for v in qt_entries]
        })

        # ── 分类4：错题剧本（ES-*）────────────────────────────────────────
        import re as _re
        es_entries = list(kb._error_scripts.values())
        def es_to_algo(s):
            tabs = {}
            q = s.question or {}
            q_text = q.get("text", "")
            q_correct = q.get("correct_answer", "")
            q_wrong = q.get("wrong_answer_sample", "")

            # ── Tab1: 错因分析（knowledge_gap 核心句，一句话讲清错在哪）──
            # 三要素（题目/误答/正答）已在置顶区展示，此Tab聚焦"为什么错"
            kg = s.script.get("knowledge_gap", "").strip()
            if kg:
                # 取 knowledge_gap 第一句作为精炼的错因（避免过长）
                kg_first = kg.split("\n")[0].split("。")[0].strip()
                tabs["1-错因分析"] = kg_first
                # 如果还有后续内容，追加到 Tab2
                rest = kg[len(kg_first):].strip()
                if rest:
                    kg = kg_first + "\n\n" + rest
                else:
                    kg = kg_first

            # ── Tab2: 深度解析（explanation + resolution）──────────────────
            tab2_parts = []
            if kg and len(kg.split("\n")) > 1:
                # knowledge_gap 有多行，第二段开始视为延伸，放入Tab2
                lines = kg.split("\n")
                tab2_parts.append("\n".join(lines[1:]).strip())
            if s.script.get("explanation"):
                tab2_parts.append(s.script["explanation"].strip())
            if s.script.get("resolution"):
                tab2_parts.append(f"【考场对策】\n{s.script['resolution'].strip()}")
            if tab2_parts:
                tabs["2-深度解析"] = "\n\n".join(tab2_parts).strip()

            # ── Tab3: 记忆口诀 ────────────────────────────────────────────
            if s.script.get("mnemonic"):
                tabs["3-记忆口诀"] = s.script["mnemonic"].strip()

            # ── 侧边栏条目名：KB编号 + 精炼核心词（≤12字）────────────────
            kb_id_short = s.trigger_kb_id \
                .replace("KB_CAFA_T", "T") \
                .replace("KB_CAFA_S", "S") \
                .replace("KB_CAFA_Q", "Q")

            def _extract_key(qc, kg_val, exp_val, et_val):
                """从答案/解析中智能提取侧边栏核心词（≤12字）"""
                # 优先级1：译篆题 → 用「XX」（多字时），单字无引号
                if "译篆" in et_val and qc:
                    m = _re.search(r"「([^」]+)」", qc)
                    if m:
                        chars = m.group(1)
                        return ("「" + chars + "」") if len(chars) > 1 else chars
                    # 无「」时，找第一个词（忽略句首括号内容，含半角/全角）
                    stripped = qc.strip()
                    # 跳过"（XX）"或"(XX)"前缀
                    for open_p, close_p in [("（", "）"), ("(", ")")]:
                        if stripped.startswith(open_p) and close_p in stripped:
                            after = stripped.split(close_p, 1)
                            if len(after) > 1 and after[1].strip():
                                stripped = after[1].strip()
                            break
                    if len(stripped) >= 2:
                        return stripped[:4]  # 取前2-4字（多字词优先）
                    return stripped[:1] if stripped else "?"
                # 优先级2：q_correct 中提取【】标签（截断12字）
                if qc:
                    m = _re.search(r"【([^】]+)】", qc)
                    if m:
                        raw = m.group(1)[:12]
                        return raw
                    # 按逗号/顿号/句号断句，取第一段（上限12字）
                    punct = next((c for c in "，、。" if c in qc), None)
                    if punct:
                        key = qc.split(punct)[0].strip()
                        return key[:12] if len(key) > 12 else key
                    # 无标点时直接截取前12字
                    key = qc.strip()[:12]
                    if len(key) >= 3:
                        return key
                # 优先级3：knowledge_gap 提「XX」或首段完整词
                if kg_val:
                    first_sent = kg_val.strip().split("\n")[0].split("。")[0]
                    # 提「XX」
                    m = _re.search(r"「([^」]{2,10}?)」", first_sent)
                    if m:
                        chars = m.group(1)
                        return ("「" + chars + "」") if len(chars) > 1 else chars
                    # "XX：XX" 冒号后内容
                    parts = first_sent.split("：")
                    if len(parts) > 1:
                        key = parts[1].split("，")[0].split("（")[0].strip()
                        if 2 <= len(key) <= 12:
                            return key
                    # 第一个逗号/顿号/句号之前（上限12字）
                    punct = next((c for c in "，、。" if c in first_sent), None)
                    if punct:
                        key = first_sent.split(punct)[0].strip()
                        if 3 <= len(key) <= 12:
                            return key
                        elif len(key) > 12:
                            return key[:12]
                    key = first_sent[:12].strip()
                    if len(key) >= 3:
                        return key
                # 优先级4：explanation（前12字）
                if exp_val:
                    first = exp_val.strip()[:50]
                    punct = next((c for c in "，、：" if c in first), None)
                    if punct:
                        key = first.split(punct)[0].strip()
                        if 3 <= len(key) <= 12:
                            return key
                    key = first[:12].strip()
                    if len(key) >= 3:
                        return key
                # 兜底：error_type 末段（限8字）
                et_parts = et_val.split("_")
                return (et_parts[-1] if et_parts else et_val)[:8]

            raw_key = _extract_key(q_correct, kg, s.script.get("explanation", ""), s.error_type)
            # 最终截断到12字（找标点断点，或直接截）
            if len(raw_key) > 12:
                truncated = raw_key[:12]
                punct_positions = [truncated.rfind(c) for c in "，、。："]
                punct_pos = max(punct_positions) if punct_positions else -1
                if punct_pos > 3:
                    raw_key = truncated[:punct_pos].strip()
                else:
                    raw_key = truncated
            sidebar_name = "%s · %s" % (kb_id_short, raw_key)

            return {
                "id": s.script_id,
                "name": sidebar_name,
                "tags": [f"#考点/{s.question_type}", f"#难度/{s.difficulty}", f"#易错/{s.error_type}"],
                "tabs": tabs,
                "question_text": q_text,
                "correct_answer": q_correct,
                "wrong_answer": q_wrong,
                "knowledge_gap": s.script.get("knowledge_gap", ""),
            }
        categories.append({
            "name": "错题剧本",
            "count": len(es_entries),
            "algos": [es_to_algo(v) for v in es_entries]
        })

        return jsonify({
            "ok": True,
            "categories": categories,
            "total_kb": len(s_entries),
            "total_t": len(t_entries),
            "total_punct_ref": len(punct_ref_data),
            "total_qt": len(qt_entries),
            "total_es": len(es_entries),
        })
    except Exception as e:
        return jsonify({"ok": False, "error": str(e), "trace": traceback.format_exc()}), 500


@app.route("/api/kb/entry/<entry_id>")
def api_kb_entry(entry_id):
    """返回单个知识条目详情"""
    try:
        kb = get_agents()["kb"]
        entry = kb.get_entry(entry_id)
        if entry:
            return jsonify({
                "ok": True,
                "entry": {
                    "kb_id": entry.kb_id,
                    "concept": entry.concept,
                    "definition": entry.definition,
                    "tags": entry.tags,
                    "exam_tips": entry.exam_tips,
                    "structured_content": entry.structured_content,
                    "cross_pack_links": entry.cross_pack_links,
                    "answer_template": entry.answer_template,
                }
            })
        # 尝试punctuation
        pt = kb._punctuation_texts.get(entry_id)
        if pt:
            return jsonify({
                "ok": True,
                "entry": {
                    "kb_id": pt.text_id,
                    "concept": pt.source,
                    "definition": pt.raw_text,
                    "tags": pt.tags,
                    "raw_text": pt.raw_text,
                    "punctuated": pt.punctuated,
                    "translation": pt.translation,
                }
            })
        return jsonify({"ok": False, "error": f"未找到 {entry_id}"}), 404
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


# ─── 启动 ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n╔═══════════════════════════════════════════╗")
    print("║   PT-037 智能体平台 — API Server          ║")
    print("║   访问 http://localhost:5188              ║")
    print("╚═══════════════════════════════════════════╝\n")
    app.run(host="0.0.0.0", port=5188, debug=False, threaded=True)
