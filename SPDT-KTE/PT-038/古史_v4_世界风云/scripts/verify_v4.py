# -*- coding: utf-8 -*-
import importlib.util, sys

files = [
    '古史_v4_ep01_帝国的崩塌.py',
    '古史_v4_ep02_赤旗与铁幕的升起.py',
    '古史_v4_ep03_大十字.py',
    '古史_v4_ep04_冷战铁幕.py',
    '古史_v4_ep05_帝国的黄昏.py',
    '古史_v4_ep06_新战国时代.py',
]
ok = True
for fname in files:
    try:
        spec = importlib.util.spec_from_file_location('ep', fname)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        d = mod.get_data()
        chains = d.get('knowledge_chains', [])
        total_nodes = sum(len(c.get('key_nodes',[])) for c in chains)
        print(f'OK | {fname} | chains={len(chains)} nodes={total_nodes}')
    except Exception as e:
        print(f'FAIL | {fname} | {e}')
        ok = False

if ok:
    print('\nAll 6 episodes passed syntax + chain check!')
