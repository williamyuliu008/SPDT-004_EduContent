"""Batch generate golden meta.yaml for DRAM V5 scenes"""
import os, yaml
GOLDEN_DIR = r'D:\6_agent_project\projects\content_quality_gate\_01_golden_tests'

# DRAM scenes from G-05 results
dram_scenes = [
    ('DRAM_01', 'title', 'PASS'),
    ('DRAM_02', 'contrast', 'PASS'),
    ('DRAM_03', 'concept', 'PASS'),
    ('DRAM_04', 'concept', 'PASS'),
    ('DRAM_05', 'diagram', 'PASS'),
    ('DRAM_06', 'contrast', 'PASS'),
    ('DRAM_07', 'contrast', 'WARN'),  # borderline threshold
    ('DRAM_08', 'diagram', 'PASS'),
    ('DRAM_09', 'steps', 'PASS'),
    ('DRAM_10', 'diagram', 'PASS'),
    ('DRAM_11', 'action', 'PASS'),
    ('DRAM_12', 'summary', 'PASS'),
]

# Create v0.2 directory
v02_dir = os.path.join(GOLDEN_DIR, 'v0.2')
os.makedirs(v02_dir, exist_ok=True)
os.makedirs(os.path.join(v02_dir, 'dram'), exist_ok=True)

for sid, stype, status in dram_scenes:
    meta = {
        'sample_id': sid,
        'version': 'v0.2',
        'date': '2026-07-04',
        'source': f'DRAM战略视频 V5 — scene_{sid.split("_")[1]}',
        'scene_type': stype,
        'expected_result': {
            'G-05A': status if status != 'WARN' else 'PASS',
            'G-05B': 'PASS',
            'G-05C': status,
        }
    }
    meta_fp = os.path.join(v02_dir, 'dram', f'{sid}_meta.yaml')
    with open(meta_fp, 'w', encoding='utf-8') as f:
        yaml.dump(meta, f, allow_unicode=True, default_flow_style=False)

count = len(os.listdir(os.path.join(v02_dir, 'dram')))
print(f'Generated {count} DRAM golden samples in v0.2/dram/')

# Update total: 12 (v0.1) + 12 (DRAM) = 24
print(f'Total golden samples: 12 (v0.1) + 12 (DRAM) = 24')
