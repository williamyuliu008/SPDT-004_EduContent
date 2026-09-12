# SPDT-004 双窗口协作说明 v1.0

> **文档名**：SPDT-004 双窗口协作说明 v1.0
> **接收方**：雪薇窗口的 AI 助手（学生侧）
> **发送方**：宇兄窗口的 AI 助手（开发侧）
> **作者**：宇兄窗口（刘宇的开发窗口 AI 助手）
> **时间戳**：2026-09-12（北京时间）
> **性质**：基线版本（baseline），后续变更累积在此版本之上
> **配套**：无单文件提示词，本文件即唯一协作说明

---

## 一、身份与代号

### 1.1 两个窗口

| 维度 | 宇兄窗口 | 雪薇窗口 |
|:---|:---|:---|
| **真人** | 刘宇（开发者） | 雪薇（学生） |
| **角色** | 开发者助手 | 学生助手 |
| **工作目录** | `D:\2_products\education\SPDT-004_EduContent` | `D:\Z_学习平台\knowledge-cards-prod` |
| **长期定位** | 教育资源挖掘和管理平台（不限高考） | 学生学习（高考专精） |
| **主要产出** | RUJING APP + 7 PDT 产品线 + 多媒体探索 | 学习中心.html（高考专精） |
| **数据范围** | 通用教育 | 高考 6 学科（语数英政史地） |

### 1.2 命名规整（重要）

- ✅ **正式名**：宇兄窗口 / 雪薇窗口
- ❌ **不再使用**："autoclaw"（旧代号，已废弃）、"mavis"（agent name，不作为角色名）
- ✅ **AI 助手** 统称"窗口的 AI 助手"，不另起名
- ✅ **真人** 称"宇兄" / "雪薇"（或"刘宇" / "雪薇"）

---

## 二、工作目录与仓结构

### 2.1 宇兄窗口（本机）

```
D:\2_products\education\SPDT-004_EduContent\
├── 1_ingest/                  # 数据采集（v1.0 规范+autoclaw_kit）
├── 2_structure/               # 结构化工具
├── 3_render/                  # 渲染管线
├── 4_adapt/                   # 自适应
├── 5_deliver/                 # 交付
├── common/                     # 公共工具
├── docs/                       # 文档
├── handoff/                    # handoff 沉淀
├── products/                   # 产品内容
│   ├── courses/               # 课程内容
│   └── math_4step_mvp/        # 4 步法数学 MVP（Flask）
├── prompts/                    # prompt 模板
├── quality/                    # 质量工具
├── review_inbox/               # 审核 inbox
├── templates/                  # 模板
├── tools/                      # 工具脚本
│   ├── math_4step_validator.py
│   ├── glm5_check.py
│   ├── draw_pp_figures.py
│   └── upgrade_pps_v11.py
└── AGENTS.md / WINDOWS.md / SPDT.yaml
```

### 2.2 雪薇窗口（你的环境）

```
D:\Z_学习平台\knowledge-cards-prod\
├── projects/                   # 6 学科高考题库
│   ├── math/                  # 145 张真题
│   ├── gaokao-history/        # 1602 题 + 60 专题
│   ├── gaokao-geography/      # 2178 题 + 49 专题
│   ├── gaokao-politics/       # 1482 题 + 60 专题
│   ├── gaokao-chinese/        # 语文（待补）
│   └── gaokao-foreign/        # 外语（待补）
├── apps/learning-hub-v2/      # 学习中心（高考专精 + v3 集成）
├── docs/                        # 文档
└── tools/                       # 题库统计/校验
```

### 2.3 共同仓（共享规范 + 工具）

**GitHub**：`https://github.com/williamyuliu008/SPDT-004_EduContent`
- 两端都有本地仓，PR 模式同步
- 共同规范/工具/课程内容都进此仓

### 2.4 卡片数据 mirror 仓

**GitHub**：`https://github.com/williamyuliu008/spdt-content-cards`
- 4 学科 172 套 K 卡 JSON
- 雪薇窗口推送，宇兄窗口按需 pull

---

## 三、双窗口角色与分工

### 3.1 雪薇窗口（学生助手）—— 主导方

**职责**：
- ✅ 学习中心.html 的展示和优化（高考专精 + 学生需要）
- ✅ 决定哪些内容进 `display_target: ["学习中心"]`
- ✅ 拉共同仓最新 + 渲染学习中心
- ✅ 高考 6 学科题库维护（数学/语文/英语/历史/地理/政治）
- ✅ v1.0/v1.1 规范制定（4 步法概念-母题-变形-综合）
- ✅ 4 步法 v1.1 母题 v1.1 模板（11 扩展字段）

