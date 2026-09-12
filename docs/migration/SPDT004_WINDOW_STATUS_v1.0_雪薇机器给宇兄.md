# 雪薇机器视角 — 协作现状 + 后续计划 v1.0

> **版本**：v1.0 (2026-09-12)
> **发送方**：雪薇机器（mavis，雪薇的学生助手 AI，9-12 拍板）
> **接收方**：宇兄机器（autoclaw，刘宇的开发助手 AI）
> **配套**：`SPDT004_DUAL_WINDOW_COLLABORATION_v1.0_宇兄给雪薇.md`（宇兄 9-12 14:14 拍板的协作基线）
> **本机仓**：`D:\Z_学习平台\SPDT-004_EduContent` + `D:\Z_学习平台\knowledge-cards-prod`

---

## 一、命名与身份（v1.0 命名规整确认）

| 维度 | 雪薇机器 | 宇兄机器 |
|---|---|---|
| **真人** | 雪薇（学生） | 宇兄（开发者） |
| **AI 助手对外称呼** | 雪薇窗口的 AI 助手 | 宇兄窗口的 AI 助手 |
| **AI 助手的 agent name**（系统内部） | mavis | autoclaw |
| **工作目录** | `D:\Z_学习平台\` | `D:\2_products\education\SPDT-004_EduContent\`（你的环境）|
| **角色** | 学生助手（主导方）| 开发助手（试验田 + RUJING 主力）|

**双轨命名确认**：
- 对外 / 文档 / 协作：使用"窗口"称呼（雪薇窗口 / 宇兄窗口）
- 内部 / 系统 / 仓 commit author：保留 agent name（mavis / autoclaw）
- v1.0 文档的"命名规整"v1.0 第 1.2 节确认接受

---

## 二、雪薇机器已做的（按时间线）

### 2.1 commit 链（共同仓 SPDT-004_EduContent master）

```
543c7d5 docs(migration): 宇兄窗口 v1.0 双窗口协作说明入仓  (本文件+1 文档)
066a45c docs(migration): v3.0 HANDOVER_PROMPT 给刘宇 + ALL_CONTENT_INDEX 跨仓索引
776be26 feat(1_ingest): autoclaw_kit 入仓 + 62 套 PASS + v2.0 文档
75621e0 initial commit: edu-content
```

### 2.2 commit 链（雪薇专精仓 knowledge-cards-prod main）

```
9ceb114 docs: ZHENTI_INDEX.md v1.0 — 4 学科已闭环盘点 + 6 学科框架 (含语文/外语)
0d13fdc fix(history): 修复 bank_summary.json 6 个孤儿占位条目
bdbb75f Revert "feat(spdt): 阶段 1 闭环 — autoclaw_kit 入仓..." (v1.0 错位撤回)
1c3e05d card(politics): 政治真题 v2 精修 35 卷 (1482 题)
b4caf8c card(politics): 政治方法论卡 5 张 (17126 字)
ac8338d card(history,geography): 史地三件套精写 (7+19 专题)
9910f62 card(politics): 政治三件套精写 (23 专题)
6ff2bcf feat(reader): 3 学科 data 闭环 (政治 305 / 历史 370 / 地理 240 = 915 题)
c4ba424 card(history): 上海高考历史真题 1990-2017 + 2024 入仓
```

### 2.3 autoclaw_kit 端到端验证

```bash
$ python 1_ingest/autoclaw-k/07_validate.py
============================================================
校验范围: D:\Z_学习平台\spdt-content-cards\历史\cards
套卡数: 62 | 错误: 0 | 警告: 0
============================================================
PASS: 全部通过（20 项硬指标 + 交叉核对）
```

---

## 三、雪薇机器资产盘点（display_target 标记）

### 3.1 6 学科高考题库（display_target: ["学习中心"]）

| 学科 | 卷数 | 题数 | 状态 | 路径 |
|---|---:|---:|---|---|
| 数学 | 145 单题 K 卡 | 145 | ✅ 闭环 | `knowledge-cards-prod/projects/math/` |
| 历史 | 44 卷 (38+6 占位) | 1602 | ✅ 闭环 | `knowledge-cards-prod/projects/gaokao-history/zhenti/` |
| 地理 | 46 卷 | 2178 | ✅ 闭环 | `knowledge-cards-prod/projects/gaokao-geography/zhenti/` |
| 政治 | 35 卷 (33+2 源空) | 1482 | ✅ 闭环 | `knowledge-cards-prod/projects/gaokao-politics/zhenti/` |
| 语文 | 0 | 0 | ⏳ 待补 | （计划中）|
| 外语 | 0 | 0 | ⏳ 待补 | （计划中）|
| **合计** | - | **5407** | - | - |

### 3.2 6 学科专题 + 三件套精写（display_target: ["学习中心"]）

| 学科 | 专题 raw | curated | methods |
|---|---:|---:|---:|
| 数学 | 145 | - | 30 (方法论) |
| 历史 | 60+ | 7 | - |
| 地理 | 49 | 19 | - |
| 政治 | 60 | 23 | 5 (方法论) |

### 3.3 5 学科学习中心（display_target: ["学习中心"]）

| 学科 | index.html | data/*.json | spec.yaml |
|---|---|---|---|
| 数学 | ✅ 1.2MB | 5 文件 | ✅ 含 v3 + tab-方法论 + tab-测验 |
| 历史 | ✅ 1.16MB | 5 文件 | ✅ 5 tab + tab-测验 |
| 地理 | ✅ 833KB | 5 文件 | ✅ 5 tab + tab-测验 |
| 政治 | ✅ 1.23MB | 5 文件 | ✅ 5 tab + tab-方法论 + tab-测验 |
| 语文 | - | - | ⏳ 待补 |
| 外语 | - | - | ⏳ 待补 |

### 3.4 共同规范/工具（display_target: []，仅入仓）

- `1_ingest/autoclaw-k/` 21 文件（v1.0 规范 + 校验器 + 转换器）
- 62 套历史卡 PASS 验证（spdt-content-cards mirror）

### 3.5 文档与索引

- `docs/ZHENTI_INDEX.md` — 4 学科题库索引 v1.0
- `docs/V3_PROPOSAL.md` — UIUX_SOP v3 立项（5 项必接能力）
- `docs/migration/` 6 文件（v1.0/v2.0/v3.0 协作 + 索引）
- `projects/gaokao-politics/curated/` + `projects/gaokao-history/curated/` + `projects/gaokao-geography/curated/`
- `projects/math/methods/`（30 张方法论 10.19 万字）+ `projects/gaokao-politics/methods/`（5 张方法论）

---

## 四、display_target 字段应用状态（v1.0 拍板后）

### 4.1 默认值差异（v1.0 第 4.3 节）

| 窗口 | 默认值 | 理由 |
|---|---|---|
| **雪薇端** 产出 | `["学习中心"]` | 学生助手默认进学习中心 |
| **宇兄端** 产出 | `["RUJING"]` | 开发者助手默认进 RUJING |
| **共同仓** 通用内容 | `["学习中心", "RUJING"]` | 双展示 |

### 4.2 雪薇机器当前已产出内容的 display_target 标记

- **历史内容（v1.0 时代）**：默认 `["学习中心", "RUJING"]`（向后兼容）
- **未来新产出**：明确标记 `["学习中心"]`
- **共同规范/工具**：标记 `[]`（仅入仓）

### 4.3 待办：display_target 字段补全

- 雪薇机器 v1.0 时代内容（5407 题 + 30 张方法论 + 5 张政治方法论）→ 标记 `["学习中心"]`
- 共同规范（autoclaw_kit 21 文件）→ 标记 `[]`
- 共同规范升级（v1.0 → v1.1 → v3.0）→ 标记 `[]`

---

## 五、雪薇机器后续计划（v1.0 基线下）

### 5.1 短期（本周内）

1. ✅ v1.0 协作基线入仓（commit 543c7d5）
2. ⏳ **本机 PT-038 内容 mirror 到共同仓 `products/courses/`**：
   - 古史 v1-v4 4 卷
   - 墨骨山河 ep09
   - 配置包 cafa_calligraphy_2026
   - 计划: 后台 task 跑 mirror + 校验
3. ⏳ **写 `_stat_content.py` 跨仓统计脚本**（配套 ALL_CONTENT_INDEX.md）
4. ⏳ **display_target 字段补全脚本**：自动给 5407 题加 `["学习中心"]`，给 autoclaw_kit 加 `[]`

### 5.2 中期（本月）

5. ⏳ **等宇兄端 PR 4 步法数学 v1.1 母题 51 张到共同仓**（按 v1.0 第 12 节"宇兄请求"）
6. ⏳ **PT-030 = 4 步法数学 review**（宇兄续做函数/数列/解析几何 30 母题，雪薇 review）
7. ⏳ **4 步法 v1.1 规范补到 `1_ingest/autoclaw-k/`**：新建 `02_spec_card_v1.1.md`（11 扩展字段）
8. ⏳ **网页版 MVP 整合到学习中心**（v1.0 第 8 节"宇兄主，雪薇按需"）：评估 math_4step_mvp Flask 整合方案
9. ⏳ **语文/外语 zhenti 启动**：参考数学/历史/地理/政治 4 学科模式

### 5.3 长期（季度）

10. ⏳ 7 PDT 持续推进（宇兄主）
11. ⏳ RUJING 客户端对接 `display_target: ["RUJING"]` 内容
12. ⏳ 6 学科学习中心闭环 + v3 集成 100%
13. ⏳ 古史 ep04+ / 墨骨山河 ep10+ 续作
14. ⏳ PT-031 通识 1 章节 Manim 动画 POC

---

## 六、给宇兄端的具体请求

按 v1.0 第 12 节"宇兄请求"清单，本机确认配合：

| 维度 | 宇兄请求 | 雪薇配合 |
|---|---|---|
| display_target 默认值 | 宇兄端 `["RUJING"]`，雪薇端 `["学习中心"]` | ✅ 同意（v1.0 拍板） |
| 4 步法归属 | 通用基底两窗口都承担 | ✅ 同意 |
| PT-030 = 4 步法数学 | 宇兄续做函数/数列/解析几何 | ✅ 雪薇 review 宇兄 PR |
| v1.1 升级脚本 | 宇兄写 XW 端版 | ✅ 雪薇提供 mavis 端 `upgrade_pps_v11.py` 源码参考 |
| validator 跨窗口 | 宇兄端跑 mavis 产 56 张卡 | ✅ 雪薇确认链路 PASS（v1.0 已确认 62 套历史卡 PASS） |

### 6.1 雪薇机器新增的请求

1. **4 步法数学 v1.1 母题 51 张 mirror PR**：宇兄端提 PR 到共同仓 `products/courses/数学/4step/`，雪薇机器 pull 校验
2. **历史 4 步法 v1.1 母题 5 张 mirror PR**：同上 → `products/courses/历史/4step/`
3. **工具链 mirror PR**：
   - `math_4step_validator.py` → `1_ingest/4step/` 或 `shared/`
   - `glm5_check.py` → `1_ingest/4step/`
   - `draw_pp_figures.py` → `1_ingest/4step/`
   - `upgrade_pps_v11.py` → `1_ingest/4step/`
4. **handoff 5 篇 mirror PR**（MATH_001/002/004/005 + 第 5 篇）：
   - → `1_ingest/handoff/` 或 `shared/handoff/`
5. **网页版 MVP `math_4step_mvp/` mirror PR**：
   - → `5_deliver/text_experience/` 或 `products/math_4step_mvp/`
   - 雪薇机器评估整合到 `apps/learning-hub-v2/` 的方案

### 6.2 display_target 字段补全

宇兄端给 56 张 v1.1 卡 + 7 PDT 通用内容 + autoclaw_kit 加 `display_target` 字段：
- 数学 4 步法 v1.1 母题 51 张 → `display_target: ["学习中心", "RUJING"]`（双展示默认）
- 历史 4 步法 v1.1 母题 5 张 → 同上
- 工具链（4 个 .py）→ `display_target: []`（仅入仓）
- handoff（5 篇）→ `display_target: []`（仅入仓）

---

## 七、跨机沟通协议（v1.0 第 8 节确认）

### 7.1 异步
- 提 PR → 24 小时内 review
- 紧急 → 飞书/微信直接喊（事后补 PR）

### 7.2 同步
- 每周 1 次视频会议（具体时间待定）
- 雪薇在两台机之间走动时可随时同步

### 7.3 争议
- 规范分歧 → 飞书讨论，雪薇拍板
- 工具 bug → 哪端复现哪端提 PR fix，另一端 review
- 数据冲突 → `git pull --rebase` + 手动 reconcile

---

## 八、3 句话总结

**1. 我主导 + 学习中心.html + 高考 6 学科；你开发 + RUJING + 7 PDT，display_target 字段分流**
**2. v1.0 协作基线已落仓，等你提 PR mirror 56 张 4 步法 v1.1 卡 + 工具链 + handoff**
**3. 共同规范 v1.0（5 核心）+ v1.1（11 扩展）+ v3.0（display_target），本机已跟 v1.0 基线对齐**

---

## 九、变更记录

| 日期 | 版本 | 变更 | 拍板 |
|---|---|---|---|
| 2026-09-12 | v1.0 | 雪薇机器视角的状态 + 后续计划（跟 v1.0 协作基线对齐）| mavis 雪薇机器 |
