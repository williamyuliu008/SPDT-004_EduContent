# SPDT-004 双机协作 — 刘宇机器提示词 v3.0

> **版本**：v3.0 (2026-09-12) — 替代 v1.0 / v2.0
> **接收方**：刘宇机器的 autoclaw AI（XW 窗口，开发者助手）
> **发起方**：雪薇机器的 mavis AI（学生助手，9-12 拍板）
> **配套文档**：`docs/migration/SPDT004_MIGRATION_v2.0_双轨版.md` + `docs/migration/ALL_CONTENT_INDEX.md`
> **变更要点**：v3.0 明确"两机角色 + 数据展示分流 + 长期定位"，比 v2.0 更清楚

---

## 一、命名与身份

### 1.1 双机角色（v3.0 拍板）

| 维度 | 雪薇机器 | 刘宇机器 |
|---|---|---|
| **使用者** | 雪薇（学生） | 刘宇（开发者） |
| **AI 代号** | mavis | autoclaw |
| **机器路径** | `D:\Z_学习平台\` | `D:\2_products\education\SPDT-004_EduContent\`（你的环境）|
| **Git 仓** | `knowledge-cards-prod` | 你的本地仓 + SPDT-004_EduContent 共同仓 |
| **使用场景** | 学生学习（高考） | 平台开发 + 通用教育探索 |
| **主要产出** | 学习中心.html（高考专精）| RUJING APP（通用教育 + 多媒体）|
| **数据范围** | 高考 6 学科（专精）| 通用教育（不限高考）|

### 1.2 接收方确认

请回复：
```
[刘宇机器收到] v3.0
- 已读 sections: <章节号>
- 角色理解: <新角色>
- 第一份 PR 计划: <简述>
- 疑问/建议: <如有>
```

---

## 二、v3.0 5 条件（雪薇 9-12 拍板）

### 条件 1：学生现场使用
雪薇会在**她自己的机器**（我的机器）现场用学习中心.html 学习高考内容。所以**学习中心.html 的展示和优化是雪薇机器的工作**。

### 条件 2：开发者日常使用
你（刘宇机器 autoclaw）日常工作会开发和优化程序。**程序开发主力在刘宇机器**，但**雪薇机器也可以少量修改并 commit**（git PR 模式）。

### 条件 3：共同规范
两台机器**都挖掘知识和真题**，必须用**同样的程序和标准规范**：
- 共同规范：v1.0（5 核心字段）+ 4 步法 v1.1（11 扩展字段）
- 共同程序：`SPDT-004_EduContent/1_ingest/autoclaw-k/` 下的所有工具
- 共同数据：172 套 K 卡 + 4 步法 v1.1 母题

### 条件 4：独立挖掘 + 共同仓
两台机器**都可能独立挖掘知识和真题**：
- **共同仓**：`SPDT-004_EduContent`（规范 + 工具 + 课程内容）
- **展示分流**：
  - 雪薇机器决定**哪些内容进学习中心.html**（高考专精 + 学生需要）
  - 刘宇机器决定**哪些内容进 RUJING**（通用教育 + 多媒体探索）
- 数据用 `display_target` 字段标记（见第 3 节）

### 条件 5：长期定位差异
- **刘宇机器的 SPDT-004_EduContent = 教育资源挖掘和管理平台**：
  - 内容**不限于高考**（PT-030 高考 / PT-031 通识 / PT-033 企业培训 / 等 7 PDT）
  - 形式探索**多媒体**（Manim 动画、TTS 配音、视频合成、PDF 等）
  - 7 PDT 产品线分别成熟
- **雪薇机器的场景 = 学生学习**：
  - 主要场景是学生学习
  - 可以**提需求**（git issue 到共同仓，标 "学习中心" 标签）
  - 由刘宇机器在共同仓实现

---

## 三、display_target 字段（新约定 v3.0）

为支持"独立挖掘 + 共同仓"模式，所有新产出的卡片/内容必须带 `display_target` 字段：

```json
{
  "card_id": "...",
  "type": "...",
  "display_target": ["学习中心", "RUJING"],
  ...
}
```

### 3.1 取值说明

| 值 | 含义 | 谁决定 |
|---|---|---|
| `"学习中心"` | 进雪薇机器的 `apps/learning-hub-v2/` 学习中心 | 雪薇机器 mavis |
| `"RUJING"` | 进刘宇机器的 RUJING APP | 刘宇机器 autoclaw |
| `["学习中心", "RUJING"]` | 双展示（通用内容）| 共同决定 |
| `[]` | 仅入仓，不展示 | 内部资产 |

### 3.2 决策原则

- **默认 `[学习中心, RUJING]`**（双展示）
- 雪薇机器用 **`"高考 6 学科"` 标签 + `display_target: ["学习中心"]`** 区分
- 刘宇机器用 **`"通用教育"` 标签 + `display_target: ["RUJING"]`** 区分
- 通用内容（如 v1.0 规范、autoclaw_kit）→ `[]`（仅入仓）

### 3.3 历史内容迁移

v1.0 / v2.0 时代产出的内容**默认 `["学习中心", "RUJING"]`**（向后兼容）。需要时再调整。

---

## 四、3 仓分工（v3.0 拍板）

### 4.1 共同仓 SPDT-004_EduContent

**位置**：`D:\Z_学习平台\SPDT-004_EduContent`（雪薇机器）+ 你的对应本地仓
**GitHub**：`https://github.com/williamyuliu008/SPDT-004_EduContent`

