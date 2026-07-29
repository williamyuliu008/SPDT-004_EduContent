# B-P1 产出 —— LLM填参自动化管线

> 日期：2026-07-03 | 依赖：T-01~T-04 Prompt就绪 + 阶段A 3种失败模式修复
> 并行任务：OMAS Elicitation验证

---

## 一、自动化Prompt链路

```
培训素材(Markdown) 
  → [T-01] LLM提取知识单元 + content_type预分类
  → [T-02] LLM生成培训模块大纲
  → [T-03] LLM生成分镜脚本（statement+narration+graphic_type）
  → [T-04] LLM生成图形参数JSON（按content_type注入审计条件）
  → Gate L1(结构)→L2(审计条件)→L3(业务规则)→L4(属性不变式)
  → 通过? → YES: 进入渲染队列
          → NO: 回退T-04重试（附失败原因）
```

## 二、阶段A识别的3种失败模式修复

直接注入对应Prompt，不改变管线结构：

| 失败模式 | 修复方式 | 注入位置 | 预期效果 |
|---------|---------|---------|---------|
| 术语近似不精确（C1） | Prompt中追加"术语库"：`必须使用以下标准术语，不得使用近义词：ChatGPT(非Chat-GPT)、Claude(非Claude AI)、Prompt(非提示词)...` | T-01 System Prompt | C1通过率↑ |
| narration过于书面（C7） | 追加口语化few-shot：`❌'人工智能写作工具是一种基于大语言模型的智能辅助系统' → ✅'AI写作工具，简单说就是你告诉它写什么，它帮你写出来'` | T-03 System Prompt | C7通过率↑ |
| 选择建议无边界（R7） | 追加条件句式模板：`选择建议格式：'如果你更关注X，选A；如果你更需要Y，选B。两者在Z场景下都可以。'` | T-04 System Prompt（contrast部分） | R7通过率↑ |

## 三、Elicitation辅助（OMAS验证项）

在T-01 Prompt中注入"培训需求结构化诱导"——对应OMAS的Elicitation缺失：

### 注入内容

```
## 培训需求诱导（自动生成多选题，人工勾选）

如果培训素材没有明确说明以下信息，
请自动生成多选题，帮助确认：

1. 学员画像（单选）
  □ 应届生（零基础，需要从工具安装开始）
  □ 在职员工（有基础，需要效率提升技巧）
  □ 管理层（只需要核心概念和决策要点）

2. 培训深度（单选）
  □ 快速入门（10min，只讲核心操作）
  □ 系统学习（30min，覆盖常见场景）
  □ 精通进阶（60min，含案例和排错）

3. 输出形态（多选）
  □ 视频课件（Manim动画 + TTS语音）
  □ 图文教程（Markdown + 截图）
  □ 实操考核（任务卡 + 自动评分）
```

**验证方式**：对同一个培训素材，对比"无Elicitation"vs"有Elicitation"两种模式下LLM生成的content_type分类准确率。预期Elicitation版本准确率提升5-10%。

## 四、管线配置（复用AI_video_edu）

所有LLM调用复用`tools/adapters/llm_connector.py`，Prompt模板从`T-01~T-04`读取：

```
llm_connector.call(
    prompt=load_prompt('T-01'),
    input=training_material,
    output_schema=knowledge_unit_schema,
    temperature=0.3  # 降低温度→提高一致性
)
```

## 五、预期B-P1完成后的里程碑

| 指标 | 阶段A（手工基线） | B-P1目标 |
|------|----------------|---------|
| 单Scene生成时间 | ~6min（人工） | ~30s（LLM全自动） |
| L2审计通过率 | 97.9%（人工） | >90%（LLM） |
| L4审计通过率 | 100% | >95% |
| 人工抽检干预率 | 33% | <15% |
