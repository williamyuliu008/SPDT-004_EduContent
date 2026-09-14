"""
知识图谱 path_finder v1.0
==========================
基于 knowledge_graphs/<graph_id>.json, 给定已掌握概念 → 推荐下一步学习路径.

用法:
  # 列出所有 in_library 概念
  python kg_path_finder.py list --graph multi_subject_kg_v1.0

  # 推荐下一步 (基于已掌握概念)
  python kg_path_finder.py recommend --graph multi_subject_kg_v1.0 --known concept_C1,concept_C2

  # 找从起点到目标的最短路径
  python kg_path_finder.py path --graph multi_subject_kg_v1.0 --from concept_C1 --to concept_C5

  # 学习路径推荐 (基于已掌握, 推荐一条完整路径)
  python kg_path_finder.py journey --graph multi_subject_kg_v1.0 --known concept_C1
"""
import argparse
import io
import json
import sys
from collections import deque
from pathlib import Path

# 强制 UTF-8 stdout (Windows GBK 兼容)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

KG_DIR = Path(r"D:\2_products\education\SPDT-004_EduContent\knowledge_graphs")


def load_graph(graph_id: str) -> dict:
    p = KG_DIR / f"{graph_id}.json"
    if not p.exists():
        # 尝试加 v1.0
        p2 = KG_DIR / f"{graph_id}_v1.0.json"
        if p2.exists():
            p = p2
        else:
            print(f"图谱不存在: {graph_id}", file=sys.stderr)
            sys.exit(1)
    return json.loads(p.read_text(encoding="utf-8"))


def build_adj(graph: dict) -> dict:
    """构建邻接表: node_id → [(target_id, edge_type, weight), ...]"""
    nodes = {n["id"]: n for n in graph.get("nodes", [])}
    adj = {nid: [] for nid in nodes}
    for e in graph.get("edges", []):
        f = e["from"]
        t = e["to"]
        if f in adj and t in adj:
            adj[f].append((t, e.get("type", "prerequisite"), e.get("weight", 1.0)))
    return adj, nodes


def list_cmd(args) -> int:
    graph = load_graph(args.graph)
    print(f"=== {graph.get('graph_id', args.graph)} ===")
    print(f"节点: {len(graph.get('nodes', []))}, 边: {len(graph.get('edges', []))}")
    print()
    print("ID                  | 状态        | 学科 | 名称")
    print("-" * 80)
    for n in graph.get("nodes", []):
        status = n.get("status", "?")
        subj = n.get("subject", "?")
        print(f'  {n["id"]:18s} | {status:11s} | {subj:4s} | {n.get("name", "?")}')
    return 0


def recommend_cmd(args) -> int:
    graph = load_graph(args.graph)
    adj, nodes = build_adj(graph)
    known = set(args.known.split(",")) if args.known else set()

    print(f"=== 推荐下一步 (基于已掌握 {len(known)} 概念) ===")
    print(f"已掌握: {known}")
    print()

    candidates = []
    for nid, node in nodes.items():
        if nid in known:
            continue
        if node.get("status") == "virtual":
            continue
        # 找 prereqs
        prereqs = node.get("prerequisites", [])
        unmet = [p for p in prereqs if p not in known]
        if not unmet and prereqs:  # 所有 prereqs 已掌握
            # 计算 score: prereqs 满足度 + chain 权重
            score = sum(adj[p][0][2] for p in prereqs if adj.get(p)) / max(len(prereqs), 1)
            candidates.append((nid, score, node))

    candidates.sort(key=lambda x: -x[1])

    if not candidates:
        print("  无可推荐概念 (所有 in_library 概念已掌握或 prereqs 不满足)")
        return 0

    print(f"Top {min(args.top, len(candidates))} 推荐:")
    for nid, score, node in candidates[:args.top]:
        print(f'  {nid:18s} | score={score:.2f} | {node.get("subject", "?")} {node.get("name", "?")}')
    return 0


def path_cmd(args) -> int:
    graph = load_graph(args.graph)
    adj, nodes = build_adj(graph)

    # BFS 找最短路径
    start, target = args.fr, args.to
    if start not in nodes or target not in nodes:
        print(f"节点不存在: {start} or {target}")
        return 1

    queue = deque([(start, [start])])
    visited = {start}
    while queue:
        cur, path = queue.popleft()
        if cur == target:
            print(f"=== 路径 ({len(path)-1} 跳) ===")
            for i, nid in enumerate(path):
                node = nodes[nid]
                print(f"  {i}. {nid:18s} | {node.get('subject','?')} {node.get('name','?')}")
            return 0
        for next_id, _, _ in adj.get(cur, []):
            if next_id not in visited:
                visited.add(next_id)
                queue.append((next_id, path + [next_id]))

    print(f"无路径从 {start} 到 {target}")
    return 1


def journey_cmd(args) -> int:
    """基于已掌握概念, 推荐一条完整学习路径"""
    graph = load_graph(args.graph)
    adj, nodes = build_adj(graph)
    known = set(args.known.split(",")) if args.known else set()

    # 1. 找所有未掌握 in_library 概念
    todo = [n["id"] for n in graph.get("nodes", []) if n["id"] not in known and n.get("status") == "in_library"]

    # 2. 拓扑排序: prereqs 在前
    in_degree = {nid: 0 for nid in todo}
    graph_sub = {nid: [] for nid in todo}
    for n in graph.get("nodes", []):
        if n["id"] in todo:
            for p in n.get("prerequisites", []):
                if p in todo:
                    graph_sub[p].append(n["id"])
                    in_degree[n["id"]] += 1

    # 3. Kahn's algorithm
    queue = deque([nid for nid in todo if in_degree[nid] == 0])
    journey = []
    while queue:
        nid = queue.popleft()
        journey.append(nid)
        for next_id in graph_sub[nid]:
            in_degree[next_id] -= 1
            if in_degree[next_id] == 0:
                queue.append(next_id)

    print(f"=== 学习路径 (基于已掌握 {len(known)} 概念, 待学 {len(journey)} 概念) ===")
    print(f"已掌握: {known}")
    print()
    for i, nid in enumerate(journey, 1):
        node = nodes.get(nid, {})
        print(f'  {i:2d}. {nid:18s} | {node.get("subject","?"):4s} {node.get("name","?")}')
    return 0


def main():
    parser = argparse.ArgumentParser(description="知识图谱 path_finder v1.0")
    sub = parser.add_subparsers(dest="cmd")

    p_list = sub.add_parser("list", help="列出所有概念")
    p_list.add_argument("--graph", required=True)

    p_rec = sub.add_parser("recommend", help="推荐下一步")
    p_rec.add_argument("--graph", required=True)
    p_rec.add_argument("--known", default="", help="已掌握概念 IDs (逗号分隔)")
    p_rec.add_argument("--top", type=int, default=10)

    p_path = sub.add_parser("path", help="两点间最短路径")
    p_path.add_argument("--graph", required=True)
    p_path.add_argument("--from", dest="fr", required=True)
    p_path.add_argument("--to", required=True)

    p_journey = sub.add_parser("journey", help="完整学习路径")
    p_journey.add_argument("--graph", required=True)
    p_journey.add_argument("--known", default="", help="已掌握概念 IDs")

    args = parser.parse_args()
    if not hasattr(args, "cmd") or args.cmd is None:
        parser.print_help()
        return 0
    fn = {"list": list_cmd, "recommend": recommend_cmd, "path": path_cmd, "journey": journey_cmd}[args.cmd]
    return fn(args)


if __name__ == "__main__":
    sys.exit(main())