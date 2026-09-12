"""A2: 批量升 14 个母题为 v1.1 字段
- 自动从现有数据派生 problem_statement / given_conditions / intuition / thinking_path / key_insight
- 用占位 + heuristic 自动生成首版, 待人工/GLM 完善
- 保留 v1.0 字段, 兼容回退
"""
import json
import re
from pathlib import Path

PP_DIR = Path(r'D:\4_data\knowledge_cards\数学\4step\parent_problems')

# v1.0 → v1.1 自动派生规则
INTUITION_TEMPLATES = {
    "G1-中位线": "中位线法是立体几何最经典的'找平行'方法。母题的几何特征是'中点 + 平行四边形'，两条中点连线天然平行。",
    "G2-平行四边形": "平行四边形法证线面平行是'借图法'。底面是平行四边形时，对角线互相平分 ⇒ 中点 + 中位线。",
    "G-几何法/线面垂直判定": "线面垂直判定的关键是'面内两条相交线'。本题两条线一条来自底面（正方形对角线垂直），一条来自侧面（PA⊥底面传递）。",
    "G-几何法/三线合一": "等腰三角形三线合一是垂直问题的'几何本能'。看到中点 + 等腰条件，要条件反射想到'中线即高'。",
    "T-面面平行升级": "面面平行 = 两条相交线分别平行于另一面。本题把'线面平行'升级为'面面平行'，训练'升维'思维。",
    "T-面面垂直升级": "面面垂直 = 一个面内有线垂直于另一面。从'线面垂直'升级为'面面垂直'，找'关键线'是关键。",
    "G-几何法/平移": "平移法求异面角的精髓：异面不能直接相交，平移让它们交于一点，降维成平面几何。",
    "V-向量法/建系": "向量法求角的精髓：建系 + 坐标 + 套公式。比几何法'机械化'，但对建系要求高。",
    "G-几何法/三垂线": "三垂线法求线面角的关键：找线在面内的射影。射影线与原线所成锐角 = 线面角。",
    "G-几何法/等体积": "等体积法求点面距的精髓：换顶点求高。三棱锥 4 顶点任选，挑最易算的。",
    "G-几何法/射影": "几何法射影的精髓：找点在面内的射影。垂直传递性质是降维。",
    "V-向量法/法向量": "向量法求点面距：建系 + 法向量叉乘 + d = |向量·法向量|/|法向量|。",
    "G-几何法/割补": "割补法求体积的精髓：化未知为已知。把不规则拆成规则或补全成规则。",
    "G-几何法/特化公式": "正四面体是三棱锥最规则形式，所有公式现成：V=√2/12·a³, R=√6/4·a, r=√6/12·a。",
    "G-几何法/线面垂直判定": "线面垂直判定的关键是'面内两条相交线'。每条线必须显式论证垂直来源。",
}

INSIGHT_TEMPLATES = {
    "G1-中位线": "中位线 = 中点 + 平行线。本题图形是'正方体 + 顶面中点'，必须连 BD 找 AC 交点 O。",
    "G2-平行四边形": "平行四边形 = 对角线互相平分。找中点 → 中位线 → 平行。",
    "G-几何法/线面垂直判定": "两线相交 + 两线都垂直于目标线 ⇒ 目标线垂直于面。三要素缺一不可。",
    "G-几何法/三线合一": "等腰三角形的中线 = 高 = 角平分线。认中点 + 等腰 = 立刻想到'中线即高'。",
    "G-几何法/平移": "异面 = 不能交。平移 = 找平行的中介线，让它们交于一点。",
    "V-向量法/建系": "建系原则：'天然墙角' > '找底面垂线' > '基底法'。选最优。",
    "G-几何法/三垂线": "线面角 = 线与射影所成锐角。射影 = 找面内一点让线投影到面。",
    "G-几何法/等体积": "三棱锥 V = (1/3)·S·h，4 顶点任选。换顶点 = 换底 = 换高。",
    "V-向量法/法向量": "法向量叉乘：n1 × n2 = (y1z2-z1y2, z1x2-x1z2, x1y2-y1x2)。",
    "G-几何法/割补": "不规则体 = 规则体 ± 规则体。补 = 补全后减；割 = 拆开分别算。",
    "G-几何法/特化公式": "正四面体：a=V×(12/√2), R=V^(1/3)×(4/√6), r=V^(1/3)×(12/√6)。",
}


