# SPDT-004：教育内容制造

> Education Content Manufacturing | 7 PDT · 全自动管线 · CGM 方法论驱动

## 一句话定位

将知识转化为可直接消费的教学成品——视频课件、培训包、试题库和交互式学习材料。

## 核心理念

**从 AI 单次生成到工业级制造。** 不依赖模型自由创作，而是通过 CGM（约束型生成方法论）将专家的教学经验编码为可复用的模板、文风包和情绪语音库，让 AI 成为"受控的教学生产线工人"。

## 覆盖领域

| PDT | 领域 | 客户 | 当前状态 |
|---|---|---|---|
| PT-030 高考备考 | 高考六科 | K12 学生 | 运行中 |
| PT-031 通识教育 | 历史/地理/科学 | 终身学习者 | 历史 SOP 已验证 |
| PT-032 高等课件 | 数学/物理/化学 | 大学生 | 运行中（数学动画工厂） |
| PT-033 企业培训 | 入职/合规/技能 | 企业员工 | 新建（cgm_training） |
| PT-034 职业教育 | IT/设计/金融 | 职业转行者 | 规划中 |
| PT-035 语言学习 | 多语种 | 语言学习者 | 规划中 |
| PT-036 儿童教育 | 学龄前/小学 | 儿童 & 家长 | 规划中 |

## 技术架构

```
知识源 (文档/课标/教材)
  → Knowledge Adapter (LLM 提取 KUs)
  → Quality Gate (G-01 ~ G-11)
  → Scene Generator (KU → Scene JSON)
  → Manim 渲染 + TTS 配音 + ffmpeg 合流
  → 成品视频 + 配套试题
```

详见 [docs/architecture.md](docs/architecture.md)

## 快速链接

- [SPDT.yaml](SPDT.yaml) — 产品线注册信息
- [MANAGEMENT.md](MANAGEMENT.md) — 管理规范
- [pdt-registry.yaml](pdt-registry.yaml) — PDT 详细注册表
