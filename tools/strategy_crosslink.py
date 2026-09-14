"""
4 步法母题 ↔ 策略卡 互引工具 v1.0
=====================================
基于 chain_id 关键词 + method_tag 智能匹配, 自动给母题加 applicable_strategies 字段,
同时回填策略卡的 original_problem_id 字段.

宇兄端开发, 雪薇端可用.

用法:
  # 1. 互引 (扫所有母题 + 策略卡, 双向回填)
  python strategy_crosslink.py crosslink --root D:\4_data\knowledge_cards

  # 2. 仅扫描母题, 看匹配结果
  python strategy_crosslink.py scan --root D:\4_data\knowledge_cards

  # 3. 统计报告
  python strategy_crosslink.py report --root D:\4_data\knowledge_cards
"""
import argparse
import json
import re
import sys
from pathlib import Path
from typing import Optional


# 策略链 → 关键词映射 (基于 method_tag / chain_id 关键词)
# v1.1: 关键词更细, 避免一词匹配所有题
STRATEGY_KEYWORDS = {
    # 数学 - 关键词更细, 避免一词匹配所有题
    "math_strategy_graphing": ["数形结合", "抛物线", "几何画图", "图象交点", "函数图象", "画图法", "顶点在区间内", "端点函数值"],
    "math_strategy_discussion": ["分类讨论", "分情况", "绝对值", "分段函数", "含参方程", "分区间", "分类型", "讨论轴"],
    "math_strategy_equation": ["列方程", "设未知数", "应用题", "工程问题", "行程问题", "等量关系", "利润问题"],
    "math_strategy_function_equation": ["函数零点", "交点个数", "f(x)=g(x)", "零点个数", "函数图象交点"],
    "math_strategy_guihua": ["化归思想", "导数", "不等式证明", "压轴题", "陌生题", "辅助函数", "构造法"],
    "math_strategy_special_value": ["特殊值法", "排除法", "选择题", "代入验证", "选项排除"],
    "math_strategy_vector": ["向量法", "向量", "建系", "空间向量", "异面直线", "异面", "立体几何", "立体几何大题", "法向量", "点面距", "建坐标系", "面面垂直", "线面垂直", "二面角"],
    "math_strategy_parameter": ["参数分离", "恒成立", "有解", "参数范围", "分离参数法", "a 的取值范围"],
    # 语文
    "chinese_strategy_poetry": ["古诗", "意象", "意境", "情感", "鉴赏", "古诗词", "诗画关系"],
    "chinese_strategy_classical": ["文言文断句", "虚词", "对仗", "文言实词", "翻译", "词类活用"],
    "chinese_strategy_modern_reading": ["现代文阅读", "主旨大意", "细节理解", "推断", "词句含义", "作用分析", "说明文议论文记叙文"],
    "chinese_strategy_essay": ["高考作文", "议论文", "立意", "素材", "引议联结", "审题", "结构模板"],
    "chinese_strategy_character": ["字音字形", "成语辨析", "病句修改", "基础知识", "形近字", "多音字"],
    # 英语
    "english_strategy_reading": ["阅读理解", "主旨", "细节", "推断", "NOT", "EXCEPT", "词义猜测", "同义替换"],
    "english_strategy_cloze": ["完形填空", "上下文推断", "主题词", "前后呼应"],
    "english_strategy_writing": ["应用文", "邀请信", "建议信", "通知", "演讲稿", "模板", "高级词汇"],
    "english_strategy_grammar": ["语法填空", "时态", "词性", "虚拟语气", "非谓语动词", "主谓一致"],
    "english_strategy_long_sentence": ["长难句", "从句", "非谓语", "主句", "五步切分"],
    # 历史
    "history_strategy_causality": ["因果分析", "原因", "4 角度", "政治经济思想对外", "唯物史观"],
    "history_strategy_timeline": ["时序定位", "时间线", "阶段", "1840", "转折", "朝代演变", "5 阶段"],
    "history_strategy_material": ["史料解读", "材料分析", "一手二手", "信息提取", "一分材料一分结论"],
    "history_strategy_comparison": ["比较异同", "中英", "中俄", "中日", "同时不同地", "5 维度对比"],
    "history_strategy_period_feature": ["阶段特征", "明清", "唐朝", "宋", "朝代综述", "5 维度"],
    # 地理
    "geo_strategy_isopleth": ["等值线判读", "等温线", "等压线", "等高线", "密集区", "判读 5 步"],
    "geo_strategy_location": ["经纬定位", "5 维定位", "海陆位置", "大洲定位"],
    "geo_strategy_climate": ["气候类型", "5 因素", "纬度海陆", "洋流地形"],
    "geo_strategy_process": ["地理过程", "外力作用", "地貌形成", "侵蚀堆积", "流水风海冰"],
    "geo_strategy_compare_regions": ["区域比较", "南北方", "东西", "5 维度区域"],
    # 政治
    "politics_strategy_subject": ["主体分析", "国家企业个人", "时政结合", "两会", "十四五"],
    "politics_strategy_dialectics": ["矛盾分析", "两点论", "重点论", "主次矛盾", "绿水青山", "两山论"],
    "politics_strategy_value_judgment": ["价值判断", "核心价值观", "躺平", "价值选择"],
    "politics_strategy_politics_current": ["政治生活", "党的领导", "政府职能", "人大政协", "脱贫攻坚"],
    "politics_strategy_argument": ["政治小论文", "论据论证", "中国式现代化", "引-本-证-结"],
    # 书法
    "calligraphy_strategy_script": ["五体辨识", "篆隶楷行草", "书体特征", "笔法辨识"],
    "calligraphy_strategy_structural": ["结构 32 法", "主笔", "比例", "颜体", "欧体", "中宫"],
    "calligraphy_strategy_brush": ["永字八法", "中锋用笔", "藏锋", "提按顿挫", "行笔节奏"],
    "calligraphy_strategy_history": ["书法史", "王羲之", "兰亭序", "书圣", "颜真卿", "五朝代默写"],
}


