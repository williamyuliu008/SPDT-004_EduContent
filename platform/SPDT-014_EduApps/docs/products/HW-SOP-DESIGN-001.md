# 鸿蒙工坊 SOP 体系设计

> 编号：HW-SOP-DESIGN-001 | 版本：v1.0 | 2026-06-18
> 借鉴：CDO-DESIGN-001 设计内阁 + UIUX_design SOP
> 负责人：模块库管理

---

## 一、借鉴分析

### 1.1 设计内阁 SOP 的核心模式

| 模式 | 说明 | 鸿蒙工坊对应 |
|------|------|------------|
| **原子架构**（9 种） | 所有复杂架构可分解为 ≤9 种不可再分解的结构本质 | **原子页面模式**（6 种）：List / Detail / Form / Dashboard / Tool / Wizard |
| **Golden Tests** | 15 场景基线验证，保证每次变更不退化 | **ArkTS 编译 Golden Tests**：15 个标准页面模式的编译基线 |
| **知识库分层** | 决策记录 / 复盘报告 / 经验教训 / 情报 | **Dev Recipes**：编译错误速查 / 组件 props 命名规范 / 常见坑 |
| **版本演进** | v3.0 → v4.0 → v5.0，每版有 retrospective | **v1.0**（当前）→ 每次大项目后迭代 |
| **ICM 请求系统** | 标准化的需求接收格式 | **MKT 下单格式**：需求文档模板 |

### 1.2 UIUX SOP 的核心模式

| 模式 | 说明 | 鸿蒙工坊对应 |
|------|------|------------|
| **Golden Test Suite**（12 场景） | 布局/风格/领域/异常全覆盖 | **App Template Suite**：ThinkKit / RhythmLife / CraftsmanUtils / Gaokao 四条赛道模板 |
| **Recipe 系统** | 可复用的解决方案片段 | **Component Recipes**：HNavBar 用法 / HProgressBar 用法 / 页面切换模式 |
| **Case 库** | 已交付项目的验证记录 | **Project Case 库**：5 个 App 的编译/运行/签名记录 |
| **四维投影** (dims.json) | 功能语义 × 用户角色 × 信息密度 × 风险等级 | **App Profile**：赛道 × 页面数 × 复杂度 × 网络需求 |
| **版本化 SOP** | v0.1 → v1.0 → v2.0，每版能力指标量化 | **能力基线量化**：组件数 / 模板数 / 编译通过率 |

### 1.3 共同基因

```
治理层(L0) → SOP层(L1) → 项目层(L2) → 知识层(L3) → 资源层(L4) → 运营层(L5)
```

鸿蒙工坊已经天然具备这个结构——只需要显式化、版本化。

---

## 二、鸿蒙工坊 SOP 体系设计

### 目录结构

```
D:\9_infra\harmony_workshop\
├── _00_governance/        ← 治理层（新增）
│   ├── 00_工坊愿景.md
│   ├── 01_工坊章程.yaml
│   ├── 02_交付管理办法.md
│   ├── 03_质量门禁.md
│   └── 04_内阁协作协议.md      ← 与 MKT/PV/KG/DESIGN 的握手协议
│
├── _01_sop/               ← SOP 层（新增，取代目前的 SOP.md）
│   ├── SOP_INDEX.yaml          ← SOP 版本目录
│   ├── SOP_新项目启动.md        ← 6 步启动流程
│   ├── SOP_页面开发.md          ← mock→UI→编译→验证
│   ├── SOP_组件开发.md          ← App内验证→提入common→barrel export
│   ├── SOP_API对接.md           ← HTTP层→mock/真实切换→联调
│   ├── SOP_签名打包.md          ← DevEco自动签名→真机安装
│   ├── SOP_错误排障.md          ← 常见错误速查表
│   └── SOP_ArkTS铁律.md         ← 禁止事项 + 正确做法
│
├── _02_templates/         ← 模板层（重命名现有 templates/）
│   ├── app-templates/          ← ThinkKit/RhythmLife/CraftsmanUtils/Gaokao 赛道模板
│   ├── page-patterns/          ← 6 种原子页面模式骨架
│   │   ├── pattern-list.ets
│   │   ├── pattern-detail.ets
│   │   ├── pattern-form.ets
│   │   ├── pattern-dashboard.ets
│   │   ├── pattern-tool.ets
│   │   └── pattern-wizard.ets
│   └── golden-tests/           ← 15 个编译基线页面
│       └── GOLDEN_TESTS.yaml
│
├── _03_knowledge/         ← 知识层（新增）
│   ├── recipes/                ← 可复用解决方案
│   │   ├── RECIPE_navbar_usage.md
│   │   ├── RECIPE_page_switch.md
│   │   ├── RECIPE_progress_usage.md
│   │   └── RECIPE_http_setup.md
│   ├── lessons/                ← 经验教训
│   │   ├── LESSON_sdk_version_mismatch.md
│   │   ├── LESSON_emulator_http_bug.md
│   │   ├── LESSON_prop_name_conflict.md
│   │   └── LESSON_cli_vs_deveco_build.md
│   ├── decisions/              ← 架构决策记录
│   │   └── DEC-20260617-001_use_builder_for_nav.md
│   └── intel/                  ← 外部情报
│       └── INTEL_api26_break_changes.md
│
├── _04_projects/          ← 项目层（新增）
│   ├── INDEX.yaml              ← 项目清单
│   ├── craftsman-utils/
│   ├── thinkkit-flashcard/
│   ├── thinkkit-zknote/
│   ├── rhythm-habit/
│   └── gaokao-agent/
│       └── PROJECT_CARD.yaml   ← 每项目一张卡片
│
├── _05_ops/               ← 运营层（新增）
│   ├── daily/                  ← 日报模板
│   ├── weekly/                 ← 周报模板
│   └── build_status/           ← 编译状态仪表盘
│       └── BUILD_DASHBOARD.yaml
│
├── common/               ← 公共内核（现有）
├── apps/                 ← App 源码（现有）
├── docs/                 ← 文档（现有）
└── scripts/              ← 工具脚本（现有）
```

