# 1_ingest · SPEC.md
# 知识摄入模块设计规范 v1.1
# 对应 SOP v4.0: M0 入口判别 + M1 需求澄清 + M2 领域本体消费
# Phase 1 扩展: pipeline_package 外层接口显式化
# 更新日期：2026-07-30
#
# **上级文档**：CGMPipeline_CGM_SOP_v1.1（Stage 1 详细实施手册）

---

## 一、定位

```
原始素材 ──→ 1_ingest ──→ 2_structure ──→ 3_render ──→ 4_adapt ──→ 5_deliver
                      │              │              │             │             │
                      │         scene_v2  ←→  outer（capability路由）→ render_outputs
                      │              │
                      ├─ content_spec.yaml（M1产出）
                      ├─ *.ingested.json（M2产出，含校准知识条目）
                      ├─ audit_log.json（质量门禁记录）
                      └─ pipeline_package.json（Phase1新增，外层+scene_v2内层）
```

**1_ingest = M0 + M1 + M2 在教育领域的具体实现**

**Phase 1 扩展（v1.1）**：输出 pipeline_package，统一管线传输格式：
- `outer` 字段：subject_domain / content_type / capabilities / knowledge_types（管线可读）
- `inner.scene_v2`：教育领域原生格式（scene_v2 v2.0.0，不变）
- `transform_hints`：阶段间变换提示

| SOP 阶段 | 内容 | 对应 ingest 子模块 |
|:---|:---|:---|
| **M0** | 入口判别：是否适用本 SOP | `ingest_entry_judge.py` |
| **M1** | 需求澄清 → ContentSpec YAML | `ingest_syllabus_parser.py` |
| **M2** | 领域本体消费 + 质量校准 | `ingest_quality_calibrator.py` |

---

## 二、输入源分类

| 来源类型 | 典型素材 | 可信度 | 说明 |
|:---|:---|:---|:---|
| **考纲** | 国美书法校考大纲 / 高考历史考纲 | **E**（官方） | 最权威的知识边界定义 |
| **古籍原文** | 《说文解字》《书谱》《史记》OCR | **E**（专家） | 经学界共识确认的内容 |
| **教材** | 历代书法论文选 / 大学书法教材 | **D**（编辑审核） | 需防版本差异 |
| **网络** | 维基/百度百科/学术网站摘要 | **C**（大众） | 需严格质量校准 |
| **专家口述** | 教师备课笔记/方向性判断 | **D-E** | 需人工确认 |

---

## 三、子模块设计

### 3.1 ingest_entry_judge（M0）

**入口判别**：判断给定课程包是否适用本 SOP。

```python
class IngestEntryJudge:
    def judge(self, raw_input: dict) -> EntryDecision:
        """
        四准入判据（全部满足→适用）：
        C1 最终产出是可定义结构的知识包
        C2 知识加工规则可被模板化
        C3 目标受众对"好内容"有共识标准
        C4 内容可被后续复用

        输出：EntryDecision(applicable: bool, reasons: list, content_type: str)
        """
```

### 3.2 ingest_syllabus_parser（M1）

**考纲解析 → ContentSpec YAML**

核心任务：
1. 从考纲 PDF/Markdown 提取题型、权重、参考书目
2. 识别关键词频次（考点密度）
3. 生成 ContentSpec YAML

```python
class SyllabusParser:
    def parse(self, syllabus_file: Path) -> ContentSpecYAML:
        """
        输入：考纲文件（PDF/Markdown/JSON）
        处理：
          1. 题型结构提取（正则/LLM）
          2. 考点权重计算（分词+频率统计）
          3. 参考书目关联（古籍/教材）
          4. ContentSpec YAML 生成

        输出：ContentSpecYAML（含 question_types/weights/reference_texts/kpi）
        """
```

**ContentSpec YAML Schema**（教育领域）：

