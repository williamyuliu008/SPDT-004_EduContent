"""
5 学科母题批量生成器 v1.0
=========================
基于 GLM-4-flash 自动生成 5 学科母题草稿, 人工 review 后入库.

5 学科 (排除物理化学生物):
  语文 10 + 英语 10 + 地理 8 + 政治 8 + 书法 5 = 41 张

宇兄端开发, 雪薇端可用.

用法:
  # 1. 单张生成
  python mother_problem_batch_gen.py gen --subject 语文 --theme "古诗意象鉴赏" --output D:/4_data/.../ch_001_xxx.json

  # 2. 单学科批量
  python mother_problem_batch_gen.py batch --subject 语文

  # 3. 5 学科批量
  python mother_problem_batch_gen.py batch-all
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


# 5 学科母题选题 (排除物理化学生物)
SUBJECT_MOTHER_PROBLEMS = {
    "数学": [
        # P0-B.2 补 4 虚拟概念 (向量基础 / 函数与方程 / 解析几何 / 导数)
        "向量加减法",                  # pp_016 (向量基础)
        "向量共线判定",                # pp_017 (向量基础)
        "向量数量积",                  # pp_018 (向量基础)
        "函数零点判定",                # pp_019 (函数与方程)
        "二次函数最值",                # pp_020 (函数与方程)
        "函数应用题",                  # pp_021 (函数与方程)
        "椭圆方程与性质",              # pp_022 (解析几何)
        "直线与圆位置关系",            # pp_023 (解析几何)
        "抛物线焦点",                  # pp_024 (解析几何)
        "导数切线方程",                # pp_025 (导数)
        "导数极值判定",                # pp_026 (导数)
        "导数不等式证明",              # pp_027 (导数)
    ],
    "语文": [
        "古诗意象-意境-情感鉴赏",       # ch_001
        "文言文断句",                  # ch_002
        "文言实词词义推断",            # ch_003
        "议论文论据分析",              # ch_004
        "现代文阅读主旨大意",          # ch_005
        "现代文阅读细节理解",          # ch_006
        "病句修改",                    # ch_007
        "成语辨析",                    # ch_008
        "名句默写",                    # ch_009
        "作文审题立意",                # ch_010
    ],
    "英语": [
        "阅读理解主旨大意",            # en_001
        "阅读理解细节理解",            # en_002
        "阅读理解词义猜测",            # en_003
        "完形填空上下文推断",          # en_004
        "语法填空时态",                # en_005
        "语法填空非谓语",              # en_006
        "应用文写作邀请信",            # en_007
        "长难句五步切分",              # en_008
        "短文改错",                    # en_009
        "七选五段落匹配",              # en_010
    ],
    "地理": [
        "经纬定位",                    # geo_001
        "等值线判读",                  # geo_002
        "气候类型判断",                # geo_003
        "地理过程-流水地貌",           # geo_004
        "区域比较-南北方",             # geo_005
        "人地关系-城市化",             # geo_006
        "自然灾害-洪涝",               # geo_007
        "资源分布",                    # geo_008
    ],
    "政治": [
        "主体分析法-国家企业个人",     # pol_001
        "矛盾分析-两点论重点论",       # pol_002
        "价值判断-核心价值观",         # pol_003
        "时政结合-十四五",             # pol_004
        "政治生活-政府职能",           # pol_005
        "经济生活-供给侧",             # pol_006
        "文化生活-文化自信",           # pol_007
        "哲学-认识论",                 # pol_008
    ],
    "书法": [
        "五体辨识",                    # cal_001
        "楷书结构-颜体欧体",           # cal_002
        "笔法-永字八法",               # cal_003
        "书法史-王羲之兰亭序",         # cal_004
        "临摹要点",                    # cal_005
    ],
}


SUBJECT_CODE_MAP = {
    "数学": ("math", "pp"),
    "语文": ("chinese", "ch"),
    "英语": ("english", "en"),
    "地理": ("geo", "geo"),
    "政治": ("politics", "pol"),
    "书法": ("calligraphy", "cal"),
}


# 5 学科母题 prompt 模板 (v1.0)
MOTHER_PROBLEM_PROMPT = """你是高考母题出题专家, 学科: {subject}。
请围绕主题 "{theme}" 生成 1 张高质量的母题 JSON, 要求:

