# 线B产出 —— 企业AI智能体培训课程集

> 日期：2026-07-03 | 阶段B主体产品
> 基于：AI_video_edu培训课程体系v2.0 + cgm_training_factory content_type v2
> 目标：L1全部10节课的课程结构定义 + 首批3节课的Scene JSON

---

## 一、课程体系总览

### L1 工具操作能力 · 5模块10节课

| 模块 | ID | 课程 | content_type | 时长 |
|------|-----|------|-------------|------|
| M1 AI写作 | T01 | AI写作工具入门：30分钟上手ChatGPT/Claude | concept | 15min |
| | T02 | 提示词工程：三句话让AI输出质量翻倍 | steps+tool_demo | 15min |
| | T03 | AI辅助求职：简历优化+模拟面试 | case_study | 20min |
| M2 AI数据分析 | T04 | AI数据对话：用自然语言分析Excel数据 | concept+tool_demo | 15min |
| | T05 | AI可视化：一句话生成图表和数据看板 | tool_demo | 12min |
| M3 AI知识管理 | T06 | 搭建个人AI知识库：Dify/RAGFlow实战 | concept+steps | 20min |
| | T07 | AI文档处理：批量摘要、翻译、格式转换 | tool_demo | 12min |
| M4 AI编程 | T08 | AI写代码：Cursor/Copilot真香与真坑 | concept+tool_demo | 18min |
| | T09 | AI调试：让AI帮你找出Bug并自动修复 | steps+tool_demo | 15min |
| M5 AI效率 | T10 | AI会议+日程：自动生成纪要+行动项 | case_study | 12min |

### 三版本编译计划

每节课生成应届生版（基准，完整四阶段）、在职白领版（70%压缩，砍准备/调整）、管理层版（40%压缩，仅框架+决策要点）。

---

## 二、首批3节课Scene JSON（T01-T03）

### T01 Scene 1：concept — 什么是AI写作工具（应届生版）

```json
{
  "scene_id": "T01_S01",
  "content_type": "concept",
  "audience": "应届生",
  "graphic_type": "term_card",
  "statement": "AI写作工具",
  "narration": "AI写作工具，简单说就是你告诉它写什么，它帮你写出来。就像一个随叫随到的写作搭档——你说'帮我写封邮件'，它几秒钟就能给你初稿。从写邮件、写报告到写文案，AI都能帮你搞定。你只需要学会怎么跟它'说话'——也就是我们下节课要讲的Prompt工程。",
  "content": {
    "title": "AI写作工具",
    "definition": "基于大语言模型的智能写作助手，你说需求，它出初稿",
    "tags": ["写邮件", "写报告", "写文案"]
  },
  "audit_checks": {"C1":"术语准确","C2":"含是什么+用途","C3":"3标签≤8字","C7":"statement=关键词，narration=完整解释"}
}
```

### T01 Scene 2：steps — 四步写好邮件（应届生版，含四阶段）

```json
{
  "scene_id": "T01_S02",
  "content_type": "steps",
  "audience": "应届生",
  "graphic_type": "box_diagram",
  "statement": "四步写好邮件",
  "narration": "用ChatGPT写邮件只需要四步。准备阶段——打开ChatGPT，告诉它你是新入职的XX岗位。执行阶段一——给出邮件需求：'请帮我写一封给客户的会议跟进邮件'。执行阶段二——补充关键信息：会议时间、讨论要点、下一步行动。验证阶段——检查输出：语气是否得体？关键信息是否遗漏？行动项是否明确？调整阶段——如果不对，就让ChatGPT调整：'语气正式一些''把行动项加粗''增加一个CC给主管'。记住：第一稿不需要完美，ChatGPT的优势就是可以无限次快速修改。",
  "content": {
    "title": "四步写好邮件",
    "steps": [
      {"phase": "prepare", "label": "设定身份", "detail": "告诉AI你是谁+场景", "expect": "打开ChatGPT，看到输入界面"},
      {"phase": "execute", "label": "给出需求", "detail": "邮件目的+收件人", "expect": "AI开始生成回复"},
      {"phase": "execute", "label": "提供信息", "detail": "关键要点+行动项", "expect": "AI生成更精准的回复"},
      {"phase": "verify", "label": "检查调整", "detail": "语气+完整性+遗漏", "expect": "可直接复制使用"},
      {"phase": "adjust", "label": "迭代优化", "detail": "'语气正式一些''增加CC'", "expect": "每次修改都更接近需求"}
    ]
  }
}
```

