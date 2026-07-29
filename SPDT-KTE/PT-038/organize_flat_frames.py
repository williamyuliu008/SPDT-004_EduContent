# -*- coding: utf-8 -*-
"""
organize_flat_frames.py — 将 flat PNG 帧序列重组为 frames_scene_XX 子目录
============================================================================
问题：scene_renderer_pillow.py 有时输出 flat PNG 到一个子目录（如 frames_scene_00/）
     而非每个 scene 一个子目录。此脚本按文件名 scene_id 前缀分组重组。

兼容两种命名格式：
  1. scene_XX_fNNNN.png   → frames_scene_XX/
  2. scene_墨骨山河_ep01_act1_00_fNNNN.png → frames_scene_墨骨山河_ep01_act1_00/

用法:
  python organize_flat_frames.py <frames_dir> [--dry-run]
"""
import os, re, argparse, shutil
from pathlib import Path


def parse_scene_id(filename: str) -> str:
    """从 PNG 文件名提取 scene_id（前缀）。"""
    # scene_墨骨山河_ep01_act1_00_f0000.png → scene_墨骨山河_ep01_act1_00
    m = re.match(r'(scene_[^_]+(?:_\w+)*)_f\d+\.png', filename, re.IGNORECASE)
    return m.group(1) if m else None


def reorganize_flat_frames(frames_dir: str, dry_run: bool = False) -> dict:
    """扫描所有子目录中的 flat PNG，按 scene_id 重组到 frames_scene_XX 子目录。"""
    frames_dir = Path(frames_dir)
    if not frames_dir.exists():
        return {"error": f"目录不存在: {frames_dir}"}

    # 收集所有 PNG（递归）
    all_pngs = [f for f in frames_dir.rglob("*.png")]
    if not all_pngs:
        return {"skipped": "无 PNG 文件"}

    # 按 scene_id 分组
    groups = {}
    for f in all_pngs:
        sid = parse_scene_id(f.name)
        if sid:
            groups.setdefault(sid, []).append(f)
        # 忽略无法识别的文件

    moved = 0
    for sid, pngs in sorted(groups.items()):
        target_dir = frames_dir / f"frames_{sid}"
        target_dir.mkdir(exist_ok=True)
        for src in sorted(pngs):
            if src.parent != target_dir:
                if not dry_run:
                    shutil.move(str(src), str(target_dir / src.name))
                moved += 1

    # 清理空目录
    for d in frames_dir.glob("frames_scene_*"):
        if not any(d.iterdir()):
            if not dry_run:
                d.rmdir()
            print(f"  [CLEAN] 空目录已删除: {d.name}")

    # 额外清理：删除多余的 scene_XX flat 目录
    for d in frames_dir.glob("scene_*"):
        if d.is_dir() and not any(d.iterdir()):
            if not dry_run:
                d.rmdir()

    n_groups = len(groups)
    print(f"  [{'DRY-RUN' if dry_run else 'OK'}] {moved} 个 PNG → {n_groups} 个子目录")
    return {"moved": moved, "groups": n_groups}


def main():
    parser = argparse.ArgumentParser(description="重组 flat 帧序列")
    parser.add_argument("dir", help="帧目录路径（包含 frames_scene_XX 子目录）")
    parser.add_argument("--dry-run", action="store_true", help="预览不实际移动")
    args = parser.parse_args()

    result = reorganize_flat_frames(args.dir, dry_run=args.dry_run)
    if "error" in result:
        print(f"[ERROR] {result['error']}")


if __name__ == "__main__":
    main()
