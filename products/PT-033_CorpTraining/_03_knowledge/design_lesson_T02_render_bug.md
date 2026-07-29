# 设计教训 —— T02渲染失败的根因与CGM原则验证

> 日期：2026-07-03 | 严重程度：机制性缺陷（非偶发bug）

---

## 一、事件

T02_PromptEngineering第2页文字未放入文本框——`label.next_to(box, LEFT)`把文字放在了方框左侧而非内部。

## 二、直接原因

手写了原始Manim定位代码，没有使用style_guide的`box_diagram()`函数。

```python
# ❌ 错误做法（T02旧版）
box = RoundedRectangle(...)
lb = Text(label, ...)
lb.next_to(box, LEFT, buff=0.3).shift(UP*0.15)  # 文字在box左边，不是内部

# ✅ 正确做法（T02修复版）
from style_guide import box_diagram
diagram = box_diagram(title='...', boxes=[...], edges=[...])
```

## 三、根因：违反了CGM支柱2（渲染确定性）

CGM支柱2的原文：**"人工编写渲染器/模板，AI只负责填参数，不负责决定排版。"**

T02的问题不是"这次定位写错了"——而是**每次手工编写原始Manim代码都可能引入不同的定位bug**。今天是把文字放在方框外，明天可能是颜色溢出、字体崩坏、动画时序错乱。手写原始渲染代码的正确率无法保证——**这和"不让LLM直接写Manim代码"是同一个逻辑，只是这次错误来自人类开发者而非AI。**

## 四、强制规则（加入项目知识库）

**cgm_training_factory渲染规则 R-001**：

> 所有Manim Scene渲染**必须**使用`style_guide`中的布局/图形函数（term_card / box_diagram / comparison_table / causal_chain / tree_chart / matrix_2x2 / layout_*）。
> 
> **禁止**在Scene中直接使用原始Manim定位API（`.next_to()` / `.shift()` / `.to_edge()` / `.arrange()`）进行内容布局。原始API仅限在style_guide函数内部使用。
>
> 如果需要新布局：先在`style_guide.py`中新增函数并验证，然后在Scene中调用——不做"隐藏于Scene中的手动布局"。

## 五、对CGM方法论的验证意义

这次故障恰好验证了CGM报告的三个核心论点：

1. **"AI不写Manim代码，只填参数"——不是因为AI不够强，而是正确率无法保证。** 人类开发者手写6行定位代码就出了bug，LLM写几十行渲染代码的不确定性要大得多。

2. **"渲染确定性 = 用已验证的函数库替代每次手写"**。T01用`term_card()`——完美。T02手写Manim——翻车。T02修复用`box_diagram()`——完美。这不是巧合。

3. **"约束前置"不仅约束AI，也约束人类开发者**。R-001规则是给人类用的——给自己加上"只能用style_guide函数"的约束，把犯错空间锁死。

## 六、对生产管线的改进

| 改进项 | 内容 |
|--------|------|
| Gate新增检查项 | G-12：场景是否使用了style_guide函数（检测`from style_guide import`或直接调用） |
| 代码审查规则 | 禁止Scene中裸用`.next_to()`/`.shift()`做元素定位 |
| 知识库 | R-001渲染强制规则 + style_guide函数清单 |
