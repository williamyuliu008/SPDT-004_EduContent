"""
window_check.py — SPDT-004 当前开发窗口检查工具 v1.0
======================================================

判断当前应在哪个开发窗口（基于时间 + 当前周几 + 分支名），
并根据 git diff 检测改动文件所属层，验证窗口与改动层是否匹配。

WINDOW 规则（详见 WINDOWS.md）:
  W_low  - 1-2 周一次（周二/周四上午），L0 修复
  W_mid  - 每天/每周，L1 内容生产
  W_high - 每天多次，L2 新功能

默认周节奏（可在 WINDOWS.md §7 调整）:
  周二 09:00-12:00  → W_low
  周五 14:00-18:00  → W_low
  其他时段          → W_mid（默认）
  特殊：L2 工作可申请 W_high（在 W_high 时间块内）

用法：
  python tools/window_check.py
  python tools/window_check.py --set-high        # 声明当前为 W_high
  python tools/window_check.py --set-mid
  python tools/window_check.py --set-low
  python tools/window_check.py --json
"""
import argparse
import io
import json
import os
import re
import subprocess
import sys
from datetime import datetime, time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# ============================================================
# WINDOW 配置
# ============================================================

# 每周固定 W_low 时段（小时制 24h）
# 格式: (weekday, start_hour, end_hour, label)
# weekday: 0=周一, 1=周二, ..., 6=周日
WINDOW_SCHEDULE = [
    (1, 9, 12, "W_low"),   # 周二上午
    (4, 14, 18, "W_low"),  # 周五下午
]

# 分支名 → 强制 WINDOW（覆盖默认）
BRANCH_WINDOW_OVERRIDE = {
    "main": "W_mid",          # main 分支只接受 W_mid 提交
    "master": "W_mid",        # master 分支同 main 规则
    "release/*": "W_low",     # 发布分支只接受 W_low
    "experimental/*": "W_high",  # 实验分支允许 W_high
    "feature/*": "W_high",    # feature 分支允许 W_high
}

# LAYER 推断（与 layer_lint.py 对齐）
LAYER_MAP: Dict[str, str] = {
    "1_ingest": "L0",
    "quality": "L0",
    "templates": "L0",
    "2_structure": "L1",
    "3_render": "L1",
    "5_deliver": "L1",
    "autoclaw_kit": "L1",
    "4_adapt": "L2",
    "tools": "L0",  # tools 自身是基础设施
    "docs": "L1",   # 文档是治理
    "LAYERS.md": "L1",
    "WINDOWS.md": "L1",
    "SPDT.yaml": "L1",
}

# LAYER → 默认 WINDOW + 跨窗口规则
# 严格违规：L0 在 W_high（绝对不允许），L2 在 W_low（绝对不允许）
# 警告：其他跨窗口组合（建议但允许，作为边角料工作）
LAYER_DEFAULT_WINDOW = {
    "L0": "W_low",
    "L1": "W_mid",
    "L2": "W_high",
}

# 严格违规组合：(current_window, changed_layer)
STRICT_VIOLATIONS = {
    ("W_high", "L0"),  # L0 禁止在 W_high 改（无 RFC 不行）
    ("W_low", "L2"),   # L2 禁止在 W_low 改（架构工作不紧急）
}

# 允许的"边角料"组合：(current_window, changed_layer)
ALLOWED_CROSS = {
    ("W_low", "L1"),   # W_low 可以改 L1（紧急修复）
    ("W_low", "L0"),   # W_low 默认就是 L0
    ("W_mid", "L0"),   # W_mid 可以改 L0（紧急修复）
    ("W_mid", "L1"),   # W_mid 默认就是 L1
    ("W_mid", "L2"),   # W_mid 可以小改 L2
    ("W_high", "L1"),  # W_high 可以改 L1（边角料）
    ("W_high", "L2"),  # W_high 默认就是 L2
}


# ============================================================
# WINDOW 推断
# ============================================================

def detect_window_from_time(now: datetime, override: Optional[str] = None) -> str:
    """根据时间推断当前窗口"""
    if override:
        return override
    weekday = now.weekday()
    hour = now.hour
    for wd, start, end, label in WINDOW_SCHEDULE:
        if weekday == wd and start <= hour < end:
            return label
    return "W_mid"  # 默认


def detect_window_from_branch(branch: str) -> Optional[str]:
    """根据分支名推断窗口"""
    for pattern, window in BRANCH_WINDOW_OVERRIDE.items():
        if "*" in pattern:
            prefix = pattern.replace("*", "")
            if branch.startswith(prefix):
                return window
        elif branch == pattern:
            return window
    return None


def detect_layer_from_path(path: str) -> str:
    """根据文件路径推断层"""
    parts = path.replace("\\", "/").split("/")
    if not parts:
        return "L1"
    top = parts[0]

    # _XX 编号子目录（如 _06_mvp_pipeline）属于父目录
    if top.startswith("_") and len(parts) > 1:
        top = parts[1]

    # 顶层文件
    if top in LAYER_MAP:
        return LAYER_MAP[top]

    return LAYER_MAP.get(top, "L1")


# ============================================================
# Git 操作
# ============================================================

def get_current_branch(root: Path) -> str:
    """获取当前 git 分支"""
    try:
        r = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=root, capture_output=True, text=True, encoding="utf-8", errors="replace"
        )
        return r.stdout.strip() if r.returncode == 0 else "unknown"
    except Exception:
        return "unknown"


