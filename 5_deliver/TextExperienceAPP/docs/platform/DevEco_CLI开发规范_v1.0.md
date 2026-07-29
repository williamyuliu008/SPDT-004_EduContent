# SPDT-001 · DevEco CLI 开发规范 v1.0

> 基于 DevEco CLI v1.2.0 | 适配 DevEco Studio 6.1+ | SPDT-001 鸿蒙生态开发
> 生成: 2026-07-16 | 鸿蒙特使

---

## 一、环境配置

### 1.1 安装

```powershell
# 全局安装
npm install -g @deveco/deveco-cli

# 验证
devecocli --version   # 预期 ≥ 1.2.0

# 初始化 AI 技能（可选，对接 Cursor/Claude Code）
devecocli init
```

### 1.2 环境变量 (Windows)

```powershell
# 系统环境变量（永久）
[Environment]::SetEnvironmentVariable("DEVECO_SDK_HOME", "D:\92_infra\DevEco_6.1\sdk", "User")
[Environment]::SetEnvironmentVariable("JAVA_HOME", "D:\92_infra\DevEco_6.1\jbr", "User")
$env:PATH = "D:\92_infra\DevEco_6.1\tools\node;$env:PATH"
```

> ⚠️ 每升级 DevEco 版本后必须更新以上路径。旧版本 JDK 可保留在 `D:\9_infra\DevEco\` 做回退保险。

### 1.3 项目环境

所有 APP 必须统一以下配置：

| 文件 | 关键字段 | 值 |
|:---|:---|:---|
| `build-profile.json5` | `compatibleSdkVersion` | `"5.0.3(15)"`（5.0.9）/ 随 DevEco 版本更新 |
| `build-profile.json5` | `signingConfigs` | 空数组 `[]`，首次 Sync 时 DevEco 自动注入 |
| `oh-package.json5` | `modelVersion` | 与 hvigor-config 一致 |
| `hvigor/hvigor-config.json5` | `modelVersion` | 与 oh-package 一致 |
| `AppScope/app.json5` | 禁止字段 | `buildVersion` |
| `signingConfigs[0]` | 允许字段 | `name`, `type`, `material` **仅此三字段** |

### 1.4 首次初始化

```powershell
# 单项目初始化（首次打开时 DevEco 自动完成 Sync + 签名注入）
devecocli build --build-mode debug

# 批量初始化所有 29 个 APP（按需）
Get-ChildItem "D:\92_products\SPDT-001_Harmony\apps" -Directory | ForEach-Object {
  Push-Location $_.FullName
  devecocli build --build-mode debug
  Pop-Location
}
```

---

## 二、CLI 命令参考

### 2.1 核心命令

| 命令 | 用途 | SPDT-001 常用场景 |
|:---|:---|:---|
| `devecocli build` | 编译构建 | CI 流水线、批量编译 |
| `devecocli run` | 编译+安装+启动 | 一键部署到真机 |
| `devecocli device list` | 列出设备 | 检查真机连接状态 |
| `devecocli log` | 抓取日志 | 调试运行时问题 |
| `devecocli create` | 新建项目 | 替代 templates/base fork |
| `devecocli lint` | 静态检查 | PREFLIGHT 替代方案 |

### 2.2 编译命令

```powershell
# 单 APP Debug 编译
cd apps/thinkkit-coach
devecocli build --build-mode debug

# 单 APP Release 编译（需签名配置）
devecocli build --build-mode release --product default

# 批量编译所有 APP（PowerShell）
Get-ChildItem "D:\92_products\SPDT-001_Harmony\apps" -Directory | ForEach-Object {
  Write-Host "[BUILD] $($_.Name)"
  Push-Location $_.FullName
  devecocli build --build-mode debug 2>&1
  Pop-Location
}
```

### 2.3 部署命令

```powershell
# 一键部署到真机
cd apps/thinkkit-coach
devecocli run --device 7GL0226313016118 --build-mode debug

# 批量部署所有 APP
$device = "7GL0226313016118"
Get-ChildItem "D:\92_products\SPDT-001_Harmony\apps" -Directory | ForEach-Object {
  Write-Host "[RUN] $($_.Name)"
  Push-Location $_.FullName
  devecocli run --device $device --build-mode debug 2>&1
  Pop-Location
}
```

### 2.4 设备管理

```powershell
# 列出所有设备
devecocli device list