def load_all_mother_problems(root: Path) -> list[dict]:
    """扫所有 4 步法母题 (按学科 4step/parent_problems/)"""
    problems = []
    for subject in ["数学", "语文", "英语", "历史", "地理", "政治", "书法"]:
        sub_root = root / subject / "4step" / "parent_problems"
        if not sub_root.exists():
            continue
        for f in sub_root.glob("*.json"):
            try:
                p = json.loads(f.read_text(encoding="utf-8"))
                p["_file"] = str(f)
                p["_subject"] = subject
                problems.append(p)
            except Exception as e:
                print(f"  WARN: {f.name}: {e}", file=sys.stderr)
    return problems


def load_all_strategy_cards(root: Path) -> list[dict]:
    """扫所有策略卡 (按学科 策略/<subject>/)"""
    strategies = []
    strat_root = root / "策略"
    if not strat_root.exists():
        return strategies
    for subject_dir in strat_root.iterdir():
        if not subject_dir.is_dir():
            continue
        for f in subject_dir.glob("*.json"):
            try:
                s = json.loads(f.read_text(encoding="utf-8"))
                s["_file"] = str(f)
                s["_subject_dir"] = subject_dir.name
                strategies.append(s)
            except Exception as e:
                print(f"  WARN: {f.name}: {e}", file=sys.stderr)
    return strategies


