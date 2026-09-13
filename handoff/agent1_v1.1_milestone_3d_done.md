# Agent 1 → 全部窗口: v1.1 立体几何路标点 — 6 母题变形题字段闭环

**日期**: 2026-09-13
**commit**: `7de2a73` on `knowledge-cards-prod main` (已 push)
**状态**: 第一个路标点（立体几何板块完整显示）的"母题/变形题"维度已就绪

---

## 1. 本次 commit 内容

```
7de2a73 card(math): v1.1 立体几何 6 母题变形题字段 - K10 标 5 变式 + K12-K15 标 91apu 真题
5 files changed, 262 insertions(+), 238 deletions(-)
```

涉及 5 张母题 K 卡（`projects/math/cards/线面平行证明/K1[0-5].json`），加 `derived_from` / `derived_variants` 字段。

## 2. 6 母题变形题映射（v1.1 1.4 规则"每母题至少 1 道变形题"）

| 母题 | 字段 | 引用 | 说明 |
|---|---|---|---|
| K10 | `derived_variants` | `["K16-2","K16-3","K16-4","K16-5","K16-6"]` | v1.0 留下的 5 张变式（改 2 个条件，符合 v1.1 1.4 "真题变形"规则）|
| K11 | `related_zhenti` | `["K_立体_2023qgjl_18","K_立体_2021xgk1_20"]` | 已有，本次不动 |
| K12 | `derived_from` | `"K_立体_2024qgjl_19"` | K12 自身改自这道 2024 全国甲理 19 题 |
| K13 | `derived_from` | `"K_立体_2023qgyl_19"` | K13 自身改自这道 2023 全国乙理 19 题 |
| K14 | `derived_from` | `"K_立体_2021qgyl_18"` | K14 自身改自这道 2021 全国乙理 18 题 |
| K15 | `derived_from` | `"K_立体_2020qg1_18"` | K15 自身是 2024 上海春 18 题；2020qg1_18 是同主题"圆锥+二面角"的 91apu 真题作为变形题 |

## 3. 立体几何板块路标点状态

按 v1.1 1.5 验收标准"立体几何板块完整显示"：

- [x] 6 张母题 K10-K15 存在 + 字段齐全（maturity=REVIEWED, chain, display_target, derived_from/variants 或 related_zhenti）
- [x] 每张母题至少 1 道变形题引用（K11 已 related_zhenti 2 道 + K10 variants 5 张 + K12-K15 derived_from 91apu 真题）
- [x] 5 链 18+ 张 K 卡挂接到对应母题（Agent 2 commit `50fed5b` 已完成，222 张全覆盖）
- [x] 5 张方法论（`projects/math/methods/立体几何/M_立体_*.json`，5 张）
- [ ] 4 Tab 正确显示（依赖 3-UI 窗口，立体几何板块点开可见变形题）— 留给雪薇验证

## 4. 留给其他窗口的接力

### 给 3-UI 窗口（雪薇）
- 打开学习中心数学板块 → 立体几何
- 点开 K10-K15 任一母题，应能看到变形题/真题引用
- 验收通过后此路标点算完成

### 给 Agent 1 自己（继续推进）
- 解析几何、导数、数列、概率统计 4 板块母题 K20-K69 仍 untracked（25 张母题 + 5 main.json + ALL_ZHENTI_INDEX.md）
- 之后按 v1.1 节奏，给这 4 板块母题补 derived_from / derived_variants 字段
- 注意 K11.json 仍是 `M` 状态（50fed5b 之前的修改与本次任务无关，不归本次 commit）

## 5. 已知遗留（不归本次 commit）

- K11.json `M` 状态（50fed5b 之前累积的修改，与本次任务无关）
- `gen_math_reader.py` 1237 行 unstaged diff（Agent 3 之前工作，用户决定）
- 大量 untracked 文件（Agent 1 自己的 K20-K69 工作 + 5 main.json + 历史遗留 .txt 文件）

## 6. v1.1 节奏参考

按 1 窗口（母题扩展+变形题挖掘）路线：
- 本 commit 完成"立体几何板块母题/变形题字段"维度
- 下一步：解析几何板块（20 张母题 K20-K39）
- 目标：分钟级推进，能 commit 就 commit，不等超过 60 分钟
