# SOP v1.0 执行规范对齐审计报告
> **审计对象**：SPDT-004 v2.3 + SPDT-005 v2.1
> **规范基准**：`D:/1_omas/governance/内容制造管线执行规范_v1.0.md`
> **审计日期**：2026-07-29

---

## §0 规范要求速查

| 维度 | SOP v1.0 要求 |
|:---|:---|
| 五阶段目录 | `1_ingest` / `2_structure` / `3_render` / `4_adapt` / `5_deliver` |
| SOP M0-M6 映射 | 1_ingest→M0+M1+M2，2_structure→M3，3_render→M4，4_adapt→M5，5_deliver→M6 |
| omas_link.yaml | 必须含 `pipeline:` 段（§5.3） |
| MODLIB 纳管 | ContentSpec 模板 / scene_v2 Schema / 质量门禁 Schema / 体裁注册表 / 接口协议 |
| 领域门禁 | education: G-AUDIT-A/B, G-COGNITION, G-INTERFACE；media: G-SOURCE/TIMELINESS/FACTUAL/STYLE |

---

## §1 SPDT-004（教育）审计

### 1.1 五阶段目录结构 ✅ 匹配

| 阶段 | 规范要求 | SPDT-004 实现 | 状态 |
|:---|:---|:---|:---|
| 1_ingest | M0+M1+M2 | `ingest_entry_judge` + `ingest_syllabus_parser` + `ingest_quality_calibrator` | ✅ |
| 2_structure | M3 | `TextExperience`（scene_v2 生成） | ✅ |
| 3_render | M4 | `SPDT-KTE` + `video_factory`（质量门禁） | ✅ |
| 4_adapt | M5 | `AdaptivePrepPlatform`（记分卡 + 薄弱点驱动） | ⚠️ 部分（maturity=0.1） |
| 5_deliver | M6 | `TextExperienceAPP`（HarmonyOS 多端） | ✅ |

### 1.2 1_ingest 子目录结构 ⚠️ 偏差

| 规范（§2.1） | SPDT-004 实际 | 偏差说明 |
|:---|:---|:---|
| `router/` | ❌ 缺失（无 `router/` 子目录） | ingest_entry_judge.py 在根目录 |
| `router/entry_gate.py` | ⚠️ `ingest_entry_judge.py` 替代 | 功能覆盖，命名不同 |
| `router/content_type.yaml` | ⚠️ `config/trust_levels.yaml` 部分覆盖 | 用途不同（content_type 规则→可信度配置） |
| `content_spec/` | ⚠️ `ingest_syllabus_parser.py` 替代 | 功能覆盖，但非独立 validator |
| `content_spec/templates/` | ⚠️ `schemas/content_spec.schema.json` | Schema 有，模板子目录缺失 |
| `content_spec/validator.py` | ❌ 缺失 | 无独立验证脚本 |
| `ontology/` | ⚠️ `ingest_quality_calibrator.py` 内含 | 无独立 `ontology/consumer.py` |
| `ontology/consumer.py` | ❌ 缺失 | KBC 查询在 calibrator 内部，未独立 |
| `README.md` | ✅ | |

**结论**：功能基本覆盖，但与规范目录命名有偏差（不影响运行，影响规范一致性）。

### 1.3 MODLIB 纳管 ✅ 基本匹配

| 规范（§4） | 规范路径 | SPDT-004 实际 | 状态 |
|:---|:---|:---|:---|
| ContentSpec 模板 | `MODLIB/templates/content_spec_template.yaml` | `MODLIB/content_manufacturing/content_spec/B1_deep_content.yaml` | ⚠️ 路径偏差（应在 `templates/`） |
| scene_v2 Schema | `MODLIB/schemas/scene_v2_schema.json` | `MODLIB/content_manufacturing/interface_protocols/IF-A_scene_json_v2.schema.json` | ⚠️ 路径偏差 |
| 质量门禁 Schema | `MODLIB/schemas/quality_gate_schema.json` | ❌ 缺失 | 🔴 缺失 |
| 体裁注册表 | `MODLIB/genre_registry/` | `MODLIB/content_manufacturing/genre_registry/` | ⚠️ 路径偏差 |
| 接口协议 | `MODLIB/interface_protocols/` | ✅ IF-A/B/C/D 已注册 | ✅ |
| media_adapter | `MODLIB/adapters/` | ❌（SPDT-004 教育，无需 media_adapter） | ✅ N/A |
| education_adapter | `MODLIB/adapters/` | ❌ 缺失 | 🔴 缺失 |

