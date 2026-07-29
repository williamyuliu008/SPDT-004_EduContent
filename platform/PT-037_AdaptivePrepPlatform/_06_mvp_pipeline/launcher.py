# -*- coding: utf-8 -*-
"""
PT-037 自适应备考智能体平台 — 启动器
"""

import subprocess
import webbrowser
import sys
import os
from pathlib import Path

BASE = Path(__file__).parent
SERVER = BASE / "server.py"
GUI    = BASE / "gui.html"
PIPELINE = BASE / "main_pipeline.py"


def run_py(path):
    subprocess.run([sys.executable, str(path)], cwd=str(BASE))


def main():
    print("\n" + "=" * 44)
    print("  PT-037 自适应备考智能体平台")
    print("=" * 44)
    print("  [1] 🌐 学习 GUI（答题模式）")
    print("  [2] 📚 知识库看板")
    print("  [3] 📋 CLI 管道（GLM 模式）")
    print("  [4] 📋 CLI 管道（Mock 模式）")
    print("  [0] 退出")
    print("-" * 44)
    c = input("选择 > ").strip()

    if c == "1":
        print("\n启动后端 → http://localhost:5188")
        webbrowser.open("http://localhost:5188")
        run_py(SERVER)

    elif c == "2":
        print("\n启动知识库看板 → http://localhost:5188/kb")
        webbrowser.open("http://localhost:5188/kb")
        run_py(SERVER)

    elif c == "3":
        os.environ["PYTHONIOENCODING"] = "utf-8"
        run_py(PIPELINE)

    elif c == "4":
        os.environ["PYTHONIOENCODING"] = "utf-8"
        subprocess.run(
            [sys.executable, str(PIPELINE), "--mode", "mock"],
            cwd=str(BASE)
        )

    elif c == "0":
        print("退出")
    else:
        print("无效选择")


if __name__ == "__main__":
    main()