def get_git_diff_files(root: Path) -> List[str]:
    """获取 git diff 改动的文件（staged + unstaged）"""
    files = set()
    try:
        # Unstaged
        r = subprocess.run(
            ["git", "diff", "--name-only"],
            cwd=root, capture_output=True, text=True, encoding="utf-8", errors="replace"
        )
        if r.returncode == 0:
            files.update(f for f in r.stdout.strip().split("\n") if f)
        # Staged
        r = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            cwd=root, capture_output=True, text=True, encoding="utf-8", errors="replace"
        )
        if r.returncode == 0:
            files.update(f for f in r.stdout.strip().split("\n") if f)
    except Exception:
        pass
    return sorted(files)


# ============================================================
# 主流程
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="SPDT-004 窗口检查")
    parser.add_argument("--root", type=Path, default=None, help="项目根目录")
    parser.add_argument("--set-high", action="store_true", help="声明当前为 W_high")
    parser.add_argument("--set-mid", action="store_true", help="声明当前为 W_mid")
    parser.add_argument("--set-low", action="store_true", help="声明当前为 W_low")
    parser.add_argument("--json", action="store_true", help="输出 JSON 报告")
    args = parser.parse_args()

    root = args.root or Path(__file__).parent.parent
    now = datetime.now()

    # 1. 推断当前窗口
    override = None
    if args.set_high:
        override = "W_high"
    elif args.set_low:
        override = "W_low"
    elif args.set_mid:
        override = "W_mid"

    branch = get_current_branch(root)
    branch_window = detect_window_from_branch(branch)
    time_window = detect_window_from_time(now, override)
    current_window = branch_window or time_window

    # 2. 检测改动文件
    changed_files = get_git_diff_files(root)
    if not changed_files:
        if not args.json:
            print(f"当前时间: {now.strftime('%Y-%m-%d %H:%M:%S %A')}")
            print(f"当前分支: {branch}")
            print(f"当前窗口: {current_window} ({'分支强制' if branch_window else '时间推断'})")
            print()
            print("✅ 无 git diff 改动，无需检查")
            return 0

    # 3. 按层分组
    by_layer: Dict[str, List[str]] = {}
    for f in changed_files:
        layer = detect_layer_from_path(f)
        by_layer.setdefault(layer, []).append(f)

    # 4. 验证窗口与改动层匹配
    mismatches = []
    warnings = []
    for layer, files in by_layer.items():
        if (current_window, layer) in STRICT_VIOLATIONS:
            mismatches.append({
                "layer": layer,
                "expected_window": LAYER_DEFAULT_WINDOW.get(layer),
                "current_window": current_window,
                "files": files,
                "severity": "error",
            })
        elif (current_window, layer) not in ALLOWED_CROSS:
            warnings.append({
                "layer": layer,
                "expected_window": LAYER_DEFAULT_WINDOW.get(layer),
                "current_window": current_window,
                "files": files,
                "severity": "warning",
            })

    # 5. 输出
    if args.json:
        report = {
            "timestamp": now.isoformat(),
            "branch": branch,
            "current_window": current_window,
            "branch_override": branch_window,
            "time_inferred": time_window,
            "manual_override": override,
            "changed_files_count": len(changed_files),
            "by_layer": by_layer,
            "mismatches": mismatches,
            "warnings": warnings,
        }
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print("=" * 60)
        print("SPDT-004 窗口检查")
        print("=" * 60)
        print(f"当前时间: {now.strftime('%Y-%m-%d %H:%M:%S %A')}")
        print(f"当前分支: {branch}")
        print(f"当前窗口: {current_window}")
        print(f"  来源: {'分支强制' if branch_window else ('手动覆盖' if override else '时间推断')}")
        print()
        print(f"改动文件: {len(changed_files)} 个")
        for layer, files in by_layer.items():
            default = LAYER_DEFAULT_WINDOW.get(layer, "?")
            if (current_window, layer) in STRICT_VIOLATIONS:
                mark = "MISMATCH (违规)"
            elif (current_window, layer) in ALLOWED_CROSS:
                mark = "OK"
            else:
                mark = "WARNING (边角料)"
            print(f"  [{layer}] 默认 {default} → {mark} ({len(files)} 个)")

        print()
        if mismatches:
            print("=" * 60)
            print("[ERROR] 严格违规（必须修复）")
            print("=" * 60)
            for m in mismatches:
                print(f"  [{m['layer']}] 当前 {m['current_window']} ≠ 期望 {m['expected_window']}")
                print(f"    文件 ({len(m['files'])} 个):")
                for f in m["files"][:5]:
                    print(f"      - {f}")
                if len(m["files"]) > 5:
                    print(f"      ... 还有 {len(m['files']) - 5} 个")
                print(f"    建议: 等到 {m['expected_window']} 窗口，或申请破窗")
            print()
            return 1
        elif warnings:
            print("=" * 60)
            print("[WARNING] 边角料工作（允许但不建议）")
            print("=" * 60)
            for w in warnings:
                print(f"  [{w['layer']}] 当前 {w['current_window']}（默认 {w['expected_window']}）")
                print(f"    文件: {len(w['files'])} 个")
            print()
            print("=" * 60)
            print("[OK] 窗口检查通过（带边角料警告）")
            print("=" * 60)
            return 0
        else:
            print("=" * 60)
            print("[OK] 窗口与改动层完全匹配")
            print("=" * 60)
            return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
