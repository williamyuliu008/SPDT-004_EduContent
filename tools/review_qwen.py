"""
Qwen3.5-Plus 推演 (雪薇端, 立体几何重点)
=========================================
Qwen API: 阿里通义千问 3.5 Plus
endpoint: https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions
兼容 OpenAI chat completions 格式

用法:
    from review_qwen import review_one_question
    result = review_one_question(question, "数学立体几何", api_key)
"""

import json
import os
import sys
from pathlib import Path
import httpx

QWEN_ENDPOINT = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
DEFAULT_MODEL = "qwen-plus"  # 通义千问 Plus
DEFAULT_TIMEOUT = 30.0

# 立体几何专项 prompt (增强, 注重教学价值)
REVIEW_PROMPT_3D = """你是上海高考立体几何推演专家, 学科: {subject}。
请对以下立体几何母题进行深度推演:

【母题】
{question_json}

请输出 (JSON 格式, 详细):
{{
  "q_no": {q_no},
  "verdict": "可解" | "歧义" | "超纲",
  "verdict_reason": "判定理由 (20-50 字)",
  "answer": "答案字母或完整答案",
  "explanation": "解题步骤 (100-300 字, 分 1/2/3 步, 含关键定理引用: 三垂线定理/线面垂直判定/面面垂直性质/二面角/建系法/向量法 等)",
  "key_concepts": ["核心概念 1 (如:三垂线定理)", "核心概念 2 (如:线面垂直判定")],
  "common_mistakes": ["易错点 1 (如:漏 PA⊥底面 条件)", "易错点 2 (如:建系坐标算错)"],
  "variants": [
    {{
      "direction": "简化/深化/条件隐藏/递推/分类讨论/改图形 (如四棱锥→正方体)/改条件 (如矩形→正方形)",
      "stem": "变式题干 (50-100 字, 完整可解)",
      "key_change": "与原题的关键差异 (1 句话)",
      "solution_sketch": "变式解题思路 (30-80 字)"
    }},
    {{
      "direction": "...",
      "stem": "...",
      "key_change": "...",
      "solution_sketch": "..."
    }}
  ],
  "difficulty": "易/中/难/压轴",
  "estimated_time_minutes": 数字 (5-15),
  "knowledge_tags": ["考点1 (如:线面垂直判定)", "考点2 (如:三垂线定理)"]
}}

只输出 JSON, 不要其他文字。变式必须可解, 思路要清晰。
"""


def get_api_key() -> str:
    """API key 优先级: 环境变量 QWEN_API_KEY > config > 默认"""
    env = os.environ.get("QWEN_API_KEY")
    if env:
        return env
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from pt030_toolkit.config import get_config
        cfg = get_config()
        return cfg.get("qwen_api_key", "")
    except Exception:
        return ""


def review_one_question(question: dict, subject: str, api_key: str,
                        model: str = DEFAULT_MODEL, timeout: float = DEFAULT_TIMEOUT) -> dict:
    """单题推演 (httpx 直调 Qwen, timeout 完全可控)"""
    if not api_key:
        return {"_review_failed": True, "_error": "no api key"}

    prompt = REVIEW_PROMPT_3D.format(
        subject=subject,
        question_json=json.dumps(question, ensure_ascii=False, indent=2),
        q_no=question.get("q_no", 0),
    )

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
        "max_tokens": 2500,
    }

    try:
        with httpx.Client(timeout=timeout) as client:
            r = client.post(QWEN_ENDPOINT, json=payload, headers=headers)
            r.raise_for_status()
            data = r.json()
        content = data["choices"][0]["message"]["content"]
    except httpx.TimeoutException:
        return {"_review_failed": True, "_error": f"timeout {timeout}s"}
    except Exception as e:
        return {"_review_failed": True, "_error": str(e)[:200]}

    # 解析 JSON
    import re
    m = re.search(r"\{.*\}", content, re.DOTALL)
    if not m:
        return {"_review_failed": True, "_error": f"no JSON: {content[:100]}"}
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError as e:
        return {"_review_failed": True, "_error": f"JSON decode: {e}", "_raw": content[:500]}


if __name__ == "__main__":
    import time
    api_key = get_api_key()
    print(f"API key: {api_key[:8]}...{api_key[-4:]} (len={len(api_key)})")
    test_q = {
        "q_no": 1,
        "stem": "如图, 在四棱锥 P-ABCD 中, 底面 ABCD 是矩形, PA⊥底面, E 是 PD 的中点. 求证: PB∥平面 ACE",
        "options": [],
    }
    t0 = time.time()
    r = review_one_question(test_q, "数学立体几何", api_key)
    print(f"耗时 {time.time()-t0:.1f}s")
    print(json.dumps(r, ensure_ascii=False, indent=2)[:600])
