# dev-loop.ps1 — 开发闭环：编译 → 错误分析 → 安装 → 截图
#
# 用途：整合编译、错误分析、安装、截图的全流程开发闭环
#       编译失败时自动输出结构化错误日志供 AI 分析
#       编译成功时自动安装到设备并截图验证
#
# 依赖：
#   - build.ps1（编译脚本）
#   - install-and-screenshot.ps1（安装截图脚本）
#   - DevEco Studio + hdc
#
# 用法：
#   .\scripts\dev-loop.ps1                        # 完整闭环
#   .\scripts\dev-loop.ps1 -SkipInstall            # 仅编译，不安装
#   .\scripts\dev-loop.ps1 -SkipScreenshot         # 编译 + 安装，不截图
#   .\scripts\dev-loop.ps1 -AiMode                 # AI 模式：输出机器可读的 JSON 结果
#
# AI 集成说明：
#   当 -AiMode 启用时，脚本输出 JSON 格式的结果到 stdout
#   AI 可解析 buildResult.json 获取编译状态和错误信息
#   流程：AI 修改代码 → dev-loop.ps1 -AiMode → AI 解析结果 → 修复 → 重试

param(
    [switch]$SkipInstall,
    [switch]$SkipScreenshot,
    [switch]$AiMode,
    [ValidateSet("debug", "release")]
    [string]$Mode = "debug",
    [int]$MaxRetries = 3,
    [int]$TimeoutMinutes = 10
)

$ErrorActionPreference = "Continue"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Resolve-Path (Join-Path $scriptDir "..")

$startTime = Get-Date

# 结果对象（AI 模式使用）
$result = @{
    success = $false
    build = @{
        success = $false
        hapPath = ""
        errorLog = ""
        duration = 0
    }
    install = @{
        success = $false
        message = ""
    }
    screenshot = @{
        success = $false
        path = ""
    }
    totalDuration = 0
    errors = @()
}

function Write-Step {
    param([string]$Message, [string]$Status = "")
    if (-not $AiMode) {
        $icon = switch ($Status) {
            "ok" { "[✓]" }
            "fail" { "[✗]" }
            "running" { "[…]" }
            default { "[→]" }
        }
        $color = switch ($Status) {
            "ok" { "Green" }
            "fail" { "Red" }
            "running" { "Yellow" }
            default { "Cyan" }
        }
        Write-Host "$icon $Message" -ForegroundColor $color
    }
}

function Write-Result {
    param([string]$Label, $Value)
    if (-not $AiMode) {
        Write-Host "  $Label $Value" -ForegroundColor Gray
    }
}

# ============================================================================
# Phase 1: 编译
# ============================================================================

if (-not $AiMode) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host " 开发闭环 (Dev Loop)" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "项目: $projectRoot"
    Write-Host "模式: $Mode"
    Write-Host ""
}

Write-Step "Phase 1/3: 编译项目" "running"

$buildStart = Get-Date
$buildScript = Join-Path $scriptDir "build.ps1"
$buildOutput = & powershell -NoProfile -ExecutionPolicy Bypass -File $buildScript -ProjectPath $projectRoot -Mode $Mode 2>&1
$buildSuccess = ($LASTEXITCODE -eq 0)
$buildDuration = [math]::Round(((Get-Date) - $buildStart).TotalSeconds, 1)

$result.build.success = $buildSuccess
$result.build.duration = $buildDuration

if ($buildSuccess) {
    Write-Step "Phase 1/3: 编译成功 (${buildDuration}s)" "ok"

    # 提取 HAP 路径
    $hapLine = $buildOutput | Where-Object { $_ -match "\.hap$" } | Select-Object -First 1
    if ($hapLine) {
        $hapPath = $hapLine.Trim()
        $result.build.hapPath = $hapPath
        Write-Result "HAP:" $hapPath
    }
} else {
    Write-Step "Phase 1/3: 编译失败 (${buildDuration}s)" "fail"

    # 读取错误日志
    $errorLogPath = Join-Path $projectRoot "build-error.log"
    if (Test-Path $errorLogPath) {
        $errorContent = Get-Content $errorLogPath -Raw -Encoding utf8
        $result.build.errorLog = $errorContent

        # 提取关键错误行（最多显示 10 行）
        $keyErrors = $errorContent -split "`n" | Where-Object { $_ -match "ERROR|error|Error" } | Select-Object -First 10
        $result.errors = @($keyErrors)

        if (-not $AiMode) {
            Write-Host ""
            Write-Host "--- 编译错误（可将以下内容提供给 AI 分析）---" -ForegroundColor Red
            $keyErrors | ForEach-Object { Write-Host "  $_" -ForegroundColor Red }
            Write-Host ""
            Write-Host " 错误日志: $errorLogPath" -ForegroundColor Yellow
            Write-Host ""
            Write-Host " AI 分析提示：" -ForegroundColor Cyan
            Write-Host '   "请分析以下鸿蒙 ArkTS 编译错误并给出修复方案：`n' -ForegroundColor Cyan
            $keyErrors | ForEach-Object { Write-Host "   $_" -ForegroundColor Cyan }
            Write-Host '   "' -ForegroundColor Cyan
        }
    }

    # AI 模式输出 JSON 后退出
    if ($AiMode) {
        $result.totalDuration = [math]::Round(((Get-Date) - $startTime).TotalSeconds, 1)
        $result | ConvertTo-Json -Depth 3
    }
    exit 1
}

