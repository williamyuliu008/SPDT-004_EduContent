# HarmonyCoder 品牌手册 — SPDT-001

> **说需求，出代码** · AI编程伙伴（旗舰） · HDT-001-HC · v1.1 · 2026-07-17

---

## 一、品牌定位

### 品牌标识

| 属性 | 值 |
|------|-----|
| 品牌名 | HarmonyCoder |
| 品牌色 | `#7B2D8E` 紫 |
| OMAS 编号 | HDT-001-HC |
| 品类 | AI编程伙伴（旗舰） |
| Slogan | 说需求，出代码 |
| 定位 | 鸿蒙开发者首选 AI 编程伙伴 |

### 目标用户

**鸿蒙开发者**：从入门到进阶的 HarmonyOS NEXT 应用开发者，需要 AI 辅助完成代码生成、项目搭建、三方库选型、DevEco 集成等日常开发任务。

- 开发者画像：独立开发者 / 企业鸿蒙开发团队 / 鸿蒙初学者
- 核心场景：快速原型开发 / 学习 HarmonyOS API / 查三方库 / 导出到 DevEco Studio

### 定价模式

| 项目 | 价格 |
|------|------|
| HarmonyCoder（旗舰）| ¥68 买断制 |
| 免费试用 | 基础代码生成可用 |

### 差异化对比

| 维度 | HarmonyCoder | 传统 IDE 插件 | 通用 AI 编程助手 |
|------|-------------|-------------|----------------|
| 鸿蒙专属 | ✅ 深度适配 | ❌ 通用 | ❌ 通用 |
| 零警告 | ✅ warnings_policy: zero | ❌ 不保证 | ❌ 不保证 |
| OHPM 推荐 | ✅ 内置 10+ 库推荐引擎 | ❌ 需手动查找 | ❌ 不涵盖 |
| DevEco 导出 | ✅ 一键导出 | ❌ 需手动迁移 | ❌ 不支持 |
| 买断制 | ✅ ¥68 终身 | — | 按月订阅 |

---

## 二、产品矩阵

### APP 清单

| # | APP | 中文名 | 功能 | 编译 | 签名 | HAP | 特色能力 |
|---|-----|--------|------|------|------|-----|----------|
| 1 | harmonycoder | AI编程伙伴 | AI编程伙伴，说需求即出代码 | ✅ | ✅ | 392 KB | 代码生成 / 项目导引 / DevEco导出 / OHPM推荐 |
| 2 | harmonycoder-snippets | 代码片段库 | 常用鸿蒙组件模板一键插入 | ✅ | ✅ | 156 KB | 分类管理 / 代码预览 / 一键复制 |

> **总计**: 2 款 APP，总 HAP 体积 548 KB，编译 + 签名 100% 通过。

### 核心能力

- **代码生成 (enableCodeGen)**：自然语言 → ArkTS 代码，零 deprecated 警告
- **项目导引 (enableProjectGuide)**：从零搭建鸿蒙项目骨架，最佳实践自动注入
- **DevEco导出 (enableDevecoExport)**：生成的代码一键导出到 DevEco Studio 工程
- **OHPM推荐 (enableOhpmRecommend)**：内置 10 个三方库推荐引擎

### OHPM 三方库推荐引擎

| 序号 | 库名 | 用途 |
|------|------|------|
| 1 | axios | HTTP 网络请求 |
| 2 | pulltorefresh | 下拉刷新 |
| 3 | lottie | 动画渲染 |
| 4 | imageknife | 图片加载与缓存 |
| 5 | mp4parser | 视频解析 |
| 6 | crypto-js | 加密算法 |
| 7 | hamock | Mock 数据 |
| 8 | hypium | 测试框架 |
| 9 | aki | ArkTS ↔ Native 交互 |
| 10 | MMKV | 高性能 KV 存储 |

### 产品架构 — AI编程四层引擎

```
┌──────────────────────────────────────────┐
│  输入层：自然语言需求解析                   │
│  说需求，出代码 — 中英文混合输入理解          │
├──────────────────────────────────────────┤
│  生成层：AI 代码生成引擎                    │
│  需求 → ArkTS 代码 / 项目骨架 / 组件模板     │
├──────────────────────────────────────────┤
│  增强层：三方库推荐 + DevEco 集成            │
│  OHPM 引擎 + 一键导出 DevEco Studio 工程     │
├──────────────────────────────────────────┤
│  质量层：零警告编译保障                      │
│  warnings_policy: zero + Navigation API     │
└──────────────────────────────────────────┘
```

### Feature Flag 矩阵

| APP | enableCodeGen | enableProjectGuide | enableDevecoExport | enableOhpmRecommend | NavPathStack |
|-----|:---:|:---:|:---:|:---:|:---:|
| harmonycoder | ✅ | ✅ | ✅ | ✅ | ✅ |
| harmonycoder-snippets | — | — | — | — | ✅ |

---

## 三、智能体定位

> 依据《智能体APP设计指南》，HarmonyCoder 旗舰版嵌入**对话式智能体**，以全屏 IDE 风格提供流程自动化与问答辅助，详见产品蓝图 v2.0。

