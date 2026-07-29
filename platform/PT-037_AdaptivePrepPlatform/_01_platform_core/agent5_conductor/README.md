# Agent 5: 全局调度与推荐 (Conductor)

> 版本: v1.0 | 适用: PT-037 AdaptivePrepPlatform

## 职责概述

系统的「大脑」，决定「现在该学什么、该练什么」。根据用户四维状态模型做出调度决策。

## 用户状态模型

| 维度 | 全称 | 范围 | 说明 |
|------|------|------|------|
| S | Score（掌握度） | 0–100% | 答题正确率 + Agent2标签 |
| C | Cognitive Load（认知负荷） | 1–10 | 实时监测 |
| F | Fatigue（疲劳值） | 0–∞ | 连续学习累积 |
| I | Interest（兴趣指数） | 1–10 | 停留时长/主动提问/创作得分 |

## 决策优先级

```
优先级1：熔断保护
  if C >= 8 or F >= 3:
    → Agent3（微剧本/低功耗模式）

优先级2：核心优先（80/20法则）
  if ⭐⭐⭐⭐⭐考点 S < 80%:
    → C <= 5 ? Agent4(Lv3) : Agent4(Lv2)

优先级3：跨包联动
  if 当前学习触发跨包关联:
    → Agent4（缝合训练）

优先级4：节奏控制
  - Agent2 连续调用 <= 20分钟
  - Agent4 连续调用 <= 30分钟
  - 遵循"学-练-测-玩"循环
```

## 跨包联动示例

```
用户正在学习「安史之乱」（历史配置包）
    ↓
Agent5 发现关联：书法配置包中的「颜真卿在蒲州」
    ↓
Agent5 发现关联：地理配置包中的「蒲州地形」
    ↓
调度 Agent4 生成跨包缝合题：
  "分析蒲州地理位置对颜真卿平叛策略及书法风格的影响"
```

## 配置包专属触发条件

各配置包的 `prompts/agent5_triggers.json` 定义跨包联动触发规则。

## 调度输出格式

```json
{
  "action_type": "agent4_training",
  "target_agent": "Agent 4",
  "content_spec": {
    "type": "Lv2综合题",
    "focus": "颜真卿书法风格",
    "cross_pack_links": ["history_gaokao"]
  },
  "duration_minutes": 25,
  "priority": "P3"
}
```

## 使用方法

```python
# TODO: 集成调度决策引擎
# 输入: 全局记忆体(S/C/F/I) → Agent5决策 → 调度指令
```

## 状态

- 状态: 设计中
- 优先级: P0（平台核心）
- 参考: PT-037/_03_subject_packs/cafa_calligraphy_2026/prompts/agent5_triggers.json
