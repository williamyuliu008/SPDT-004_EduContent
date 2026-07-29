# 阶段B启动 + OMAS组织演进路线

> 日期：2026-07-03 | 项目：cgm_training_factory
> 范围：阶段B工作计划 + 项目作为OMAS演进试验场的路线设计

---

## 一、阶段B工作计划（优先级排序，预计5-7天）

### B-P0：步骤完整性模板（0.5天，依赖：阶段A M6未达标）

阶段A发现唯一未达标项：人工修改率33%（步骤从3步扩为4步）。根因是培训场景的步骤需要覆盖"准备→执行→验证→调整"四个阶段。

**任务**：在steps content_type的Schema中增加`step_phases`字段：

```json
"steps": [
  {"phase": "准备", "label": "设定身份", "detail": "告诉AI你是谁+场景"},
  {"phase": "执行", "label": "给出需求", "detail": "邮件目的+收件人"},
  {"phase": "执行", "label": "提供信息", "detail": "关键要点+行动项"},
  {"phase": "验证", "label": "检查调整", "detail": "语气+完整性+遗漏"}
]
```

同步更新S1审计条件：从"每步可执行"增强为"步骤覆盖准备/执行/验证三个阶段"。

### B-P1：LLM填参自动化（1天，依赖：T-01~T-04 Prompt就绪）

阶段A已验证LLM填参的12倍速度优势和3种系统性失败模式。任务：

1. **搭建T-01→T-02→T-03→T-04自动化Prompt链路**（复用AI_video_edu的adapters/llm_connector.py）
2. **注入阶段A识别的3种修复**：
   - 术语库注入到T-01 Prompt（修复C1失败）
   - "口语化"few-shot示例注入T-03（修复C7失败）
   - "条件句式"模板注入T-04（修复R7失败）
3. **跑通LLM全自动生成→Gate校验→人工抽检的完整链路**
4. **目标**：LLM版本L2审计通过率从~85%提升到>90%

### B-P2：进化选择自动化（1天，依赖：B-P1）

阶段A的首循环是手工操作的（人工vs LLM各3个→手工排名）。任务：

1. **搭建自动化进化循环脚本**：对同一培训素材生成3变体→L1+L2审计→fitness排名→elite标记→失败模式汇总
2. **每日自动运行**：对新素材跑一轮进化选择，积累fitness数据
3. **elite作为few-shot注入**：每轮优胜版本自动加入Prompt的few-shot示例库

### B-P3：content_type扩展到5种（1天）

新增两种类型，达到7±2目标区间：

| 新content_type | 培训场景 | graphic_type映射 | 审计条件 |
|---------------|---------|-----------------|---------|
| `case_study` | 项目实战案例 | causal_chain + term_card | 案例完整性/真实性/可复用性（6条） |
| `tool_demo` | 工具操作演示 | box_diagram（代码编辑器风格） | 步骤可复现/界面匹配/异常处理（7条） |

### B-P4：多版本编译（1.5天，依赖：B-P1）

基于T-05 Prompt模板，对同一培训模块生成3个编译版本：

| 版本 | 时长压缩 | 语言风格 | 步骤粒度 |
|------|---------|---------|---------|
| 应届生版 | 100%基准 | 亲切引导 | 完整细化 |
| 在职白领版 | 60-70% | 专业干货 | 核心步骤 |
| 管理层版 | 30-40% | 战略简明 | 仅框架 |

### B-P5：L3学员测试（可选，3天，需学员资源）

若有条件：选T01-T03课程做小规模测试→理解度评分→审计数据闭环→反馈到Prompt/Schema优化。

---

## 二、训练工厂 → OMAS组织演进映射

OMAS文档揭示的四个结构性断层，恰好可以在训练工厂项目中逐一验证和修复：

### 2.1 已经验证的

| OMAS机制 | 训练工厂对应实现 | 验证状态 |
|----------|---------------|---------|
| Gate Agent L1-L3 | G-01~G-09 + C/S/R 22条审计条件 | ✅ 阶段A已验证97.9% |
| Gap Evaluator | 进化首循环识别LLM的3种失败模式→Prompt修复 | ✅ 阶段A首循环已运行 |
| Knowledge Cell | content_type定义 + 审计条件 + Prompt模板 | ✅ Day 2-3产出已入库 |

### 2.2 阶段B可引入的OMAS修复项