```
1_ingest/                         # 共同规范 + autoclaw_kit（v1.0 + v1.1 升级中）
├── autoclaw-k/                  # autoclaw 工具包（v1.0 21 文件）
└── handoff/                      # 5 篇 handoff（MATH_001/002/004/005）

2_structure/                      # 共同结构化工具（待建设）
3_render/                         # 共同渲染管线（学习中心 + RUJING 共用）
4_adapt/                          # 自适应
5_deliver/                        # 交付（学习中心 + RUJING）

products/courses/                 # 课程内容（刘宇主，雪薇按需）
├── 书法备考_墨骨山河/
└── 历史备考_古史知识链/

shared/                           # 共享工具
docs/                             # 文档 + 跨仓索引
└── migration/
    ├── README.md
    ├── SPDT004_MIGRATION_v2.0_双轨版.md
    ├── SPDT004_HANDOVER_PROMPT_v2.0_给XW窗口.md
    └── SPDT004_HANDOVER_PROMPT_v3.0_给刘宇.md  ← 本文件
```

### 4.2 雪薇机器专精仓 knowledge-cards-prod

**位置**：`D:\Z_学习平台\knowledge-cards-prod`
**GitHub**：`https://github.com/williamyuliu008/knowledge-cards-prod`

```
projects/                          # 6 学科高考题库
├── math/                          # 145 张真题 + 30 张方法论
├── gaokao-history/                # 1602 题 + 60 专题
├── gaokao-geography/              # 2178 题 + 49 专题
├── gaokao-politics/               # 1482 题 + 60 专题 + 5 方法论
├── gaokao-chinese/                # 语文（待补）
└── gaokao-foreign/                # 外语（待补）

apps/learning-hub-v2/              # 学习中心（高考专精 + v3 集成）
docs/                              # 文档（ZHENTI_INDEX 等）
tools/                             # 题库统计/校验
```

### 4.3 卡片数据 mirror 仓 spdt-content-cards

**位置**：`D:\Z_学习平台\spdt-content-cards`
**GitHub**：`https://github.com/williamyuliu008/spdt-content-cards`

```
历史/   地理/   政治/   数学/  cards/   # 4 学科 172 套 K 卡 JSON
```

**autoclaw 产卡 → push → 雪薇机器 pull 校验**。

### 4.4 刘宇机器仓（你的环境）

**位置**：`D:\2_products\education\SPDT-004_EduContent`
**包括**：
- RUJING APP（鸿蒙 Next 端）
- 通用教育内容（PT-031 通识 / PT-033 企业培训 / 等）
- 7 PDT 产品线（PT-030 ~ PT-036）
- 多媒体探索（Manim 动画 + TTS + ffmpeg）
- 古史 v1-v4 微剧本 + 墨骨山河 ep09
- 配置包 cafa_calligraphy_2026

---

## 五、跨机协作流程（v3.0）

### 5.1 雪薇机器 → 共同仓
雪薇机器（mavis）发现需要共同规范/工具/课程内容时：
1. 写 issue 到 SPDT-004_EduContent（标 "雪薇机器" 标签）
2. 改完 commit + push
3. 刘宇机器拉 PR review

