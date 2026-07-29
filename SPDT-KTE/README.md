# SPDT-KTE · Knowledge Transmission Engine

> **管线名称**：知识传递引擎  
> **版本**：v1.0 | **创建日期**：2026-07-16  
> **定位**：认知科学驱动的多格式知识传递管线，从知识输入到移动端交付的完整闭环。

---

## 一、管线是什么

SPDT-KTE 是一个**垂直整合的知识传递管线**——不是三个独立项目，而是一条首尾相连的链路：

```
知识库 (PT-037)
    ↓
PT-038 内容工厂      →  微剧本 + Flashcard + 电子书 + 广播剧音频
    ↓ scene JSON v2
PT-VFX 视觉渲染引擎  →  Pillow 渲染帧 + MP4 视频
    ↓ video_package
PT-RUJ "入境" App    →  链阅读 + Flashcard复习 + 视频播放
    ↓ learning feedback
PT-038 知识链优化    →  （Phase C 反馈闭环）
```

**为什么叫"管线"而不是"产品线"**：

产品线的终点是一个交付物（一个 App、一个课程）。
管线的终点是一种**能力**——把任意学科知识，按认知规律加工，输出多格式内容，再通过终端触达用户，同时收集反馈持续优化。

这条管线跑通之后，新增一个学科（书法史、世界史、量子力学）= 写一份 meta.json + N 个 episode .py → 跑管线 → 自动产出卡片+电子书+音频+视频，不需要从零设计生产流程。

---

## 二、三个 PT 各是什么

| PT | 名称 | 定位 | 物理位置 |
|---|---|---|---|
| **PT-038** | TextExperience | 内容工厂：微剧本 + Flashcard + 电子书 + 广播剧音频 | `D:\...\PT-038_TextExperience` |
| **PT-VFX** | VideoFactory | 视觉渲染引擎：Pillow 渲染帧 + MP4 视频合成 | `D:\...\shared\video_factory` |
| **PT-RUJ** | Rujing（入境） | 移动交付终端：鸿蒙 App，链阅读 + 卡片复习 + 视频播放 | `D:\...\apps\rujing` |

---

## 三、管线核心机制

### 六尘分工

| 六尘 | PT | 产物 |
|---|---|---|
| 声尘（主） | PT-038 | 微剧本广播剧音频 + 旁白文本 |
| 色尘（辅） | PT-VFX | Pillow 渲染帧 + MP4 视频 |
| 行蕴尘 | PT-RUJ | Flashcard 间隔重复复习 |

### 五蕴链路

```
PT-038 微剧本 + PT-VFX 视频  →  PT-RUJ 链阅读（色蕴接收）
                                   ↓
PT-038 核心问题认知冲突    →  受蕴激活（好奇/共鸣）
                                   ↓
PT-038 知识链 chain_id      →  想蕴分别（初步结构化）
                                   ↓
PT-RUJ Flashcard 间隔重复  →  行蕴激活（前额叶-海马回环）
                                   ↓
PT-RUJ 生/熟二态标记       →  识蕴落地
```

### 脑科学约束（已在管线中嵌入）

- **工作记忆 4±1**：单 scene 新要点 ≤ 4，scene_quality_gate G06 校验
- **双重编码**：声尘与色尘必须语义对齐，scene_quality_gate G08 校验
- **情绪-记忆**：PT-038 每集含 emotion_trigger 字段（Phase B）
- **类比通道**：knowledge_type I/II/III/IV 分类，PT-VFX analogy_scene 模板

---

## 四、接口协议（核心约束）

管线三个 PT 之间通过**不可变接口协议**耦合：

| 接口 | 版本 | 从 | 到 | 不可变性 |
|---|---|---|---|---|
| `scene_json_v2` | 2.0.0 | PT-038 | PT-VFX | **严格**（破坏性变更 major+1） |
| `video_package_metadata` | 1.0.0 | PT-VFX | PT-RUJ | **严格** |
| `card_package_json` | 3.0.0 | PT-038 | PT-RUJ | **严格** |
| `learning_feedback` | 0.1.0 | PT-RUJ | PT-038 | 暂定（Phase C） |