| OMAS修复项 | 训练工厂对应任务 | 预计工时 | 优先级 |
|-----------|---------------|---------|--------|
| **Gate L4属性审计** | 为3种content_type各定义1-2个不变量（如"concept的statement+tags信息不重复"、"steps的步骤间必有箭头方向"）→Python硬规则检查 | 0.5天 | B-P0同步 |
| **进化选择MVP** | B-P2的任务直接就是Evolution Cell的最小版——Gate排名→elite保留→失败反馈 | 1天 | B-P2 |
| **Elicitation辅助** | 在T-01 Prompt中注入"培训需求结构化诱导"——不是让人写完整需求，而是让LLM出多选题 | 0.5天 | B-P1同步 |
| **域知识库构建流程** | 审计条件库 + Prompt few-shot库 + 失败模式库的版本化管理 | 1天 | B-P3同步 |
| **运行时审计Dashboard** | 进化选择循环的fitness趋势图（每轮通过率变化曲线） | 0.5天 | B-P2同步 |

### 2.3 阶段B暂不引入（留给后续项目）

| OMAS修复项 | 为什么暂缓 |
|-----------|----------|
| 分布漂移检测 | 训练工厂是"批处理"模式，在线漂移问题不突出 |
| 人机交接协议 | 培训场景的人工审核是最后一步，交接模式简单 |
| 经济ROI模型 | 需要积累更多成本数据才能建模 |

---

## 三、从"项目"到"Guild"的组织演进路径

训练工厂项目当前的"项目"形态，可以按以下路径逐步进化为OMAS中的一个**PL-Guild（产品线Guild）**：

<div class="rich-timeline">

<div class="rich-step">
<span class="rich-step-marker">1</span>
<div class="rich-step-body">
<div class="rich-step-title">阶段B完成时 · 项目 → 原型Guild</div>
<div class="rich-step-text">B-P0~P5全部完成后，训练工厂具备：LLM自动填参能力 + 进化选择循环 + 5种content_type + 多版本编译。这已经是一个"可自运行的培训内容生产系统"。</div>
</div>
</div>

<div class="rich-step">
<span class="rich-step-marker">2</span>
<div class="rich-step-body">
<div class="rich-step-title">阶段B+1 · 原型Guild → 正式Guild</div>
<div class="rich-step-text">注册为OMAS的PL-Training-Guild：接入Event Bus（接收培训需求SR）、挂接Gate Agent（接收全平台审计）、对接SupplyChain Cell（TTS/LLM/渲染能力计费）。</div>
</div>
</div>

<div class="rich-step">
<span class="rich-step-marker">3</span>
<div class="rich-step-body">
<div class="rich-step-title">阶段B+2 · 单一Guild → 多Guild模板</div>
<div class="rich-step-text">训练工厂的content_type定义+审计条件+Prompt模板的"三件套"模式，可以作为新Guild的启动模板。一个新的内容领域（如法律文书、金融报告）只需要替换三件套，不需要重建管线。</div>
</div>
</div>

<div class="rich-step">
<span class="rich-step-marker">4</span>
<div class="rich-step-body">
<div class="rich-step-title">阶段B+3 · 多Guild → Evolution Cell跨Guild共享</div>
<div class="rich-step-text">训练工厂验证过的进化选择机制（L1-L4审计→fitness排名→elite保留→失败反馈）作为Evolution Cell的参考实现，供所有Guild使用。</div>
</div>
</div>

</div>

---

## 四、阶段B的两条并行工作流

训练工厂进入阶段B后，同时推进两条线：

| 工作流 | 负责人/角色 | 任务 | 产出 |
|--------|-----------|------|------|
| **产品线** | 训练内容生产 | B-P0~P5，按优先级逐个推进 | 可运行的培训内容自动生产线 |
| **组织线** | OMAS修复验证 | 在项目中植入5个OMAS修复项 | 每个修复项在训练工厂中的验证报告 |

**两条线的协同**：组织线的每一项修复（L4审计/进化选择/Elicitation/知识库/审计Dashboard）都直接提升产品线的能力。不是两条平行线——是同一个项目的两个视角。

---

## 五、下一步的具体行动项

| 优先级 | 行动 | 项目线 | 组织线 |
|--------|------|--------|--------|
| 本周 | B-P0 步骤完整性模板（0.5天） | ✅ 产品 | — |
| 本周 | Gate L4原型（0.5天，与B-P0并行） | ✅ 产品 | ✅ L4审计验证 |
| 本周 | B-P1 LLM填参自动化（1天） | ✅ 产品 | ✅ Elicitation验证 |
| 本周 | B-P2 进化选择自动化（1天） | ✅ 产品 | ✅ Evolution Cell验证 |
| 下周 | B-P3 content_type扩展（1天） | ✅ 产品 | ✅ 知识库流程验证 |
| 下周 | B-P4 多版本编译（1.5天） | ✅ 产品 | — |
| 下周 | B-P5 L3学员测试（可选） | ✅ 产品 | — |
