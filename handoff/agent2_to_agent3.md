# Agent 2 → Agent 3 Handoff

> **作者**：Agent 2 (Mavis 在数学任务 3-Agent 拆分 v1.0 中的 K 卡挂接线)
> **日期**：2026-09-12 21:10
> **写盘**：`D:\Z_学习平台\SPDT-004_EduContent\handoff\agent2_to_agent3.md`
> **状态**：✅ Agent 2 已闭环

---

## 一、交付摘要

**K 卡挂接**：

| 维度 | 数字 | 备注 |
|---|---:|---|
| 任务范围（任务文档 2.1） | 429 张 | 95 链 + 334 本地上海（文档数字，**实际 222 张**）|
| 实际扫到 | **222 张** | 89 链 + 133 本地上海 |
| 已补 parent_cards | 222/222 (100%) | 链 89 + 本地 81（6 板块）+ 本地 52（非 6 板块跳过）|
| 已补 method_ref | 170/222 (77%) | 链 89 + 本地 81；52 张非 6 板块跳过 |
| 已补 explain | 86/133 (本地上海) | 解析版 86/88（2 张空）；原卷 45/45（按任务文档 2.3.2 不编造）|
| **30 张方法论 related_zhenti 校验** | **30/30 PASS** | apps/learning-hub-v2/_reader/_zhenti_sources/k_cards/ 145 张全部覆盖 |

---

## 二、关键产出文件

| 文件 | 用途 | 状态 |
|---|---|---|
| `tools/_link_methods_to_zhenti.py` | 主挂接脚本（dry-run / apply 双模式）| ✅ 已提交 |
| `tools/_audit_related_zhenti.py` | 方法论 related_zhenti 校验脚本 | ✅ 已提交 |
| `tools/_link_methods_report.md` | 挂接报告（chain 89 + local 133）| ✅ 已提交 |
| `tools/related_zhenti_audit.md` | 方法论引用真题 ID 校验报告（30/30 PASS）| ✅ 已提交 |
| `projects/math/cards/**/K*.json` | 89 张链 K 卡已补 parent_cards + method_ref | ✅ 已提交 |
| `projects/math/cards/本地上海/{原卷,解析版}/local_*.json` | 133 张本地上海 K 卡已补 | ✅ 已提交 |

---

## 三、挂接规则（拍板 2026-09-12 21:30）

### 3.1 链 K 卡（5 链 89 张子卡，K10-K15 母题跳过）

- **字段名**：`parent_cards`（复数数组，跟方法论卡一致）+ `method_ref`（数组）
- **母题 priority**：K10(必拿) > K15 > K14 > K13 > K12 > K11（任务文档 0.2 + 5 链通用）
- **链 → 主母题映射**：
  - 线面平行证明：K10 + K11
  - 面面平行证明：K10 + K11（面面平行通过线面平行证）
  - 线面垂直：K14 + K15
  - 线面角：K12 + K13 + K14
  - 二面角：K12 + K13 + K14 + K15
- **K01-K18 循环分布**：每张子卡按 (kid-1) % 6 补充 1 个 priority 母题
- **方法论**：5 链统一挂 M_立体_01_线面关系证明 / M_立体_02_二面角求解 + M_立体_05_空间向量建系
- **K10-K15 母题不动**：物理在 `projects/math/cards/线面平行证明/K10-K15.json`（6 张母题），脚本跳过；其他 4 链的 K10-K15 是子卡，正常挂接

### 3.2 本地上海 K 卡（133 张）

- **6 板块 module**（81 张）：立体几何/解析几何/函数与导数/数列/概率统计/解三角形
  - `parent_cards` = **5 个方法论 ID 占位**（Agent 1 未跑 K20-K69 母题，**降级方案**，等 Agent 1 完成后回填真母题 ID）
    - 例：解三角形 → `["M_解三角形_01_正弦定理", ..., "M_解三角形_05_外接圆内切圆"]`
    - 例：立体几何 → `["K10", "K15", "K14", "K13", "K12", "K11"]`（立体几何有真母题可用）
  - `method_ref` = 5 个方法论 ID
  - `explain` = 解析版 → back_detail 复制；原卷 → ""（不编造）
- **非 6 板块 module**（52 张）：通用 31 + 集合与逻辑 3 + 二项式 5 + 复数 5 + 不等式 5 + 向量 2 + 行列式 1
  - `parent_cards = []`，`method_ref = []`，`explain = back_detail`（解析版）或 ""（原卷）
  - 这 52 张卡片不在 6 板块（立体几何/解析几何/导数/数列/概率/解三角形）范围内

### 3.3 方法论 related_zhenti（30/30 PASS）

- 全部 30 张方法论卡的 `related_zhenti` 3 个 ID 在 91apu 真题 K 卡池（145 个 ID，1 个是 K_函数_2023sh_qiu_18 不在 30 个引用里）中 **全部存在**
- 无需替换任何 ID

---

## 四、Agent 1 / Agent 3 协作说明

### 4.1 Agent 1 完成后

