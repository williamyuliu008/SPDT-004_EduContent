# init-project.ps1 — 一键创建鸿蒙 App 项目
#
# 用途：从 app-scaffold 模板创建新 App，自动替换占位符、复制 common/、配置 Feature Flag
#
# 用法：
#   交互模式    ：.\scripts\init-project.ps1
#   参数模式    ：.\scripts\init-project.ps1 -AppKey "my-app" -AppName "我的App" ...
#   赛道模板    ：.\scripts\init-project.ps1 -Track "ThinkKit" -AppKey "thinkkit-xxx" -AppName "我的App"
#
# 支持的赛道模板：
#   ThinkKit       →  productivity/knowledge, color #5B8C5A
#   RhythmLife     →  habit/life, color #4A90D9
#   CraftsmanUtils →  dev tools, color #3C3C3C
#   Custom         →  手动指定所有参数
#
# 产出：apps/{AppKey}/ 下的完整鸿蒙项目骨架

param(
    [string]$AppKey,
    [string]$AppName,
    [string]$AppDesc,
    [string]$Track = "Custom",
    [string]$PrimaryColor,
    [string]$BundleName,
    [string]$StoreCategory,
    [string]$StoreKeywords,
    [string[]]$Pages = @("IndexPage"),
    [switch]$NonInteractive
)

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$workshop = Resolve-Path (Join-Path $scriptDir "..")
$template = Join-Path $workshop "templates\app-scaffold"
$appsDir = Join-Path $workshop "apps"
$genScript = Join-Path $scriptDir "generate-app.ps1"

# ============================================================================
# 赛道预设
# ============================================================================

$trackPresets = @{
    "ThinkKit" = @{
        PrimaryColor    = "#5B8C5A"
        StoreCategory   = "PRODUCTIVITY"
        Features        = "enableFlashCard: false,`n    enableOutlineNote: false,`n    enableExportCSV: false,`n    enableBadge: false,"
        DataModels      = "export interface Note { id: string; title: string; body: string; tags: string[]; createdAt: number; updatedAt: number; }"
        StorageInstances = "notes: new StorageService<Note>(STORAGE_KEYS.NOTES),"
        SampleTitle     = "未命名笔记"
        SampleSubtitle  = "刚刚创建"
    }
    "RhythmLife" = @{
        PrimaryColor    = "#4A90D9"
        StoreCategory   = "HEALTH_AND_FITNESS"
        Features        = "enableHabitTracking: true,`n    enableStreakView: true,`n    enableWidget: false,"
        DataModels      = "export interface Habit { id: string; name: string; description: string; icon: string; color: string; targetDays: number; createdAt: number; }"
        StorageInstances = "habits: new StorageService<Habit>(STORAGE_KEYS.HABITS),"
        SampleTitle     = "新习惯"
        SampleSubtitle  = "连续 0 天 · 今天未打卡"
    }
    "CraftsmanUtils" = @{
        PrimaryColor    = "#3C3C3C"
        StoreCategory   = "TOOLS"
        Features        = "enableDevTools: true,"
        DataModels      = "export interface ToolPref { id: string; toolName: string; pinned: boolean; lastUsedAt: number; }"
        StorageInstances = "devPrefs: new StorageService<ToolPref>(STORAGE_KEYS.DEV_TOOLS_PREFS),"
        SampleTitle     = "JSON 格式化"
        SampleSubtitle  = "格式化/压缩/校验 JSON 数据"
    }
}

# ============================================================================
# 交互模式
# ============================================================================

if (-not $NonInteractive -and (-not $AppKey -or -not $AppName)) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host " 鸿蒙 App 项目初始化向导" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""

    # Step 1: 选择赛道
    Write-Host "可选赛道：" -ForegroundColor Yellow
    Write-Host "  1. ThinkKit       — 生产力/知识管理 (森绿 #5B8C5A)" -ForegroundColor Gray
    Write-Host "  2. RhythmLife     — 习惯/生活优化 (靛蓝 #4A90D9)" -ForegroundColor Gray
    Write-Host "  3. CraftsmanUtils — 开发者/极客工具 (深灰 #3C3C3C)" -ForegroundColor Gray
    Write-Host "  4. Custom         — 自定义所有参数" -ForegroundColor Gray
    $trackChoice = Read-Host "选择赛道 (1-4)"

    switch ($trackChoice) {
        "1" { $Track = "ThinkKit" }
        "2" { $Track = "RhythmLife" }
        "3" { $Track = "CraftsmanUtils" }
        "4" { $Track = "Custom" }
        default { Write-Host "无效选择，使用 Custom" -ForegroundColor Yellow; $Track = "Custom" }
    }

    # Step 2: App 基本信息
    if (-not $AppKey) {
        $defaultKey = if ($Track -ne "Custom") { "$($Track.ToLower())-" } else { "" }
        $AppKey = Read-Host "App Key (如 thinkkit-flashcard)"
    }
    if (-not $AppName) {
        $AppName = Read-Host "App 显示名称 (如 静·闪卡)"
    }
    if (-not $AppDesc) {
        $AppDesc = Read-Host "App 描述 (一句话)"
    }
    if (-not $BundleName) {
        $BundleName = Read-Host "bundleName (如 com.harmonystudio.thinkkit.flashcard)"
    }

    # Step 3: 赛道特定参数
    if ($Track -eq "Custom") {
        if (-not $PrimaryColor) { $PrimaryColor = Read-Host "主色 (如 #5B8C5A)" }
        if (-not $StoreCategory) { $StoreCategory = Read-Host "应用市场分类 (如 PRODUCTIVITY)" }
        if (-not $StoreKeywords) { $StoreKeywords = Read-Host "ASO 关键词 (逗号分隔)" }
    }
}