# method_tag 前缀 → 必推荐策略 (v1.1 智能映射)
METHOD_TAG_RULES = {
    # 数学 method_tag 前缀 (G-/G1-/G2-/T-/T1-/V-/P-/M-/F-/S-/A-/X-)
    "G1-": ["math_strategy_vector"],            # 中位线法 → 向量
    "G2-": ["math_strategy_vector", "math_strategy_graphing"],  # 平行四边形法 → 向量+数形
    "G-": ["math_strategy_vector", "math_strategy_graphing"],   # 几何方法 → 向量+数形
    "T1-": ["math_strategy_vector", "math_strategy_graphing"],  # 面面平行升级 → 向量+数形
    "T-": ["math_strategy_vector", "math_strategy_graphing"],   # 建系/坐标法
    "V-": ["math_strategy_vector", "math_strategy_graphing"],   # 向量法
    "M-": ["math_strategy_vector", "math_strategy_guihua"],     # 辅助线 → 向量+化归
    "F-": ["math_strategy_graphing", "math_strategy_function_equation"],  # 函数法
    "S-": ["math_strategy_special_value", "math_strategy_discussion"],   # 选择题/特殊值
    "A-": ["math_strategy_equation", "math_strategy_graphing"],   # 应用题 → 方程
    "P-": ["math_strategy_parameter", "math_strategy_discussion"],  # 参数问题
    "X-": ["math_strategy_discussion"],   # 讨论/分类
    # 历史 method_tag 前缀 (C-/M-/T-/W-)
    "C-": ["history_strategy_causality", "history_strategy_period_feature"],  # 因果/特征
    "M-": ["history_strategy_timeline", "history_strategy_period_feature"],   # 时序
    "T-": ["history_strategy_comparison", "history_strategy_period_feature"],  # 比较
    "W-": ["history_strategy_material", "history_strategy_timeline"],  # 文字/材料
    # 语文 method_tag 前缀 (Y-) → 5 策略链全映射
    "Y-": [
        "chinese_strategy_poetry", "chinese_strategy_classical",
        "chinese_strategy_modern_reading", "chinese_strategy_essay",
        "chinese_strategy_character",
    ],
    # 英语 method_tag 前缀 (E-) → 5 策略链全映射
    "E-": [
        "english_strategy_reading", "english_strategy_cloze",
        "english_strategy_writing", "english_strategy_grammar",
        "english_strategy_long_sentence",
    ],
    # 地理 method_tag 前缀 (D-) → 5 策略链全映射
    "D-": [
        "geo_strategy_isopleth", "geo_strategy_location",
        "geo_strategy_climate", "geo_strategy_process",
        "geo_strategy_compare_regions",
    ],
    # 政治 method_tag 前缀 (P-) → 5 策略链全映射
    "P-": [
        "politics_strategy_subject", "politics_strategy_dialectics",
        "politics_strategy_value_judgment", "politics_strategy_politics_current",
        "politics_strategy_argument",
    ],
    # 书法 method_tag 前缀 (S-) → 4 策略链全映射
    "S-": [
        "calligraphy_strategy_script", "calligraphy_strategy_structural",
        "calligraphy_strategy_brush", "calligraphy_strategy_history",
    ],
}


def match_strategies_for_problem(p: dict, strategies: list[dict]) -> list[str]:
    """v1.1: method_tag 规则优先 + 关键词 fallback"""
    pp_id = p.get("id", "")
    pp_subject = p.get("_subject", "")
    method_tag = p.get("method_tag", "")
    concepts = " ".join(p.get("concepts_used", []))
    text = f"{pp_id} {method_tag} {concepts}".lower()

    matches = set()

    # 1. method_tag 规则优先 (按前缀)
    for prefix, rule_strategies in METHOD_TAG_RULES.items():
        if method_tag.startswith(prefix):
            for s in strategies:
                chain = s.get("chain_id", "")
                if chain in rule_strategies and pp_subject == s.get("_subject_dir", ""):
                    matches.add(s.get("card_id", Path(s["_file"]).stem))

    # 2. 关键词 fallback (补充)
    for s in strategies:
        chain = s.get("chain_id", "")
        if pp_subject != s.get("_subject_dir", ""):
            continue
        keywords = STRATEGY_KEYWORDS.get(chain, [])
        if any(kw.lower() in text for kw in keywords):
            matches.add(s.get("card_id", Path(s["_file"]).stem))

    return list(matches)


