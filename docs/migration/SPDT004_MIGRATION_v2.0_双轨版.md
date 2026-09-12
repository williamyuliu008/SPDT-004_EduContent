# SPDT-004 双机协作方案 v2.0

> **版本**：v2.0 (2026-09-11) — 替代 v1.0
> **方案调整**：原 v1.0 由 XW 窗口（autoclaw AI）2026-09-11 拍板，本机 mavis 评估后调整
> **核心变化**：双轨并行 + 路径解耦 + 角色重新定义 + 4 步法 v1.1 采用
> **拍板**：mavis (本机) 2026-09-11

---

## 一、v1.0 → v2.0 的核心调整

| 维度 | v1.0 提案（XW 窗口） | v2.0 拍板（本机 mavis） | 理由 |
|:---|:---|:---|:---|
| **路径** | XW 窗口建议"目标根 D:\Z_学习平台\knowledge-cards-prod\" | **双轨各自解耦**，不强制统一根 | XW 路径未在本机验证；强耦合增加维护成本 |
| **主导方** | 提案"另一台机（XW）= 主力产卡 + 维护规范" | **本机 mavis = 主导**，XW 窗口 = 试验田 + 校验回归 | 实际 9-11 所有产卡 + 规范都是 mavis 在做 |
| **命名** | "autoclaw" AI（另一台机器代号） | **XW 窗口**（雪薇窗口 AI，autoclaw 是 XW 旧名） | 简化认知 |
| **4 步法** | 提案里 v1.0 规范的 5 字段是"禁区" | **采用 4 步法 v1.1**（v1.0 + 11 扩展字段） | mavis 9-11 产出的新方向 |
| **数据镜像** | 阶段 2 全 mirror 172+144 张 | **按需镜像**：本机缺什么镜像什么 | 减少冗余存储 |

---

## 二、双轨架构

```
[mavis 主场 - 本机]                                          [XW 窗口客场 - 另一台机]
D:\2_products\education\SPDT-004_EduContent\              D:\【XW 自选路径】\spdt\
   ↓                                                              ↓
5 目录 1_ingest / 2_structure / 3_render / 4_adapt / 5_deliver    同构 5 目录（XW 端）
   ↓                                                              ↓
handoff/ 沉淀文档 (4 步法 v1.0/v1.1, 母题构建方法论, 5 道历史真题)  handoff/ (XW 端)
   ↓                                                              ↓
products/ (math_4step_mvp)  ← [Git PR 模式] →             XW 端试验田
   ↓                                                              ↓
D:\4_data\knowledge_cards\数学\4step\ (51 张卡 v1.1)        D:\4_data\knowledge_cards\【XW 端】\
   ↓                                                              ↓
D:\4_data\knowledge_cards\历史\4step\ (5 张卡 v1.1)         XW 镜像（按需）
```

