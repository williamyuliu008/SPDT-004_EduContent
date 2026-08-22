"""
install_watcher.py — SPDT-004 1_ingest watcher 一键安装 v1.0
=============================================================

将 watcher 注册为系统 cron / 计划任务（跨平台）。

WINDOWS 方式:
  - 用 schtasks 创建计划任务（每分钟跑一次 watcher.py --once）
  - 或启动后台 Python 进程

LINUX 方式:
  - 写 systemd service（systemd-run --user）
  - 或写 cron entry（每分钟 * * * *）

用法:
  python 1_ingest/install_watcher.py install
  python 1_ingest/install_watcher.py status
  python 1_ingest/install_watcher.py uninstall
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

WATCHER_PY = Path(__file__).parent / "watcher.py"
PYTHON_EXE = sys.executable

# Windows 计划任务名
TASK_NAME = "SPDT-004_1_ingest_watcher"


def log(msg, level="INFO"):
    print(f"[{level}] {msg}")


def run(cmd, **kwargs):
    """运行命令"""
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", **kwargs)
        return r.returncode, (r.stdout + r.stderr).strip()
    except Exception as e:
        return 1, str(e)


def install_windows():
    """Windows: 用 schtasks 创建计划任务"""
    cmd_str = f'"{PYTHON_EXE}" "{WATCHER_PY}" --once'
    schtasks_cmd = [
        "schtasks", "/Create", "/SC", "MINUTE", "/MO", "1",
        "/TN", TASK_NAME, "/TR", cmd_str, "/F"
    ]
    log(f"创建 Windows 计划任务: {TASK_NAME}")
    log(f"  命令: {cmd_str}")
    code, out = run(schtasks_cmd)
    if code == 0:
        log(f"  ✓ 计划任务创建成功（每分钟跑一次）")
    else:
        log(f"  ✗ 创建失败: {out}", "ERROR")
    return code


def install_linux():
    """Linux: 写 systemd user service"""
    service_dir = Path.home() / ".config" / "systemd" / "user"
    service_dir.mkdir(parents=True, exist_ok=True)
    service_file = service_dir / f"{TASK_NAME}.service"
    service_content = f"""[Unit]
Description=SPDT-004 1_ingest watcher
After=network.target

[Service]
Type=simple
ExecStart={PYTHON_EXE} {WATCHER_PY} --interval 60
Restart=always
RestartSec=10

[Install]
WantedBy=default.target
"""
    service_file.write_text(service_content, encoding="utf-8")
    log(f"创建 systemd service: {service_file}")
    log(f"  启动: systemctl --user enable --now {TASK_NAME}")
    run(["systemctl", "--user", "daemon-reload"])
    code, out = run(["systemctl", "--user", "enable", "--now", f"{TASK_NAME}.service"])
    if code == 0:
        log(f"  ✓ service 启动成功")
    else:
        log(f"  ✗ 启动失败: {out}", "ERROR")
    return code


def install():
    if sys.platform == "win32":
        return install_windows()
    return install_linux()


def status():
    if sys.platform == "win32":
        code, out = run(["schtasks", "/Query", "/TN", TASK_NAME, "/FO", "LIST", "/V"])
        if code == 0:
            log(f"✓ 计划任务存在: {TASK_NAME}")
            log(out[:500])
        else:
            log(f"✗ 计划任务不存在", "WARN")
    else:
        code, out = run(["systemctl", "--user", "status", f"{TASK_NAME}.service"])
        log(out[:500])
    return 0


def uninstall():
    if sys.platform == "win32":
        code, out = run(["schtasks", "/Delete", "/TN", TASK_NAME, "/F"])
        if code == 0:
            log(f"✓ 计划任务删除成功")
        else:
            log(f"⚠️ 删除失败: {out}", "WARN")
    else:
        code, out = run(["systemctl", "--user", "disable", "--now", f"{TASK_NAME}.service"])
        log(out[:300])
    return 0


def main():
    parser = argparse.ArgumentParser(description="1_ingest watcher 一键安装")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("install", help="安装 watcher")
    sub.add_parser("status", help="查看 watcher 状态")
    sub.add_parser("uninstall", help="卸载 watcher")

    args = parser.parse_args()
    if args.command == "install":
        return install()
    elif args.command == "status":
        return status()
    elif args.command == "uninstall":
        return uninstall()
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
