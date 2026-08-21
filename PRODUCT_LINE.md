# SPDT-004 产品线目录 v2.0

> **版本**：v2.0（2026-08-21）
> **基于**：v1.0 + willi 决策（精简产品线 / 明确"真产品 vs 中间产物" / 专注教育/备考功能性）
> **配套**：[LAYERS.md](LAYERS.md) + [WINDOWS.md](WINDOWS.md) + [SPDT.yaml](SPDT.yaml)
> **状态**：W22 治理精简首发

---

## 0. 核心变更（vs v1.0）

v1.0 列出 9 大类产品，**v2.0 精简为 4 个真产品 + 3 个中间产物**：

| 类型 | v1.0 (9 个) | v2.0 (4+3) | 变化 |
|:---|:---|:---|:---|
| **真产品** | 9 | **4** | 拿掉 2 + 降级 3 |
| **中间产物** | 0 | **3** | 显式标"不算产品" |
| **已废止** | 0 | **2** | 微剧本 + Skill 拿掉 |

**核心原则**（willi 2026-08-21 决策）：
- **真产品 = 用户直接消费**（4 个）
- **中间产物 = 服务真产品**（3 个，不算"产品"）
- **专注功能性**（准确 / 方便 / 体系 / 多平台），不追求"艺术性/感染力"
- **避免定位漂移**：服务对象是"教育/备考"用户（学生），不是"写作者/创作者"

---

## 1. 产品大类总览

### 1.1 真产品（4 个）

| ID | 产品 | 价值主张 | 已产物 |
|:---|:---|:---|:---|
| **P-001** | 视频课件 | 知识可视化的标准载体 | 古史 v1/v3 + 墨骨山河 ep01/ep09 |
| **P-002** | 知识卡片 | 高频接触的速查形态 | 1039 张子卡（历史/地理/政治） |
| **P-003** | 电子书 | 完整知识体系的章节化呈现 | H-M1/H-M2/G-M1/P-M1 四大模块 |
| **P-004** | 音频 | 通勤/沉浸式场景 | 古史 v3 完整 4 集音频 |

### 1.2 中间产物（3 个，不算"产品"）

| ID | 中间产物 | 服务于 | 状态 |
|:---|:---|:---|:---|
| **M-001** | 知识链 | P-001 视频 + P-003 电子书的共享骨架 | 古史 v1-v4 |
| **M-002** | 配置数据 | P-002 知识卡片在 APP 端的学科分组 | 3 个（cafa/geo/political） |
| **M-003** | 视觉素材 | M-002 cafa 的子模块（草书辨析） | 13 张辨析卡 |

### 1.3 已废止（2 个，v2.0 拿掉）

| v1.0 ID | 产品 | 拿掉理由 | 处理方式 |
|:---|:---|:---|:---|
| v1.0-P-004 | 微剧本 | 没有"最终用户消费形态"，本质是 P-001 的输入剧本；8 集规划只生产 2 集，资源浪费 | 合并到 P-001 视频的"剧本子模块" |
| v1.0-P-007 | Skill 方案 | 服务"写作者"超出"教育/备考"用户群；11 Skill + 3 Chain + 6 StylePack 维护成本高 | 整体拿掉，文档归档到 `docs/archive/` |

### 1.4 ID 对照表（v1.0 → v2.0）

| v1.0 ID | v2.0 ID | 变化 |
|:---|:---|:---|
| P-001 视频课件 | **P-001 视频课件** | 保留 |
| P-002 电子书 | **P-003 电子书** | 重排（让位给高频的 P-002 知识卡片） |
| P-003 知识卡片 | **P-002 知识卡片** | 重排（按使用频率升至第 2 位） |
| P-004 微剧本 | ❌ 已废止 | 合并到 P-001 剧本子模块 |
| P-005 知识链 | **M-001 知识链**（中间产物） | 降级 + 改编号 |
| P-006 配置包 | **M-002 配置数据**（中间产物） | 降级 + 改名 + 改编号 |
| P-007 Skill 方案 | ❌ 已废止 | 整体拿掉 |
| P-008 视觉素材 | **M-003 视觉素材**（中间产物） | 降级 + 改编号 |
| P-009 音频 | **P-004 音频** | 保留 |

---

## 2. 回答 willi 6 个问题（v2.0 版）