1. **problem_statement**: 完整高考真题或改编题。**注意: 选项 A/B/C/D 只能出现一次**! 若是选择题, 只在题尾给 4 个选项 (不再嵌一段"答案选项")。最后用 "【答案】X" 给正确答案。
2. **given_conditions**: 列出题目关键给定条件 (2-4 条)
3. **goal**: 题目目标 (选什么/算什么/写什么)
4. **intuition**: 1-2 句话, 直觉理解这题考什么
5. **thinking_path**: **5 步以内具体解题路径**, 每步 10-20 字, 形如 "识别 X → 排除 Y → 锁定 Z" (不要用"步骤1/步骤2"占位!)
6. **key_insight**: 1 句话跨题迁移金句
7. **core_method**: 核心方法名
8. **method_tag**: 1-2 个词, 形如 "{tag_prefix}-xxx/xxx" (示例: 语文 "Y-古诗鉴赏/意象", 英语 "E-阅读理解/主旨", 地理 "D-自然地理/等值线", 政治 "P-政治生活/政府职能", 书法 "S-楷书/颜体")
9. **standard_steps**: 4-5 步标准解题步骤 (列表, 每步 10-20 字)
10. **scoring_points**: 评分要点 (含分值)
11. **common_mistakes**: 2-3 个常见错误
12. **realistic_mapping**: 1 句话真实应用场景
13. **tags**: 3-5 个标签
14. **concepts_used**: 1-3 个核心概念
15. **title**: 母题标题 (10-20 字, 形如 "古诗意象-意境-情感鉴赏母题")
16. **chain_id**: "{chain_id_prefix}/X-M?-主题" 模式 (X=学科首字母, M?=模块号, 主题简短)
17. **figure_description**: 如果无图, 写 "无图"; 有图就写 "示意图说明"
18. **source_ref**: 写成"上海高考 X 年 X 学科 X 题改编" (具体年份题号, 不要"XX"占位)
19. **variant_ids_pending**: 写 "[]" 或 "待 3 变式"

输出 JSON 对象 (注意: 严格按下面 schema):
{{
  "id": "母题ID (留空, 由程序生成)",
  "chain_id": "{chain_id_prefix}/Y-M1-主题",
  "subject": "{subject_en}",
  "domain": "学科子域 (如 '古诗鉴赏/意象', '阅读理解/主旨')",
  "title": "母题标题 (10-20 字)",
  "difficulty": "中",
  "frequency": "高频",
  "source_type": "改编",
  "source_ref": "上海高考 2018 语文 Q12 改编",
  "original_problem_id": "EXAM_2018_SH_{subject_en}_12",
  "problem_statement": "完整题目 (含题干 + 4 个选项 A/B/C/D + 【答案】X)",
  "given_conditions": ["条件1", "条件2"],
  "figure_description": "无图",
  "figure_ref": null,
  "figure_type": "none",
  "goal": "题目目标",
  "intuition": "直觉理解",
  "thinking_path": "识别 X → 排除 Y → 锁定 Z → 验证",
  "key_insight": "核心金句",
  "core_method": "核心方法",
  "method_tag": "{tag_prefix}-xxx/xxx",
  "standard_steps": ["1. xxx", "2. xxx", "3. xxx", "4. xxx"],
  "scoring_points": ["要点1 (X 分)", "要点2 (X 分)"],
  "common_mistakes": ["错选1", "错选2"],
  "realistic_mapping": "真实应用",
  "variant_ids_pending": "[]",
  "tags": ["标签1", "标签2", "标签3", "v1.1"]
}}

