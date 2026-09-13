# 解题策略卡片 v1.0 规范 (P0-A 主线)

**版本**: v1.0
**作者**: 宇兄窗口 (开发助手)
**拍板时间**: 2026-09-13
**配套规范**: `handoff/MATH_001_4step_v1.0_规范.md` (4 步法 v1.0 母题版, 已被市场验证)

---

## 一、定位

### 1.1 4 步法母题 vs 策略卡片 (v1.0 vs v1.0)

| 维度 | 4 步法母题 (v1.0) | 策略卡片 (v1.0, 本规范) |
|------|------------------|----------------------|
| **颗粒度** | 单题级 (1 母题) | 方法论级 (1 策略覆盖 N 道题) |
| **数量** | 56 张 (数学 51 + 历史 5) | 计划 42-56 张 (6 主科) + 20-30 张 (元学习) |
| **重点** | 怎么解这道题 | 怎么用方法解一类题 |
| **学科覆盖** | 数学 + 历史 (5 张) | 语数英史地政 + 书法 (7 学科) |
| **互引** | 引用策略 (4 步法本身就是 1 策略) | 引用母题 (举 1 例) |

### 1.2 与现有 4 步法规范的关系
- **4 步法 v1.0** = 数学的"4 步法"通用方法论 (概念-母题-变形-综合)
- **策略卡片 v1.0** = 跨学科方法论 (数形结合/文言断句/史料解读/...)
- **关系**: 策略卡片是"母题级方法论的上层"——每张策略卡片下挂 5-10 张母题卡片

### 1.3 学科范围 (本项目学生画像)
- 6 主科: 语文 / 数学 / 英语 / 历史 / 地理 / 政治
- 1 艺术科: 书法 (国美校招)
- **排除**: 物理 / 化学 / 生物

---

## 二、卡片结构 (16 字段)

### 2.1 5 核心字段 (两窗口禁区, 改需 issue 讨论)

| 字段 | 类型 | 说明 |
|------|------|------|
| `card_id` | str | 唯一 ID, 格式: `strategy_<学科>_<编号>` 例: `strategy_math_001` |
| `chain_id` | str | 策略族, 格式: `<学科>_strategy_<方法族>` 例: `math_strategy_graphing` |
| `schema_version` | str | "v1.0" |
| `SOP` | str | 标准操作流程 (5 步内), 学生可直接照做 |
| `验收标准` | str | 检验标准, 学生自检用 |

### 2.2 11 扩展字段 (宇兄端可加, 需 PR)

| 字段 | 类型 | 说明 |
|------|------|------|
| `source_type` | str | "教学法" / "学科方法论" / "元学习" / "应试策略" |
| `source_ref` | str | 出处, 自由文本 |
| `original_problem_id` | str | 关联母题 ID (可多个, 逗号分隔) |
| `problem_statement` | str | 典型例题 (简短, 1-2 句) |
| `given_conditions` | str | 适用条件 (题型/题目特征) |
| `figure_description` | str | (可选) 配图描述 |
| `figure_ref` | str | (可选) 配图路径 |
| `figure_type` | str | (可选) 配图类型: "svg" / "image" / "table" |
| `intuition` | str | 直觉理解 (为什么这方法有效) |
| `thinking_path` | str | 思维路径 (5 步以内) |
| `key_insight` | str | 核心洞察 (一句话总结) |

### 2.3 display_target 字段 (v3.0 必填)

| 字段 | 类型 | 说明 |
|------|------|------|
| `display_target` | list | ["RUJING"] (宇兄端默认) 或 ["学习中心"] (雪薇端默认) 或 ["RUJING", "学习中心"] (通用) |

### 2.4 完整卡片示例 (数形结合)

```json
{
  "card_id": "strategy_math_001",
  "chain_id": "math_strategy_graphing",
  "schema_version": "v1.0",
  "SOP": "1. 把代数式画成图 → 2. 标记关键点 (交点/极值/零点) → 3. 从图读答案 → 4. 代数验证",
  "验收标准": "能用数形结合独立解 3 道二次函数题 (含求最值/解集/参数)",

  "source_type": "学科方法论",
  "source_ref": "上海高中数学教材 + 高考 5 年真题总结",
  "original_problem_id": "pp_001, pp_006",
  "problem_statement": "求函数 f(x) = -x² + 2x + 3 在 [-1, 4] 上的最值",
  "given_conditions": "适用: 二次函数/分式/根式/三角函数 等代数式; 题型: 求最值/解集/参数范围/零点个数",
  "figure_description": "二次函数抛物线 + 关键点标注",
  "figure_ref": "D:/4_data/knowledge_cards/数学/4step/figures/pp_001.svg",
  "figure_type": "svg",
  "intuition": "图象是代数的'翻译', 几何直观比代数推导快 5 倍",
  "thinking_path": "1. 画图 (顶点 (-1,4), 零点 (-1, 3)) → 2. 标区间 [-1, 4] → 3. 顶点 y=4, 端点 f(-1)=0, f(4)=-5 → 4. 结论: max=4 (顶点), min=-5 (x=4)",
  "key_insight": "数形结合 = 把抽象代数变直观几何, 解题路径从'算'变'看'",

  "display_target": ["RUJING", "学习中心"]
}
```

---

## 三、chain_id 命名规范

### 3.1 格式
`<学科>_<类型>_<方法族>`