接口协议定义在 `interface_protocols/` 目录。任何 PT 在实现时必须通过 schema 校验。

---

## 五、目录结构

```
SPDT-KTE/                          ← 本管线根目录（junction point 集成）
│
├── SPDT.yaml                      ← 管线元数据（含接口协议清单）
├── README.md                      ← 本文件
│
├── PT-038 @ [junction]            ← → D:\...\PT-038_TextExperience
├── PT-VFX  @ [junction]           ← → D:\...\shared\video_factory
├── PT-RUJ  @ [junction]           ← → D:\...\SPDT-001_Harmony\apps\rujing
│
├── interface_protocols/            ← 【核心】接口协议定义（冻结区）
│   ├── scene_json_v2_schema.json  ← IF-A: PT-038 → PT-VFX
│   ├── video_package_metadata.json← IF-B: PT-VFX → PT-RUJ
│   ├── card_package_schema.json   ← IF-C: PT-038 → PT-RUJ
│   └── learning_feedback.json     ← IF-D: PT-RUJ → PT-038 (Phase C)
│
├── docs/                          ← 管线级共享文档
│   ├── SPDT-KTE_architecture.md  ← 跨项目架构设计
│   ├── SPDT-KTE_cognitive_model.md← 六根六尘·五蕴·脑科学模型
│   ├── PT-038_integration.md     ← PT-038 接入规范
│   ├── PT-VFX_integration.md     ← PT-VFX 接入规范
│   ├── PT-RUJ_integration.md     ← PT-RUJ 接入规范
│   └── DRC/                       ← Design Review Committee（变更提案）
│
└── registry/                      ← PT 级注册表扩展
    └── kte_pt_registry.yaml       ← PT 专属注册表（覆盖 pdt-registry.yaml 的 KTE 相关条目）
```

---

## 六、快速导航

- **[项目总览与任务规划](docs/SPDT-KTE_项目总览与任务规划.md)** ← **首次接手请先读此文档**
- [认知模型：六根六尘·五蕴·脑科学](docs/SPDT-KTE_cognitive_model.md) — 管线理论依据
- [三项目协同方案（代码层）](docs/../PT-038_TextExperience/docs/三项目协同方案_代码层审计与补全路线图.md) — 实施路线图
- [PT-038 TextExperience](PT-038/docs/TextExperience_SOP.md) — SOP、战略分析、配置包
- [PT-VFX VideoFactory](PT-VFX/tools/工具链配置指南.md) — 工具链、场景渲染器、质量门
- [PT-RUJ 入境 App](PT-RUJ/README.md) — 功能概览、技术栈、导入服务
- [接口协议清单](#接口协议核心约束) — IF-A/B/C/D 详细定义

---

## 七、当前里程碑

| 里程碑 | 内容 | 状态 |
|---|---|---|
| **v1.0 基础管线** | PT-038 + PT-VFX + PT-RUJ 数据层打通 | 🔴 进行中 |
| **v1.1 认知嵌入** | scene JSON v2 + SOP v1.2 + 脑科学约束 | 🟡 规划 |
| **v1.2 反馈闭环** | IF-D learning_feedback + 五蕴卡点自适应 | 🟡 规划 |
| **[中长期规划](docs/SPDT-KTE_中长期规划_v1.0.md)** | P1（1-3月）× P2（3-9月）× P3（9-18月）详细任务表 | 🟡 规划 |

---

## 八、治理原则

1. **接口优先于实现**：任何 PT 改动，不能破坏已冻结接口的兼容性
2. **Schema 即法律**：`interface_protocols/` 下的 JSON Schema 是管线宪法
3. **PT 独立迭代**：`interface_protocols/` 冻结后，各 PT 可独立优化内部实现
4. **用户决策权**：涉及接口协议变更，由用户最终确认