**不做**：
- ❌ 替宇兄窗口做 RUJING APP 客户端开发
- ❌ 替宇兄窗口做 7 PDT 产品线决策
- ❌ 替宇兄窗口决定 `display_target: ["RUJING"]` 的内容

### 3.2 宇兄窗口（开发助手）—— 试验田 + RUJING 主力

**职责**：
- ✅ RUJING APP 客户端开发（鸿蒙 Next 端）
- ✅ 7 PDT 产品线开发（PT-030 高考 / PT-031 通识 / PT-032 高校课件 / PT-033 企业培训 / PT-CAFAS 国美书法 / 等）
- ✅ 通用教育内容挖掘（不限高考）
- ✅ 多媒体形式探索（Manim 动画 + TTS 配音 + 视频合成 + PDF）
- ✅ 古史 v1-v4 微剧本 + 墨骨山河 ep09+ 续作
- ✅ 共同规范迭代（v1.0 → v1.1 → display_target 字段，**提 PR + 标"规范"标签**）
- ✅ 给 4 步法 v1.1 母题做 enhancement（enrichment/图/例）
- ✅ 决定 `display_target: ["RUJING"]` 内容

**不做**：
- ❌ 替雪薇窗口决定哪些进学习中心.html
- ❌ 改 v1.0 5 核心字段（chain_id / card_id / schema_version / SOP / 验收标准）
- ❌ 直接 push 到共同仓 main 分支（走 PR）
- ❌ 替雪薇窗口修改 `apps/learning-hub-v2/`

### 3.3 共同仓归属

| 内容 | 进哪个仓 | 谁主导 |
|:---|:---|:---|
| v1.0 规范 + autoclaw_kit 21 文件 | 共同仓 | 雪薇拍板，宇兄 PR |
| v1.1 4 步法 11 扩展字段 | 共同仓 | 雪薇拍板，宇兄 PR |
| v3.0 display_target 字段 | 共同仓 | 雪薇拍板，宇兄 PR |
| 4 步法数学 v1.1 母题（15 张） | 共同仓 | 雪薇产，宇兄 PR enhancement |
| 6 学科高考题库 | 雪薇专精仓 `knowledge-cards-prod` | 雪薇产 |
| RUJING APP 客户端 | 宇兄端仓 | 宇兄产 |
| 7 PDT 课程内容 | 共同仓 `products/courses/` | 宇兄主，雪薇按需 |
| 学习中心.html 渲染 | 雪薇专精仓 `apps/learning-hub-v2/` | 雪薇 |

---

## 四、共同规范（v1.0 + v1.1 + v3.0）

### 4.1 v1.0 5 核心字段（两窗口禁区）

1. `card_id`（唯一标识）
2. `chain_id`（v1.2 chain 关联）
3. `schema_version`（版本号）
4. SOP（产卡流程）
5. 验收标准（质量门禁）

**修改规则**：两窗口都不能改，要改先 issue 讨论 + 雪薇拍板

### 4.2 v1.1 11 扩展字段（4 步法，宇兄可加，需 PR）

1. `source_type`（"真题改造"/"原创"）
2. `source_ref`（来源，如"2018 上海高考 Q1"）
3. `original_problem_id`（原题 ID）
4. `problem_statement`（题目原文）
5. `given_conditions`（结构化已知条件）
6. `figure_description`（图形描述）
7. `figure_ref`（图形引用路径）
8. `figure_type`（"svg"/"png"/"none"）
9. `intuition`（题目背景）
10. `thinking_path`（思路引导）
11. `key_insight`（核心洞察）

**兼容期**：v1.1 母题可暂不带 `concepts_used` 和 `variant_ids`（空数组）

### 4.3 v3.0 display_target 字段（新必填）

```json
{
  "card_id": "...",
  "type": "...",
  "display_target": ["学习中心", "RUJING"],
  ...
}
```

**取值说明**：

| 值 | 含义 | 决定权 |
|:---|:---|:---|
| `"学习中心"` | 进雪薇专精仓 `apps/learning-hub-v2/` | 雪薇拍板 |
| `"RUJING"` | 进宇兄端 RUJING APP | 宇兄拍板 |
| `["学习中心", "RUJING"]` | 双展示（通用内容） | 共同决定 |
| `[]` | 仅入共同仓，不展示 | 内部资产 |

**默认值差异**（两窗口拍板）：

