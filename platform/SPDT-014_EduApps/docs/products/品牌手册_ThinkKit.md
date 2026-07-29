# ThinkKit 品牌手册

> 版本: v1.1 | 更新: 2026-07-17 | 隶属: SPDT-001 鸿蒙生态开发
> 品牌色: #5B8C5A 森绿 | OMAS 注册: HDT-001-TK

---

## 一、品牌定位

### 1.1 品牌标识

| 项 | 值 |
|:---|:---|
| 品牌名 | **ThinkKit** |
| 中文释义 | 思考工具集 / 思维套件 |
| 品牌色 | <span style="display:inline-block;width:14px;height:14px;background:#5B8C5A;border-radius:2px;vertical-align:middle;"></span> `#5B8C5A` 森绿 |
| 设计语言 | 知识感 · 专注 · 舒适 |
| Slogan | _用思考驱动学习_ |
| 商标状态 | 待注册 |

### 1.2 价值主张

ThinkKit 是一套**知识学习工具矩阵**——覆盖"学—记—思—测—读"全链路，每款 APP 专注单一场景、零学习成本、本地优先。

用户不需要在「功能臃肿的大而全」和「功能残缺的极简」之间妥协：**9 个工具各司其职，共同内核保证体验一致**。

### 1.3 目标用户画像

| 维度 | 描述 |
|:---|:---|
| 核心用户 | 18-35 岁知识工作者（学生 / 教师 / 研究者 / 自学者） |
| 使用场景 | 课堂笔记、考试复习、阅读摘录、技能学习、思维整理 |
| 设备环境 | 鸿蒙 NEXT 手机 + 平板（优先手机适配） |
| 付费意愿 | 买断制为主，轻度用户免费 + 高级功能一次性付费 |

### 1.4 差异化定位

| 对比维度 | ThinkKit | 传统笔记 APP | 超级 APP |
|:---|:---|:---|:---|
| 产品形态 | 独立工具矩阵 | 单一 APP | 多合一 |
| 学习曲线 | 零学习成本 | 中 | 高 |
| 内核复用 | common/ 23 文件共享 | 无 | 内部但有臃肿 |
| AI 生成率 | 85%+ | 0% | N/A |
| 数据主权 | 本地优先 | 云端为主 | 混合 |

---

## 二、产品矩阵

### 2.1 APP 清单

| # | APP | 中文名 | 功能 | 编译 | 签名 | HAP | 特色能力 |
|:---|:---|:---|:---|:---|:---|:---|:---|
| 1 | thinkkit-coach | 学习教练 | Agent 驱动个性化学习 | ✅ | ✅ | 228.8 KB | 知识全景 / 闪卡生成 / 模板系统 |
| 2 | thinkkit-flashcard | 静·闪卡 | 双向闪卡记忆 | ✅ | ✅ | 427.2 KB | SM-2 间隔重复算法 |
| 3 | thinkkit-zknote | 大纲速记 | 极简大纲笔记 | ✅ | ✅ | 418.6 KB | 本地优先 / 无干扰写作 |
| 4 | thinkkit-mindmap | 思维导图 | 灵活思维导图 | ✅ | ✅ | 187.7 KB | 脑图可视化 |
| 5 | thinkkit-quiz | 互动测验 | 知识测验工具 | ✅ | ✅ | 165.9 KB | 计时 / 评分 / 解析 |
| 6 | thinkkit-reader | 深度阅读器 | 阅读 + 摘录批注 | ✅ | ✅ | 110.8 KB | 多级字号 / 标注系统 |
| 7 | thinkkit-note | 轻笔记 | 轻量级笔记与灵感捕捉 | ✅ | ✅ | 175.3 KB | 快速记录 / Markdown 支持 |
| 8 | thinkkit-rss | RSS 订阅 | 知识源订阅与聚合阅读 | ✅ | ✅ | 190.2 KB | 多源聚合 / 离线阅读 |
| 9 | thinkkit-flashcard2 | 闪卡 Pro | 高级闪卡记忆与自定义模板 | ✅ | ✅ | 245.6 KB | SM-2 增强 / 多媒体卡片 |

> **总计**: 9 款 APP，总 HAP 体积 2,150 KB，编译 + 签名 100% 通过。

### 2.2 产品架构

