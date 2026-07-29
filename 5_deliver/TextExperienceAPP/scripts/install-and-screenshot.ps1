# install-and-screenshot.ps1 — hdc install + 截图拉取
#
# 用途：将编译好的 HAP 安装到鸿蒙真机/模拟器，并拉取屏幕截图
# 依赖：hdc（HarmonyOS Device Connector）在 PATH 中
#       DevEco Studio 自带 hdc：{DevEco_Studio}\sdk\default\openharmony\toolchains\hdc.exe
# 用法：.\scripts\install-and-screenshot.ps1 [-HapPath <path>] [-ScreenshotDir <path>]
#
# 前置条件：
#   1. 设备已通过 USB 连接并开启开发者模式 + USB 调试
#   2. hdc 已添加到系统 PATH
#
# 输出：
#   安装成功 → 返回 0，截图保存到 ScreenshotDir
#   安装失败 → 返回 1

param(
    [string]$HapPath = "",
    [string]$ScreenshotDir = ".\screenshots",
    [int]$ScreenshotDelay = 3  # 截图前等待秒数（等待 App 启动）
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " 安装 & 截图脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# ---- 检查 hdc 可用性 ----

$hdcCmd = Get-Command hdc -ErrorAction SilentlyContinue
if (-not $hdcCmd) {
    Write-Host "[错误] 未找到 hdc 命令" -ForegroundColor Red
    Write-Host "       请将 DevEco Studio SDK 的 toolchains 目录添加到 PATH"
    Write-Host "       例: %USERPROFILE%\AppData\Local\Huawei\DevEcoStudio\sdk\default\openharmony\toolchains"
    exit 1
}

Write-Host "hdc 路径: $($hdcCmd.Source)" -ForegroundColor Gray

# ---- 检查设备连接 ----

Write-Host ""
Write-Host "[1/4] 检查设备连接..." -ForegroundColor Yellow

$deviceList = hdc list targets 2>&1
if ($LASTEXITCODE -ne 0 -or -not $deviceList -or $deviceList -eq "[Empty]") {
    Write-Host "[错误] 未检测到已连接的鸿蒙设备" -ForegroundColor Red
    Write-Host ""
    Write-Host "请确保：" -ForegroundColor Yellow
    Write-Host "  1. 设备已通过 USB 连接" -ForegroundColor Gray
    Write-Host "  2. 开发者模式已开启（设置-关于手机-连续点击版本号）" -ForegroundColor Gray
    Write-Host "  3. USB 调试已开启并授权此电脑" -ForegroundColor Gray
    Write-Host ""
    Write-Host "如果使用模拟器：" -ForegroundColor Yellow
    Write-Host "  DevEco Studio > Tools > Device Manager > 启动模拟器" -ForegroundColor Gray
    exit 1
}

# 多设备：自动选第一个
$deviceLines = @($deviceList -split "`n" | Where-Object { $_ -match '\S' })
$targetDevice = $deviceLines[0].Trim()
if ($deviceLines.Count -gt 1) {
    Write-Host "检测到 $($deviceLines.Count) 台设备，自动选择: $targetDevice" -ForegroundColor Yellow
} else {
    Write-Host "已连接设备: $targetDevice" -ForegroundColor Green
}

# ---- 查找 HAP 文件 ----

Write-Host ""
Write-Host "[2/4] 查找 HAP 文件..." -ForegroundColor Yellow

if (-not $HapPath) {
    # 自动搜索最新的 HAP
    $hapPattern = "entry\build\default\outputs\default\*.hap"
    $hapFiles = Get-ChildItem -Path $hapPattern -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending

    if (-not $hapFiles) {
        # 尝试另一种路径
        $hapPattern = "**\build\**\*.hap"
        $hapFiles = Get-ChildItem -Path $hapPattern -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending
    }

    if (-not $hapFiles) {
        Write-Host "[错误] 未找到 HAP 文件" -ForegroundColor Red
        Write-Host "       请先运行 build.ps1 编译项目"
        Write-Host "       或手动指定 HAP 路径: .\install-and-screenshot.ps1 -HapPath <path>"
        exit 1
    }

    $HapPath = $hapFiles[0].FullName
    Write-Host "自动选择最新 HAP: $HapPath" -ForegroundColor Green
} else {
    if (-not (Test-Path $HapPath)) {
        Write-Host "[错误] HAP 文件不存在: $HapPath" -ForegroundColor Red
        exit 1
    }
    Write-Host "HAP 路径: $HapPath" -ForegroundColor Green
}

# ---- 安装 HAP ----

Write-Host ""
Write-Host "[3/4] 安装 HAP 到设备..." -ForegroundColor Yellow

$installOutput = hdc install $HapPath 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "[失败] 安装失败:" -ForegroundColor Red
    Write-Host $installOutput -ForegroundColor Red
    exit 1
}

Write-Host "安装成功!" -ForegroundColor Green

# ---- 截图 ----

Write-Host ""
Write-Host "[4/4] 等待 $ScreenshotDelay 秒后截图..." -ForegroundColor Yellow
Start-Sleep -Seconds $ScreenshotDelay

# 创建截图目录
if (-not (Test-Path $ScreenshotDir)) {
    New-Item -ItemType Directory -Force -Path $ScreenshotDir | Out-Null
}

# 在设备上截图
$deviceScreenshotPath = "/data/local/tmp/screenshot_$(Get-Date -Format 'yyyyMMdd_HHmmss').png"
$snapOutput = hdc shell snapshot_display -f $deviceScreenshotPath 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "[警告] 设备截图失败，尝试备用方法..." -ForegroundColor Yellow
    # 备用方法：使用 shell screencap（如果可用）
    $snapOutput = hdc shell "snapshot_display -f $deviceScreenshotPath" 2>&1
}

# 拉取截图到本地
$localScreenshot = Join-Path $ScreenshotDir "screenshot_$(Get-Date -Format 'yyyyMMdd_HHmmss').png"
$pullOutput = hdc file recv $deviceScreenshotPath $localScreenshot 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "[错误] 截图拉取失败" -ForegroundColor Red
    Write-Host $pullOutput -ForegroundColor Red
    exit 1
}

# 清理设备上的临时文件
hdc shell rm -rf $deviceScreenshotPath 2>&1 | Out-Null

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host " 截图已保存: $localScreenshot" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

# 尝试用默认图片查看器打开截图
try {
    Start-Process $localScreenshot
} catch {
    Write-Host "(无法自动打开图片查看器，请手动打开截图)" -ForegroundColor Gray
}

exit 0
