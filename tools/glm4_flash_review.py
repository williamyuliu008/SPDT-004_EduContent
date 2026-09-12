"""
PT-030 C3.2 glm-4-flash 推演验证模板 v1.0
=========================================
对已有母题 (或 GLM-5 草稿), glm-4-flash 推演:
- 验证母题可解 (无歧义/有解)
- 生成完整答案 + 解析
- 推演 1-2 个变式
- 标记可能的考点

宇兄端开发, 雪薇端调用 (双 LLM 协作: GLM-5 brainstorming + glm-4-flash 验证).

用法:
  python glm4_flash_review.py <parent_problem.json> [--output reviewed.json]
  python -m pt030_toolkit.cli llm-review <parent_problem.json>

输入: parent_problem.json (含 stem, options 字段, 可选)
输出: reviewed.json (含 answer, explanation, variant 字段, 完整 4 步法母题格式)

API key: 环境变量 ZHIPU_API_KEY 或 config.yaml glm4_flash_api_key
"""

import argparse
import json
import os
import sys
from pathlib import Path

_TOOLS_DIR = Path(__file__).parent
sys.path.insert(0, str(_TOOLS_DIR))
from pt030_toolkit.config import get_config, ensure_dirs


def get_api_key() -> str:
    env = os.environ.get("ZHIPU_API_KEY")
    if env:
        return env
    cfg = get_config()
    return cfg.get("glm4_flash_api_key", cfg.get("glm5_api_key", ""))


# 推演 Prompt 模板
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


def call_glm4_flash(question: dict, subject: str, api_key: str) -> dict:
    """调用 glm-4-flash 推演单道题"""
    try:
        from zhipuai import ZhipuAI
    except ImportError:
        print("ERROR: 需要 pip install zhipuai", file=sys.stderr)
        return {}
    if not api_key:
        print("ERROR: 缺少 API key", file=sys.stderr)
        return {}

    client = ZhipuAI(api_key=api_key)
    prompt = REVIEW_PROMPT.format(
        subject=subject,
        question_json=json.dumps(question, ensure_ascii=False, indent=2),
        q_no=question.get("q_no", 0),
    )

    try:
        response = client.chat.completions.create(
            model="glm-4-flash",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=2000,
        )
        content = response.choices[0].message.content

        import re
        m = re.search(r"\{.*\}", content, re.DOTALL)
        if not m:
            print(f"  ERROR: 模型未返回 JSON", file=sys.stderr)
            print(f"  内容前 200: {content[:200]}", file=sys.stderr)
            return {}
        return json.loads(m.group(0))

    except Exception as e:
        print(f"ERROR: API 调用失败: {e}", file=sys.stderr)
        return {}


def main():
    parser = argparse.ArgumentParser(
        description="PT-030 C3.2 glm-4-flash 推演验证 v1.0"
    )
    parser.add_argument("path", help="parent_problem.json 路径 (含 questions 数组)")
    parser.add_argument("--subject", "-s", default="数学", help="学科")
    parser.add_argument("--output", "-o", help="输出 JSON 路径")
    parser.add_argument("--api-key", help="API key")
    args = parser.parse_args()

    api_key = args.api_key or get_api_key()
    if not api_key:
        print("ERROR: 缺少 API key", file=sys.stderr)
        return 1

    # 读输入
    input_path = Path(args.path)
    if not input_path.exists():
        print(f"ERROR: 输入文件不存在 {input_path}", file=sys.stderr)
        return 1
    data = json.loads(input_path.read_text(encoding="utf-8"))
    questions = data.get("questions", data if isinstance(data, list) else [data])

    if not isinstance(questions, list):
        print("ERROR: 输入 JSON 缺少 questions 数组", file=sys.stderr)
        return 1

    print(f"推演: 学科={args.subject}, 共 {len(questions)} 题")

    reviewed = []
    for i, q in enumerate(questions, 1):
        print(f"  [{i}/{len(questions)}] Q{q.get('q_no', i)}: ", end="")
        result = call_glm4_flash(q, args.subject, api_key)
        if result:
            print(f"{result.get('verdict', '?')} - {q.get('stem', '')[:40]}...")
            # 合并原题 + 推演结果
            merged = {**q, **result}
            reviewed.append(merged)
        else:
            print(f"FAILED")
            reviewed.append({**q, "_review_failed": True})

    # 输出
    if args.output:
        out_path = Path(args.output)
    else:
        out_path = input_path.parent / f"{input_path.stem}_reviewed.json"

    out_path.parent.mkdir(parents=True, exist_ok=True)
    output = {
        "subject": args.subject,
        "input_file": str(input_path),
        "total": len(questions),
        "reviewed": len([r for r in reviewed if not r.get("_review_failed")]),
        "questions": reviewed,
        "_v1_caveat": "v1.0 glm-4-flash 推演. 4 步法 v1.0/v1.1 字段需人工补全 (display_target, source_type, source_ref 等).",
        "_created": "2026-09-12 by 宇兄窗口 (PT-030 C3.2 模板)"
    }
    out_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  写入: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