### 1.4 质量门禁 ✅ 匹配（教育专用）

| 规范门禁（§6.2） | SPDT-004 实现位置 | 状态 |
|:---|:---|:---|
| G-AUDIT-A（历史准确性） | `3_render/SPDT-KTE/quality/` | ✅ |
| G-AUDIT-B（交叉验证） | `3_render/SPDT-KTE/quality/` | ✅ |
| G-COGNITION（认知合规） | `3_render/SPDT-KTE/quality/` | ✅ |
| G-INTERFACE（接口协议） | `3_render/SPDT-KTE/quality/` | ✅ |
| G-STRUCTURE | ❌ 缺失（规范要求） | 🔴 |
| G-FORMAT | ❌ 缺失（规范要求） | 🔴 |
| G-REUSE | ❌ 缺失 | 🔴 |
| G-REGISTRY | ⚠️ 体裁注册表有，gate 无 | ⚠️ |

### 1.5 omas_link.yaml ⚠️ 缺少 pipeline 段

| 规范要求（§5.3） | SPDT-004 omas_link.yaml | 状态 |
|:---|:---|:---|
| `pipeline.sop_family` | ❌ 缺失（仅有 `sop_family` 顶层） | 🔴 |
| `pipeline.stages_active` | ❌ 缺失 | 🔴 |
| `pipeline.execution_spec` | ❌ 缺失 | 🔴 |
| `pipeline.modlib_root` | ❌ 缺失 | 🔴 |
| SOP 族标注 | ✅ `sop_family: content_manufacturing` | ✅ |

### 1.6 SPDT-004 缺失清单

| 优先级 | 缺失项 | 影响 |
|:---|:---|:---|
| 🔴 P1 | `omas_link.yaml` 缺 pipeline 段 | OMAS 治理无法识别管线状态 |
| 🔴 P1 | MODLIB `quality_gate_schema.json` 缺失 | 跨领域质量门禁无统一 Schema |
| 🔴 P1 | MODLIB `education_adapter.py` 缺失 | 跨领域适配无标准接口 |
| 🔴 P1 | G-STRUCTURE / G-FORMAT / G-REUSE 门禁缺失 | 规范要求未完全满足 |
| 🟡 P2 | 1_ingest `ontology/` 子目录缺失 | KBC 查询未独立模块化 |
| 🟡 P2 | `content_spec/templates/` 子目录缺失 | ContentSpec 模板未独立存储 |

---

## §2 SPDT-005（媒体）审计

### 2.1 五阶段目录结构 ✅ 匹配

| 阶段 | 规范要求 | SPDT-005 实现 | 状态 |
|:---|:---|:---|:---|
| 1_ingest | M0+M1 | `platform/infrastructure/smarttext_router` | ✅ |
| 2_structure | M3 | `platform/services/ManuscriptsEngine` | ✅ |
| 3_render | M4 | `pipeline_runner.py` | ⚠️ 部分 |
| 4_adapt | M5 | `ManuscriptsEngine/agents` | ✅ |
| 5_deliver | M6 | `platform/infrastructure/autopublish` | ⚠️ 缺 checkpoint/ |

### 2.2 MODLIB 纳管 🔴 严重缺失