```
ThinkKit 知识学习矩阵
│
├─ 📖 输入层 ──────────────────────────
│   ├── reader     深度阅读器（读）
│   ├── rss        RSS 订阅（源）
│   ├── note       轻笔记（捕捉）
│   └── coach      学习教练（引导输入）
│
├─ 🧠 加工层 ──────────────────────────
│   ├── zknote     大纲速记（写）
│   ├── mindmap    思维导图（理）
│   ├── flashcard  闪卡记忆（记）
│   └── flashcard2 闪卡 Pro（深度记忆）
│
└─ 📊 输出层 ──────────────────────────
    └── quiz       互动测验（测）
```

学习闭环：**源 → 读 → 写 → 理 → 记 → 测**，每层独立工具，层间通过 common/ 内核保证数据和交互一致。

### 2.3 Feature Flag 矩阵

| APP | enableCoach | enableFlashCard | enableOutlineNote | enableKnowledgePanorama | enableTemplates | 其他 |
|:---|:---|:---|:---|:---|:---|:---|
| coach | ✅ | ✅ | — | ✅ | ✅ | Lingkong AI |
| flashcard | — | ✅ | — | — | — | SM-2 |
| zknote | — | — | ✅ | — | — | — |
| mindmap | — | — | — | — | — | 独立功能 |
| quiz | — | — | — | — | — | 计时/评分 |
| reader | — | — | — | — | — | 字号/标注 |
| note | — | — | — | — | — | Markdown |
| rss | — | — | — | — | — | 多源聚合 |
| flashcard2 | — | ✅ | — | — | — | SM-2 增强 |

> coach 作为旗舰产品承载了最多的 Feature Flag 复用。

### 2.4 定价体系

| 层级 | 范围 | 模式 | 建议价格 | 状态 |
|:---|:---|:---|:---|:---|
| 免费层 | 全部 9 款基础功能 | 免费 | ¥0 | 已实现 |
| 高级层 | coach/flashcard/quiz/flashcard2 高级功能 | 买断制 | ¥12-30/款 | 待接入支付 |
| 套装 | ThinkKit 全家桶 | 买断制 | ¥98 (9 款) | 规划中 |

---

## 三、智能体定位

> 依据《智能体APP设计指南》，ThinkKit 将 Agent 能力嵌入旗舰学习工具，以**任务型智能体**驱动个性化学习体验。

### 3.1 智能体矩阵

| APP | Agent 优先级 | 智能体类型 | 核心能力 |
|:---|:---|:---|:---|
| thinkkit-coach | **P0** | 任务型 · 个性化学习 Agent | 知识全景诊断 → 学习路径规划 → 闪卡自动生成 → 模板推荐 |
| thinkkit-flashcard | **P0** | 任务型 · SM-2 自适应 Agent | SM-2 间隔重复调度 → 遗忘曲线预测 → 复习提醒 → 难度自适应 |
| thinkkit-quiz | **P0** | 任务型 · 自动出题批改 Agent | 知识点提取 → 试题自动生成 → 智能评分 → 错因解析 |
| thinkkit-flashcard2 | P1 | 任务型 · 高级记忆 Agent | 多媒体卡片生成 → 增强 SM-2 调度 → 自定义模板 |

### 3.2 Agent 交互入口

| 属性 | 规范 |
|:---|:---|
| **入口形态** | 页面右下角**浮动按钮**（FAB），不干扰主界面内容区 |
| **品牌色** | 森绿色 `#5B8C5A`，与品牌 Design Token 统一 |
| **触发方式** | 点击唤起 Agent 对话面板，半屏/全屏自适应 |
| **可见性规则** | 仅在 P0/P1 Agent APP 中显示；reader/note/rss 等纯工具 APP 不启用 |
| **设计原则** | 按需唤起、非侵入式、上下文感知（根据当前页面智能推荐操作） |

### 3.3 智能体设计原则

1. **场景分离**: Agent 面板独立于工具主体，不破坏原有页面流
2. **任务闭环**: 用户提需求 → Agent 执行 → 结果反馈 → 一键应用，全链路在面板内完成
3. **品牌一致性**: FAB 颜色、动画、文案风格与 ThinkKit 森绿品牌体系统一
4. **渐进式介入**: 首次使用引导提示，熟练后可快捷指令唤起

---

## 四、技术规格

### 4.1 SDK 与编译环境

| 项 | 值 |
|:---|:---|
| 语言 | ArkTS (TypeScript 超集，strict mode，禁止 `any`) |
| UI 框架 | ArkUI 声明式 (Stage 模型) |
| 状态管理 | @State / @Link / @Provide-@Consume |
| 路由 | Navigation + NavPathStack (**已从 router API 迁移**) |
| targetSdkVersion | 26.0.0 |
| compatibleSdkVersion | 6.1.1(24) |
| 编译工具 | hvigorw.bat (v6.26.1) |
| 存储 | Preferences (本地 JSON) |

