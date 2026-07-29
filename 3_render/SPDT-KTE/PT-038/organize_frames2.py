# -*- coding: utf-8 -*-
"""Rename scene_* subdirs to frames_scene_* for compose_video.py compatibility"""
import os

def rename_dirs(frames_dir):
    for d in os.listdir(frames_dir):
        if d.startswith('scene_') and os.path.isdir(os.path.join(frames_dir, d)):
            new_name = 'frames_' + d
            old_path = os.path.join(frames_dir, d)
            new_path = os.path.join(frames_dir, new_name)
            if not os.path.exists(new_path):
                os.rename(old_path, new_path)
                print(f"  Renamed: {d} -> {new_name}")
            else:
                print(f"  Already exists: {new_name}")

# ep07
ep07_dir = r"D:\92_products\SPDT-004_EduContent\PT-038_TextExperience\墨骨山河_ep07_test\ep07_frames"
print("Renaming ep07...")
rename_dirs(ep07_dir)

# ep08
ep08_dir = r"D:\92_products\SPDT-004_EduContent\PT-038_TextExperience\墨骨山河_ep08_test\ep08_frames"
print("Renaming ep08...")
rename_dirs(ep08_dir)
