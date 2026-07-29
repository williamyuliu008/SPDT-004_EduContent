# -*- coding: utf-8 -*-
"""快速验证：增强1条，写入文件"""
import json, sys, os
from pathlib import Path

os.environ["PYTHONIOENCODING"] = "utf-8"
_kf = Path("D:/_CEO/bulletin/SECRET_KEY/zhipu_api.txt")
if _kf.exists():
    os.environ["ZHIPU_API_KEY"] = _kf.read_text(encoding="utf-8").strip()

PT_ROOT = Path(__file__).parent.parent
KB_FILE = PT_ROOT / "_03_subject_packs" / "cafa_calligraphy_2026" / "knowledge" / "kb_vocab.json"
OUT_PATH = PT_ROOT / "_03_subject_packs" / "cafa_calligraphy_2026" / "knowledge" / "kb_vocab_enhanced.json"
PACK_DIR = PT_ROOT / "_03_subject_packs" / "cafa_calligraphy_2026"

sys.path.insert(0, str(PT_ROOT / "_01_platform_core"))
from llm.llm_wrapper import create_llm_client
from knowledge_base.knowledge_base import KnowledgeBase

llm = create_llm_client(mode="glm" if os.environ.get("ZHIPU_API_KEY") else "mock")
kb = KnowledgeBase.from_pack(str(PACK_DIR))

targets = [(k, v) for k, v in kb._kb_entries.items() if k.startswith("KB_CAFA_S")]
print(f"Mode: {llm.mode if hasattr(llm,'mode') else '?'}, Entries: {len(targets)}")

PROMPT = (
    "请为中国美术学院书法史论考试备考，撰写以下知识点的背景补充（150-200字）。\n"
    "要求分2段：\n"
    "第1段：历史背景+书法史地位+跨学科联想（历史/文学）\n"
    "第2段：理解记忆口诀或核心意象\n"
    "只输出正文，不要任何格式符号。\n\n"
    "知识点：{c}\n"
    "定义：{d}"
)

# Test with first entry
kb_id, entry = targets[0]
print(f"Testing: {kb_id} - {entry.concept}")
prompt = PROMPT.format(c=entry.concept, d=(entry.definition or "")[:150])
resp = llm.chat([{"role": "user", "content": prompt}])

if hasattr(resp, "content"):
    bg = resp.content or ""
elif isinstance(resp, dict):
    bg = resp.get("text", "") or resp.get("content", "") or ""
else:
    bg = str(resp)

print(f"Response length: {len(bg)}")
print(f"Response: {bg[:200]}")

# Write to file
bg_map = {kb_id: bg}

with open(KB_FILE, "r", encoding="utf-8") as f:
    original = json.load(f)

def merge(obj):
    if isinstance(obj, dict):
        if "kb_id" in obj and obj["kb_id"] in bg_map:
            sc = obj.get("structured_content", {})
            if isinstance(sc, dict):
                sc["background"] = bg_map[obj["kb_id"]]
                obj["structured_content"] = sc
        for v in obj.values():
            merge(v)
    elif isinstance(obj, list):
        for item in obj:
            merge(item)

merge(original)

with open(OUT_PATH, "w", encoding="utf-8") as f:
    json.dump(original, f, ensure_ascii=False, indent=2)

print(f"Written to {OUT_PATH}")
