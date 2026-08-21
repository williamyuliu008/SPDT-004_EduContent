# 1_ingest 输入端 Envelope 规范 v1.0

> **版本**：v1.0（2026-08-21）
> **目的**：定义 1_ingest 知识摄入层**对外接口机制**——上游怎么喂、喂什么、怎么知道处理完。
> **配套**：[SPDT.yaml v3.0](../SPDT.yaml) + [PRODUCT_LINE.md v2.0](../PRODUCT_LINE.md) + [LAYERS.md](../LAYERS.md)
> **状态**：W22 治理首发

---

## 1. 设计动机

之前 1_ingest 内部有 M0 入口判别 / M1 考纲解析 / M2 质量校准，**但对外接口机制不明确**：

| 问题 | 现状 | 后果 |
|:---|:---|:---|
| 上游是谁？ | 不明确 | 谁都能调，无法治理 |
| 怎么喂？ | 文件直接丢 | 没有标准化入口 |
| 喂什么格式？ | 任意 PDF/YAML | M0/M1 解析困难 |
| 怎么知道处理完？ | 无 | 上游不知何时取结果 |

**解决**：4 层接口机制 + Envelope JSON 标准化信封。

---

## 2. 4 层接口机制

### 2.1 Layer 1 · 数据格式

**Envelope JSON v1.0**（标准化信封）+ 任意素材附件

详见 [envelope.schema.json](schemas/envelope.schema.json) JSON Schema 验证。

### 2.2 Layer 2 · 投递机制

**文件投递（Envelop 队列）**：
```
D:/4_data/ingest_queue/
  <ingest_id>/
    envelope.json          # 标准化信封（必填）
    sources/               # 原始素材
      <file_1>.pdf
      <file_2>.md
    ...
```

> **目录约定**：`D:/4_data/ingest_queue/` 是项目数据目录（`AGENTS.md` 规范），不在 Git 仓库内。

### 2.3 Layer 3 · 接口形式

| 阶段 | 接口 | 状态 |
|:---|:---|:---:|
| W22 | CLI（手动）| ✅ 落地 |
| W23 | API（HTTP）| 📋 planned |
| W25 | Web UI | 📋 planned |

**当前（W22）**：通过 `python 1_ingest/ingest_cli.py submit <envelope_path>` 提交。

### 2.4 Layer 4 · 触发方式

| 阶段 | 触发 | 状态 |
|:---|:---|:---:|
| W22 | 手动（CLI）| ✅ 落地 |
| W23 | 定时（cron）| 📋 planned |
| W24 | 事件（文件 watcher）| 📋 planned |

**当前（W22）**：手动提交。**W23 增加**：自动轮询 `ingest_queue/` 目录（每 1 分钟），新 Envelope 触发处理。

---

## 3. Envelope JSON 规范 v1.0

### 3.1 完整示例

```json
{
  "envelope_version": "1.0",
  "ingest_id": "550e8400-e29b-41d4-a716-446655440000",
  "submitted_at": "2026-08-21T17:30:00+08:00",
  "submitted_by": "willi",
  "source_type": "exam_syllabus",
  "source_paths": [
    "sources/2026-gaokao-history-syllabus.pdf"
  ],
  "priority": "P1",
  "metadata": {
    "domain": "高考历史",
    "exam_type": "gaokao",
    "expected_chains": ["古史_v4_18链"],
    "target_products": ["P-001 视频", "P-002 知识卡片", "P-003 电子书"]
  },
  "callback": {
    "on_complete": "ingest://completed/550e8400-e29b-41d4-a716-446655440000",
    "on_failed": "ingest://failed/550e8400-e29b-41d4-a716-446655440000"
  }
}
```

### 3.2 字段定义

| 字段 | 类型 | 必填 | 说明 |
|:---|:---|:---:|:---|
| `envelope_version` | string | ✅ | 规范版本，当前 `1.0` |
| `ingest_id` | UUIDv4 | ✅ | 全局唯一，建议用 `uuid.uuid4()` |
| `submitted_at` | ISO-8601 | ✅ | 提交时间（带时区） |
| `submitted_by` | enum | ✅ | 上游身份（详见 §4） |
| `source_type` | enum | ✅ | 素材类型（详见 §3.3） |
| `source_paths` | string[] | ✅ | 相对 envelope 目录的素材路径列表 |
| `priority` | enum | ✅ | P0/P1/P2/P3（详见 §3.4） |
| `metadata.domain` | string | ✅ | 学科领域 |
| `metadata.exam_type` | string | ✅ | 考试类型（gaokao/cafa/...） |
| `metadata.expected_chains` | string[] | ⬜ | 期望生成的知识链（中间产物 M-001） |
| `metadata.target_products` | string[] | ⬜ | 目标真产品（来自 PRODUCT_LINE.md v2.0） |
| `callback.on_complete` | URI | ⬜ | 完成回调（W23+ 支持） |
| `callback.on_failed` | URI | ⬜ | 失败回调（W23+ 支持） |

### 3.3 source_type 枚举

| 值 | 含义 | 走 M0/M1/M2 哪个？ |
|:---|:---|:---|
| `exam_syllabus` | 考纲文件 | M0 → M1（必走）→ M2 |
| `ancient_text` | 古籍原文 | M0 → M2（OCR 路径） |
| `web` | 网络素材 | M0 → M2（爬取路径） |
| `expert_notes` | 专家口述笔记 | M0 → M2（直接） |
| `mixed` | 混合 | M0 → 按子类型路由 |

### 3.4 priority 枚举

