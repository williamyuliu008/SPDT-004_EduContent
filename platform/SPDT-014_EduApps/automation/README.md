# SPDT-001 自动化工作台

> 鸿蒙特使 🏗️ | agent-e926h | 2026-07-18 建立 | P0 执行: 2026-07-18 15:40

## 当前状态

| 指标 | 数值 | 变化 |
|:---|:---|:---|
| APP 总数 | 30 | — |
| 已签名 | 13 (43%) | — |
| 缺证书 | 17 | 待 batch-sync.bat |
| P0.2 批量部署 | 2/3 GaokaoAgent ✅ | gaokao-agent ArkTS 错误 |
| P0.3 旗舰冒烟 | 2/5 通过 | harmonycoder/rhythm 缺签名 |
| CI cron | 每日 8:00 CST | ✅ 已激活 |

## 目录

```
automation/
├── README.md                ← 本文件
├── smoke-test.py            ← 真机冒烟测试 (Python, AgentMode)
├── sync-signing.ps1         ← DevEco Studio 批量 Sync 签名注入
├── batch-sync.bat           ← 手动辅助: 17 APP 逐次打开 Sync
├── main.py                  ← 已有: 自动化主入口
├── config/                  ← 已有: 自动化配置
├── testcases/               ← 已有: Hypium 测试用例
├── docs/                    ← 自动化文档
├── reports/                 ← CI 报告输出
└── workdir/                 ← 临时工作文件
```

## 外部脚本

| 脚本 | 路径 | 用途 | 状态 |
|:---|:---|:---|:---|
| build-all.py | `..\apps\build-all.py` | 批量编译+签名+部署 30 APP | ✅ 已验证 |
| build_any.py | `..\apps\build_any.py` | 单 APP 编译+部署 | ✅ 保留 |
| init-app.ps1 | `..\scripts\init-app.ps1` | 一键创建 APP v2 | ✅ 增强 |
| inject-signing.ps1 | `..\scripts\inject-signing.ps1` | 批量签名注入 | ⚠️ CLI 限制 |
| ci-daily.ps1 | `..\scripts\ci-daily.ps1` | 每日 CI 全流程 | ✅ |
| deploy-all.ps1 | `..\scripts\deploy-all.ps1` | 批量部署 | ✅ |
| preflight.ps1 | `..\ci\stages\preflight.ps1` | 项目完整性检查 | ✅ |

## 快速命令卡

```powershell
# === 状态扫描 ===
python ..\apps\build-all.py --report-only

# === 批量编译 ===
python ..\apps\build-all.py --parallel 4                    # 全部已签名APP
python ..\apps\build-all.py --brand gaokao --deploy         # 单品牌+部署
python ..\apps\build-all.py --brand gaokao --app gaokao-language gaokao-volunteer --deploy

# === 签名管理 ===
..\scripts\inject-signing.ps1 -DryRun                       # 扫描未签名
.\batch-sync.bat                                             # 手动 DevEco Sync

# === 真机测试 ===
python smoke-test.py                                        # 5 旗舰冒烟
python smoke-test.py --agent-mode                           # 智能体维度断言
python smoke-test.py --brand gaokao --agent-mode            # 单品牌

# === 每日 CI ===
..\scripts\ci-daily.ps1
..\scripts\ci-daily.ps1 -Deploy
```

## P0 执行记录 (2026-07-18)

### P0.1: 签名注入 — 方案就绪，待手动执行
- `inject-signing.ps1` — DevEco 6.1 CLI 无法自动注入签名（已确认: devecocli build/run 均不支持）
- `sync-signing.ps1` — DevEco Studio CLI 批量打开策略（超时不可靠）
- `batch-sync.bat` — 推荐方案: 双击运行，逐个打开 17 APP 触发 Sync
- **执行**: 运行 `D:\92_products\SPDT-001_Harmony\automation\batch-sync.bat`

### P0.2: GaokaoAgent 批量部署 — 2/3 通过
- ✅ gaokao-language: 构建(1.4s) → 安装 → 启动 — PASS
- ✅ gaokao-volunteer: 构建(1.3s) → 安装 → 启动 — PASS
- ❌ gaokao-agent: 23个 ArkTS 严格模式编译错误 (DevEco 6.1 新增)
  - `arkts-no-obj-literals-as-types` (types.ets, InputAssist.ets, Index.ets)
  - `arkts-no-spread` (AgentProfile.ets)
  - `arkts-no-untyped-obj-literals` (InputAssist.ets)
  - Type mismatch PreviewService (storageService.ts)

### P0.3: 旗舰冒烟测试 — 2/5 通过 (AgentMode)
- ✅ thinkkit-coach: 构建(3.4s) → 安装 → 启动 → Prefs/HTTP/Battery ✅
- ✅ craftsman-arkui: 构建(3.5s) → 安装 → 启动 → Prefs/HTTP/Battery ✅
- ⏭ harmonycoder: 无签名配置
- ⏭ rhythm-habit: 无签名配置
- ❌ gaokao-agent: ArkTS 编译错误

### P0.4: 手动 DevEco Sync — 待执行
- 运行 `batch-sync.bat` 处理 17 个未签名 APP
- 预计耗时: ~2-3分钟/APP × 17 = ~40分钟
