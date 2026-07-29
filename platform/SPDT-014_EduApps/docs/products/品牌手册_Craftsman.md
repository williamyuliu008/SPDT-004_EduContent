# Craftsman 品牌手册

> 版本: v1.1 | 更新: 2026-07-17 | 隶属: SPDT-001 鸿蒙生态开发
> 品牌色: #E87A2A 工匠橙 | OMAS 注册: HDT-001-CM

---

## 一、品牌定位

### 1.1 品牌标识

| 项 | 值 |
|:---|:---|
| 品牌名 | **Craftsman** |
| 中文释义 | 工匠 / 手艺人 → 开发者工具套件 |
| 品牌色 | <span style="display:inline-block;width:14px;height:14px;background:#E87A2A;border-radius:2px;vertical-align:middle;"></span> `#E87A2A` 工匠橙 |
| 设计语言 | 工具感 · 高效 · 硬核 · 专业 |
| Slogan | _为鸿蒙开发者锻造利器_ |
| 商标状态 | 待注册 |

### 1.2 价值主张

Craftsman 是一套**开发者工具矩阵**——覆盖鸿蒙 NEXT 开发全流程：组件速查、包管理、工具集、代码增强，每款 APP 专注单一开发场景、零上下文切换、本地即时响应。

开发者不需要在「功能臃肿的超级 IDE」和「功能残缺的零散插件」之间妥协：**10 个工具各司其职，共同内核保证体验一致**。

### 1.3 目标用户画像

| 维度 | 描述 |
|:---|:---|
| 核心用户 | 鸿蒙 NEXT 开发者（ArkTS / ArkUI 栈） |
| 使用场景 | 组件查阅、三方库发现、开发工具箱、API 调试 |
| 设备环境 | 鸿蒙 NEXT 手机 + 平板（移动端开发辅助） |
| 付费意愿 | 买断制为主，单款 ¥12-30 |

### 1.4 差异化定位

| 对比维度 | Craftsman | 传统 IDE 插件 | 在线工具站 |
|:---|:---|:---|:---|
| 产品形态 | 独立工具矩阵 | IDE 内嵌 | 网页端 |
| 即时性 | 本地即时响应 | 依赖 IDE 启动 | 需网络 |
| 内核复用 | common/ 22 文件共享 | 无 | 无 |
| 品牌一致性 | 统一 Design Token | 碎片化 | 碎片化 |
| 鸿蒙原生 | ArkUI Stage 模型 | 非原生 | 非原生 |

---

## 二、产品矩阵

### 2.1 APP 清单

| # | APP | 中文名 | 功能 | 编译 | 签名 | HAP | 特色能力 |
|:---|:---|:---|:---|:---|:---|:---|:---|
| 1 | craftsman-arkui | ArkUI组件速查 | 鸿蒙ArkUI组件示例与参考 | ✅ | ✅ | 161 KB | 组件代码 / 交互预览 / 属性速查 |
| 2 | craftsman-ohpm | OHPM三方库 | 鸿蒙三方库发现工具 | ✅ | ✅ | 156 KB | 库搜索 / 版本比对 / 依赖分析 |
| 3 | craftsman-utils | 开发者工具箱v1 | OHPM三方库推荐 | ✅ | ✅ | 63 KB | 智能推荐 / 库评分 |
| 4 | craftsman-utils-v2 | 开发者工具箱v2 | 开发者工具箱增强版 | ✅ | ✅ | 96 KB | 多工具集成 / 快捷操作 |
| 5 | craftsman-scanner | 代码扫描器 | 代码质量扫描与问题定位 | ✅ | ✅ | 132 KB | 实时扫描 / 问题分类 |
| 6 | craftsman-translate | 开发翻译助手 | 技术文档翻译与术语查询 | ✅ | ✅ | 110 KB | 术语库 / 多语支持 |
| 7 | craftsman-clipboard | 代码剪贴板 | 代码片段收藏与快捷粘贴 | ✅ | ✅ | 88 KB | 分类管理 / 语法高亮 |
| 8 | craftsman-code-editor | 轻量代码编辑器 | 移动端 ArkTS 代码编辑 | ✅ | ✅ | 205 KB | 语法高亮 / 自动补全 / AI 补全 |
| 9 | craftsman-image-tool | 图片工具 | 开发用图片处理与格式转换 | ✅ | ✅ | 145 KB | 格式转换 / 尺寸调整 |
| 10 | craftsman-api-tester | API 测试工具 | REST API 调试与 Mock | ✅ | ✅ | 178 KB | 请求构建 / 响应分析 / AI 测试生成 |