### 3.1 智能体矩阵

| APP | Agent 优先级 | 智能体类型 | 核心能力 |
|:---|:---|:---|:---|
| harmonycoder | **P0** | 对话式 · 流程自动化 + 问答 Agent | 自然语言 → ArkTS 代码生成 → 项目骨架搭建 → DevEco 一键导出 → OHPM 三方库推荐 → 编译错误诊断 |

### 3.2 Agent 交互入口

| 属性 | 规范 |
|:---|:---|
| **入口形态** | **对话式 · 全屏 IDE 风**——Agent 面板占据主体视图区，代码与对话同屏展示 |
| **设计风格** | 深色 IDE 风格（#1E1E1E 底色），代码高亮 + 行号 + 分屏布局 |
| **触发方式** | APP 启动即进入对话模式；支持 @ 指令快捷操作（@generate / @project / @debug） |
| **可见性规则** | 旗舰 harmonycoder 全时启用；snippets 为纯工具模式，不加载 Agent |
| **设计原则** | 对话即界面、代码即产物、全流程闭环 |

### 3.3 智能体设计原则

1. **对话驱动**: 用户通过自然语言描述需求，Agent 直接生成可编译的 ArkTS 代码
2. **IDE 体验**: 代码区支持语法高亮、行号、一键复制，与 DevEco Studio 体验衔接
3. **质量保障**: 所有生成代码通过 warnings_policy: zero 校验，零 deprecated 警告
4. **全流程闭环**: 需求 → 代码生成 → OHPM 依赖推荐 → DevEco 导出，一步到位

---

## 四、技术规格

### 4.1 编译环境（CLI 全自动流水线）

| 项目 | 值 |
|------|-----|
| 语言与框架 | ArkTS strict mode · ArkUI Stage 模型 |
| 路由方案 | Navigation + NavPathStack（已迁移，零 deprecated 警告） |
| compileSdkVersion | 26.0.0 |
| compatibleSdkVersion | 6.1.1(24) |
| 编译工具 | hvigorw.bat v6.26.1 · DevEco Studio 26.0 |
| PREFLIGHT | 8 项自动检查 · 品牌级 -BrandPrefix 过滤 |

### 4.2 公共内核 (common/) — 22 个源文件

| 模块 | 文件数 | 内容 |
|------|--------|------|
| 组件库 | 12 | HButton, HCard, HConfirmDialog, HEmptyState, HFAB, HFormItem, HNavBar, HProgressBar, HSearchBar, HTag, HTagGroup, HToast |
| 工具 | 5 | date.ts, debounce.ts, format.ts, id.ts, validate.ts |
| 存储层 | 2 | storageService.ts (泛型 CRUD), keys.ts |
| 主题 | 1 | tokens.ts (Design Token) |
| 算法 | 2 | 代码质量分析 / 依赖检测 |

### 4.3 Navigation API 迁移（里程碑）

| 页面 | 旧路由 (router) | 新路由 (NavPathStack) | 状态 |
|------|----------------|----------------------|------|
| 主页 | router.pushUrl | NavPathStack.pushPathByName | ✅ |
| 代码生成 | router.pushUrl | NavPathStack.pushPathByName | ✅ |
| 项目导引 | router.pushUrl | NavPathStack.pushPathByName | ✅ |
| OHPM 推荐 | router.pushUrl | NavPathStack.pushPathByName | ✅ |
| DevEco 导出 | router.pushUrl | NavPathStack.pushPathByName | ✅ |

### 4.4 常见编译问题速查

| 错误码 | 症状 | 修复 |
|--------|------|------|
| 00303096 | mock 无效路径 | 重命名 mock → mock_disabled |
| 00303038 | main_pages schema 失败 | `"pages" → "src"` |
| 00303027 | modelVersion 不一致 | 统一 26.0.0 |
| 11203005 | float.json 空节点 | 补占位项 |
| 11211120 | $media 缺失 | 创建图标资源 |
| 10605071/29/01 | bracket notation | class + dot notation |

---

## 五、运营数据（占位）

> HarmonyCoder 尚未上架鸿蒙应用商店。

| 指标 | 当前 | Q3 目标 | Q4 目标 |
|------|------|---------|---------|
| 上架数 | 0/2 | 2/2 | 2/2 |
| 下载量 | — | 5,000+ | 20,000+ |
| 日活 (DAU) | — | 500+ | 2,000+ |
| 评分 | — | 4.5+ ★ | 4.7+ ★ |
| 月收入 | — | ¥10,000+ | ¥30,000+ |
| 崩溃率 | — | < 0.3% | < 0.1% |
| 代码生成准确率 | — | 90%+ | 95%+ |

---

## 六、发展规划

### 6.1 里程碑时间线

| 里程碑 | 内容 | 时间 |
|--------|------|------|
| M1 ✅ | 旗舰版 + 代码片段库 编译+签名+CI 首跑 · 零警告达标 | 2026-07-08 |
| M2 ✅ | 真机部署验证 · 冷启动 <1.5s（DevEco 6.1 + devecocli 全自动流水线） | 2026-07-15 |
| M3 | 鸿蒙应用商店上架审核 | 2026-08-01 |
| M4 | 多语言支持（英文 → 日文 / 韩文）| 2026-09-01 |
| M5 | 模板市场上线 · 社区贡献版 | 2026-10-01 |
| M6 | 云端同步 + 团队协作版 | 2026-12-01 |

