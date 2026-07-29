# SPDT-KTE 认知模型：六根六尘 × 五蕴 × 脑科学

> **版本**：v1.0 | **日期**：2026-07-16  
> **参考来源**：教学建模文档（0716-教学场景知识传递的建模）+ TextExperience 五蕴认知模型分析  
> **适用**：SPDT-KTE 全体 PT 的内容设计与质量标准

---

## 一、模型总览

SPDT-KTE 的认知模型由三个层次叠加而成：

```
第一层：六根六尘（外部传递）→ 知识从哪里来
第二层：五蕴（内部认知）    → 知识如何内化
第三层：脑科学约束（硬件规格）→ 如何确保高效
```

三个 PT 的职责分工与此完全对应：
- **PT-038** 负责设计"给什么尘"（声尘原料 + 色尘原料）
- **PT-VFX** 负责把"尘"变成可感知的视觉形式（精加工色尘）
- **PT-RUJ** 负责驱动五蕴链路的运行（行蕴激活 + 识蕴落地）

---

## 二、第一层：六根六尘 → PT 功能映射

### 2.1 通道优先级与 PT 对应

| 通道 | 人类感知权重 | PT | 产物 | 管线阶段 |
|---|---|---|---|---|
| **声尘**（听觉） | 主通道（约60%） | PT-038 | 微剧本旁白文本 | P1 |
| **色尘**（视觉） | 辅助通道（约30%） | PT-VFX | Pillow 渲染帧 + MP4 | P2 |
| **行蕴尘**（主动检索） | 转化关键 | PT-RUJ | Flashcard 间隔重复 | P3 |
| 触/身/嗅尘 | 实体场景（暂缺） | — | 标注边界 | — |

### 2.2 声尘 → PT-038 的设计要求

> **核心原则**："听觉是人类感知外部世界的最原初通道，在抽象知识传递中承担主叙事线功能。"

PT-038 的微剧本旁白必须：
1. **叙事驱动**：不是"讲定义"，而是"讲故事"——让历史自己说话
2. **情绪锚点**：每集含至少 1 个认知冲突触发点（"你觉得X，但真相是Y"）
3. **结构清晰**：旁白文本须对应明确的 scene_id，供 PT038_to_VideoFactory 切分
4. **语义对齐**：旁白中的关键概念，必须能在 scene JSON v2 的 `five_skandha.color_base` 中找到对应

### 2.3 色尘 → PT-VFX 的设计要求

> **核心原则**："视觉在抽象知识中不是'直接接收具象刺激'，而是'把抽象关系转化为可结构化/空间化的视觉表征'。"

PT-VFX 的 Pillow 渲染帧必须：
1. **语义对齐**：每个 scene 的视觉帧必须与对应旁白的核心概念语义对齐
2. **降载设计**：视觉帧替工作记忆减负——把线性听觉信息变成空间视觉结构
3. **情绪色调**：根据 `emotion_trigger` 选择视觉基调（solemnity=深墨色，curiosity=蓝调）
4. **五蕴锚点**：`five_skandha.color_base` 必须在帧中高亮显示

---

## 三、第二层：五蕴 → PT-RUJ 的认知链路

### 3.1 五蕴每蕴的认知任务与 PT 覆盖

| 五蕴 | 认知任务 | 覆盖 PT | 触发机制 | 缺口分析 |
|---|---|---|---|---|
| **色蕴** | 感官接收外界信息 | PT-038（旁白）+ PT-VFX（视觉帧） | 被动输入，无需设计 | 语义对齐不足→色蕴接收质量下降 |
| **受蕴** | 即时情绪反应 | PT-038（`emotion_trigger` 字段） | 认知冲突声尘 | 未工程化，SOP v1.2 需写入 |
| **想蕴** | 表象分别 + 意义初判 | PT-038（知识链 chain_id） | 知识结构化呈现 | scene JSON 无 chain_id 关联 |
| **行蕴** | 主动造作的深加工 | **PT-RUJ（Flashcard 间隔重复）** | 强制输出任务 | PT-038 的 `five_skandha.action_prompt` 尚无反馈闭环 |
| **识蕴** | 稳定内化的认知结果 | PT-RUJ（生/熟二态标记） | 间隔重复后固化 | 无"识蕴是否真成"的验证机制 |

### 3.2 行蕴激活的核心机制：Flashcard

> **认知科学依据**（教学建模文档§11）：主动输出（说/写/判）比被动接收激活更广泛的前额叶-海马回路，修正错误认知。

PT-RUJ 的 Flashcard 复习实现的是**强制行蕴激活**：
1. **低门槛输出**：front 是主动检索式问题（"安史之乱爆发于哪一年？"），不是陈述句
2. **即时反馈**：back_core 给出对比或反例（"755年，安禄山、史思明发动"），触发想蕴修正
3. **间隔重复**：基于复习间隔自动安排下次复习时间，强化识蕴

### 3.3 五蕴卡点与干预

| 五蕴卡点 | 表现 | PT-RUJ 干预 | PT-038 改进方向 |
|---|---|---|---|
| 色蕴卡点 | 走神、记不住关键词 | — | 增强声尘语气的节奏感 + 色尘关键词放大 |
| 受蕴卡点 | 厌烦、漠然 | — | PT-038 换更强烈的认知冲突设计 |
| 想蕴卡点 | "好像懂了"但答错 | Flashcard 反馈回指 | PT-038 增加更多对比/反例 |
| 行蕴卡点 | 不愿主动输出 | 降低门槛（填空替代问答） | PT-038 简化 front 语言 |
| 识蕴卡点 | 能背但不会用 | 标记为"卡点节点" | PT-038 增加远迁移练习 |

