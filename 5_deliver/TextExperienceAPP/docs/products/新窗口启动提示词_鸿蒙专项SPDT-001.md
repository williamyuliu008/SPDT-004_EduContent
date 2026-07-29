# 鸿蒙专项 SPDT-001 · 新窗口启动提示词

> 生成: 2026-07-07 13:52 CST | 更新: 2026-07-08 代码迁移 | 产出: KG Agent
> 用法: 在新 Agent 窗口中粘贴此文件全部内容作为第一条消息

---

## 启动步骤

1. 阅读项目 README: `D:\92_products\SPDT-001_Harmony\README.md`
2. 阅读交接文档: `D:\92_products\SPDT-001_Harmony\docs\工作交接_鸿蒙专项SPDT-001.md`
3. 运行全品牌预检:
   ```
   powershell -ExecutionPolicy Bypass -File "D:\92_products\SPDT-001_Harmony\ci\stages\preflight.ps1" -ScanAll
   ```
4. 确认 22/22 PASS 后，根据下方待办清单推进

---

## 一、项目定位

**SPDT-001 鸿蒙生态开发** — AI 驱动鸿蒙 NEXT 精品 App 矩阵

- 工作目录: `D:\92_products\SPDT-001_Harmony\`D:\92_products\SPDT-001_Harmony\`
- 战略: `common/` 内核复用 + AI 代码生成 80%+ → 年产 100+ 款 APP
- 治理: SPDT → 品牌子PDT 两级管理 (OMAS 注册: `D:\6_agent_project\omas\`)

## 二、品牌矩阵 (5 品牌, 22 APP)

| 品牌 | 品牌色 | APP 数 | 编译 | 签名 | 注册 ID |
|:---|:---|:---|:---|:---|:---|
| ThinkKit | #5B8C5A | 6 | ✅ 6/6 | ✅ 6/6 | HDT-001-TK |
| Craftsman | #E87A2A | 4 | ✅ 4/4 | ✅ 4/4 | HDT-001-CM |
| HarmonyCoder | #7B2D8E | 1 | ✅ 1/1 | ✅ 1/1 | HDT-001-HC |
| RhythmHabit | #3B82B0 | 1 | ✅ 1/1 | ✅ 1/1 | HDT-001-RH |
| GaokaoAgent | #C44536 | 1 | ✅ 1/1 | ✅ 1/1 | HDT-001-GK |

### APP 清单

```
thinkkit-*     : coach (228.8KB), flashcard (427.2), zknote (418.6),
                 mindmap (187.7), reader (110.8), quiz (134.9)
craftsman-*    : arkui (120), ohpm (114.7), utils (21.6), utils-v2 (96)
harmonycoder   : 392.2 KB
rhythm-habit   : 412.6 KB
gaokao-agent   : 288.8 KB
```

## 三、技术栈与规范

- **语言**: ArkTS (TypeScript 超集, strict mode, 禁止 any)
- **UI**: ArkUI 声明式 (Stage 模型)
- **路由**: Navigation + NavPathStack (**已从 router API 迁移**)
- **SDK**: 编译 API 26 → 真机兼容 API 24 (compatibleSdkVersion: `6.1.1(24)`)
- **签名**: 统一 debug profile + 自建 cert chain, `sign-all.ps1` 全自动
- **品牌隔离**: PREFLIGHT 自动检测跨品牌代码污染

## 四、编译环境

```powershell
$env:OHOS_SDK_HOME = "D:\9_infra\DevEco Studio\sdk"
$env:PATH = "D:\9_infra\DevEco Studio\tools\node;$env:PATH"

# 单 APP 编译
Push-Location "D:\92_products\SPDT-001_Harmony\apps\{appname}"
& "D:\9_infra\DevEco Studio\tools\hvigor\bin\hvigorw.bat" assembleHap
Pop-Location