# ============================================================================
# 参数填充
# ============================================================================

$preset = $trackPresets[$Track]
if (-not $PrimaryColor -and $preset) { $PrimaryColor = $preset.PrimaryColor }
if (-not $StoreCategory -and $preset) { $StoreCategory = $preset.StoreCategory }
if (-not $AppDesc) { $AppDesc = $AppName }
if (-not $BundleName) { $BundleName = "com.harmonystudio.$($AppKey.ToLower().Replace('-','.'))" }
if (-not $PrimaryColor) { $PrimaryColor = "#5B8C5A" }
if (-not $StoreCategory) { $StoreCategory = "TOOLS" }
if (-not $StoreKeywords) { $StoreKeywords = "鸿蒙原生,$AppName" }

$features = if ($preset) { $preset.Features } else { "// TODO: define feature flags" }
$dataModels = if ($preset) { $preset.DataModels } else { "// TODO: define data models" }
$storageInstances = if ($preset) { $preset.StorageInstances } else { "// TODO: define storage instances" }
$sampleTitle = if ($preset) { $preset.SampleTitle } else { $AppName }
$sampleSubtitle = if ($preset) { $preset.SampleSubtitle } else { "刚刚创建" }

# ============================================================================
# 检查冲突
# ============================================================================

$target = Join-Path $appsDir $AppKey
if (Test-Path $target) {
    $confirm = Read-Host "项目 '$AppKey' 已存在，是否覆盖？(y/N)"
    if ($confirm -ne 'y' -and $confirm -ne 'Y') {
        Write-Host "已取消。" -ForegroundColor Yellow
        exit 0
    }
    Remove-Item -Recurse -Force $target
}

# ============================================================================
# 调用 generate-app.ps1 生成项目
# ============================================================================

Write-Host ""
Write-Host "正在生成项目..." -ForegroundColor Yellow

$genArgs = @(
    "-ExecutionPolicy", "Bypass",
    "-File", $genScript,
    "-AppKey", $AppKey,
    "-AppName", $AppName,
    "-AppDesc", $AppDesc,
    "-BundleName", $BundleName,
    "-TrackName", $Track,
    "-PrimaryColor", $PrimaryColor,
    "-StoreCategory", $StoreCategory,
    "-StoreKeywords", $StoreKeywords,
    "-DataModels", $dataModels,
    "-FeatureFlags", $features,
    "-StorageInstances", $storageInstances,
    "-SampleItemTitle", $sampleTitle,
    "-SampleItemSubtitle", $sampleSubtitle
)

$output = & powershell @genArgs 2>&1
$success = ($LASTEXITCODE -eq 0)

if (-not $success) {
    Write-Host "生成失败！" -ForegroundColor Red
    Write-Host $output -ForegroundColor Red
    exit 1
}

# ============================================================================
# 注册额外页面路由
# ============================================================================

$mainPagesPath = Join-Path $target "entry\src\main\resources\base\profile\main_pages.json"
$existingPages = @("pages/IndexPage")
if ($Pages.Count -gt 1 -or $Pages[0] -ne "IndexPage") {
    $allPages = @("pages/IndexPage") + ($Pages | Where-Object { $_ -ne "IndexPage" } | ForEach-Object { "pages/$_" })
    $pagesJson = @{ src = $allPages } | ConvertTo-Json -Depth 2
    $utf8NoBom = New-Object System.Text.UTF8Encoding $false
    [System.IO.File]::WriteAllText($mainPagesPath, $pagesJson + "`n", $utf8NoBom)
    Write-Host "  路由已注册: $($allPages -join ', ')" -ForegroundColor Gray
}

# ============================================================================
# 完成
# ============================================================================

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host " 项目创建完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "  路径    : $target" -ForegroundColor Gray
Write-Host "  赛道    : $Track" -ForegroundColor Gray
Write-Host "  主色    : $PrimaryColor" -ForegroundColor Gray
Write-Host "  分类    : $StoreCategory" -ForegroundColor Gray
Write-Host ""
Write-Host "  下一步：" -ForegroundColor Cyan
Write-Host "  1. cd $target" -ForegroundColor Gray
Write-Host "  2. 在 DevEco Studio 中打开此目录" -ForegroundColor Gray
Write-Host "  3. 用 AI 提示词手册生成其他页面" -ForegroundColor Gray
Write-Host "  4. 运行 dev-loop.ps1 编译验证" -ForegroundColor Gray