# 输出示例:
# 7GL0226313016118    VYG-AL30    phone    connected
```

### 2.5 日志抓取

```powershell
# 抓取指定 APP 日志
devecocli log --filter com.harmonystudio.thinkkit.coach

# 实时跟踪错误日志
devecocli log --filter com.harmonystudio.harmonycoder --level error
```

---

## 三、自动化脚本套件

### 3.1 目录结构

```
SPDT-001_Harmony/
├── scripts/
│   ├── init-app.ps1           # 已有：创建新 APP（保留）
│   ├── build-all.ps1          # 已有：批量编译（需更新为 devecocli）
│   ├── sign-all.ps1           # 已有：批量签名（devecocli 内置后可选退役）
│   ├── deploy-all.ps1         # 新增：批量部署
│   ├── ci-daily.ps1           # 新增：每日 CI 全流程
│   └── cli-config.json        # 新增：CLI 全局配置
├── ci/
│   ├── pipeline.yaml          # 已有：CI 定义（需更新）
│   └── stages/                # 已有：PREFLIGHT/BUILD/SIGN/DEPLOY/REPORT
└── templates/
    └── base/                   # 已有：标准化模板
```

### 3.2 全局配置 `cli-config.json`

```json
{
  "sdkHome": "D:\\92_infra\\DevEco_6.1\\sdk",
  "javaHome": "D:\\92_infra\\DevEco_6.1\\jbr",
  "workspace": "D:\\92_products\\SPDT-001_Harmony",
  "appsDir": "D:\\92_products\\SPDT-001_Harmony\\apps",
  "defaultDevice": "7GL0226313016118",
  "buildMode": "debug",
  "signConfig": "auto",
  "brands": {
    "thinkkit": { "prefix": "thinkkit-", "color": "#5B8C5A" },
    "craftsman": { "prefix": "craftsman-", "color": "#E87A2A" },
    "harmonycoder": { "prefix": "harmonycoder", "color": "#7B2D8E" },
    "rhythm": { "prefix": "rhythm-", "color": "#3B82B0" },
    "gaokao": { "prefix": "gaokao-", "color": "#C44536" }
  }
}
```

### 3.3 批量部署脚本 `deploy-all.ps1`

```powershell
# SPDT-001 批量部署脚本 (DevEco CLI)
param(
  [string]$Device = "7GL0226313016118",
  [string]$Brand = "",
  [switch]$SkipBuild
)

$config = Get-Content "$PSScriptRoot\cli-config.json" -Raw | ConvertFrom-Json
$apps = Get-ChildItem $config.appsDir -Directory

if ($Brand) {
  $prefix = $config.brands.$Brand.prefix
  $apps = $apps | Where-Object { $_.Name -like "$prefix*" }
}

$pass = 0; $fail = 0
foreach ($app in $apps) {
  Write-Host "[DEPLOY] $($app.Name)" -ForegroundColor Cyan
  Push-Location $app.FullName
  
  if ($SkipBuild) {
    $result = devecocli run --device $Device --skip-build 2>&1
  } else {
    $result = devecocli run --device $Device --build-mode $config.buildMode 2>&1
  }
  
  if ($LASTEXITCODE -eq 0) { $pass++; Write-Host "  OK" -ForegroundColor Green }
  else { $fail++; Write-Host "  FAIL" -ForegroundColor Red }
  Pop-Location
}

Write-Host "`n$pass deployed, $fail failed"
```

### 3.4 每日 CI 脚本 `ci-daily.ps1`

```powershell
# SPDT-001 每日 CI 全流程
param([switch]$Deploy)

$root = "D:\92_products\SPDT-001_Harmony"

# 1. PREFLIGHT
Write-Host "=== PREFLIGHT ==="
& "$root\ci\stages\preflight.ps1" -ScanAll

# 2. BUILD (devecocli)
Write-Host "`n=== BUILD ==="
Get-ChildItem "$root\apps" -Directory | ForEach-Object {
  Push-Location $_.FullName
  devecocli build --build-mode debug 2>&1 | Select-Object -Last 1
  Pop-Location
}

# 3. OMAS 心跳
Write-Host "`n=== OMAS ==="
@("HDT-001-TK","HDT-001-CM","HDT-001-HC","HDT-001-RH","HDT-001-GK") | ForEach-Object {
  python "D:\6_agent_project\omas\tools\registry_checker.py" --touch $_
}