### 2.1 本管线生产内容是哪几类？

**2 大类（4 真产品 + 3 中间产物）**。

- **真产品** 是用户能直接消费的最终交付物
- **中间产物** 是支持真产品生成的内部结构 / 数据 / 素材

### 2.2 每类的输入是什么？是否有结构化模板？

#### 真产品（4 个）

| 产品 | 输入 | 模板 |
|:---|:---|:---|
| P-001 视频 | scene_v2 JSON 剧本 | `templates/scene_v2.template.json` |
| P-002 知识卡片 | 文本 / Q&A | `docs/04-Skills/card_schema.json` (v1.3) |
| P-003 电子书 | 章节 Markdown + book_config.yaml | `D:/3_infra/ebook-builder/configs/book_config.template.yaml` |
| P-004 音频 | 剧本旁白 + voice_id | `templates/audio_spec.yaml`（**W22 待补**） |

#### 中间产物（3 个）

| 中间产物 | 输入 | 模板 |
|:---|:---|:---|
| M-001 知识链 | 考纲 + 时代范围 | `2_structure/TextExperience/古史_vX/meta.json` |
| M-002 配置数据 | 学科 + 题型 + 知识条目 | `_03_subject_packs/<pack>/meta.json` |
| M-003 视觉素材 | 碑帖图 + 草书片段 | `草书辨析卡/template.yaml`（**W22 待补**） |

### 2.3 每类产品带什么参数？有缺省集合吗？

**有**。每个产品定义**必填参数 + 可选参数 + 缺省值**：

```
真产品统一参数集（default_config.yaml）:
  voice_id: "male-qn-qingse"        # TTS 默认音色
  resolution: "1080P"               # 视频分辨率
  theme: "serif"                    # 电子书排版
  cover_path: "auto"                # 封面（自动生成）
  font: "思源宋体"                  # 字体
  output_format: "html"             # 电子书输出
  exam_type: "gaokao"               # 考试类型（高考/校考）

每个产品的特定参数详见 §3。
```

### 2.4 每类产品的开发管线复用哪些模块？

**v1.0 表格有误，v2.0 修正**——**不是所有产品都走全 5 阶段**。

| 产品 | 实际走的阶段 | 关键复用 |
|:---|:---|:---|
| P-001 视频 | 1 → 2 → 3 → 5 | 知识链（M-001）/ PT-VFX / 3_render / 5_deliver |
| P-002 知识卡片 | 1 → 2 → KBC → 5 | 1_ingest / knowledge_cards / KBC.card_maker / ru_cardpkg_convert |
| P-003 电子书 | 1 → 2 → ebook_builder | 1_ingest / 2_structure / CMC.ebook_builder |
| P-004 音频 | 2 → 3 | 2_structure / 3_render + TTS |
| M-001 知识链 | 1 → 2 | 1_ingest / 2_structure/TextExperience |
| M-002 配置数据 | 4 | 4_adapt 直接生成 |
| M-003 视觉素材 | 3 | 3_render 直接出图 |

**横向模块**（不依赖阶段）：
- **L0 稳定层**（受 W_low 保护）：1_ingest / knowledge_cards / card_auditor / 模板基础设施
- **L1 演化层**（默认 W_mid）：2_structure 已产物 / OMAS Cell 集成 / autoclaw_kit
- **L2 实验层**（仅 W_high）：4_adapt 完整版（未投产）

**默认原则**：真产品走 L0/L1，**不直接调 L2 实验代码**。

### 2.5 输出分几类，分别是什么？

**3 大类**（同 v1.0）：

| 输出类别 | 内容 | 用途 |
|:---|:---|:---|
| **A. 中间产物** | scene_v2 JSON / 章节 Markdown / CardPackage JSON / 知识链 meta.json / 配置数据 | 流水线节点产物，有版本控制 |
| **B. 最终产物** | MP4 / MP3 / HTML / EPUB / CardPackage（含 rujing 上架） | **真产品交付物** |
| **C. 元数据** | MANIFEST.yaml / audit_report.html / SPDT.yaml / 校考对照表 | 治理 + 审计 |

**B 是面向用户的真产品**，A 和 C 是内部支撑。

### 2.6 各类输出的质量标准？有无核对机制？

#### 4 大质量维度（willi 决策：专注功能性）

