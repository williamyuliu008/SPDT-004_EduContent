"""
PT-037 自适应备考智能体平台 — 主流程
"""

import json
import sys
import os
from pathlib import Path

PT_ROOT = Path(__file__).parent.parent
CORE = PT_ROOT / "_01_platform_core"

# 方案A: 将 _01_platform_core 作为 "platform_core" 包加入路径
# 重命名为不含数字前缀的包名
sys.path.insert(0, str(CORE))

# 同时创建软链接包（用于 platform_core.xxx 导入）
_platform_core_pkg = PT_ROOT / "platform_core"
if not _platform_core_pkg.exists():
    import os
    try:
        os.symlink(str(CORE), str(_platform_core_pkg), target_is_directory=True)
    except OSError:
        # Windows fallback: copy a __init__.py stub
        pass

from llm.llm_wrapper import create_llm_client
from knowledge_base.knowledge_base import KnowledgeBase
from agent_conductor.agent_conductor import AgentConductor, UserState
from agent_coach.agent_coach import AgentCoach
from agent_auditor.agent_auditor import AgentAuditor


# ─── 颜色打印 ───────────────────────────────────────────────────────────

C = {"h": "\033[95m", "b": "\033[94m", "c": "\033[96m",
     "g": "\033[92m", "y": "\033[93m", "r": "\033[91m",
     "bold": "\033[1m", "end": "\033[0m"}

def h(text): return f"{C['h']}{C['bold']}{text}{C['end']}"
def c(text): return f"{C['c']}{text}{C['end']}"
def g(text): return f"{C['g']}{text}{C['end']}"
def y(text): return f"{C['y']}{text}{C['end']}"
def r(text): return f"{C['r']}{text}{C['end']}"
def b(text): return f"{C['b']}{text}{C['end']}"


def divider(title: str = ""):
    line = "─" * 60
    if title:
        print(f"\n{h(line)}\n  {title}\n{h(line)}\n")
    else:
        print(f"\n{h(line)}\n")


def step(n: int, label: str, detail: str = ""):
    print(f"{c(f'  Step {n}')} {b(label)}")
    if detail:
        print(f"         {y(detail)}")
    print()


