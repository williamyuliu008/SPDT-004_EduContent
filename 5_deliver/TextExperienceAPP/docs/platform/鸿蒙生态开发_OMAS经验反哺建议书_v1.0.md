# 鸿蒙生态开发 · OMAS 经验反哺建议书 v1.0

> 来源 SPDT-001 鸿蒙生态开发实战 | 对标 OMAS架构优化建议书 v2.1 格式  
> 版本 v1.0 | 2026-07-10 | 鸿蒙特使 (agent-e926h)  
> 提交 OMAS 理事会及对应 Cell 维护方

**背景：** SPDT-001 在 2 天窗口期内完成了从 13→29 款 APP、模板自动化、品牌管理、MAC 市场调研、DevEco 版本迁移等全链路实战，识别出 5 类可迁移至 OMAS 平台的能力模块。

| 指标 | 数值 |
|:---|:---|
| 可迁移模块数 | 5 个（SDC×2 / OGC×1 / MAC×1 / Governance×1） |
| 验证规模 | 29 款 APP、5 品牌、22 项 PREFLIGHT 检查 |
| 涉及 Cell | 4 个（SDC、OGC、MAC、Governance） |
| 与其他 SPDT 的协同 | 3 个交叉赋能方向 |

---

## 一、项目定位与 OMAS 关系

SPDT-001（鸿蒙生态开发）是 OMAS 治理体系下第一个大规模品牌管理实践。其核心工程模式——"common/ 内核复用 + 模板自动化 + 品牌两级治理 + 批量流水线"——为 OMAS 提供了独特的"工程自动化"视角，与 SPDT-002/003 的"数据管道/内容生产"视角形成互补。

### 1.1 与已有 Cell 的映射

| SPDT-001 能力 | 对标 Cell | 重合度 | 说明 |
|:---|:---|:---|:---|
| init-app.ps1 模板自动化 | **SDC** | 高 | 与 SDC-1 Pipeline Scheduler 互补，提供"项目骨架生成"的增量能力 |
| PREFLIGHT 8 项检查 | **OGC** | 高 | 品牌色/代码污染/API兼容的自动检查，与 OGC 质量门禁对齐 |
| MAC 市场机会扫描 | **MAC** | 中 | 20品类鸿蒙空白机会扫描方法论 |
| 品牌两级治理 | **Governance** | 中 | SPDT→品牌子PDT 的实战治理模板 |
| 批量编译+签名流水线 | **SDC** | 中 | hvigorw CLI 5阶段CI |

---

## 二、可迁移模块详析

### 2.1 SDC-3：项目骨架生成器（init-app.ps1）

**来源：** `scripts/init-app.ps1` + `templates/base/`

**当前状态：** 一键创建新 APP，自动完成：模板 fork → 配置占位替换 → 品牌色注入 → string.json 生成 → sign-all 注册 → PREFLIGHT 验证 → 编译。29 次验证，零手动修复。

```
init-app.ps1 -Name "app-name" -Brand "ThinkKit" -Color "5B8C5A" -Desc "描述"
  └─ templates/base/ (49文件)
       ├─ build-profile.json5 (SDK版本自动适配)
       ├─ AppScope/app.json5 (bundleName自动生成)
       ├─ entry/src/main/ets/app.config.ts (品牌配置)
       ├─ entry/src/main/ets/pages/Index.ets (骨架页面)
       └─ signing/ (自动注册到sign-all.ps1)
```

**OMAS 迁移方案：**

| 维度 | 当前实现 | OMAS 泛化方向 |
|:---|:---|:---|
| 输入 | CLI参数 (Name/Brand/Color) | YAML/JSON 项目定义文件 |
| 模板引擎 | PowerShell 字符串替换 | Jinja2 或 Go template |
| 输出验证 | PREFLIGHT 8项自动检查 | OGC 质量门禁集成 |
| 注册 | sign-all.ps1 bundleMap | OMAS project registry API |

**代码量：** ~200 行 PowerShell，迁移为 Python 模块约 ~150 行。

**优先级：P0** — 低代码量、高复用度，是 SPDT-001 最显性的工程能力输出。

---

### 2.2 OGC-5：品牌级质量门禁（PREFLIGHT 框架）

**来源：** `ci/stages/preflight.ps1`

**当前状态：** 8 项自动检查，支持单品牌和全品牌扫描（-ScanAll），29 次验证，22/22 PASS。