> **总计**: 10 款 APP，总 HAP 体积 1,334 KB，编译 + 签名 100% 通过。目标扩展至 20 款。

### 2.2 产品架构

```
Craftsman 开发者工具矩阵
│
├─ 🔍 查询层 ──────────────────────────
│   └── arkui        ArkUI组件速查（快速查阅官方组件文档与示例）
│
├─ 📦 包管理层 ──────────────────────────
│   └── ohpm         OHPM三方库（发现、比对、分析鸿蒙三方库）
│
├─ 🧰 工具层 ──────────────────────────
│   ├── utils        开发者工具箱v1（智能推荐三方库）
│   ├── utils-v2     开发者工具箱v2（增强版：多工具一键调用）
│   ├── scanner      代码扫描器（质量扫描与问题定位）
│   ├── translate    开发翻译助手（技术文档翻译）
│   ├── clipboard    代码剪贴板（片段收藏与粘贴）
│   └── image-tool   图片工具（格式转换与处理）
│
├─ 🤖 智能层 ──────────────────────────
│   ├── code-editor  轻量代码编辑器（AI 补全）
│   └── api-tester   API 测试工具（AI 测试生成）
│
└─ 🚀 扩展层（规划中） ────────────────
    ├── perf-analyzer 性能分析
    ├── layout-preview 布局预览
    ├── i18n-helper  国际化助手
    ├── a11y-checker 无障碍检查
    ├── snippet-mgr  代码片段管理
    ├── arch-viz     架构可视化
    ├── code-review  代码审查助手
    ├── db-browser   数据库浏览器
    └── asset-gen    资源生成器
```

五层架构：**查询 → 包管理 → 工具集成 → 智能增强 → 专业扩展**，每层对应不同开发阶段需求，通过 common/ 内核保证体验一致。

### 2.3 Feature Flag 矩阵

| APP | enableComponentPreview | enablePackageSearch | enableToolIntegration | enableRecommendation | enableAIAssist | 其他 |
|:---|:---|:---|:---|:---|:---|:---|
| arkui | ✅ | — | — | — | — | 组件渲染 / 属性面板 |
| ohpm | — | ✅ | — | — | — | 库搜索 / 依赖图 |
| utils | — | — | ✅ | ✅ | — | 智能推荐引擎 |
| utils-v2 | — | — | ✅ | ✅ | — | 多工具面板 / 快捷入口 |
| scanner | — | — | ✅ | — | — | 实时扫描 |
| translate | — | — | ✅ | — | — | 术语库 |
| clipboard | — | — | ✅ | — | — | 语法高亮 |
| code-editor | — | — | ✅ | — | ✅ | AI 代码补全 |
| image-tool | — | — | ✅ | — | — | 格式转换 |
| api-tester | — | — | ✅ | — | ✅ | AI 测试生成 |

> utils-v2 和 code-editor 作为增强版/智能版承载了更多 UI 组件和 AI 能力。

### 2.4 定价体系

| 层级 | 范围 | 模式 | 建议价格 | 状态 |
|:---|:---|:---|:---|:---|
| 基础功能 | arkui / ohpm 基础查询 | 免费 | ¥0 | 已实现 |
| 高级功能 | utils / code-editor / api-tester 高级功能 | 买断制 | ¥12-30/款 | 待接入支付 |
| 套装 | Craftsman 十合一套装 | 买断制 | ¥88 (10 款) | 规划中 |

---

## 三、智能体定位

> 依据《智能体APP设计指南》，Craftsman 在代码编辑和 API 测试工具中嵌入**辅助型智能体**，以轻量级 AI 辅助提升开发效率。

### 3.1 智能体矩阵

| APP | Agent 优先级 | 智能体类型 | 核心能力 |
|:---|:---|:---|:---|
| craftsman-code-editor | **P2** | 辅助型 · 代码补全 Agent | 上下文感知代码补全 → 智能缩进 → 语法纠错 → 代码片段推荐 |
| craftsman-api-tester | **P2** | 辅助型 · 测试生成 Agent | 接口分析 → 测试用例自动生成 → 断言建议 → Mock 数据构造 |

### 3.2 Agent 交互入口

| 属性 | 规范 |
|:---|:---|
| **入口形态** | 工具栏内嵌**直角面板**，与编辑器/测试器无缝融合 |
| **设计风格** | 工具感 · 直角边框 · **暗色模式**（#1E1E1E 底色），匹配开发工具调性 |
| **触发方式** | 光标停顿 500ms 自动建议 / 快捷键 `Ctrl+Space` 手动唤起 |
| **可见性规则** | 仅在 code-editor 和 api-tester 中启用；其余纯查询/工具 APP 不加载 Agent 模块 |
| **设计原则** | 嵌入式辅助、低干扰、即时响应（< 300ms） |

