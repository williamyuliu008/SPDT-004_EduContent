"""
PT-030 → K 卡 整合脚本 v1.0 (雪薇端)
=====================================
把 PT-030 工具链产物 (split + reviewed + llm_gen) 整合成 v1.2.1 schema 的 K 卡,
入库到 knowledge-cards-prod/projects/math/cards/本地上海/PT030_<日期>/

输入:
- D:\\Z_学习平台\\SPDT-004_EduContent\\PT-030\\zhenti\\数学\\split\\*_split_v11.json
- D:\\Z_学习平台\\SPDT-004_EduContent\\PT-030\\zhenti\\数学\\split\\*_reviewed.json (可选)
- D:\\Z_学习平台\\SPDT-004_EduContent\\PT-030\\zhenti\\数学\\llm_gen\\*_gen.json

输出:
- D:\\Z_学习平台\\knowledge-cards-prod\\projects\\math\\cards\\本地上海\\PT030_<日期>\\<year>_<q_no>_<subject>.json

每张 K 卡字段:
- id, type, maturity, version, schema (v1.2.1)
- subject, module, topic
- source, source_type, source_year, source_paper
- front (题干), back (答案)
- front_detail, back_detail (含 explanation)
- verdict, difficulty, knowledge_points
- chain_id, display_target (v3.0)
- related_cards, prerequisites
- tags, provenance
"""

import json
import re
import sys
import time
from pathlib import Path
from collections import defaultdict


PT030_ROOT = Path(r"D:\Z_学习平台\SPDT-004_EduContent\PT-030\zhenti\数学")
SPLIT_DIR = PT030_ROOT / "split"
LLM_GEN_DIR = PT030_ROOT / "llm_gen"
KCARDS_ROOT = Path(r"D:\Z_学习平台\knowledge-cards-prod\projects\math\cards\本地上海")


def detect_module(stem: str, q: dict) -> str:
    """根据题号/学科猜板块 (启发式)"""
    q_no = q.get("q_no", 0)
    type_ = q.get("type", "")
    stem_ = q.get("stem", "")

    # 主观题 (简答/论述) → 通用
    if type_ in ("简答", "论述"):
        return "解答题"

    # 启发式按关键词
    if "解三角形" in stem_ or "正弦定理" in stem_ or "余弦定理" in stem_:
        return "解三角形"
    if "数列" in stem_ or "等差" in stem_ or "等比" in stem_ or "通项" in stem_:
        return "数列"
    if "概率" in stem_ or "分布列" in stem_ or "期望" in stem_ or "方差" in stem_:
        return "概率统计"
    if "立体" in stem_ or "正方体" in stem_ or "三棱锥" in stem_ or "球" in stem_ and "面" in stem_:
        return "立体几何"
    if "椭圆" in stem_ or "双曲线" in stem_ or "抛物线" in stem_ or "焦点" in stem_:
        return "解析几何"
    if "导数" in stem_ or "单调" in stem_ or "极值" in stem_ or "不等式" in stem_ and "x" in stem_:
        return "导数"

    # 填空 Q1-Q12 多数是代数/集合/函数
    if q_no <= 6:
        return "集合与函数"
    if q_no <= 12:
        return "代数"
    return "通用"


def detect_difficulty(q: dict) -> str:
    """根据 type/分值猜难度"""
    type_ = q.get("type", "")
    score = q.get("score") or 0
    if type_ == "填空" and score <= 4:
        return "基础"
    if type_ == "填空" and score <= 5:
        return "中档"
    if type_ in ("简答", "论述"):
        return "中档"
    return "中档"


def extract_year_paper(filename: str) -> tuple[int, str]:
    """从文件名解析年份 + 名称 (解析版/原卷版)"""
    m = re.match(r"(\d{4})", filename)
    year = int(m.group(1)) if m else 0
    if "春季" in filename:
        season = "春季高考"
    elif "高考" in filename:
        season = "秋季高考"
    else:
        season = "高考"
    return year, season