| 学科 | type | 示例 chain_id |
|------|------|---------------|
| 数学 | strategy | math_strategy_graphing, math_strategy_discussion, math_strategy_equation |
| 语文 | strategy | chinese_strategy_poetry, chinese_strategy_classical, chinese_strategy_essay |
| 英语 | strategy | english_strategy_reading, english_strategy_writing, english_strategy_grammar |
| 历史 | strategy | history_strategy_timeline, history_strategy_causality, history_strategy_material |
| 地理 | strategy | geo_strategy_location, geo_strategy_isopleth, geo_strategy_climate |
| 政治 | strategy | politics_strategy_subject, politics_strategy_dialectics, politics_strategy_politics |
| 书法 | strategy | calligraphy_strategy_script, calligraphy_structure, calligraphy_history |
| 元学习 | learning | meta_learning_ebbinghaus, meta_learning_pomodoro, meta_exam_strategy |

### 3.2 数量预估

| 学科 | 策略数 | 估算 |
|------|------|------|
| 数学 | 8-10 | 数形结合/分类讨论/方程思想/函数与方程/化归/特殊值/向量/参数/几何变换/概率 |
| 语文 | 6-8 | 古诗意象/文言断句/议论文/现代文/作文审题/字音字形/病句 |
| 英语 | 6-8 | 阅读主旨/完形填空/写作/语法填空/词义猜测/长难句 |
| 历史 | 6-8 | 时序/因果/史料/比较/阶段/唯物史观/全球史 |
| 地理 | 6-8 | 经纬/等值线/气候/地理过程/区域/人地 |
| 政治 | 6-8 | 主体/矛盾/价值判断/时政/论证/综合探究 |
| 书法 | 4-6 | 五体辨识/临摹/创作/书法史/篆刻/装裱 |
| **合计** | **42-56** | 6 主科 + 1 艺术科 |

---

## 四、产出文件组织

### 4.1 目录

```
D:/4_data/knowledge_cards/
├── 数学/4step/           # 已有 (4 步法数学母题, 51 张)
├── 历史/4step/           # 已有 (4 步法历史母题, 5 张)
├── 策略/                  # 新建 (本规范)
│   ├── 语文/             # chinese_strategy_*.json
│   ├── 数学/             # math_strategy_*.json
│   ├── 英语/             # english_strategy_*.json
│   ├── 历史/             # history_strategy_*.json
│   ├── 地理/             # geo_strategy_*.json
│   ├── 政治/             # politics_strategy_*.json
│   └── 书法/             # calligraphy_strategy_*.json
├── 元学习/                # 新建 (P0-C)
│   └── meta_*.json
└── 4step/
    └── figures/          # 已有 (SVG 配图)
```

### 4.2 文件命名

- 单卡: `<card_id>.json` 例: `strategy_math_001.json`
- 批量: `_strategy_cards_batch_<n>.md` 例: `_strategy_cards_batch_1.md`

---

## 五、工作流

### 5.1 宇兄端 (本规范 v1.0 启动)
1. 写规范 v1.0 (本文档) ✅
2. 写 `tools/strategy_card_validator.py` (类比 `math_4step_validator.py`)
3. 写 5-10 张示范卡 (覆盖 5 学科, 验证规范可行)
4. 跑 validator 通过
5. commit + push

### 5.2 雪薇端 (v1.0 之后)
1. 拉规范
2. 批量生产 30+ 张 (LLM 协助, 人工 review)
3. 推 4 步法母题 → 引用策略卡片 (双向链接)
4. 4 步法 v1.1 模板兼容 (display_target 字段)

### 5.3 双 LLM 协作 (P0-A 启动后)
- **GLM-5**: brainstorming 学科方法论候选
- **glm-4-flash**: 推演 + 验证 (用现有 `tools/glm4_flash_review.py`)
- **人工**: review + 修订

---

## 六、与 4 步法 v1.1 规范的兼容性

### 6.1 共享字段
- 5 核心字段: card_id, chain_id, schema_version, SOP, 验收标准 (两套共用)
- display_target v3.0 (v3.0 规范)

### 6.2 不同字段
- 策略卡片多 `source_type` "学科方法论" / "元学习" 分类
- 4 步法多 `original_problem_id` (数学母题关联具体 4 步法)

### 6.3 互引
- 策略卡片 → 母题: `original_problem_id` (1 策略关联 5-10 母题)
- 母题 → 策略: 引用 chain_id (4 步法母题头部加 "适用策略: math_strategy_graphing")

---

## 七、版本演进

| 版本 | 计划 | 关键变化 |
|------|------|---------|
| v1.0 (本轮) | 启动 + 5 学科示范 | 16 字段结构, 6+1 学科覆盖 |
| v1.1 | 雪薇端批量生产后 | 根据 review 反馈调字段 |
| v2.0 | 知识图谱打通 | 加 `prerequisite_chain_ids` (前驱策略) |
| v3.0 | 跨学科融合 | 加 `cross_subject_links` (例: 文综三科关联) |

---

## 八、风险与权衡

### 8.1 风险
- **学科专业性**: 数学/物理 策略需要专业验证, 我方可能判断不准
- **数量大**: 42-56 张需要持续 1-2 周
- **质量参差**: LLM 生成策略质量不稳定, 需要逐张 review

### 8.2 缓解
- **专业性**: 参考教材 + 5 年高考真题, 雪薇端 review
- **数量**: 批量 + 模板化, 1 张规范 5 张批量
- **质量**: GLM-5 brainstorm → glm-4-flash 推演 → 人工 review 三步法

---

**下一步**: 写 `tools/strategy_card_validator.py` + 5 张示范卡 (语数英史地 各 1 张)