**关键：**
- **路径解耦**：两边路径完全独立，不互相引用
- **代码同步**：Git 仓 `williamyuliu008/SPDT-004_EduContent` 双向同步（PR 模式）
- **数据独立**：两边都有 `D:\4_data\knowledge_cards\`（按需镜像）

---

## 三、角色定义（v2.0 拍板）

### 3.1 本机 mavis（主导）

**职责**：
- ✅ 产卡（数学/历史/未来 9 科）
- ✅ 规范制定（4 步法 v1.0/v1.1, 真题卡 v1.0-v1.2, 母题构建方法论）
- ✅ 工具开发（pydantic validator, GLM-4-flash 推演, matplotlib SVG）
- ✅ 网页版 MVP（math_4step_mvp Flask）
- ✅ 沉淀文档（handoff/）
- ✅ 跨机 PR review（接受 XW 提的 PR，24 小时内 review）
- ✅ 决定合入或打回

**不做**：
- ❌ 替 XW 窗口做统筹决策（如 XW 端的工具选型、目录结构）
- ❌ 替 XW 窗口拍板新学科 POC 优先级

### 3.2 XW 窗口（试验田 + 校验回归）

**职责**：
- ✅ 试验新功能 POC（不破坏 v1.0 5 核心字段）
- ✅ 校验回归（跑本机的 51+5 张卡，确认 v1.1 兼容性）
- ✅ 增 SOP 章节（细化产卡流程）
- ✅ 修小 bug（validator 边缘场景）
- ✅ 新学科 POC（如生物/化学 9 科扩展）

**不做**：
- ❌ 直接 push 到 `williamyuliu008/SPDT-004_EduContent` 仓 main 分支
- ❌ 改 v1.0 5 核心字段（chain_id / card_id / schema_version / SOP / 验收标准）
- ❌ 替 mavis 做产品定义/版本号/MANIFEST 升级决策
- ❌ 改 v3 学习中心 / UIUX SOP（这是 mavis 的活）

**不确定先问**：
- ⚠️ 改 v1.0 边缘字段（tags 增项等）→ 提 PR 说明
- ⚠️ 校验器规则变化 → 提 PR + 跑回归
- ⚠️ 新增学科 schema → 提 PR + 跟 mavis 对齐前缀

---

## 四、4 步法 v1.1 兼容说明

**v1.0 规范 5 核心字段**（XW 窗口禁区）：
- `card_id` / `chain_id` / `schema_version` / SOP / 验收标准

**v1.1 扩展 11 字段**（XW 窗口可加，需提 PR）：
1. `source_type` (真题改造/原创)
2. `source_ref` (来源)
3. `original_problem_id` (原题 ID)
4. `problem_statement` (题目原文)
5. `given_conditions` (结构化已知条件)
6. `figure_description` (图形描述)
7. `figure_ref` (图形引用)
8. `figure_type` (svg/png)
9. `intuition` (题目背景)
10. `thinking_path` (思路引导)
11. `key_insight` (核心洞察)

**v1.0 → v1.1 关系**：
- v1.1 母题卡是 v1.0 母题卡的"扩展"（super-set）
- v1.0 校验器仍能识别 v1.1 卡（兼容读）
- v1.1 validator 允许 `concepts_used: []` 和 `variant_ids: []`（v1.1 兼容期）

详见 `handoff/MATH_004_母题构建方法论_v1.1.md`

---

## 五、跨机协作协议（双轨版）

### 5.1 数据交换（轻量，按需）
- mavis 产新卡 → 写到本机 → 必要时 git push 到 `williamyuliu008/SPDT-004_EduContent` 仓
- XW 窗口 需要看 mavis 产出 → `git pull` 拉取
- XW 窗口 想看 51+5 张卡内容 → 直接看本机 `D:\4_data\knowledge_cards\数学\4step\`（**注意：XW 端路径是 XW 自选，不一定是这个**）

### 5.2 代码同步（PR 模式）
1. XW 端：改完 → commit 到自己仓
2. XW 端：push 分支到 GitHub
3. XW 端：提 PR 到 `williamyuliu008/SPDT-004_EduContent` 仓 main
4. mavis 端：拉 PR → 跑 validator 回归 → 决定合入或打回
5. mavis 端：合并 → 推远端 → CI 跑

### 5.3 紧急修复
- 紧急 bug → 飞书/微信直接喊
- **事后必须补 PR 留痕**（即使 hotfix 也要走 PR）

### 5.4 争议处理
- 规范分歧 → 飞书讨论，雪薇拍板
- 工具 bug → mavis 在本机复现，XW 提 PR fix
- 数据冲突 → 仓 `git pull --rebase` + 手动 reconcile

---

## 六、本机 mavis 已完成工作（XW 窗口应了解）

### 6.1 4 步法 v1.0/v1.1 规范
- `handoff/MATH_001_4步法_概念-母题-变形-综合_v1.0.md`
- `handoff/MATH_004_母题构建方法论_v1.1.md`

### 6.2 内容资产
- 数学 4 步法：5 chain + 21 概念 + 15 母题 + 15 变形 = **51 张 PASS**（v1.1）
- 历史 4 步法：5 chain + 5 母题 = **5 张 PASS**（v1.1）
- 总计：56 张 v1.1 卡

### 6.3 工具链
- `tools/math_4step_validator.py` (pydantic 风格，跨学科)
- `tools/glm5_check.py` (GLM-4-flash 反向推演，绕开 GLM-5 reasoning 占满)
- `tools/draw_pp_figures.py` (matplotlib SVG 配图)
- `tools/upgrade_pps_v11.py` (v1.0 → v1.1 批量升级)

### 6.4 网页版 MVP
- `products/math_4step_mvp/` (Flask 3.1.3, 跨学科路由 math + history)
- 6 端点全 200，Flask 跑在 `http://127.0.0.1:5050/`

### 6.5 handoff 沉淀（5 篇）
- MATH_001: 4 步法 v1.0 规范
- MATH_002: 网页版 MVP 架构
- MATH_004: 母题构建方法论 v1.1
- MATH_005: 5 道历史真题改造为母题原型

---

## 七、XW 窗口可立即做的事（按优先级）

| 优 | 任务 | 产出 | 时间 |
|:---|:---|:---|:---|
| **高** | 跑 mavis 的 56 张 v1.1 卡，回归验证 | 校验报告（PASS/FAIL） | 1 天 |
| **高** | 写自己的 v1.0 → v1.1 升级脚本（参考 mavis 的 upgrade_pps_v11.py） | 工具脚本 | 1-2 天 |
| **中** | 试验新学科 POC（如生物/化学） | 新学科 schema 提案 PR | 1 周 |
| **中** | 给 51+5 张卡做 materials 增强 | enrichment PR | 3-5 天 |
| **低** | 修 validator 边缘场景 | 小 PR | 按需 |
| **低** | 丰富 v1.0 规范（如 exam_questions 增 1 类型） | 提案 PR | 1 周+ |

---

## 八、里程碑

| 里程碑 | 时间 | 验收 |
|:---|:---|:---|
| **M0** 双轨启动 | 2026-09-11 (本轮) | v2.0 方案 + XW 提示词落盘 ✅ |
| **M1** XW 校验回归 | 2026-09-18 | XW 跑 56 张 v1.1 卡，PASS 报告 |
| **M2** XW 第一份 PR | 2026-09-25 | 1 个 PR 合并到本机仓 |
| **M3** 9 学科闭环 | 2026-Q4 | 数学/历史/地理/政治 + 5 新学科全闭环 |
| **M4** CI 自动化 | 2026-Q4 | GitHub Actions 跑 validator |

---

## 九、变更记录

| 日期 | 版本 | 变更 | 拍板 |
|:---|:---|:---|:---|
| 2026-09-11 | v1.0 | 初版（3 阶段迁移 + autoclaw 视角）| XW 窗口 AI |
| 2026-09-11 | v2.0 | 双轨 + 路径解耦 + 角色重定义 + 4 步法 v1.1 | mavis（本机）|

---

## 十、给 XW 窗口的提示词

见 `handoff/SPDT004_HANDOVER_PROMPT_v2.0_给XW窗口.md`