```yaml
spec_id: "CAFA_书法_复试_2026"
spec_version: "1.0"
domain: "education"
content_type: "B1_deep_content"    # SOP v4.0 B1

exam_meta:
  exam_name: "中国美术学院书法学本科专业复试"
  exam_code: "CAFA_书法_复试"
  subject: "书法与篆刻"
  total_duration_min: 60
  total_score: 100

question_types:
  - id: "Q_TRANSDUCTION"
    name: "译篆"
    weight: 0.25
    description: "将简体汉字按《说文解字》标准译为小篆"
    key_topics: ["小篆", "说文540部首", "六书"]
  - id: "Q_PUNCT_TRANSLATION"
    name: "句读与翻译"
    weight: 0.35
    description: "无标点文言文断句并翻译为现代汉语"
    key_topics: ["句读", "文言翻译", "语境推断"]
  - id: "Q_TERM_EXPLAIN"
    name: "名词解释"
    weight: 0.40
    description: "书法史/书论核心概念的名词解释"
    key_topics: ["书法史", "书论", "六书", "书风"]

reference_texts:
  - title: "《说文解字》"
    author: "许慎"
    trust: "E"
    weight_in_syllabus: 0.30
  - title: "《书谱》"
    author: "孙过庭"
    trust: "E"
    weight_in_syllabus: 0.20
  - title: "《史记》"
    author: "司马迁"
    trust: "E"
    weight_in_syllabus: 0.15

quality_constraints:
  factual_accuracy: "expert_reviewed"    # E级可信度优先
  cross_check_required: true             # 古籍内容需多源印证
  hallucination_threshold: 0.05          # 幻觉率容忍上限 5%

production_target:
  knowledge_entries_target: 50         # kb_vocab.json 目标条目数
  ability_count_target: 8               # ability_list.json 目标能力数
  coverage_target: 0.85                # 考点覆盖率目标

human_checkpoint: ["M1_syllabus_confirmed"]
```

### 3.3 ingest_quality_calibrator（M2 核心）

**双 Agent 质量校准**

这是 ingest 的质量核心，用对抗式验证防止低质量素材进入 2_structure。

```python
class QualityCalibrator:
    def calibrate(
        self,
        raw_entries: list[RawKnowledgeEntry],
        content_spec: ContentSpecYAML,
        dual_agent: bool = True
    ) -> tuple[list[IngestedEntry], AuditLog]:
        """
        双 Agent 对抗校准流程：

        Agent-A（提请方）：
          - 读取 raw_entries
          - 生成初稿知识条目（kb_vocab 格式）
          - 标注来源可信度（A/B/C）

        Agent-B（质疑方）：
          - 读取 Agent-A 产出
          - 对每条知识发起质疑：
            1. 历史事实质疑：「这个年份/地点/人物关系准确吗？」
            2. 书法术语质疑：「这个概念的定义符合学界共识吗？」
            3. 逻辑一致性质疑：「这段因果关系是否自洽？」
          - 输出质疑清单

        仲裁层（Resolver）：
          - 对每条质疑判定：接受 / 修正 / 拒绝
          - 修正后重新入池
          - 拒绝条目记录 audit_log

        输出：
          - ingested_entries: 通过校准的知识条目
          - audit_log: 质疑记录 + 仲裁结果
        """
```

**IngestedEntry Schema**（ingest 输出格式）：

```json
{
  "ingested_id": "ING_CAFA_001",
  "source_raw_id": "RAW_网络_001",
  "concept": "《说文解字》",
  "definition": "东汉许慎著，我国首部系统分析汉字字形和考究字源的字典。",
  "structured_content": {
    "定性": "作者+年代+核心贡献",
    "核心内容": "小篆基准+六书分类",
    "历史地位": "文字学根本依据"
  },
  "trust": {
    "level": "E",
    "source": "古籍原文",
    "source_title": "《说文解字》",
    "cross_checked": true,
    "cross_check_sources": ["《历代书法论文选》", "现代文字学教材"]
  },
  "exam_tags": {
    "subject": "古代汉语",
    "module": "文字学",
    "question_types": ["Q_TERM_EXPLAIN", "Q_TRANSDUCTION"],
    "frequency": "⭐⭐⭐⭐⭐",
    "cognitive_level": "理解"
  },
  "calibration": {
    "agent_a_version": "v1.2",
    "challenges": [
      {
        "agent": "Agent-B",
        "challenge_type": "fact_accuracy",
        "content": "许慎的年代应更精确为「东汉建光元年（公元121年）」而非泛称「东汉」",
        "verdict": "accepted",
        "resolution": "修正为「东汉建光元年（公元121年）」"
      }
    ],
    "rejected_entries": []
  },
  "output_status": "ready_for_2_structure"
}
```

**AuditLog Schema**：

