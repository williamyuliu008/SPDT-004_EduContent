"""
策略卡批量生产工具 v1.0
========================
基于 GLM-5 (实际 glm-4-flash) 自动生成策略卡草稿, 人工 review 后入库.

宇兄端开发, 雪薇端可用.

用法:
  # 1. 单卡生成 (按主题 + 学科)
  python strategy_batch_gen.py gen --subject 数学 --theme "分类讨论" --output D:/4_data/.../strategy_math_002.json

  # 2. 批量生成 (1 学科 5-8 张)
  python strategy_batch_gen.py batch --subject 数学 --count 5

  # 3. 跨学科批量
  python strategy_batch_gen.py batch-all --count-per-subject 3

依赖: zhipuai (与 glm5_question_gen.py 共享 API)
"""
import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

# 路径配置
_TOOLS_DIR = Path(__file__).parent
sys.path.insert(0, str(_TOOLS_DIR))
from pt030_toolkit.config import get_config, ensure_dirs, RAW_DIR


def get_api_key() -> str:
    env = os.environ.get("ZHIPU_API_KEY")
    if env:
        return env
    cfg = get_config()
    return cfg.get("glm4_flash_api_key", cfg.get("glm5_api_key", ""))


# 学科策略族 (拍板: 6 主科 + 1 艺术)
SUBJECT_STRATEGIES = {
    "数学": [
        "数形结合", "分类讨论", "方程思想", "函数与方程", "化归思想",
        "特殊值法", "向量法", "参数法", "几何变换", "概率与统计"
    ],
    "语文": [
        "古诗意象-意境-情感", "文言文断句", "议论文引-议-联-结", "现代文阅读",
        "作文审题立意", "字音字形辨识", "病句修改", "古诗比较鉴赏"
    ],
    "英语": [
        "阅读理解主旨-细节-推理", "完形填空上下文推断", "写作模板+亮点",
        "语法填空", "词义猜测", "长难句分析", "听力速记"
    ],
    "历史": [
        "时序定位法", "因果链分析", "史料解读法", "比较类答题",
        "阶段特征", "唯物史观生产力-生产关系", "全球史视野", "史料互证"
    ],
    "地理": [
        "经纬定位", "等值线判读", "气候类型分析", "地理过程",
        "区域比较", "人地关系", "地理示意图", "自然地理综合"
    ],
    "政治": [
        "主体分析法", "矛盾分析法", "价值判断与价值选择",
        "时政结合", "论证结构", "综合探究", "经济生活", "政治生活"
    ],
    "书法": [
        "五体辨识", "临摹要点", "创作转化", "中国书法史",
        "篆刻基础", "装裱与展示"
    ],
}


# 4 步法策略卡 Prompt (v1.0 沿用 4 步法结构)
STRATEGY_GEN_PROMPT = """你是高考策略卡出题专家, 学科: {subject}。
请围绕策略主题 "{theme}" 生成 1 张高质量的策略卡, 要求:

1. **5 步 SOP**: 5 步内的标准操作流程, 学生可照做 (用 → 或 . 串联)
2. **验收标准**: 1-2 句话, 含可量化指标 (能/会/正确/通过 + 数字)
3. **典型例题**: 1-2 句话的简短例题 (高考真题或典型题)
4. **适用条件**: 题型/题目特征 (选择题/大题/客观题/主观题)
5. **直觉理解**: 1 句话, 为什么这策略有效
6. **思维路径**: 5 步以内, 从识别 → 操作 → 验证
7. **核心洞察**: 1 句话, 跨题迁移的"金句"
8. **关联母题**: 1-3 个相关母题 ID (如 pp_001/pp_006, 历史可填 hp_001)
9. **出处**: 教材/教师参考书/网课/经验, 1-2 句话
10. **学科核心概念**: 2-3 个

输出 JSON 对象:
{{
  "card_id": "strategy_{subject_code}_{3位编号}",
  "chain_id": "{subject_code}_strategy_{theme_pinyin}",
  "schema_version": "v1.0",
  "SOP": "1. ... → 2. ... → 3. ... → 4. ... → 5. ...",
  "验收标准": "能独立...",
  "source_type": "学科方法论",
  "source_ref": "...",
  "original_problem_id": "pp_xxx, pp_yyy",
  "problem_statement": "...",
  "given_conditions": "适用: 题型/题目特征",
  "intuition": "...",
  "thinking_path": "1. ... 2. ... 3. ... 4. ... 5. ...",
  "key_insight": "..."
}}

只输出 JSON, 不要其他文字。
"""


SUBJECT_CODE_MAP = {
    "数学": "math", "语文": "chinese", "英语": "english",
    "历史": "history", "地理": "geo", "政治": "politics", "书法": "calligraphy"
}