### 4.2 编译命令（CLI 全自动流水线）

```powershell
$env:OHOS_SDK_HOME = "D:\9_infra\DevEco Studio\sdk"
$env:PATH = "D:\9_infra\DevEco Studio\tools\node;$env:PATH"

# 单 APP
Push-Location "D:\92_products\SPDT-001_Harmony\apps\thinkkit-coach"
& "D:\9_infra\DevEco Studio\tools\hvigor\bin\hvigorw.bat" assembleHap
Pop-Location

# 品牌级批量编译
powershell -ExecutionPolicy Bypass -File "D:\92_products\SPDT-001_Harmony\build-all.ps1" -Brand thinkkit
```

### 4.3 签名策略

- **开发阶段**: debug profile + 自建 cert chain
- **批量签名**: `sign-all.ps1` 自动识别 bundleName → 匹配对应 profile
- **签名状态**: 6/6 通过

### 4.4 公共内核 (common/)

ThinkKit 9 款 APP 共享同一套 `common/` 内核（23 个源文件）：

| 模块 | 文件 | 说明 |
|:---|:---|:---|
| **组件** (12) | HButton, HCard, HConfirmDialog, HEmptyState, HFAB, HFormItem, HNavBar, HProgressBar, HSearchBar, HTag, HTagGroup, HToast | UI 组件库，品牌色统一注入 |
| **存储** (2) | storageService.ts, keys.ts | 泛型 CRUD，Preferences 封装 |
| **主题** (1) | tokens.ts | Design Token（3 套主题） |
| **工具** (5) | date.ts, debounce.ts, format.ts, id.ts, validate.ts | 日期/防抖/格式化/ID/校验 |
| **算法** (2) | sm2.ts, streak.ts | SM-2 间隔重复 + 连续打卡 |

### 4.5 PREFLIGHT 检查项

8 项自动检查，品牌级 `-BrandPrefix "thinkkit-"` 过滤：

| 检查项 | 说明 |
|:---|:---|
| build-profile.json5 | API 24 兼容 |
| oh-package.json5 | modelVersion 26 |
| hvigor-config.json5 | modelVersion 26 |
| AppScope/app.json5 | bundleName 格式 |
| module.json5 | 存在且格式正确 |
| pages/ | 至少 1 个 .ets |
| brand color | ThinkKit #5B8C5A |
| 跨品牌污染 | 禁止非 thinkkit 引用 |

### 4.6 常见编译问题

| 错误码 | 症状 | 修复 |
|:---|:---|:---|
| 00303096 | mock-config.json5 无效路径 | 重命名 mock → mock_disabled |
| 00303038 | main_pages.json schema | `"pages"` → `"src"` |
| 00303034 | compileSdkVersion 缺失 | 切 HarmonyOS + targetSdk 26 |
| 00303027 | modelVersion 不一致 | 统一 26.0.0 |
| 11203005 | float.json 空节点 | 补占位项 |
| 11211120 | $media 缺失 | 创建图标资源 |
| 10605071/05029/05001 | bracket notation | class + dot notation |

> 完整手册: [编译问题修复手册 v2](D:\92_products\SPDT-001_Harmony\编译问题修复手册 v2.md)

---

## 五、运营数据

> ⚠️ 以下为占位，当前 ThinkKit 尚未上架鸿蒙应用商店。

| 指标 | 当前值 | 目标 (Q3) |
|:---|:---|:---|
| 上架数 | 0/9 | 9/9 |
| 下载量 | — | 10,000+ |
| 日活用户 (DAU) | — | 1,000+ |
| 评分 | — | 4.5+ ★ |
| 月收入 | — | ¥5,000+ |
| 崩溃率 | — | < 0.5% |

---

## 六、发展规划

### 6.1 当前缺口

| 缺口 | 影响 | 优先级 |
|:---|:---|:---|
| 未上架应用商店 | 无真实用户反馈 | P0 |
| 无自动化测试框架 | 回归依赖手工 | P2 |
| quiz 功能仅骨架 | 产品不完整 | ✅ 已修复 |

### 6.2 教育系列 15 款扩展路线图

基于当前 "读→写→理→记→测" 五层闭环，扩展至教育全场景：