```json
{
  "audit_id": "AUDIT_CAFA_20260729_001",
  "spec_id": "CAFA_书法_复试_2026",
  "timestamp": "2026-07-29T12:00:00+08:00",
  "calibration_mode": "live",   // ⚠️ 必填："live"=真实API校准，"mock"=API未设置模式
  "dual_agent": {
    "agent_a": "proposer",
    "agent_b": "adversary",
    "total_challenges": 47,
    "accepted": 41,
    "rejected": 6,
    "rejected_reasons": {
      "fact_inaccuracy": 3,
      "definition_conflict": 2,
      "hallucination_detected": 1
    }
  },
  "trust_distribution": {
    "E": 30,
    "D": 12,
    "C": 5
  },
  "pass_rate": 0.872,
  "pass_threshold": 0.80,
  "overall_verdict": "PASS"
}
```

> **⚠️ Mock 模式风险提示**（来源：地理科目经验，2026-08-01）：
>
> 当 `DEEPSEEK_API_KEY` 等环境变量未设置时，校准器进入 Mock 模式：
> - 所有条目默认 C 级信任，直接接受，**不触发真实质疑**
> - 数值类条目（流量/面积/年份/百分比）未经验证
> - **地理/理科类科目数值精度要求极高，误判一个数量级即完全错误**
>
> Mock 模式 audit_log 必须包含 `calibration_mode: "mock"` 字段和醒目警告，提示人工复核关键数值条目。
> **强烈建议**：数值密集型科目（地理/物理/化学/历史年代）使用真实 API 进行 M2 校准。

### 3.4 ingest_raw_material（M2 预处理）

**原材料预处理**

```python
class RawMaterialPreprocessor:
    def preprocess(self, raw_source: Path | URL) -> list[RawKnowledgeEntry]:
        """
        输入类型处理：
        - PDF（考纲）    → pdfplumber 提取文本 + 表格
        - Markdown        → 标题/列表结构解析
        - OCR（古籍）    → pytesseract + 语言模型校正
        - URL（网络）    → 爬取 + 去广告 + 正文提取

        输出：RawKnowledgeEntry 列表（含 raw_id / text / source_url / estimated_trust）
        """
```

---

## 四、完整工作流

```
① raw_input（考纲 PDF / 古籍 OCR / 网络 URL）
    │
    ├─→ ingest_entry_judge（M0）
    │         └─ 判定：适用 SOP / 不适用 / 需要人工确认
    │
    └─→ [适用] ingest_syllabus_parser（M1）
              └─→ content_spec.yaml（M1 人类检查点 #1）
                  │
                  ├─→ [人类确认] ✅
                  └─→ [修改] ↩️ 重新生成

              ingest_raw_material（M2 预处理）
                  └─→ list[RawKnowledgeEntry]
                          │
                          ↓
              ingest_quality_calibrator（M2 核心）
                  └─→ list[IngestedEntry] + AuditLog
                          │
                          ├─→ [pass_rate >= 0.80] ✅
                          │       │
                          │       └─→ [人类确认] ✅
                          │               └─→ 输出 → 2_structure/
                          │
                          └─→ [pass_rate < 0.80] ❌
                                  └─→ 回写修正 → 重新校准
```

---

## 五、与 SOP v4.0 M0-M2 的完整映射

| SOP 步骤 | 动作 | ingest 实现 |
|:---|:---|:---|
| M0 C1-C4 | 入口四判据 | `ingest_entry_judge` |
| M1 | 6维度提问 → ContentSpec | `ingest_syllabus_parser` |
| M2 | KBC查询 → 术语词典 → 体裁匹配 | `ingest_quality_calibrator` + KBC接口 |
| M2 两级降级 | KBC无本体 → 公开本体 → 最小词典 | KBC fallback + minimum 20条底线 |
| M2 体裁注册 | 已有模板但未注册 → 先注册再入M3 | `ingest_genre_registrar`（可选）|

---

## 六、目录结构

