# -*- coding: utf-8 -*-
"""
用 GLM 批量增强 kb_vocab.json 内容（仅书法史核心条目）
"""
import json, sys, os, time
from pathlib import Path

PT_ROOT = Path(__file__).parent.parent
KB_PATH = PT_ROOT / "_03_subject_packs" / "cafa_calligraphy_2026" / "knowledge" / "kb_vocab.json"
OUT_PATH = PT_ROOT / "_03_subject_packs" / "cafa_calligraphy_2026" / "knowledge" / "kb_vocab_enhanced.json"

os.environ["PYTHONIOENCODING"] = "utf-8"
_api_key_path = Path("D:/_CEO/bulletin/SECRET_KEY/zhipu_api.txt")
if _api_key_path.exists():
    os.environ["ZHIPU_API_KEY"] = _api_key_path.read_text(encoding="utf-8").strip()

sys.path.insert(0, str(PT_ROOT / "_01_platform_core"))
from llm.llm_wrapper import create_llm_client
from knowledge_base.knowledge_base import KnowledgeBase

llm_mode = "glm" if os.environ.get("ZHIPU_API_KEY") else "mock"
print(f"LLM mode: {llm_mode}")
llm = create_llm_client(mode=llm_mode)
kb = KnowledgeBase.from_pack(str(PT_ROOT / "_03_subject_packs" / "cafa_calligraphy_2026"))

targets = [(k, v) for k, v in kb._kb_entries.items() if k.startswith("KB_CAFA_S")]
print(f"Total entries: {len(targets)}")

PROMPT = (
    '请为中国美术学院书法史论考试备考，撰写以下知识点的"背景补充"（200-250字）。\n'
    '要求分3段：\n'
    '第1段（历史背景+地位）：交代知识点产生的时代背景、在书法史上的地位\n'
    '第2段（跨学科联想）：与高考历史、古代文学的关联考点（1-2句话）\n'
    '第3段（理解记忆）：用一个核心意象或一句话帮助记住这个知识点\n'
    '直接输出正文，不要标题，不要加引号，用自然段落。\n\n'
    '知识点：{concept}\n'
    '现有定义：{definition}'
)

count = 0
errors = 0
enhanced_map = {}

for kb_id, entry in targets:
    count += 1
    print(f"[{count}/{len(targets)}] {kb_id} {entry.concept}", flush=True)

    try:
        prompt = PROMPT.format(
            concept=entry.concept,
            definition=(entry.definition or "")[:200]
        )
        resp = llm.chat([{"role": "user", "content": prompt}])

        if hasattr(resp, "content"):
            bg_text = resp.content or ""
        elif isinstance(resp, dict):
            bg_text = resp.get("text", "") or resp.get("content", "")
        else:
            bg_text = str(resp)

        bg_text = bg_text.strip()
        if len(bg_text) < 30:
            print(f"  SKIP (too short: {len(bg_text)} chars)")
            continue

        enhanced_map[kb_id] = bg_text
        print(f"  OK ({len(bg_text)} chars)", flush=True)

        # 速率控制
        if count % 20 == 0:
            print(f"  -- checkpoint, sleeping 2s --", flush=True)
            time.sleep(2)
        else:
            time.sleep(0.8)

    except Exception as e:
        print(f"  ERR: {e}", flush=True)
        errors += 1

print(f"\nDone: {count - errors}/{len(targets)} enhanced, {errors} errors")

# ── 合并 ──────────────────────────────────────────────────────────────
print("Merging into original...")
with open(KB_PATH, "r", encoding="utf-8") as f:
    original = json.load(f)

def merge(obj):
    if isinstance(obj, dict):
        if "kb_id" in obj and obj["kb_id"] in enhanced_map:
            sc = obj.get("structured_content", {})
            if isinstance(sc, dict):
                sc["background"] = enhanced_map[obj["kb_id"]]
                obj["structured_content"] = sc
        for v in obj.values():
            merge(v)
    elif isinstance(obj, list):
        for item in obj:
            merge(item)

merge(original)

with open(OUT_PATH, "w", encoding="utf-8") as f:
    json.dump(original, f, ensure_ascii=False, indent=2)

print(f"Saved: {OUT_PATH} ({len(enhanced_map)} entries)")
