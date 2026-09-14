"""
元学习批量生成器 v1.0
====================
基于 GLM-4-flash 自动生成元学习卡草稿, 人工 review 后入库.

学生画像: 上海文科艺术生 (高考 6 主科 + 1 艺术, 排除理化生)
目标: 8 → 20 张

用法:
  python meta_batch_gen.py gen --theme 主动回忆 --output D:/4_data/.../meta_009.json
  python meta_batch_gen.py batch
"""
import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

_TOOLS_DIR = Path(__file__).parent
sys.path.insert(0, str(_TOOLS_DIR))


def get_api_key() -> str:
    env = os.environ.get("ZHIPU_API_KEY")
    if env:
        return env
    secret = Path(r"D:\3_infra\_SECRET_KEY\zhipu_api.txt")
    if secret.exists():
        return secret.read_text(encoding="utf-8").strip()
    return ""


# 12 张 P0-C 元学习选题 (排除已有 8 张)
META_THEMES = [
    "主动回忆法",
    "间隔重复",
    "睡眠与记忆巩固",
    "错题本使用法",
    "刻意练习",
    "SQ3R阅读法",
    "番茄变体52+17长时段专注",
    "元认知监控",
    "自我效能感培养",
    "学习迁移",
    "反馈循环",
    "成长型思维",
]


META_GEN_PROMPT = """你是高考元学习策略专家, 学生画像: 上海文科艺术生 (高考 6 主科语数英史地政 + 1 艺术书法 + 国美校招).
请围绕主题 "{theme}" 生成 1 张高质量的元学习卡 JSON, 要求:

字段 schema (参考已有 8 张):
- card_id: "meta_NNN" (由程序生成, 留空)
- chain_id: "meta_learning_xxx" (英文连字符, 简短)
- schema_version: "v1.0"
- SOP: 5-7 步标准操作流程 (用 → 串联, 简短)
- 验收标准: 1-2 句话, 含可量化指标 (天数/正确率/产出)
- source_type: "记忆术/认知科学/应试策略/心理学/时间管理" 之一
- source_ref: 来源 (1-2 句, 含学者或研究)
- original_problem_id: ""
- problem_statement: 1-2 句话, 学生场景问题
- given_conditions: 适用场景 + 学科范围 (含上海高考 6 主科 + 1 艺术)
- figure_description: 1-2 句图描述
- figure_ref: ""
- figure_type: ""
- intuition: 1-2 句话, 为什么这方法有效
- thinking_path: 5-7 步具体应用路径
- key_insight: 1 句话跨场景金句
- display_target: ["学习中心"]

要求:
- 不要在文本中使用 \\\\ 双重反斜杠或 $ 公式符号
- 选题主语用"学生"或"我", 避免抽象
- SOP 和 thinking_path 各步具体可执行 (10-20 字/步), 不要"步骤1"/"步骤2"占位
- 验收标准含具体数字 (如 "坚持 2 周后错题复现率 < 20%")
- display_target 只填 ["学习中心"], 不要填 RUJING

输出 JSON 对象:
{{
  "card_id": "meta_NNN",
  "chain_id": "meta_learning_xxx",
  "schema_version": "v1.0",
  "SOP": "1. xxx → 2. xxx → 3. xxx → 4. xxx → 5. xxx",
  "验收标准": "坚持 N 周后, 量化指标",
  "source_type": "记忆术/认知科学/...",
  "source_ref": "来源",
  "original_problem_id": "",
  "problem_statement": "学生场景",
  "given_conditions": "适用场景",
  "figure_description": "图描述",
  "figure_ref": "",
  "figure_type": "",
  "intuition": "为什么有效",
  "thinking_path": "应用步骤",
  "key_insight": "金句",
  "display_target": ["学习中心"]
}}

只输出 JSON, 不要其他文字。
"""


def call_glm4_flash(theme: str, api_key: str) -> dict:
    try:
        from zhipuai import ZhipuAI
    except ImportError:
        return {}
    client = ZhipuAI(api_key=api_key)
    prompt = META_GEN_PROMPT.format(theme=theme)
    for retry in range(2):
        try:
            response = client.chat.completions.create(
                model="glm-4-flash",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4,
                max_tokens=2500,
            )
            content = response.choices[0].message.content
            m = re.search(r"\{.*\}", content, re.DOTALL)
            if not m:
                continue
            try:
                return json.loads(m.group(0))
            except json.JSONDecodeError:
                fixed = m.group(0).replace("\\\\", "\\")
                try:
                    return json.loads(fixed)
                except Exception:
                    continue
        except Exception as e:
            print(f"ERROR (retry {retry+1}): {e}", file=sys.stderr)
            time.sleep(2)
    return {}


def gen_one(args) -> int:
    api_key = args.api_key or get_api_key()
    if not api_key:
        return 1

    meta_dir = Path(r"D:\4_data\knowledge_cards\元学习")
    existing = list(meta_dir.glob("meta_*.json"))
    max_n = 0
    for f in existing:
        m = re.search(r"meta_(\d{3})", f.name)
        if m:
            max_n = max(max_n, int(m.group(1)))
    next_n = max_n + 1
    card_id = f"meta_{next_n:03d}"

    print(f"生成: {card_id} (主题: {args.theme})")
    card = call_glm4_flash(args.theme, api_key)
    if not card:
        print(f"  FAILED: {args.theme}", file=sys.stderr)
        return 1

    card["card_id"] = card_id
    # chain_id 后缀化
    theme_en = re.sub(r"[^a-zA-Z]", "", args.theme.lower())[:20] or "general"
    if not card.get("chain_id") or "meta_learning_xxx" in card.get("chain_id", ""):
        card["chain_id"] = f"meta_learning_{theme_en}"
    card["schema_version"] = "v1.0"
    card["display_target"] = ["学习中心"]
    card["original_problem_id"] = ""
    card["_created_by"] = "P0-C 元学习 batch gen (GLM-4-flash)"

    out = args.output or (meta_dir / f"{card_id}.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(card, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  OK: {out}")
    return 0


def batch(args) -> int:
    api_key = args.api_key or get_api_key()
    if not api_key:
        return 1

    themes = META_THEMES[:args.count] if args.count else META_THEMES
    print(f"批量生成: {len(themes)} 张元学习")
    rc = 0
    for i, theme in enumerate(themes, 1):
        print(f"\n[{i}/{len(themes)}] {theme}:")
        class A:
            pass
        a = A()
        a.theme = theme
        a.api_key = api_key
        a.output = None
        rc = max(rc, gen_one(a))
        time.sleep(1)
    print(f"\n完成 {len(themes)} 张")
    return rc


def main():
    parser = argparse.ArgumentParser(description="元学习批量生成器 v1.0")
    sub = parser.add_subparsers(dest="cmd")

    p_gen = sub.add_parser("gen")
    p_gen.add_argument("--theme", required=True)
    p_gen.add_argument("--output")
    p_gen.add_argument("--api-key")
    p_gen.set_defaults(func=gen_one)

    p_batch = sub.add_parser("batch")
    p_batch.add_argument("--count", type=int)
    p_batch.add_argument("--api-key")
    p_batch.set_defaults(func=batch)

    args = parser.parse_args()
    if not hasattr(args, "func"):
        parser.print_help()
        return 0
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())