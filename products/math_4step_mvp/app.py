"""
4 步法网页版 MVP - Flask 后端 + 知识图谱 + path_finder 集成 (P0-B.4 收官)
====================================
W3 网页版骨架 + kg 路由 (/kg, /kg/<id>) + API (/api/path_finder)
启动: python app.py  → http://127.0.0.1:5050
"""

import json
import subprocess
from pathlib import Path
from flask import Flask, render_template, jsonify, request, abort

APP_ROOT = Path(__file__).parent
KB_ROOTS = {
    "math": Path(r"D:\4_data\knowledge_cards\数学\4step"),
    "history": Path(r"D:\4_data\knowledge_cards\历史\4step"),
}
KB_CARDS = Path(r"D:\4_data\knowledge_cards\数学\cards")  # 数学 chain 根目录 (历史 chain 在历史/cards)
KG_DIR = Path(r"D:\2_products\education\SPDT-004_EduContent\knowledge_graphs")
PATH_FINDER_TOOL = Path(r"D:\2_products\education\SPDT-004_EduContent\tools\kg_path_finder.py")

app = Flask(__name__, template_folder=str(APP_ROOT / "templates"), static_folder=str(APP_ROOT / "static"))


def _load_json_files(folder: Path) -> list[dict]:
    if not folder.exists():
        return []
    return [json.loads(p.read_text(encoding="utf-8")) for p in folder.glob("*.json")]


def _find_by_id(folder: Path, target_id: str) -> dict | None:
    """通过 JSON 内部 'id' 字段扫描查找（不依赖文件名）"""
    if not folder.exists():
        return None
    # 短 ID 支持: pp_001 / concept_001 / var_001 / hp_001 可匹配以该前缀开头的任意 ID
    is_short_id = bool(target_id) and (
        target_id.replace("_", "").isdigit()
        or (target_id.startswith(("pp_", "var_", "concept_", "hp_")) and len(target_id) <= 8)
    )
    for p in folder.glob("*.json"):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            full_id = data.get("id", "")
            if full_id == target_id:
                return data
            if is_short_id and full_id.startswith(target_id):
                return data
        except (json.JSONDecodeError, OSError):
            continue
    return None


def _find_across_subjects(folder_type: str, target_id: str) -> dict | None:
    """跨学科查找 (math / history)"""
    for subject, root in KB_ROOTS.items():
        folder = root / folder_type
        data = _find_by_id(folder, target_id)
        if data:
            return data
    return None


def _index_cards() -> dict:
    """建立卡片索引: 概念/母题/变形 + chain 列表 (跨学科)"""
    cards = {"concepts": [], "parent_problems": [], "variants": []}
    for subject, root in KB_ROOTS.items():
        for ctype in ("concepts", "parent_problems", "variants"):
            cards[ctype].extend(_load_json_files(root / ctype))
    return cards


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/browse")
def browse():
    chain_id = request.args.get("chain")
    cards = _index_cards()
    chains = sorted({c["chain_id"] for cat in cards.values() for c in cat})
    return render_template("browse.html", cards=cards, chains=chains, current_chain=chain_id)


@app.route("/learn/<pp_id>")
def learn(pp_id: str):
    """学习流：母题 → 变形训练 (跨学科: 数学 pp_/历史 hp_)"""
    pp = _find_across_subjects("parent_problems", pp_id)
    if not pp:
        abort(404)
    # 变形: 跨学科找 (按 parent_id 匹配)
    variants = []
    for subject, root in KB_ROOTS.items():
        variants.extend([v for v in _load_json_files(root / "variants") if v.get("parent_id") == pp_id])
    return render_template("learn.html", pp=pp, variants=variants)


@app.route("/verify")
def verify():
    """验收模式: ?id=concept_xxx (query 参数支持中文 ID, 跨学科)"""
    concept_id = request.args.get("id")
    if not concept_id:
        abort(400, "missing id")
    concept = _find_across_subjects("concepts", concept_id)
    if not concept:
        abort(404)
    return render_template("verify.html", concept=concept)


@app.route("/api/concept")
def api_concept():
    concept_id = request.args.get("id")
    if not concept_id:
        return jsonify({"error": "missing id"}), 400
    data = _find_across_subjects("concepts", concept_id)
    return jsonify(data) if data else (jsonify({"error": "not found"}), 404)


@app.route("/api/pp")
def api_pp():
    pp_id = request.args.get("id")
    if not pp_id:
        return jsonify({"error": "missing id"}), 400
    data = _find_across_subjects("parent_problems", pp_id)
    return jsonify(data) if data else (jsonify({"error": "not found"}), 404)


@app.route("/api/variant")
def api_variant():
    var_id = request.args.get("id")
    if not var_id:
        return jsonify({"error": "missing id"}), 400
    data = _find_across_subjects("variants", var_id)
    return jsonify(data) if data else (jsonify({"error": "not found"}), 404)


# ===== P0-B.4: 知识图谱 + path_finder 集成 =====

def _list_kg_graphs() -> list[dict]:
    """列出所有 kg JSON"""
    if not KG_DIR.exists():
        return []
    out = []
    for p in sorted(KG_DIR.glob("*.json")):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
            out.append({
                "filename": p.name,
                "graph_id": d.get("graph_id", p.stem),
                "subject": d.get("subject", "?"),
                "node_count": len(d.get("nodes", [])),
                "edge_count": len(d.get("edges", [])),
                "scope": d.get("scope", "")[:60],
            })
        except Exception:
            continue
    return out


def _load_kg_graph(graph_id: str) -> dict | None:
    p = KG_DIR / f"{graph_id}.json"
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


@app.route("/kg")
def kg_list():
    """知识图谱列表"""
    graphs = _list_kg_graphs()
    return render_template("kg_list.html", graphs=graphs)


@app.route("/kg/<graph_id>")
def kg_view(graph_id):
    """知识图谱详情"""
    graph = _load_kg_graph(graph_id)
    if not graph:
        abort(404, f"graph not found: {graph_id}")
    return render_template("kg_view.html", graph=graph)


@app.route("/api/path_finder")
def api_path_finder():
    """调用 kg_path_finder 工具的 wrapper"""
    graph_id = request.args.get("graph", "multi_subject_kg_v1.0")
    mode = request.args.get("mode", "recommend")
    known = request.args.get("known", "")
    top = request.args.get("top", "10")
    fr = request.args.get("from", "")
    to = request.args.get("to", "")

    cmd = ["python", str(PATH_FINDER_TOOL), mode, "--graph", graph_id]
    if mode == "recommend":
        cmd += ["--known", known, "--top", top]
    elif mode == "path":
        cmd += ["--from", fr, "--to", to]
    elif mode == "journey":
        cmd += ["--known", known]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30,
                                encoding="utf-8", errors="replace")
        return jsonify({
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
        })
    except subprocess.TimeoutExpired:
        return jsonify({"error": "timeout"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5050, host="127.0.0.1")