def run_mvp(llm_mode: str = "mock"):
    """MVP 端到端流程"""
    divider("PT-037 自适应备考智能体平台 — MVP 演示")

    # 1. 初始化
    step(1, "初始化组件")
    pack_path = PT_ROOT / "_03_subject_packs" / "cafa_calligraphy_2026"
    llm = create_llm_client(mode=llm_mode)
    kb = KnowledgeBase.from_pack(pack_path)
    conductor = AgentConductor(llm, kb)
    coach = AgentCoach(llm, kb)
    auditor = AgentAuditor(llm, kb)

    summary = kb.summary()
    print(f"    {g('✓')} 知识库：{summary['total_kb_entries']}条书法史 / "
          f"{summary['total_translation_entries']}组译篆 / "
          f"{summary['total_punctuation_texts']}篇句读 / "
          f"{summary['total_error_scripts']}条错题剧本")

    # 2. 用户状态
    step(2, "创建模拟用户状态")
    state = UserState(user_id="demo_001", S_score=55.0, C_cognitive_load=4.0,
                      F_fatigue=0.5, I_interest=6.0, pack_id="cafa_calligraphy_2026")
    for k, v in state.summary().items():
        if k != "user_id":
            print(f"       {k}: {v}")

    # 3. Agent5 调度
    step(3, "Agent5 调度决策")
    decision = conductor.decide(state)
    print(f"    {g('→')} 行动类型: {decision.action_type}")
    print(f"       目标Agent: {decision.target_agent}  优先级: {decision.priority}")
    print(f"       推理: {decision.reasoning}")
    print(f"       难度: {decision.scaffold_level}")
    if decision.content_spec.get("focus_kb_id"):
        print(f"       知识点: {decision.content_spec['focus_kb_id']} ({decision.content_spec.get('focus_concept','')})")

    # 4. Agent4 出题
    step(4, "Agent4 生成训练题")
    q = coach.generate_question(
        focus_kb_id=decision.content_spec.get("focus_kb_id"),
        difficulty=decision.scaffold_level,
        pack_id=state.pack_id
    )
    if "error" not in q:
        print(f"    {g('✓')} 题型: {q.get('question_type')}  难度: {q.get('difficulty')}")
        print(f"    {b('[题目]')} {y(q.get('text',''))}")
        if q.get("hints"):
            print(f"\n    {c('【提示】')} {' / '.join(q.get('hints',[]))}")
    else:
        print(f"    {r('✗')} {q.get('error')}")

    # 5. 模拟作答
    step(5, "模拟用户作答")
    user_answer_raw = q.get("correct_answer", "")
    if q.get("answer") and isinstance(q["answer"], dict):
        user_answer_raw = "\n".join(q["answer"].values())
    user_answer = str(user_answer_raw)  # 确保是字符串
    print(f"    答案: {y(user_answer[:80])}{'...' if len(user_answer)>80 else ''}")

    # 6. Agent4 评分
    step(6, "Agent4 评分")
    grading = coach.grade_answer(q, str(user_answer), kb.get_entry(q.get("kb_id")))
    status = g("正确 ✓") if grading.get("correct") else y("有误 ✗")
    print(f"    判定: {status}  得分: {grading.get('score',0)}/{grading.get('max_score',20)}")
    print(f"    反馈: {grading.get('feedback','')}")

    # 7. 更新状态
    step(7, "更新用户状态")
    state.update_from_answer(grading.get("correct", False), q.get("ability_id", "A5"))
    state.tick(decision.duration_minutes)
    print(f"    {g('状态变化:')} S={state.S_score:.1f}% | C={state.C_cognitive_load:.1f} | "
          f"F={state.F_fatigue:.1f} | I={state.I_interest:.1f}")

    # 8. Agent2 审计
    step(8, "Agent2 知识审计")
    entry = kb.get_entry(decision.content_spec.get("focus_kb_id", "KB_CAFA_S001"))
    if entry:
        audit = auditor.audit_entry(entry)
        v = audit["verdict"]
        v_color = g("PASS") if v == "PASS" else (y("NEED_REVISION") if v == "NEED_REVISION" else r("REJECT"))
        print(f"    审计: {v_color}  分数: {audit['score']}/{audit['max_score']}")
        for dim, res in audit.get("dimensions", {}).items():
            icon = g("✓") if "PASS" in res else r("✗")
            print(f"      {icon} {dim}: {res}")

    # 9. 下一轮
    step(9, "下一轮调度")
    next_d = conductor.decide(state)
    print(f"    下一轮: {next_d.action_type} | {next_d.reasoning}")

    # 10. 错题剧本
    if not grading.get("correct") and decision.content_spec.get("focus_kb_id"):
        step(10, "错题剧本")
        scripts = kb.get_error_script_by_kb(decision.content_spec["focus_kb_id"])
        if scripts:
            s = scripts[0]
            print(f"    剧本: {s.script_id} | {s.error_type}")
            print(f"    {r('错误')} {s.script.get('conflict','')}")
            print(f"    {g('正确')} {s.script.get('logic_chain','')[:60]}")
            print(f"    {c('口诀')} {s.script.get('mnemonic','')}")

    divider("MVP 完成 — 最终状态")
    for k, v in state.summary().items():
        print(f"    {k}: {v}")
    print(f"\n  {g('✅ PT-037 MVP 跑通！')}\n")


if __name__ == "__main__":
    import argparse, os
    # 自动读取 ZHIPU_API_KEY（如未设置）
    if not os.environ.get("ZHIPU_API_KEY"):
        api_key_path = Path("D:/_CEO/bulletin/SECRET_KEY/zhipu_api.txt")
        if api_key_path.exists():
            with open(api_key_path, "r", encoding="utf-8") as f:
                key = f.read().strip()
            os.environ["ZHIPU_API_KEY"] = key
            print(f"    {c('[auto]')} 已从 {api_key_path} 加载 ZHIPU_API_KEY")

    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["mock","glm","openai"],
                       default="glm" if os.environ.get("ZHIPU_API_KEY") else "mock")
    parser.add_argument("--api-key")
    args = parser.parse_args()
    if args.api_key:
        os.environ["ZHIPU_API_KEY"] = args.api_key

    run_mvp(llm_mode=args.mode)
