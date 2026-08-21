"""
4_adapt/_06_mvp_pipeline · L2 实验性标识
==========================================

LAYER: L2 (Experimental) — 与 L0/L1 物理隔离
STABILITY: 0.1（不可生产）
UPGRADE-TO-L1-REQUIREMENTS: 见 ../ISOLATION.md

任何对本目录的引用必须通过此文件暴露的接口。
禁止跨层 import 内部模块。

详见: ../../LAYERS.md + ../../WINDOWS.md
"""
import os
import sys
import io
from pathlib import Path

# 修复 Windows GBK 编码问题
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# ============================================================
# L2 标识符（CI 检查用）
# ============================================================

LAYER = "L2_experimental"
STABILITY = 0.1
CHANGE_WINDOW = "W_high"
ISOLATION_DOC = Path(__file__).parent / "ISOLATION.md"

# ============================================================
# 暴露的接口（受控的）
# ============================================================

def get_status() -> dict:
    """获取 L2 状态（受控接口）"""
    return {
        "layer": LAYER,
        "stability": STABILITY,
        "change_window": CHANGE_WINDOW,
        "isolation_doc": str(ISOLATION_DOC),
        "ready_for_l1_upgrade": False,
    }

def list_experimental_scripts() -> list:
    """列出本目录所有实验性脚本（仅元信息，不导入）"""
    scripts = []
    for f in sorted(Path(__file__).parent.glob("*.py")):
        if f.name.startswith("_") and f.name != "__init__.py":
            continue  # 跳过内部文件
        if f.name == "_experimental_marker.py":
            continue
        scripts.append({
            "name": f.name,
            "size": f.stat().st_size,
            "mtime": f.stat().st_mtime,
        })
    return scripts

# ============================================================
# L2 警告（任何 import 都会触发）
# ============================================================

def _warn():
    print(f"[L2 WARNING] _06_mvp_pipeline 是实验性模块（稳定性 {STABILITY}）")
    print(f"    改动窗口: {CHANGE_WINDOW} only")
    print(f"    详见: {ISOLATION_DOC}")
    print(f"    升级条件: L2 → L1 需 >=3 次成功 + 接口冻结 + 测试覆盖 >=70%")

if __name__ == "__main__":
    _warn()
    print()
    print(f"当前状态: {get_status()}")
    print()
    print("实验性脚本清单:")
    for s in list_experimental_scripts():
        print(f"  - {s['name']} ({s['size']} bytes)")