### 核心机制：把开发变成"选择题"

借鉴设计 SOP 的核心理念——**"把设计变成选择题"**。在鸿蒙开发中对应：

```
设计 SOP:  需求 → 原子架构匹配 → 架构模板 → 生成
UIUX SOP:  需求 → 功能语义投影 → 布局/风格锚定 → 生成

鸿蒙 SOP: 需求 → 赛道/模式匹配 → App模板 → 注入组件 → 编译 → 交付
          └─ 选择题 ─┘  └─── 选择题 ───┘
```

具体化为三步选择：

**第 1 步：选赛道模板**（5 选 1）
- ThinkKit → 知识管理类（列表+详情+闪卡）
- RhythmLife → 习惯追踪类（列表+打卡+统计）
- CraftsmanUtils → 工具矩阵类（网格+独立工具页）
- Gaokao → 教育辅导类（标签导航+Mock数据+HTTP）
- Custom → 自定义

**第 2 步：选页面模式**（每个页面 6 选 1）
- List → HCard + HSearchBar + HEmptyState
- Detail → HNavBar + 内容区 + 操作按钮
- Form → HFormItem + HButton + 校验
- Dashboard → KPI卡片 + 图表 + 列表
- Tool → 输入区 + 处理按钮 + 输出区
- Wizard → 步骤导航 + 进度条 + 分步内容

**第 3 步：注入组件**（从 13 个 common/ 组件中按需选取）
- 导航：HNavBar
- 内容：HCard, HTag, HTagGroup
- 输入：HFormItem, HSearchBar
- 展示：HProgressBar, HRadarChart, HEmptyState
- 操作：HButton, HFAB, HConfirmDialog
- 反馈：HToast

### Golden Tests 设计

```
GOLDEN_TESTS.yaml:
  - 编译基线:
    - GT-001: 空项目编译通过
    - GT-002: 含 common/ 的项目编译通过
    - GT-003: 使用所有 13 个组件的页面编译通过
    - GT-004: 含 Canvas 组件的页面编译通过
    - GT-005: 含 HTTP 层的页面编译通过
  - UI 基线:
    - GT-010: 列表页渲染（卡片+空状态+FAB）
    - GT-011: 表单页渲染（必填+校验+错误提示）
    - GT-012: Dashboard渲染（KPI卡片+柱状图+进度条）
    - GT-013: 标签导航渲染（5标签+页面切换）
    - GT-014: 深色模式切换正常
  - 交付基线:
    - GT-020: HAP 文件生成
    - GT-021: 签名有效
    - GT-022: 模拟器安装成功
    - GT-023: App 启动后 3 秒内首屏渲染
```

### Project Card 格式

```yaml
# _04_projects/gaokao-agent/PROJECT_CARD.yaml
project_id: "PP-20260617-002"
name: "GaokaoAgent"
赛道: "Gaokao"
页面数: 5
组件使用: [HNavBar, HRadarChart, HTagGroup]
API端点: 7
编译状态: "PASS"
模拟器验证: "PASS"
真机验证: "PENDING"
上架状态: "PENDING"
数据来源: "交付内阁 PV/DLV"
```

### 版本演进路线

```
v1.0 (当前) — 6原子页面 + 3步选择法 + Golden Tests
    │
    ▼ 基于 GaokaoAgent + 4 App 经验
v1.1 — 加入 API 联调自动化 + 真机测试 SOP
    │
    ▼ 基于后续项目经验
v1.2 — 加入用户体验评估量表 + A/B 测试模式
    │
    ▼ 规模化
v2.0 — 全自动脚手架到上架 + 多内阁协同编排
```

---

## 三、与现有内阁的协作协议

| 内阁 | 输入给鸿蒙工坊 | 鸿蒙工坊输出 |
|------|-------------|------------|
| **MKT** | 需求文档（赛道、目标用户、功能清单） | 可运行的 App + 上架素材 |
| **PV/DLV** | 后端 API + 知识底座 + domain_profile | 对接好的前端 + API 契约反馈 |
| **KG** | 知识 Schema + 题库数据 | 数据模型适配 + 渲染逻辑 |
| **DESIGN** | 原子架构建议 + 集群设计 | ArkTS 实现 + 编译验证反馈 |

---

## 四、能力基线

| 指标 | v1.0 |
|------|------|
| 原子页面模式 | 6（List/Detail/Form/Dashboard/Tool/Wizard） |
| 赛道模板 | 4（ThinkKit/RhythmLife/CraftsmanUtils/Gaokao） |
| Common 组件 | 13（含 HRadarChart） |
| Golden Tests | 15（编译 5 + UI 5 + 交付 5） |
| Recipes（经验配方） | 8 |
| Lessons（教训库） | 4 |
| 已验证 App | 5 |
| 编译通过率 | 100%（最终态） |
