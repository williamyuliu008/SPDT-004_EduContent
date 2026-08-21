# SPDT-004 产品线目录 v1.0

> **版本**：v1.0（2026-08-21）
> **目的**：把"逐步叠加开发"积累的产物，**结构化、可枚举、可复用**地描述清楚。
> **依据**：willi 2026-08-21 决策——"先暂停，梳理一下产品线"
> **配套**：[LAYERS.md](LAYERS.md) + [WINDOWS.md](WINDOWS.md) + [SPDT.yaml](SPDT.yaml)
> **状态**：W22 治理梳理首发

---

## 0. 阅读指南

本文档回答 willi 提出的 6 个问题：
1. 本管线生产内容是哪几类？
2. 每类的输入是什么？是否有结构化模板？
3. 每类产品输入时带什么参数？是否有缺省参数集合？
4. 每类产品的开发管线复用哪些模块？
5. 输出分几类，分别是什么？
6. 各类输出的质量标准是什么？有无核对检验机制？

文档结构：
- §1：产品大类总览（产品分类树）
- §2：6 个问题的逐项回答
- §3：9 个产品（P-001 ~ P-009）的详细规格表
- §4：产品状态看板（截至 2026-08-21）
- §5：演化规则（如何新增/弃用/升级产品）

---

## 1. 产品大类总览

SPDT-004 管线目前可生产 **9 大类产品**，按"内容形态"分类：

| ID | 产品大类 | 已有产物 | 受众 | 主力阶段 |
|:---|:---|:---|:---|:---|
| **P-001** | 视频课件（manim + TTS） | 古史 v1-v3 + 墨骨山河 ep01/ep09 | K12 / 通识 | 2_structure → 3_render |
| **P-002** | 电子书（HTML / EPUB / Markdown） | H-M1/H-M2/G-M1/P-M1 等 4 大模块 | K12 / 终身学习 | 2_structure → ebook_builder |
| **P-003** | 知识卡片集合（v1.3 JSON） | 1039 张子卡（历史 379 + 地理 294 + 政治 366） | K12 / 复习速查 | 2_structure → KBC.card_maker |
| **P-004** | 微剧本（micro_dramas.json） | 墨骨山河 ep01-ep09 规划 | K12 / 沉浸式学习 | 2_structure/TextExperience |
| **P-005** | 知识链（古史知识链） | 古史 v1-v4 共 24+ 链 | K12 / 高考备考 | 2_structure/TextExperience |
| **P-006** | 配置包（cafa_calligraphy_2026 等） | 3 个（书法 / 地理 / 政治） | 校考 / 高考 | 4_adapt/AdaptivePrepPlatform |
| **P-007** | Skill 写作方案（5 段式 Markdown） | chain_A 三步骤 + 颜真卿范例 | 创作者 / 学生 | docs/04-Skills |
| **P-008** | 视觉素材（草书辨析卡 + 碑帖图） | 草书辨析卡 v4（13 张） | 书法学习 | products/PT-039 |
| **P-009** | 音频（MP3 / 广播剧） | 古史 v3 完整 4 集音频 | 通勤 / 沉浸式 | 3_render + TTS |

```
P-001 视频课件 ──┐
P-002 电子书   ──┤
P-003 知识卡片 ──┤
P-004 微剧本   ──┼─→ 1_ingest 原材料
P-005 知识链   ──┤
P-006 配置包   ──┤   2_structure 剧本/卡片 (TextExperience)
P-007 Skill   ──┤
P-008 视觉素材 ──┤   3_render 视频/音频 (SPDT-KTE)
P-009 音频    ──┘
                 ↓
                 4_adapt 编排消费 (AdaptivePrepPlatform)
                 ↓
                 5_deliver rujing APP
```

---

## 2. 6 个问题的回答

### 2.1 本管线生产内容是哪几类？

**9 大类（P-001 ~ P-009）**，分类原则：

