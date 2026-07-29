#!/usr/bin/env python
# coding: utf-8
"""
入境APP · DevEco Testing Hypium 自动化入口
用法:
  python main.py                           # 交互模式（进入 hypium 控制台）
  python main.py run -l TC_001_video_play   # 直接运行指定用例
  python main.py run -l TC_001_video_play -ta screenshot:true  # 带截图运行
"""

import sys
import os

# 确保 hypium 模块可用
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from xdevice import Variables, run


def main():
    # 设置项目根目录（config/ 和 testcases/ 的查找起点）
    project_root = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_root)

    # 执行 hypium run
    run()


if __name__ == "__main__":
    main()
