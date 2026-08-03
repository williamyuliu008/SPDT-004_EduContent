# 1_ingest — 知识摄入层

## 定位

知识加工流水线的**入口阶段**。负责从原始素材（考纲/古籍/教材/网络）中识别、筛选、校准高质量知识原料，为后续结构化加工奠定基础。

## 核心职责

| 职责 | 说明 |
|:---|:---|
| **考纲对齐** | 锚定目标考试（国美书法/高考历史），筛选相关性最高的内容 |
| **质量校准** | 双Agent交叉验证，剔除低可信度素材 |
| **原料标注** | 元数据标记（年代/作者/可信度/版权/跨学科标签） |
| **防幻觉审计** | 历史事实/书法术语的对抗性核查 |

## 输入

- 原始考纲文件（PDF/网页）
- 古籍原文（影印件/OCR文本）
- 网络素材（网页/论文摘要）
- 专家口述笔记

## 输出

- `*.ingested.json` — 经过筛选和标注的原始知识单元
- `audit_log.json` — 质量门禁记录
- 送入 `2_structure/` 的中间包

## 当前状态

### ✅ 已实现

| 模块 | 文件 | 说明 |
|:---|:---|:---|
| M0 入口判别 | `ingest_entry_judge.py` | 四判据自动评估（C1-C4） |
| M1 考纲解析 | `ingest_syllabus_parser.py` | ContentSpec YAML 生成 |
| M2 质量校准 | `ingest_quality_calibrator.py` | 双Agent对抗校准 |
| schemas | `schemas/*.schema.json` | ContentSpec / IngestedEntry / AuditLog |
| config | `config/trust_levels.yaml` | A/B/C/D/E 可信度定义 |
| config | `config/calibration_rules.yaml` | Agent-B 质疑规则配置 |

### 🔄 待实现

| 优先级 | 模块 | 说明 |
|:---|:---|:---|
| 🔴 P4 | `ingest_raw_material.py` | OCR + 网络爬取预处理 |
| 🔴 集成 | 端到端测试 | 完整流水线联调 |

### 使用方法

```python
from ingest_entry_judge import IngestEntryJudge
judge = IngestEntryJudge()
decision = judge.judge({"type": "exam_syllabus", "path": "/path/to/package"})
# decision.to_json() → 输出判别结果
```

### 与 cafa_calligraphy_2026 的关系

现有配置包是 ingest 的手工产出物：

| 配置包文件 | ingest 产出对应 |
|:---|:---|
| `meta.json` | ContentSpec YAML |
| `kb_vocab.json` | `*.ingested.json` |
| `ability_list.json` | 从 ingested entries 派生 |