| 规范（§4） | 规范路径 | SPDT-005 声明（SPDT.yaml） | 状态 |
|:---|:---|:---|:---|
| article_v2 Schema | `MODLIB/schemas/article_v2_schema.json` | SPDT.yaml 声明 pending | 🔴 缺失（未建立） |
| news_v2 Schema | `MODLIB/schemas/news_v2_schema.json` | ❌ 未声明 | 🔴 缺失 |
| quality_gate Schema | `MODLIB/schemas/quality_gate_schema.json` | SPDT.yaml 声明 pending | 🔴 缺失 |
| media ContentSpec 模板 | `MODLIB/templates/content_spec_media.yaml` | ❌ 未声明 | 🔴 缺失 |
| genre_registry/media/ | `MODLIB/genre_registry/media/` | ❌ 目录不存在 | 🔴 缺失 |
| media_adapter | `MODLIB/adapters/media_adapter.py` | SPDT.yaml 声明 pending | 🔴 缺失 |
| scene_v2 Schema（教育→媒体适配基础） | `MODLIB/schemas/scene_v2_schema.json` | SPDT.yaml 有引用（通过 MODLIB 层） | ⚠️ |
| interface_protocols | `MODLIB/interface_protocols/` | ✅ IF-A/B/C 已纳管（来自 SPDT-004） | ✅ |

### 2.3 质量门禁 ✅ 声明匹配（媒体专用）

| 规范门禁（§6.3） | SPDT-005 实现声明 | 状态 |
|:---|:---|:---|
| G-SOURCE | ✅ SPDT.yaml pipeline 声明 | ✅ |
| G-TIMELINESS | ✅ SPDT.yaml pipeline 声明 | ✅ |
| G-FACTUAL | ✅ SPDT.yaml pipeline 声明 | ✅ |
| G-STYLE | ✅ SPDT.yaml pipeline 声明 | ✅ |
| G-STRUCTURE | ✅ SPDT.yaml pipeline 声明 | ✅ |
| G-FORMAT | ✅ SPDT.yaml pipeline 声明 | ✅ |
| 实际 gate 实现代码 | ❌ 代码未检查（协调型依赖 ManuscriptsEngine） | ⚠️ 待验证 |

### 2.4 omas_link.yaml ⚠️ 阶段状态偏差

| 规范要求（§5.3） | SPDT-005 omas_link.yaml | 状态 |
|:---|:---|:---|
| pipeline 段存在 | ✅ 有 | ✅ |
| `stages_active` | `[3_render, 4_adapt, 5_deliver]` | ⚠️ 偏差（SPDT.yaml v2.1 已标 active） |
| `stages_planned` | `[1_ingest, 2_structure]` | ⚠️ 偏差（SPDT.yaml v2.1 已标 active） |
| `1_ingest` 状态 | `planned` | ⚠️ 应为 `active`（smarttext_router 已存在） |
| `2_structure` 状态 | `planned` | ⚠️ 应为 `active`（ManuscriptsEngine 已存在） |
| junction_map | ✅ SPDT.yaml v2.1 有 | ✅ |

### 2.5 5_deliver 子目录偏差 ⚠️

| 规范（§2.5） | SPDT-005 实际 | 状态 |
|:---|:---|:---|
| `checkpoint/` 子目录 | ❌ 缺失 | 🔴 缺失 |
| `checkpoint/deliver_checklist.yaml` | ❌ 缺失 | 🔴 缺失 |
| `checkpoint/signoff.py` | ❌ 缺失 | 🔴 缺失 |

### 2.6 SPDT-005 缺失清单

| 优先级 | 缺失项 | 影响 |
|:---|:---|:---|
| 🔴 P1 | MODLIB `schemas/article_v2_schema.json` | media 领域无结构化 Schema |
| 🔴 P1 | MODLIB `schemas/quality_gate_schema.json` | 质量门禁无统一规范 |
| 🔴 P1 | MODLIB `adapters/media_adapter.py` | scene_v2→article_v2 无标准化适配 |
| 🔴 P1 | `5_deliver/checkpoint/` 子目录 | M6 人类检查点缺失 |
| 🔴 P1 | `omas_link.yaml` stages_active 状态偏差 | OMAS 误判管线进度 |
| 🔴 P1 | MODLIB `genre_registry/media/` 子目录 | media 体裁注册缺失 |
| 🟡 P2 | MODLIB `templates/content_spec_media.yaml` | media ContentSpec 无标准化模板 |
| 🟡 P2 | MODLIB `schemas/news_v2_schema.json` | 快讯格式无 Schema |

---

## §3 整体评估

### 3.1 SPDT-004 评分卡

