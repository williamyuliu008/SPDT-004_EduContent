# SPDT-004 分层架构 v1.0

> **版本**：v1.0（2026-08-21）
> **目的**：把"功能堆叠的 monolith"拆成 **3 层 + 3 窗口**，每层有清晰的"准入准出"和"保护规则"。
> **作者**：willi / Mavis
> **状态**：W21 治理收口首发，伴随 SPDT.yaml v3.0 一起落地。

---

## 1. 设计动机

SPDT-004 跑了一个半月，已经承载：

- 5 阶段流水线（1_ingest → 5_deliver）
- 3 个配置包（cafa_calligraphy_2026 / geo_shanhe_2026 / political_gaokao_2026）
- 1039 张知识子卡
- 11 个 Skill + 3 条 Chain + 6 个 Style Pack
- 20+ 个 Python 工具脚本
- 1 个 HarmonyOS APP（rujing）
- 3 个 OMAS Cell（KBC/CMC/KCE）

**问题**：所有代码、数据、文档"堆"在一个仓库里，没有"稳定 / 演化 / 开发"的区分。结果是：

- 改 L2（4_adapt）时容易误碰 L0（1_ingest）
- 推送脚本的 bug 会污染 SOP 文档
- 内容扩产和架构开发互相阻塞

**解决**：物理分层 + 节奏分层。

---

## 2. 三层定义

### L0 · 稳定层（Stable）

> **定义**：已通过端到端验证、契约稳定、不预期大改、只做小修小补。

| 模块 | 说明 |
|:---|:---|
| 1_ingest 工具链 | M0 入口判别 / M1 考纲解析 / M2 质量校准（含 schemas、config） |
| knowledge_cards 卡库 | 1039 张子卡（历史 379 / 地理 294 / 政治 366） |
| 转换/推送工具链 | `ru_cardpkg_convert.py` v6.0 + `_push_to_rujing.py` + `_validate_cards.py` |
| 质量审计 | `card_auditor.py` + 5 维度评分 + 认证体系（GOLD/SILVER/CERTIFIED） |
| 模板基础设施 | `templates/agent_templates/T1-T8/M1`（早期产物，作为产线模板） |
| OMAS 接口契约 | `IF-D_Protocol_v1.0.md` + `interface_protocol_SPDT4_ebook.md` |

**保护规则**：
- ❌ 禁止在 W_high 窗口内改 L0 代码
- ❌ 禁止 L1/L2 反向依赖 L0 内部（只能通过暴露的接口）
- ✅ 任何 L0 变更必须走 RFC（哪怕 1 行）
- ✅ 每次 L0 变更触发全量回归测试

### L1 · 演化层（Evolutionary）

> **定义**：日常小迭代的模块，频繁有新内容/新配置加入，但接口和契约稳定。

| 模块 | 说明 |
|:---|:---|
| CGMPipeline SOP | CGM 方法论文档（v1.0 → v1.1 已迭代，下次预计 v1.2） |
| 2_structure 已产物 | 古史 v1-v3 已有产物，v4 在 L2 扩产 |
| 墨骨山河 ep01/ep09 | 已完成基础剧本 |
| Skill 系统 | 11 Skill + 3 Chain + 6 Style Pack，要扩但每次增量小 |
| autoclaw_kit 协作工具 | 5_templates / 6_example / 8_tools（产线协作机制） |
| 治理文档 | `SPDT.yaml` / `LAYERS.md` / `WINDOWS.md` / `docs/` |
| OMAS Cell 内部 | KBC/CMC/KCE 的 kernel 实现（接口在变但已注册） |

**保护规则**：
- ❌ 禁止跨入 L2 范围（除非走 RFC）
- ✅ 通过 L0 暴露的接口消费能力
- ✅ 每次 L1 变更做增量单元测试 + 与 L0 接口对齐

### L2 · 开发层（Experimental）

> **定义**：频繁变、正在搭、未来预期大改的模块。

| 模块 | 说明 |
|:---|:---|
| 4_adapt（AdaptivePrepPlatform） | 5 Agent 调度 + 全局记忆体（当前 0.1 成熟度） |
| 4_adapt/_06_mvp_pipeline | MVP 试跑代码，状态：实验性 |
| 4_adapt/_07_gaokao_volunteer / _08_calligraphy_linting | 早期 MVP |
| 跨包联动 _04_cross_pack | 完全空白，待建 |
| 古史_v4 内容扩产 | meta.json 完整，待生产 |
| 墨骨山河 ep02-08 扩产 | 8 集规划，缺生产 |
| ebook_builder Stage A 改造 | 替换为 card_maker |
| Skill T4 叙事审计 | 半自动评分设计 |
| 新 Skill 探索 | `hist-civilization-clash` / `hist-tech-reshapes` 等 planned 状态 |

