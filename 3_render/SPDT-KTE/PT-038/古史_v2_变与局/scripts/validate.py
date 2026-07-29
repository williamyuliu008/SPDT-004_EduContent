# -*- coding: utf-8 -*-
from importlib import util
import os
files = [
    '古史_v2_ep01_宋的困局',
    '古史_v2_ep02_王安石变法',
    '古史_v2_ep03_靖康之变',
    '古史_v2_ep04_蒙古帝国',
    '古史_v2_ep05_明帝国的两难',
    '古史_v2_ep06_晚清变局'
]
base = r"C:\Users\willi\Desktop\我的视野\0713-基于知识库的高阶备考智能体\02-设计文档\古史_v2_变与局\scripts"
for f in files:
    path = os.path.join(base, f + ".py")
    spec = util.spec_from_file_location(f, path)
    mod = util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    d = mod.get_data()
    print(f"OK: {f} | acts={len(d['acts'])} | title={d['title']}")