只输出 JSON, 不要其他文字。
"""


def call_glm4_flash(subject: str, theme: str, api_key: str) -> dict:
    """调用 GLM-4-flash 生成 1 张母题"""
    try:
        from zhipuai import ZhipuAI
    except ImportError:
        print("ERROR: 需要 pip install zhipuai", file=sys.stderr)
        return {}

    if not api_key:
        print("ERROR: 缺少 API key", file=sys.stderr)
        return {}

    subject_en, code = SUBJECT_CODE_MAP.get(subject, (subject.lower(), "x"))

    # chain_id 前缀
    chain_id_map = {
        "数学": "math",
        "语文": "chinese",
        "英语": "english",
        "地理": "geo",
        "政治": "politics",
        "书法": "calligraphy",
    }
    chain_id_prefix = chain_id_map.get(subject, subject_en)

    # method_tag 前缀 (与 strategy_crosslink v1.2 规则对齐)
    tag_prefix_map = {
        "数学": "M",
        "语文": "Y",
        "英语": "E",
        "地理": "D",
        "政治": "P",
        "书法": "S",
    }
    tag_prefix = tag_prefix_map.get(subject, "X")

    prompt = MOTHER_PROBLEM_PROMPT.format(
        subject=subject, theme=theme,
        subject_en=subject_en,
        chain_id_prefix=chain_id_prefix,
        tag_prefix=tag_prefix,
    )

    client = ZhipuAI(api_key=api_key)
    for retry in range(2):
        try:
            response = client.chat.completions.create(
                model="glm-4-flash",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=3000,
            )
            content = response.choices[0].message.content
            m = re.search(r"\{.*\}", content, re.DOTALL)
            if not m:
                print(f"  ERROR: 未返回 JSON, 内容前 200: {content[:200]}", file=sys.stderr)
                continue
            try:
                card = json.loads(m.group(0))
                return card
            except json.JSONDecodeError as e:
                print(f"  WARN: JSON 解析失败 (retry {retry+1}): {e}", file=sys.stderr)
                # 修复常见转义问题: \\ 替换
                fixed = m.group(0).replace("\\\\", "\\")
                try:
                    card = json.loads(fixed)
                    print(f"  OK: 修复转义后成功", file=sys.stderr)
                    return card
                except Exception as e2:
                    print(f"  ERROR: 修复后仍失败: {e2}", file=sys.stderr)
                    continue
        except Exception as e:
            print(f"ERROR: API 调用失败 (retry {retry+1}): {e}", file=sys.stderr)
            time.sleep(2)
    return {}


def gen_one(args) -> int:
    """生成 1 张母题"""
    api_key = args.api_key or get_api_key()
    if not api_key:
        print("ERROR: 缺少 API key", file=sys.stderr)
        return 1

    subject_en, code = SUBJECT_CODE_MAP[args.subject]

    # 推断编号: 找目录下最大编号 + 1
    subject_dir = Path(rf"D:\4_data\knowledge_cards\{args.subject}\4step\parent_problems")
    existing = list(subject_dir.glob(f"{code}_*.json")) if subject_dir.exists() else []
    max_n = 0
    for f in existing:
        m = re.search(r"_(\d{3})_", f.name)
        if m:
            max_n = max(max_n, int(m.group(1)))
    next_n = max_n + 1

    # 生成母题主题拼音 (简化为英文)
    theme_pinyin = re.sub(r"[^a-zA-Z\u4e00-\u9fff]", "", args.theme)
    if not theme_pinyin:
        theme_pinyin = "general"

    print(f"生成: {code}_{next_n:03d} (主题: {args.theme})")
    card = call_glm4_flash(args.subject, args.theme, api_key)
    if not card:
        return 1

    # 强制设置 id 和 chain_id
    card_id = f"{code}_{next_n:03d}"
    card["id"] = card_id
    # chain_id 自动补全
    if not card.get("chain_id") or card.get("chain_id") == f"{subject_en}/xxx":
        card["chain_id"] = f"{subject_en}/{args.theme[:20]}"
    # display_target
    if "display_target" not in card:
        card["display_target"] = ["学习中心"]
    # 通用字段
    card.setdefault("card_type", "parent_problem")
    card.setdefault("subject", subject_en)
    card.setdefault("difficulty", "中")
    card.setdefault("frequency", "高频")
    card.setdefault("source_type", "改编")
    card.setdefault("_created_by", "v1.0 母题 batch gen (GLM-4-flash)")

    out_path = args.output or (subject_dir / f"{card_id}_{theme_pinyin[:20]}.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(card, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  写入: {out_path}")
    return 0


def batch(args) -> int:
    """单学科批量"""
    api_key = args.api_key or get_api_key()
    if not api_key:
        print("ERROR: 缺少 API key", file=sys.stderr)
        return 1

    themes = SUBJECT_MOTHER_PROBLEMS.get(args.subject, [])
    if args.count:
        themes = themes[:args.count]

    print(f"批量生成: 学科={args.subject}, 主题数={len(themes)}")
    print()
    rc = 0
    for i, theme in enumerate(themes, 1):
        print(f"[{i}/{len(themes)}] {theme}:")
        class Args:
            pass
        a = Args()
        a.subject = args.subject
        a.theme = theme
        a.api_key = api_key
        a.output = None
        rc = max(rc, gen_one(a))
        print()
        time.sleep(1)
    return rc


def batch_all(args) -> int:
    """5 学科批量"""
    subjects = list(SUBJECT_MOTHER_PROBLEMS.keys())
    print(f"5 学科批量: {len(subjects)} 学科")
    rc = 0
    for subj in subjects:
        print(f"\n=== {subj} ===")
        class Args:
            pass
        a = Args()
        a.subject = subj
        a.count = args.count
        a.api_key = args.api_key
        rc = max(rc, batch(a))
    return rc


def main():
    parser = argparse.ArgumentParser(
        description="5 学科母题批量生产工具 v1.0 (GLM-4-flash)"
    )
    subparsers = parser.add_subparsers(dest="command")

    p_gen = subparsers.add_parser("gen", help="单张生成")
    p_gen.add_argument("--subject", required=True, choices=list(SUBJECT_MOTHER_PROBLEMS.keys()))
    p_gen.add_argument("--theme", required=True)
    p_gen.add_argument("--output", "-o")
    p_gen.add_argument("--api-key")
    p_gen.set_defaults(func=gen_one)

    p_batch = subparsers.add_parser("batch", help="单学科批量")
    p_batch.add_argument("--subject", required=True, choices=list(SUBJECT_MOTHER_PROBLEMS.keys()))
    p_batch.add_argument("--count", type=int)
    p_batch.add_argument("--api-key")
    p_batch.set_defaults(func=batch)

    p_ba = subparsers.add_parser("batch-all", help="5 学科批量")
    p_ba.add_argument("--count", type=int, help="每学科限制数")
    p_ba.add_argument("--api-key")
    p_ba.set_defaults(func=batch_all)

    args = parser.parse_args()
    if not hasattr(args, "func"):
        parser.print_help()
        return 0
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
