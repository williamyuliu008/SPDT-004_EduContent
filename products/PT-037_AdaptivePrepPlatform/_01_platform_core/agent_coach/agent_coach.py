"""
Agent 4: 能力训练与动态出题 (Coach)
PT-037 平台
"""

import json
from pathlib import Path
from typing import Optional

from llm.llm_wrapper import LLMClient
from knowledge_base.knowledge_base import KnowledgeBase


class AgentCoach:
    """Agent4 — 动态出题教练"""

    SYSTEM_PROMPT = """你是国美书法校考备考平台的首席教练 Agent4。
严格遵循以下规则输出，每道题必须输出标准JSON对象：
{
  "question_id": "QT_001",
  "question_type": "A1_译篆|A2_书体辨识|A3_句读|A4_古文翻译|A5_名词解释|A6_史论|A7_缝合",
  "difficulty": "Lv1|Lv2|Lv3",
  "text": "题目正文（中文，不含选项列表以外的任何说明）",
  "options": null,
  "correct_answer": "参考答案（中文，直接给出答案内容）",
  "hints": ["提示1", "提示2"],
  "scoring": {"满分": "描述", "部分得分": "描述"}
}
重要：top-level key 必须是纯ASCII字符串如"question_id"，不要用中文key，不要嵌套额外的包装对象。只输出这一个JSON，不要有任何其他文字。"""

    def __init__(self, llm_client: LLMClient, knowledge_base: KnowledgeBase):
        self.llm = llm_client
        self.kb = knowledge_base

    def generate_question(
        self,
        focus_kb_id: Optional[str] = None,
        ability_id: Optional[str] = None,
        difficulty: str = "Lv2",
        pack_id: str = "cafa_calligraphy_2026",
        override: Optional[dict] = None
    ) -> dict:
        kb_entry = self.kb.get_entry(focus_kb_id) if focus_kb_id else None
        ability = self._infer_ability(focus_kb_id, difficulty)

        user_prompt = self._build_prompt(ability, kb_entry, difficulty)
        resp = self.llm.chat(
            [{"role": "user", "content": user_prompt}],
            system=self.SYSTEM_PROMPT
        )
        return self._parse_response(resp.content, ability)

    def grade_answer(self, question: dict, user_answer: str, kb_entry=None) -> dict:
        qtype = question.get("question_type", "")

        # 译篆题自动精确评分
        if qtype in ("A1_译篆", "A1"):
            correct = question.get("correct_answer", "")
            u_clean = user_answer.strip().replace(" ", "")
            c_clean = correct.strip().replace(" ", "")
            if u_clean == c_clean:
                return {"correct": True, "score": 5.0, "max_score": 5.0,
                        "feedback": "正确！字形完全符合《说文解字》标准。"}
            return {"correct": False, "score": 0.0, "max_score": 5.0,
                    "feedback": f"错误。正确答案为：{correct}。请复习「以义定形」辨析规则。"}

        # 其他题型：简单关键词匹配评分
        correct_text = question.get("correct_answer", "")
        if not correct_text and isinstance(question.get("answer"), dict):
            # 名词解释题：检查四要素关键词
            answer_dict = question["answer"]
            correct_text = json.dumps(answer_dict, ensure_ascii=False)

        # 提取答案中的关键词（约简匹配）
        answer_str = str(correct_text)
        u_str = str(user_answer)
        key_terms = ["苏轼", "黄庭坚", "米芾", "蔡襄", "尚意", "天下第",
                      "书谱", "颜真卿", "孙过庭", "五乖五合", "古质今妍"]
        found = sum(1 for t in key_terms if t in u_str)
        total = sum(1 for t in key_terms if t in answer_str)

        if total > 0:
            ratio = found / total
            if ratio >= 0.8:
                score = 16; feedback = "优秀！涵盖主要采分点。"
            elif ratio >= 0.5:
                score = 10; feedback = "基本正确，但遗漏部分要点。"
            else:
                score = 5; feedback = "要点覆盖不足，建议复习四句公式。"
        else:
            score = 8; feedback = "内容已收到，请对照参考答案复习。"

        return {"correct": ratio >= 0.5 if total > 0 else True,
                "score": score, "max_score": 20,
                "feedback": feedback}



    def _infer_ability(self, kb_id, difficulty):
        if not kb_id:
            return {"ability_id": "A5", "name": "名词解释", "question_types": ["名词解释"]}
        entry = self.kb.get_entry(kb_id)
        if not entry:
            return {"ability_id": "A5", "name": "名词解释", "question_types": ["名词解释"]}
        for tag in entry.tags:
            if tag.startswith("#考点类型/"):
                qtype = tag.replace("#考点类型/", "")
                aid = {"译篆": "A1", "句读": "A3", "名词解释": "A5",
                       "论述": "A6"}.get(qtype, "A5")
                ability = self.kb.get_ability(aid)
                if ability:
                    return {"ability_id": ability.ability_id, "name": ability.name,
                            "question_types": ability.question_types,
                            "method_破题心法": ability.method_破题心法}
        return {"ability_id": "A5", "name": "名词解释", "question_types": ["名词解释"]}

    def _build_prompt(self, ability, kb_entry, difficulty):
        kb_ctx = ""
        if kb_entry:
            kb_ctx = f"\n知识点：{kb_entry.concept}\n定义：{kb_entry.definition}\n标签：{','.join(kb_entry.tags)}"
        return (
            f"能力：{ability['ability_id']} {ability['name']}\n"
            f"心法：{ability.get('method_破题心法','')}\n"
            f"难度：{difficulty}{kb_ctx}\n\n"
            f"请生成1道训练题，JSON格式包含：question_id, question_type, difficulty, text, "
            f"correct_answer, hints, scoring。"
        )

    def _parse_response(self, content, ability):
        text = content.strip()
        # 去掉 markdown 代码块
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(l for l in lines[1:] if not l.startswith("```"))
        try:
            data = json.loads(text)
            # GLM 有时返回 {"prompt": ..., "context": ...} 的包装，跳过
            if "prompt" in data and "text" not in data:
                # 提取真正的 question 部分
                data["text"] = data.get("prompt", "")
            data.setdefault("ability_id", ability.get("ability_id", "A5"))
            return data
        except json.JSONDecodeError:
            # 尝试从非JSON文本中提取关键字段
            return {
                "error": "JSON解析失败",
                "raw": content[:500],
                "question_type": ability.get("question_types", ["未知"])[0],
                "difficulty": "Lv2",
                "text": content[:200]
            }