### 3.3 智能体设计原则

1. **工具内嵌**: Agent 面板嵌入编辑器/测试器主体，不弹出独立浮层
2. **暗色优先**: 统一使用暗色模式，与开发者编辑器视觉一致
3. **即时反馈**: 代码补全建议 < 300ms，测试生成 < 2s
4. **可关闭**: 高级开发者可在设置中完全关闭 AI 辅助，回归纯工具模式

---

## 四、技术规格

### 4.1 SDK 与编译环境

| 项 | 值 |
|:---|:---|
| 语言 | ArkTS (TypeScript 超集，strict mode，禁止 `any`) |
| UI 框架 | ArkUI 声明式 (Stage 模型) |
| 状态管理 | @State / @Link / @Provide-@Consume |
| 路由 | Navigation + NavPathStack |
| targetSdkVersion | 26.0.0 |
| compatibleSdkVersion | 6.1.1(24) |
| 编译工具 | hvigorw.bat (v6.26.1) |
| 存储 | Preferences (本地 JSON) |

### 4.2 编译命令（CLI 全自动流水线）

```powershell
$env:OHOS_SDK_HOME = "D:\9_infra\DevEco Studio\sdk"
$env:PATH = "D:\9_infra\DevEco Studio\tools\node;$env:PATH"

# 单 APP
Push-Location "D:\92_products\SPDT-001_Harmony\apps\craftsman-arkui"
& "D:\9_infra\DevEco Studio\tools\hvigor\bin\hvigorw.bat" assembleHap
Pop-Location

# 品牌级批量编译
powershell -ExecutionPolicy Bypass -File "D:\92_products\SPDT-001_Harmony\build-all.ps1" -Brand craftsman
```

### 4.3 签名策略

- **开发阶段**: debug profile + 自建 cert chain
- **批量签名**: `sign-all.ps1` 自动识别 bundleName → 匹配对应 profile
- **签名状态**: 10/10 通过

### 4.4 公共内核 (common/)

Craftsman 10 款 APP 共享同一套 `common/` 内核（22 个源文件）：

| 模块 | 文件 | 说明 |
|:---|:---|:---|
| **组件** (12) | HButton, HCard, HConfirmDialog, HEmptyState, HFAB, HFormItem, HNavBar, HProgressBar, HSearchBar, HTag, HTagGroup, HToast | UI 组件库，品牌色 #E87A2A 统一注入 |
| **存储** (2) | storageService.ts, keys.ts | 泛型 CRUD，Preferences 封装 |
| **主题** (1) | tokens.ts | Design Token（品牌级 #E87A2A 工匠橙） |
| **工具** (5) | date.ts, debounce.ts, format.ts, id.ts, validate.ts | 日期/防抖/格式化/ID/校验 |
| **算法** (2) | sm2.ts, streak.ts | 通用算法工具（预留扩展） |

> 与 ThinkKit 共享 common/ 内核，通过 Design Token 切换驱动品牌差异化。

### 4.5 PREFLIGHT 检查项

Craftsman 特有 8 项自动检查，品牌级 `-BrandPrefix "craftsman-"` 过滤：

| 检查项 | 说明 |
|:---|:---|
| build-profile.json5 | API 24 兼容 |
| oh-package.json5 | modelVersion 26 |
| hvigor-config.json5 | modelVersion 26 |
| AppScope/app.json5 | bundleName 格式 `com.craftsman.*` |
| module.json5 | 存在且格式正确 |
| pages/ | 至少 1 个 .ets |
| **品牌色一致性** | 全局 Design Token 强制 #E87A2A |
| **ThinkKit 代码污染** | 禁止引用任何 `thinkkit-*` bundleName 或命名空间 |

> **品牌污染保护**: PREFLIGHT 阶段自动扫描全部 .ets/.ts/.json5，拦截跨品牌 `thinkkit-*` 字符串，确保 Craftsman 代码库纯净独立。

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
| — | 品牌色不一致 | Design Token 未注入 #E87A2A |

> 完整手册: [编译问题修复手册 v2](D:\92_products\SPDT-001_Harmony\编译问题修复手册 v2.md)

---

## 五、运营数据

> ⚠️ 以下为占位，当前 Craftsman 尚未上架鸿蒙应用商店。

