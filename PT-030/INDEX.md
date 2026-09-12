# PT-030 高考真题挖掘项目 — 统一索引 INDEX

> **版本**：v1.0 (2026-09-12)
> **拍板人**：雪薇机器 (mavis)
> **配套**：`README.md` (本目录)
> **范围**：4 学科已闭环 (5407 题) + 2 待补 (语文/外语) + 共同仓 handoff/tools 资产索引

---

## 一、4 学科已闭环盘点 (共 5407 题)

| 学科 | 卷数 | 总题数 | 覆盖年份 | 闭环状态 | 源头 (雪薇专精仓) |
|---|---:|---:|---|---|---|
| **数学** | 145 (单题 K 卡) | **145** | 2018-2024 (91apu) + 2008-2023 (上海) | ✅ 闭环 | `knowledge-cards-prod/projects/math/cards/` |
| **历史** | 44 (38+6 占位) | **1602** | 1990-2017 + 2024 | ✅ 闭环 | `knowledge-cards-prod/projects/gaokao-history/zhenti/` |
| **地理** | 46 | **2178** | 1990-2021+2024 | ✅ 闭环 | `knowledge-cards-prod/projects/gaokao-geography/zhenti/` |
| **政治** | 35 (33+2 源空) | **1482** | 1990-2018 | ✅ 闭环 | `knowledge-cards-prod/projects/gaokao-politics/zhenti/` |
| **合计** | — | **5407** | 1990-2024 | 4 closed | — |

> 注：6 个历史占位 (`h1996/h1997/h2001_12/13/h2003/h2004`) 已在 commit `0d13fdc` 修复；
> 2 个政治源空 (`p2001_12/p2002_14`) 保留 `has_issue` 标记追溯。

### 1.1 学科目录布局 (雪薇专精仓)

```
knowledge-cards-prod/projects/
├── math/
│   ├── cards/                        # 145 张真题 K 卡 (6 板块)
│   ├── methods/                      # 30 张方法论卡 v2.0.0
│   └── ALL_ZHENTI_INDEX.md           # 数学专属索引
│
├── gaokao-history/
│   ├── cards/                        # 60+ 专题 v0.4 raw (不入 zhenti 流程)
│   ├── curated/                      # 三件套精写 7 专题 38 quiz
│   ├── methods/                      # 待建
│   └── zhenti/                       # 1990-2017 + 2024 (44 卷)
│       ├── papers/h1990_01.json ~ h2017_44.json (38 卷)
│       ├── sources/                  # 2 个 2024 .txt
│       ├── tools/                    # 转换/校验脚本
│       └── bank_summary.json         # 索引 (44 条)
│
├── gaokao-geography/
│   ├── cards/                        # 49 专题 v0.4 (空目录, 需催另一 AI)
│   ├── curated/                      # 三件套精写 19 专题 88 quiz
│   ├── methods/                      # 待建
│   └── zhenti/                       # 1990-2021+2024 (46 卷)
│
└── gaokao-politics/
    ├── cards/                        # 60 专题 v0.4 raw
    ├── curated/                      # 三件套精写 23 专题 99 quiz
    ├── methods/                      # 5 张方法论
    └── zhenti/                       # 1990-2018 (35 卷)
```

---

## 二、2 学科待补 (语文/外语)

| 学科 | 题数 | 状态 | 外部资源 |
|---|---:|---|---|
| **语文** (古诗文) | 0 | ⏳ 待补 | `D:\E_古诗文\三件套\` (实词过/断句方法/送别诗母题) |
| **外语** (英语) | 0 | ⏳ 待补 | `D:\F_英语\三件套\` (定语从句/时态总览/阅读细节题策略) |

**优先级**：
- 真题库 (上海 2018-2024) — **高优**
- 三件套精写合并入 `curated/` — **中优**

### 2.1 待建目录

```
knowledge-cards-prod/projects/
├── gaokao-chinese/                   # 语文
│   ├── cards/                        # 待产 (spdt 排期 47 概念)
│   ├── curated/                      # 三件套精写 (待合并)
│   ├── methods/                      # 待建
│   └── zhenti/                       # 待爬 (上海 2018-2024)
│
└── gaokao-foreign/                   # 外语
    ├── cards/                        # 待产 (spdt 排期 57 概念)
    ├── curated/                      # 三件套精写 (待合并)
    ├── methods/                      # 待建
    └── zhenti/                       # 待爬 (上海 2018-2024)