| 窗口 | 默认值 | 理由 |
|:---|:---|:---|
| **雪薇端** 产出 | `["学习中心"]` | 学生助手默认进学习中心 |
| **宇兄端** 产出 | `["RUJING"]` | 开发者助手默认进 RUJING |
| 共同仓通用内容 | `["学习中心", "RUJING"]` | 双展示 |

**v1.0/v1.1 时代产出**（历史内容）：默认 `["学习中心", "RUJING"]`（向后兼容），需要时再调整。

---

## 五、4 步法通用基底（拍板）

**v1.1 4 步法**（概念-母题-变形-综合）是**通用教育资源基底**，**两窗口都承担**：

- **雪薇窗口**：4 步法数学 v1.1（已产 15 母题 + 5 历史母题 = 56 张 PASS）
- **宇兄窗口**：4 步法作为"通用教育"基底，**不限学科**：
  - PT-030 高考 = 4 步法数学续做（函数/数列/解析几何）
  - PT-031 通识 = 4 步法通识（如物理/化学/生物）
  - PT-033 企业培训 = 4 步法专业技能

**PT-030 = 4 步法数学**（重叠）：

| 学科子板块 | 雪薇已做 | 宇兄续做 |
|:---|:---|:---|
| 立体几何 | ✅ 15 母题（PP_001-015） | 给 enhancement |
| 函数 | ⏳ 待启 | ✅ 起草 10 母题（PP_016-025） |
| 数列 | ⏳ 待启 | ✅ 起草 10 母题（PP_026-035） |
| 解析几何 | ⏳ 待启 | ✅ 起草 10 母题（PP_036-045） |
| 概率统计 | ⏳ 待启 | 后期 |

---

## 六、Git PR 协作流程

### 6.1 雪薇窗口 → 共同仓

1. 雪薇端：写 issue 到共同仓（标"学习中心"或"规范"标签）
2. 雪薇端：改完 commit + push 分支
3. 雪薇端：提 PR
4. 宇兄端：24 小时内 review
5. 合并：宇兄 review 通过 → 雪薇合并 → 推远端

### 6.2 宇兄窗口 → 共同仓

1. 宇兄端：写 issue + 标"刘宇机器"标签
2. 宇兄端：改完 commit + push 分支
3. 宇兄端：提 PR
4. 雪薇端：24 小时内 review
5. 合并：雪薇 review 通过 → 宇兄合并 → 推远端

### 6.3 跨窗口数据交换

- **4 步法数学 v1.1**（雪薇产，已完成）→ 共同仓 `products/courses/数学/4step/`
- **PT-030 函数/数列/解析几何**（宇兄产）→ 共同仓 `products/courses/数学/4step/`
- **RUJING 通用内容**（宇兄产）→ 共同仓 `products/courses/通用/`
- **高考题库**（雪薇产）→ 雪薇专精仓 `knowledge-cards-prod`

### 6.4 PR 描述模板

```markdown
## 目的
<这次改什么、为什么>

## 改动
- 改了哪些文件
- 加了什么 / 删了什么

## 测试
- 跑了哪个 validator
- 校验结果：PASS / FAIL

## 关联
- 关联到哪个 doc / 哪个母题 / 哪个 chain

Reported-by: 宇兄窗口（或 雪薇窗口）
```

### 6.5 分支命名

```
feat/<short-name>          # 新功能
fix/<short-name>           # bug 修复
docs/<short-name>          # 文档
chore/<short-name>         # 杂项
refactor/<short-name>      # 重构
poc/<short-name>           # 概念验证
```

---

## 七、display_target 字段分流（示例）

### 7.1 雪薇端产出（学生学习为主）

```json
{
  "card_id": "math_4step_2026_pp_001_正方体_中位线_线面平行",
  "type": "parent_problem",
  "display_target": ["学习中心"],
  "chain_id": "math/M-V3-01-线面平行",
  ...
}
```

### 7.2 宇兄端产出（RUJING + 通用教育为主）

```json
{
  "card_id": "rujing_2026_pp_016_二次函数_区间最值",
  "type": "parent_problem",
  "display_target": ["RUJING"],
  "chain_id": "math/M-V4-01-函数",
  ...
}
```

### 7.3 共同仓通用内容（双展示）

```json
{
  "card_id": "spdt_2026_4step_v1_1_spec",
  "type": "specification",
  "display_target": ["学习中心", "RUJING"],
  ...
}
```

---

## 八、紧急情况

### 8.1 紧急 bug 修复

- 紧急 bug → 飞书/微信直接喊
- **事后必须补 PR 留痕**（即使 hotfix 也要走 PR）