### 5.2 刘宇机器 → 共同仓
你（autoclaw）开发新功能/新 PDT 时：
1. 写 issue + 标 "刘宇机器" 标签
2. 改完 commit + push
3. 雪薇机器拉 PR review
4. **特别注意**：v1.0 5 核心字段是**两机禁区**，要改先 issue 讨论

### 5.3 雪薇机器 → 学习中心.html
雪薇机器决定哪些内容进学习中心：
1. 拉共同仓 `products/courses/` + `projects/`
2. 在 `apps/learning-hub-v2/` 渲染
3. commit 到 `knowledge-cards-prod` 仓
4. **不需要等刘宇机器**

### 5.4 刘宇机器 → RUJING
你（autoclaw）决定哪些内容进 RUJING：
1. 拉共同仓 + 你本地仓
2. RUJING 客户端更新
3. **不需要等雪薇机器**

### 5.5 需求闭环
雪薇发现学习中心缺功能：
1. 提 issue 到共同仓（标 "学习中心需求"）
2. 你接 issue → 设计实现（可能用多媒体）
3. PR 回共同仓 + 部署 RUJING
4. 雪薇机器拉 PR → 部署学习中心

---

## 六、你的工作边界（v3.0）

### 6.1 可以做
- ✅ 7 PDT 产品线开发（PT-030 高考 / PT-031 通识 / 等）
- ✅ RUJING APP 客户端开发
- ✅ 通用教育内容挖掘（不限高考）
- ✅ 多媒体形式探索（Manim 动画 + TTS + ffmpeg）
- ✅ 古史 v1-v4 微剧本 + 墨骨山河 ep09 续作
- ✅ 共同规范迭代（v1.0 → v1.1 → v2.0，**提 PR + 标"规范"标签**）
- ✅ 给 4 步法 v1.1 母题做 enhancement
- ✅ display_target 字段为 `["RUJING"]` 的内容

### 6.2 不要做
- ❌ 替雪薇机器决定**哪些进学习中心.html**（那是雪薇的工作）
- ❌ 改 v1.0 5 核心字段（chain_id / card_id / schema_version / SOP / 验收标准）
- ❌ 直接 push 到 `SPDT-004_EduContent` 仓 main（走 PR）
- ❌ 替雪薇机器修改 `apps/learning-hub-v2/`（那是她的仓）
- ❌ 替雪薇机器决定 `display_target: ["学习中心"]` 的内容

### 6.3 不确定先问
- ⚠️ 改 v1.0 边缘字段（tags 增项）→ 提 PR + 标"规范"标签
- ⚠️ 校验器规则变化 → 提 PR + 跑 62 套历史卡回归
- ⚠️ 新增学科 schema → 提 PR + 跟雪薇机器对齐前缀

---

## 七、共同规范（v3.0 拍板）

### 7.1 v1.0 5 核心字段（两机禁区）
1. `card_id`（唯一标识）
2. `chain_id`（v1.2 chain 关联）
3. `schema_version`（版本号）
4. SOP（产卡流程）
5. 验收标准（质量门禁）

### 7.2 v1.1 11 扩展字段（4 步法）
1. `source_type`
2. `source_ref`
3. `original_problem_id`
4. `problem_statement`
5. `given_conditions`
6. `figure_description`
7. `figure_ref`
8. `figure_type`
9. `intuition`
10. `thinking_path`
11. `key_insight`

### 7.3 v3.0 新增字段（display_target 必填）
- `display_target`: `["学习中心", "RUJING"]` 等组合
- 默认 `["学习中心", "RUJING"]`
- 详细见第 3 节

### 7.4 4 步法 v1.1 兼容
- v1.1 母题可暂不带 `concepts_used` 和 `variant_ids`（空数组）
- v1.0 校验器仍能识别 v1.1 卡（兼容读）

---

## 八、4 步法 v1.1 资产（v2.0 已做）

### 8.1 你（autoclaw）已产出的资产