- **按内容形态分**（不是按"产品名"分，因为同一形态可服务多个学科）
- **按"是否可独立消费"分**（独立可消费 vs 需嵌入其他产品）

| 大类 | 独立消费？ | 依赖其他产品？ |
|:---|:---:|:---|
| P-001 视频课件 | ✅ 独立 | 依赖 P-005 知识链作为剧本 |
| P-002 电子书 | ✅ 独立 | 可选依赖 P-003 卡片 |
| P-003 知识卡片 | ✅ 独立 | 可独立消费 |
| P-004 微剧本 | ⚠️ 半独立 | 需配合 P-001 视频或 P-007 Skill |
| P-005 知识链 | ⚠️ 半独立 | 需配合 P-001 视频 |
| P-006 配置包 | ✅ 独立 | 嵌入 rujing APP |
| P-007 Skill | ✅ 独立 | 可独立消费 |
| P-008 视觉素材 | ✅ 独立 | 可独立消费 |
| P-009 音频 | ✅ 独立 | 可独立消费 |

### 2.2 每类的输入是什么？是否有结构化模板？

每类产品都有**结构化输入模板**：

| 产品 | 输入类型 | 模板文件 | 模板状态 |
|:---|:---|:---|:---:|
| P-001 视频课件 | scene_v2 JSON 剧本 | `templates/scene_v2.template.json` | ✅ |
| P-002 电子书 | 章节 Markdown + book_config.yaml | `D:/3_infra/ebook-builder/configs/book_config.template.yaml` | ✅ |
| P-003 知识卡片 | 文本 / 对话记录 | `docs/04-Skills/card_schema.json` (v1.3) | ✅ |
| P-004 微剧本 | 人物 + 事件 + 场景 | `2_structure/TextExperience/.../micro_dramas.json` 模板 | ✅ |
| P-005 知识链 | 考纲 + 元信息 | `2_structure/TextExperience/古史_vX_*/meta.json` | ✅ |
| P-006 配置包 | 学科 + 题型 + 知识条目 | `_03_subject_packs/<pack>/meta.json` | ✅ |
| P-007 Skill 方案 | 卡片包 + Skill ID | `docs/04-Skills/SKILL_*.md` 模板 | ✅ |
| P-008 视觉素材 | 原图 + 标签 | `products/PT-039/草书辨析卡/template.yaml` | ⚠️ 待补 |
| P-009 音频 | 剧本 + voice_id | `templates/audio_spec.yaml` | ⚠️ 待补 |

### 2.3 每类产品输入时带什么参数？是否有缺省参数集合？

每类产品定义**必填参数 + 可选参数 + 缺省值**。详细见 §3 各产品表。

**总原则**：
- 必填参数：缺少则产品无法生产
- 可选参数：缺省时使用项目默认（每个产品有自己的 `default_config.yaml`）
- 全局缺省：渲染精度、配色、字体等（用户在 `LAYERS.md §6` 提到 planned 的 rfc 模板中会集中管理）

### 2.4 每类产品的开发管线复用哪些模块？

**5 阶段流水线 + 横向模块**：

```
                     P-001 P-002 P-003 P-004 P-005 P-006 P-007 P-008 P-009
1_ingest 摄入          ●     ●     ●     ●     ●     ●     -     ●     -
2_structure 结构化     ●     ●     ●     ●     ●     ●     ●     ●     ●
3_render 渲染          ●     -     -     -     -     -     -     -     ●
4_adapt 编排           -     -     -     -     -     ●     -     -     -
5_deliver 触达         ●     ●     ●     ●     ●     ●     -     -     ●

横向模块（不依赖阶段）：
  ● L0 知识卡片工具链（card_auditor / _validate_cards / ru_cardpkg_convert）
  ● L0 质量审计（card_auditor.py）
  ● L0 模板基础设施（templates/agent_templates/）
  ● L1 OMAS Cell 集成（KBC.card_maker / CMC.ebook_builder / KCE.orchestrator）
  ● L1 autoclaw_kit 协作工具（产线生产）
  ● L2 Skill 系统（11 个 Skill + 3 Chain + 6 Style Pack）
```

