"""
从 kb_vocab.json 提取临帖字帖库
生成 lint_library.json，包含可用于描红练习的汉字

用法：
  python generate_lint_library.py
"""

import json
from pathlib import Path

KB_PATH = Path(r"C:\Users\willi\Desktop\我的视野\0713-基于知识库的高阶备考智能体\02-设计文档\配置包_cafa_calligraphy_2026\knowledge\kb_vocab.json")
OUT_PATH = Path(r"D:\92_products\SPDT-001_Harmony\apps\rujing\entry\src\main\resources\rawfile\lint_library.json")


def extract_char_from_kb(entry: dict) -> dict | None:
    """从 KB 条目提取临帖字信息"""
    kb_id = entry.get("kb_id", "")
    tags = entry.get("tags", [])

    # 只处理译篆类词条
    is_zhuan = any("译篆" in t for t in tags)

    concept = entry.get("concept", "")
    structured = entry.get("structured_content", {})

    if is_zhuan:
        # 提取繁体/篆字
        # 格式如 "译篆：斗/鬥 vs 斗"
        if '/' in concept and 'vs' in concept:
            parts = concept.split('：')[1].split(' vs ')
            if len(parts) >= 2:
                traditional = parts[0].strip()
                simplified = parts[1].strip()
                return {
                    "char": traditional,
                    "simplified": simplified,
                    "type": "篆书",
                    "source": "说文解字",
                    "kb_id": kb_id,
                    "tags": tags,
                    "example_from": structured.get("斗争", ""),
                }
    return None


def build_library():
    """构建字帖库"""
    # 默认字帖（高频书法字）
    base_library = [
        {"char": "永", "font": "小篆", "example": "王羲之·兰亭序", "description": "永字八法：侧勒弩趯策掠啄磔", "difficulty": 1},
        {"char": "書", "font": "楷书", "example": "孙过庭·书谱", "description": "书者，散也", "difficulty": 1},
        {"char": "山", "font": "小篆", "example": "《说文解字》", "description": "象形字，山峰之形", "difficulty": 1},
        {"char": "水", "font": "小篆", "example": "《说文解字》", "description": "象形字，流水之形", "difficulty": 1},
        {"char": "日", "font": "小篆", "example": "《说文解字》", "description": "象形字，太阳之形", "difficulty": 1},
        {"char": "月", "font": "小篆", "example": "《说文解字》", "description": "象形字，月亮之形", "difficulty": 1},
        {"char": "道", "font": "小篆", "example": "《说文解字》", "description": "道者，路也", "difficulty": 2},
        {"char": "法", "font": "小篆", "example": "唐人尚法", "description": "法者，规矩也", "difficulty": 2},
        {"char": "意", "font": "小篆", "example": "宋人尚意", "description": "意者，心之所向", "difficulty": 2},
        {"char": "龍", "font": "小篆", "example": "李斯·峄山碑", "description": "秦篆典范", "difficulty": 3},
        {"char": "德", "font": "小篆", "example": "《说文解字》", "description": "德者，得也", "difficulty": 2},
        {"char": "風", "font": "小篆", "example": "《说文解字》", "description": "风动虫生", "difficulty": 3},
        {"char": "馬", "font": "小篆", "example": "秦汉碑刻", "description": "马形多曲折", "difficulty": 3},
        {"char": "魚", "font": "小篆", "example": "《说文解字》", "description": "象形字，鱼形", "difficulty": 2},
        {"char": "鳥", "font": "小篆", "example": "《说文解字》", "description": "象形字，鸟形", "difficulty": 2},
        {"char": "言", "font": "小篆", "example": "《说文解字》", "description": "言从口出", "difficulty": 1},
        {"char": "心", "font": "小篆", "example": "《说文解字》", "description": "心字底草法", "difficulty": 2},
        {"char": "手", "font": "小篆", "example": "《说文解字》", "description": "象形字，手形", "difficulty": 1},
        {"char": "止", "font": "小篆", "example": "《说文解字》", "description": "足之停止", "difficulty": 1},
        {"char": "戈", "font": "小篆", "example": "戈字演变", "description": "兵器之象形", "difficulty": 3},
    ]

    # 从 KB Vocab 提取译篆词条
    try:
        with open(KB_PATH, "r", encoding="utf-8") as f:
            kb_data = json.load(f)
        entries = kb_data.get("entries", [])
    except Exception:
        entries = []

    zhuan_chars = []
    for entry in entries:
        result = extract_char_from_kb(entry)
        if result and result["char"] not in [c["char"] for c in base_library]:
            zhuan_chars.append({
                "char": result["char"],
                "simplified": result.get("simplified", ""),
                "font": "小篆",
                "example": result.get("source", "说文解字"),
                "description": result.get("example_from", ""),
                "difficulty": 2,
                "kb_id": result.get("kb_id", ""),
                "source": "kb_vocab",
            })

    return {
        "schema_version": "1.0",
        "pack_id": "cafa_lint_library",
        "total_items": len(base_library) + len(zhuan_chars),
        "base_library": base_library,
        "kb_derived_chars": zhuan_chars,
        "all_items": base_library + zhuan_chars,
    }


def main():
    lib = build_library()
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(lib, f, ensure_ascii=False, indent=2)
    print(f"✅ 字帖库已生成 → {OUT_PATH}")
    print(f"   基础字帖：{len(lib['base_library'])} 字")
    print(f"   KB 译篆字：{len(lib['kb_derived_chars'])} 字")
    print(f"   总计：{lib['total_items']} 字")


if __name__ == "__main__":
    main()
