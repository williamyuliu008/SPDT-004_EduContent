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

## 2. 文件清单（截至 2026-08-21，全 29 个 .py）

> 自动维护：`tools/layer_doc_sync.py` 校验本清单与实际目录是否一致
> 校验通过状态：✅ 0 警告

### 2.1 按类型分组

#### 核心入口（3 个）
- `main_pipeline.py` — 主流程入口
- `launcher.py` — 启动器
- `server.py` — 本地服务器

#### 卡片管理（18 个）
- `analyze_kb.py` — 知识库分析
- `inspect_kb.py` — 知识库检视
- `verify_s010.py` — S010 验证
- `enhance_kb.py` — 知识库增强入口
- `enhance_quick.py` — 快速增强
- `enhance_all.py` — 全部增强
- `enhance_s010.py` — S010 专用增强 v1
- `enhance_s010_v2.py` — S010 专用增强 v2
- `enhance_es_questions.py` — 错题脚本增强
- `batch_enhance.py` — 批量增强 v1
- `batch_enhance_v2.py` — 批量增强 v2
- `batch_enhance_v3.py` — 批量增强 v3
- `batch_fill_error_scripts.py` — 批量填充错题脚本
- `check_all.py` — 全部检查
- `check_enhance.py` — 增强检查
- `check_enhanced.py` — 增强后检查
- `check_json.py` — JSON 检查
- `check_quotes.py` — 引文检查
- `full_check.py` — 完整检查

#### LLM 与 API（4 个）
- `test_api.py` — API 测试
- `test_batch.py` — 批量测试
- `test_llm.py` — LLM 测试
- `test_llm_quick.py` — LLM 快速测试

#### GUI（1 个）
- `gui.py` — GUI 入口

#### 隔离/治理（1 个）
- `_experimental_marker.py` — L2 警告 marker（自动生成，**不要删除**）

#### 临时/待清理（1 个）
- `_temp_check.py` — ⚠️ 临时检查脚本，**计划 W22 清理**

### 2.2 完整清单（28 个，不含 _experimental_marker.py）

> 此节是 `tools/layer_doc_sync.py` 校验依据（正则 `^- \`xxx.py\``），保持完整

- `analyze_kb.py`
- `batch_enhance.py`
- `batch_enhance_v2.py`
- `batch_enhance_v3.py`
- `batch_fill_error_scripts.py`
- `check_all.py`
- `check_enhance.py`
- `check_enhanced.py`
- `check_json.py`
- `check_quotes.py`
- `enhance_all.py`
- `enhance_es_questions.py`
- `enhance_kb.py`
- `enhance_quick.py`
- `enhance_s010.py`
- `enhance_s010_v2.py`
- `full_check.py`
- `gui.py`
- `inspect_kb.py`
- `launcher.py`
- `main_pipeline.py`
- `server.py`
- `test_api.py`
- `test_batch.py`
- `test_llm.py`
- `test_llm_quick.py`
- `verify_s010.py`
- `_temp_check.py`

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
| 2026-08-21 | 完善文件清单（自动验证：29 个 .py 全列） | Mavis | active |
| 2026-08-21 | 创建本文件，标记 L2 隔离 | Mavis | active |
