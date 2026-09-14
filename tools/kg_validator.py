"""
知识图谱 v1.0 validator
=======================
检查 JSON schema, 节点/边完整性, 母题/策略链引用有效性.
"""
import json
import sys
from pathlib import Path
from collections import Counter


def load_graph(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate(graph: dict, knowledge_root: Path) -> list[str]:
    errors = []
    # 1. 必备字段
    for k in ["schema_version", "graph_id", "subject", "nodes", "edges"]:
        if k not in graph:
            errors.append(f"缺少必备字段: {k}")
    if errors:
        return errors

    # 2. 节点 ID 唯一
    node_ids = [n["id"] for n in graph.get("nodes", [])]
    if len(node_ids) != len(set(node_ids)):
        errors.append("节点 ID 重复")
    dup_ids = [i for i, c in Counter(node_ids).items() if c > 1]
    if dup_ids:
        errors.append(f"节点 ID 重复: {dup_ids}")

    # 3. 边引用节点存在
    node_set = set(node_ids)
    for e in graph.get("edges", []):
        if e["from"] not in node_set:
            errors.append(f"边引用不存在的节点: {e['from']}")
        if e["to"] not in node_set:
            errors.append(f"边引用不存在的节点: {e['to']}")

    # 4. 母题引用存在
    subj = graph.get("subject", "数学")
    subj_path = knowledge_root / subj / "4step" / "parent_problems"
    if not subj_path.exists():
        errors.append(f"学科目录不存在: {subj_path}")
    else:
        def _id(p):
            parts = p.stem.split("_")
            return "_".join(parts[:2]) if len(parts) >= 2 else p.stem
        all_pp = set()
        for prefix in ["pp_", "hp_", "ch_", "en_", "geo_", "pol_", "cal_"]:
            for p in subj_path.glob(f"{prefix}*.json"):
                all_pp.add(_id(p))
        for n in graph.get("nodes", []):
            for pp in n.get("mother_problems", []):
                if pp not in all_pp:
                    errors.append(f"节点 {n['id']} 引用不存在的母题: {pp}")

    # 5. 策略链引用存在 (接受 card_id 或 chain_id)
    strat_path = knowledge_root / "策略" / subj
    if strat_path.exists():
        existing_card_ids = set()
        existing_chain_ids = set()
        for p in strat_path.glob("*.json"):
            try:
                d = json.loads(p.read_text(encoding="utf-8"))
                existing_card_ids.add(d.get("card_id", p.stem))
                existing_chain_ids.add(d.get("chain_id", ""))
            except Exception:
                pass
        for n in graph.get("nodes", []):
            for sc in n.get("strategy_chains", []):
                if sc not in existing_card_ids and sc not in existing_chain_ids:
                    errors.append(f"节点 {n['id']} 引用不存在的策略链: {sc}")

    # 6. 前驱/后继一致性
    for n in graph.get("nodes", []):
        nid = n["id"]
        for pre in n.get("prerequisites", []):
            if pre not in node_set:
                errors.append(f"节点 {nid} prereq 引用不存在节点: {pre}")
        for suc in n.get("successors", []):
            if suc not in node_set:
                errors.append(f"节点 {nid} successor 引用不存在节点: {suc}")

    return errors


def main():
    if len(sys.argv) < 2:
        print("用法: kg_validator.py <graph.json> [knowledge_root]")
        sys.exit(1)
    graph_path = Path(sys.argv[1])
    knowledge_root = Path(sys.argv[2] if len(sys.argv) > 2 else r"D:\4_data\knowledge_cards")
    if not graph_path.exists():
        print(f"图谱文件不存在: {graph_path}")
        sys.exit(1)
    graph = load_graph(graph_path)
    print(f"=== {graph.get('graph_id', '?')} 验证 ===")
    print(f"节点: {len(graph.get('nodes', []))}, 边: {len(graph.get('edges', []))}")
    errors = validate(graph, knowledge_root)
    if errors:
        print(f"\n[FAIL] {len(errors)} errors:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    print("\n[PASS] all checks ok")
    sys.exit(0)


if __name__ == "__main__":
    main()