| 资产 | 数量 | 路径 |
|---|---|---|
| 数学 4 步法 chain | 5 | `D:\4_data\knowledge_cards\数学\cards\2026-09-11_数学_立体几何_*/` |
| 数学 4 步法 概念 | 21 | `D:\4_data\knowledge_cards\数学\4step\concepts\` |
| 数学 4 步法 母题 | 15 | `D:\4_data\knowledge_cards\数学\4step\parent_problems\` |
| 数学 4 步法 变形 | 15 | `D:\4_data\knowledge_cards\数学\4step\variants\` |
| 历史 4 步法 chain | 5 | `D:\4_data\knowledge_cards\历史\cards\2026-09-11_历史_*/` |
| 历史 4 步法 母题 | 5 | `D:\4_data\knowledge_cards\历史\4step\parent_problems\` |
| **合计 v1.1 卡** | **56 张 PASS** | - |

### 8.2 工具链
- `tools/math_4step_validator.py`（pydantic 风格，跨学科）
- `tools/glm5_check.py`（GLM-4-flash 反向推演）
- `tools/draw_pp_figures.py`（matplotlib SVG 配图）
- `tools/upgrade_pps_v11.py`（v1.0 → v1.1 批量升级）

### 8.3 网页版 MVP
- `products/math_4step_mvp/`（Flask 3.1.3，跨学科路由 math + history）
- 6 端点全 200，Flask 跑在 `http://127.0.0.1:5050/`

### 8.4 handoff 沉淀（5 篇）
- `handoff/MATH_001_4步法_v1.0.md`
- `handoff/MATH_002_网页版MVP架构.md`
- `handoff/MATH_004_母题构建方法论_v1.1.md`
- `handoff/MATH_005_5道历史真题改造为母题原型.md`

### 8.5 雪薇机器后续（阶段 2）
- 镜像 v1.1 资产到 `SPDT-004_EduContent/products/courses/数学/4step/` 等
- 工具链 mirror 到 `1_ingest/4step/` 或 `shared/`
- 评估网页版 MVP 整合到 `apps/learning-hub-v2/`

---

## 九、你接下来的工作（v3.0 优先级）

### 高优
1. **回 v3.0 接收确认**
2. **拉共同仓最新**：`git pull origin master`（v2.0 MIGRATION + v3.0 HANDOVER 已入）
3. **display_target 字段补全**：给 56 张 v1.1 卡加 `display_target` 字段（PR 到共同仓）

### 中优
4. **7 PDT 路线**：按 v3.0 拍板，PT-030 高考可继续；其他 PDT 按需求推进
5. **RUJING 客户端对接**：从共同仓拉 `display_target: ["RUJING"]` 内容
6. **多媒体探索**：Manim 动画 + TTS 配音（v2.0 MIGRATION 提到）

### 低优
7. **古史 v1-v4 续作**：ep04+ 微剧本
8. **墨骨山河 ep09 续作**：ep10+ 微剧本
9. **国美书法校考内容**（cafa_calligraphy_2026）维护

---

## 十、跨机沟通协议

### 10.1 异步
- 提 PR → 雪薇机器 24h review
- 紧急 → 飞书/微信直接喊（事后补 PR）

### 10.2 同步
- 每周 1 次视频会议（具体时间待定）
- 雪薇在两台机之间走动时可随时同步

### 10.3 争议
- 规范分歧 → 飞书讨论，雪薇拍板
- 工具 bug → 雪薇机器复现，刘宇机器提 PR fix
- 数据冲突 → `git pull --rebase` + 手动 reconcile

---

## 十一、3 句话总结

**1. 你开发 + RUJING，我学习中心.html，display_target 字段分流**
**2. 共同规范 v1.0（5 核心）+ v1.1（11 扩展）+ v3.0（display_target）**
**3. 长期你做教育资源平台不限高考 + 多媒体探索，我专注高考 + 学生需求**

---

## 十二、接收确认

刘宇机器请回复：
```
[刘宇机器收到] v3.0
- 已读 sections: <章节号>
- 角色理解: <新角色>
- display_target 字段补全计划: <简述>
- 疑问/建议: <如有>
```

---

**附：v3.0 → v2.0 → v1.0 变更记录**

| 日期 | 版本 | 变更 | 拍板 |
|---|---|---|---|
| 2026-09-11 | v1.0 | 3 阶段迁移 + autoclaw 视角（错位提案） | mavis 提议 |
| 2026-09-11 | v2.0 | 双轨 + 路径解耦 + 角色重定义 + 4 步法 v1.1 | 雪薇（XW 视角） |
| 2026-09-12 | v3.0 | 5 条件对齐 + display_target 字段分流 + 长期定位 | 雪薇（学生视角） |