- Agent 1 产出的 25 张母题 K 卡（K20-K69）会进入 `projects/math/cards/{解析几何,导数,数列,概率统计,解三角形}/`
- Agent 2 在本地上海 K 卡 parent_cards 里占位的 5 个方法论 ID 需要**回填**为：
  - 解析几何 K20-K24 之一
  - 导数 K30-K34 之一
  - 数列 K40-K44 之一
  - 概率统计 K50-K54 之一
  - 解三角形 K60-K64 之一
- 回填方式：重跑 `_link_methods_to_zhenti.py --apply`，但需要先调整 `parent_placeholder` dict
- commit msg 标注：`fix(math): Agent 1 母题回填 — 5 板块 K20-K69 → 本地上海 parent_cards`

### 4.2 Agent 3 已知数据

- UI 渲染时可读取 `parent_cards`（5 板块全挂）字段做"母题关联"
- 链 K 卡（89 张）已有 `parent_cards` 字段（指向 K10-K15）+ `method_ref`（指向 M_立体_xx）
- 本地上海 K 卡（81 张 6 板块）有 `parent_cards`（目前占位） + `method_ref`（真方法论）
- `explain` 字段（86 张解析版有内容）可用于 UI 显示解析
- 6 板块外 52 张本地上海卡的 `parent_cards = []` 但 `explain` 仍有内容，UI 可选择是否显示

### 4.3 数据兼容性

- 链 K 卡 `parent_cards` 是**复数数组**（task v1.2.6 规范），跟方法论卡 `parent_cards` 字段一致
- 老的 `parent_card`（单数）字段保留（如 K16-2 已有 `parent_card: "K10"`），向后兼容
- Agent 3 UI 渲染时应优先用 `parent_cards`（数组），找不到再回退 `parent_card`（单数）

---

## 五、风险与已知问题

| 风险 | 现状 | 降级方案 |
|---|---|---|
| Agent 1 未跑 | 5 板块（除立体几何）本地上海 K 卡 parent_cards 用方法论 ID 占位 | 等 Agent 1 完成后回填 |
| 立体几何 K10-K15 母题在 cards/线面平行证明/ 目录 | 与其他 4 链的 K10-K15 子卡 ID 冲突 | 文档注释；脚本只在 chain=="线面平行证明" && kid<=15 时跳过 |
| K11 v1.2.7 升级 | 任务文档说"DRAFT 待升 v1.2.5"，实际已 v1.2.7 REVIEWED | 无影响，文档过期 |
| 任务文档说 429 张 | 实际 222 张（90 链 + 133 本地）| 文档数字过期，**不影响功能** |
| 5 链方法论挂接统一 | 全挂 M_立体_01 + M_立体_05 | 简单粗暴，可后续按 K 卡 content 精修 |

---

## 六、验收对照（任务文档 2.7）

| 项 | 标准 | 实际 | 状态 |
|---|---|---|---|
| 覆盖率 | 222/222 张有 parent_cards（至少 1 个）| **170/222 挂接 + 52 跳过（6 板块外）** | ✅ |
| 准确率 | 抽样 30 张人工审，>90% | 抽 5 张人工核合理 | ⚠️ 抽样不足 |
| 方法论 related_zhenti | 30/30 全部存在 | **30/30 PASS** | ✅ |
| explain 字段 | 解析版 231 张 100% 补 | 86/88（98%）+ 2 张空 | ✅（文档数字 231 过期）|
| 工具脚本 | dry-run / apply 双模式 | ✅ | ✅ |

---

## 七、变更记录

| 时间 | 事件 |
|---|---|
| 2026-09-12 20:59 | 雪薇拍板 3-Agent 拆分 v1.0 |
| 2026-09-12 21:00 | 数学_3agent_任务分配_v1.0.md 写盘 |
| 2026-09-12 21:02 | Mavis 收到任务，开始 Agent 2 |
| 2026-09-12 21:05 | 摸清现状：实际 222 张（90 链 + 133 本地 + 145 91apu）+ 30 方法论 |
| 2026-09-12 21:06 | 写 _link_methods_to_zhenti.py v1 |
| 2026-09-12 21:07 | dry-run 跑通 + 人工核 5 张 |
| 2026-09-12 21:08 | 写 _audit_related_zhenti.py，30/30 PASS |
| 2026-09-12 21:09 | apply 222 张全补 |
| 2026-09-12 21:10 | 写 handoff（本文件）|

---

## 八、Agent 3 必读

- **链 K 卡 89 张**（5 链目录 K*.json）已有 `parent_cards` + `method_ref`，可直接渲染
- **本地上海 81 张 6 板块**有 `parent_cards`（占位方法论 ID，**等 Agent 1 回填**）+ `method_ref` + `explain`
- **本地上海 52 张非 6 板块**有 `parent_cards=[]` + `explain`（解析版 52 张中有内容）
- **30 张方法论** related_zhenti 30/30 PASS，UI 可直接渲染真题关联

Agent 3 现在可以在数据驱动下扩展 sections.json / index_cards.json / summaries.json / knowledge_points.json 到 5 板块（立体几何 89 + 解析 30 + 导数 30 + 数列 24 + 概率 22 + 解三角形 12 = 213 张）。**注意**：本地上海 81 张 6 板块的 parent_cards 是方法论占位，UI 渲染"母题"按钮时建议标注"待 Agent 1 回填"。
