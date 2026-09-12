"""
PT-030 C3.1 GLM-5 出题模板 v1.0
================================
给定主题/知识点, GLM-5 生成 N 个母题候选 (含题干/选项/答案/解析).

宇兄端开发, 雪薇端调用.

注: GLM-5 max_tokens 经常被 reasoning 占满, content 0 chars
    实际生产用 glm-4-flash (GLM-5 作 brainstorming, glm-4-flash 作正式生成)

用法:
  python glm5_question_gen.py <theme> [--count 5] [--output questions.json]
  python -m pt030_toolkit.cli llm-gen "函数与极限" --count 3

API key: 环境变量 ZHIPU_API_KEY 或 config.yaml glm5_api_key
"""

import argparse
import json
import os
import sys
from pathlib import Path

# 路径配置
_TOOLS_DIR = Path(__file__).parent
sys.path.insert(0, str(_TOOLS_DIR))
from pt030_toolkit.config import get_config, ensure_dirs


def get_api_key() -> str:
    """API key 优先级: 环境变量 > config.yaml > 默认空"""
    env = os.environ.get("ZHIPU_API_KEY")
    if env:
        return env
    cfg = get_config()
    return cfg.get("glm5_api_key", "")


# 4 步法母题 Prompt 模板 (v1.0)
QUESTION_GEN_PROMPT = """你是高考母题出题专家, 学科: {subject}。
请围绕主题 "{theme}" 生成 {count} 道高质量母题, 每道母题要求:

1. 题干: 50-150 字, 体现高考考点, 难易度中等
2. 选项: 4 个 (A/B/C/D), 长度相近, 干扰项有迷惑性
3. 答案: 字母 (A/B/C/D)
4. 解析: 30-80 字, 说明解题关键步骤
5. 知识点: 列出 2-3 个核心概念
6. 母题变式: 给出 1 个简化/深化变式方向 (一句话)

输出 JSON 数组, 每个元素:
[
  {{
    "q_no": 1,
    "stem": "题干文字...",
    "options": {{"A": "...", "B": "...", "C": "...", "D": "..."}},
    "answer": "A",
    "explanation": "解析...",
    "knowledge_points": ["概念1", "概念2"],
    "variant_direction": "变式方向"
  }},
  ...
]

只输出 JSON 数组, 不要其他文字。
"""


def call_glm5(theme: str, subject: str, count: int, api_key: str) -> list[dict]:
    """调用 GLM-5 API 出题 (实际用 glm-4-flash fallback)"""
    try:
        from zhipuai import ZhipuAI
    except ImportError:
        print("ERROR: 需要 pip install zhipuai", file=sys.stderr)
        return []

    if not api_key:
        print("ERROR: 缺少 API key, 设环境变量 ZHIPU_API_KEY 或 config.yaml glm5_api_key", file=sys.stderr)
        return []

    client = ZhipuAI(api_key=api_key)
    prompt = QUESTION_GEN_PROMPT.format(
        subject=subject, theme=theme, count=count
    )

    # 优先用 glm-4-flash (GLM-5 reasoning 占满 max_tokens)
    # 注释: 实际工程中可作双 LLM 协作 (GLM-5 brainstorming, glm-4-flash 生成)
    model = "glm-4-flash"
    print(f"  调用 {model} (GLM-5 fallback, 因 reasoning 占用 max_tokens)...")

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000,
        )
        content = response.choices[0].message.content

        # 解析 JSON
        import re
        m = re.search(r"\[\s*\{.*\}\s*\]", content, re.DOTALL)
        if not m:
            print(f"ERROR: 模型未返回 JSON 数组", file=sys.stderr)
            print(f"  原始内容前 300 字符: {content[:300]}", file=sys.stderr)
            return []
        questions = json.loads(m.group(0))
        return questions

    except Exception as e:
        print(f"ERROR: API 调用失败: {e}", file=sys.stderr)
        return []


def main():
    parser = argparse.ArgumentParser(
        description="PT-030 C3.1 GLM-5 出题模板 v1.0 (宇兄端 ↔ 雪薇端)"
    )
    parser.add_argument("theme", help="主题/知识点 (如 '函数与极限')")
    parser.add_argument("--subject", "-s", default="数学", help="学科 (默认: 数学)")
    parser.add_argument("--count", "-c", type=int, default=5, help="出题数量 (默认 5)")
    parser.add_argument("--output", "-o", help="输出 JSON 路径")
    parser.add_argument("--api-key", help="API key (默认从环境变量/config 读取)")
    args = parser.parse_args()

    api_key = args.api_key or get_api_key()
    if not api_key:
        print("ERROR: 缺少 API key, 参见 --help", file=sys.stderr)
        return 1

    ensure_dirs()

    print(f"出题: 学科={args.subject}, 主题={args.theme}, 数量={args.count}")
    questions = call_glm5(args.theme, args.subject, args.count, api_key)

    if not questions:
        print("ERROR: 未生成任何题目", file=sys.stderr)
        return 1

    print(f"  生成 {len(questions)} 道母题")

    # 输出
    if args.output:
        out_path = Path(args.output)
    else:
        out_dir = Path(__file__).parent.parent.parent.parent / "4_data" / "rujing_out" / "真题主库" / "llm_gen"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{args.subject}_{args.theme}_gen.json"

    out_path.parent.mkdir(parents=True, exist_ok=True)
    result = {
        "subject": args.subject,
        "theme": args.theme,
        "count": len(questions),
        "model": "glm-4-flash (GLM-5 fallback)",
        "questions": questions,
        "_v1_caveat": "v1.0 LLM 出题模板. 实际用 glm-4-flash (GLM-5 reasoning 占满 max_tokens). 答案/解析需人工 review.",
        "_created": "2026-09-12 by 宇兄窗口 (PT-030 C3.1 模板)"
    }
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  写入: {out_path}")

    # 打印前 2 题预览
    for q in questions[:2]:
        print(f"  Q{q.get('q_no', '?')}: {q.get('stem', '')[:60]}...")
        print(f"    答案: {q.get('answer', '?')}, 解析: {q.get('explanation', '')[:50]}...")

    return 0


if __name__ == "__main__":
    sys.exit(main())