| 指标 | 当前值 | 目标 (Q3) |
|:---|:---|:---|
| 上架数 | 0/10 | 10/10 |
| 下载量 | — | 8,000+ |
| 日活用户 (DAU) | — | 800+ |
| 评分 | — | 4.5+ ★ |
| 月收入 | — | ¥3,000+ |
| 崩溃率 | — | < 0.5% |
| 新增 APP | 10 | 14 (Q3 目标) |

---

## 六、发展规划

### 6.1 当前缺口

| 缺口 | 影响 | 优先级 |
|:---|:---|:---|
| 未上架应用商店 | 无真实开发者反馈 | P0 |
| 无自动化测试框架 | 回归依赖手工 | P2 |

### 6.2 10 款扩展路线图

从当前 "查询→包管理→工具集成" 三层，扩展至开发者全场景：

```
当前 4 款                           目标 20 款
─────────────────────────────────────────────
🔍 arkui            ──→ +layout-preview（布局预览）+i18n-helper（国际化助手）
📦 ohpm             ──→ +api-debug（API调试）+db-browser（数据库浏览器）
🧰 utils            ──→ +snippet-mgr（代码片段管理）+code-review（代码审查助手）
🚀 utils-v2         ──→ +perf-analyzer（性能分析）+a11y-checker（无障碍检查）
                      ──→ +arch-viz（架构可视化）+asset-gen（资源生成器）
```

| 批次 | APP | 功能 | 预计 HAP | 生成方式 |
|:---|:---|:---|:---|:---|
| 第 1 批 (7 月) | api-debug, perf-analyzer, layout-preview | API 调试 / 性能分析 / 布局预览 | 各 ~80-150 KB | 模板 fork |
| 第 2 批 (8 月) | i18n-helper, a11y-checker, snippet-mgr | 国际化 / 无障碍检查 / 代码片段 | 各 ~80-150 KB | 模板 fork |
| 第 3 批 (9 月) | arch-viz, code-review, db-browser, asset-gen | 架构可视化 / 代码审查 / 数据库浏览 / 资源生成 | 各 ~100-200 KB | 模板 fork + AI 补充 |

> 合计: 10 款新增 + 10 款已有 → 20 款目标。预计总 HAP 体积 ~2,500 KB。

### 6.3 新 APP 立项评审标准

| 维度 | 评审问题 | 权重 |
|:---|:---|:---|
| 场景匹配 | 是否填补鸿蒙开发流程中的真实痛点？ | 高 |
| 内核复用 | 能否用 common/ 现有组件覆盖 80%+ UI？ | 高 |
| 竞品缺口 | 鸿蒙生态中是否有同类开发者工具？ | 中 |
| AI 可达 | 代码生成率能否达到 85%+？ | 中 |
| 开发者痛点 | 是否能真正提升开发效率？ | 高 |

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
| M1: 首批 10 款全通 | 2026-07-08 | ✅ 完成 | 10/10 编译+签名 |
| M2: 真机部署验证 | 2026-07-12 | ✅ 完成 | 10/10 真机安装 + 冷启动 < 2s（DevEco 6.1 + devecocli 全自动流水线） |
| M3: 扩展第 1 批启动 | 2026-07-20 | ⏳ 规划 | 3 款新 APP 编译通过 |
| M4: 应用商店上架 | 2026-08-01 | ⏳ 规划 | 10 款提交审核 |
| M5: 第 2 批交付 | 2026-08-20 | ⏳ 规划 | 13/13 编译+签名 |
| M6: 20 款全部交付 | 2026-10-15 | ⏳ 规划 | 20/20 编译+签名+上架 |

---

## 七、营销素材

### 6.1 品牌话术

**一句话介绍:**
> Craftsman —— 为鸿蒙开发者锻造利器，10 个独立工具覆盖全链路开发辅助。

**扩展介绍 (100 字):**
> Craftsman 是鸿蒙生态首套开发者工具矩阵。从 ArkUI 组件速查到 OHPM 三方库发现，从代码编辑器到 API 测试工具——10 款独立 APP 各司其职，共享统一内核。本地即时响应，买断制，不订阅不套路。让开发者在手机端也能高效查阅、快速决策。锻造你自己的鸿蒙利器。

**品牌故事角度:**
> 「好工匠需要好工具。」Craftsman 的核心理念是：每个开发场景都值得一个专属工具——需要查组件时打开 ArkUI 速查，需要找三方库时打开 OHPM，需要效率工具时打开 Utility Toolbox。小而专，各司其职，这才是开发者工具该有的样子。

### 6.2 应用商店描述模板

