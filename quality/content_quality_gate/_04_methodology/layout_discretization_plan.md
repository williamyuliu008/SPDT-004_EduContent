# 视频布局离散化专题 —— 研究方案

> 日期：2026-07-04
> 目标：将视频布局的输入、中间、输出空间全部离散化，建立确定性映射模型

---

## 一、空间定义

### 输入空间（需离散化）

| 维度 | 连续值 | 离散化后 |
|------|--------|---------|
| 文本长度 | 任意字数 | {S≤4, M5-8, L9-12, XL13+} |
| 内容项数 | 任意数量 | {1, 2, 3, 4, 5+} |
| 内容结构 | 自由文本 | {单概念, 双栏对比, 多行表, 顺序链, 并列节点} |
| teaching_boxes | 0-N个 | {0, 1, 2+} |

### 输出空间（已离散——style_guide函数有限集）

| 函数 | 参数 | 约束 |
|------|------|------|
| term_card | title(≤12字), keywords(≤3个×≤8字) | 固定布局 |
| box_diagram | title(≤12), boxes(≤4×label≤8+subtitle≤10), edges | 水平排列 |
| causal_chain | title(≤12), chain(≤5×≤8字) | 顺序链 |
| comparison_table | title(≤12), headers(≤4×≤8), rows(≤5×≤8) | 表格 |

### 中间元素

title, keyword, label, subtitle, chain_item, cell, header

---

## 二、分析方法

### 2.1 输入→元素映射

对每种style_guide函数，枚举所有离散输入→可能的中间元素组合：

```
term_card: {title字数} × {keyword个数} × {keyword字数}
box_diagram: {node数} × {label字数} × {subtitle字数}
causal_chain: {item数} × {item字数}
comparison_table: {行数} × {列数} × {cell字数}
```

### 2.2 分析维度（每个agent负责一个维度）

| Agent | 任务 |
|-------|------|
| Agent A | 枚举所有`(输入组合, 渲染结果, 是否出现bug)`的三元组 |
| Agent B | 检测已知失败模式（溢出/截断/字体不一致） |
| Agent C | 生成最优映射规则：给定输入→最优函数+参数选择 |

### 2.3 对抗Agent设计

对抗Agent的任务不是"找到好参数"，而是**主动寻找会导致渲染失败的最坏输入组合**：

```
给定: term_card函数
目标: 找到一组(title, keywords)参数，使得渲染结果出现缺陷
方法: 边界探测——title=12字 vs 13字, keyword=8字 vs 9字
```

---

## 三、实施方案

### 方案A：本地确定性分析（推荐，1天内完成）

无需调用LLM。直接对每种函数做参数枚举：

1. 枚举所有`(text_length, item_count, scene_type)`组合
2. 对每个组合，确定可用的style_guide函数和参数
3. 标记每个组合的约束边界（PASS/OVERFLOW/DOWNGRADE）
4. 生成确定性映射表

### 方案B：SDC cell + 多Agent（适合更复杂场景）

如果Layout设计超出当前的4种函数（例如需要新增layout类型），可调用SDC cell生成分析Agent集群。

当前场景：4种函数 x 7种元素 x 4档文本长度 = 112种组合，枚举即可完成，不需要分布式Agent。

---

## 四、产出

**离散化映射表**：针对每种输入组合→确定的输出选择

```
输入 (scene_type='concept', title_len=S, keyword_count=2, kw_len=M)
  → 输出 (function='term_card', params={title:S, keywords:[kw1_M, kw2_M]})
  → 约束: PASS（所有参数在边界内）

输入 (scene_type='concept', title_len=XL, keyword_count=3, kw_len=L)  
  → 输出 WARN: title>12→截断, kw>8→截断, kw_count=3→OK
```

---

## 五、立即执行

方案A——本地确定性枚举。4种函数×4档×3个参数维度，约50-80个组合。30分钟内完成分析并生成映射表。

需要我开始执行吗？