### 8.2 规范分歧

- 雪薇端有最终拍板权（v1.0/v1.1/v3.0 规范相关）
- 宇兄端提 issue 标"规范"标签
- 雪薇 24 小时内回应

### 8.3 工具 bug

- 哪端复现哪端提 PR fix
- 另一端 review

### 8.4 数据冲突

- `git pull --rebase` + 手动 reconcile
- 重要冲突雪薇拍板

---

## 九、长期定位差异

### 9.1 雪薇窗口

- **场景**：学生学习
- **专精**：高考 6 学科（语数英政史地）
- **展示**：学习中心.html（极简白 + 思源宋体）
- **核心价值**：把"题-考点-答案"沉淀为可复用的训练卡

### 9.2 宇兄窗口

- **场景**：平台开发 + 通用教育探索
- **范围**：7 PDT（PT-030 高考 / PT-031 通识 / PT-032 高校课件 / PT-033 企业培训 / PT-CAFAS 国美书法 / 等）
- **形式**：多媒体（Manim 动画 + TTS 配音 + 视频合成 + PDF）+ RUJING APP
- **核心价值**：把"4 步法通用基底"扩展到所有学科、所有场景

---

## 十、3 句话总结

**1. 我开发 + RUJING + 7 PDT，你学习中心.html + 高考 6 学科，display_target 字段分流**
**2. 共同规范：v1.0（5 核心）+ v1.1（11 扩展）+ v3.0（display_target 必填）**
**3. 4 步法通用基底两窗口都承担；PT-030 数学宇兄续做函数/数列/解析几何**

---

## 十一、宇兄窗口的"立刻可做"清单

### 高优（本周）

1. **拉共同仓最新**：`git pull origin master`
2. **跑 56 张 v1.1 卡校验回归**：输出 PASS/FAIL 报告
3. **给 56 张卡加 `display_target: ["RUJING"]` 字段**：提 PR 到共同仓
4. **写 XW 端 v1.0→v1.1 升级脚本**：参考 mavis 端 `upgrade_pps_v11.py`

### 中优（本月）

5. **PT-030 函数 4 步法母题**（10 母题 + 30 概念 + 30 变形）
6. **PT-030 数列 4 步法母题**（10 母题）
7. **PT-030 解析几何 4 步法母题**（10 母题）
8. **PT-031 通识 1 章节 Manim 动画 POC**

### 低优（按需）

9. 古史 v1-v4 ep04+ 微剧本
10. 墨骨山河 ep10+ 微剧本
11. 国美书法校考内容维护

---

## 十二、宇兄窗口需要雪薇窗口配合的请求

| 维度 | 宇兄请求 | 雪薇配合 |
|:---|:---|:---|
| display_target 默认值 | 宇兄端 `["RUJING"]`，雪薇端 `["学习中心"]` | 雪薇同意 |
| 4 步法归属 | 通用基底两窗口都承担 | 雪薇同意 |
| PT-030 = 4 步法数学 | 宇兄续做函数/数列/解析几何 | 雪薇 review 宇兄 PR |
| v1.1 升级脚本 | 宇兄写 XW 端版 | 雪薇提供 mavis 端 `upgrade_pps_v11.py` 源码参考 |
| validator 跨窗口 | 宇兄端跑 mavis 产 56 张卡 | 雪薇确认链路 PASS |

---

## 十三、基线版本约定

- **v1.0**（本文件，2026-09-12）：基线版，宇兄窗口发出
- **后续变更**：累积在 v1.0 之上，标注 v1.1/v1.2
- **回退**：v1.0 是 baseline，任何分歧以此版为准
- **冲突解决**：雪薇有最终拍板权

---

## 十四、文档签名

**作者**：宇兄窗口（刘宇的开发窗口 AI 助手）
**接收方**：雪薇窗口（雪薇的学生窗口 AI 助手）
**时间戳**：2026-09-12 14:14 北京时间
**文件路径**：`D:\2_products\education\SPDT-004_EduContent\handoff\SPDT004_DUAL_WINDOW_COLLABORATION_v1.0_给雪薇窗口.md`
**基线版本**：v1.0
**配套**：无单文件提示词（本文件即唯一协作说明）

---

**【完】**

**确认回执**（请雪薇窗口回复）：

```
[雪薇窗口收到] v1.0 协作说明
- 已读 sections: <章节号>
- 角色理解: <学生助手 / 主导方>
- display_target 默认值: ["学习中心"]
- 4 步法数学 v1.1 现状: 56 张 PASS（已发共同仓）
- 疑问/建议: <如有>
```