---

## 四、第三层：脑科学约束 → 管线的硬件规格

### 4.1 工作记忆约束（4±1 组块）

> **依据**：教学建模文档§11引用最新研究，前额叶工作记忆约 4±1 组块（比传统米勒定律 7±2 更严格）

| 应用场景 | 约束 | PT |
|---|---|---|
| 单集旁白 | 核心问题链 ≤ 3 个递进节点 | PT-038 |
| 单张 Flashcard | front 新要点 ≤ 2，answer 逻辑步骤 ≤ 4 | PT-038 |
| 单 scene 视觉帧 | `cognitive_load.points_count` ≤ 4 | PT-VFX |

**校验机制**：scene_quality_gate G06 自动校验，超载报警并建议拆分。

### 4.2 双重编码约束（Paivio）

> **依据**：同时用言语和视觉编码，记忆保持率是单一编码的 2 倍以上。

**管线规则**：
- PT-038 每个核心概念必须同时有旁白（声尘）+ scene JSON 中的 `five_skandha.color_base`（色尘）
- PT-VFX 渲染帧时校验 `semantic_alignment` 字段完整性
- **禁止**：旁白讲 A，视觉帧放无关 B 图

**校验机制**：scene_quality_gate G08 强制核心 scene 包含语义对齐标注。

### 4.3 情绪-记忆约束（杏仁核-海马体）

> **依据**：带情绪（好奇、共鸣、轻微认知冲突）的信息更容易进入长时记忆。

**管线规则**：
- PT-038 每个 episode 的 `dramatic_beats` 必含 `emotion_trigger` 字段
- 色蕴输入后、想蕴启动前，必须有认知冲突触发（"你觉得X，但真相是Y"）
- **禁止**：全程平铺直叙的"定义→例子→练习"无情绪声尘

### 4.4 图式约束（Schema / 皮亚杰）

> **依据**：新知识必须挂到旧图式（长时记忆里的已有结构）上才能被同化/顺应。

**管线规则**：
- 知识链的"核心问题"必须关联学生已有知识（标注具体来源：初中历史/本卷第X集）
- 译篆/句读类知识，唤醒"汉字结构感知"作为旧图式锚点

### 4.5 行蕴闭环约束（前额叶监控）

> **依据**：主动输出 + 即时反馈，触发前额叶-海马体记忆巩固回路。

**管线规则**：
- 每个 episode 必有低门槛输出任务（判断/填空/口述）
- Flashcard 必有反馈声尘（答错回指色尘锚点，答对强化关键词）
- PT-RUJ 记录每次复习的间隔和正确率（IF-D，Phase C）

---

## 五、类比专属通道（Knowledge Type I-IV）

> **依据**：教学建模文档§12-13，类比是学习迁移的核心触发器，但不是所有知识都适合类比。

| 类型 | 特征 | 类比处理 | PT-038 字段 | PT-VFX 渲染 |
|---|---|---|---|---|
| **I型** | 结构清晰 + 日常有同构体 | 主力类比 + 结构映射图 | `knowledge_type: I` + `analogy_block` | analogy_scene 模板 |
| **II型** | 部分清晰 + 含领域假设 | 受限类比 + 差异红框 | `knowledge_type: II` + `analogy_block` + `difference_annotations` | analogy_scene + 差异标注区 |
| **III型** | 纯形式化，无日常同构 | 关闭类比，纯结构推导 | `knowledge_type: III` | steps_scene / causal_chain_scene |
| **IV型** | 具象事实性知识 | 不需要类比 | `knowledge_type: IV` | timeline_scene |

---

## 六、认知模型 × 三 PT 的数据流

```
PT-037 知识库
    ↓
PT-038 episode .py（含 knowledge_type + emotion_trigger + analogy_block + five_skandha）
    ↓ PT038_to_VideoFactory.py
PT-VFX scene JSON v2（含 five_skandha + analogy_block + semantic_alignment + cognitive_load）
    ↓ scene_renderer_pillow.py → TTS → ffmpeg
PT-VFX video_package（含 metadata.json + MP4 + scene_timeline）
    ↓
PT-RUJ ChainReaderPage（链阅读 → 色蕴接收）
         ↓
    PT-RUJ Flashcard 复习 → 行蕴激活（前额叶-海马回路）
         ↓
    PT-RUJ 生/熟标记 → 识蕴落地
         ↓ IF-D (Phase C)
    PT-RUJ 学习日志 → PT-038 五蕴卡点分析 → 优化 episode .py
```

---

## 七、参考文档

| 文档 | 路径 |
|---|---|
| 教学建模文档 | `C:\Users\willi\Desktop\我的视野\_自动化内容设计\0716-教学场景知识传递的建模\0716-教学场景知识传递的建模_titled.md` |
| TextExperience 五蕴分析 | `PT-038/docs/TextExperience_五蕴认知模型分析.md` |
| 三项目协同方案 | `PT-038/docs/三项目协同方案_代码层审计与补全路线图.md` |
| 接口协议 IF-A | `SPDT-KTE/interface_protocols/scene_json_v2_schema.json` |
| 接口协议 IF-B | `SPDT-KTE/interface_protocols/video_package_metadata.json` |
| 接口协议 IF-C | `SPDT-KTE/interface_protocols/card_package_schema.json` |