```

---

## 三、共同仓 handoff/ 规范索引 (13 份)

| 编号 | 文档 | 用途 | 来源 |
|---|---|---|---|
| `PT-030_启动指南_v1.0.md` | PT-030 雪薇端启动指南 (5 步流程) | 雪薇端第一周执行手册 | 宇兄端 |
| `PT-030_雪薇端启动报告_v1.0.md` | 雪薇端启动报告 (盘点 + 立即可做) | 雪薇端回执 | 雪薇端 |
| `RUJING_004_真题卡片规范_v1.0.md` | 真题卡字段标准 v1.0 | 数据 schema 起点 | 宇兄端 |
| `RUJING_005_真题卡试点报告_2018上海历史.md` | 2018 上海历史 20 题 v1.1 试点 | 首批实战数据 | 宇兄端 |
| `RUJING_006_真题卡规范_v1.1修订_2026-09-10.md` | v1.0 → v1.1 修订 (加 11 字段) | 升级规范 | 宇兄端 |
| `RUJING_007_真题卡v1.2扩产报告_70题.md` | 2017+2018+2019 上海历史 70 题 v1.2 | v1.2 扩产报告 | 宇兄端 |
| `RUJING_007_真题卡扩产报告_2018-2019_2026-09-10.md` | 同 007 子集 (2018-2019) | v1.2 子集 | 宇兄端 |
| `MATH_001_4步法_概念-母题-变形-综合_v1.0.md` | 4 步法 v1.0 规范 | 工具方法论 | 宇兄端 |
| `MATH_002_网页版MVP架构_v1.0.md` | 网页版 MVP 架构 | 前端架构 | 宇兄端 |
| `MATH_004_母题构建方法论_v1.1.md` | 母题构建方法论 v1.1 (11 扩展字段) | 母题方法论 | 宇兄端 |
| `MATH_005_5道历史真题改造为母题原型.md` | 5 道历史真题改造示例 | 4 步法 + PT-030 桥接 | 宇兄端 |
| `SPDT004_DUAL_WINDOW_COLLABORATION_v1.0_给雪薇窗口.md` | 双窗口协作 v1.0 (协作基线) | v1.0 拍板 | 宇兄端 |
| `SPDT004_DUAL_WINDOW_COLLABORATION_v1.1_PT-030分工修正.md` | 双窗口协作 v1.1 (PT-030 分工修正) | v1.1 拍板 | 宇兄端 |
| `SPDT004_HANDOVER_PROMPT_v2.0_给XW窗口.md` | 雪薇窗口 v2.0 HANDOVER | 工作交接 | 宇兄端 |
| `SPDT004_MIGRATION_v2.0_双轨版.md` | 双轨迁移 v2.0 | 阶段文档 | 宇兄端 |
| `rujing.md` | 汝婧综合 | rujing 总览 | 宇兄端 |
| `RUJING_002_ebook_设计经验沉淀_v0.3.8.md` | ebook 设计经验 | 排版沉淀 | 宇兄端 |
| `RUJING_003_产品定义_2026-09-10.md` | 汝婧产品定义 v3 | 产品 spec | 宇兄端 |

> 注：13 份是按 PT-030 直接相关的核心规范计；含子集/总览共 18 份。

---

## 四、共同仓 tools/ 5 核心工具索引

| 工具 | 用途 | 雪薇端用法 |
|---|---|---|
| **`math_4step_validator.py`** | JSON schema 校验 (pydantic 风格) | 跑回归 + 入仓前 PASS/FAIL |
| **`glm5_check.py`** | GLM-4-flash 反向推演 (合理性门) | 绕开 GLM-5 reasoning 占满 |
| **`draw_pp_figures.py`** | matplotlib SVG 配图生成 | 几何/函数图 |
| **`upgrade_pps_v11.py`** | v1.0 → v1.1 升级 (批量加 11 字段) | 2018 上海历史 20 题升级 |
| **`parse_pdf_exam.py`** | PT-030 C1 PDF 解析器 (pypdf 6.10.2) | 原始 PDF → raw JSON |

其他可用：
- `accuracy_auditor.py` (精度审计)
- `add_display_target_v1.py` (display_target 补全)
- `fix_bom_variants.py` (BOM 修复)
- `fix_hp005.py` `fix_hp_v11.py` (PP 卡修复)
- `list_2018_qs.py` (2018 上海历史题列表)
- `replace_pp002_v11.py` (PP002 v1.1 替换)
- `window_check.py` (窗口检查)
- `_add_display_target.py` `_stat_content.py` (本机工具, 1340+ 跨仓统计)

---

## 五、v1.0 协作基线分工 (commit 543c7d5)

### 5.1 雪薇窗口职责

- ✅ 真题挖掘 (数据主导)
- ✅ 知识/真题卡内容生产
- ✅ 链 ID 关联 (v1.2.0 chain 库)
- ✅ display_target 字段 (默认 `["学习中心"]`)
- ✅ commit + push 共同仓

### 5.2 宇兄窗口职责

- ✅ 工具开发 (PDF 解析器、切分算法、双 LLM 协作)
- ✅ validator 校验
- ✅ GLM-4-flash 反向推演
- ✅ 24 小时内 PR review
- ✅ 写难度高的算法组件

### 5.3 v1.0 5 核心字段 (雪薇端不修改)

| 字段 | 说明 | 修改权 |
|---|---|---|
| `chain_id` | 链 ID 关联 | 宇兄端 |
| `card_id` | 卡片 ID | 宇兄端 |
| `schema_version` | schema 版本 | 宇兄端 |
| `SOP` | 标准作业流程 | 宇兄端 |
| 验收标准 | validator PASS 规则 | 宇兄端 |

---

## 六、雪薇端立即可做 (按宇兄端指南 + v1.0 分工)

### 高优 (本周)

1. **PT-030 统一索引** → 本 INDEX.md (4 学科 5407 题总览) ✅ 已完成
2. **PT-030 目录骨架入共同仓** → 本目录结构 (README + INDEX + curriculum + zhenti + methodology + mirror) ✅ 已完成
3. **2018 上海历史 20 题 v1.1 → v1.2 升级** → `PT-030/zhenti/历史/2018/` (待 upgrade_pps_v11.py 跑)
4. **PT-030 雪薇端 README 写** → 本目录 README.md ✅ 已完成

### 中优 (本月)

5. **语文 zhenti 启动** → 爬上海 2018-2024 (高优)
6. **外语 zhenti 启动** → 爬上海 2018-2024 (高优)
7. **2017/2019/2024 上海历史扩产** → 宇兄端 v1.2 已做 70 题，雪薇端接力
8. **数学 1990-2025 扩产** → 145 → 扩 (commit b877fcf 后扩)
9. **地理/政治 1990-2025 扩产** → 2178/1482 题基础上扩
10. **历史方法论卡 5 张** → 按数学 6 板块 × 5 方法模式
11. **地理方法论卡 5 张** → 同上

### 低优 (下季度)

12. PT-031 通识 / PT-032 高校课件 (不在雪薇端高考专精内，按 v1.0 协作基线由宇兄端主导)
13. 古史/墨骨山河续作 (PT-038，宇兄端主，雪薇端 review)

---

## 七、跨机数据流

```
雪薇端 D:\Z_学习平台\ (本机 mavis)
   ↓
   1. 读共同仓 handoff/ 规范
   2. 用 4 学科 zhenti/ 数据 (knowledge-cards-prod)
   3. 用 tools/ 工具链 (math_4step_validator 等)
   ↓
