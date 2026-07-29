"""
LLM 接口封装 — PT-037 MVP
支持 Mock 模式（开发/演示）和真实 GLM API 调用
"""

import os
import json
import re
from typing import Optional
from dataclasses import dataclass


@dataclass
class LLMResponse:
    content: str
    raw: dict
    tokens_used: Optional[int] = None


class LLMClient:
    """LLM 调用客户端，支持 mock / GLM / OpenAI 兼容接口"""

    def __init__(self, mode: str = "mock", model: str = "glm-4-flash", **kwargs):
        self.mode = mode
        self.model = model
        self.kwargs = kwargs

    def chat(
        self,
        messages: list[dict],
        system: Optional[str] = None,
        temperature: float = 0.7,
        **kwargs
    ) -> LLMResponse:
        """
        统一 chat 接口。

        Args:
            messages: [{"role": "user"/"assistant"/"system", "content": "..."}]
            system: 系统提示（优先级高于 messages 中的 system 条目）
            temperature: 采样温度
        """
        if system:
            messages = [{"role": "system", "content": system}] + messages

        if self.mode == "mock":
            return self._mock_response(messages)
        elif self.mode == "glm":
            return self._glm_call(messages, temperature, **kwargs)
        elif self.mode == "openai":
            return self._openai_call(messages, temperature, **kwargs)
        else:
            raise ValueError(f"Unknown mode: {self.mode}")

    # ─── Mock 模式 ───────────────────────────────────────────────────────────

    def _mock_response(self, messages: list[dict]) -> LLMResponse:
        """根据消息内容生成模拟响应，用于开发测试"""
        last_msg = messages[-1]["content"] if messages else ""

        # Agent4 Coach 模拟响应
        if "出题" in last_msg or "生成" in last_msg or "题目" in last_msg:
            return self._mock_coach(last_msg)
        # Agent2 Auditor 模拟响应
        if "审计" in last_msg or "Critic" in last_msg or "审查" in last_msg:
            return self._mock_auditor(last_msg)
        # Agent5 Conductor 模拟响应
        if "调度" in last_msg or "决策" in last_msg or "S_C_F_I" in last_msg:
            return self._mock_conductor(last_msg)
        # 默认
        return LLMResponse(
            content=f"[Mock] 已处理请求，消息长度={len(last_msg)}字符",
            raw={"mode": "mock", "messages_count": len(messages)}
        )

    def _mock_coach(self, prompt: str) -> LLMResponse:
        """Agent4 模拟出题"""
        # 检测题型
        if "译篆" in prompt:
            content = json.dumps({
                "question_type": "A1_译篆",
                "difficulty": "Lv2",
                "text": "请将「斗争」译为《说文解字》标准篆书。",
                "options": None,
                "correct_answer": "鬥爭",
                "hints": [
                    "提示：「斗」在《说文解字》中对应两个篆形，请根据含义判断。",
                    "辨析：争斗之「斗」从「鬥」部（两手相持）；量器之「斗」从「十」从「又」。"
                ],
                "scoring": {
                    "满分": "每个篆字5分，字形结构完全正确",
                    "部分得分": "部首正确但位置错误=3分；简体字=0分"
                }
            }, ensure_ascii=False, indent=2)
        elif "句读" in prompt:
            content = json.dumps({
                "question_type": "A3_句读",
                "difficulty": "Lv2",
                "text": "请给下列文言文加注标点，并翻译成现代汉语：\n张旭善草书不治他技喜怒窘穷忧悲愉佚怨恨思慕酣醉无聊不平有动于心必于草书焉发之",
                "answer": {
                    "punctuated": "张旭善草书，不治他技。喜怒窘穷，忧悲愉佚，怨恨思慕，酣醉无聊，不平，有动于心，必于草书焉发之。",
                    "translation": "张旭擅长草书，不钻研其他技艺。高兴、愤怒、窘迫、贫穷，忧愁、悲伤、愉快、放纵，怨恨、思慕，酒醉、无聊，心中感到不平时，必定借助草书来抒发。"
                },
                "scoring_points": [
                    "正确断开「喜怒窘穷」「忧悲愉佚」等情绪词排比（4分）",
                    "正确断开「山水崖谷」等物象词排比（4分）",
                    "关键词「不治他技」「有动于心」「一寓于书」翻译准确（4分）"
                ]
            }, ensure_ascii=False, indent=2)
        elif "名词解释" in prompt:
            content = json.dumps({
                "question_type": "A5_名词解释",
                "difficulty": "Lv2",
                "text": "名词解释：宋四家",
                "answer": {
                    "定性": "北宋四大书法家苏轼、黄庭坚、米芾、蔡襄的合称，代表宋代书法最高成就。",
                    "展开": "宋代打破唐代「尚法」书风，倡导「尚意」，强调书写者的学识、性情与主体精神。苏轼丰腴跌宕（《黄州寒食诗帖》，天下第三行书）；黄庭坚长枪大戟（《松风阁诗帖》）；米芾八面出锋（《蜀素帖》）；蔡襄淳淡婉美（《扈从帖》）。",
                    "评价": "宋四家确立宋代尚意书风，对元明清文人书审美走向影响深远。"
                },
                "scoring": "定性4分 + 四人全+代表作6分 + 尚意关键词4分 + 影响评价2分 = 满分20分",
                "common_mistakes": [
                    "蔡襄写成蔡京（正统为蔡襄）",
                    "苏轼写成「苏东坡」（写本名）",
                    "遗漏「天下第三行书」"
                ]
            }, ensure_ascii=False, indent=2)
        else:
            content = json.dumps({
                "question_type": "A5_名词解释",
                "difficulty": "Lv2",
                "text": "名词解释：《书谱》",
                "answer": {
                    "定性": "唐代孙过庭所著《书谱卷上》，书于垂拱三年（687年），既是草书杰作，也是中国书法史上最系统的书学论著之一。",
                    "展开": "系统论述书法的源流、技法（执使转用）、风格变迁与学书阶段。核心理论：「古质今妍」（审美演进观）、「五乖五合」（创作条件论）、「达其情性，形其哀乐」（情感表现说）。墨迹本草书，法二王而自成清健遒劲。",
                    "评价": "确立「艺文并重」的书法批评体系，对宋元以来文人书法理论与创作实践影响深远。"
                },
                "scoring": "定性4分 + 理论内容6分 + 代表作4分 + 影响评价2分 = 满分16分（参考）"
            }, ensure_ascii=False, indent=2)

        return LLMResponse(
            content=content,
            raw={"mode": "mock", "agent": "coach"}
        )

    def _mock_auditor(self, prompt: str) -> LLMResponse:
        """Agent2 模拟对抗式审计"""
        # 检测是否包含待审计的知识条目
        if "宋四家" in prompt:
            verdict = {
                "verdict": "PASS",
                "dimensions": {
                    "事实核查": "PASS — 四人名单准确，苏轼/黄庭坚/米芾/蔡襄正确",
                    "逻辑诊断": "PASS — 因果关系成立，尚意为宋代书风转变的核心原因",
                    "概念界定": "PASS — 「尚意」与「尚法」区分清晰",
                    "应试有效性": "PASS — 包含全部采分点，有助于国美校考得分"
                },
                "score": 18,
                "max_score": 20,
                "revision_suggestions": [
                    "可补充：蔡襄的代表作《扈从帖》是否确为书法界公认，可考虑以《虹县帖》替代"
                ]
            }
        elif "书谱" in prompt:
            verdict = {
                "verdict": "NEED_REVISION",
                "dimensions": {
                    "事实核查": "PASS — 作者孙过庭、垂拱三年准确",
                    "逻辑诊断": "PASS",
                    "概念界定": "FAIL — 「五乖五合」的解释过于简略，未区分「乖」与「合」的具体内容",
                    "应试有效性": "PASS"
                },
                "score": 12,
                "max_score": 20,
                "revision_suggestions": [
                    "「五乖五合」需展开：乖（不利）= 神怡务闲 / 感惠徇知 ... 合（有利）= 时和气润 / 纸墨相发 ...",
                    "补充《书谱》草书墨迹传世这一双重属性"
                ]
            }
        elif "知识条目" in prompt or "kb_vocab" in prompt:
            verdict = {
                "verdict": "PASS",
                "dimensions": {
                    "事实核查": "PASS",
                    "逻辑诊断": "PASS",
                    "概念界定": "PASS",
                    "应试有效性": "PASS"
                },
                "score": 18,
                "max_score": 20,
                "revision_suggestions": []
            }
        else:
            verdict = {
                "verdict": "PASS",
                "dimensions": {
                    "事实核查": "PASS",
                    "逻辑诊断": "PASS",
                    "概念界定": "PASS",
                    "应试有效性": "PASS"
                },
                "score": 16,
                "max_score": 20,
                "revision_suggestions": []
            }

        return LLMResponse(
            content=json.dumps(verdict, ensure_ascii=False, indent=2),
            raw={"mode": "mock", "agent": "auditor"}
        )

    def _mock_conductor(self, prompt: str) -> LLMResponse:
        """Agent5 模拟调度决策"""
        decision = {
            "action_type": "agent4_training",
            "target_agent": "Agent4",
            "content_spec": {
                "type": "Lv2名词解释",
                "focus_kb_id": "KB_CAFA_S003",
                "focus_concept": "书谱",
                "pack_id": "cafa_calligraphy_2026"
            },
            "duration_minutes": 25,
            "priority": "P2",
            "reasoning": "S=65%（书谱掌握度偏低），C=5（认知负荷适中），F=1（疲劳值低），I=6（兴趣正常）→ 推送Lv2专项训练",
            "scaffolding": "Lv2 — 双知识点关联，考察理解与应用",
            "next_if_correct": "升级Lv3，跨学科缝合（书法史+文言文）",
            "next_if_wrong": "推送同类型变式题10道 + 错题剧本 ES-005"
        }
        return LLMResponse(
            content=json.dumps(decision, ensure_ascii=False, indent=2),
            raw={"mode": "mock", "agent": "conductor"}
        )

    # ─── GLM 模式 ───────────────────────────────────────────────────────────

    def _glm_call(
        self,
        messages: list[dict],
        temperature: float,
        **kwargs
    ) -> LLMResponse:
        """调用 GLM 系列模型（需要配置 API Key）"""
        import urllib.request
        import urllib.error

        api_key = os.environ.get("ZHIPU_API_KEY") or self.kwargs.get("api_key")
        if not api_key:
            raise RuntimeError(
                "未设置 ZHIPU_API_KEY 环境变量，请先设置：\n"
                "  $env:ZHIPU_API_KEY='your-api-key'\n"
                "或切换到 mock 模式：LLMClient(mode='mock')"
            )

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            **kwargs
        }

        req = urllib.request.Request(
            "https://open.bigmodel.cn/api/paas/v4/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                content = data["choices"][0]["message"]["content"]
                tokens = data.get("usage", {}).get("total_tokens")
                return LLMResponse(content=content, raw=data, tokens_used=tokens)
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8")
            raise RuntimeError(f"GLM API 错误 {e.code}: {err_body}")

    # ─── OpenAI 兼容模式 ─────────────────────────────────────────────────────

    def _openai_call(
        self,
        messages: list[dict],
        temperature: float,
        **kwargs
    ) -> LLMResponse:
        """调用 OpenAI 兼容 API"""
        import urllib.request
        import urllib.error

        base_url = self.kwargs.get("base_url", "https://api.openai.com/v1")
        api_key = os.environ.get("OPENAI_API_KEY") or self.kwargs.get("api_key")
        if not api_key:
            raise RuntimeError("未设置 OPENAI_API_KEY 环境变量")

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            **kwargs
        }

        req = urllib.request.Request(
            f"{base_url.rstrip('/')}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                content = data["choices"][0]["message"]["content"]
                tokens = data.get("usage", {}).get("total_tokens")
                return LLMResponse(content=content, raw=data, tokens_used=tokens)
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8")
            raise RuntimeError(f"OpenAI API 错误 {e.code}: {err_body}")


# ─── 快捷工厂函数 ───────────────────────────────────────────────────────────

def create_llm_client(mode: str = "mock", **kwargs) -> LLMClient:
    """根据模式创建 LLM 客户端"""
    return LLMClient(mode=mode, **kwargs)
