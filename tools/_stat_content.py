# -*- coding: utf-8 -*-
"""
_stat_content.py — 跨 3 仓统计脚本 (SPDT-004 长期维护)

== 用途 ==
季度 audit / 每周报告: 跨 3 仓统计资产, 输出表格, 配套 ALL_CONTENT_INDEX.md 使用。
- 共同仓 SPDT-004_EduContent (规范 + 工具 + 课程内容)
- 雪薇专精仓 knowledge-cards-prod (高考 6 学科 + 学习中心)
- 卡片数据 mirror 仓 spdt-content-cards (172 套 K 卡)

== 用法 ==
    python tools/_stat_content.py                # 终端打印
    python tools/_stat_content.py --save-md=out.md  # 同时写文件
    python tools/_stat_content.py --no-validate  # 跳过校验器 (加速)

== 输出 ==
- 总览 + 各仓详情
- 错误/警告 (WARN/ERR 前缀)
- 退出码: 0=全过, 1=有错误

== 配套 ==
- docs/migration/ALL_CONTENT_INDEX.md (跨仓索引 v1.0)
- docs/migration/SPDT004_MIGRATION_v2.0_双轨版.md
- tools/_stat_zhenti.py (仅统计 zhenti 题量, 旧脚本)
"""
from __future__ import annotations
import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# === 编码 (Windows 终端) ===
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# === 3 仓根路径 ===
ROOT_COMMON = Path(r"D:\Z_学习平台\SPDT-004_EduContent")
ROOT_PROD = Path(r"D:\Z_学习平台\knowledge-cards-prod")
ROOT_CARDS = Path(r"D:\Z_学习平台\spdt-content-cards")

# === 仓角色定义 ===
WAREHOUSES = [
    ("共同仓", "SPDT-004_EduContent", ROOT_COMMON, "williamyuliu008/SPDT-004_EduContent"),
    ("雪薇专精", "knowledge-cards-prod", ROOT_PROD, "williamyuliu008/knowledge-cards-prod"),
    ("卡片 mirror", "spdt-content-cards", ROOT_CARDS, "williamyuliu008/spdt-content-cards"),
]

# === 收集结果 ===
errors: list[str] = []
warns: list[str] = []


def err(msg: str):
    errors.append(msg)
    print(f"  [ERR] {msg}")


def warn(msg: str):
    warns.append(msg)
    print(f"  [WARN] {msg}")


def ok(msg: str):
    print(f"  [OK] {msg}")