4. 产出：4 学科 zhenti JSON + 升级到 v1.2
   ↓
5. commit + push 共同仓 (PT-030/ 目录)
   ↓
宇兄端 (另一台机 autoclaw)
   ↓
6. 24h 内 PR review + validator 跑回归
7. 反馈 PASS/FAIL
   ↓
雪薇端修复 → 合入
```

### 7.1 mirror 队列 (待宇兄端 push)

| 资产 | 状态 | 入口 | 备注 |
|---|---|---|---|
| **v1.2 70 题历史 (2017+2018+2019)** | ⏳ 宇兄端机器未 push | `PT-030/mirror/v1.2_70题历史/` | 详见 RUJING_007 |
| **PT-030 C1 PDF 解析器数据** | ✅ 工具已推 (commit 2590401) | 共同仓 `tools/parse_pdf_exam.py` | 雪薇端可跑回归 |
| **语文/外语 zhenti 增量** | ⏳ 待爬 | 待建 | 优先级高 |

---

## 八、4 学科 zhenti 索引 (本仓镜像入口)

| 学科 | 入口 | 数据源头 | 本仓镜像 |
|---|---|---|---|
| **数学** | `zhenti/数学/INDEX.md` | `knowledge-cards-prod/projects/math/ALL_ZHENTI_INDEX.md` | 本目录 `zhenti/数学/` |
| **历史** | `zhenti/历史/INDEX.md` | `knowledge-cards-prod/projects/gaokao-history/zhenti/bank_summary.json` (44 卷 1602 题) | 本目录 `zhenti/历史/` |
| **地理** | `zhenti/地理/INDEX.md` | `knowledge-cards-prod/projects/gaokao-geography/zhenti/bank_summary.json` (46 卷 2178 题) | 本目录 `zhenti/地理/` |
| **政治** | `zhenti/政治/INDEX.md` | `knowledge-cards-prod/projects/gaokao-politics/zhenti/bank_summary.json` (35 卷 1482 题) | 本目录 `zhenti/政治/` |

---

## 九、变更记录

| 日期 | 版本 | 变更 | 拍板 |
|---|---|---|---|
| 2026-09-12 | v1.0 | 初版（4 学科 5407 题总览 + 共同仓资产索引 + 跨机数据流 + 立即可做 4 项）| mavis 雪薇机器 |
