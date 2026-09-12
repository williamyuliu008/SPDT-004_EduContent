# 教育内容资产统一索引 (ALL_CONTENT_INDEX)

> **版本**：v1.0 (2026-09-12)
> **范围**：3 仓分工（共同仓 + 雪薇专精 + 卡片数据）
> **维护**：雪薇机器 mavis（每周 _stat_content.py 报告 + 季度 audit）
> **配套**：`SPDT004_MIGRATION_v2.0_双轨版.md` + `SPDT004_HANDOVER_PROMPT_v3.0_给刘宇.md`

---

## 一、3 仓分工总览

| 仓 | GitHub | 角色 | 路径 | 主导方 |
|---|---|---|---|---|
| **SPDT-004_EduContent** | williamyuliu008/SPDT-004_EduContent | 共同仓（规范 + 工具 + 课程内容）| `D:\Z_学习平台\SPDT-004_EduContent` | 雪薇机器 mavis |
| **knowledge-cards-prod** | williamyuliu008/knowledge-cards-prod | 雪薇专精仓（高考 6 学科 + 学习中心）| `D:\Z_学习平台\knowledge-cards-prod` | 雪薇机器 mavis |
| **spdt-content-cards** | williamyuliu008/spdt-content-cards | 卡片数据 mirror 仓（172 套 K 卡）| `D:\Z_学习平台\spdt-content-cards` | 雪薇机器 mavis（autoclaw 产卡 push）|
| **刘宇机器本地仓** | （自行维护）| RUJING APP + 通用教育 + 多媒体探索 | `D:\2_products\education\SPDT-004_EduContent` | 刘宇机器 autoclaw |

---

## 二、按场景分的内容资产

### 2.1 学习中心.html（雪薇机器负责，display_target: ["学习中心"]）

#### 2.1.1 6 学科高考题库（knowledge-cards-prod）

| 学科 | 卷数 | 题数 | 闭环状态 | commit |
|---|---:|---:|---|---|
| 数学 | 145 (单题 K 卡) | 145 | ✅ 闭环 | `b877fcf` |
| 历史 | 44 (38+6 占位) | 1602 | ✅ 闭环 | `c4ba424` + `0d13fdc` |
| 地理 | 46 | 2178 | ✅ 闭环 | `e591000` |
| 政治 | 35 (33+2 源空) | 1482 | ✅ 闭环 | `180aceb` + `1c3e05d` |
| 语文 | 0 | 0 | ⏳ 待补 | （计划中）|
| 外语 | 0 | 0 | ⏳ 待补 | （计划中）|
| **合计** | - | **5407** | - | - |

#### 2.1.2 6 学科专题卡（cards/）

| 学科 | 专题数 | curated | methods | status |
|---|---:|---:|---:|---|
| 数学 | 145 + 30 | - | 30 (方法论) | ✅ |
| 历史 | 60+ | 7 (ac8338d) | - | ✅ |
| 地理 | 49 | 19 (ac8338d) | - | ✅ |
| 政治 | 60 | 23 (9910f62) | 5 (b4caf8c) | ✅ |
| 语文 | 0 | - | - | ⏳ |
| 外语 | 0 | - | - | ⏳ |

#### 2.1.3 学习中心渲染（apps/learning-hub-v2/）