def crosslink(args) -> int:
    # 强制 stdout UTF-8
    import io, sys
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

    root = Path(args.root)
    print(f"互引: 母题 <-> 策略卡 ({root})")
    print()

    problems = load_all_mother_problems(root)
    strategies = load_all_strategy_cards(root)
    print(f"扫到 {len(problems)} 张母题, {len(strategies)} 张策略卡")
    print()

    # 1. 给每张母题添加 applicable_strategies 字段
    p_modified = 0
    for p in problems:
        matches = match_strategies_for_problem(p, strategies)
        if matches:
            # 保留原有 applicable_strategies (如有), 追加
            old = p.get("applicable_strategies", [])
            new_list = list(set(old + matches))
            if set(old) != set(new_list):
                p["applicable_strategies"] = new_list
                # 写回文件
                Path(p["_file"]).write_text(
                    json.dumps(p, ensure_ascii=False, indent=2),
                    encoding="utf-8"
                )
                p_modified += 1

    # 2. 给每张策略卡回填 original_problem_id
    s_modified = 0
    for s in strategies:
        chain = s.get("chain_id", "")
        strategy_id = s.get("card_id", Path(s["_file"]).stem)
        # 找引用此策略的母题
        related_pp_ids = []
        for p in problems:
            if strategy_id in p.get("applicable_strategies", []):
                related_pp_ids.append(p.get("id", ""))
        if related_pp_ids:
            old = s.get("original_problem_id", "")
            old_list = [x.strip() for x in old.split(",") if x.strip()] if old else []
            new_list = list(set(old_list + related_pp_ids))
            new_str = ", ".join(sorted(new_list))
            if new_str != old:
                s["original_problem_id"] = new_str
                Path(s["_file"]).write_text(
                    json.dumps(s, ensure_ascii=False, indent=2),
                    encoding="utf-8"
                )
                s_modified += 1

    print(f"双向回填: 母题 {p_modified} 张 + 策略 {s_modified} 张")
    print(f"  互引后:")
    n_with = sum(1 for p in problems if p.get("applicable_strategies"))
    print(f"  - 母题含 applicable_strategies: {n_with}/{len(problems)}")
    return 0


def scan(args) -> int:
    import io, sys
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

    root = Path(args.root)
    problems = load_all_mother_problems(root)
    strategies = load_all_strategy_cards(root)
    print(f"扫到 {len(problems)} 张母题, {len(strategies)} 张策略卡")
    print()
    print("=== 母题匹配结果 (前 10) ===")
    for p in problems[:10]:
        pp_id = p.get("id", "?")
        method_tag = p.get("method_tag", "?")
        matches = match_strategies_for_problem(p, strategies)
        print(f"  {pp_id:50} | {method_tag:15} | 匹配: {matches}")
    return 0


def report(args) -> int:
    import io, sys
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

    root = Path(args.root)
    problems = load_all_mother_problems(root)
    strategies = load_all_strategy_cards(root)
    print(f"=== 互引报告 ===")
    print(f"母题: {len(problems)} 张")
    print(f"策略卡: {len(strategies)} 张")
    print()

    # 统计
    n_with = sum(1 for p in problems if p.get("applicable_strategies"))
    n_with_5 = sum(1 for p in problems if len(p.get("applicable_strategies", [])) >= 2)
    n_with_0 = len(problems) - n_with
    print(f"母题含 applicable_strategies: {n_with} ({n_with * 100 // max(1, len(problems))}%)")
    print(f"  - 0 关联: {n_with_0} 张")
    print(f"  - 1 关联: {n_with - n_with_5} 张")
    print(f"  - 2+ 关联: {n_with_5} 张")

    s_with_pp = sum(1 for s in strategies if s.get("original_problem_id"))
    print(f"\n策略卡含 original_problem_id: {s_with_pp}/{len(strategies)}")

    # 平均
    if problems:
        avg = sum(len(p.get("applicable_strategies", [])) for p in problems) / len(problems)
        print(f"\n平均每张母题关联策略数: {avg:.2f}")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="4 步法母题 ↔ 策略卡 互引工具 v1.0"
    )
    subparsers = parser.add_subparsers(dest="command")
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--root", default=r"D:\4_data\knowledge_cards", help="卡库根目录")

    p_x = subparsers.add_parser("crosslink", parents=[common], help="双向回填")
    p_x.set_defaults(func=crosslink)
    p_s = subparsers.add_parser("scan", parents=[common], help="扫描匹配")
    p_s.set_defaults(func=scan)
    p_r = subparsers.add_parser("report", parents=[common], help="统计报告")
    p_r.set_defaults(func=report)

    args = parser.parse_args()
    if not hasattr(args, "func"):
        parser.print_help()
        return 0
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