# 4. 可选部署
if ($Deploy) {
  Write-Host "`n=== DEPLOY ==="
  & "$root\scripts\deploy-all.ps1" -SkipBuild
}
```

---

## 四、签名配置模板

### 4.1 `sign_config.json`（手动签名时使用）

```json
{
  "material": {
    "storeFile": "C:\\Users\\willi\\.ohos\\config\\default_thinkkit-coach_xxx.p12",
    "storePassword": "0000001B...",
    "keyAlias": "debugKey",
    "keyPassword": "0000001B...",
    "signAlg": "SHA256withECDSA",
    "profile": "C:\\Users\\willi\\.ohos\\config\\default_thinkkit-coach_xxx.p7b",
    "certpath": "C:\\Users\\willi\\.ohos\\config\\default_thinkkit-coach_xxx.cer"
  }
}
```

> **注意：** DevEco CLI 的自动签名（`devecocli run` 不加 `--sign` 参数）会自动使用项目 build-profile.json5 中的 signingConfigs，无需手动提供此文件。仅 Release 签名或非 DevEco 自动签名场景才需要。

---

## 五、AI 驱动开发流程

```
用户需求 → AI 生成代码 → devecocli lint (语法检查)
                ↓ (有错误)
         AI 修复代码 ← devecocli log (错误日志)
                ↓ (无错误)
         devecocli run --device (部署测试)
                ↓
         用户验收
```

### 5.1 AI Agent 集成接口

```python
# Python 示例：AI 调用 devecocli 的循环迭代模式
import subprocess, json

def ai_dev_loop(app_path: str, max_iterations: int = 8):
    """AI 驱动的开发-测试闭环"""
    for i in range(max_iterations):
        # 1. 编译
        result = subprocess.run(
            ["devecocli", "build", "--build-mode", "debug"],
            cwd=app_path, capture_output=True, text=True
        )
        if result.returncode != 0:
            yield {"status": "build_error", "log": result.stderr, "iteration": i}
            continue
        
        # 2. 部署运行
        result = subprocess.run(
            ["devecocli", "run", "--device", "7GL0226313016118"],
            cwd=app_path, capture_output=True, text=True
        )
        
        # 3. 抓取日志
        log = subprocess.run(
            ["devecocli", "log", "--level", "error"],
            capture_output=True, text=True
        )
        
        if "ERROR" in log.stdout:
            yield {"status": "runtime_error", "log": log.stdout, "iteration": i}
        else:
            yield {"status": "success", "iteration": i}
            break
```

---

## 六、常见问题速查

| 错误 | 原因 | 修复 |
|:---|:---|:---|
| `DevEco Studio version below 6.1.0` | DevEco 版本过低 | 升级到 6.1+ |
| `Schema validate failed: signingConfigs[0]` | signingConfig 含非法字段 | 删除 configs 数组中的 `signingConfig` 字段，仅保留 `name/type/material` |
| `modelVersion mismatch` | oh-package 与 hvigor-config 不一致 | 统一为当前 DevEco 版本要求的值 |
| `could not open jvm.cfg` | JAVA_HOME 指向旧路径 | 更新 `JAVA_HOME` + 复制 JDK 到旧路径兜底 |
| `could not open ...\DevEco Studio\jbr\...` | hvigor 守护进程缓存旧 JDK | `devecocli build --clean` 或删除 `.hvigor` 缓存 |
| `no signature file (9568320)` | build-profile.json5 缺签名 | Sync 时 DevEco 自动注入，手动则需执行一次 `devecocli run` |

---

## 七、版本迁移检查清单

每次 DevEco 大版本升级时执行：

- [ ] 新建空白项目 → 获取标准 `build-profile.json5` / `oh-package.json5` / `hvigor-config.json5` 格式
- [ ] 比对差异 → 批量更新所有 29 个 APP 的配置文件
- [ ] 更新 `cli-config.json` 中的 `sdkHome` / `javaHome`
- [ ] 更新系统环境变量 `DEVECO_SDK_HOME` / `JAVA_HOME`
- [ ] 更新 `scripts/*.ps1` 和 `ci/*` 中的路径引用
- [ ] 清理所有 `.hvigor` 缓存和 `entry/build` 目录
- [ ] 测试 1 个 APP 的 `devecocli build → run`
- [ ] PREFLIGHT -ScanAll 验证

---

> 🏗️ 鸿蒙特使 · SPDT-001 | CLI 开发规范 v1.0 | 2026-07-16