```
当前 6 款                           目标 15 款
─────────────────────────────────────────────
📖 reader           ──→ +vocabulary（单词本）+article（范文库）
✏️ zknote           ──→ +diary（学习日记）+todo（学习计划）
🧠 mindmap          ──→ +timeline（时间线）+concept（概念图）
🔁 flashcard        ──→ +review（错题本）+spaced（间隔复习）
📊 quiz             ──→ +exam（模拟考试）+report（成绩报告）
🤖 coach            ──→ +tutor（AI 辅导）+plan（学习规划）+track（进度追踪）
```

| 批次 | APP | 预计 HAP | 生成方式 |
|:---|:---|:---|:---|
| 第 1 批 (7 月) | vocabulary, diary, timeline, review, exam | 各 ~100-200 KB | 模板 fork |
| 第 2 批 (8 月) | article, todo, concept, spaced, report | 各 ~100-200 KB | 模板 fork |
| 第 3 批 (9 月) | tutor, plan, track | 各 ~300-500 KB | 模板 fork + AI 补充 |

> 合计: 15 款 APP，其中 9 款新增，预计总 HAP 体积 ~3,000 KB。

### 6.3 新 APP 立项评审标准

| 维度 | 评审问题 | 权重 |
|:---|:---|:---|
| 场景匹配 | 是否填补"学—记—思—测—读"中的空白？ | 高 |
| 内核复用 | 能否用 common/ 现有组件覆盖 80%+ UI？ | 高 |
| 竞品缺口 | 鸿蒙生态中是否有同类产品？ | 中 |
| AI 可达 | 代码生成率能否达到 85%+？ | 中 |
| 用户痛点 | 是否解决真实学习场景中的具体问题？ | 高 |

### 6.4 版本迭代节奏

| 阶段 | 周期 | 产出 |
|:---|:---|:---|
| 骨架生成 | 1 天 | 模板 fork → 配置 → 编译通过 |
| 功能开发 | 2-3 天 | UI 页面 + 核心交互 |
| 内测 | 1 天 | PREFLIGHT → 编译 → 签名 → 模拟器 |
| 真机部署 | 1 天 | hdc install → 截图 → 核心路径验收 |
| 上架准备 | 1 天 | 商店素材 → 描述文案 → ASO |

### 6.5 里程碑

| 里程碑 | 目标日期 | 状态 | 关键产出 |
|:---|:---|:---|:---|
| M1: 首批 6 款全通 | 2026-07-08 | ✅ 完成 | 6/6 编译+签名 |
| M2: 真机部署验证 | 2026-07-12 | ✅ 完成 | 9/9 真机安装 + 冷启动 < 2s（DevEco 6.1 + devecocli 全自动流水线） |
| M3: 教育系列 15 款启动 | 2026-07-20 | ⏳ 规划 | 首批 5 款新 APP 编译通过 |
| M4: 应用商店上架 | 2026-08-01 | ⏳ 规划 | 9 款提交审核 |
| M5: 15 款全部交付 | 2026-09-15 | ⏳ 规划 | 15/15 编译+签名+上架 |

---

## 七、营销素材

### 6.1 品牌话术

**一句话介绍:**
> ThinkKit —— 用思考驱动学习，6 个独立工具覆盖全链路知识管理。

**扩展介绍 (100 字):**
> ThinkKit 是鸿蒙生态首套知识学习工具矩阵。从深度阅读到闪卡记忆，从大纲速记到思维导图，从互动测验到 AI 教练——6 款独立 APP 各司其职，共享统一内核，零学习成本。本地优先，买断制，不订阅不套路。

**品牌故事角度:**
> 「学习不该被一个臃肿的 APP 绑架。」ThinkKit 的核心理念是：每个学习场景都值得一个专属工具——需要笔记时打开 ZKNote，需要复习时打开 FlashCard，需要测试时打开 Quiz。小而美，各司其职，这才是工具该有的样子。

### 6.2 应用商店描述模板

```
## 概述
[APP 中文名] 是 ThinkKit 知识学习工具系列的一员——[一句话功能]。

## 核心功能
• [功能点 1]
• [功能点 2]
• [功能点 3]

## 为什么选择我们？
✅ 专注单一场景，零学习成本
✅ 本地数据优先，隐私安全
✅ 买断制，一次付费永久使用
✅ 鸿蒙 NEXT 原生，API 24 优化

## ThinkKit 系列
ThinkKit 提供 9 款独立学习工具：[列出其余 8 款名称]
```

