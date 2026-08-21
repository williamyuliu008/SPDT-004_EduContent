"""
layer_lint.py — SPDT-004 跨层依赖检查工具 v1.0
================================================

扫描所有 .py 文件，AST 解析 import 语句，检查是否违反分层规则。

LAYER 规则（详见 LAYERS.md §4）:
  L0 → (none，只依赖标准库 + 已批准的第三方)
  L1 → L0（通过暴露的接口）
  L2 → L0 / L1（通过暴露的接口）

违规类型：
  ❌ L0 import L1/L2 内部模块
  ❌ L1 import L2 内部模块
  ❌ 跨层 import 内部模块（只能通过 __init__.py 暴露的 API）

用法：
  python tools/layer_lint.py
  python tools/layer_lint.py --root D:/path/to/SPDT-004_EduContent
  python tools/layer_lint.py --json   # 输出 JSON 报告
  python tools/layer_lint.py --strict # 警告也升级为错误
"""
import ast
import io
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# ============================================================
# LAYER 配置（与 LAYERS.md 对齐）
# ============================================================

# 顶层目录 → 所属层
LAYER_MAP: Dict[str, str] = {
    "1_ingest": "L0",
    "quality": "L0",
    "templates": "L0",
    "knowledge_cards": "L0",  # 注：知识卡片工具链实际在 D:/4_data/knowledge_cards/_tools/
    "2_structure": "L1",  # 默认 L1（已产物在 L1；新扩产在 L2 标记）
    "3_render": "L1",
    "5_deliver": "L1",
    "autoclaw_kit": "L1",
    "skill_system": "L1",
    "4_adapt": "L2",
    "cross_pack": "L2",
    "古史_v4_世界风云": "L2",
    "墨骨山河_ep02-08": "L2",
    "墨骨山河_ep09": "L1",  # 已产物
    "墨骨山河_ep01": "L1",  # 已产物
    "古史_v1_革与鼎": "L1",
    "古史_v2_变与局": "L1",
    "古史_v3_共和新生": "L1",
}

# 跨层允许的 import 方向
ALLOWED_DEPENDENCIES: Dict[str, Set[str]] = {
    "L0": set(),  # L0 不依赖任何人
    "L1": {"L0"},
    "L2": {"L0", "L1"},
}

# 例外：L1 中明确允许 import 的 L0 子模块（通过 __init__.py 暴露的）
ALLOWED_L0_PUBLIC_MODULES = {
    "ingest_entry_judge",
    "ingest_syllabus_parser",
    "ingest_quality_calibrator",
}

# 第三方库白名单（允许 L0 依赖）
APPROVED_THIRD_PARTY = {
    "PyYAML", "yaml", "jsonschema", "pydantic", "requests", "urllib",
    "json", "os", "sys", "pathlib", "io", "re", "ast", "subprocess",
    "datetime", "time", "hashlib", "logging", "typing", "collections",
    "itertools", "functools", "argparse", "dataclasses", "enum",
    "PIL", "pillow", "numpy", "pandas", "matplotlib",  # 可视化类
}

# 跳过的目录（不扫描）
SKIP_DIRS = {
    ".git", ".hvigor", ".github", "__pycache__", "node_modules", "build",
    ".venv", "venv", "env", "dist", ".pytest_cache", ".mypy_cache",
    "tools",  # tools 自身是 orchestration，可横跨
    "docs",   # docs 是文档目录，不扫描
}

# ============================================================
# 路径 → LAYER 推断
# ============================================================

def detect_layer(path: Path, root: Path) -> Optional[str]:
    """根据文件路径推断所属层"""
    rel = path.relative_to(root).as_posix()
    parts = rel.split("/")
    if not parts:
        return None

    # 跳过隐藏/缓存目录
    for skip in SKIP_DIRS:
        if skip in parts:
            return None

    # 顶层目录查找
    top = parts[0]

    # _XX 编号子目录（如 _06_mvp_pipeline）属于父目录
    if top.startswith("_") and len(parts) > 1:
        top = parts[1]

    return LAYER_MAP.get(top)


def is_internal_module(imported: str) -> bool:
    """判断是否为项目内部模块（非第三方）"""
    if imported in APPROVED_THIRD_PARTY:
        return False
    # 相对 import（from .x import y）算内部
    if imported.startswith("."):
        return True
    # 项目内的绝对 import（以项目顶层目录开头）
    top_dirs = ["1_ingest", "2_structure", "3_render", "4_adapt", "5_deliver",
                "common", "knowledge", "quality", "templates", "tools"]
    return any(imported.startswith(d + ".") or imported == d for d in top_dirs)


# ============================================================
# AST 扫描
# ============================================================