### T01 Scene 3：contrast — ChatGPT vs Claude怎么选（应届生版）

```json
{
  "scene_id": "T01_S03",
  "content_type": "contrast",
  "audience": "应届生",
  "graphic_type": "comparison_table",
  "statement": "两大工具对比",
  "narration": "ChatGPT和Claude是目前最主流的两款AI写作工具。ChatGPT的写作风格更灵活、更有创意，特别适合需要发散思维的场景——比如写营销文案、头脑风暴、创意写作。Claude的写作更严谨、更结构化，特别适合需要精确性的场景——比如写技术文档、合同条款、学术论文。如果你是做市场的，建议从ChatGPT开始；做技术或法律的，Claude可能更顺手。好消息是两个都可以免费试用——不妨都试试，看哪个更符合你的工作习惯。",
  "content": {
    "title": "ChatGPT vs Claude",
    "headers": ["维度", "ChatGPT", "Claude"],
    "rows": [
      ["写作风格", "灵活有创意", "严谨结构化"],
      ["擅长场景", "营销/文案/头脑风暴", "技术/法律/学术"],
      ["免费版本", "GPT-4o-mini", "Claude Haiku"],
      ["建议人群", "市场/运营/产品", "技术/法律/学术"]
    ]
  }
}
```

### T02 Scene 1：steps — 三句话让AI输出质量翻倍

```json
{
  "scene_id": "T02_S01",
  "content_type": "steps",
  "audience": "应届生",
  "graphic_type": "box_diagram",
  "statement": "结构化Prompt",
  "narration": "写好Prompt只需要记住一个公式：角色+任务+约束。第一句告诉AI它是谁——'你是一个资深HR'。第二句告诉AI做什么——'帮我写一份市场专员的岗位描述'。第三句告诉AI怎么约束——'要有岗位职责和任职要求，用bullet points格式'。这个'角色-任务-约束'三段式，适用于90%的AI写作场景。",
  "content": {
    "title": "Prompt三段式",
    "steps": [
      {"phase": "execute", "label": "设定角色", "detail": "告诉AI它是谁", "example": "你是一个资深HR"},
      {"phase": "execute", "label": "定义任务", "detail": "告诉AI做什么", "example": "写一份市场专员JD"},
      {"phase": "execute", "label": "添加约束", "detail": "告诉AI怎么做", "example": "含岗位职责+任职要求，bullet格式"}
    ]
  }
}
```

---

## 三、首批3节课的里程碑预估

| 课程 | Scene数 | 预计门控通过率 | 白领版压缩 | 管理层版压缩 |
|------|---------|:---:|:---:|:---:|
| T01 | 5-6 | 95%+ | 70%（~10min） | 40%（~6min） |
| T02 | 4-5 | 95%+ | 70%（~10min） | 40%（~6min） |
| T03 | 5-6 | 90%+ | 70%（~14min） | 40%（~8min） |

---

## 四、与降内存战略验证的协同

降内存战略验证已完成G-01~G-09跨领域通过率100%。培训课程集验证的是**同一管线的规模化生产能力**——从1个素材→N个素材，从1种content_type→5种×3版本×10节课=150个Scene的规模化输出。两者互补：线A证明管线"什么都能做"，线B证明管线"能稳定地做很多"。