每个产品**默认走 L0/L1 模块**（受保护的稳定层），**不直接调 L2 实验代码**。

### 2.5 输出分几类，分别是什么？

**3 大类**：

#### A. 中间产物（可重建、有版本控制）
- scene_v2 JSON（视频剧本）
- 章节 Markdown（电子书）
- CardPackage JSON（知识卡片）
- micro_dramas.json（微剧本）
- chain_meta.json（知识链元信息）
- 配置包 meta.json
- Skill 写作方案 Markdown
- rujing CardPackage（消费端转换产物）

#### B. 最终产物（交付给用户）
- MP4 视频 / MP3 音频
- HTML / EPUB / Markdown 电子书
- 知识卡片 JSON（可被 rujing APP 消费）
- micro_dramas 剧本
- 知识链（带元信息）
- 配置包 zip（含 meta/scripts/prompts）
- 草书辨析卡（图片 + 文字描述）

#### C. 元数据（用于治理和审计）
- MANIFEST.yaml（知识卡片全局索引）
- audit_report.html（卡片质量审计）
- SPDT.yaml（产品线注册）
- _index_<日期>.md（项目周报）
- chain_meta.article / chain_meta.self_test（链级自测）
- 校考 / 高考 知识点对照表

### 2.6 各类输出的质量标准是什么？有无核对检验机制？

#### 已有质量标准（L0 工具支持）

| 维度 | 标准 | 工具 | 状态 |
|:---|:---|:---|:---:|
| A. 格式合规 | 100% 必填字段 / 类型 / 枚举值 | `card_auditor.py` Layer 1 | ✅ |
| B. 原子性 | back 字段不含复合因果 | `card_auditor.py` Layer 1 | ✅ |
| C. 来源可信 | sources[] 非空 + 类型合法 | `card_auditor.py` Layer 2 | ✅ |
| D. 材料完整 | materials 至少一层非空 | `card_auditor.py` Layer 2 | ✅ |
| E. 语义可检索 | concepts[] 非空 + 语义相关 | `card_auditor.py` Layer 2 | ✅ |

**认证体系**：GOLD（≥95）/ SILVER（≥85）/ CERTIFIED（≥75）/ FAIL（<75）

#### 待建立质量标准（W22-W24 推进）

| 产品 | 待建立标准 | 计划工具 | 计划窗口 |
|:---|:---|:---|:---:|
| P-001 视频 | 帧率 / 字幕对齐 / 渲染时长偏差 | `video_qa.py` (planned) | W23 |
| P-002 电子书 | 章节结构 / 交叉引用 / 排版一致性 | `ebook_qa.py` (planned) | W23 |
| P-004 微剧本 | 场景完整度 / 人物一致性 / 时代考据 | `drama_qa.py` (planned) | W24 |
| P-005 知识链 | 链长 / 节点连接 / 跨链引用 | `chain_qa.py` (planned) | W24 |
| P-006 配置包 | schema 合规 / 题型覆盖 / 知识条目完整 | `pack_qa.py` (planned) | W24 |
| P-007 Skill 方案 | 模板完整度 / 写作步骤覆盖 / 测试用例 | `skill_qa.py` (planned) | W23 |
| P-008 视觉素材 | 图像清晰度 / 标签准确度 / 辨析深度 | `asset_qa.py` (planned) | W24 |
| P-009 音频 | 音量一致性 / 角色音色区分 / 时长 | `audio_qa.py` (planned) | W24 |

**核对检验机制**：
- **L0 模块**：`tools/layer_lint.py` + `tools/layer_doc_sync.py` 自动化（已落地）
- **L1 模块**：`card_auditor.py` + `ru_cardpkg_convert.py` 自动化（已落地）
- **L2 模块**：`tools/window_check.py` + ISOLATION.md 人工（已落地）

---

## 3. 9 个产品的详细规格

