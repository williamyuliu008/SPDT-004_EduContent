# build.ps1 — 封装 hvigorw assembleHap 调用
#
# 用途：编译鸿蒙项目并捕获错误输出到日志文件
# 依赖：DevEco Studio 已安装，hvigorw 在 PATH 中或项目根目录
# 用法：.\scripts\build.ps1 [-ProjectPath <path>] [-Mode <debug|release>]
#       默认在当前目录编译，mode 为 debug
#
# 输出：
#   成功 → 返回 0，输出 HAP 路径
#   失败 → 返回 1，输出错误日志路径 build-error.log
#
# 错误分析：
#   AI 可读取 build-error.log 分析编译错误并提供修复建议

param(
    [string]$ProjectPath = ".",
    [ValidateSet("debug", "release")]
    [string]$Mode = "debug"
)

$ErrorActionPreference = "Stop"
$startTime = Get-Date

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " 鸿蒙编译脚本 (HarmonyOS Build Script)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "项目路径: $ProjectPath"
Write-Host "编译模式: $Mode"
Write-Host "开始时间: $($startTime.ToString('yyyy-MM-dd HH:mm:ss'))"
Write-Host ""

# 检查 hvigorw 是否可用（多种查找策略）
$hvigorwExe = $null

# 策略 1: 项目根目录下的 hvigorw
$localHvigorw = Join-Path $ProjectPath "hvigorw"
if (Test-Path $localHvigorw) { $hvigorwExe = $localHvigorw }

# 策略 2: 全局 PATH 中的 hvigorw
if (-not $hvigorwExe) {
    $globalCmd = Get-Command hvigorw -ErrorAction SilentlyContinue
    if ($globalCmd) { $hvigorwExe = "hvigorw" }
}

# 策略 3: DevEco Studio 默认安装路径
if (-not $hvigorwExe) {
    $devEcoPaths = @(
        "$env:LOCALAPPDATA\Huawei\DevEcoStudio\bin\hvigorw.bat",
        "$env:APPDATA\Huawei\DevEcoStudio\bin\hvigorw.bat",
        "C:\Program Files\Huawei\DevEcoStudio\bin\hvigorw.bat"
    )
    foreach ($p in $devEcoPaths) {
        if (Test-Path $p) { $hvigorwExe = $p; break }
    }
}

if (-not $hvigorwExe) {
    Write-Host "[错误] 未找到 hvigorw 编译器" -ForegroundColor Red
    Write-Host ""
    Write-Host "请确保以下之一：" -ForegroundColor Yellow
    Write-Host "  1. 已安装 DevEco Studio 5.x" -ForegroundColor Gray
    Write-Host "    下载: https://developer.huawei.com/consumer/cn/deveco-studio/" -ForegroundColor Gray
    Write-Host "  2. 在 DevEco Studio 项目根目录下运行此脚本" -ForegroundColor Gray
    Write-Host "  3. 将 DevEco Studio 的 hvigorw 添加到系统 PATH" -ForegroundColor Gray
    Write-Host ""
    Write-Host "当前未安装 DevEco Studio？跳过编译，先完成代码生成。" -ForegroundColor Cyan
    Write-Host "后续安装 DevEco 后重新运行此脚本即可。" -ForegroundColor Cyan
    exit 1
}

# 编译参数
$assembleArgs = @(
    "assembleHap",
    "--mode", "module",
    "-p", "product=default",
    "-p", "buildMode=$Mode"
)

# 日志文件
$logFile = Join-Path $ProjectPath "build-output.log"
$errorFile = Join-Path $ProjectPath "build-error.log"

Write-Host "[1/2] 正在编译..." -ForegroundColor Yellow
Write-Host "命令: $hvigorwExe $($assembleArgs -join ' ')"
Write-Host ""

try {
    # 执行编译，捕获标准输出和错误输出
    $output = & $hvigorwExe @assembleArgs 2>&1

    # 写入完整日志
    $output | Out-File -FilePath $logFile -Encoding utf8

    # 检查是否编译成功
    $exitCode = $LASTEXITCODE

    if ($exitCode -eq 0) {
        # 编译成功
        Write-Host "[2/2] 编译成功!" -ForegroundColor Green

        # 查找生成的 HAP 文件
        $hapPattern = Join-Path $ProjectPath "entry\build\default\outputs\default\*.hap"
        $hapFiles = Get-ChildItem -Path $hapPattern -ErrorAction SilentlyContinue

        if ($hapFiles) {
            foreach ($hap in $hapFiles) {
                $sizeMB = [math]::Round($hap.Length / 1MB, 2)
                Write-Host "  HAP: $($hap.FullName)" -ForegroundColor Green
                Write-Host "  大小: ${sizeMB} MB" -ForegroundColor Green
            }
        } else {
            Write-Host "  (未自动检测到 HAP 文件，请手动检查)" -ForegroundColor Yellow
        }

        $elapsed = (Get-Date) - $startTime
        Write-Host ""
        Write-Host "编译耗时: $($elapsed.TotalSeconds.ToString('0.0'))s" -ForegroundColor Cyan
        Write-Host "完整日志: $logFile" -ForegroundColor Cyan

        exit 0
    } else {
        # 编译失败
        throw "编译失败 (exit code: $exitCode)"
    }
} catch {
    # 提取错误信息
    Write-Host "[2/2] 编译失败!" -ForegroundColor Red
    Write-Host ""

    # 从输出中提取错误行
    $errorLines = $output | Where-Object {
        $_ -match "ERROR|error|Error|FAILED|failed|BUILD FAILED"
    }

    if ($errorLines) {
        Write-Host "--- 编译错误摘要 ---" -ForegroundColor Red
        $errorLines | ForEach-Object {
            Write-Host "  $_" -ForegroundColor Red
        }
        Write-Host ""

        # 写入错误日志供 AI 分析
        $errorSummary = @"
编译时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
项目路径: $ProjectPath
编译模式: $Mode
退出码: $exitCode

=== 错误摘要 ===
$($errorLines -join "`n")

=== 完整日志 ===
$($output -join "`n")
"@
        $errorSummary | Out-File -FilePath $errorFile -Encoding utf8

        Write-Host "错误日志已保存至: $errorFile" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "提示：将 $errorFile 提供给 AI 可获取修复建议" -ForegroundColor Cyan
        Write-Host "  (如: '请分析 $errorFile 中的编译错误并给出修复方案')" -ForegroundColor Cyan
    } else {
        # 没有明显的错误行，输出全部日志
        $output | ForEach-Object { Write-Host $_ -ForegroundColor Red }
        $output | Out-File -FilePath $errorFile -Encoding utf8
    }

    exit 1
}
