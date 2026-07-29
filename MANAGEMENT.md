# SPDT-004 管理规范

> 版本: v1.0 | 生效: 2026-07-10
> 适用范围: 教育内容制造产品线 (7 PDT)

## 一、PDT 生命周期

```
提议 → 注册 → 开发 → 验收 → 运行 → 扩张
  │                        │
  └── 驳回                  └── 退役/合并
```

### 注册条件
1. 明确的教育细分定位（学科/客户群/年龄段，与现有 PDT 不重叠）
2. 指定 PDT 负责人（agent 或 human）
3. PDT.yaml 就位（领域定义 + 知识源 + 模板清单）
4. 首集试生产通过 CGM 审计（≥80% 通过率）

### 验收标准
1. CGM 审计通过率 ≥85%（核心门禁）
2. 端到端生产管线可运行（KB → Scene JSON → Manim → TTS → 视频）
3. 首套完整课程产出（≥5 集，含配套试题）
4. 知识图谱 + 标签体系就位

### 退役条件
- 连续 30 天无产量且无维护计划
- 或合并到更成熟 PDT

## 二、目录规范

```
SPDT-004_EduContent/
├── README.md                # 产品线概览
├── SPDT.yaml                # SPDT 注册 + PDT 清单
├── MANAGEMENT.md             # 本文件
├── pdt-registry.yaml        # PDT 详细注册表
├── docs/                    # 跨 PDT 文档
│   └── architecture.md      # 总体架构
├── pdt/                     # PDT 注册文件
│   └── {PT-ID}/
│       └── PDT.yaml         # PDT 快照
├── shared/                  # 共享引擎
│   └── video_factory/       # Manim + TTS + ffmpeg 管线
├── common/                  # 公共模块
│   ├── cgm_core/            # CGM 方法论核心库
│   ├── kb_tools/            # 知识库工具
│   └── eval_engine/         # 评估引擎（试题/组卷）
├── templates/               # CGM 模板库
│   ├── actions/             # 动作模板
│   ├── styles/              # 文风包
│   ├── voices/              # 情绪语音模板
│   └── scenes/              # 场景布局模板
├── quality/                 # 质量体系
│   ├── golden_tests/        # Golden Test 用例
│   └── audit_rules/         # CGM 审计规则
├── knowledge/               # 跨 PDT 知识资产
│   ├── tags/                # 统一标签体系
│   └── crosswalks/          # 课标/大纲对标文件
└── PT-0XX_{Name}/           # 各 PDT 独立目录
    ├── README.md
    ├── PDT.yaml
    ├── domains/             # 领域定义 + 知识源
    ├── courses/             # 课程产出
    └── reports/             # 质量报告
```

## 三、PDT 间协作规则

### 共享引擎 (shared/video_factory/)
- shared/video_factory 是 SPDT-004 的生命线，由 SPDT owner 统一维护
- 所有 PDT 必须通过 shared/video_factory 的标准化接口消费（不得私自分叉管线）
- 管线升级需走 RFC（Request for Change），评估对所有 PDT 的影响

### 知识库隔离
- 每个 PDT 维护自己的 domains/（领域知识库）
- knowledge/ 下放置跨 PDT 共享资产（标签体系、课标对标）
- PDT 间知识复用通过 knowledge/crosswalks/ 声明引用关系

### CGM 审计
- 所有 PDT 的内容输出必须通过 quality/audit_rules/ 的 CGM 审计
- 审计规则按 PDT 类型分：体制教育（PT-030/031/032）走学术性审计，企业培训（PT-033/034）走合规性审计
- 审计不通过的内容不得交付

## 四、当前 PDT 负责人

| PDT | Agent | 状态 | 成熟度 |
|---|---|---|---|
| PT-030 GaokaoPrep | agent-e926h | 运行中 | 60% |
| PT-031 GeneralEdu | agent-e926h | 新建，待验收 | 30% |
| PT-032 CollegeCourseware | agent-e926h | 运行中 | 70% |
| PT-033 CorpTraining | agent-e926h | 新建，待验收 | 40% |
| PT-034 CareerEdu | — | 规划中 | — |
| PT-035 LanguageLearning | — | 规划中 | — |
| PT-036 ChildEdu | — | 规划中 | — |

## 五、日常运营

### 生产节奏
- PT-030/032：按学科持续产出，每日至少 1 集
- PT-031：按历史时间线批次产出（事件驱动）
- PT-033：按培训需求批次产出（客户驱动）

### CGM 审计日检
- daily cron：全 PDT 最新产出抽样审计
- 输出 CGM 审计日报（通过率 + 典型案例）

### 模板库维护
- 每新增一个典型成功案例 → 提取为模板
- 模板库变更需经过模板一致性检查（不会影响已有课程）