| 维度 | 含义 | 优先级 |
|:---|:---|:---:|
| **准确性** | 知识事实零错误 | 🔴 P0 |
| **方便性** | 3 步内可消费 | 🟡 P1 |
| **体系化** | 与上下游知识关联 | 🟡 P1 |
| **多平台** | ≥2 端可消费 | 🟢 P2 |

> **v1.0 的"帧率 / 字幕对齐 / 渲染时长偏差"是技术指标，不是用户价值指标。v2.0 改用 4 维度功能性指标。**

#### 分阶建设计划（willi 决策）

**Phase A：准确性（W22-W23 优先）**
- 扩展 `card_auditor.py` 覆盖 4 个真产品
- 加准确性规则：知识事实校验、术语一致性、数据点交叉验证
- 工具：`accuracy_auditor.py`（W22 起步）

**Phase B：方便性 + 体系化（W24）**
- 方便性：UX 流程审查 checklist
- 体系化：跨链 / 跨书 / 跨学科引用校验
- 工具：`ux_review_checklist.md` + `chain_qa.py`

**Phase C：多平台（W25+）**
- 部署清单：≥2 端可消费
- 工具：`deployment_checklist.md`

#### 现有核对机制（L0 已建）

- `card_auditor.py` — 5 维度评分 + 认证体系（GOLD/SILVER/CERTIFIED）
- `tools/layer_lint.py` — 跨层依赖检查
- `tools/layer_doc_sync.py` — 文档与代码一致性
- `tools/window_check.py` — 窗口与改动层匹配

---

## 3. 4 个真产品的详细规格

### P-001 · 视频课件

| 项 | 内容 |
|:---|:---|
| 定位 | 知识可视化的标准载体 |
| 输入 | scene_v2 JSON 剧本（来自 M-001 知识链） |
| 输入模板 | `templates/scene_v2.template.json` |
| 必填参数 | `title` / `chain_id` / `scenes[]` |
| 可选参数 | `voice_id` (default: `male-qn-qingse`) / `resolution` (default: `1080P`) |
| 5 阶段 | 1 → 2 → 3 → 5 |
| 复用模块 | M-001 知识链 / L0: 模板 / L1: 3_render/SPDT-KTE / L1: PT-VFX |
| 输出 | MP4 视频 + 字幕 SRT |
| 质量标准 | 准确性（0 错误）/ 方便性（≤3 步打开）/ 体系化（链可溯）/ 多平台（≥2 端） |
| 已产物 | 古史 v1（6 集）/ 古史 v3（4 集）/ 墨骨山河 ep01 / 墨骨山河 ep09 |

### P-002 · 知识卡片

| 项 | 内容 |
|:---|:---|
| 定位 | 高频接触的速查形态 |
| 输入 | 文本 / Q&A / 任意片段 |
| 输入模板 | `docs/04-Skills/card_schema.json` (v1.3) |
| 必填参数 | `card_id` / `title` / `back` / `card_type` / `domain` / `concepts[]` |
| 可选参数 | `tags[]` / `sources[]` / `materials.*` |
| 5 阶段 | 1 → 2 → KBC → 5 |
| 复用模块 | L0: 1_ingest / L0: knowledge_cards / L0: card_auditor / L0: ru_cardpkg_convert / M-002 配置数据 |
| 输出 | CardPackage JSON + 审计报告 + rujing 上架 |
| 质量标准 | 准确性（5 维度 ≥75）/ 方便性（单卡 200 字内）/ 体系化（跨链引用）/ 多平台（rujing/Web/纸印） |
| 已产物 | **1039 张子卡**（历史 379 + 地理 294 + 政治 366） |

### P-003 · 电子书

| 项 | 内容 |
|:---|:---|
| 定位 | 完整知识体系的章节化呈现 |
| 输入 | 章节 Markdown + book_config.yaml |
| 输入模板 | `D:/3_infra/ebook-builder/configs/book_config.template.yaml` |
| 必填参数 | `title` / `author` / `chapters[]` |
| 可选参数 | `format` (default: HTML) / `theme` (default: serif) / `cover_path` |
| 5 阶段 | 1 → 2 → ebook_builder（**绕开 3/4/5**） |
| 复用模块 | L0: ebook_builder / L1: OMAS Cell (CMC.ebook_builder) / M-001 知识链（骨架） |
| 输出 | 整书 HTML / EPUB / Markdown |
| 质量标准 | 准确性（章节无错）/ 方便性（章节 ≤10）/ 体系化（跨章引用）/ 多平台（HTML/EPUB/MD） |
| 已产物 | H-M1 千年治乱 / H-M2 食货之道 / G-M1 阶梯山河 / P-M1 道路的选择 |