### P-001 · 视频课件

| 项 | 内容 |
|:---|:---|
| 定位 | 教材知识 → 视频（manim 渲染 + TTS 配音） |
| 输入 | scene_v2 JSON 剧本（来自 P-005 知识链） |
| 输入模板 | `templates/scene_v2.template.json` |
| 必填参数 | `title` / `chain_id` / `scenes[]` |
| 可选参数 | `voice_id` (default: `male-qn-qingse`) / `resolution` (default: `1080P`) / `bgm_path` |
| 复用模块 | L0: 1_ingest（输入）/ L0: templates（scene_v2 模板）/ L1: 3_render/SPDT-KTE（编排）/ L1: PT-VFX（渲染） |
| 输出 | MP4 视频 + 字幕 SRT + 场景元信息 |
| 质量标准 | 帧率 24fps / 字幕 100% 对齐 / 渲染时长偏差 ±5% |
| 已产物 | 古史 v1（6 集）/ 古史 v3（4 集）/ 墨骨山河 ep01 / 墨骨山河 ep09 |

### P-002 · 电子书

| 项 | 内容 |
|:---|:---|
| 定位 | 章节 Markdown → HTML / EPUB / Markdown 整书 |
| 输入 | 章节 Markdown + book_config.yaml |
| 输入模板 | `D:/3_infra/ebook-builder/configs/book_config.template.yaml` |
| 必填参数 | `title` / `author` / `chapters[]` |
| 可选参数 | `format` (HTML/EPUB/MD, default: HTML) / `theme` (default: serif) / `cover_path` |
| 复用模块 | L0: ebook_builder / L1: OMAS Cell (CMC.ebook_builder) / L1: 2_structure (章节源) |
| 输出 | 整书 HTML / EPUB / Markdown + 元数据 |
| 质量标准 | 章节完整 / 交叉引用准确 / 排版一致 |
| 已产物 | H-M1 千年治乱 / H-M2 食货之道 / G-M1 阶梯山河 / P-M1 道路的选择 |

### P-003 · 知识卡片

| 项 | 内容 |
|:---|:---|
| 定位 | 文本 / 对话记录 → v1.3 JSON 卡片集合 |
| 输入 | 任意文本（AI 提炼）或结构化 Q&A |
| 输入模板 | `docs/04-Skills/card_schema.json` (v1.3) |
| 必填参数 | `card_id` / `title` / `back` / `card_type` / `domain` / `concepts[]` |
| 可选参数 | `tags[]` / `sources[]` / `materials.{narrative,data,quotes,argument_framing}` |
| 复用模块 | L0: 1_ingest（M0-M2）/ L0: knowledge_cards（存储）/ L0: card_auditor / L0: ru_cardpkg_convert |
| 输出 | CardPackage JSON + 审计报告 HTML + rujing 上架文件 |
| 质量标准 | 5 维度评分 ≥75（FAIL 0） + 91% SILVER+ |
| 已产物 | 1039 张子卡（历史 379 + 地理 294 + 政治 366） |

### P-004 · 微剧本

| 项 | 内容 |
|:---|:---|
| 定位 | 人物 + 事件 + 场景 → 沉浸式微剧本（4 幕结构） |
| 输入 | 人物档案 + 事件时间线 + 时代背景 |
| 输入模板 | `micro_dramas.json`（每集一个） |
| 必填参数 | `episode_id` / `title` / `main_character` / `time_period` / `act1-act4` |
| 可选参数 | `narrative_style` (default: `popular-ming`) / `voice_assignments{}` |
| 复用模块 | L0: 1_ingest（人物考据）/ L1: 2_structure/TextExperience（生产） |
| 输出 | micro_dramas.json + 4 幕 Markdown + 配套音频 |
| 质量标准 | 场景完整 / 人物一致 / 时代考据准确 |
| 已产物 | 墨骨山河 ep01 颜真卿（完整）+ ep09 商鞅变法（完整）+ ep02-08 规划 |