| 学科 | index.html | data/*.json | spec.yaml | 备注 |
|---|---|---|---|---|
| 数学 | ✅ 1.2MB | 5 文件 | ✅ | 含 v3 集成 + tab-方法论 + tab-测验 |
| 历史 | ✅ 1.16MB | 5 文件 | ✅ | 5 tab + tab-测验 |
| 地理 | ✅ 833KB | 5 文件 | ✅ | 5 tab + tab-测验 |
| 政治 | ✅ 1.23MB | 5 文件 | ✅ | 5 tab + tab-方法论 + tab-测验 |
| 语文 | - | - | - | ⏳ |
| 外语 | - | - | - | ⏳ |

### 2.2 RUJING APP（刘宇机器负责，display_target: ["RUJING"]）

#### 2.2.1 7 PDT 产品线

| PDT | 领域 | 状态 | 成熟度 |
|---|---|---|---|
| PT-030 GaokaoPrep | 高考 6 科 | 运行中 | 60% |
| PT-031 GeneralEdu | 历史/地理/科学 | 新建，待验收 | 30% |
| PT-032 CollegeCourseware | 数学/物理/化学 | 运行中 | 70% |
| PT-033 CorpTraining | 入职/合规/技能 | 新建，待验收 | 40% |
| PT-034 CareerEdu | IT/设计/金融 | 规划中 | - |
| PT-035 LanguageLearning | 多语种 | 规划中 | - |
| PT-036 ChildEdu | 学龄前/小学 | 规划中 | - |

#### 2.2.2 课程内容（products/courses/）

| 课程 | 状态 | 位置 |
|---|---|---|
| 书法备考_墨骨山河 | ep09 完成 | `D:\2_product\PT-038_TextExperience\墨骨山河_ep09\` |
| 历史备考_古史知识链 | v1-v4 完成 | `D:\2_product\PT-038_TextExperience\古史_v{1~4}\` |
| 配置包_cafa_calligraphy_2026 | 完整 | `D:\2_product\PT-038_TextExperience\配置包_cafa_calligraphy_2026\` |

#### 2.2.3 4 步法 v1.1 母题（刘宇机器产出，本机待 mirror）

| 资产 | 数量 | 状态 | 路径 |
|---|---:|---|---|
| 数学 4 步法 | 51 张 v1.1 PASS | ✅ | `D:\4_data\knowledge_cards\数学\4step\` |
| 历史 4 步法 | 5 张 v1.1 PASS | ✅ | `D:\4_data\knowledge_cards\历史\4step\` |
| 工具链 | 4 个 .py | ✅ | `tools/` |
| 网页版 MVP | math_4step_mvp | ✅ | `products/math_4step_mvp/` |
| handoff | 5 篇 | ✅ | `handoff/MATH_*.md` |

### 2.3 共同内容（display_target: ["学习中心", "RUJING"]）

- **autoclaw_kit**（21 文件）：1_ingest/autoclaw-k/
- **v1.0 规范**：02_spec_card_v1.0.md
- **4 步法 v1.1 规范**：v2.0 MIGRATION 提到 11 扩展字段
- **K 卡数据**（172 套）：spdt-content-cards/4 学科 cards/

---

## 三、显示分流（display_target 字段 v3.0）

### 3.1 默认值
- 旧内容（v1.0 / v2.0 时代）→ `["学习中心", "RUJING"]`
- 高考 6 学科内容（雪薇机器产出）→ `["学习中心"]`（主）
- 通用教育内容（刘宇机器产出）→ `["RUJING"]`（主）
- 共同规范/工具 → `[]`（仅入仓）

### 3.2 决策原则
- 雪薇机器决定 `display_target: ["学习中心"]` 的内容
- 刘宇机器决定 `display_target: ["RUJING"]` 的内容
- 共同内容 → 双方都标，自动展示

---

## 四、长期维护约定

### 4.1 共同规范（两机都用）
- v1.0 5 核心字段：`card_id` / `chain_id` / `schema_version` / SOP / 验收标准
- v1.1 11 扩展字段：4 步法
- v3.0 1 字段：`display_target`

### 4.2 git PR 模式
- 共同仓改动 → 走 PR + 24h review
- 雪薇机器专精仓 → 雪薇直接 commit
- 刘宇机器专精仓 → 刘宇直接 commit

### 4.3 镜像策略
- 按需镜像（v2.0 拍板）
- 不强制全 mirror
- 4 步法 v1.1 母题 → 雪薇机器阶段 2 mirror

### 4.4 季度 audit
- `_stat_content.py` 跨仓统计
- 季度 release note
- 兼容性检查（schema 兼容、display_target 字段统一）

---

## 五、待办清单

### 本周
- [x] v3.0 HANDOVER_PROMPT 入仓 `docs/migration/`（commit 776be26 后续）
- [x] ALL_CONTENT_INDEX.md 跨仓索引 v1.0（本文件）
- [ ] `_stat_content.py` 跨仓统计脚本
- [ ] commit + push 到 SPDT-004_EduContent

### 本月
- [ ] 4 步法 v1.1 母题 56 张 mirror 到 `SPDT-004_EduContent/products/courses/数学/4step/` 等
- [ ] 工具链 mirror 到 `1_ingest/4step/` 或 `shared/`
- [ ] 网页版 MVP 评估整合到 `apps/learning-hub-v2/`
- [ ] display_target 字段补全 56 张 v1.1 卡
- [ ] 语文/外语 zhenti 启动（学习中心 6 学科闭环）

### 长期
- [ ] 7 PDT 产品线 PT-030 ~ PT-036 持续推进（刘宇机器）
- [ ] RUJING 客户端对接 `display_target: ["RUJING"]` 内容
- [ ] 多媒体探索（Manim 动画 + TTS 配音 + ffmpeg 视频）
- [ ] 古史 v1-v4 续作 / 墨骨山河 ep10+
- [ ] v3 学习中心集成 6 学科 + RUJING 对接

---

## 六、相关资源

- **v2.0 双轨方案**：`docs/migration/SPDT004_MIGRATION_v2.0_双轨版.md`
- **v3.0 HANDOVER_PROMPT**：`docs/migration/SPDT004_HANDOVER_PROMPT_v3.0_给刘宇.md`
- **v2.0 HANDOVER_PROMPT**：`docs/migration/SPDT004_HANDOVER_PROMPT_v2.0_给XW窗口.md`
- **阶段 1 落地说明**：`docs/migration/README.md`
- **题库索引**：`D:\Z_学习平台\knowledge-cards-prod\docs\ZHENTI_INDEX.md`
- **V3 学习中心**：`D:\Z_学习平台\knowledge-cards-prod\docs\V3_PROPOSAL.md`

---

## 七、变更记录

| 日期 | 版本 | 变更 | 拍板 |
|---|---|---|---|
| 2026-09-12 | v1.0 | 初版（3 仓分工 + display_target 字段） | 雪薇（5 条件对齐） |
