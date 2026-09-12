# PT-030 高考真题挖掘项目 — 雪薇端 (主目录)

> **项目编号**：PT-030 (高考备考 / 9 科真题挖掘)
> **雪薇端版本**：v1.0 (2026-09-12)
> **拍板人**：雪薇 (用户) + mavis (本机管家 AI)
> **性质**：雪薇端主导，宇兄端提供工具 + 校验 + 高难度算法

---

## 一、项目范围

PT-030 聚焦上海高考 **9 科** 1990-2025 真题资产挖掘，落到共同仓供跨机协作。

| 维度 | 范围 |
|---|---|
| **目标学科** | 9 科 (语数外 + 史地政 + 物化生) |
| **当前闭环** | 4 学科 (数学/历史/地理/政治) — 5407 题 |
| **待补** | 2 学科 (语文/外语) + 3 学科 (物/化/生) |
| **时间窗** | 1990-2025 (上海卷为主) |
| **方法论** | 4 步法数学 v1.0 + 真题卡规范 v1.1/v1.2 |

---

## 二、雪薇端 vs 宇兄端 (v1.0 协作基线)

### 雪薇端主导（本机 mavis, 路径 D:\Z_学习平台\）

- ✅ **真题挖掘** (数据主导) — 4 学科 5407 题已闭环
- ✅ **知识/真题卡内容生产** — 30 张数学方法论 + 5 张政治方法论 + 49 专题 quiz
- ✅ **链 ID 关联** (v1.2.0 chain 库)
- ✅ **display_target 字段补全** — 默认 `["学习中心"]` (v3.0 拍板)
- ✅ **commit + push 共同仓** (本机作为共同仓主开发者可直推)

### 宇兄端提供（另一台机 autoclaw）

- ✅ **工具开发** — PDF 解析器 (PT-030 C1)、docx 解析器、题目切分算法、双 LLM 协作
- ✅ **validator 校验** — `tools/math_4step_validator.py`
- ✅ **GLM-4-flash 反向推演** — `tools/glm5_check.py`
- ✅ **24 小时内 PR review**
- ✅ **高难度算法组件** (题切分、双 LLM 链)

---

## 三、雪薇端实际工作环境

```
D:\Z_学习平台\                        ← 本机 (mavis) 工作根
├── SPDT-004_EduContent/              ← 共同仓 (本项目所在)
│   ├── PT-030/                       ← 本目录
│   ├── handoff/                      ← 13 份规范 (宇兄端已推)
│   ├── tools/                        ← 5+ 工具 (宇兄端已推)
│   ├── docs/                         ← 架构 + v3.0 拍板 + 治理
│   └── ...
├── knowledge-cards-prod/             ← 雪薇专精仓 (4 学科 5407 题源头)
│   ├── projects/
│   │   ├── math/                     ← 145 张 K 卡
│   │   ├── gaokao-history/           ← 44 卷 1602 题
│   │   ├── gaokao-geography/         ← 46 卷 2178 题
│   │   └── gaokao-politics/          ← 35 卷 1482 题
│   └── docs/ZHENTI_INDEX.md          ← 6 学科架构
└── ... (其他学习工作目录)
```

---

## 四、本目录结构

```
PT-030/
├── README.md                         ← 本文件
├── INDEX.md                          ← 4 学科 5407 题统一索引 + 跨机协作总览
├── curriculum/                       ← 学科结构 (高考 6 学科)
│   ├── 数学.md                       ✅ 已闭环 (145 题)
│   ├── 历史.md                       ✅ 已闭环 (1602 题)
│   ├── 地理.md                       ✅ 已闭环 (2178 题)
│   ├── 政治.md                       ✅ 已闭环 (1482 题)
│   ├── 语文.md                       ⏳ 待补 (D:\E_古诗文\三件套)
│   └── 外语.md                       ⏳ 待补 (D:\F_英语\三件套)
├── zhenti/                           ← 4 学科真题索引 (镜像入口)
│   ├── 数学/INDEX.md
│   ├── 历史/INDEX.md
│   ├── 地理/INDEX.md
│   └── 政治/INDEX.md
├── methodology/                      ← 方法论索引
│   ├── 4step_v1.1.md                 ← 4 步法规范 (链接 handoff/MATH_004)
│   └── display_target_v3.0.md        ← display_target v3.0 拍板 (链接 docs/)
└── mirror/                           ← 待宇兄端 push 后 mirror 资产
    └── v1.2_70题历史/
        └── README.md                 ← RUJING_007 70 题 mirror 入口 (待宇兄 push)
```

---

## 五、立即可做 (本周)

按 `handoff/PT-030_雪薇端启动报告_v1.0.md` 三.高优：

1. **PT-030 统一索引** → 本目录 INDEX.md (4 学科 5407 题总览)
2. **PT-030 目录骨架入共同仓** → 本目录结构 (本 README + INDEX + curriculum + zhenti + methodology + mirror)
3. **2018 上海历史 20 题 v1.1 → v1.2 升级** → `PT-030/zhenti/历史/2018/` (待 upgrade_pps_v11.py 跑)
4. **PT-030 雪薇端 README** → 本文件 (给宇兄端后续参考)

详见 `INDEX.md` 第 6 节。

---

## 六、立即可不做 (按 v1.0 分工)

- ❌ 替宇兄端决定 RUJING APP 客户端开发
- ❌ 替宇兄端做 7 PDT 产品线决策
- ❌ 替宇兄端做工具开发 (PDF 解析器等高难度算法)
- ❌ 替宇兄端决定 `display_target: ["RUJING"]` 内容
- ❌ 改 v1.0 5 核心字段 (chain_id / card_id / schema_version / SOP / 验收标准)

---

## 七、相关资源

- **共同仓 handoff/**：
  - `PT-030_启动指南_v1.0.md` (宇兄端发雪薇端)
  - `PT-030_雪薇端启动报告_v1.0.md` (雪薇端回执)
  - `RUJING_004/005/006/007` 真题卡规范 v1.0 → v1.2 + 70 题扩产
  - `MATH_001/002/004/005` 4 步法 + 网页版 MVP + 母题方法论 + 5 道改造示例
- **共同仓 tools/**：
  - `math_4step_validator.py` `glm5_check.py` `draw_pp_figures.py` `upgrade_pps_v11.py` `parse_pdf_exam.py`
- **雪薇专精仓**：
  - `knowledge-cards-prod/docs/ZHENTI_INDEX.md` (6 学科架构总览)
  - `knowledge-cards-prod/projects/<subj>/` (4 学科源头)
- **共同仓 docs/**：
  - `migration/SPDT004_DUAL_WINDOW_COLLABORATION_v1.0_宇兄给雪薇.md`
  - `migration/SPDT004_SNOWEI_TODO_v1.0.md`
  - `v3.0_approved.md` (display_target 拍板)

---

## 八、变更记录

| 日期 | 版本 | 变更 | 拍板 |
|---|---|---|---|
| 2026-09-12 | v1.0 | 初版（PT-030 雪薇端主目录入共同仓）| mavis 雪薇机器 |
