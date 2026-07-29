# PT-037 自适应备考智能体平台

> Adaptive Prep Agent Platform | BUILD-R × CGM 双方法论融合 | 平台层 PDT

---

## 一句话定位

**通用备考操作系统**：平台层（知识图谱+5 Agent调度+自适应训练），通过标准化配置包驱动多学科内容消费。

与 PT-030/031/032 的关系：各 PDT 提供**内容原料**（知识条目、视频课件、试题），PT-037 负责**内容消费编排**（知识图谱 + 自适应调度）。

---

## 核心架构

```
用户交互层（Web / APP）
        │
        ▼
  Agent 5（Conductor） ← 全局调度，S/C/F/I 状态模型
        │
        ├─ Agent 1（Analyst） 考纲解析 & 标引
        ├─ Agent 2（Architect）知识架构 & 对抗式审计
        ├─ Agent 3（Visual）  可视化 & 多端交互
        └─ Agent 4（Coach）   能力训练 & 动态出题
        │
        ▼
  全局记忆体（Global Memory）
  PostgreSQL · Neo4j · InfluxDB · Redis
        │
        ▼
  配置包层（Subject Packs）
  └── cafa_calligraphy_2026（首发）
  └── history_gaokao（规划）
  └── geography_gaokao（规划）
```

---

## 目录结构

```
PT-037_AdaptivePrepPlatform/
├── _00_governance/              ← 方法论文档 & 治理规范
│   ├── BUILD-R×CGM_融合方法论.md
│   ├── AGENT_DESIGN_SPEC.md     ← Agent1-5 详细设计规范
│   ├── GLOBAL_MEMORY_SCHEMA.md  ← 全局记忆体数据结构
│   └── PHASE_ROADMAP.md         ← 实施路线图
├── _01_platform_core/           ← 5个Agent核心模块
│   ├── agent1_syllabus/
│   ├── agent2_knowledge/
│   ├── agent3_visual/
│   ├── agent4_training/
│   └── agent5_conductor/
├── _02_global_memory/           ← 数据库存储规范
│   ├── postgres/    用户画像 + 错题剧本
│   ├── neo4j/       知识图谱
│   ├── influxdb/    学习轨迹时序数据
│   └── redis/       系统配置缓存
├── _03_subject_packs/           ← 配置包目录
│   └── cafa_calligraphy_2026/   ← 首发：国美书法
│       ├── meta.json
│       ├── syllabus/
│       ├── knowledge/
│       ├── capability/
│       ├── scripts/
│       ├── prompts/
│       └── resources/
├── _04_cross_pack/              ← 跨包联动引擎
└── _05_reports/                 ← 质量报告 & 学习效果
```

---

## 方法论基础

| 模型 | 来源 | 作用 |
|------|------|------|
| **BUILD-R** | 本项目原创 | 通用学习模型：Blueprint + Utility + Integration + Library + Drama + Revision |
| **CGM** | SPDT-004 传承 | 约束型生成方法论：模板+审计双驱动 |
| **对抗式审计** | 融合创新 | Gen+Critic 双模型，确保知识库准确性 |

---

## 与 SPDT-004 的关系

| 复用资产 | 来源 | 用途 |
|----------|------|------|
| quality_gate | `shared/quality/` | 内容审计标准对齐 |
| cgm_templates | `templates/` | 能力模板复用 |
| knowledge_engine | `knowledge/tags/` | 标签体系对齐 |
| eval_engine | `common/eval_engine/` | 出题质量评估 |

---

## 实施阶段

| 阶段 | 目标 | 里程碑 |
|------|------|--------|
| Phase 0 | 国美书法配置包建设 | P0知识条目录入完成 |
| Phase 1 | MVP单包运行 | Agent2+Agent4闭环 |
| Phase 2 | Agent5调度 + 全局记忆体 | 平台核心跑通 |
| Phase 3 | 跨包联动验证 | 高考历史包对接 |
| Phase 4 | 平台化，开放接口 | 成为SPD-004内容消费中枢 |
