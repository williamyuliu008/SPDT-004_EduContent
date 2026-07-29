# Agent 1: 考纲解析与标引 (Analyst)

> 版本: v1.0 | 适用: PT-037 AdaptivePrepPlatform

## 职责概述

处理输入源（考纲PDF、真题、教材），将文本转化为结构化知识点 JSON 输出。

## 核心能力

| 能力 | 描述 |
|------|------|
| 结构化提取 | 将考纲文本转化为 JSON/知识图谱节点 |
| 考频分析 | 统计各知识点在历年真题中出现频次 |
| 难度标定 | 结合布鲁姆认知分类法标注认知层级 |
| 三级标注 | 标注知识点间的依赖关系（前置/后置/并列） |

## 输入

```
输入源 → 考纲PDF / 历年真题 / 教材目录
```

## 输出

```json
{
  "kb_id": "KB_CAFA_XXX",
  "concept": "知识点名称",
  "definition": "一句话定义",
  "bloom_level": "记忆 | 理解 | 应用 | 分析 | 评价 | 创造",
  "frequency_stars": "⭐~⭐⭐⭐⭐⭐",
  "dependencies": {
    "prerequisites": ["KB_CAFA_YYY"],
    "related": ["KB_CAFA_ZZZ"]
  },
  "exam_weight": 0.0-1.0,
  "source_reference": "考纲/真题出处"
}
```

## 与其他 Agent 的关系

- **Agent 2**：将结构化节点输入 Agent 2 构建知识库
- **Agent 5**：接收 Agent 5 调度，处理新增考纲更新

## 使用方法

```python
# TODO: 集成 OCR + NLP 解析管道
# 输入: 考纲PDF → Agent1处理 → 知识点JSON
```

## 状态

- 状态: 设计中
- 优先级: P1