### P-004 · 音频

| 项 | 内容 |
|:---|:---|
| 定位 | 通勤 / 沉浸式场景 |
| 输入 | 剧本旁白 + voice_id 分配 |
| 输入模板 | `templates/audio_spec.yaml`（**W22 待补**） |
| 必填参数 | `script_path` / `voice_assignments{}` / `output_format` |
| 可选参数 | `speed` (default: 1.0) / `volume` (default: 1.0) / `emotion` |
| 5 阶段 | 2 → 3（**绕开 1/4/5**） |
| 复用模块 | L0: TTS 工具 / L1: 3_render |
| 输出 | MP3 音频 + 元数据 |
| 质量标准 | 准确性（念读无误）/ 方便性（≤3 步播放）/ 体系化（章节标记）/ 多平台（MP3 流/下载） |
| 已产物 | 古史 v3 共和新生（4 集完整，2 种音色对比） |

---

## 4. 3 个中间产物的详细规格

### M-001 · 知识链

| 项 | 内容 |
|:---|:---|
| 定位 | P-001 视频 + P-003 电子书的共享骨架 |
| 输入 | 考纲 + 时代范围 + 主题清单 |
| 输入模板 | `2_structure/TextExperience/古史_vX/meta.json` |
| 必填参数 | `series` / `volume` / `time_span` / `episodes[]` / `main_line` |
| 可选参数 | `cross_volume_links` / `target_students` / `chain_count_target` |
| 5 阶段 | 1 → 2（**不直接走 3/4/5**，作为真产品的输入） |
| 复用模块 | L0: 1_ingest / L1: 2_structure/TextExperience |
| 输出 | meta.json + 每集 scene_v2 JSON + 链级元信息 |
| 已产物 | 古史 v1 革与鼎（6 集）/ v2 变与局 / v3 共和新生（4 集）/ v4 世界风云（meta 完整） |

### M-002 · 配置数据

| 项 | 内容 |
|:---|:---|
| 定位 | P-002 知识卡片在 APP 端的学科分组 |
| 输入 | 学科 + 题型 + 知识条目 |
| 输入模板 | `_03_subject_packs/<pack>/meta.json` |
| 必填参数 | `pack_id` / `subject` / `exam_type` / `question_types[]` |
| 可选参数 | `activation.suggested_sequences[]` / `statistics.*` |
| 5 阶段 | 4（**只在 4_adapt 阶段使用**） |
| 复用模块 | L0: knowledge_cards / L0: ru_cardpkg_convert / L1: 4_adapt |
| 输出 | 配置包目录（含 meta/capability/knowledge/prompts/scripts） |
| 已产物 | cafa_calligraphy_2026 / geo_shanhe_2026 / political_gaokao_2026 |

### M-003 · 视觉素材

| 项 | 内容 |
|:---|:---|
| 定位 | M-002 cafa 的子模块（草书辨析） |
| 输入 | 碑帖图 + 草书片段 + 时代信息 |
| 输入模板 | `草书辨析卡/template.yaml`（**W22 待补**） |
| 必填参数 | `image_path` / `character_set[]` / `style_period` |
| 可选参数 | `annotation_level` (default: intermediate) / `comparison_set[]` |
| 5 阶段 | 3（**只在 3_render 阶段生产**） |
| 复用模块 | L0: PT-039_CalligraphyVision |
| 输出 | 辨析卡 JSON / Markdown + 图像元数据 |
| 已产物 | 草书辨析卡 v4（13 张） |

---

## 5. 产品状态看板（截至 2026-08-21）

### 5.1 真产品

| 产品 | 状态 | 产物数 | 受众规模 |
|:---|:---|:---:|:---|
| P-002 知识卡片 | 🟢 稳定 | 1039 张 | 高考 3 学科 |
| P-003 电子书 | 🟢 稳定 | 4 大模块 | K12 |
| P-001 视频课件 | 🟡 演化中 | 4 卷 + 2 集 | 高考 + 校考 |
| P-004 音频 | 🟡 演化中 | 1 卷 4 集 | 通识 |