# 批量编译
powershell -ExecutionPolicy Bypass -File "D:\92_products\SPDT-001_Harmony\build-all.ps1" -All
```

## 五、CI 流水线 (5 阶段)

| 阶段 | 脚本 | 说明 |
|:---|:---|:---|
| PREFLIGHT | `ci/stages/preflight.ps1 -BrandPrefix "xxx-"` | 8 项完整性检查 |
| BUILD | `ci/stages/build.ps1 -BrandPrefix "xxx-"` | 品牌并行编译 |
| SIGN | `ci/stages/sign.ps1 -BrandPrefix "xxx-"` | hap-sign-tool.jar 签名 |
| DEPLOY | `ci/stages/deploy.ps1 -BrandPrefix "xxx-"` | hdc install + aa start |
| REPORT | `ci/stages/report.ps1 -BrandPrefix "xxx-"` | JSON/MD 统计报告 |

PREFLIGHT 还支持 `-ScanAll` 全品牌扫描。

## 六、编译问题修复速查

| 错误码 | 修复 |
|:---|:---|
| 00303096 | mock 目录 → 重命名 `mock_disabled` |
| 00303038 | `"pages"` → `"src"` (main_pages.json) |
| 00303034 | compileSdkVersion → 26.0.0 |
| 00303027 | modelVersion 统一 26.0.0 |
| 11203005 | float.json / element 空节点 → 补占位 |
| 11211120 | $media 缺失 → 创建图标资源 |
| 10605071/10605029/10505001 | `obj['field']` → class + dot notation |

> 完整手册: `D:\9_infra\harmony_workspace\编译问题修复手册 v2.md`

## 七、本轮会话完成的工作

1. **thinkkit-quiz 签名修复** — sign-all.ps1 增加 bundle 映射, HAP 165.9KB
2. **harmonycoder Navigation API 迁移** — 5 页面 router→NavPathStack, 零 deprecated 警告
3. **thinkkit-quiz 功能补全** — 骨架→完整测验 (10 题/计时/评分/解析)
4. **品牌扩展** — 新增 RhythmHabit (#3B82B0) + GaokaoAgent (#C44536) 子PDT
5. **CI 流水线** — 5 阶段脚本全部交付并验证
6. **SPDT 注册更新** — 品牌 3→5, KPI 更新
7. **PREFLIGHT 修复** — 支持 -ScanAll + 5 品牌自动识别

## 八、待办 (P3 战略层)

| 优先级 | 事项 |
|:---|:---|
| P3 | 真机部署验证 (需 API 24 真机连接) |
| P3 | ThinkKit 教育系列 15 款启动 (从品牌模板批量生成) |
| P3 | Craftsman 开发者工具扩展至 10 款 |
| P3 | GaokaoAgent 系列扩展: 志愿填报/分数查询/专业解读/刷题/历年真题 |
| P3 | daily cron 构建接入 (`ci/pipeline.yaml` cron: `0 8 * * *`) |
| P3 | harmonycoder 真机部署验证 |

## 九、关键路径速查

```
D:\92_products\SPDT-001_Harmony\                        # 项目根
D:\92_products\SPDT-001_Harmony\apps\                   # 22 APP 源码
D:\92_products\SPDT-001_Harmony\common\                 # 公共内核 (组件/存储/主题/工具/算法)
D:\92_products\SPDT-001_Harmony\templates\base\          # 标准化 APP 模板
D:\92_products\SPDT-001_Harmony\ci\                      # CI 流水线
D:\92_products\SPDT-001_Harmony\signing\                 # 签名证书
D:\92_products\SPDT-001_Harmony\docs\                    # 文档 (SOP/手册/报告)
D:\92_products\SPDT-001_Harmony\_archive_v1\             # 历史日志 + 归档
D:\6_agent_project\omas\spdt_registry\SPDT-001\      # SPDT 注册
D:\6_agent_project\omas\pdt_registry\HDT-001-{TK,CM,HC,RH,GK}\  # 品牌子PDT
D:\9_infra\DevEco Studio\                            # DevEco IDE
```

---

*将此文件全文粘贴到新 Agent 窗口即可继承完整上下文。*