def extract_imports(file_path: Path) -> List[Tuple[str, str, int]]:
    """提取文件中的所有 import 语句
    返回: [(imported_module, type, lineno), ...]
    type: 'import' 或 'from'
    """
    imports = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()
        tree = ast.parse(source, filename=str(file_path))
    except (SyntaxError, UnicodeDecodeError):
        return imports

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append((alias.name, "import", node.lineno))
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append((node.module, "from", node.lineno))
    return imports


# ============================================================
# 违规检测
# ============================================================

def check_file(file_path: Path, root: Path) -> List[Dict]:
    """检查单个文件的跨层违规"""
    violations = []
    file_layer = detect_layer(file_path, root)
    if file_layer is None:
        return violations

    imports = extract_imports(file_path)
    for imported, imp_type, lineno in imports:
        if not is_internal_module(imported):
            continue

        # 推断被 import 的模块所属层
        # 简化：取 import 路径的第一段
        parts = imported.split(".")
        if not parts:
            continue
        first = parts[0].lstrip(".")

        # 检查是否是 L0 公开 API
        if first in ALLOWED_L0_PUBLIC_MODULES:
            continue

        target_layer = LAYER_MAP.get(first)
        if target_layer is None:
            # 未识别的内部模块，跳过
            continue

        # 检查是否违规
        allowed = ALLOWED_DEPENDENCIES.get(file_layer, set())
        if target_layer not in allowed:
            rel = file_path.relative_to(root).as_posix()
            violations.append({
                "file": rel,
                "lineno": lineno,
                "imported": imported,
                "file_layer": file_layer,
                "target_layer": target_layer,
                "type": imp_type,
                "severity": "error",
                "message": f"{file_layer} 禁止 import {target_layer} 内部模块 '{imported}'",
            })
        elif target_layer == file_layer:
            # 同层引用：检查是否通过 __init__.py
            # 简化：暂不强制检查同层（避免误报）
            pass
        else:
            # 跨层但允许：检查是否通过 __init__.py（公开 API）
            # 简化：标记为 warning
            rel = file_path.relative_to(root).as_posix()
            violations.append({
                "file": rel,
                "lineno": lineno,
                "imported": imported,
                "file_layer": file_layer,
                "target_layer": target_layer,
                "type": imp_type,
                "severity": "warning",
                "message": f"{file_layer} -> {target_layer} 应通过 {target_layer} 的 __init__.py 公开 API（{imported}）",
            })
    return violations


# ============================================================
# 主流程
# ============================================================

def scan(root: Path) -> List[Dict]:
    """扫描整个项目"""
    all_violations = []
    py_files = list(root.rglob("*.py"))
    for f in py_files:
        all_violations.extend(check_file(f, root))
    return all_violations


def main():
    import argparse
    parser = argparse.ArgumentParser(description="SPDT-004 跨层依赖检查")
    parser.add_argument("--root", type=Path, default=None, help="项目根目录")
    parser.add_argument("--json", action="store_true", help="输出 JSON 报告")
    parser.add_argument("--strict", action="store_true", help="警告也升级为错误")
    args = parser.parse_args()

    root = args.root or Path(__file__).parent.parent
    if not root.exists():
        print(f"❌ 项目根目录不存在: {root}")
        return 1

    print(f"扫描项目: {root}")
    print(f"LAYER 配置: L0={len([v for v in LAYER_MAP.values() if v == 'L0'])} L1={len([v for v in LAYER_MAP.values() if v == 'L1'])} L2={len([v for v in LAYER_MAP.values() if v == 'L2'])}")
    print()

    violations = scan(root)

    # 分类
    errors = [v for v in violations if v["severity"] == "error"]
    warnings = [v for v in violations if v["severity"] == "warning"]

    if args.json:
        report = {
            "root": str(root),
            "total_files": len(list(root.rglob("*.py"))),
            "total_violations": len(violations),
            "errors": len(errors),
            "warnings": len(warnings),
            "violations": violations,
        }
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"扫描完成: {len(errors)} 错误 / {len(warnings)} 警告")
        print()
        if errors:
            print("=" * 60)
            print("[ERRORS] 违规（必须修复）")
            print("=" * 60)
            for v in errors:
                print(f"  {v['file']}:{v['lineno']}")
                print(f"    {v['message']}")
                print()

        if warnings and not args.strict:
            print("=" * 60)
            print("[WARNINGS] 建议优化")
            print("=" * 60)
            for v in warnings:
                print(f"  {v['file']}:{v['lineno']}")
                print(f"    {v['message']}")
                print()

    # 退出码
    if errors:
        return 1
    if args.strict and warnings:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