| 等级 | 含义 | 响应时间 |
|:---|:---|:---|
| P0 | 生产故障 / 安全漏洞 | 立即（< 1h） |
| P1 | 关键里程碑 / 高考前 | 当天 |
| P2 | 日常生产 | 1 周内 |
| P3 | 实验性 / 长期 | 排队 |

### 3.5 submitted_by 枚举

| 值 | 身份 | 默认 priority |
|:---|:---|:---|
| `willi` | 决策者 | P0/P1 |
| `Mavis` | 本机管家 | P1/P2 |
| `autoclaw` | 生产 AI（另一台电脑） | P2/P3 |
| `<spdt_id>` | 其他 SPDT 项目 | P2/P3 |

---

## 4. 上游身份矩阵

| 上游 | 接口形式 | 触发方式 | 典型 priority | 配额 |
|:---|:---|:---|:---:|:---|
| willi（决策者） | CLI + Web UI | 手动 | P0/P1 | 无限 |
| Mavis（管家） | CLI | 手动 | P1/P2 | 无限 |
| autoclaw（生产 AI） | CLI + 文件 | 定时（W23+）| P2/P3 | 每日 ≤10 |
| 其他 SPDT | API（W23+）| 事件（W24+）| P2/P3 | 每日 ≤5 |

---

## 5. 处理流程

```
上游写 Envelope JSON + 投放素材
        ↓
D:/4_data/ingest_queue/<ingest_id>/
  ├── envelope.json
  └── sources/<files>
        ↓
1. 入口检测（W22: 手动 / W23+: watcher）
        ↓
2. M0 入口判别（C1-C4 四判据）
   - 通过 → 接受（accepted）
   - 拒绝 → 投递到 ingest_rejected/<ingest_id>/
   - 调整 → 返回调整建议
        ↓
3. M1 考纲解析（仅 source_type=exam_syllabus）
   - 产出 ContentSpec YAML
        ↓
4. M2 质量校准（双 Agent 对抗）
   - 产出 ingested.json + audit_log.json
        ↓
5. 投递到 2_structure 队列
   D:/4_data/2_structure_queue/<chain_id>/
        ↓
6. 回调通知（W23+ 支持）
   - on_complete → 成功
   - on_failed → 失败 + 错误原因
```

---

## 6. 与现有 1_ingest 组件的关系

| 现有组件 | 在 Envelope 流程中的角色 | 状态 |
|:---|:---|:---:|
| `ingest_entry_judge.py` (M0) | Step 2：入口判别 | ✅ 集成 |
| `ingest_syllabus_parser.py` (M1) | Step 3：考纲解析 | ✅ 集成 |
| `ingest_quality_calibrator.py` (M2) | Step 4：质量校准 | ✅ 集成 |
| `ingest_raw_material.py` (OCR/爬取) | Step 3 旁路 | 📋 待实现 |
| `config/trust_levels.yaml` | M2 校准规则 | ✅ 已有 |
| `config/calibration_rules.yaml` | M2 质疑规则 | ✅ 已有 |
| `schemas/content_spec.schema.json` | Step 3 输出验证 | ✅ 已有 |
| `schemas/ingested_entry.schema.json` | Step 4 输出验证 | ✅ 已有 |
| `schemas/audit_log.schema.json` | Step 4 输出验证 | ✅ 已有 |
| **新增 `schemas/envelope.schema.json`** | Step 1 输入验证 | ✅ W22 落地 |
| **新增 `ingest_cli.py`** | Step 1 CLI 入口 | 📋 W22 待写 |

---

## 7. 落地计划

| 阶段 | 任务 | 状态 |
|:---|:---|:---:|
| W22 | 写 `ENVELOPE_SPEC.md`（本文件）| ✅ |
| W22 | 写 `schemas/envelope.schema.json` | ✅ |
| W22 | 写 `ingest_cli.py`（CLI 入口）| 📋 W22 下半 |
| W23 | 实现 watcher（自动轮询）| 📋 planned |
| W23 | API 入口 | 📋 planned |
| W24 | 事件触发 | 📋 planned |

---

## 8. 失败处理

### 8.1 失败分类

| 失败类型 | 原因 | 处理 |
|:---|:---|:---|
| `envelope_invalid` | Envelope JSON 不符合 schema | 拒绝（投递到 ingest_rejected） |
| `source_missing` | 素材文件不存在 | 拒绝 + 错误日志 |
| `M0_rejected` | 入口判别不通过 | 拒绝 + 理由 |
| `M1_failed` | 考纲解析失败 | 重试 3 次 → 失败 |
| `M2_failed` | 质量校准失败 | 重试 1 次 → 失败 + 人工审查 |

### 8.2 失败队列

```
D:/4_data/ingest_rejected/
  <ingest_id>/
    envelope.json          # 原 envelope
    sources/               # 原素材
    rejection.json         # 拒绝原因
```

---

## 9. 文件索引

```
1_ingest/ENVELOPE_SPEC.md                       ← 本文件
1_ingest/schemas/envelope.schema.json           ← Envelope JSON Schema
1_ingest/ingest_cli.py                          ← CLI 入口 (W22 下半)
1_ingest/ingest_entry_judge.py                  ← M0 入口判别
1_ingest/ingest_syllabus_parser.py              ← M1 考纲解析
1_ingest/ingest_quality_calibrator.py           ← M2 质量校准
1_ingest/SPEC.md                                ← 1_ingest 整体规范
1_ingest/README.md                              ← 1_ingest README
```

---

## 10. 版本历史

| 版本 | 日期 | 核心变更 |
|:---|:---|:---|
| v1.0 | 2026-08-21 | 首发：4 层接口机制 + Envelope JSON 规范 + 上游身份矩阵 + 落地计划 |