# ============================================================
# 1) 共同仓 SPDT-004_EduContent
# ============================================================
def stat_common() -> dict:
    """统计共同仓 5 目录架构 + 课程/迁移文档 + autoclaw_kit + commits"""
    r = ROOT_COMMON
    info = {
        "root": str(r),
        "exists": r.exists(),
        "five_dirs": {},
        "products_courses_files": 0,
        "products_courses_subdirs": 0,
        "docs_migration_files": 0,
        "autoclaw_kit_files": 0,
        "autoclaw_kit_files_expected": 21,
        "commits": 0,
        "branch": "?",
        "last_commit": "?",
    }
    if not r.exists():
        err(f"共同仓不存在: {r}")
        return info

    # 1. 5 目录架构完整性
    for sub in ("1_ingest", "2_structure", "3_render", "4_adapt", "5_deliver"):
        p = r / sub
        if p.exists() and p.is_dir():
            info["five_dirs"][sub] = "✅"
        else:
            info["five_dirs"][sub] = "❌"
            err(f"共同仓缺 5 目录: {sub}/")

    # 2. products/courses/ 文件数
    courses = r / "products" / "courses"
    if courses.exists():
        info["products_courses_files"] = sum(1 for _ in courses.rglob("*") if _.is_file())
        info["products_courses_subdirs"] = sum(1 for _ in courses.iterdir() if _.is_dir())
    else:
        warn(f"products/courses 不存在: {courses}")

    # 3. docs/migration/ 文件数
    migration = r / "docs" / "migration"
    if migration.exists():
        info["docs_migration_files"] = sum(1 for _ in migration.iterdir() if _.is_file())
    else:
        warn(f"docs/migration 不存在: {migration}")

    # 4. autoclaw_kit 21 文件
    ak = r / "1_ingest" / "autoclaw-k"
    if ak.exists():
        files = list(ak.rglob("*"))
        n_files = sum(1 for f in files if f.is_file())
        info["autoclaw_kit_files"] = n_files
        if n_files == 21:
            ok(f"autoclaw_kit = 21 文件 (匹配预期)")
        else:
            warn(f"autoclaw_kit = {n_files} 文件 (预期 21, 差 {n_files - 21})")
    else:
        err(f"autoclaw_kit 不存在: {ak}")

    # 5. commits 数
    try:
        result = subprocess.run(
            ["git", "-C", str(r), "rev-list", "--count", "HEAD"],
            capture_output=True, text=True, encoding="utf-8", timeout=30
        )
        if result.returncode == 0:
            info["commits"] = int(result.stdout.strip())
        else:
            warn(f"git rev-list 失败: {result.stderr.strip()[:200]}")

        branch_r = subprocess.run(
            ["git", "-C", str(r), "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, encoding="utf-8", timeout=30
        )
        if branch_r.returncode == 0:
            info["branch"] = branch_r.stdout.strip()

        log_r = subprocess.run(
            ["git", "-C", str(r), "log", "-1", "--pretty=format:%h %s"],
            capture_output=True, text=True, encoding="utf-8", timeout=30
        )
        if log_r.returncode == 0:
            info["last_commit"] = log_r.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        warn(f"git 调用失败: {e}")

    return info


# ============================================================
# 2) 雪薇专精仓 knowledge-cards-prod
# ============================================================
def stat_prod() -> dict:
    """统计雪薇专精仓: 6 学科目录 + zhenti 题量 + 学习中心 + 文档"""
    r = ROOT_PROD
    info = {
        "root": str(r),
        "exists": r.exists(),
        "projects": {},          # 学科 -> {cards, zhenti, ...}
        "zhenti_totals": {},     # 学科 -> {volumes, questions, has_answer, has_issue}
        "reader_files": 0,
        "reader_dirs": 0,
        "docs_files": 0,
        "commits": 0,
        "branch": "?",
        "last_commit": "?",
    }
    if not r.exists():
        err(f"雪薇专精仓不存在: {r}")
        return info

    projects = r / "projects"
    if not projects.exists():
        err(f"projects/ 不存在: {projects}")
    else:
        # 6 学科期望: math, gaokao-history, gaokao-geography, gaokao-politics, gaokao-chinese, gaokao-english
        expected = ["math", "gaokao-history", "gaokao-geography", "gaokao-politics",
                    "gaokao-chinese", "gaokao-english"]
        for sub in expected:
            p = projects / sub
            proj_info = {
                "exists": p.exists(),
                "cards_files": 0,         # cards/ 递归 .json 文件数 (含 K 卡)
                "zhenti_exists": False,
                "bank_total_questions": 0,
                "question_source": "",     # "bank_summary" | "k_cards" | "none"
            }
            if p.exists():
                # cards/ 递归 .json 文件数
                cards = p / "cards"
                if cards.exists():
                    proj_info["cards_files"] = sum(
                        1 for f in cards.rglob("*.json") if f.is_file()
                    )
                # zhenti
                zh = p / "zhenti"
                if zh.exists():
                    proj_info["zhenti_exists"] = True
                    bs = zh / "bank_summary.json"
                    if bs.exists():
                        try:
                            data = json.loads(bs.read_text(encoding="utf-8"))
                            proj_info["bank_total_questions"] = sum(
                                b.get("questions", 0) for b in data
                            )
                            proj_info["question_source"] = "bank_summary"
                            info["zhenti_totals"][sub] = {
                                "volumes": len(data),
                                "questions": proj_info["bank_total_questions"],
                                "has_answer": sum(1 for b in data if b.get("has_answer")),
                                "has_issue": sum(1 for b in data if b.get("has_issue")),
                            }
                        except Exception as e:
                            warn(f"[{sub}] bank_summary.json 解析失败: {e}")
                else:
                    # 回退: 无 zhenti/ 时, 用 cards/ 里的 K 卡数作为题量近似
                    # (math 学科是单题 K 卡模式, 145 张)
                    k_count = sum(
                        1 for f in cards.rglob("K??.json") if f.is_file()
                    ) if cards.exists() else 0
                    proj_info["bank_total_questions"] = k_count
                    if k_count > 0:
                        proj_info["question_source"] = "k_cards"
            else:
                if sub in ("gaokao-chinese", "gaokao-english"):
                    warn(f"未闭环学科目录缺失: {sub}/ (计划中)")
                else:
                    err(f"已闭环学科目录缺失: {sub}/")
            info["projects"][sub] = proj_info

    # 学习中心 _reader 文件
    reader = r / "apps" / "learning-hub-v2" / "_reader"
    if reader.exists():
        info["reader_files"] = sum(1 for _ in reader.rglob("*") if _.is_file())
        info["reader_dirs"] = sum(1 for _ in reader.iterdir() if _.is_dir())
    else:
        warn(f"_reader 不存在: {reader}")

    # docs/
    docs = r / "docs"
    if docs.exists():
        info["docs_files"] = sum(1 for _ in docs.iterdir() if _.is_file())
    else:
        warn(f"docs/ 不存在: {docs}")

    # commits
    try:
        result = subprocess.run(
            ["git", "-C", str(r), "rev-list", "--count", "HEAD"],
            capture_output=True, text=True, encoding="utf-8", timeout=30
        )
        if result.returncode == 0:
            info["commits"] = int(result.stdout.strip())
        else:
            warn(f"knowledge-cards-prod git rev-list 失败: {result.stderr.strip()[:200]}")

        branch_r = subprocess.run(
            ["git", "-C", str(r), "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, encoding="utf-8", timeout=30
        )
        if branch_r.returncode == 0:
            info["branch"] = branch_r.stdout.strip()

        log_r = subprocess.run(
            ["git", "-C", str(r), "log", "-1", "--pretty=format:%h %s"],
            capture_output=True, text=True, encoding="utf-8", timeout=30
        )
        if log_r.returncode == 0:
            info["last_commit"] = log_r.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        warn(f"git 调用失败 (prod): {e}")

    return info


# ============================================================
# 3) 卡片数据 mirror 仓 spdt-content-cards
# ============================================================
def stat_cards(run_validate: bool = True) -> dict:
    """统计卡片 mirror 仓: 4 学科 cards/ 套数 + 校验器状态"""
    r = ROOT_CARDS
    info = {
        "root": str(r),
        "exists": r.exists(),
        "subjects": {},      # 学科 -> 套数
        "total_tao": 0,
        "validate_results": {},  # 学科 -> (status, err_count, warn_count)
    }
    if not r.exists():
        err(f"卡片 mirror 仓不存在: {r}")
        return info

    subjects = ["数学", "历史", "地理", "政治"]
    for sub in subjects:
        cards_dir = r / sub / "cards"
        if cards_dir.exists():
            tao = sum(1 for d in cards_dir.iterdir() if d.is_dir()
                      and d.name[:10].count("-") == 2)  # YYYY-MM-DD_xxx
            # 回退方案: 全部子目录数
            if tao == 0:
                tao = sum(1 for d in cards_dir.iterdir() if d.is_dir())
            info["subjects"][sub] = tao
            info["total_tao"] += tao
        else:
            info["subjects"][sub] = 0
            warn(f"卡片仓学科目录缺失: {sub}/cards/")

    # 校验器 (跑 历史 + 地理 + 政治, 数学为空跳过)
    if run_validate:
        validator = ROOT_COMMON / "1_ingest" / "autoclaw-k" / "07_validate.py"
        if not validator.exists():
            warn(f"校验器不存在: {validator}")
        else:
            for sub in ["历史", "地理", "政治"]:
                cards_dir = r / sub / "cards"
                if not cards_dir.exists() or not any(cards_dir.iterdir()):
                    continue
                try:
                    result = subprocess.run(
                        [sys.executable, str(validator), str(cards_dir)],
                        capture_output=True, text=True, encoding="utf-8",
                        timeout=180,
                    )
                    # exit: 0=PASS, 1=有 err, 2=有 warn
                    if result.returncode == 0:
                        status = "PASS"
                    elif result.returncode == 1:
                        status = "FAIL"
                    else:
                        status = "WARN"
                    # 提取 err/warn 计数
                    err_count = result.stdout.count("[ERR] ")
                    warn_count = result.stdout.count("[WARN] ")
                    info["validate_results"][sub] = {
                        "status": status,
                        "exit": result.returncode,
                        "err_count": err_count,
                        "warn_count": warn_count,
                    }
                except subprocess.TimeoutExpired:
                    warn(f"校验器超时 ({sub})")
                except Exception as e:
                    warn(f"校验器异常 ({sub}): {e}")

    return info


# ============================================================
# 渲染: 表格输出
# ============================================================
def render_markdown(common: dict, prod: dict, cards: dict) -> str:
    """渲染成 Markdown 文本"""
    lines: list[str] = []
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    lines.append(f"# SPDT-004 跨仓统计报告 (auto-generated)")
    lines.append("")
    lines.append(f"> **生成时间**: {now}")
    lines.append(f"> **脚本**: `tools/_stat_content.py`")
    lines.append(f"> **配套**: `docs/migration/ALL_CONTENT_INDEX.md` v1.0")
    lines.append("")
    lines.append("---")
    lines.append("")

    # === 总览 ===
    lines.append("## 一、3 仓总览")
    lines.append("")
    lines.append("| 仓 | 路径 | commits | 状态 |")
    lines.append("|---|---|---:|---|")
    for label, name, path, _ in WAREHOUSES:
        if name == "SPDT-004_EduContent":
            c = common.get("commits", "?")
            br = common.get("branch", "?")
        elif name == "knowledge-cards-prod":
            c = prod.get("commits", "?")
            br = prod.get("branch", "?")
        else:
            c = "—"
            br = "—"
        exists = "✅" if Path(path).exists() else "❌"
        lines.append(f"| {label} (`{name}`) | `{path}` | {c} | exists={exists} branch={br} |")
    lines.append("")

    # === 共同仓 ===
    lines.append("---")
    lines.append("")
    lines.append("## 二、共同仓 SPDT-004_EduContent")
    lines.append("")

    if common.get("exists"):
        # 5 目录架构
        lines.append("### 2.1 5 目录架构完整性")
        lines.append("")
        lines.append("| 目录 | 状态 |")
        lines.append("|---|---|")
        for sub, status in common["five_dirs"].items():
            lines.append(f"| `{sub}/` | {status} |")
        lines.append("")

        # products/courses
        lines.append("### 2.2 products/courses/ (课程内容)")
        lines.append("")
        lines.append(f"- 子目录数: **{common['products_courses_subdirs']}**")
        lines.append(f"- 文件数 (递归): **{common['products_courses_files']}**")
        lines.append("")

        # docs/migration
        lines.append("### 2.3 docs/migration/ (迁移文档)")
        lines.append("")
        lines.append(f"- 文件数: **{common['docs_migration_files']}**")
        lines.append("")

        # autoclaw_kit
        n = common["autoclaw_kit_files"]
        exp = common["autoclaw_kit_files_expected"]
        match = "✅" if n == exp else "⚠️"
        lines.append("### 2.4 autoclaw_kit (21 文件验证)")
        lines.append("")
        lines.append(f"- 实际文件数: **{n}** (预期 {exp}) {match}")
        lines.append("")

        # commits
        lines.append("### 2.5 Git 状态")
        lines.append("")
        lines.append(f"- branch: **{common['branch']}**")
        lines.append(f"- commits: **{common['commits']}**")
        lines.append(f"- last: `{common['last_commit']}`")
        lines.append("")
    else:
        lines.append("> 共同仓不存在，跳过详情")
        lines.append("")

    # === 雪薇专精仓 ===
    lines.append("---")
    lines.append("")
    lines.append("## 三、雪薇专精仓 knowledge-cards-prod")
    lines.append("")

    if prod.get("exists"):
        # 6 学科目录
        lines.append("### 3.1 projects/ 6 学科目录")
        lines.append("")
        lines.append("| 学科 | 状态 | cards/ .json | zhenti/ | 总题数 | 题源 |")
        lines.append("|---|---|---:|---|---:|---|")
        for sub, pinfo in prod["projects"].items():
            status = "✅" if pinfo["exists"] else "❌"
            zhenti = "✅" if pinfo["zhenti_exists"] else "—"
            qsrc = pinfo.get("question_source", "—") or "—"
            lines.append(
                f"| {sub} | {status} | {pinfo['cards_files']} | {zhenti} | "
                f"{pinfo['bank_total_questions']} | {qsrc} |"
            )
        lines.append("")

        # zhenti 详情
        if prod["zhenti_totals"]:
            lines.append("### 3.2 zhenti/ 题量详情 (4 学科)")
            lines.append("")
            lines.append("| 学科 | 卷数 | 总题数 | has_answer | has_issue |")
            lines.append("|---|---:|---:|---:|---:|")
            total_q = 0
            for sub, zt in prod["zhenti_totals"].items():
                lines.append(
                    f"| {sub} | {zt['volumes']} | {zt['questions']} | {zt['has_answer']} | {zt['has_issue']} |"
                )
                total_q += zt["questions"]
            lines.append(f"| **合计** | - | **{total_q}** | - | - |")
            lines.append("")

        # 学习中心
        lines.append("### 3.3 apps/learning-hub-v2/_reader/ 学习中心")
        lines.append("")
        lines.append(f"- 子目录数: **{prod['reader_dirs']}**")
        lines.append(f"- 文件数 (递归): **{prod['reader_files']}**")
        lines.append("")

        # docs
        lines.append("### 3.4 docs/ 文档数")
        lines.append("")
        lines.append(f"- 文件数: **{prod['docs_files']}**")
        lines.append("")

        # commits
        lines.append("### 3.5 Git 状态")
        lines.append("")
        lines.append(f"- branch: **{prod['branch']}**")
        lines.append(f"- commits: **{prod['commits']}**")
        lines.append(f"- last: `{prod['last_commit']}`")
        lines.append("")
    else:
        lines.append("> 雪薇专精仓不存在，跳过详情")
        lines.append("")

    # === 卡片 mirror ===
    lines.append("---")
    lines.append("")
    lines.append("## 四、卡片数据 mirror 仓 spdt-content-cards")
    lines.append("")

    if cards.get("exists"):
        # 4 学科
        lines.append("### 4.1 4 学科 cards/ 套数")
        lines.append("")
        lines.append("| 学科 | 套数 | 备注 |")
        lines.append("|---|---:|---|")
        for sub, tao in cards["subjects"].items():
            note = ""
            if tao == 0:
                note = "(空目录)"
            lines.append(f"| {sub} | {tao} | {note} |")
        lines.append(f"| **合计** | **{cards['total_tao']}** | - |")
        lines.append("")

        # 校验器
        if cards["validate_results"]:
            lines.append("### 4.2 校验器 PASS 状态 (07_validate.py)")
            lines.append("")
            lines.append("| 学科 | 状态 | 错误数 | 警告数 |")
            lines.append("|---|---|---:|---:|")
            for sub, vr in cards["validate_results"].items():
                icon = {"PASS": "✅", "WARN": "⚠️", "FAIL": "❌"}.get(vr["status"], "?")
                lines.append(
                    f"| {sub} | {icon} {vr['status']} | {vr['err_count']} | {vr['warn_count']} |"
                )
            lines.append("")

    # === 错误/警告汇总 ===
    lines.append("---")
    lines.append("")
    lines.append("## 五、错误/警告汇总")
    lines.append("")
    if not errors and not warns:
        lines.append("> ✅ 无错误无警告")
    else:
        if errors:
            lines.append(f"### 错误 ({len(errors)})")
            for e in errors:
                lines.append(f"- [ERR] {e}")
            lines.append("")
        if warns:
            lines.append(f"### 警告 ({len(warns)})")
            for w in warns:
                lines.append(f"- [WARN] {w}")
            lines.append("")

    lines.append("---")
    lines.append("")
    lines.append(f"_本报告由 `tools/_stat_content.py` 自动生成, {now}_")
    lines.append("")

    return "\n".join(lines)


# ============================================================
# 终端表格输出 (精简版)
# ============================================================
def render_terminal(common: dict, prod: dict, cards: dict) -> None:
    """终端打印 (人类可读, 不依赖 Markdown 渲染)"""
    print()
    print("=" * 70)
    print(f"  SPDT-004 跨仓统计报告  ({datetime.now().strftime('%Y-%m-%d %H:%M')})")
    print("=" * 70)

    # 总览
    print("\n[1/3] 3 仓总览")
    print("-" * 70)
    for label, name, path, _ in WAREHOUSES:
        if name == "SPDT-004_EduContent":
            c = common.get("commits", "?")
        elif name == "knowledge-cards-prod":
            c = prod.get("commits", "?")
        else:
            c = "—"
        print(f"  {label:12s} {name:25s} commits={c:>4}  {path}")

    # 共同仓
    print("\n[2/3] 共同仓 SPDT-004_EduContent")
    print("-" * 70)
    if common.get("exists"):
        print(f"  5 目录: {common['five_dirs']}")
        print(f"  products/courses/  子目录={common['products_courses_subdirs']}  "
              f"文件={common['products_courses_files']}")
        print(f"  docs/migration/  文件={common['docs_migration_files']}")
        print(f"  autoclaw_kit 文件数: {common['autoclaw_kit_files']}/21")
        print(f"  git: branch={common['branch']}  commits={common['commits']}")
    else:
        print("  [跳过] 共同仓不存在")

    # 雪薇专精
    print("\n[3/3] 雪薇专精仓 knowledge-cards-prod")
    print("-" * 70)
    if prod.get("exists"):
        print(f"  6 学科目录状态:")
        for sub, pinfo in prod["projects"].items():
            mark = "✓" if pinfo["exists"] else "✗"
            zh = "✓" if pinfo["zhenti_exists"] else "-"
            qsrc = pinfo.get("question_source", "") or "—"
            print(f"    {mark} {sub:25s} cards={pinfo['cards_files']:>4}  "
                  f"zhenti={zh}  total_q={pinfo['bank_total_questions']:>5}  ({qsrc})")

        if prod["zhenti_totals"]:
            print(f"\n  zhenti 题量汇总:")
            total_q = 0
            for sub, zt in prod["zhenti_totals"].items():
                print(f"    {sub:20s} 卷={zt['volumes']:>3}  题={zt['questions']:>5}  "
                      f"ans={zt['has_answer']:>3}  issue={zt['has_issue']:>2}")
                total_q += zt["questions"]
            print(f"    {'合计':20s} 题={total_q:>5}")

        print(f"\n  _reader/  子目录={prod['reader_dirs']}  文件={prod['reader_files']}")
        print(f"  docs/   文件={prod['docs_files']}")
        print(f"  git: branch={prod['branch']}  commits={prod['commits']}")
    else:
        print("  [跳过] 雪薇专精仓不存在")

    # 卡片 mirror
    print("\n[卡片 mirror] spdt-content-cards")
    print("-" * 70)
    if cards.get("exists"):
        print(f"  4 学科 cards/ 套数:")
        for sub, tao in cards["subjects"].items():
            mark = "✓" if tao > 0 else "✗"
            print(f"    {mark} {sub:6s} 套数={tao:>3}")
        print(f"    {'合计':6s} 套数={cards['total_tao']:>3}")

        if cards["validate_results"]:
            print(f"\n  校验器状态:")
            for sub, vr in cards["validate_results"].items():
                print(f"    {sub:6s} {vr['status']}  err={vr['err_count']}  warn={vr['warn_count']}")
    else:
        print("  [跳过] 卡片 mirror 仓不存在")

    # 错误/警告
    print("\n[汇总]")
    print("-" * 70)
    print(f"  错误: {len(errors)}  警告: {len(warns)}")
    if errors:
        for e in errors:
            print(f"  [ERR] {e}")
    if warns:
        for w in warns:
            print(f"  [WARN] {w}")
    if not errors and not warns:
        print("  ✅ 无错误无警告")
    print("=" * 70)


# ============================================================
# 主入口
# ============================================================
def main():
    parser = argparse.ArgumentParser(
        description="SPDT-004 跨 3 仓统计脚本 (长期维护)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="示例:\n"
               "  python tools/_stat_content.py\n"
               "  python tools/_stat_content.py --save-md=out/stat.md\n"
               "  python tools/_stat_content.py --no-validate\n",
    )
    parser.add_argument(
        "--save-md",
        type=str, default=None,
        help="保存 Markdown 报告到指定路径",
    )
    parser.add_argument(
        "--no-validate",
        action="store_true",
        help="跳过校验器 (07_validate.py), 加速运行",
    )
    args = parser.parse_args()

    print("[*] 开始跨仓统计...")
    common = stat_common()
    prod = stat_prod()
    cards = stat_cards(run_validate=not args.no_validate)

    # 终端打印
    render_terminal(common, prod, cards)

    # 可选: 保存 Markdown
    if args.save_md:
        md_path = Path(args.save_md)
        md_path.parent.mkdir(parents=True, exist_ok=True)
        md_text = render_markdown(common, prod, cards)
        md_path.write_text(md_text, encoding="utf-8")
        print(f"\n[OK] Markdown 报告已保存: {md_path}")

    # 退出码
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
