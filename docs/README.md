# docs/ · L1_evolutionary · 文档与设计

> **Layer**: L1_evolutionary（默认 W_mid）
> **依据**: [LAYERS.md](../LAYERS.md) + [WINDOWS.md](../WINDOWS.md) + [SPDT.yaml](../SPDT.yaml)
> **状态**: 文档分散，部分历史悠久

---

## 定位

项目所有设计文档、实验记录、规范体系的存放地。

## 子目录

| 子目录 | 用途 | 状态 |
|:---|:---|:---:|
| `02-设计文档/` | 项目设计文档（古史 v1-v3、配置包等） | ✅ 活跃 |
| `03-实验/` | 实验记录（skill_card_writing 等） | 🟡 部分冻结 |
| `04-Skills/` | Skill 系统（11 Skill + 3 Chain + 6 Style Pack） | ✅ 活跃 |
| `05-知识卡片管理系统/` | 知识卡片系统设计需求 | ✅ 活跃 |
| `governance/` | 治理规范（CGM SOP + 分层检查清单） | ✅ 活跃 |

## 关键文档索引

### 顶层
- `architecture.md` — 项目架构
- `IF-D_Protocol_v1.0.md` — 接口协议
- `SOP_v1.0对齐审计报告.md` — SOP 审计
- `管线接口设计原则_v0.1.md` — 接口设计
- `AI写书管线与ebook-builder集成设计.md` — ebook 集成
- `教育产品线代码整合规划_v2.0.md` — 整合规划
- `自适应AI备考智能体平台设计需求书.md` — 平台需求

### governance/
- `CGMPipeline_CGM_SOP_v1.1.md` — CGM 方法论 SOP（v1.1）
- `分层治理检查清单.md` — L0/L1/L2 + W_low/W_mid/W_high 治理
- `GEOGRAPHY_RETROSPECTIVE_v1.md` — 地理回顾
- `INTERFACE_ANALYSIS_v1.md` — 接口分析

### 04-Skills/
- `card_schema.json` — 卡片格式规范 v1.3
- `SOP_知识卡片提炼.md` — 卡片提炼 SOP v1.1
- `SOP_卡片创作应用.md` — 卡片创作应用 v1.0
- `SKILL_REGISTRY.json` — Skill 注册表
- `SKILL_*.md` — 11 个 Skill 文档
- `SPDT-004_知识卡片系统_项目总览.md` — 卡系统总览
- `SPDT-004_知识卡片_测试标准设计.md` — 测试标准
- `整体工作总结_v1.2.md` — 整体工作总结

## 协作方

- **消费方**: 全员
- **被消费方**: 无

## 改动窗口

- 默认 **W_mid**（演化迭代窗）
- 重大规范变更可在 W_low

## 引用

- 上层: [SPDT.yaml](../SPDT.yaml) 中多个 pdt 引用 docs/
