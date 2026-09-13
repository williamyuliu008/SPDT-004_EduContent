"""
PT-030 雪薇端 httpx 直调 GLM (绕开 zhipuai SDK hang)
=====================================================
zhipuai 2.1.5 SDK 内部 httpx 不接受 timeout 参数, 会 hang 死.
本模块用 httpx 直接调 GLM API, timeout=10s 完全可控.

用法:
    from review_httpx import review_one_question
    result = review_one_question(question, "数学", api_key)
"""

import json
import os
import sys
from pathlib import Path
import httpx

GLM_ENDPOINT = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
DEFAULT_MODEL = "glm-4-flash"
DEFAULT_TIMEOUT = 10.0  # 单题 10s

REVIEW_PROMPT = """你是高考母题推演专家, 学科: {subject}。
请对以下母题进行完整推演:

【母题】
{question_json}

请输出 (JSON 格式):
{{
  "q_no": {q_no},
  "verdict": "可解" 或 "歧义" 或 "超纲",
  "verdict_reason": "判定理由 (10-30 字)",
  "answer": "答案字母 (A/B/C/D) 或 完整答案",
  "explanation": "解题步骤 (50-200 字, 分 1/2/3 步)",
  "key_concepts": ["核心概念 1", "核心概念 2"],
  "common_mistakes": ["易错点 1", "易错点 2"],
  "variants": [
    {{
      "direction": "简化/深化/条件隐藏/递推/分类",
      "stem": "变式题干 (30-80 字)",
      "key_change": "与原题的关键差异"
    }}
  ],
  "difficulty": "易/中/难",
  "estimated_time_minutes": 数字,
  "knowledge_tags": ["考点 1", "考点 2"]
}}

只输出 JSON, 不要其他文字。
"""


def get_api_key() -> str:
    """API key 优先级: 环境变量 > config.yaml"""
    env = os.environ.get("ZHIPU_API_KEY")
    if env:
        return env
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from pt030_toolkit.config import get_config
        cfg = get_config()
        return cfg.get("glm4_flash_api_key", cfg.get("glm5_api_key", ""))
    except Exception:
        return ""


def review_one_question(question: dict, subject: str, api_key: str,
                        model: str = DEFAULT_MODEL, timeout: float = DEFAULT_TIMEOUT) -> dict:
    """单题推演 (httpx 直调, timeout 完全可控)"""
    if not api_key:
        return {"_review_failed": True, "_error": "no api key"}

    prompt = REVIEW_PROMPT.format(
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
        "max_tokens": 2000,
    }

    try:
        with httpx.Client(timeout=timeout) as client:
            r = client.post(GLM_ENDPOINT, json=payload, headers=headers)
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
        return {"_review_failed": True, "_error": f"JSON decode: {e}"}


if __name__ == "__main__":
    # 干跑测试
    api_key = get_api_key()
    print(f"API key: {api_key[:8]}...{api_key[-4:]} (len={len(api_key)})")
    test_q = {
        "q_no": 1,
        "stem": "已知函数 f(x) = x^2 - 2x + 1, 求 f(2) 的值",
        "options": [],
    }
    import time
    t0 = time.time()
    r = review_one_question(test_q, "数学", api_key)
    print(f"耗时 {time.time()-t0:.1f}s")
    print(json.dumps(r, ensure_ascii=False, indent=2)[:500])