### P-005 · 知识链

| 项 | 内容 |
|:---|:---|
| 定位 | 考纲 → 链状知识结构（带元信息） |
| 输入 | 考纲文件 + 时代范围 + 主题清单 |
| 输入模板 | `2_structure/TextExperience/古史_vX/meta.json` |
| 必填参数 | `series` / `volume` / `time_span` / `episodes[]` / `main_line` |
| 可选参数 | `cross_volume_links` / `target_students` / `chain_count_target` |
| 复用模块 | L0: 1_ingest / L1: 2_structure/TextExperience / L1: 3_render |
| 输出 | meta.json + 每集 scene_v2 JSON + 链级元信息 |
| 质量标准 | 链长 18-25 / 节点连接 / 跨链引用 |
| 已产物 | 古史 v1 革与鼎（6 集）/ v2 变与局 / v3 共和新生（4 集）/ v4 世界风云（meta 完整，6 集） |

### P-006 · 配置包

| 项 | 内容 |
|:---|:---|
| 定位 | 学科 + 题型 + 知识条目 → rujing 平台配置包 |
| 输入 | 学科范围 + 题型清单 + 知识条目 JSON |
| 输入模板 | `_03_subject_packs/<pack>/meta.json` |
| 必填参数 | `pack_id` / `subject` / `exam_type` / `question_types[]` / `config.total_score` |
| 可选参数 | `activation.suggested_sequences[]` / `statistics.{knowledge_entries, star5_entries}` |
| 复用模块 | L0: knowledge_cards（KB 来源）/ L0: ru_cardpkg_convert（转换）/ L1: 4_adapt（嵌入） |
| 输出 | 配置包目录（含 meta / capability / knowledge / prompts / scripts） |
| 质量标准 | schema 合规 / 题型覆盖完整 / 知识条目 ≥40 / star5 条目 ≥15 |
| 已产物 | cafa_calligraphy_2026（书法校考）/ geo_shanhe_2026（地理）/ political_gaokao_2026（政治） |

### P-007 · Skill 写作方案

| 项 | 内容 |
|:---|:---|
| 定位 | 卡片包 + Skill ID → 5 段式写作方案 Markdown |
| 输入 | 卡片包（已分类）+ Skill 选择 |
| 输入模板 | `docs/04-Skills/SKILL_*.md` (11 个 Skill 模板) + `chain_*.json` (4 条 Chain) |
| 必填参数 | `skill_id` / `card_package_path` / `target_length` |
| 可选参数 | `style_pack` (default: `cp-academic-pop`) / `chain_id` (用于 Chain 模式) |
| 复用模块 | L0: card_auditor / L1: skill_selector.py / L1: skill_bridge.py / L2: Skill 系统（11 个） |
| 输出 | 5 段式写作方案 Markdown（情境→事件→动机→反思→升华） |
| 质量标准 | 模板完整 / 写作步骤覆盖 / 测试用例 ≥3 |
| 已产物 | chain_A 三步骤（ep01_颜真卿 完整验证） |

### P-008 · 视觉素材

| 项 | 内容 |
|:---|:---|
| 定位 | 草书 / 碑帖 / 文字 → 视觉素材库 + 辨析卡 |
| 输入 | 碑帖图片 + 草书片段 + 时代信息 |
| 输入模板 | `草书辨析卡/template.yaml`（待补） |
| 必填参数 | `image_path` / `character_set[]` / `style_period` |
| 可选参数 | `annotation_level` (default: `intermediate`) / `comparison_set[]` |
| 复用模块 | L0: PT-039_CalligraphyVision（视觉库）/ L1: 2_structure（嵌入） |
| 输出 | 辨析卡 JSON / Markdown + 图像元数据 |
| 质量标准 | 图像清晰 / 标签准确 / 辨析深度 ≥3 维度 |
| 已产物 | 草书辨析卡 v4（13 张） |

### P-009 · 音频