def build_kcard(q: dict, source_split: str, source_year: int, source_paper: str,
                 source_module: str, source_verdict: str = None, source_explanation: str = None) -> dict:
    """从 PT-030 split question 构建 K 卡 v1.2.1"""
    q_no = q.get("q_no", 0)
    type_ = q.get("type", "未知")
    score = q.get("score")
    stem = q.get("stem", "").strip()
    options = q.get("options", [])
    answer_label = q.get("answer_label", "")
    answer_text = q.get("answer_text", "")

    # 板块
    module = detect_module(source_split, q)
    difficulty = detect_difficulty(q)
    verdict = source_verdict or ("TRUE" if answer_text or answer_label else "PENDING")
    explanation = source_explanation or ""

    # id
    paper_short = "yj" if "原卷" in source_paper else "jx"
    kcard_id = f"pt030_{source_year}_q{q_no:02d}_{paper_short}_{module}"

    # knowledge_points (从 stem 启发)
    kp = []
    if "正弦" in stem: kp.append("正弦定理")
    if "余弦" in stem: kp.append("余弦定理")
    if "椭圆" in stem: kp.append("椭圆")
    if "双曲线" in stem: kp.append("双曲线")
    if "抛物线" in stem: kp.append("抛物线")
    if "等差" in stem: kp.append("等差数列")
    if "等比" in stem: kp.append("等比数列")
    if "概率" in stem: kp.append("概率")
    if "分布列" in stem: kp.append("分布列与期望")
    if "导数" in stem: kp.append("导数")
    if "单调" in stem: kp.append("单调性")
    if "极值" in stem: kp.append("极值")
    if "立体" in stem or "正方体" in stem: kp.append("立体几何")
    if "球" in stem: kp.append("球")
    if not kp:
        kp.append(module)

    # back (答案)
    if answer_text:
        back = answer_text
    elif answer_label:
        back = f"答案: {answer_label}"
    else:
        back = ""

    # tags
    tags = [
        "PT030",
        str(source_year),
        f"{source_year}年{source_paper}",
        module,
        "自动入库",
    ]

    return {
        "id": kcard_id,
        "type": f"math_{module}_question",
        "maturity": "REVIEWED" if verdict == "TRUE" else "DRAFT",
        "version": "1.2.6",
        "schema": "v1.2.1",
        "subject": "math",
        "module": module,
        "topic": module,
        "source": f"PT030_{source_year}_{source_paper}",
        "source_type": "高考真题",
        "source_year": source_year,
        "source_paper": source_paper,
        "source_split": source_split,
        "url": "",
        "verdict": verdict,
        "difficulty": difficulty,
        "score": score,
        "knowledge_points": kp,
        "front": stem,
        "back": back,
        "front_detail": "",
        "back_detail": explanation,
        "options": [{"label": o.get("label", ""), "text": o.get("text", "")} for o in options],
        "display_target": ["学习中心"],
        "tags": tags,
        "parent_cards": [],
        "method_ref": [],
        "explain": explanation,
        "chain_id": f"pt030_{source_year}_{source_paper}_{module}",
        "related_cards": [],
        "prerequisites": [],
        "provenance": {
            "type": "pt030_pipeline",
            "source": f"PT-030/{source_split}",
            "extracted_by": "merge_to_kcards.py",
            "extracted_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "schema_origin": "PT-030 split_v11.json v1.1 + 4step_v1.1",
        },
    }