def extract_conditions_from_graph_bg(graph_bg: str) -> list[str]:
    """从 graph_bg 提取 given_conditions (heuristic 拆分)"""
    conds = []
    # 拆分逗号/分号
    parts = re.split(r'[，；。]', graph_bg)
    for p in parts:
        p = p.strip()
        if p and 3 < len(p) < 30:
            conds.append(p)
    return conds[:5]  # 最多 5 条


def auto_v11(pp: dict) -> dict:
    """从 v1.0 自动派生 v1.1 字段"""
    method_tag = pp.get("method_tag", "")
    chain_id = pp.get("chain_id", "")
    pp_id = pp.get("id", "")
    graph_bg = pp.get("graph_bg", "")
    goal = pp.get("goal", "")
    steps = pp.get("standard_steps", [])
    mistakes = pp.get("common_mistakes", [])

    # 1. problem_statement
    if graph_bg and goal:
        problem_statement = f"{graph_bg.rstrip('。')}.{goal.rstrip('。')}."
    else:
        problem_statement = pp.get("problem_statement", "")

    # 2. given_conditions
    given_conditions = extract_conditions_from_graph_bg(graph_bg)

    # 3. figure_description (从 graph_bg 提取)
    figure_description = graph_bg

    # 4. figure_ref
    figure_ref = f"figures/{pp_id.split('_')[0]}_{pp_id.split('_')[1] if '_' in pp_id else 'pp'}.svg"
    figure_type = "svg"

    # 5. intuition
    intuition = INTUITION_TEMPLATES.get(method_tag, f"本题是{chain_id}领域的母题，核心方法是{method_tag}。学生需理解核心方法的应用场景和操作步骤。")

    # 6. thinking_path
    if steps:
        thinking_path = "看到题目 → 识别题型 → 调用方法 → 按步骤推演 → 验证结论。核心步骤：" + "; ".join(steps[:3])
    else:
        thinking_path = "v1.1 待人工/GLM 补全"

    # 7. key_insight
    key_insight = INSIGHT_TEMPLATES.get(method_tag, f"核心方法{method_tag}的关键步骤见 standard_steps。")

    # 8. source_type / source_ref / original_problem_id
    source_type = "v1.0 改造"
    source_ref = "SPDT-004 4 步法 v1.0 起草"
    original_problem_id = None

    # 9. v1.1_added_fields 元数据
    v11_added = ["source_type", "source_ref", "original_problem_id", "problem_statement",
                 "given_conditions", "figure_description", "figure_ref", "figure_type",
                 "intuition", "thinking_path", "key_insight"]

    # merge
    pp_v11 = dict(pp)
    pp_v11.update({
        "source_type": source_type,
        "source_ref": source_ref,
        "original_problem_id": original_problem_id,
        "problem_statement": problem_statement,
        "given_conditions": given_conditions,
        "figure_description": figure_description,
        "figure_ref": figure_ref,
        "figure_type": figure_type,
        "intuition": intuition,
        "thinking_path": thinking_path,
        "key_insight": key_insight,
        "_v11_added_fields": v11_added,
        "_v11_auto_generated": True,
        "_v11_review_pending": True,
    })
    # 给 tags 加 v1.1
    tags = pp_v11.get("tags", [])
    if "v1.1" not in tags:
        tags = tags + ["v1.1"]
    pp_v11["tags"] = tags
    return pp_v11


def main():
    pp_files = sorted(PP_DIR.glob('pp_*.json'))
    print(f'Found {len(pp_files)} pp files')
    for p in pp_files:
        pp = json.loads(p.read_text(encoding='utf-8'))
        # 已 v1.1 跳过
        if pp.get("_v11_auto_generated") or pp.get("intuition"):
            print(f'  SKIP (already v1.1): {p.name}')
            continue
        pp_v11 = auto_v11(pp)
        # 写回（无 BOM）
        p.write_bytes(json.dumps(pp_v11, ensure_ascii=False, indent=2).encode('utf-8'))
        print(f'  upgraded: {p.name}')

if __name__ == "__main__":
    main()