### 6.2 1→N 扩展路径

#### 📦 第一阶段：旗舰打磨（Q3 2026）
- 用户反馈闭环：收集首批开发者反馈，迭代代码生成质量
- ASO 优化：关键词覆盖鸿蒙开发者搜索场景
- 崩溃率优化：目标 < 0.1%

#### 📦 第二阶段：能力扩展（Q4 2026）
- **多语言支持**：ArkTS 代码注释英文化 → 日文 / 韩文生成
- **模板市场**：社区贡献的项目模板（电商 / 社交 / 工具类）
- **代码片段库**：常用鸿蒙组件模板一键插入

#### 📦 第三阶段：生态构建（2027 H1）
- **云端同步**：跨设备代码片段同步（手机 ↔ 平板 ↔ PC）
- **团队协作**：项目共享、Code Review 辅助
- **插件系统**：第三方开发者可扩展 OHPM 推荐引擎
- **多端适配**：平板 / 折叠屏专属布局

### 6.3 新能力立项评审 (5 维)

| 维度 | 评审问题 | 权重 |
|------|----------|------|
| 开发者价值 | 是否解决鸿蒙开发者的具体痛点？ | **高** |
| 技术深度 | 能否发挥 AI 代码生成的核心优势？ | **高** |
| 内核复用 | 能否复用 common/ 22 个文件？ | **高** |
| 竞品差异 | 鸿蒙生态是否有同类方案？ | 中 |
| 商业化 | 能否产生收入或用户增长？ | 中 |

---

## 七、营销素材

### 品牌口号

> **HarmonyCoder — 说需求，出代码。鸿蒙开发者的AI编程伙伴。**

### 视觉规范

| 元素 | 规范 |
|------|------|
| 应用图标 | 1024×1024 px · 紫色基调 (#7B2D8E) · 代码符号 |
| 商店截图 | 鸿蒙框架 × 5 张 · AI对话/代码生成/项目导引/OHPM推荐/DevEco导出 |
| 宣传横幅 | 1242×2688 px 竖版 · 紫色科技风 |
| 品牌 Logo | 中英文组合 · #7B2D8E 紫 · HC 字母标识 |

### ASO 关键词

| APP | 核心词 | 长尾词 |
|-----|--------|--------|
| harmonycoder | AI编程, 鸿蒙开发 | AI写代码, DevEco, ArkTS代码生成, OHPM, 鸿蒙AI, 代码助手, 编程伙伴, 鸿蒙APP开发 |

### 竞品对比

| 维度 | HarmonyCoder | GitHub Copilot | Cursor | 通义灵码 |
|------|:---:|:---:|:---:|:---:|
| 鸿蒙专属 | ✅ | ❌ | ❌ | ❌ |
| ArkTS 原生 | ✅ | 部分 | ❌ | ❌ |
| DevEco 集成 | ✅ | ❌ | ❌ | ❌ |
| OHPM 推荐 | ✅ | ❌ | ❌ | ❌ |
| 买断制 | ✅ ¥68 | ❌ 订阅 | ❌ 订阅 | ❌ 免费 |
| 离线可用 | 计划中 | ❌ | ❌ | ❌ |

---

## 八、附录

### 8.1 关键路径

| 项目 | 路径 |
|------|------|
| 项目根 | `D:\92_products\SPDT-001_Harmony\` |
| APP 目录 | `apps\harmonycoder\` |
| 公共内核 | `common\` |
| CI 流水线 | `ci\pipeline.yaml` |
| 品牌手册 | `docs\品牌手册_HarmonyCoder.md` |

### 8.2 OMAS 治理

| 属性 | 值 |
|------|-----|
| SPDT | SPDT-001 |
| HDT | HDT-001-HC |
| 品类 | AI编程伙伴（旗舰） |
| 质量策略 | warnings_policy: zero |
| 品牌色 | #7B2D8E 紫 |
| 管理模型 | 1→1（质量优先） |

### 8.3 关联文档

- README.md · 项目总览
- PREFLIGHT 检查清单
- 编译问题手册 v2
- CI 流水线配置
- OMAS 治理体系文档

### 8.4 环境变量

| 变量 | 值 |
|------|-----|
| OHOS_SDK_HOME | `DevEco Studio\sdk` |
| PATH | `+= tools\node` |

### 8.5 更新记录

| 日期 | 版本 | 变更 |
|:---|:---|:---|
| 2026-07-17 | v1.1 | 扩展至 2 款 APP（新增 harmonycoder-snippets 代码片段库）；真机部署验证通过（DevEco 6.1 + devecocli）；新增智能体定位章节 |
| 2026-07-07 | v1.0 | 初始版本，旗舰版编译+签名+CI 首跑 |

---

🏗️ 鸿蒙特使 · SPDT-001 | HarmonyCoder 品牌手册 v1.1 | 2026-07-17
