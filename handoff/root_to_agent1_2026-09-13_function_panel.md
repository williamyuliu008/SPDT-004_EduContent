# Root Mavis → Agent 1: 函数板块 (M2) 任务派单

> **时间**: 2026-09-13 14:25
> **发送方**: Root Mavis (雪薇机器 4 窗口)
> **接收方**: Agent 1 (1 窗口, 母题扩展)
> **触发**: 雪薇 9-13 14:23 拍板"下一个板块做函数板块 (M2 = 解析几何 + 导数)"

---

## 1. 现状盘点 (Root 已做)

| 资产 | 解析几何 | 导数 | 立体几何对标 |
|---|---:|---:|---|
| 母题 K2X / K3X | ❌ 目录不存在 | ❌ 目录不存在 | ✅ K10-K15 |
| 方法论 | 5/5 REVIEWED | 5/5 REVIEWED | 5/5 |
| PT-030 K 卡入库 | 29 张 | 21 张 | 8 张 |
| Qwen 升级进度 | **0/50 进行中** | **0/21 进行中** | 5/8 已完 |

**Root 已在后台跑**：
- `tools/batch_review_qwen_4panels.py` (4 板块全推, 估时 30 min) — commit 4a4528d 之后
- `tools/batch_reclassify_pt030.py` (560 张重分类, 估时 1.5-2 h, 并行)
- 预计 14:25-16:30 期间 4 板块 K 卡 + 方法论全部 Qwen 升级

---

## 2. Agent 1 立即要做 (v1.1 §3 4 板块 try best)

### 2.1 建 10 张母题 (P0, 高优, 30-60 min)

| 板块 | 母题 | 内容（参考 1 窗口已有方法论 + Agent 1 v1.1 §3 解析几何/导数） |
|---|---|---|
| **解析几何** | K20 椭圆定义与几何 | 椭圆定义/几何性质 (M_解析_01) |
| | K21 中点弦 | 中点弦问题 (M_解析_02) |
| | K22 焦点弦 | 焦点弦性质 (M_解析_03) |
| | K23 韦达定理应用 | 圆锥曲线与韦达 (M_解析_04) |
| | K24 离心率范围 | 离心率范围问题 (M_解析_05) |
| **导数** | K30 单调性 | 导数判断单调 (M_导数_01) |
| | K31 极值最值 | 极值点/最值 (M_导数_02) |
| | K32 不等式证明 | 导数证不等式 (M_导数_03) |
| | K33 零点问题 | 函数零点个数 (M_导数_04) |
| | K34 切线问题 | 切线方程/公切线 (M_导数_05) |

**模板参考** (立体几何 K10-K15):
- `D:\Z_学习平台\knowledge-cards-prod\projects\math\cards\二面角\K10.json`
- 同结构: `id` / `card_id` / `chain_id` / `front` (母题提问) / `back` (完整证明) / `concepts` / `scoring_points` / `common_mistakes` / `answer_template` / `back_core` / `tags` / `parent_card` / `maturity: REVIEWED`

### 2.2 每张母题 3 道变形题引用 (P1, 30-45 min)

- 优先用 PT-030 入库的真题 (解析几何 29 + 导数 21 + 数列 38 + 概率 16 + 解三角 7 + 集合 66)
- 每张母题 related_zhenti 3 道
- 也可以等 Root 的 Qwen 升级完成后用 Qwen 推演

### 2.3 5 链 → 母题挂接 (P1, 20 min, 可与 2.2 并行)

- 跑 `_link_methods_to_zhenti.py` 把 10 张方法论挂接到新母题
- 解析几何 5 张方法论 → K20-K24
- 导数 5 张方法论 → K30-K34

---

## 3. 时间规划 (60 min 内完成母题扩展)

| 时段 | 任务 |
|---|---|
| 14:30-15:00 | 10 张母题草稿 (front + back + concepts) |
| 15:00-15:30 | 30 道 related_zhenti 引用 (3/母题 × 10) |
| 15:30-15:45 | 5 链挂接 + commit + push |
| 15:45-16:00 | handoff 写盘 + 通知 Root |

**关键约束**:
- v1.1 §3: 1 窗口 30 min 内没推进某板块 → 切到下一板块
- 优先 30 min 内完成 5 张 (K20-K24), 然后 K30-K34
- 不锁死: Root 在跑 Qwen 推演 K 卡时, 1 窗口可同步建母题

---

## 4. Root 已支援的资产 (供 1 窗口使用)

### 4.1 PT-030 入库 K 卡 (供 related_zhenti 引用)
- `D:\Z_学习平台\knowledge-cards-prod\projects\math\cards\本地上海\PT030_2026-09-13\`
- 解析几何 29 张 + 导数 21 张 (Root 14:25-15:00 升级完成)

### 4.2 5 张方法论 (供母题挂接)
- `D:\Z_学习平台\knowledge-cards-prod\projects\math\methods\解析几何\M_解析_01~05.json`
- `D:\Z_学习平台\knowledge-cards-prod\projects\math\methods\导数\M_导数_01~05.json`

### 4.3 立体几何母题模板 (复制参考)
- `D:\Z_学习平台\knowledge-cards-prod\projects\math\cards\二面角\K10.json` (完整结构)
- v1.1 §1.4 规则: 母题/变形题用真题本身/变形, 没真题留白

---

## 5. 跨窗口交付 (Agent 1 → Root)

完成后:
1. **commit 链** (类似 agent1_v1.1_milestone_3d_done.md):
   - `card(math): v1.1 解析几何板块 5 母题入库`
   - `card(math): v1.1 导数板块 5 母题入库`
   - `feat(math-reader): K20-K34 挂接 10 链 + 30 变形题引用`
2. **handoff 文档**: `handoff/agent1_v1.2_function_panel_done.md`
3. **通知 Root**: "M2 母题闭环, Root 可验证"
4. Root 收到后: 通知 3-UI 雪薇实测函数板块

---

## 6. Root (4 窗口) 实时支持

- 每 30 min 推一次进度
- 如有 blocker (PT-030 K 卡 缺 / 方法论需补 / 5 链脚本 hang) → 立刻处理
- 60 min 无进展 → Root 主动发指令 (按 v1.1 §2.1)

---

**作者**: Root Mavis (雪薇机器, 4 窗口)
**时间戳**: 2026-09-13 14:25 北京时间
**关联 commit**:
- 4a4528d (Qwen 立体几何升级)
- 3f08d2b (574 题入库报告)
- 1475998 (agent1 立体几何数据维度)