### 5.2 中间产物

| 中间产物 | 状态 | 产物数 | 备注 |
|:---|:---|:---:|:---|
| M-001 知识链 | 🟢 稳定 | 4 卷 | 服务 P-001/P-003 |
| M-002 配置数据 | 🟡 演化中 | 3 个 | 服务 P-002 |
| M-003 视觉素材 | 🟡 演化中 | 13 张 | 服务 M-002 cafa |

### 5.3 已废止

| v1.0 ID | 处理方式 | 时间 |
|:---|:---|:---|
| v1.0-P-004 微剧本 | 合并到 P-001 视频的"剧本子模块" | 2026-08-21 |
| v1.0-P-007 Skill 方案 | 文档归档 `docs/archive/`，git tag `v1.0-final` | 2026-08-21 |

---

## 6. 演化规则

### 6.1 新增真产品

- 必须满足"用户直接消费"
- 必须有：定位 / 输入 / 模板 / 必填参数 / 复用模块 / 输出 / 质量标准（4 维度）
- 走 RFC 流程 + willi 拍板
- 默认 L1 / 实验性

### 6.2 降级真产品 → 中间产物

- 触发条件：发现"用户不直接消费，仅服务其他真产品"
- 流程：v(N+1).0 重新分类 + ID 改名 + 文档迁移
- 保留可溯源（ID 对照表）

### 6.3 拿掉产品

- 触发条件：长期无产物 / 资源浪费 / 定位漂移
- 流程：v(N+1).0 标记"已废止" + 文档归档 `docs/archive/` + git tag
- 6 个月内不复活则正式删除

### 6.4 升级中间产物 → 真产品

- 触发条件：发现独立用户群 + 独立消费场景
- 流程：v(N+1).0 重新分类 + ID 升级

### 6.5 状态变迁

```
真产品:
  prototype → stable → deprecated
  
中间产物:
  draft → active → deprecated
```

---

## 7. 质量标准 4 维度（详表）

| 维度 | 含义 | 度量 | 工具（分阶） | 阶段 |
|:---|:---|:---|:---|:---:|
| **准确性** | 知识事实零错误 | 5 维度评分 ≥75 | `card_auditor.py` + `accuracy_auditor.py`（待建） | A |
| **方便性** | 3 步内可消费 | UX 流程审查 | `ux_review_checklist.md`（待建） | B |
| **体系化** | 跨链/跨书/跨学科引用 | 引用完整度 | `chain_qa.py`（待建） | B |
| **多平台** | ≥2 端可消费 | 部署清单 | `deployment_checklist.md`（待建） | C |

**Phase A（W22-W23 优先）**：准确性
**Phase B（W24）**：方便性 + 体系化
**Phase C（W25+）**：多平台

---

## 8. 文件索引

```
PRODUCT_LINE.md                              ← 本文件
SPDT.yaml                                    ← 产品线注册（v3.0）
LAYERS.md                                    ← 分层定义
WINDOWS.md                                   ← 窗口节奏
docs/governance/分层治理检查清单.md          ← 治理检查
docs/archive/                                ← 已废止产品归档（待建）

P-001 视频：2_structure/TextExperience/古史_v*/
P-002 卡片：docs/04-Skills/card_schema.json + D:/4_data/knowledge_cards/
P-003 电子书：D:/3_infra/ebook-builder/
P-004 音频：2_structure/TextExperience/古史_v3/audio/

M-001 知识链：2_structure/TextExperience/古史_v*/
M-002 配置数据：4_adapt/.../_03_subject_packs/
M-003 视觉素材：products/PT-039_CalligraphyVision/草书辨析卡/
```

---

## 9. 版本历史

| 版本 | 日期 | 核心变更 |
|:---|:---|:---|
| v2.0 | 2026-08-21 | 精简：9 → 4 真产品 + 3 中间产物。拿掉 P-004 微剧本 + P-007 Skill。质量标准改为 4 维度功能性。5 阶段管线真实范围修正。新旧 ID 对照。 |
| v1.0 | 2026-08-21 | 首发：9 大产品 + 6 个问题回答 + 详细规格表 + 状态看板 + 演化规则 |
