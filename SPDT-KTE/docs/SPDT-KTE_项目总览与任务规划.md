# SPDT-KTE · 项目总览与任务规划

> **版本**：v1.0 | **日期**：2026-07-16  
> **定位**：SPDT-KTE 根目录核心文档——项目本质、当前状态、任务规划的自述文件  
> **建议**：首次接手 SPDT-KTE 的 Agent 或人工，先读本文件

---

## 一、项目本质：它是什么

**SPDT-KTE 不是"一个内容工具"，而是"一套认知工程的生产线"。**

它的底层逻辑来自一个核心问题：**为什么学生听课觉得懂，关掉视频就忘？为什么刷了很多题，遇到新题还是不会？为什么用 App 背单词，单词记住了但不会用？**

这三个问题都指向同一个根本：**知识的传递没有遵循人脑的认知规律。**

六根六尘模型揭示了"知识从教师到学生"的外部通道：声尘（听觉主通道）传递主叙事线，色尘（视觉辅助）提供结构锚点。但这只是外层。五蕴模型揭示了内层：光有外部输入不够——没有行蕴的主动加工（Flashcard 强制检索），知识永远停在"想蕴的表层模糊"，成不了"识蕴的稳定内化"。

**SPDT-KTE 的本质，是把这两个模型工程化——让内容从设计的第一刻起，就内置认知规律，不是事后补救。**

---

## 二、为什么这条管线有竞争力

市面上不缺内容工具：剪映可以生成视频，Quizlet 可以做卡片，Obsidian 可以做知识图谱。但它们都是**单点工具**，没有任何一个在设计时就内置了"这段内容应该用声尘还是色尘"、"这个知识点属不属于 I 型（可以用类比）"、"这张卡片的 front 会不会超载工作记忆"这类认知约束。

**SPDT-KTE 的护城河，是把"认知规律"从人的经验变成管线的规则。**

| 维度 | 普通内容工具 | SPDT-KTE |
|---|---|---|
| 设计依据 | 设计师的个人经验 | 六根六尘 + 五蕴 + 脑科学 |
| 类比处理 | 随意打比方，不校验 | Type I-IV 分类 + 差异标注 + 闭环回扣 |
| 认知负荷 | 不控制 | 工作记忆 4±1，自动校验 |
| 双重编码 | 有图有声音就算 | 声尘-色尘语义对齐强制校验 |
| 知识链 | 孤立知识点 | chain_id + 核心问题 + 当代回响，结构化 |
| 多格式一致性 | 视频和卡片毫无关联 | 同一知识源 → 音频 + 卡片 + 视频，格式不同但认知链路统一 |
| 反馈闭环 | 无 | Phase C：学习行为日志 → 五蕴卡点分析 → 内容优化 |

---

## 三、三 PT 的现状与定位

### PT-038 · 内容工厂（跑通了，但需要升级）

**已跑通**：
- SOP v1.1，13 章节，Phase 0-6 全链路
- 4 卷古代史 + 世界史，共 31 集，440 张卡片，5 本电子书
- card_generator.py、ebook_generator.py、broadcast_audio.py 全套管线
- CGM Audit A/B/C 质量管理体系
- 五蕴认知模型文档 + 战略定位文档

**当前短板**：
- episode .py 无 `knowledge_type`（I/II/III/IV）字段 → 类比专属通道无法激活
- episode .py 无 `emotion_trigger` 字段 → 受蕴情绪触发未工程化
- episode .py 无 `five_skandha` 字段 → 五蕴链路无显式数据
- SOP 停留在 v1.1 → 脑科学约束（5条规则）未写入
- 声尘无精细化标注（语气/停顿/节奏）→ 影响受蕴触发质量
- 电子书尚未从 v2 episode 数据重新生成

**自我评分**：6.5 / 10

### PT-VFX · 视觉渲染引擎（工具就绪，但未接入 PT-038）

**已跑通**：
- scene_renderer_pillow.py，10 种 Pillow 场景模板
- TTS 音频合成（Azure / MiniMax / Coqui）
- ffmpeg 视频合成，assemble_v2.py 全自动拼接
- scene_quality_gate.py，5 个 Gate（G01-G05）
- PT038_to_VideoFactory.py 转换器（v1，有 v2 升级基础）