def call_glm4_flash(subject: str, theme: str, api_key: str) -> dict:
    """调用 glm-4-flash 生成单张策略卡"""
    try:
        from zhipuai import ZhipuAI
    except ImportError:
        print("ERROR: 需要 pip install zhipuai", file=sys.stderr)
        return {}

    if not api_key:
        print("ERROR: 缺少 API key", file=sys.stderr)
        return {}

    client = ZhipuAI(api_key=api_key)
    prompt = STRATEGY_GEN_PROMPT.format(subject=subject, theme=theme)
    try:
        response = client.chat.completions.create(
            model="glm-4-flash",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=2500,
        )
        content = response.choices[0].message.content
        # 提取 JSON
        m = re.search(r"\{.*\}", content, re.DOTALL)
        if not m:
            print(f"  ERROR: 模型未返回 JSON, 内容前 200: {content[:200]}", file=sys.stderr)
            return {}
        card = json.loads(m.group(0))
        # 自动补 display_target
        if "display_target" not in card:
            card["display_target"] = ["RUJING", "学习中心"]
        return card
    except Exception as e:
        print(f"ERROR: API 调用失败: {e}", file=sys.stderr)
        return {}


def gen_one(args) -> int:
    api_key = args.api_key or get_api_key()
    if not api_key:
        print("ERROR: 缺少 API key", file=sys.stderr)
        return 1
    ensure_dirs()

    subject_code = SUBJECT_CODE_MAP.get(args.subject, args.subject.lower())
    # 推断编号: 找目录下最大编号 + 1
    subject_dir = RAW_DIR.parent.parent / "knowledge_cards" / "策略" / args.subject
    if not subject_dir.exists():
        subject_dir = Path(rf"D:\4_data\knowledge_cards\策略\{args.subject}")
    existing = list(subject_dir.glob(f"strategy_{subject_code}_*.json")) if subject_dir.exists() else []
    max_n = 0
    for f in existing:
        m = re.search(r"_(\d{3})\.json", f.name)
        if m:
            max_n = max(max_n, int(m.group(1)))
    next_n = max_n + 1
    card_id = f"strategy_{subject_code}_{next_n:03d}"

    print(f"生成: {card_id} (主题: {args.theme})")
    card = call_glm4_flash(args.subject, args.theme, api_key)
    if not card:
        return 1
    # 强制覆盖 card_id
    card["card_id"] = card_id

    # 推断 chain_id (拼音) - 简化用英文
    theme_pinyin = re.sub(r"[^a-zA-Z]", "", args.theme.lower())[:20] or "general"
    card["chain_id"] = f"{subject_code}_strategy_{theme_pinyin}"

    # 输出
    out_path = args.output or (subject_dir / f"{card_id}.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(card, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  写入: {out_path} ({len(open(out_path, encoding='utf-8').read())} 字符)")
    return 0


def batch(args) -> int:
    api_key = args.api_key or get_api_key()
    if not api_key:
        print("ERROR: 缺少 API key", file=sys.stderr)
        return 1

    themes = SUBJECT_STRATEGIES.get(args.subject, [])
    if not themes:
        print(f"ERROR: 学科 {args.subject} 不在策略库", file=sys.stderr)
        return 1
    themes = themes[:args.count]

    print(f"批量生成: 学科={args.subject}, 主题数={args.count}, 主题={themes}")
    print()
    rc = 0
    for i, theme in enumerate(themes, 1):
        print(f"[{i}/{args.count}] {theme}:")
        # 模拟 argparse Namespace
        class Args:
            pass
        a = Args()
        a.subject = args.subject
        a.theme = theme
        a.api_key = api_key
        a.output = None
        rc = max(rc, gen_one(a))
        print()
        time.sleep(1)  # 限流
    return rc


def batch_all(args) -> int:
    """跨学科批量"""
    subjects = list(SUBJECT_STRATEGIES.keys())
    print(f"跨学科批量: {len(subjects)} 学科, 每学科 {args.count_per_subject} 张")
    rc = 0
    for subj in subjects:
        print(f"\n=== {subj} ===")
        class Args:
            pass
        a = Args()
        a.subject = subj
        a.count = args.count_per_subject
        a.api_key = args.api_key
        rc = max(rc, batch(a))
    return rc


def main():
    parser = argparse.ArgumentParser(
        description="策略卡批量生产工具 v1.0 (GLM-5 fallback glm-4-flash)"
    )
    subparsers = parser.add_subparsers(dest="command")

    # gen
    p_gen = subparsers.add_parser("gen", help="单卡生成")
    p_gen.add_argument("--subject", required=True, choices=list(SUBJECT_STRATEGIES.keys()))
    p_gen.add_argument("--theme", required=True, help="策略主题 (如 '分类讨论')")
    p_gen.add_argument("--output", "-o", help="输出 JSON 路径")
    p_gen.add_argument("--api-key", help="API key")
    p_gen.set_defaults(func=gen_one)

    # batch
    p_batch = subparsers.add_parser("batch", help="单学科批量")
    p_batch.add_argument("--subject", required=True, choices=list(SUBJECT_STRATEGIES.keys()))
    p_batch.add_argument("--count", type=int, default=5, help="生成数量")
    p_batch.add_argument("--api-key", help="API key")
    p_batch.set_defaults(func=batch)

    # batch-all
    p_ba = subparsers.add_parser("batch-all", help="跨学科批量")
    p_ba.add_argument("--count-per-subject", type=int, default=2, help="每学科生成数量")
    p_ba.add_argument("--api-key", help="API key")
    p_ba.set_defaults(func=batch_all)

    args = parser.parse_args()
    if not hasattr(args, "func"):
        parser.print_help()
        return 0
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
