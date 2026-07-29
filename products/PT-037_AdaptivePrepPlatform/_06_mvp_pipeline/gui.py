# -*- coding: utf-8 -*-
"""
PT-037 自适应备考智能体平台 — Tkinter GUI
直接运行: python gui.py
"""

import json
import sys
import os
import threading
import tkinter as tk
from tkinter import scrolledtext, ttk, messagebox
from pathlib import Path

# ─── 项目路径 ───────────────────────────────────────────────────────────────
PT_ROOT = Path(__file__).parent.parent
CORE = PT_ROOT / "_01_platform_core"
sys.path.insert(0, str(CORE))

from llm.llm_wrapper import create_llm_client
from knowledge_base.knowledge_base import KnowledgeBase
from agent_conductor.agent_conductor import AgentConductor, UserState
from agent_coach.agent_coach import AgentCoach
from agent_auditor.agent_auditor import AgentAuditor


# ─── 颜色 ───────────────────────────────────────────────────────────────────
C_STEP_BG    = "#1a1a2e"
C_TITLE_BG   = "#16213e"
C_ACCENT     = "#e94560"
C_GREEN      = "#4ecca3"
C_YELLOW     = "#f9ed69"
C_BLUE       = "#00b4d8"
C_TEXT       = "#e0e0e0"
C_MUTED      = "#7f8c8d"
C_PANEL_BG   = "#0f0f23"
C_ENTRY_BG  = "#1b1b3a"
C_BTN_RUN    = "#e94560"
C_BTN_ANS    = "#00b4d8"