```
检查项：
  1. build-profile.json5 — API版本兼容
  2. oh-package.json5 — modelVersion 一致性
  3. hvigor-config.json5 — modelVersion 一致性
  4. AppScope/app.json5 — bundleName 格式
  5. module.json5 — 存在且格式正确
  6. pages/ — 至少 1 个 .ets 文件
  7. brand color — 品牌色一致性
  8. cross-brand pollution — 跨品牌代码污染检测
```

**OMAS 迁移方案：**

| 维度 | 当前实现 | OMAS 泛化方向 |
|:---|:---|:---|
| 检查规则 | PowerShell 脚本内嵌 | YAML 规则文件（可扩展） |
| 品牌隔离 | import 语句扫描 | 通用模块依赖分析 |
| 颜色/命名 | 正则匹配 app.config.ts | Schema 验证 + lint rules |
| 执行模式 | CLI -ScanAll / -BrandPrefix | OGC 标准化审计 pipeline |

**核心创新：** "跨品牌代码污染检测"是 SPDT-001 独有的质量维度——通过扫描 import 语句检测品牌间代码引用，防止 ThinkKit 的组件被 Craftsman 误用。此模式可推广到任何需要模块边界隔离的 OMAS 项目。

**代码量：** ~150 行 PowerShell，迁移为 OGC 审计规则集约 80 行规则配置。

**优先级：P1** — 规则标准化工作量小，但需要 OGC 适配审计框架。

---

### 2.3 MAC-3：市场空白扫描器（鸿蒙机会扫描方法论）

**来源：** `docs/MAC_市场机会报告_2026-07-08.html`

**当前状态：** 20 品类 × 100+ APP 的鸿蒙 NEXT 空白机会扫描，产出 9 个 P0 机会（全部已立项）。

**方法论核心：**

```
iOS/Android热门APP → 鸿蒙应用商店对标 → 空白度评分
     ↓                      ↓                  ↓
  下载量>100万          有/弱/无竞争       三维评分:
  评分>4.0                               需求热度 × 空白度 × 技术可行性
```

**OMAS 迁移方案：**

| 维度 | 当前实现 | OMAS 泛化方向 |
|:---|:---|:---|
| 数据源 | iOS App Store / Google Play | 插件化数据源接口 |
| 分析维度 | 3维 (热度/空白/可行) | N维可配置 |
| 输出 | HTML 报告 + 优先级排序 | MAC 标准报告格式 |
| 自动化 | 半自动 (子Agent并行) | SDC Pipeline 调度 |

**代码量：** 方法论文档化为主，自动化实现约 200 行 Python。

**优先级：P1** — 方法论已验证，但跨品类推广需要适配不同市场的数据源。

---

### 2.4 Governance-1：品牌两级治理模板

**来源：** SPDT-001 治理实践（SPDT.yaml + MANAGEMENT.md + pdt-registry.yaml）

**当前状态：** SPDT → 5品牌子PDT 的两级管理体系，含生命周期/目录规范/协作规则/PREFLIGHT日检。

**核心设计：**

| 层级 | 文件 | 职责 |
|:---|:---|:---|
| SPDT | SPDT.yaml + MANAGEMENT.md | 品牌清单/KPI聚合/CI基础设施/资源配额 |
| 品牌PDT | pdt.yaml + PDT.yaml + README.md | APP全生命周期/品牌质量门禁/里程碑管理 |

**OMAS 迁移方案：**

| 维度 | 当前实现 | OMAS 泛化方向 |
|:---|:---|:---|
| 注册 | pdt.yaml v2 (last_active+priority) | OMAS governance/_template |
| 管理 | MANAGEMENT.md | OMAS governance 规范集 |
| 心跳 | registry_checker --touch | OMAS health-check 自动检测 |
| 目录 | SPDT-001_Harmony 结构 | OMAS 推荐目录规范 |

**优先级：P2** — MANAGEEMENT.md 和 SPDT.yaml 的模板化可复用到所有 SPDT。

---

### 2.5 SDC-4：批量编译签名流水线

**来源：** `build-all.ps1` + `sign-all.ps1` + `ci/pipeline.yaml`

**当前状态：** 5阶段CI流水线，支持按品牌触发，daily cron 8:00 自动执行。

**与已有 Cell 的关系：** 此模块与 SDC-1 Pipeline Scheduler 高度重叠，建议作为 SDC-1 的参考实现而非独立新增。

