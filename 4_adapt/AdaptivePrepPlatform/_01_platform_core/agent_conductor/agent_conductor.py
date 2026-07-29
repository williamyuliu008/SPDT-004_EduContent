"""
Agent 5: 全局调度与推荐 (Conductor)
PT-037 平台的大脑
"""

import json
from dataclasses import dataclass, field
from typing import Optional

from llm.llm_wrapper import LLMClient
from knowledge_base.knowledge_base import KnowledgeBase


@dataclass
class UserState:
    """用户四维状态"""
    user_id: str = "demo_user"
    S_score: float = 50.0        # 掌握度 0-100
    C_cognitive_load: float = 5.0 # 认知负荷 1-10
    F_fatigue: float = 0.0      # 疲劳值 0-∞
    I_interest: float = 5.0     # 兴趣指数 1-10
    pack_id: str = "cafa_calligraphy_2026"

    def update_from_answer(self, correct: bool, ability_id: str = "A5"):
        delta = 5.0 if correct else -8.0
        self.S_score = max(0.0, min(100.0, self.S_score + delta))
        self.I_interest = max(1.0, min(10.0, self.I_interest + (1.0 if correct else -1.5)))

    def tick(self, minutes: float = 1.0):
        self.F_fatigue = min(10.0, self.F_fatigue + minutes * 0.05)
        self.I_interest = max(1.0, self.I_interest - 0.02)
        if self.F_fatigue >= 3:
            self.C_cognitive_load = min(10.0, self.C_cognitive_load + 0.5)

    def is_tired(self) -> bool:
        return self.F_fatigue >= 3.0

    def is_overloaded(self) -> bool:
        return self.C_cognitive_load >= 8.0

    def summary(self) -> dict:
        status = "正常" if not self.is_tired() and not self.is_overloaded() \
                 else "疲劳" if self.is_tired() else "过载"
        return {
            "user_id": self.user_id,
            "S_score": round(self.S_score, 1),
            "C_cognitive_load": round(self.C_cognitive_load, 1),
            "F_fatigue": round(self.F_fatigue, 1),
            "I_interest": round(self.I_interest, 1),
            "status": status
        }


@dataclass
class ConductorDecision:
    action_type: str
    target_agent: str
    content_spec: dict = field(default_factory=dict)
    duration_minutes: int = 25
    priority: str = "P2"
    reasoning: str = ""
    scaffold_level: str = "Lv2"
    next_if_correct: str = ""
    next_if_wrong: str = ""


class AgentConductor:
    """Agent5 — 全局调度指挥官（规则驱动 MVP）"""

    def __init__(self, llm_client: LLMClient, knowledge_base: KnowledgeBase):
        self.llm = llm_client
        self.kb = knowledge_base

    def decide(self, state: UserState) -> ConductorDecision:
        # P1 熔断
        if state.is_overloaded() or state.is_tired():
            return ConductorDecision(
                action_type="agent3_micro_drama",
                target_agent="Agent3",
                content_spec={"type": "微剧本", "duration": "10分钟", "mode": "低功耗"},
                duration_minutes=10,
                priority="P1",
                reasoning=f"熔断：C={state.C_cognitive_load:.1f} F={state.F_fatigue:.1f}，切换低功耗",
                scaffold_level="Lv1"
            )

        # P2 核心优先
        top_entries = self.kb.get_top_starred_entries(min_stars=4)
        weak_entries = [e for e in top_entries if self._estimate_mastery(e, state) < 80]

        if weak_entries:
            entry = weak_entries[0]
            level = "Lv3" if state.C_cognitive_load <= 5 else "Lv2"
            return ConductorDecision(
                action_type="agent4_training",
                target_agent="Agent4",
                content_spec={
                    "type": f"{level}训练",
                    "focus_kb_id": entry.kb_id,
                    "focus_concept": entry.concept,
                    "pack_id": state.pack_id,
                    "ability_id": self._infer_ability_id(entry)
                },
                duration_minutes=25,
                priority="P2",
                reasoning=(
                    f"核心优先：{entry.concept}（⭐⭐⭐⭐⭐）"
                    f"掌握度≈{self._estimate_mastery(entry, state):.0f}%<80%，"
                    f"C={state.C_cognitive_load:.1f}→Lv{level[2]}"
                ),
                scaffold_level=level,
                next_if_correct="升级Lv3或跨学科缝合",
                next_if_wrong=f"变式题10道+错题剧本{self._get_error_script_id(entry.kb_id)}"
            )

        # P3/P4 节奏
        if state.I_interest >= 7:
            return ConductorDecision(
                action_type="agent4_advanced",
                target_agent="Agent4",
                content_spec={"type": "Lv3综合题", "mode": "兴趣驱动", "pack_id": state.pack_id},
                duration_minutes=30, priority="P3",
                reasoning=f"兴趣高 I={state.I_interest:.1f}，推送Lv3",
                scaffold_level="Lv3"
            )
        else:
            return ConductorDecision(
                action_type="agent3_review",
                target_agent="Agent3",
                content_spec={"type": "闪卡复习", "mode": "轻松", "pack_id": state.pack_id},
                duration_minutes=15, priority="P4",
                reasoning=f"兴趣偏低 I={state.I_interest:.1f}，轻松复习",
                scaffold_level="Lv1"
            )

    def _estimate_mastery(self, entry, state: UserState) -> float:
        base = state.S_score
        for tag in entry.tags:
            if tag.startswith("#认知层级/"):
                level = tag.replace("#认知层级/", "")
                if level == "记忆": return min(100, base + 10)
                elif level in ("分析", "评价"): return max(0, base - 10)
        return base

    def _infer_ability_id(self, entry) -> str:
        for tag in entry.tags:
            if tag.startswith("#考点类型/"):
                qtype = tag.replace("#考点类型/", "")
                return {"译篆": "A1", "句读": "A3", "名词解释": "A5",
                        "论述": "A6"}.get(qtype, "A5")
        return "A5"

    def _get_error_script_id(self, kb_id: str) -> str:
        scripts = self.kb.get_error_script_by_kb(kb_id)
        return scripts[0].script_id if scripts else "未知"
