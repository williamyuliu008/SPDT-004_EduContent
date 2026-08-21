"""
layer_doc_sync.py — SPDT-004 文档与代码一致性检查工具 v1.0
============================================================

校验：
1. SPDT.yaml 中每个 pdt 的 directory 是否存在
2. 每个 L0/L1/L2 目录是否有对应标识
3. _06_mvp_pipeline/ISOLATION.md 的文件清单与实际一致
4. LAYERS.md / WINDOWS.md / 检查清单.md 引用的文件路径都存在

用法：
  python tools/layer_doc_sync.py
  python tools/layer_doc_sync.py --root D:/path/to/SPDT-004_EduContent
  python tools/layer_doc_sync.py --json
  python tools/layer_doc_sync.py --fix   # 自动修复可修复项（不推荐）
"""
import argparse
import io
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# ============================================================
# YAML 简化解析（避免依赖 PyYAML）
# ============================================================

def parse_simple_yaml(text: str) -> Dict:
    """极简 YAML 解析（仅支持 pdt_list 的 directory 提取）"""
    result = {"pdt_list": []}
    current_pdt = None
    in_pdt_list = False

    for line in text.split("\n"):
        stripped = line.strip()
        if stripped.startswith("pdt_list:"):
            in_pdt_list = True
            continue
        if in_pdt_list:
            # 新的 pdt
            m = re.match(r"^  - pdt_id: (.+)$", line)
            if m:
                if current_pdt:
                    result["pdt_list"].append(current_pdt)
                current_pdt = {"pdt_id": m.group(1).strip(), "directory": None, "layer_arch": None}
                continue
            # 目录
            m = re.match(r"^    directory: (.+)$", line)
            if m and current_pdt is not None:
                current_pdt["directory"] = m.group(1).strip()
                continue
            # layer_arch
            m = re.match(r"^    layer_arch: (.+)$", line)
            if m and current_pdt is not None:
                current_pdt["layer_arch"] = m.group(1).strip()
                continue
            # 顶层非 pdt 字段，结束 pdt_list
            if line.startswith("  ") and not line.startswith("    "):
                # 不是当前 pdt 的属性
                if not re.match(r"^    \w+:", line):
                    in_pdt_list = False
                    if current_pdt:
                        result["pdt_list"].append(current_pdt)
                        current_pdt = None

    if current_pdt:
        result["pdt_list"].append(current_pdt)

    return result


# ============================================================
# 检查项
# ============================================================

def check_pdt_directory_exists(root: Path, pdts: List[Dict]) -> List[Dict]:
    """检查 SPDT.yaml 中每个 pdt 的 directory 是否存在"""
    issues = []
    for pdt in pdts:
        directory = pdt.get("directory")
        if not directory:
            continue
        # 处理 Windows 路径
        if ":" in directory and "\\" in directory:
            # 绝对 Windows 路径
            full_path = Path(directory)
        else:
            # 相对路径（相对于 root）
            full_path = root / directory
        if not full_path.exists():
            issues.append({
                "type": "missing_directory",
                "severity": "warning",
                "pdt_id": pdt.get("pdt_id"),
                "directory": directory,
                "expected_path": str(full_path),
                "message": f"pdt '{pdt.get('pdt_id')}' 的 directory '{directory}' 不存在",
            })
    return issues


def check_layer_markers(root: Path) -> List[Dict]:
    """检查每个 L0/L1/L2 目录是否有标识"""
    issues = []
    layer_dirs = {
        "L0": ["1_ingest", "quality", "templates"],
        "L1": ["2_structure", "3_render", "5_deliver", "autoclaw_kit", "docs"],
        "L2": ["4_adapt"],
    }

    for layer, dirs in layer_dirs.items():
        for d in dirs:
            path = root / d
            if not path.exists():
                continue
            # 检查目录下是否有 README.md 或 LAYER 标记
            has_marker = False
            for marker in ["README.md", "ISOLATION.md", "_experimental_marker.py"]:
                if (path / marker).exists():
                    has_marker = True
                    break
            if not has_marker:
                issues.append({
                    "type": "missing_layer_marker",
                    "severity": "info",
                    "layer": layer,
                    "directory": d,
                    "message": f"目录 '{d}' 属于 {layer} 但缺少 README.md/ISOLATION.md/_experimental_marker.py",
                })
    return issues


