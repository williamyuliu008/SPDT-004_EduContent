# 4_adapt/_06_mvp_pipeline · L2 隔离标记

> **写入日期**：2026-08-21
> **依据**：[LAYERS.md](../../../LAYERS.md) + [WINDOWS.md](../../../WINDOWS.md)
> **状态**：实验性 / 不可生产

---

## ⚠️ 警告

**本目录属于 L2_experimental 层（开发层），与 L0/L1 物理隔离。**

任何对 L0/L1 模块的引用必须通过暴露的接口（`__init__.py` 暴露的 API），禁止直接 `import` 内部模块。

---

## 1. 当前状态

| 项 | 数据 |
|:---|:---|
| 成熟度 | 0.1（实验性） |
| 接口契约 | 未冻结 |
| 单元测试 | 无 |
| 集成测试 | 部分（仅启动验证） |
| 文档 | 散落脚本注释，无系统文档 |
| 已知缺陷 | 高（接口易变 / 配置散乱 / 无错误处理） |
| 风险 | 高（不可直接生产） |

---

## 2. 文件清单（截至 2026-08-21）

### 2.1 核心入口
- `main_pipeline.py` — 主流程入口
- `launcher.py` — 启动器
- `server.py` — 本地服务器

### 2.2 卡片管理
- `kb_all.json` — 知识库全集（快照）
- `enhance_kb.py` / `enhance_quick.py` / `enhance_s010.py` / `enhance_s010_v2.py`
- `batch_enhance.py` / `batch_enhance_v2.py` / `batch_enhance_v3.py`
- `enhance_es_questions.py` / `enhance_all.py`
- `analyze_kb.py` / `inspect_kb.py` / `verify_s010.py`
- `check_all.py` / `check_enhance.py` / `check_enhanced.py` / `check_json.py` / `check_quotes.py`
- `full_check.py` / `batch_fill_error_scripts.py`
- `kb_all_inline.js` / `kb_browser.html` / `card_browser_generator.py`

### 2.3 LLM 与 API
- `test_api.py` / `test_batch.py` / `test_llm.py` / `test_llm_quick.py`
- `gui.html` / `gui.py`

### 2.4 杂项
- `_temp_check.py` — 临时检查脚本（应清理）

---

## 3. 与 L0/L1 的接口边界

### 3.1 允许的消费
- 通过 `2_structure.TextExperience.cards` 读取已产物（只读）
- 通过 `knowledge_cards._tools._validate_cards.py` 跑校验

### 3.2 禁止的依赖
- ❌ 禁止 `import` L0 内部模块（只能通过 L0 暴露的 `__init__.py` API）
- ❌ 禁止直接修改 `1_ingest/` 下任何文件
- ❌ 禁止直接修改 `2_structure/TextExperience/` 下已产物（v1-v3）

### 3.3 升级到 L1 的条件
- [ ] ≥3 次成功运行（带数据 + 报告）
- [ ] 接口契约冻结（不能再大改 API）
- [ ] 单元测试覆盖 ≥70%
- [ ] 文档完整（README + 接口说明 + 已知缺陷列表）
- [ ] 至少 1 个 L1 模块正在消费它

---

## 4. 改动窗口

**仅在 W_high 窗口内改动**。其他窗口禁止修改 `_06_mvp_pipeline/` 下任何文件。

例外：
- 紧急 P0 bug 走 W_low 破窗
- 任何改动必须更新本文件的"已知缺陷"章节

---

## 5. 已知缺陷（持续更新）

| # | 缺陷 | 影响 | 计划修复 |
|:---:|:---|:---|:---|
| 1 | 多个 `enhance_*.py` 版本并存（v1/v2/v3）| 维护混乱 | W22 整合为单文件 |
| 2 | 临时脚本 `_temp_check.py` 未清理 | 干扰 | W22 清理 |
| 3 | 启动器 `launcher.py` 与 `main_pipeline.py` 入口不一致 | 调用混乱 | W23 整理 |
| 4 | LLM wrapper 配置散落（test_llm.py / test_llm_quick.py）| 难维护 | W23 统一 |
| 5 | `kb_all.json` 快照无版本控制 | 状态不清 | W22 加 CHANGELOG |

---

## 6. CHANGELOG（必须维护）

| 日期 | 变更 | 作者 | 状态 |
|:---|:---|:---|:---|
| 2026-08-21 | 创建本文件，标记 L2 隔离 | Mavis | active |