**当前短板**：
- 尚未处理过 PT-038 的真实 episode .py 数据
- 转换器输出 scene JSON v1，无五蕴/类比字段
- 无 scene JSON v2 schema 校验
- 无 G06（认知负荷）/ G07（五蕴完整性）/ G08（双重编码对齐）
- 尚未生成过 PT-038 内容的真实视频

**自我评分**：6 / 10

### PT-RUJ · 入境 App（音频就绪，视频待接入）

**已跑通**：
- HarmonyOS NEXT 完整 App，ArkUI + ArkTS
- 音频播放（MediaService.playAudio）完全就绪
- ChainReaderPage 链阅读器 UI 完整
- Flashcard 复习（间隔重复）核心逻辑完成
- ImportService 支持 v1/v2/v3 card_package JSON
- 生/熟二态标记，叙事文本缓存

**当前短板**：
- VideoPlayerInterface 为空桩 → 视频播放未实现
- ImportService 无 video_package 导入逻辑
- audio_meta.json 硬编码在 resources，无法热更新
- IF-D learning_feedback 尚未设计

**自我评分**：5 / 10（音频部分 7/10，视频部分 2/10）

---

## 四、任务规划

### 紧急（P0）：打通数据流（让管线真正跑起来）

> **目标**：让 PT-038 → PT-VFX → PT-RUJ 的数据流实际跑通，不再是"理论上可以连"

| 任务 | PT | 工作量 | 阻塞关系 |
|---|---|---|---|
| PT-038 episode .py 增加 v2 字段（6个已有 episode + 新写） | PT-038 | 3小时 | 阻塞转换器升级 |
| PT038_to_VideoFactory.py 升级（透传 v2 字段 + 校验 analogy_block） | PT-VFX | 2小时 | 阻塞 scene JSON v2 生成 |
| PT-VFX series_builder.py 增加 video_package metadata 生成 | PT-VFX | 2小时 | 阻塞 rujing 接入 |
| rujing MediaService 实现 playVideo() | PT-RUJ | 1小时 | 阻塞视频播放 |
| rujing ImportService 增加 video_package 导入逻辑 | PT-RUJ | 2小时 | 阻塞视频数据加载 |
| rujing ChainReaderPage 增加视频入口 UI | PT-RUJ | 1小时 | 阻塞用户体验 |
| **端到端验证**：墨骨山河 Ep01 从 episode .py 到 rujing 视频播放全链路 | 全 | 半天 | — |

**里程碑目标**：用户能在 rujing App 里播放"乾元元年·蒲州的墨与血"的视频，绑定的 Flashcard 同时出现在复习队列。

---

### 重要（P1）：认知机制嵌入（让管线开始"懂认知"）

> **目标**：把六根六尘/五蕴/脑科学从文档变成代码约束

| 任务 | PT | 工作量 | 依赖 |
|---|---|---|---|
| PT-038 SOP v1.2：增加 §14 脑科学约束 + §15 类比通道 + §16 声尘精细化 + §17 v2 字段规范 | PT-038 | 4小时 | P0 完成 |
| PT-038 card_generator.py：单卡 front ≤ 2 要点、answer ≤ 4 步，校验并自动拆分 | PT-038 | 2小时 | P0 完成 |
| PT-038 audio_generator.py：旁白文本增加语气标注字段（Tone enum 扩展） | PT-038 | 2小时 | P0 完成 |
| PT-VFX scene_quality_gate.py：增加 G06（认知负荷）+ G07（五蕴完整性）+ G08（双重编码对齐） | PT-VFX | 2小时 | P0 完成 |
| PT-VFX scene_renderer_pillow.py：新增 analogy_scene 模板（G） | PT-VFX | 3小时 | P0 完成 |
| PT-VFX 渲染器：读取 `emotion_trigger` → 动态选择视觉色调 | PT-VFX | 2小时 | P0 完成 |
| PT-RUJ ChainReaderPage：基于 scene_timeline 实现"跳转至 scene"功能 | PT-RUJ | 2小时 | P0 完成 |
| PT-RUJ Flashcard：显示关联 scene 的 `five_skandha.action_prompt` | PT-RUJ | 2小时 | P0 完成 |