def check_isolation_md_accuracy(root: Path) -> List[Dict]:
    """检查 _06_mvp_pipeline/ISOLATION.md 的文件清单是否准确"""
    issues = []
    isolation_path = root / "4_adapt" / "AdaptivePrepPlatform" / "_06_mvp_pipeline" / "ISOLATION.md"
    if not isolation_path.exists():
        return issues

    try:
        content = isolation_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return issues

    # 提取 ISOLATION.md 中列出的 .py 文件
    listed_in_md = set(re.findall(r"^- `(\w+\.py)`", content, re.MULTILINE))
    # 提取 ISOLATION.md 中提到的脚本（章节 2.2 风格）
    listed_section = set(re.findall(r"^- `?(\w+\.py)`?", content, re.MULTILINE))

    # 实际目录中的 .py 文件
    actual_dir = root / "4_adapt" / "AdaptivePrepPlatform" / "_06_mvp_pipeline"
    if not actual_dir.exists():
        return issues
    actual_files = set(f.name for f in actual_dir.glob("*.py"))

    # 在 ISOLATION.md 中没列出的
    missing_in_doc = actual_files - listed_in_md - {"_experimental_marker.py"}
    if missing_in_doc:
        issues.append({
            "type": "isolation_doc_stale",
            "severity": "warning",
            "path": str(isolation_path.relative_to(root)),
            "missing_files": sorted(missing_in_doc),
            "message": f"ISOLATION.md 未列出以下文件: {', '.join(sorted(missing_in_doc))}",
        })

    return issues


def check_md_references(root: Path) -> List[Dict]:
    """检查 LAYERS.md / WINDOWS.md / 检查清单.md 引用的路径是否都存在"""
    issues = []
    md_files = [
        root / "LAYERS.md",
        root / "WINDOWS.md",
        root / "docs" / "governance" / "分层治理检查清单.md",
    ]
    for md in md_files:
        if not md.exists():
            continue
        try:
            content = md.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        # 提取 markdown 链接 [text](path)
        links = re.findall(r"\[([^\]]+)\]\(([^\)]+)\)", content)
        for text, link in links:
            # 跳过外部链接
            if link.startswith(("http://", "https://", "mailto:", "#")):
                continue
            # 处理 ./ 相对路径
            target = (md.parent / link).resolve()
            if not target.exists():
                issues.append({
                    "type": "broken_md_link",
                    "severity": "warning",
                    "source": str(md.relative_to(root)),
                    "link_text": text,
                    "link_target": link,
                    "resolved_path": str(target),
                    "message": f"{md.name} 中链接 [{text}]({link}) 指向不存在的路径",
                })
    return issues


def check_yaml_health(root: Path) -> List[Dict]:
    """检查 SPDT.yaml 的 layer_arch 字段完整性"""
    issues = []
    yaml_path = root / "SPDT.yaml"
    if not yaml_path.exists():
        return [{"type": "missing_yaml", "severity": "error", "message": "SPDT.yaml 不存在"}]

    try:
        content = yaml_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return [{"type": "yaml_unreadable", "severity": "error", "message": "SPDT.yaml 无法读取（编码）"}]

    parsed = parse_simple_yaml(content)
    pdts = parsed.get("pdt_list", [])

    for pdt in pdts:
        if not pdt.get("layer_arch"):
            issues.append({
                "type": "missing_layer_arch",
                "severity": "error",
                "pdt_id": pdt.get("pdt_id"),
                "message": f"pdt '{pdt.get('pdt_id')}' 缺少 layer_arch 字段",
            })

    return issues


# ============================================================
# 主流程
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="SPDT-004 文档一致性检查")
    parser.add_argument("--root", type=Path, default=None, help="项目根目录")
    parser.add_argument("--json", action="store_true", help="输出 JSON 报告")
    args = parser.parse_args()

    root = args.root or Path(__file__).parent.parent
    if not root.exists():
        print(f"❌ 项目根目录不存在: {root}")
        return 1

    print(f"检查项目: {root}")
    print()

    all_issues = []
    all_issues.extend(check_yaml_health(root))
    all_issues.extend(check_pdt_directory_exists(root, parse_simple_yaml((root / "SPDT.yaml").read_text(encoding="utf-8")).get("pdt_list", [])))
    all_issues.extend(check_layer_markers(root))
    all_issues.extend(check_isolation_md_accuracy(root))
    all_issues.extend(check_md_references(root))

    # 分类
    by_severity = {"error": [], "warning": [], "info": []}
    for issue in all_issues:
        by_severity[issue["severity"]].append(issue)

    if args.json:
        report = {
            "root": str(root),
            "total_issues": len(all_issues),
            "errors": len(by_severity["error"]),
            "warnings": len(by_severity["warning"]),
            "info": len(by_severity["info"]),
            "issues": all_issues,
        }
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"检查完成: {len(by_severity['error'])} 错误 / {len(by_severity['warning'])} 警告 / {len(by_severity['info'])} 信息")
        print()
        for severity in ["error", "warning", "info"]:
            items = by_severity[severity]
            if not items:
                continue
            print("=" * 60)
            print(f"[{severity.upper()}] ({len(items)} 个)")
            print("=" * 60)
            for i in items:
                print(f"  [{i['type']}] {i['message']}")
            print()

    if by_severity["error"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
