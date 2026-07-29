# -*- coding: utf-8 -*-
"""Reorganize flat frames into scene subdirectories"""
import os, shutil

def organize(frames_dir, prefix_filter=None):
    """Move flat PNG files into subdirectories based on scene prefix."""
    files = [f for f in os.listdir(frames_dir) if f.endswith('.png')]
    
    # Group by scene prefix
    groups = {}
    for f in files:
        # Extract scene prefix: scene_墨骨山河_ep07_act1_00_f0000.png -> scene_墨骨山河_ep07_act1_00
        parts = f.replace('.png', '').rsplit('_f', 1)
        if len(parts) == 2:
            prefix = parts[0]
            if prefix not in groups:
                groups[prefix] = []
            groups[prefix].append(f)
    
    for prefix, group_files in groups.items():
        subdir = os.path.join(frames_dir, prefix)
        if not os.path.exists(subdir):
            os.makedirs(subdir)
        
        for f in group_files:
            src = os.path.join(frames_dir, f)
            dst = os.path.join(subdir, f)
            if not os.path.exists(dst):
                shutil.move(src, dst)
        print(f"  {prefix}: {len(group_files)} frames -> {subdir}")
    
    print(f"Organized {len(files)} frames into {len(groups)} scene dirs")

# Organize ep07
ep07_dir = r"D:\92_products\SPDT-004_EduContent\PT-038_TextExperience\墨骨山河_ep07_test\ep07_frames"
print("Organizing ep07 frames...")
organize(ep07_dir)

# Organize ep08
ep08_dir = r"D:\92_products\SPDT-004_EduContent\PT-038_TextExperience\墨骨山河_ep08_test\ep08_frames"
print("\nOrganizing ep08 frames...")
organize(ep08_dir)