**里程碑目标**：scene JSON v2 全字段通过 G06-G08 Gate；analogy_scene 模板渲染"刀锋入纸"scene；rujing 看完视频后，Flashcard 复习队列自动出现该集相关卡片。

---

### 中期（P2）：反馈闭环 + 内容扩展（让管线有"自我优化"能力）

| 任务 | PT | 工作量 | 依赖 |
|---|---|---|---|
| PT-RUJ DatabaseService：记录每张卡片的复习间隔、正确率、识蕴落成时间 | PT-RUJ | 3小时 | P0 完成 |
| PT-RUJ IF-D：输出 learning_feedback JSON（日志文件） | PT-RUJ | 2小时 | 上行 |
| PT-038：接收 IF-D，分析五蕴卡点（高频错知识节点） | PT-038 | 高（设计工作） | 上行 + P0 完成 |
| PT-038：针对卡点自动生成"补强 scene"（额外类比 + 强化行蕴） | PT-038 | 高 | 上行 |
| PT-038 新学科包：PT-038-F（译篆/句读专项）基于 cafa_calligraphy_2026 | PT-038 | 中 | SOP v1.2 完成 |
| PT-VFX：scene_renderer_pillow.py 增加 quote_highlight 动效模板（H） | PT-VFX | 3小时 | P1 完成 |
| PT-RUJ：音频热更新（audio_meta 迁移到 DB，不再硬编码 resources） | PT-RUJ | 2小时 | P0 完成 |

**里程碑目标**：PT-RUJ 的学习行为日志每周汇总一次，自动识别高频错知识点，回传给 PT-038 优化内容。

---

### 长期（P3）：平台化 + 规模化（让管线成为基础设施）

| 任务 | 说明 |
|---|---|
| **SPDT-KTE 接口协议服务化** | 把 IF-A/B/C schema 校验从文件级变成 API 服务，任何 PT 提交 scene JSON 时自动校验 |
| **PT-038 → 新学科包** | SOP v1.2 跑通后，新增一个学科包 = 写 meta.json + episode .py → 跑管线，时间压缩到 1 天 |
| **PT-VFX 多风格渲染** | 增加"水墨风""现代极简""手绘风"三套 Pillow 主题，同一内容可输出不同视觉风格 |
| **PT-RUJ 多端交付** | 将 delivery 层扩展到不止 rujing——Android/iOS/Web 可复用同一数据协议 |
| **认知诊断报告** | PT-RUJ 的学习行为日志 → 每月生成"认知诊断报告"：五蕴哪一蕴是瓶颈、建议优先补强哪些知识节点 |

---

## 五、质量评估标准

### 当前整体评分：5.5 / 10

| 维度 | 评分 | 说明 |
|---|---|---|
| 认知模型嵌入 | 4/10 | 五蕴/脑科学仅在文档中，未进代码约束 |
| 数据流连通 | 4/10 | PT-038 产出丰富，PT-VFX/PT-RUJ 尚未消费 |
| 多格式一致性 | 7/10 | PT-038 内部一致，跨 PT 尚未验证 |
| 质量门覆盖 | 5/10 | PT-038 CGM 较完整，PT-VFX G06-G08 缺失 |
| 反馈闭环 | 2/10 | IF-D 未实现，零反馈数据 |
| 端到端可演示 | 2/10 | 无完整跑通案例，墨骨山河 Ep01 待验证 |

---

## 六、为什么值得持续投入

这条管线面对的核心问题是：**真正懂认知科学的内容生产，和不懂认知科学的内容生产，成本应该差多少？**

如果不用六根六尘、不做五蕴链路、不控工作记忆——省下的设计成本，迟早会变成学生的认知负担。学习这件事是最诚实的：知识没有内化，就是没有内化，不会因为包装好看就自动变懂。

**SPDT-KTE 的赌注是：把认知规律系统性地嵌入管线，让"符合认知的设计"变成默认选项而非额外选项。** 一旦这条管线跑通，新增一个学科的知识传递产品，生产成本趋近于零，但认知质量不会随规模下降。

这才是这条管线的终局价值。