```
1_ingest/
├── SPEC.md                         ← 本文件（模块设计规范 v1.1）
├── README.md                        ← 定位说明
│
├── ingest_entry_judge.py          ← M0：入口判别
├── ingest_syllabus_parser.py       ← M1：考纲解析 → ContentSpec YAML
├── ingest_quality_calibrator.py   ← M2：双Agent质量校准
├── ingest_raw_material.py          ← M2：原材料预处理
│
├── router/                         ← M0 后置路由（Phase1 新增外层接口）
│   ├── router.py                  ← B1-B4 路由器 + to_outer() 外层生成
│   ├── content_type.yaml          ← B1-B4 路由规则
│   └── __init__.py
│
├── schemas/                        ← ingest 输出 Schema
│   ├── content_spec.schema.yaml
│   ├── ingested_entry.schema.json
│   └── audit_log.schema.json
│
├── config/                         ← ingest 配置
│   ├── trust_levels.yaml           ← A/B/C/D/E 可信度定义
│   └── calibration_rules.yaml      ← 双Agent质疑规则
│
└── _output/                       ← ingest 产出（不进入Git）
    ├── content_spec/               # 每课程包一份
    ├── ingested/                   # 每课程包一份
    └── pipeline_packages/          # Phase1: pipeline_package 格式（含 outer+scene_v2）
```
```

---

## 七、与 cafa_calligraphy_2026 的关系

现有 `配置包_cafa_calligraphy_2026/` 是 ingest 的**手工产出物**：

| cafa 配置包文件 | 对应 ingest 产出 |
|:---|:---|
| `meta.json` | `content_spec.yaml`（解析自官方考纲） |
| `kb_vocab.json` | `ingested/*.ingested.json`（经过双Agent校准） |
| `ability_list.json` | `ingested/*.ability.json`（从 ingested entries 派生） |
| `answer_templates.json` | `content_spec.yaml`（从题型规格派生） |

**流水线化目标**：将手工产出变为自动化管道输出。

---

## 九、Phase 1：pipeline_package 外层接口（v1.1 新增）

### 9.1 背景

管线需要支持多学科内容流动（书法史/数学/化学/历史）。不同学科的内部知识表示完全不同（scene_v2 ≠ math_v1 ≠ chem_v1），但管线的路由、渲染、编排决策只需要通用的元数据。

**解决方案**：两层接口。
- `outer`：管线通用元数据（subject_domain / capabilities / knowledge_types）
- `inner`：学科自治内容（scene_v2 / math_v1 / chem_v1）

### 9.2 外层字段说明

```json
{
  "version": "1.0.0",
  "outer": {
    "subject_domain": "HIST_ART",           // 学科域（来自 Domain Registry）
    "subject_detail": "书法史",
    "content_type": "B1_deep_content",     // B1/B2/B3/B4
    "knowledge_types": ["K_CONCEPT"],     // K_FACT / K_CONCEPT / K_PROCEDURE / K_METACOG
    "capabilities": ["needs_narrative", "needs_analogy", "needs_visual"],
    "source_chain_id": "cafa_calligraphy_2026_ep01",
    "trust_level": "E"
  },
  "inner": {
    "schema": "scene_v2",
    "schema_version": "2.0.0",
    "data": { /* scene_v2 内容 */ }
  },
  "transform_hints": { ... }
}
```

### 9.3 管线各阶段对外层的读写

| 阶段 | 读 outer | 写 outer | 写 inner |
|:---|:---|:---|:---|
| 1_ingest | — | ✅ 生成初始 outer（via router.to_outer()） | — |
| 2_structure | ✅ 读取 content_type / capabilities | ✅ 丰富化 outer | ✅ 填充 scene_v2 |
| 3_render | ✅ 读取 capabilities → 路由 renderer | ✅ 追加 render_outputs | — |
| 4_adapt | ✅ 读取 knowledge_types / capabilities | ✅ 写入 quality_score / adaptive_notes | ✅ 更新学习路径 |
| 5_deliver | ✅ 读取所有 outer 字段 | ✅ 写入终检元数据 | — |

### 9.4 router.to_outer() 使用方式

```python
from ingest_entry_judge import IngestEntryJudge
from router import ContentRouter

judge = IngestEntryJudge()
router = ContentRouter()

decision = judge.judge(raw_input)
route = router.route(decision, raw_input)

# Phase 1: 生成 pipeline_package outer
outer = route.to_outer(raw_input, content_spec)
# → 用于 education_adapter.build_pipeline_package() 组装完整 package
```

---

## 十、实施优先级

| 优先级 | 子模块 | 说明 |
|:---|:---|:---|
| 🔴 P1 | `ingest_syllabus_parser.py` | 最小可行：考纲 Markdown → ContentSpec YAML |
| 🟡 P2 | `ingest_entry_judge.py` | M0 入口判别（轻量逻辑） |
| 🟡 P3 | `ingest_quality_calibrator.py` | 核心：双Agent校准 |
| 🟢 P4 | `ingest_raw_material.py` | OCR + 网络爬取（依赖外部工具） |
| ✅ P1（Phase1） | `router.to_outer()` + `build_pipeline_package()` | 外层接口生成（已完成） |