**优先级：P3** — SDC-1 已覆盖此能力，提供参考实现代码即可。

---

## 三、跨 SPDT 协同赋能

### 3.1 HarmonyCoder × OMAS SDC（P1）

HarmonyCoder 是鸿蒙端的 AI 编程产品。OMAS SDC 的 CodeGen+Review 管线可作为 HarmonyCoder 的后端引擎：

```
HarmonyCoder APP (ArkTS前端)
  └─ AI编程问答
       └─ OMAS SDC CodeGen (Generator)
       └─ OMAS OGC CodeReview (Critic)
       └─ OMAS KBC 代码片段库 (Knowledge Base)
```

### 3.2 GaokaoAgent × SPDT-002 KBC（P1）

SPDT-002 的实体提取+知识图谱能力可用于高考知识诊断：

```
GaokaoAgent 知识诊断模块
  └─ 试卷知识点提取
       └─ SPDT-002 KBC EntityExtractor (NER+实体解析)
       └─ SPDT-002 KBC KnowledgeGraph (知识盲区检测)
```

### 3.3 ThinkKit × SPDT-003 CMC（P2）

SPDT-003 的约束生成管道可用于 ThinkKit 教育内容视频化：

```
ThinkKit 闪卡/笔记
  └─ CMC 布局约束引擎 (10种布局)
  └─ CMC TTS合成管道
  └─ 输出: AI教学视频 (MP4)
```

---

## 四、实施路线建议

| 阶段 | 时间 | 内容 | 涉及 Cell | 参考来源 |
|:---|:---|:---|:---|:---|
| **P0-1** | 第1周 | SDC-3 项目骨架生成器迁移：init-app.ps1 → Python 模块，集成 YAML 项目定义 + OGC 质量门禁 | SDC, OGC | 本文 §2.1 |
| **P0-2** | 第1-2周 | OGC-5 品牌质量门禁标准化：PREFLIGHT 规则 → YAML 配置，通用模块边界隔离检测 | OGC | 本文 §2.2 |
| **P1-1** | 第2周 | MAC-3 市场扫描器文档化 + 接口设计 | MAC | 本文 §2.3 |
| **P1-2** | 第2-3周 | HarmonyCoder × SDC 原型：harmonycoder APP 接入 OMAS CodeGen | SDC, HarmonyCoder | 本文 §3.1 |
| **P1-3** | 第3周 | GaokaoAgent × KBC 试点：高考知识点 → 知识图谱映射 | KBC, GaokaoAgent | 本文 §3.2 |
| **P2-1** | 第4周 | Governance-1 治理模板标准化 | Governance | 本文 §2.4 |
| **P2-2** | 第5周 | ThinkKit × CMC 内容视频化 MVP | CMC, ThinkKit | 本文 §3.3 |

### 分阶段风险控制

| 阶段 | 风险 | 缓解 |
|:---|:---|:---|
| P0-1 | init-app.ps1 的 PowerShell 特性 Python 难以完全复现 | 先做核心功能（模板渲染+占位替换），边缘功能（sign-all注册）用回调接口 |
| P0-2 | PREFLIGHT 规则高度绑定 ArkTS/HarmonyOS 生态 | 设计为"规则集插件"模式，各 SPDT 可定义自己的规则 |
| P1-2 | HarmonyCoder APP 当前为骨架，需要先补 API 调用功能 | 先做 OMAS API 的 mock 层，验证交互流程后再接真实后端 |

---

## 五、附录：SPDT-001 核心数字

| 指标 | 数值 |
|:---|:---|
| 运行窗口 | 2026-07-07 → 2026-07-09（~2天） |
| APP 增长 | 13 → 29（+123%） |
| 品牌数 | 5 |
| PREFLIGHT 通过率 | 100%（29/29） |
| 真机部署 | DevEco 5.0.9 通路打通 |
| 自动化工具 | init-app.ps1 / build-all.ps1 / sign-all.ps1 / preflight.ps1 |
| CI cron | 每日 8:00 CST 自动 BUILD+SIGN+REPORT |
| 品牌手册 | 5品牌 × 2格式 = 10份 |
| MAC 调研 | 20品类 × 100+APP |

---

> 🏗️ 鸿蒙特使 · SPDT-001 | 2026-07-10 | 提交 OMAS 理事会
