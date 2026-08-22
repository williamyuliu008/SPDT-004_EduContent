"""
install_hooks.py — SPDT-004 Git hooks 自动安装工具 v1.0
========================================================

一次性安装 .githooks/ 目录到 Git 配置（core.hooksPath）。
之后每次 commit 自动跑 .githooks/pre-commit（详见 pre-commit 脚本）。

跨平台:
  - Windows: git config core.hooksPath .githooks
  - Linux/Mac: 同上 + chmod +x .githooks/pre-commit

用法:
  python tools/install_hooks.py            # 安装
  python tools/install_hooks.py --check    # 检查是否已安装
  python tools/install_hooks.py --uninstall  # 卸载
"""
import argparse
import io
import os
import subprocess
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parent.parent
HOOKS_DIR = REPO_ROOT / ".githooks"
PRE_COMMIT = HOOKS_DIR / "pre-commit"


def run_git(*args, cwd=None) -> tuple[bool, str]:
    """运行 git 命令"""
    try:
        r = subprocess.run(
            ["git"] + list(args),
            cwd=cwd or REPO_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=10,
        )
        return r.returncode == 0, (r.stdout + r.stderr).strip()
    except Exception as e:
        return False, str(e)


def check() -> bool:
    """检查 hooks 是否已安装"""
    print("=== 检查 hooks 状态 ===")
    print(f"仓库: {REPO_ROOT}")
    print(f".githooks 目录: {HOOKS_DIR} {'✓' if HOOKS_DIR.exists() else '✗'}")
    print(f"pre-commit 脚本: {PRE_COMMIT} {'✓' if PRE_COMMIT.exists() else '✗'}")
    if PRE_COMMIT.exists() and sys.platform != "win32":
        import stat
        is_exec = os.access(PRE_COMMIT, os.X_OK)
        print(f"可执行: {'✓' if is_exec else '✗ (chmod +x .githooks/pre-commit)'}")
    print()
    ok, current = run_git("config", "--get", "core.hooksPath")
    print(f"git config core.hooksPath: {current if ok and current else '(未设置，用 .git/hooks/)'}")
    is_set = ok and current == ".githooks"
    print(f"是否指向 .githooks: {'✓' if is_set else '✗'}")
    print()
    return is_set


def install() -> bool:
    """安装 hooks"""
    print("=== 安装 hooks ===")
    if not HOOKS_DIR.exists():
        print(f"❌ .githooks 目录不存在: {HOOKS_DIR}")
        return False
    if not PRE_COMMIT.exists():
        print(f"❌ pre-commit 脚本不存在: {PRE_COMMIT}")
        return False
    # 设置 core.hooksPath
    ok, msg = run_git("config", "core.hooksPath", ".githooks")
    if not ok:
        print(f"❌ git config 失败: {msg}")
        return False
    print(f"✓ git config core.hooksPath = .githooks")
    # Linux/Mac 加可执行权限
    if sys.platform != "win32":
        try:
            PRE_COMMIT.chmod(0o755)
            print(f"✓ chmod +x .githooks/pre-commit")
        except Exception as e:
            print(f"⚠️ chmod 失败: {e}")
    print()
    # 验证
    print("=== 安装后状态 ===")
    check()
    print()
    # 测试运行一次
    print("=== 测试 pre-commit（dry run 不实际 commit）===")
    try:
        r = subprocess.run(
            [sys.executable, str(PRE_COMMIT)],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=60,
        )
        print(r.stdout)
        if r.returncode != 0:
            print(f"⚠️ pre-commit 退出码 {r.returncode}（不代表安装失败，只是当前状态不通过）")
    except Exception as e:
        print(f"❌ 测试运行失败: {e}")
        return False
    return True


def uninstall() -> bool:
    """卸载 hooks"""
    print("=== 卸载 hooks ===")
    ok, msg = run_git("config", "--unset", "core.hooksPath")
    if ok:
        print("✓ git config --unset core.hooksPath")
    else:
        print(f"⚠️ git config --unset 失败（可能没设置过）: {msg}")
    print()
    print("（注意：.githooks/ 目录保留，可随时重装）")
    return True


def main():
    parser = argparse.ArgumentParser(description="SPDT-004 Git hooks 安装")
    parser.add_argument("--check", action="store_true", help="检查安装状态")
    parser.add_argument("--uninstall", action="store_true", help="卸载")
    args = parser.parse_args()

    if args.check:
        ok = check()
        return 0 if ok else 1
    if args.uninstall:
        ok = uninstall()
        return 0 if ok else 1
    # 默认安装
    ok = install()
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
