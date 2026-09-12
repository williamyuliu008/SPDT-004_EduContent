# tools/ — SPDT-004 工具脚本

> 共同仓自动化脚本集合。`tools/_stat_content.py` 是核心长期维护脚本。

---

## `_stat_content.py` — 跨 3 仓统计脚本

### 用途

SPDT-004 项目跨 3 仓分工（共同仓 + 雪薇专精 + 卡片 mirror）。本脚本自动统计 3 仓资产状况，输出统一表格，配套 `docs/migration/ALL_CONTENT_INDEX.md` v1.0 使用。

### 适用范围

| 仓 | 角色 | 主导方 |
|---|---|---|
| `SPDT-004_EduContent` (本仓) | 共同仓（规范 + 工具 + 课程内容）| 雪薇机器 mavis |
| `knowledge-cards-prod` | 雪薇专精（高考 6 学科 + 学习中心）| 雪薇机器 mavis |
| `spdt-content-cards` | 卡片数据 mirror（172 套 K 卡）| 雪薇机器 mavis |

> 刘宇机器本地仓 `D:\2_products\education\SPDT-004_EduContent\` 不直接统计（跨机不可见）。

### 用法

```powershell
# 终端打印
python tools/_stat_content.py

# 同时保存 Markdown 报告
python tools/_stat_content.py --save-md=out/stat_2026-09-12.md

# 跳过校验器（加速, 适合 CI/大批量）
python tools/_stat_content.py --no-validate
```

### 统计维度

#### 共同仓 `SPDT-004_EduContent`
- **5 目录架构完整性**：`1_ingest/` `2_structure/` `3_render/` `4_adapt/` `5_deliver/`
- **products/courses/**：子目录数 + 递归文件数
- **docs/migration/**：迁移文档数
- **autoclaw_kit 21 文件验证**：`1_ingest/autoclaw-k/` 递归 .md/.py/.tpl/.json 数量
- **Git 状态**：branch / commits / last commit

#### 雪薇专精仓 `knowledge-cards-prod`
- **6 学科目录状态**：math + gaokao-{history,geography,politics,chinese,english}
  - 卡片仓 (`cards/`) 递归 .json 数量
  - 真题库 (`zhenti/`) 是否存在
  - 题量（来源标注：`bank_summary` / `k_cards` / 无）
- **zhenti 详细题量**：卷数 / 总题数 / has_answer / has_issue
- **学习中心 `_reader/`**：子目录 + 递归文件
- **`docs/` 文档数**
- **Git 状态**

#### 卡片 mirror 仓 `spdt-content-cards`
- **4 学科 cards/ 套数**：数学 / 历史 / 地理 / 政治（按 `YYYY-MM-DD_概念名` 子目录计数）
- **校验器 PASS 状态**：跑 `1_ingest/autoclaw-k/07_validate.py` 检测 20 项硬指标 + 概念交叉核对
  - 退出码: 0 = PASS, 1 = FAIL (有错误), 2 = WARN (有警告)
  - 数学为空目录跳过

### 输出示例（终端）

```
======================================================================
  SPDT-004 跨仓统计报告  (2026-09-12 14:50)
======================================================================

[1/3] 3 仓总览
----------------------------------------------------------------------
  共同仓          SPDT-004_EduContent       commits=   6  ...
  雪薇专精         knowledge-cards-prod      commits=  65  ...
  卡片 mirror    spdt-content-cards        commits=   —  ...

[2/3] 共同仓 SPDT-004_EduContent
----------------------------------------------------------------------
  5 目录: {'1_ingest': '✅', ..., '5_deliver': '✅'}
  products/courses/  子目录=2  文件=157
  docs/migration/  文件=7
  autoclaw_kit 文件数: 21/21
  git: branch=master  commits=6

[3/3] 雪薇专精仓 knowledge-cards-prod
----------------------------------------------------------------------
  6 学科目录状态:
    ✓ math                      cards= 445  zhenti=-  total_q=   90  (k_cards)
    ✓ gaokao-history            cards= 509  zhenti=✓  total_q= 1602  (bank_summary)
    ✓ gaokao-geography          cards= 402  zhenti=✓  total_q= 2178  (bank_summary)
    ✓ gaokao-politics           cards= 488  zhenti=✓  total_q= 1482  (bank_summary)
    ✗ gaokao-chinese            cards=   0  zhenti=-  total_q=    0  (—)
    ✗ gaokao-english            cards=   0  zhenti=-  total_q=    0  (—)

  zhenti 题量汇总:
    gaokao-history       卷= 44  题= 1602  ans= 22  issue= 6
    gaokao-geography     卷= 46  题= 2178  ans= 11  issue= 0
    gaokao-politics      卷= 35  题= 1482  ans= 19  issue= 2
    合计                   题= 5262

  _reader/  子目录=13  文件=430
  docs/   文件=2
  git: branch=main  commits=65

[卡片 mirror] spdt-content-cards
----------------------------------------------------------------------
  4 学科 cards/ 套数:
    ✗ 数学     套数=  0
    ✓ 历史     套数= 62
    ✓ 地理     套数= 49
    ✓ 政治     套数= 61
    合计     套数=172

  校验器状态:
    历史     PASS  err=0  warn=0
    地理     PASS  err=0  warn=0
    政治     PASS  err=0  warn=0

[汇总]
----------------------------------------------------------------------
  错误: 0  警告: 2
  [WARN] 未闭环学科目录缺失: gaokao-chinese/ (计划中)
  [WARN] 未闭环学科目录缺失: gaokao-english/ (计划中)
======================================================================
```

### 退出码

- `0` — 全部 OK（含警告）
- `1` — 有错误（ERR）

### 配套文档

- `docs/migration/ALL_CONTENT_INDEX.md` — 跨仓索引 v1.0（本脚本是它的数据源）
- `docs/migration/SPDT004_MIGRATION_v2.0_双轨版.md` — 双轨迁移方案
- `docs/migration/SPDT004_HANDOVER_PROMPT_v3.0_给刘宇.md` — v3.0 交接说明
- `1_ingest/autoclaw-k/07_validate.py` — 卡片校验器（被本脚本调用）

### 维护约定

- **每周**：跑一次 `--save-md=out/weekly_stat.md` 提交历史快照
- **季度**：跑一次完整版（默认带校验器），对比 ALL_CONTENT_INDEX 表格，更新跨仓索引
- **schema 变化**：更新本脚本的 `expected` 字段（如新增 7 学科、display_target 字段等）
