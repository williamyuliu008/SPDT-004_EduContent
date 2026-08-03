# -*- coding: utf-8 -*-
"""Debug domain inference"""
import importlib.util
import sys
from pathlib import Path

_r = Path("router/router.py")
spec = importlib.util.spec_from_file_location("router", _r)
mod = importlib.util.module_from_spec(spec)
sys.modules["router"] = mod
spec.loader.exec_module(mod)
ContentRouter = mod.ContentRouter
router = ContentRouter()

test_cases = [
    ("chinese_classical", {"type": "textbook", "description": "韩愈《师说》文言文阅读，含原文、断句、翻译的语言知识转化", "keywords": ["语文", "文言文", "翻译", "转化", "古诗文"], "source_chain_id": "师说韩愈", "exam_type": "高考语文"}),
    ("english_reading", {"type": "textbook", "description": "高考英语阅读理解主旨大意题解题策略，从英文到方法的转化", "keywords": ["英语", "阅读", "翻译", "转化", "辨析"], "source_chain_id": "阅读主旨策略", "exam_type": "高考英语"}),
    ("calligraphy", {"type": "expert_notes", "description": "颜真卿楷书风格辨析卡，从书论原文到现代解释的翻译转化", "keywords": ["辨析", "区分", "解释", "转化", "书法史"], "source_chain_id": "颜真卿辨析卡", "exam_type": "国美书法校考"}),
]

for name, raw_input in test_cases:
    class D:
        verdict = "APPLICABLE"
    route = router.route(D(), raw_input)
    domain = route._infer_subject_domain(raw_input)
    print(f"{name}: domain={domain}, b1_b4={route.b1_b4_type}")
    # Debug combined
    desc = raw_input.get("description", "").lower()
    type_field = raw_input.get("type", "").lower()
    combined = desc + " " + type_field
    print(f"  desc={desc[:60]}")
    print(f"  keywords={raw_input.get('keywords', [])}")