def merge_split_to_kcards(split_path: Path, reviewed_path: Path = None,
                          output_dir: Path = None) -> tuple[int, int, int]:
    """把单套 split 转 K 卡, 输出到 output_dir/<year>/, 返回 (ok, fail, total)"""
    if not split_path.exists():
        return (0, 0, 0)
    d = json.loads(split_path.read_text(encoding="utf-8"))
    questions = d.get("questions", [])
    if not questions:
        return (0, 0, 0)

    # source_paper
    fn = split_path.stem.replace("_split_v11", "").replace("_split", "")
    source_year, season_short = extract_year_paper(fn)
    source_paper = fn  # 全名 (e.g. "2024年上海高考数学真题（原卷版）")
    paper_dir_name = f"{source_year}_{season_short.replace('高考', '')}_{'原卷' if '原卷' in fn else '解析'}"
    # 简化为 "原卷版" / "解析版"
    paper_type = "原卷版" if "原卷" in fn else "解析版"

    # 读 reviewed (可选)
    reviewed_map = {}
    if reviewed_path and reviewed_path.exists():
        rd = json.loads(reviewed_path.read_text(encoding="utf-8"))
        for rq in rd.get("questions", []):
            q_no = rq.get("q_no")
            if q_no is not None:
                reviewed_map[q_no] = rq

    # 写 K 卡
    year_dir = output_dir / f"{source_year}_{paper_type}"
    year_dir.mkdir(parents=True, exist_ok=True)

    ok, fail = 0, 0
    for q in questions:
        q_no = q.get("q_no", 0)
        rev = reviewed_map.get(q_no, {})
        merged = {**q, **rev}  # reviewed 字段覆盖

        # verdict / explanation 从 reviewed 拿
        verdict = rev.get("verdict")
        explanation = rev.get("explanation", "")

        # front (题干): 优先 reviewed.stem
        front = rev.get("stem", q.get("stem", "")).strip()
        if not front:
            front = q.get("stem", "").strip()

        # back (答案): 优先 reviewed.answer
        back = rev.get("answer", q.get("answer_text", ""))
        if not back and q.get("answer_label"):
            back = f"答案: {q.get('answer_label')}"

        # back_detail (解析): 优先 reviewed.explanation
        back_detail = explanation or ""

        # options: 优先 reviewed.variants 的方向（暂不存变式）
        options = q.get("options", [])

        # 检测板块
        module = detect_module(fn, q)

        # 难度: 优先 reviewed.difficulty
        difficulty = rev.get("difficulty", detect_difficulty(q))

        # 知识标签
        kp = rev.get("knowledge_tags", rev.get("key_concepts", [])) or []
        if not kp:
            kp = []
            stem_ = front
            for keyword, tag in [
                ("正弦", "正弦定理"), ("余弦", "余弦定理"),
                ("椭圆", "椭圆"), ("双曲线", "双曲线"), ("抛物线", "抛物线"),
                ("等差", "等差数列"), ("等比", "等比数列"),
                ("概率", "概率"), ("分布列", "分布列与期望"),
                ("导数", "导数"), ("单调", "单调性"), ("极值", "极值"),
                ("立体", "立体几何"), ("正方体", "正方体"),
            ]:
                if keyword in stem_:
                    kp.append(tag)
            if not kp:
                kp.append(module)

        # id
        paper_short = "yj" if "原卷" in fn else "jx"
        kcard_id = f"pt030_{source_year}_q{q_no:02d}_{paper_short}_{module}"

        # variants (从 reviewed)
        variants = rev.get("variants", [])

        # score
        score = q.get("score")

        # chain_id
        chain_id = f"pt030_{source_year}_{paper_type}_{module}"

        kcard = {
            "id": kcard_id,
            "type": f"math_{module}_question",
            "maturity": "REVIEWED" if verdict == "可解" or verdict == "TRUE" else "DRAFT",
            "version": "1.2.6",
            "schema": "v1.2.1",
            "subject": "math",
            "module": module,
            "topic": module,
            "source": f"PT030_{source_year}_{paper_type}",
            "source_type": "高考真题",
            "source_year": source_year,
            "source_paper": paper_type,
            "source_split_file": split_path.name,
            "url": "",
            "verdict": "TRUE" if verdict in ("可解", "TRUE") else (verdict or "PENDING"),
            "difficulty": difficulty,
            "score": score,
            "knowledge_points": kp,
            "front": front,
            "back": back,
            "front_detail": "",
            "back_detail": back_detail,
            "options": options,
            "display_target": ["学习中心"],
            "tags": ["PT030", str(source_year), f"{source_year}年上海{season_short}{paper_type}", module, "自动入库"],
            "parent_cards": [],
            "method_ref": [],
            "explain": back_detail,
            "chain_id": chain_id,
            "related_cards": [],
            "prerequisites": [],
            "variants": variants,
            "estimated_time_minutes": rev.get("estimated_time_minutes"),
            "common_mistakes": rev.get("common_mistakes", []),
            "key_concepts": rev.get("key_concepts", []),
            "provenance": {
                "type": "pt030_pipeline",
                "source": f"PT-030/zhenti/数学/split/{split_path.name}",
                "reviewed": f"PT-030/zhenti/数学/split/{reviewed_path.name}" if reviewed_path else None,
                "extracted_by": "merge_to_kcards.py v1.0",
                "extracted_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "schema_origin": "PT-030 split_v11.json v1.1 + 4step_v1.1",
            },
        }

        out_path = year_dir / f"{kcard_id}.json"
        try:
            out_path.write_text(json.dumps(kcard, ensure_ascii=False, indent=2), encoding="utf-8")
            ok += 1
        except Exception as e:
            print(f"  ERR {kcard_id}: {e}", flush=True)
            fail += 1
    return (ok, fail, len(questions))