| 项 | 内容 |
|:---|:---|
| 定位 | 剧本 + voice_id → MP3 音频（旁白 / 角色） |
| 输入 | 剧本旁白 / 对话文本 + voice_id 分配 |
| 输入模板 | `templates/audio_spec.yaml`（待补） |
| 必填参数 | `script_path` / `voice_assignments{}` / `output_format` |
| 可选参数 | `speed` (default: 1.0) / `volume` (default: 1.0) / `emotion` |
| 复用模块 | L0: TTS 工具 / L1: 3_render（编排） |
| 输出 | MP3 音频 + 元数据（时长 / 角色 / 章节） |
| 质量标准 | 音量一致 / 角色音色区分 / 时长误差 ±3% |
| 已产物 | 古史 v3 共和新生（4 集完整音频，2 种音色对比） |

---

## 4. 产品状态看板（截至 2026-08-21）

### 4.1 已成熟产品（≥3 个产物，状态稳定）

| 产品 | 状态 | 产物数 | 受众规模 |
|:---|:---|:---:|:---|
| P-003 知识卡片 | 🟢 稳定 | 1039 张 | 高考 3 学科 |
| P-002 电子书 | 🟢 稳定 | 4 大模块 | K12 |
| P-005 知识链 | 🟢 稳定 | 4 卷（v1-v4） | 高考历史 |
| P-001 视频课件 | 🟡 演化中 | 4 卷 + 2 集 | 高考 + 校考 |
| P-009 音频 | 🟡 演化中 | 1 卷 4 集 | 通识 |

### 4.2 实验中产品（1-2 个产物，规则未冻结）

| 产品 | 状态 | 产物数 | 风险 |
|:---|:---|:---:|:---|
| P-004 微剧本 | 🟡 实验 | 2 集（ep01/ep09） | 8 集规划未生产 |
| P-006 配置包 | 🟡 实验 | 3 个（cafa/geo/political） | 校考 1 个跑通 |
| P-007 Skill 方案 | 🟡 实验 | 1 个完整 chain_A | 10 个 Skill 待补 |
| P-008 视觉素材 | 🟡 实验 | 13 张 | 待接入主产品 |

### 4.3 待启动产品

（暂无——9 大类已覆盖当前需求）

---

## 5. 演化规则

### 5.1 新增产品

- 必须有：定位 / 输入 / 模板 / 必填参数 / 复用模块 / 输出 / 质量标准
- 走 RFC 流程（哪怕新增 P-010 也需 willi 拍板）
- 加入本目录 + SPDT.yaml
- 默认 L1 / 实验性

### 5.2 弃用产品

- 标记为 `STATUS: deprecated`（保留文档）
- 6 个月内不复活则正式删除

### 5.3 升级产品

- L2 → L1：≥3 次成功 + 接口冻结 + 测试覆盖 ≥70%
- L1 → L0：持续稳定 ≥3 个月 + willi 拍板

### 5.4 状态变迁

```
planned → prototype → stable → deprecated
```

---

## 6. 文件索引

```
PRODUCT_LINE.md                                    ← 本文件
SPDT.yaml                                          ← 产品线注册
LAYERS.md                                          ← 分层定义
WINDOWS.md                                         ← 窗口节奏
docs/governance/分层治理检查清单.md                ← 治理检查
2_structure/TextExperience/古史_v*/meta.json       ← P-005 知识链输入
4_adapt/.../_03_subject_packs/                     ← P-006 配置包
docs/04-Skills/SKILL_*.md                          ← P-007 Skill 模板
docs/04-Skills/card_schema.json                    ← P-003 卡片 Schema
D:/4_data/knowledge_cards/00-项目文档/MANIFEST.yaml ← P-003 全局索引
```

---

## 7. 版本历史

| 版本 | 日期 | 核心变更 |
|:---|:---|:---|
| v1.0 | 2026-08-21 | 首发：9 大产品 + 6 个问题回答 + 详细规格表 + 状态看板 + 演化规则 |