class PT037GUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PT-037 自适应备考智能体平台")
        self.geometry("1100x780")
        self.minsize(900, 680)
        self.configure(bg=C_PANEL_BG)
        self._running = False

        # 加载 API key
        self._load_api_key()

        # 状态
        self.llm_mode = "glm" if os.environ.get("ZHIPU_API_KEY") else "mock"
        self.kb = None
        self.llm = None
        self.conductor = None
        self.coach = None
        self.auditor = None
        self.user_state = None
        self.current_q = None
        self.current_decision = None

        self._build_ui()
        self._init_components(write_log=False)

    # ── 布局 ──────────────────────────────────────────────────────────────

    def _build_ui(self):
        # ── 标题栏 ──
        hdr = tk.Frame(self, bg=C_TITLE_BG, height=60)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)

        tk.Label(hdr, text="PT-037 自适应备考智能体平台",
                 font=("Microsoft YaHei UI", 16, "bold"),
                 fg=self._hex(C_ACCENT), bg=C_TITLE_BG).pack(side="left", padx=20, pady=12)

        # LLM 模式标签
        self._mode_lbl = tk.Label(hdr, text=f"LLM: {self.llm_mode.upper()}",
                                  font=("Microsoft YaHei UI", 9),
                                  fg=C_GREEN, bg=C_TITLE_BG)
        self._mode_lbl.pack(side="right", padx=20, pady=12)

        # ── 主框架 (左右分栏) ──
        main = tk.Frame(self, bg=C_PANEL_BG)
        main.pack(fill="both", expand=True)

        # 左：控制面板
        left = tk.Frame(main, bg=C_ENTRY_BG, width=280)
        left.pack(side="left", fill="y", padx=(8, 4), pady=8)
        left.pack_propagate(False)

        self._build_left_panel(left)

        # 右：日志输出
        right = tk.Frame(main, bg=C_PANEL_BG)
        right.pack(side="right", fill="both", expand=True, padx=(4, 8), pady=8)

        self._build_right_panel(right)

    def _build_left_panel(self, parent):
        # 用户状态
        tk.Label(parent, text="📊 用户状态",
                 font=("Microsoft YaHei UI", 11, "bold"),
                 fg=self._hex(C_BLUE), bg=C_ENTRY_BG).pack(anchor="w", padx=15, pady=(12, 4))

        self._state_labels = {}
        state_keys = [
            ("S_score",        "掌握度 S",     "50.0%"),
            ("C_cognitive_load","认知负荷 C",   "3.0"),
            ("F_fatigue",       "疲劳度 F",     "0.3"),
            ("I_interest",      "兴趣度 I",     "6.0"),
        ]
        for key, label, default in state_keys:
            row = tk.Frame(parent, bg=C_ENTRY_BG)
            row.pack(fill="x", padx=15, pady=2)
            tk.Label(row, text=label, font=("Microsoft YaHei UI", 9),
                     fg=C_TEXT, bg=C_ENTRY_BG, width=12, anchor="w").pack(side="left")
            val_lbl = tk.Label(row, text=default,
                               font=("Consolas", 9), fg=C_GREEN, bg=C_ENTRY_BG)
            val_lbl.pack(side="right")
            self._state_labels[key] = val_lbl

        sep = tk.Frame(parent, bg=C_MUTED, height=1)
        sep.pack(fill="x", padx=15, pady=10)

        # 决策结果
        tk.Label(parent, text="🎯 Agent5 决策",
                 font=("Microsoft YaHei UI", 11, "bold"),
                 fg=self._hex(C_ACCENT), bg=C_ENTRY_BG).pack(anchor="w", padx=15, pady=(0, 4))

        self._decision_lbl = tk.Label(parent, text="—",
                                      font=("Microsoft YaHei UI", 9),
                                      fg=C_TEXT, bg=C_ENTRY_BG, wraplength=240,
                                      justify="left", anchor="w")
        self._decision_lbl.pack(anchor="w", padx=15, pady=2)

        sep2 = tk.Frame(parent, bg=C_MUTED, height=1)
        sep2.pack(fill="x", padx=15, pady=10)

        # 题目卡片
        tk.Label(parent, text="📝 当前题目",
                 font=("Microsoft YaHei UI", 11, "bold"),
                 fg=self._hex(C_YELLOW), bg=C_ENTRY_BG).pack(anchor="w", padx=15, pady=(0, 4))

        self._q_type_lbl = tk.Label(parent, text="—",
                                     font=("Microsoft YaHei UI", 9, "italic"),
                                     fg=C_MUTED, bg=C_ENTRY_BG)
        self._q_type_lbl.pack(anchor="w", padx=15, pady=2)

        self._q_text_lbl = tk.Label(parent, text="—",
                                     font=("Microsoft YaHei UI", 9),
                                     fg=C_TEXT, bg=C_ENTRY_BG, wraplength=250,
                                     justify="left", anchor="w")
        self._q_text_lbl.pack(anchor="w", padx=15, pady=2)

        sep3 = tk.Frame(parent, bg=C_MUTED, height=1)
        sep3.pack(fill="x", padx=15, pady=10)

        # 评分结果
        tk.Label(parent, text="✅ 评分 & 审计",
                 font=("Microsoft YaHei UI", 11, "bold"),
                 fg=self._hex(C_GREEN), bg=C_ENTRY_BG).pack(anchor="w", padx=15, pady=(0, 4))

        self._grade_lbl = tk.Label(parent, text="—",
                                    font=("Microsoft YaHei UI", 9),
                                    fg=C_TEXT, bg=C_ENTRY_BG, wraplength=250,
                                    justify="left", anchor="w")
        self._grade_lbl.pack(anchor="w", padx=15, pady=2)

        self._audit_lbl = tk.Label(parent, text="—",
                                    font=("Microsoft YaHei UI", 9),
                                    fg=C_TEXT, bg=C_ENTRY_BG, wraplength=250,
                                    justify="left", anchor="w")
        self._audit_lbl.pack(anchor="w", padx=15, pady=2)

        # 按钮
        sep4 = tk.Frame(parent, bg=C_MUTED, height=1)
        sep4.pack(fill="x", padx=15, pady=10)

        self._btn_run = tk.Button(parent, text="▶ 一键运行全流程",
                                   font=("Microsoft YaHei UI", 10, "bold"),
                                   fg="white", bg=C_ACCENT, relief="flat",
                                   cursor="hand2", command=self._run_full)
        self._btn_run.pack(fill="x", padx=15, pady=4)

        self._btn_answer = tk.Button(parent, text="📋 填入答案（演示）",
                                     font=("Microsoft YaHei UI", 10),
                                     fg="white", bg=C_BLUE, relief="flat",
                                     cursor="hand2", command=self._fill_demo_answer,
                                     state="disabled")
        self._btn_answer.pack(fill="x", padx=15, pady=4)

        self._btn_next = tk.Button(parent, text="🔄 下一轮",
                                    font=("Microsoft YaHei UI", 10),
                                    fg="white", bg="#2d6a4f", relief="flat",
                                    cursor="hand2", command=self._run_full,
                                    state="disabled")
        self._btn_next.pack(fill="x", padx=15, pady=4)

        # 进度指示
        self._progress = ttk.Progressbar(parent, mode="indeterminate")
        self._progress.pack(fill="x", padx=15, pady=(8, 0))

    def _build_right_panel(self, parent):
        # 工具栏
        toolbar = tk.Frame(parent, bg=C_ENTRY_BG)
        toolbar.pack(fill="x", pady=(0, 6))

        tk.Label(toolbar, text="📋 执行日志",
                  font=("Microsoft YaHei UI", 11, "bold"),
                  fg=self._hex(C_BLUE), bg=C_ENTRY_BG).pack(side="left", padx=10, pady=6)

        tk.Button(toolbar, text="🗑 清空",
                  font=("Microsoft YaHei UI", 9),
                  fg=C_TEXT, bg=C_ENTRY_BG, relief="flat",
                  cursor="hand2", command=lambda: self._log_area.delete("1.0", "end")
                  ).pack(side="right", padx=10, pady=6)

        # 日志文本框
        self._log_area = scrolledtext.ScrolledText(
            parent,
            bg=C_STEP_BG,
            fg=C_TEXT,
            font=("Consolas", 9),
            insertbackground=C_ACCENT,
            relief="flat",
            wrap="word",
            padx=10,
            pady=10,
            highlightthickness=0,
        )
        self._log_area.pack(fill="both", expand=True)
        self._log_area.tag_configure("h", foreground=self._hex(C_ACCENT), font=("Consolas", 9, "bold"))
        self._log_area.tag_configure("s", foreground=self._hex(C_BLUE), font=("Consolas", 9, "bold"))
        self._log_area.tag_configure("g", foreground=self._hex(C_GREEN))
        self._log_area.tag_configure("y", foreground=self._hex(C_YELLOW))
        self._log_area.tag_configure("m", foreground=C_MUTED)
        self._log_area.tag_configure("err", foreground="#e74c3c")
        self._log_area.tag_configure("q", foreground=self._hex(C_YELLOW), font=("Consolas", 9, "bold"))
        self._log_area.tag_configure("title", foreground=self._hex(C_ACCENT), font=("Consolas", 10, "bold"))

    # ── 核心逻辑 ───────────────────────────────────────────────────────────

    def _load_api_key(self):
        if not os.environ.get("ZHIPU_API_KEY"):
            p = Path("D:/_CEO/bulletin/SECRET_KEY/zhipu_api.txt")
            if p.exists():
                os.environ["ZHIPU_API_KEY"] = p.read_text(encoding="utf-8").strip()

    def _init_components(self, write_log=True):
        if write_log:
            self._log("h", "\n═══ 初始化组件 ═══\n")

        try:
            pack_path = PT_ROOT / "_03_subject_packs" / "cafa_calligraphy_2026"
            self.llm = create_llm_client(mode=self.llm_mode)
            self.kb = KnowledgeBase.from_pack(pack_path)
            self.conductor = AgentConductor(self.llm, self.kb)
            self.coach = AgentCoach(self.llm, self.kb)
            self.auditor = AgentAuditor(self.llm, self.kb)

            summary = self.kb.summary()
            init_msg = (f"✓ 知识库：{summary['total_kb_entries']}条书法史 / "
                        f"{summary['total_translation_entries']}组译篆 / "
                        f"{summary['total_punctuation_texts']}篇句读 / "
                        f"{summary['total_error_scripts']}条错题剧本")
            if write_log:
                self._log("g", init_msg + "\n")
        except Exception as e:
            if write_log:
                self._log("err", f"初始化失败: {e}\n")
            raise

    def _run_full(self):
        if self._running:
            return
        self._running = True
        self._btn_run.config(state="disabled", text="⏳ 运行中…")
        self._progress.start(8)
        threading(target=self._run_full_bg, daemon=True).start()

    def _run_full_bg(self):
        try:
            self._log("title", "\n\n══════════════════════════════════════\n")
            self._log("title", "  PT-037 自适应备考智能体平台 — MVP 演示\n")
            self._log("title", "══════════════════════════════════════\n\n")

            # Step 1 — 用户状态
            self._log("s", "  Step 1  初始化用户状态\n")
            self.user_state = UserState(
                user_id="gui_001",
                S_score=50.0,
                C_cognitive_load=3.0,
                F_fatigue=0.3,
                I_interest=6.0,
                pack_id="cafa_calligraphy_2026"
            )
            self._update_state_ui()
            self._log("m", "       S=50% | C=3.0 | F=0.3 | I=6.0\n")

            # Step 2 — Agent5 调度
            self._log("s", "\n  Step 2  Agent5 调度决策\n")
            self.current_decision = self.conductor.decide(self.user_state)
            d = self.current_decision
            self._log("g", f"    → 行动类型: {d.action_type}\n")
            self._log("g", f"    → 目标Agent: {d.target_agent}  优先级: {d.priority}\n")
            self._log("m", f"    → 推理: {d.reasoning}\n")
            self._log("m", f"    → 难度: {d.scaffold_level}\n")
            if d.content_spec.get("focus_kb_id"):
                self._log("y", f"    → 知识点: {d.content_spec['focus_kb_id']} "
                            f"({d.content_spec.get('focus_concept','')})\n")
            self._update_decision_ui(d)

            # Step 3 — Agent4 出题
            self._log("s", "\n  Step 3  Agent4 生成训练题\n")
            self.current_q = self.coach.generate_question(
                focus_kb_id=d.content_spec.get("focus_kb_id"),
                difficulty=d.scaffold_level,
                pack_id=self.user_state.pack_id
            )
            if "error" not in self.current_q:
                self._log("g", f"    ✓ 题型: {self.current_q.get('question_type')}  "
                            f"难度: {self.current_q.get('difficulty')}\n")
                q_text = self.current_q.get("text", "")
                self._log("q", f"\n  【题目】{q_text}\n")
                if self.current_q.get("hints"):
                    self._log("m", f"\n  【提示】{' / '.join(self.current_q.get('hints', []))}\n")
                self._update_q_ui(self.current_q)
            else:
                self._log("err", f"    ✗ {self.current_q.get('error')}\n")

            # Step 4 — 演示答案（从题目 correct_answer 字段读取）
            self._log("s", "\n  Step 4  填入演示答案\n")
            raw = self.current_q.get("correct_answer", "")
            if self.current_q.get("answer") and isinstance(self.current_q["answer"], dict):
                raw = "\n".join(self.current_q["answer"].values())
            user_answer = str(raw)
            self._log("y", f"    答案: {user_answer[:80]}{'…' if len(user_answer)>80 else ''}\n")
            self._enable_answer_btn(user_answer)

            # Step 5 — Agent4 评分
            self._log("s", "\n  Step 5  Agent4 评分\n")
            grading = self.coach.grade_answer(
                self.current_q,
                user_answer,
                self.kb.get_entry(self.current_q.get("kb_id"))
            )
            status = "✓ 正确" if grading.get("correct") else "✗ 有误"
            status_tag = "g" if grading.get("correct") else "y"
            self._log(status_tag, f"    判定: {status}  得分: {grading.get('score',0)}"
                      f"/{grading.get('max_score',20)}\n")
            self._log("m", f"    反馈: {grading.get('feedback','')}\n")

            # Step 6 — 更新状态
            self._log("s", "\n  Step 6  更新用户状态\n")
            self.user_state.update_from_answer(
                grading.get("correct", False),
                self.current_q.get("ability_id", "A5")
            )
            self.user_state.tick(d.duration_minutes)
            self._update_state_ui()
            self._log("g", f"    新状态: S={self.user_state.S_score:.1f}% | "
                            f"C={self.user_state.C_cognitive_load:.1f} | "
                            f"F={self.user_state.F_fatigue:.1f} | "
                            f"I={self.user_state.I_interest:.1f}\n")

            # Step 7 — Agent2 审计
            self._log("s", "\n  Step 7  Agent2 知识审计\n")
            entry = self.kb.get_entry(d.content_spec.get("focus_kb_id", "KB_CAFA_S001"))
            if entry:
                audit = self.auditor.audit_entry(entry)
                v = audit["verdict"]
                v_color = "g" if v == "PASS" else ("y" if v == "NEED_REVISION" else "err")
                self._log(v_color, f"    审计: {v}  分数: {audit['score']}/{audit['max_score']}\n")
                for dim, res in audit.get("dimensions", {}).items():
                    icon = "✓" if "PASS" in res else "✗"
                    tag = "g" if "PASS" in res else "err"
                    self._log(tag, f"      {icon} {dim}: {res}\n")
                self._update_audit_ui(audit)

            # Step 8 — 错题剧本（如需）
            if not grading.get("correct") and d.content_spec.get("focus_kb_id"):
                self._log("s", "\n  Step 8  错题剧本\n")
                scripts = self.kb.get_error_script_by_kb(d.content_spec["focus_kb_id"])
                if scripts:
                    s = scripts[0]
                    self._log("err", f"    剧本: {s.script_id} | {s.error_type}\n")
                    self._log("err", f"    错误: {s.script.get('conflict','')}\n")
                    self._log("g", f"    正确: {s.script.get('logic_chain','')[:60]}\n")
                    self._log("y", f"    口诀: {s.script.get('mnemonic','')}\n")

            # 完成
            self._log("title", "\n══════════════════════════════════════\n")
            self._log("g", f"  ✅ MVP 完成 — S={self.user_state.S_score:.1f}% | "
                            f"C={self.user_state.C_cognitive_load:.1f} | "
                            f"F={self.user_state.F_fatigue:.1f} | "
                            f"I={self.user_state.I_interest:.1f}\n")
            self._log("title", "══════════════════════════════════════\n")

            self.after(0, lambda: self._btn_next.config(state="normal"))

        except Exception as e:
            import traceback
            self._log("err", f"\n运行时错误: {e}\n{traceback.format_exc()}\n")
        finally:
            self.after(0, self._done)

    def _done(self):
        self._running = False
        self._progress.stop()
        self._btn_run.config(state="normal", text="▶ 一键运行全流程")
        self._log_area.see("end")

    def _fill_demo_answer(self):
        # 演示模式下，填入答案后直接触发评分（GUI中实际已自动完成，这里做占位）
        self._log("m", "\n  [演示模式] 答案已自动填入，评分已在Step 5完成\n")

    # ── UI 更新 ───────────────────────────────────────────────────────────

    def _update_state_ui(self):
        if not self.user_state:
            return
        updates = {
            "S_score":        f"{self.user_state.S_score:.1f}%",
            "C_cognitive_load": str(self.user_state.C_cognitive_load),
            "F_fatigue":      f"{self.user_state.F_fatigue:.2f}",
            "I_interest":    str(self.user_state.I_interest),
        }
        for k, v in updates.items():
            self._state_labels[k].config(text=v)

    def _update_decision_ui(self, d):
        txt = (f"类型: {d.action_type}\n"
               f"目标: {d.target_agent}\n"
               f"优先级: {d.priority}\n"
               f"难度: {d.scaffold_level}")
        self._decision_lbl.config(text=txt)

    def _update_q_ui(self, q):
        self._q_type_lbl.config(
            text=f"{q.get('question_type', '?')} · {q.get('difficulty', '?')}")
        self._q_text_lbl.config(text=q.get("text", "—")[:120])

    def _update_audit_ui(self, audit):
        v = audit["verdict"]
        self._audit_lbl.config(
            text=f"审计: {v} | {audit['score']}/{audit['max_score']}")

    def _enable_answer_btn(self, answer):
        self._btn_answer.config(state="normal")

    # ── 工具 ───────────────────────────────────────────────────────────────

    def _log(self, tag, text):
        def _append():
            self._log_area.insert("end", text, tag)
            self._log_area.see("end")
        self.after(0, _append)

    @staticmethod
    def _hex(color_int_or_str):
        """处理整数值颜色（如 0xe94560）转为 '#rrggbb'"""
        c = color_int_or_str
        if isinstance(c, int):
            return f"#{c:06x}"
        return color_int_or_str


if __name__ == "__main__":
    app = PT037GUI()
    app.mainloop()