### 6.3 截图与图标规范

| 项目 | 规范 |
|:---|:---|
| 应用图标 | 1024×1024 px，森绿基调，白色内容物 |
| 商店截图 | 鸿蒙设备框架 × 5 张（首页 / 核心功能 1 / 核心功能 2 / 结果页 / 设置） |
| 宣传横幅 | 1242×2688 px (竖版) |
| 品牌 Logo | 中英文组合，森绿 #5B8C5A |

### 6.4 ASO 关键词策略

| APP | 核心词 | 长尾词 |
|:---|:---|:---|
| coach | 学习教练, AI 学习 | 高考数学辅导, 个性化学习方案 |
| flashcard | 闪卡, 记忆卡片 | 间隔重复, SM-2 算法, 考试复习 |
| zknote | 大纲笔记, 速记 | 极简笔记, 无干扰写作 |
| mindmap | 思维导图, 脑图 | 思维整理, 知识可视化 |
| quiz | 测验, 题库 | 知识测试, 互动问答, 模拟考试 |
| reader | 阅读器, 深度阅读 | 摘录批注, 多级字号, 标注 |

### 6.5 竞品参考 (鸿蒙生态)

> [待调研] 鸿蒙应用商店同类产品清单、定价、评分对比。

---

## 八、附录

### 8.1 关键路径速查

```
项目根       D:\92_products\SPDT-001_Harmony\
ThinkKit APP D:\92_products\SPDT-001_Harmony\apps\thinkkit-*
公共内核     D:\92_products\SPDT-001_Harmony\common\
CI 流水线    D:\92_products\SPDT-001_Harmony\ci\
签名证书     D:\92_products\SPDT-001_Harmony\signing\profile-thinkkit-*
品牌模板     D:\92_products\SPDT-001_Harmony\templates\base\
OMAS 注册    D:\6_agent_project\omas\pdt_registry\HDT-001-TK\
编译手册     D:\92_products\SPDT-001_Harmony\编译问题修复手册 v2.md
```

### 8.2 OMAS 治理信息

| 字段 | 值 |
|:---|:---|
| SPDT | SPDT-001 鸿蒙生态开发 |
| 子PDT ID | HDT-001-TK |
| 品类 | 知识学习工具 |
| 负责人 | PL-thinkkit |
| 质量策略 | warnings_policy: no_new |
| 目标总数 | 50 款 APP |

### 8.3 关联文档索引

| 文档 | 路径 |
|:---|:---|
| 项目 README | [D:\92_products\SPDT-001_Harmony\README.md](D:\92_products\SPDT-001_Harmony\README.md) |
| 工作交接文档 | [D:\92_products\SPDT-001_Harmony\docs\工作交接_鸿蒙专项SPDT-001.md](D:\92_products\SPDT-001_Harmony\docs\工作交接_鸿蒙专项SPDT-001.md) |
| 编译问题手册 v2 | [D:\92_products\SPDT-001_Harmony\编译问题修复手册 v2.md](D:\92_products\SPDT-001_Harmony\编译问题修复手册 v2.md) |
| DevEco 操作手册 | [D:\92_products\SPDT-001_Harmony\DevEco完整操作手册_v1.md](D:\92_products\SPDT-001_Harmony\DevEco完整操作手册_v1.md) |
| CI 流水线配置 | [D:\92_products\SPDT-001_Harmony\ci\pipeline.yaml](D:\92_products\SPDT-001_Harmony\ci\pipeline.yaml) |
| SPDT 注册 | [D:\6_agent_project\omas\spdt_registry\SPDT-001\spdt.yaml](D:\6_agent_project\omas\spdt_registry\SPDT-001\spdt.yaml) |
| 运营 SOP | [D:\92_products\SPDT-001_Harmony\运营SOP_v1.md](D:\92_products\SPDT-001_Harmony\运营SOP_v1.md) |

### 8.4 更新记录

| 日期 | 版本 | 变更 |
|:---|:---|:---|
| 2026-07-17 | v1.1 | 扩展至 9 款 APP（新增 note/rss/flashcard2）；真机部署验证通过（DevEco 6.1 + devecocli）；新增智能体定位章节 |
| 2026-07-07 | v1.0 | 初始版本，覆盖 6 款 APP 全貌 |

---

> 🏗️ 鸿蒙特使 · SPDT-001 | ThinkKit 品牌手册 v1.1 | 下一步: 生成 HTML 渲染版
