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
STRATEGY_KEYWORDS = {
    # 数学
    "math_strategy_graphing": ["数形", "图象", "图", "抛物线", "几何画图"],
    "math_strategy_discussion": ["分类讨论", "讨论", "分情况", "区间", "绝对值", "分段"],
    "math_strategy_equation": ["方程", "列方程", "设", "解方程", "应用题"],
    "math_strategy_function_equation": ["函数零点", "函数与方程", "交点", "零点"],
    "math_strategy_guihua": ["化归", "转化", "导数", "不等式证明", "压轴"],
    "math_strategy_special_value": ["特殊值", "排除", "选择题", "代入"],
    "math_strategy_vector": ["向量", "建系", "立体几何", "异面", "垂直", "夹角"],
    "math_strategy_parameter": ["参数", "恒成立", "有解", "分离参数", "a 的范围"],
    # 语文
    "chinese_strategy_poetry": ["古诗", "意象", "意境", "情感", "鉴赏"],
    "chinese_strategy_classical": ["文言", "断句", "虚词", "对仗"],
    "chinese_strategy_modern_reading": ["现代文", "阅读", "主旨", "细节", "推断"],
    "chinese_strategy_essay": ["作文", "议论文", "立意", "结构", "素材"],
    "chinese_strategy_character": ["字音", "字形", "成语", "病句", "基础"],
    # 英语
    "english_strategy_reading": ["阅读", "主旨", "细节", "推断", "NOT", "EXCEPT"],
    "english_strategy_cloze": ["完形", "上下文", "推断"],
    "english_strategy_writing": ["写作", "应用文", "邀请信", "建议信", "模板"],
    "english_strategy_grammar": ["语法", "时态", "词性", "虚拟"],
    "english_strategy_long_sentence": ["长难句", "从句", "非谓语"],
    # 历史
    "history_strategy_causality": ["因果", "原因", "多角度", "4 角度"],
    "history_strategy_timeline": ["时序", "时间线", "阶段", "1840", "转折"],
    "history_strategy_material": ["材料", "史料", "解读", "信息提取"],
    "history_strategy_comparison": ["比较", "同", "异", "中英", "中俄", "中日"],
    "history_strategy_period_feature": ["阶段特征", "5 维", "明清", "唐朝", "宋"],
    # 地理
    "geo_strategy_isopleth": ["等值线", "判读", "等温", "等压", "等高"],
    "geo_strategy_location": ["经纬", "定位", "5 维"],
    "geo_strategy_climate": ["气候", "5 因素", "类型"],
    "geo_strategy_process": ["地理过程", "外力", "地貌", "侵蚀", "堆积"],
    "geo_strategy_compare_regions": ["区域比较", "南北方", "东西", "5 维"],
    # 政治
    "politics_strategy_subject": ["主体", "国家/企业/个人", "时政"],
    "politics_strategy_dialectics": ["矛盾", "两点论", "重点论", "绿水青山"],
    "politics_strategy_value_judgment": ["价值", "核心价值观", "躺平"],
    "politics_strategy_politics_current": ["政治生活", "党", "政府", "人大", "脱贫"],
    "politics_strategy_argument": ["小论文", "论据", "中国式现代化"],
    # 书法
    "calligraphy_strategy_script": ["五体", "篆隶楷行草", "辨识"],
    "calligraphy_strategy_structural": ["结构", "主笔", "比例", "32 法"],
    "calligraphy_strategy_brush": ["笔法", "永字八法", "中锋", "藏锋"],
    "calligraphy_strategy_history": ["书法史", "王羲之", "兰亭序", "书圣", "默写"],
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


def match_strategies_for_problem(p: dict, strategies: list[dict]) -> list[str]:
    """根据母题 chain_id + method_tag + concepts_used 匹配策略卡"""
    pp_id = p.get("id", "")
    pp_subject = p.get("_subject", "")
    method_tag = p.get("method_tag", "")
    concepts = " ".join(p.get("concepts_used", []))
    text = f"{pp_id} {method_tag} {concepts}".lower()

    matches = []
    for s in strategies:
        chain = s.get("chain_id", "")
        # 学科匹配
        if pp_subject != s.get("_subject_dir", ""):
            continue
        # 关键词匹配
        keywords = STRATEGY_KEYWORDS.get(chain, [])
        if any(kw.lower() in text for kw in keywords):
            # 提取策略卡 ID
            strategy_id = s.get("card_id", Path(s["_file"]).stem)
            matches.append(strategy_id)
    return matches


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