```
## 概述
[APP 中文名] 是 Craftsman 开发者工具系列的一员——[一句话功能]。

## 核心功能
• [功能点 1]
• [功能点 2]
• [功能点 3]

## 为什么选择我们？
✅ 专注单一开发场景，零上下文切换
✅ 本地数据优先，即时响应无需联网
✅ 买断制，一次付费永久使用
✅ 鸿蒙 NEXT 原生，ArkUI Stage 模型

## Craftsman 系列
Craftsman 提供 10 款独立开发者工具：[列出其余 9 款名称]
```

### 6.3 截图与图标规范

| 项目 | 规范 |
|:---|:---|
| 应用图标 | 1024×1024 px，工匠橙基调，白色工具/扳手图标 |
| 商店截图 | 鸿蒙设备框架 × 5 张（首页 / 核心功能 1 / 核心功能 2 / 结果页 / 设置） |
| 宣传横幅 | 1242×2688 px (竖版) |
| 品牌 Logo | "Craftsman" + "工" 字形组合，工匠橙 #E87A2A |

### 6.4 ASO 关键词策略

| APP | 核心词 | 长尾词 |
|:---|:---|:---|
| arkui | ArkUI组件, 组件速查 | 鸿蒙UI组件示例, ArkTS组件参考, 鸿蒙开发 |
| ohpm | OHPM, 三方库 | 鸿蒙三方库, openHarmony包管理, 鸿蒙依赖 |
| utils | 开发者工具箱, 工具集 | 鸿蒙开发工具, 鸿蒙NEXT工具箱, ArkTS效率 |
| utils-v2 | 开发者工具箱Pro, 多功能工具 | 鸿蒙开发增强, 鸿蒙工具大全, 鸿蒙快捷操作 |
| scanner | 代码扫描, 质量检查 | 鸿蒙代码扫描, ArkTS质量检测, 代码审查 |
| translate | 开发翻译, 技术文档翻译 | 鸿蒙开发翻译, 多语支持, 术语查询 |
| clipboard | 代码剪贴板, 片段管理 | 鸿蒙代码收藏, 快速粘贴, 语法高亮 |
| code-editor | 代码编辑器, AI补全 | 鸿蒙移动IDE, ArkTS编辑, AI代码补全 |
| image-tool | 图片工具, 格式转换 | 开发图片处理, 尺寸调整, 格式转换 |
| api-tester | API测试, 接口调试 | 鸿蒙API调试, REST测试, Mock数据 |

### 7.5 竞品参考 (鸿蒙生态)

> [待调研] 鸿蒙应用商店同类开发者工具产品清单、定价、评分对比。

---

## 八、附录

### 8.1 关键路径速查

```
项目根        D:\92_products\SPDT-001_Harmony\
Craftsman APP D:\92_products\SPDT-001_Harmony\apps\craftsman-*
公共内核      D:\92_products\SPDT-001_Harmony\common\
CI 流水线     D:\92_products\SPDT-001_Harmony\ci\
签名证书      D:\92_products\SPDT-001_Harmony\signing\profile-craftsman-*
品牌模板      D:\92_products\SPDT-001_Harmony\templates\base\
OMAS 注册     D:\6_agent_project\omas\pdt_registry\HDT-001-CM\
编译手册      D:\92_products\SPDT-001_Harmony\编译问题修复手册 v2.md
```

### 8.2 OMAS 治理信息

| 字段 | 值 |
|:---|:---|
| SPDT | SPDT-001 鸿蒙生态开发 |
| 子PDT ID | HDT-001-CM |
| 品类 | 开发者工具 |
| 负责人 | PL-craftsman |
| 质量策略 | warnings_policy: no_new |
| 目标总数 | 20 款 APP |
| 特有 PREFLIGHT | 无 ThinkKit 代码污染 + 品牌色一致性检查 |

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
| ThinkKit 品牌手册 | [D:\92_products\SPDT-001_Harmony\docs\品牌手册_ThinkKit.md](D:\92_products\SPDT-001_Harmony\docs\品牌手册_ThinkKit.md) |

### 8.4 更新记录

| 日期 | 版本 | 变更 |
|:---|:---|:---|
| 2026-07-17 | v1.1 | 扩展至 10 款 APP（新增 scanner/translate/clipboard/code-editor/image-tool/api-tester）；真机部署验证通过（DevEco 6.1 + devecocli）；新增智能体定位章节 |
| 2026-07-07 | v1.0 | 初始版本，覆盖 4 款 APP 全貌 + 10 款扩展路线图 |

---

> 🏗️ 鸿蒙特使 · SPDT-001 | Craftsman 品牌手册 v1.1