**保护规则**：
- ❌ **物理隔离**：L2 目录独立（不在 L0/L1 目录内）
- ❌ L2 代码禁止被 L0/L1 直接 `import`（只能通过 `_experimental/` 边界）
- ❌ L2 变更不走 RFC（鼓励快速试错），但失败要快速清理
- ✅ 每次 L2 变更记录在 `_changelog.md`
- ✅ L2 升级到 L1 需满足：≥3 次成功 + 接口稳定 + 文档完整

---

## 3. 物理隔离（不是"搬动"，是"标注"）

> **原则**：不破坏 git 历史，不动现有目录结构，通过"软隔离"建立清晰边界。

### 3.1 L0 标识
- `SPDT.yaml` 顶层 `pdt_list[]` 加 `layer: L0` 字段
- 关键 L0 工具脚本顶层加注释：
  ```python
  # LAYER: L0 (Stable) — 受保护，禁止在 W_high 窗口内修改
  # CONTRACT: see docs/LAYERS.md#l0-stable
  ```

### 3.2 L1 标识
- `SPDT.yaml` 加 `layer: L1` 字段
- 顶层加注释：
  ```python
  # LAYER: L1 (Evolutionary) — 通过 L0 接口消费能力
  ```

### 3.3 L2 隔离（重点）
- 4_adapt/ 下所有子模块顶层加 `__experimental__.py`：
  ```python
  # LAYER: L2 (Experimental) — 与 L0/L1 物理隔离
  # STABILITY: 0.1（不可生产）
  # UPGRADE-TO-L1-REQUIREMENTS: 见 docs/LAYERS.md#l2-experimental
  ```
- `4_adapt/_06_mvp_pipeline/` 顶层加 `ISOLATION.md` 标注：
  - 明确标"实验性"
  - 列出与 L0/L1 的接口边界
  - 列出升级到 L1 的条件

### 3.4 不搬动
- 不移动文件（避免破坏 git 历史、避免破坏 CI 引用）
- 不重命名（保持现有 PR / commit 关联）
- 只加标识 + 文档 + 准入准出门控

---

## 4. 跨层依赖规则

### 4.1 允许的依赖

```
L0  →  (none，只依赖 Python 标准库 + 已批准的第三方)
L1  →  L0（通过暴露的接口）
L2  →  L0 / L1（通过暴露的接口）
```

### 4.2 禁止的依赖

- ❌ L0 → L1 / L0 → L2
- ❌ L1 → L2
- ❌ 跨层 `import` 内部模块（只能 `import` `__init__.py` 暴露的 API）

### 4.3 例外情况

- 工具脚本（`_tools/`、`_scripts/`）可以横跨 L0/L1/L2 调用（因为是 orchestration）
- 但工具脚本必须放在 `tools/` 顶层，不放在 L0/L1/L2 目录内

---

## 5. 升级路径（L2 → L1 → L0）

### L2 → L1 的准入条件（必须全部满足）
- [ ] ≥3 次成功生产/调用
- [ ] 接口契约冻结（不能继续大改）
- [ ] 单元测试覆盖 ≥70%
- [ ] 文档完整（README + 接口说明 + 已知缺陷）
- [ ] 至少 1 个 L1 模块正在消费它

### L1 → L0 的准入条件（必须全部满足）
- [ ] 持续稳定 ≥3 个月（无破坏性变更）
- [ ] 完整单元测试 + 集成测试
- [ ] 有 CHANGELOG 记录所有变更
- [ ] 有至少 1 个真实业务案例证明稳定
- [ ] willi 拍板

---

## 6. 文件索引

```
LAYERS.md                          ← 本文件
WINDOWS.md                         ← 窗口节奏 + 准入准出
SPDT.yaml                          ← 各模块的 layer 字段标识
docs/04-Skills/SPDT-004_知识卡片_测试标准设计.md   ← L0 测试标准
```

---

## 7. 版本历史

| 版本 | 日期 | 核心变更 |
|:---|:---|:---|
| v1.0 | 2026-08-21 | 首发：L0/L1/L2 三层 + 软隔离策略 |
