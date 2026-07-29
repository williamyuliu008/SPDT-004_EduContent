# -*- coding: utf-8 -*-
"""用 GLM 批量增强 kb_vocab.json — 完整版"""
import json, sys, os, time
from pathlib import Path

os.environ["PYTHONIOENCODING"] = "utf-8"

PT_ROOT = Path(__file__).parent.parent
KB_FILE = PT_ROOT / "_03_subject_packs" / "cafa_calligraphy_2026" / "knowledge" / "kb_vocab.json"
OUT_PATH = PT_ROOT / "_03_subject_packs" / "cafa_calligraphy_2026" / "knowledge" / "kb_vocab_enhanced.json"
PACK_DIR = PT_ROOT / "_03_subject_packs" / "cafa_calligraphy_2026"

_kf = Path("D:/_CEO/bulletin/SECRET_KEY/zhipu_api.txt")
if _kf.exists():
    os.environ["ZHIPU_API_KEY"] = _kf.read_text(encoding="utf-8").strip()

sys.path.insert(0, str(PT_ROOT / "_01_platform_core"))
from llm.llm_wrapper import create_llm_client
from knowledge_base.knowledge_base import KnowledgeBase

llm = create_llm_client(mode="glm" if os.environ.get("ZHIPU_API_KEY") else "mock")
kb = KnowledgeBase.from_pack(str(PACK_DIR))
targets = [(k, v) for k, v in kb._kb_entries.items() if k.startswith("KB_CAFA_S")]

print(f"Mode: {llm.mode if hasattr(llm,'mode') else 'mock'}, Entries: {len(targets)}")

PROMPT = (
    "请为中国美术学院书法史论考试备考，撰写以下知识点的背景补充（150-200字）。\n"
    "分2段输出（不要标题、不要引号、不要任何格式符号）：\n"
    "第1段（历史+地位+跨学科）：交代时代背景、书法史地位，并关联高考历史/文学考点1-2句\n"
    "第2段（记忆口诀）：用一句话或意象帮助记住该知识点\n\n"
    "知识点：{c}\n"
    "已有定义：{d}"
)

bg_map = {}
n = 0
err = 0

for kb_id, entry in targets:
    n += 1
    sys.stdout.write(f"[{n}/{len(targets)}] {kb_id} {entry.concept}")
    sys.stdout.flush()

    try:
        prompt = PROMPT.format(
            c=entry.concept,
            d=(entry.definition or "")[:150]
        )
        resp = llm.chat([{"role": "user", "content": prompt}])

        if hasattr(resp, "content"):
            bg = (resp.content or "").strip()
        elif isinstance(resp, dict):
            bg = (resp.get("text", "") or resp.get("content", "") or "").strip()
        else:
            bg = str(resp).strip()

        if len(bg) >= 30 and not bg.startswith("LLMResponse"):
            bg_map[kb_id] = bg
            sys.stdout.write(f" OK({len(bg)})\n")
        else:
            sys.stdout.write(f" SKIP({len(bg)})\n")
        sys.stdout.flush()

    except Exception as e:
        sys.stdout.write(f" ERR({e})\n")
        sys.stdout.flush()
        err += 1

    if n % 20 == 0:
        time.sleep(1)

print(f"\nEnhanced: {len(bg_map)}/{len(targets)}, Errors: {err}")

# Merge into original
print("Merging...")
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

print(f"Done: {OUT_PATH}")
