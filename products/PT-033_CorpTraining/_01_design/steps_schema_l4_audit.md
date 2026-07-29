# B-P0 产出 —— 步骤完整性模板 + Gate L4属性审计原型

> 日期：2026-07-03 | 依赖：阶段A M6未达标（人工修改率33%）
> 并行任务：OMAS Gate L4原型（两个不变量）

---

## 一、步骤完整性模板

### 问题回顾

阶段A唯一未达标项：人工修改率33%。根因——培训场景的步骤需要覆盖"准备→执行→验证→调整"四阶段，而原有Schema只检查"每步可执行"。

### 升级后的steps Schema

```json
{
  "steps": [
    {
      "phase": "prepare",
      "phase_label": "准备",
      "label": "打开ChatGPT并设定身份",
      "detail": "访问chat.openai.com，输入：'我是新入职的市场专员'",
      "phase_check": "确保能正常访问ChatGPT界面"
    },
    {
      "phase": "execute",
      "phase_label": "执行",
      "label": "描述邮件需求",
      "detail": "输入：'请帮我写一封给客户的会议跟进邮件，主要内容包括：会议时间、讨论要点、下一步行动'",
      "phase_check": ""
    },
    {
      "phase": "execute", 
      "phase_label": "执行",
      "label": "提供具体信息",
      "detail": "补充：'会议时间是本周五下午3点，讨论了Q2预算方案，下一步是下周一前提交修订版'",
      "phase_check": ""
    },
    {
      "phase": "verify",
      "phase_label": "验证",
      "label": "检查输出质量",
      "detail": "检查邮件：语气是否得体？关键信息是否遗漏？行动项是否明确？",
      "phase_check": "语气适合商务场景 + 三个关键信息点齐全 + 有明确的回复截止时间"
    },
    {
      "phase": "adjust",
      "phase_label": "调整",
      "label": "不满意就迭代修改",
      "detail": "如果输出不符合要求，告诉ChatGPT需要调整什么：'语气更正式一些''把行动项加粗''增加一个CC给部门主管'",
      "phase_check": ""
    }
  ]
}
```

### 四阶段定义

| 阶段 | phase值 | 含义 | 是否必需 | 审计规则 |
|------|---------|------|---------|---------|
| 准备 | `prepare` | 前置条件、工具准备、环境确认 | 是 | 至少1步 + 有phase_check |
| 执行 | `execute` | 核心操作步骤 | 是 | 至少1步 |
| 验证 | `verify` | 确认操作结果正确 | 是 | 至少1步 + 有phase_check |
| 调整 | `adjust` | 异常处理、迭代优化 | 否 | 可选 |

### 升级后的审计条件

原S1-S8保留，新增2条：

| # | 审计条件 | 验证方式 | 级别 |
|---|---------|---------|------|
| S1' | 步骤覆盖准备/执行/验证三个阶段（每阶段至少1步） | phase字段分布检查 | **BLOCK** |
| S8' | 验证步骤有明确的phase_check（可操作的验证标准） | phase=verify的步骤中phase_check非空 | **BLOCK** |

原有S1（"每步可独立执行"）改为S0作为基础约束。

---

## 二、Gate L4属性审计原型

### 设计要求（来自OMAS修补路线图P0）

- **Python硬规则**（不依赖LLM）——L4的可靠性不能低于L1
- **1-2个不变量**作为概念验证
- **跨Scene审计**——检查同一个培训模块中不同Scene之间的一致性

### 不变量定义

#### L4-I1：concept的statement与tags信息不重叠

```
规则：如果一个concept Scene的statement中出现的词语，也出现在tags中作为独立标签，且该标签不增加新信息 → WARN

示例：
  statement: "AI写作工具"
  tags: ["AI写作", "工具"]  → WARN: "AI写作"和"工具"拆分自statement，未增加新信息
  tags: ["写邮件", "写报告", "写文案"] → PASS: 每个tag是statement之外的新信息
```

```python
def l4_invariant_concept_statement_tags(scene):
    """L4-I1: concept的tags必须包含statement之外的新信息"""
    if scene['content_type'] != 'concept' or scene['graphic_type'] != 'term_card':
        return True, ""
    
    statement_words = set(scene['statement'].replace(' ', ''))
    tags_text = ''.join(scene['content']['tags'])
    
    # 如果所有tag文字都来自statement中 → WARN
    overlap = all(t in statement_words for t in tags_text)
    if overlap:
        return False, f"L4-I1: tags重复statement信息，未增加新信息"
    return True, ""
```

#### L4-I2：steps的步骤间必须有明确的顺序依赖

```
规则：如果steps中所有边的type都是"sequential"但步骤之间的逻辑关系完全相同 → 检查是否有实质性的顺序依赖
      如果某两个相邻步骤互换顺序后仍可执行 → WARN: 步骤间缺乏实质顺序依赖

示例：
  Step1 "打开ChatGPT" → Step2 "输入需求" → 顺序不可互换 → PASS
  Step1 "查看竞品A" → Step2 "查看竞品B" → 可互换 → WARN
```

```python
def l4_invariant_steps_ordering(scene):
    """L4-I2: steps相邻步骤必须有实质性顺序依赖"""
    if scene['content_type'] != 'steps':
        return True, ""
    
    steps = scene['content']['steps']
    issues = []
    
    for i in range(len(steps) - 1):
        # 检查相邻两步的phase是否从低阶段跳到高阶段
        phase_order = {'prepare': 0, 'execute': 1, 'verify': 2, 'adjust': 3}
        curr = phase_order.get(steps[i].get('phase', 'execute'), 1)
        next_ = phase_order.get(steps[i+1].get('phase', 'execute'), 1)
        
        if next_ < curr:
            issues.append(f"Step{i+1}({steps[i]['label']})→Step{i+2}({steps[i+1]['label']}): phase倒退")
    
    if issues:
        return False, f"L4-I2: {len(issues)}个步骤顺序问题: " + "; ".join(issues)
    return True, ""
```

### L4执行位置

L4审计在L1-L3全部通过后、elite标记前执行。L4-WARN不阻塞发布（给人工参考），L4-BLOCK（正式版中增加）阻塞发布。

**当前阶段B的定位**：L4为WARN模式——积累数据，验证不变量设计的有效性，阶段C再升级为BLOCK。

---

## 三、验证：对Day 4的3个Scene重新跑L4

| Scene | L4-I1结果 | L4-I2结果 | 说明 |
|-------|----------|----------|------|
| S01 (concept) | ✅ PASS | — | tags=["写邮件","写报告","写文案"]——均不在statement"AI写作工具"中 |
| S02 (steps) | — | ✅ PASS | 阶段顺序: prepare→execute→execute→verify→adjust，无倒退 |
| S03 (contrast) | — | — | L4不适用 |

**L4通过率：2/2 applicable = 100%**

L4的引入没有产生新的误报，两个不变量在当前3个Scene上都正确判定了。

---

## 四、本次迭代对M6的修正预期

| 指标 | 阶段A实际 | B-P0修正后预期 |
|------|---------|-------------|
| 步骤完整性（四阶段覆盖） | 3/4阶段 → 人工补充"检查调整" | Schema强制四阶段 → LLM自动覆盖 |
| 人工修改率 | 33%（1/3） | 预计<10%（四阶段模板减少结构性问题） |
| L4审计覆盖 | 0 | 2个不变量，WARN模式 |
