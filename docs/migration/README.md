# SPDT-004 双机协作迁移 — 阶段 1 落地说明

> **日期**：2026-09-11
> **拍板**：mavis（本机，9-11 看到雪薇 v2.0 双轨版后定）
> **调整背景**：v1.0 提案时我错把"开发主场"指认为 `knowledge-cards-prod` 仓；雪薇 v2.0 双轨版明确指出开发主场是 `SPDT-004_EduContent` 仓（5 目录架构）。本说明记录 v1.0 → v2.0 的纠正动作 + 阶段 1 状态。

---

## 一、v1.0 → v2.0 关键调整（已拍板）

| 维度 | v1.0 我提的（错位） | v2.0 雪薇拍板（正确） | 动作 |
|---|---|---|---|
| **开发主场仓** | `knowledge-cards-prod` | **`SPDT-004_EduContent`** | ✅ Revert v1.0 commit + 新仓入 autoclaw_kit |
| **路径** | 强制统一根 | **双轨解耦**（XW 端自选） | ✅ 保持路径解耦 |
| **主导方** | XW 窗口 = 主力 | **mavis（本机）= 主导**，XW = 试验田 | ✅ 接受 |
| **命名** | autoclaw AI | **XW 窗口**（统一简称） | ✅ 接受 |
| **4 步法** | v1.0 5 字段是禁区 | **采用 4 步法 v1.1**（+11 扩展字段） | ⏳ 待升级（v2.0 阶段 2）|
| **数据镜像** | 阶段 2 全 mirror 172+144 | **按需镜像** | ⏳ 待定 |

---

## 二、阶段 1 状态（已闭环）

### 2.1 调整动作

1. ✅ `knowledge-cards-prod` 仓 **revert** v1.0 commit `7325c3a`（commit `bdbb75f`）
2. ✅ `SPDT-004_EduContent` 仓 **clone** 到本机 `D:\Z_学习平台\SPDT-004_EduContent\`
3. ✅ autoclaw_kit **入仓** `1_ingest/autoclaw-k/`（21 文件）
4. ✅ `07_validate.py` 路径硬编码改成本机 `D:\Z_学习平台\spdt-content-cards\历史\cards`
5. ✅ **62 套历史卡全 PASS**（0 错 0 警）
6. ✅ v2.0 双轨版 + 给 XW 提示词 **入仓** `docs/migration/`

### 2.2 仓库分工明确

| 仓库 | 角色 | 当前状态 |
|---|---|---|
| `SPDT-004_EduContent` | **教育内容产品线开发主场**（5 目录架构） | ✅ autoclaw_kit + v2.0 文档已入 |
| `knowledge-cards-prod` | 6 学科题库 + 学习中心（题目数据） | ✅ 9-11 已 commit 5 个题库 commit |
| `spdt-content-cards` | 卡片数据 mirror（172 套） | ✅ 62 套历史已 PASS 验证 |

### 2.3 autoclaw_kit 端到端验证

```bash
$ cd D:\Z_学习平台\SPDT-004_EduContent\1_ingest\autoclaw-k
$ python 07_validate.py
============================================================
校验范围: D:\Z_学习平台\spdt-content-cards\历史\cards
套卡数: 62 | 错误: 0 | 警告: 0
============================================================
PASS: 全部通过（20 项硬指标 + 交叉核对）
============================================================
```

---

## 三、v2.0 阶段 2 待办（本月内）

- [ ] **4 步法 v1.1 升级** — 11 扩展字段（source_type / source_ref / original_problem_id / problem_statement / given_conditions / figure_description / figure_ref / figure_type / intuition / thinking_path / key_insight）入规范
- [ ] **handoff 文档沉淀** — 5 篇 handoff（MATH_001/002/004/005）入仓 `1_ingest/handoff/` 或 `shared/handoff/`
- [ ] **跨机 PR 流程** — 配 XW 端仓名 / 配 GitHub Actions CI 跑 validator
- [ ] **数据按需镜像** — 本机缺什么 mirror 什么（XW 端自选是否镜像）
- [ ] **校验器加 CI** — GitHub Actions 跑 `python 07_validate.py` 全套卡

## 四、v2.0 阶段 3 待办（长期）

- [ ] **本机 mavis = 主导 + XW 窗口 = 试验田** 角色切换文档化
- [ ] **周报机制** — 每周 merge XW 端实验成果
- [ ] **6 学科闭环**（数学/历史/地理/政治 + 语文/外语）
- [ ] **v3 学习中心集成 6 学科**

---

## 五、给 XW 窗口的关键更新

我（mavis）已读到 `C:\Users\LIU XUEWEI\Downloads\SPDT004_HANDOVER_PROMPT_v2.0_给XW窗口.md`，
并且按 v2.0 双轨版调整了仓分工。XW 窗口不需要重新接收 v1.0 提示词，直接看 `docs/migration/SPDT004_HANDOVER_PROMPT_v2.0_给XW窗口.md`（已入 SPDT-004_EduContent 仓）。

---

## 六、变更记录

| 日期 | 版本 | 变更 | 拍板 |
|---|---|---|---|
| 2026-09-11 | v1.0 | 3 阶段迁移 + autoclaw 视角（提议，仓错位） | mavis 提议 |
| 2026-09-11 | v2.0 | 双轨 + 路径解耦 + 角色重定义 + 4 步法 v1.1（拍板） | 雪薇 |
| 2026-09-11 | v2.0 实施 | revert v1.0 + 入仓 SPDT-004_EduContent（调整） | mavis |