| 维度 | 覆盖率 | 说明 |
|:---|:---|:---|
| 五阶段目录 | 5/5 ✅ | 全部建立 |
| SOP M0-M6 映射 | 5/6 ✅ | 4_adapt 成熟度不足（0.1） |
| MODLIB 纳管 | 3/7 ⚠️ | Schema 路径偏差 + 质量门禁 Schema 缺失 |
| 质量门禁 | 4/7 ⚠️ | 通用门禁（G-STRUCTURE/G-FORMAT）缺失 |
| omas_link.yaml | 1/5 🔴 | pipeline 段缺失 |
| **综合** | **60%** | 功能实现良好，规范合规不足 |

### 3.2 SPDT-005 评分卡

| 维度 | 覆盖率 | 说明 |
|:---|:---|:---|
| 五阶段目录 | 5/5 ✅ | 全部建立（README 层） |
| MODLIB 纳管 | 1/8 🔴 | 仅 IF-A/B/C 接口协议到位 |
| 质量门禁（声明） | 6/6 ✅ | SPDT.yaml 全部声明 |
| 质量门禁（实现） | ⚠️ | 代码实现待验证 |
| omas_link.yaml | 3/5 ⚠️ | 有 pipeline 段，但 stages_active 偏差 |
| 5_deliver/checkpoint | 0/2 🔴 | M6 人类检查点缺失 |
| **综合** | **50%** | 协调型架构声明完整，落地严重不足 |

---

## §4 修复建议

### 🔴 P1 立即修复

| # | 操作 | 目标文件 |
|:---|:---|:---|
| F1 | 更新 `omas_link.yaml` 添加 `pipeline:` 段 | SPDT-004 `omas_link.yaml` |
| F2 | 同步 SPDT-005 `omas_link.yaml` stages_active | SPDT-005 `omas_link.yaml` |
| F3 | 建立 `MODLIB/schemas/quality_gate_schema.json` | OMAS MODLIB |
| F4 | 建立 `MODLIB/schemas/article_v2_schema.json` | OMAS MODLIB |
| F5 | 建立 `MODLIB/adapters/media_adapter.py` | OMAS MODLIB |
| F6 | 建立 SPDT-005 `5_deliver/checkpoint/` 子目录 | SPDT-005 |

### 🟡 P2 建议修复

| # | 操作 | 目标文件 |
|:---|:---|:---|
| F7 | 重构 SPDT-004 1_ingest 子目录（`router/`/`content_spec/`/`ontology/`） | SPDT-004 1_ingest |
| F8 | 建立 `MODLIB/genre_registry/media/` 体裁注册表 | OMAS MODLIB |
| F9 | 建立 `MODLIB/templates/content_spec_media.yaml` | OMAS MODLIB |
| F10 | 建立 `MODLIB/adapters/education_adapter.py` | OMAS MODLIB |
| F11 | SPDT-004 补充 G-STRUCTURE / G-FORMAT / G-REUSE 门禁 | SPDT-004 3_render |

---

## §5 SOP 规范状态确认

根据审计结果，更新 SOP v1.0 执行规范 §7 路线图状态：

```diff
### Phase 1（本轮）✅
| 本规范落盘 | ✅ |
| SPDT-004 按五阶段重构 | ✅ |
| 教育产品线 SOP 衔接分析 | ✅ |

### Phase 2（下一轮）⏳
| SPDT-005 五阶段流水线重组 | ✅目录已建，内容待完善 |
| smarttext_router → 1_ingest | ✅（smarttext_router 已存在） |
| autopublish → 5_deliver | ✅（autopublish 已存在） |
| quality_gate 实现 | ⚠️声明到位，实现待验证 |
| 更新 SPDT.yaml + omas_link.yaml | ⚠️SPDT.yaml v2.1 完成，omas_link 需修 |

### Phase 3（后续）⏳
| scene_v2_schema.json → MODLIB | ✅ 部分完成（IF-A 路径偏差） |
| quality_gate_schema.json → MODLIB | 🔴 缺失 |
| content_spec_template.yaml → MODLIB | ⚠️ 路径偏差 |
| genre_registry/ → MODLIB | ⚠️ 路径偏差 |
| interface_protocols/ → MODLIB | ✅ IF-A/B/C/D 完成 |
| adapters/ → MODLIB | 🔴 缺失（两个 adapter 均未建立） |
```