def main():
    today = time.strftime("%Y-%m-%d")
    output_dir = KCARDS_ROOT / f"PT030_{today}"
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"[merge] 输出: {output_dir}")

    # 列所有 split
    splits = list(SPLIT_DIR.glob("*_split_v11.json"))
    splits.sort(key=lambda p: p.name)
    total_ok, total_fail, total_q, total_set = 0, 0, 0, 0

    t0 = time.time()
    for sp in splits:
        # 找 reviewed (同 stem)
        rp = sp.parent / f"{sp.stem.replace('_split_v11', '')}_split_v11_reviewed.json"
        if not rp.exists():
            rp = None
        ok, fail, n = merge_split_to_kcards(sp, rp, output_dir)
        total_ok += ok; total_fail += fail; total_q += n
        if n > 0:
            total_set += 1
        flag = "✅" if ok > 0 else "⏭"
        print(f"  {flag} {sp.name[:60]}: {ok}/{n} 题")

    elapsed = time.time() - t0
    print(f"\n[merge] 完成: 套数={total_set} 题数={total_q} ok={total_ok} fail={total_fail} 耗时={elapsed:.1f}s")
    print(f"[merge] 输出目录: {output_dir}")

    # 处理 llm_gen (新母题)
    print(f"\n[merge] 处理 llm_gen ...")
    gen_dir = output_dir / "llm_gen"
    gen_dir.mkdir(parents=True, exist_ok=True)
    gens = list(LLM_GEN_DIR.glob("*_gen.json"))
    gens.sort(key=lambda p: p.name)
    for g in gens:
        theme = g.stem.replace("_gen", "").replace("_test", "")
        try:
            gd = json.loads(g.read_text(encoding="utf-8"))
            questions = gd.get("questions", [])
            for q in questions:
                q_no = q.get("q_no", 0)
                kcard_id = f"pt030_gen_{theme}_q{q_no:02d}"
                kcard = {
                    "id": kcard_id,
                    "type": f"math_{theme}_question",
                    "maturity": "DRAFT",
                    "version": "1.2.6",
                    "schema": "v1.2.1",
                    "subject": "math",
                    "module": theme,
                    "topic": theme,
                    "source": f"PT030_llm_gen_{theme}",
                    "source_type": "LLM生成",
                    "source_year": 0,
                    "source_paper": "AI出题",
                    "url": "",
                    "verdict": "PENDING",
                    "difficulty": "中档",
                    "knowledge_points": q.get("knowledge_points", []),
                    "front": q.get("stem", ""),
                    "back": q.get("answer", ""),
                    "front_detail": "",
                    "back_detail": q.get("explanation", ""),
                    "options": [{"label": k, "text": v} for k, v in q.get("options", {}).items()],
                    "display_target": ["学习中心"],
                    "tags": ["PT030", "llm_gen", theme, "AI出题"],
                    "parent_cards": [],
                    "method_ref": [],
                    "explain": q.get("explanation", ""),
                    "chain_id": f"pt030_gen_{theme}",
                    "related_cards": [],
                    "prerequisites": [],
                    "variants": [{"direction": q.get("variant_direction", "")}],
                    "provenance": {
                        "type": "llm_gen",
                        "source": f"glm-4-flash (PT-030 llm-gen)",
                        "theme": theme,
                        "extracted_by": "merge_to_kcards.py v1.0",
                        "extracted_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                    },
                }
                (gen_dir / f"{kcard_id}.json").write_text(
                    json.dumps(kcard, ensure_ascii=False, indent=2), encoding="utf-8"
                )
                total_ok += 1
                total_q += 1
            print(f"  ✅ {g.name}: {len(questions)} 道母题")
        except Exception as e:
            print(f"  ERR {g.name}: {e}")

    print(f"\n[merge] 总入库: 套数={total_set} + llm_gen 主题={len(gens)} 题数={total_q} ok={total_ok}")
    print(f"[merge] 输出目录: {output_dir}")


if __name__ == "__main__":
    main()