# ============================================================================
# Phase 2: 安装
# ============================================================================

if (-not $SkipInstall) {
    Write-Step "Phase 2/3: 安装到设备" "running"

    $installStart = Get-Date
    $installScript = Join-Path $scriptDir "install-and-screenshot.ps1"
    $installArgs = @(
        "-NoProfile", "-ExecutionPolicy", "Bypass",
        "-File", $installScript,
        "-HapPath", $result.build.hapPath
    )

    if ($SkipScreenshot) {
        # 仅安装，不截图 — 使用自定义逻辑
        $hdcCmd = Get-Command hdc -ErrorAction SilentlyContinue
        if (-not $hdcCmd) {
            $result.install.message = "hdc 未找到"
            Write-Step "Phase 2/3: 安装失败 (hdc 不可用)" "fail"
            if ($AiMode) {
                $result.totalDuration = [math]::Round(((Get-Date) - $startTime).TotalSeconds, 1)
                $result | ConvertTo-Json -Depth 3
            }
            exit 1
        }

        $installOutput = hdc install $result.build.hapPath 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Step "Phase 2/3: 安装成功" "ok"
            $result.install.success = $true
        } else {
            Write-Step "Phase 2/3: 安装失败" "fail"
            $result.install.message = ($installOutput -join "`n")
            Write-Host $installOutput -ForegroundColor Red
            if ($AiMode) {
                $result.totalDuration = [math]::Round(((Get-Date) - $startTime).TotalSeconds, 1)
                $result | ConvertTo-Json -Depth 3
            }
            exit 1
        }
    } else {
        # 完整安装 + 截图
        $installOutput = & powershell @installArgs 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Step "Phase 2/3: 安装成功" "ok"
            $result.install.success = $true

            # 提取截图路径
            $screenLine = $installOutput | Where-Object { $_ -match "截图已保存" }
            if ($screenLine) {
                $screenPath = ($screenLine -split ": ")[1].Trim()
                $result.screenshot.path = $screenPath
                $result.screenshot.success = $true
            }
        } else {
            Write-Step "Phase 2/3: 安装失败" "fail"
            $result.install.message = ($installOutput -join "`n")
            Write-Host $installOutput -ForegroundColor Red
            if ($AiMode) {
                $result.totalDuration = [math]::Round(((Get-Date) - $startTime).TotalSeconds, 1)
                $result | ConvertTo-Json -Depth 3
            }
            exit 1
        }
    }
} else {
    Write-Step "Phase 2/3: 跳过安装 (--SkipInstall)" "ok"
}

# ============================================================================
# Phase 3: 截图验证
# ============================================================================

if (-not $SkipScreenshot -and $result.screenshot.success) {
    Write-Step "Phase 3/3: 截图已保存" "ok"
    Write-Result "路径:" $result.screenshot.path
} elseif (-not $SkipScreenshot -and -not $SkipInstall) {
    Write-Step "Phase 3/3: 截图获取中..." "ok"
} else {
    Write-Step "Phase 3/3: 跳过截图" "ok"
}

# ============================================================================
# 完成
# ============================================================================

$result.success = $true
$result.totalDuration = [math]::Round(((Get-Date) - $startTime).TotalSeconds, 1)

if (-not $AiMode) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host " 开发闭环完成! (总耗时: $($result.totalDuration)s)" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green

    if ($result.screenshot.path) {
        Write-Host ""
        Write-Host "截图已保存: $($result.screenshot.path)" -ForegroundColor Cyan
        Write-Host "接下来: Review UI → 修改代码 → 重新运行 dev-loop.ps1" -ForegroundColor Cyan
    }
} else {
    # AI 模式：输出 JSON 结果
    $result | ConvertTo-Json -Depth 3
}

exit 0
