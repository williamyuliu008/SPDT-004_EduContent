# 4_adapt — 自适应编排层

## 定位

知识加工流水线的**智能编排引擎**。消费 `3_render/` 的产出，驱动个性化学习路径，为每位用户构建专属知识图谱，实现"学什么+怎么学"的自适应闭环。

## 核心职责

| 职责 | 说明 |
|:---|:---|
| **知识图谱构建** | 基于用户学习轨迹构建个性化知识图谱 |
| **学习路径编排** | 分析薄弱点 → 推荐下一个scene |
| **薄弱点驱动** | 从用户反馈中识别薄弱知识节点 |
| **5Agent调度** | Analyst/Architect/Visual/Coach/Conductor 协同 |

## 架构

```
4_adapt/
├── agents/                   ← 5Agent 集群
│   ├── analyst/               ← 薄弱点分析
│   ├── architect/             ← 知识图谱构建
│   ├── visual/                ← 知识可视化
│   ├── coach/                 ← 学习教练
│   └── conductor/             ← 总调度
├── knowledge_graph/           ← 知识图谱引擎
├── user_profiles/             ← 用户学习画像
└── _output/                   ← 编排输出（不进入Git）
```

## 消费链路

```
3_render/_output/
    │
    ├── audio/*.mp3 ──→ 纳入知识图谱节点
    ├── video/*.mp4 ──→ 学习路径标记
    └── cards/*.png ──→ 薄弱点检测输入
            │
            ↓
    识别薄弱点 → 触发 IF-E（重渲染请求）→ 3_render/
            │
            ↓
    推荐下一个 scene → IF-F（学习路径）→ 5_deliver/
```

## 数据存储

- `D:/4_data/education/AdaptivePrep/_input/` — 消费 3_render 输出
- `D:/4_data/education/AdaptivePrep/knowledge_graph/` — 知识图谱
- `D:/4_data/education/AdaptivePrep/user_profiles/` — 用户画像

## 接口协议

| 协议 | 起点 | 终点 | 内容 |
|:---|:---|:---|:---|
| IF-C1 | 4_adapt | 5_deliver | card_package（含薄弱点标记） |
| IF-C2 | 4_adapt | 5_deliver | audio_package（含学习指引） |
| IF-E | 4_adapt | 3_render | 薄弱点反馈（重渲染触发） |

## 当前状态

**建设初期** — AdaptivePrepPlatform，Maturity: 0.1
