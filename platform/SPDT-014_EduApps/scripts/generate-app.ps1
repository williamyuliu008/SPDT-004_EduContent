# generate-app.ps1 — 从模板生成单个 App 项目
#
# 用法：.\scripts\generate-app.ps1 -AppKey "craftsman-utils" -AppName "极客工具箱" -BundleName "com.harmonystudio.craftsman.utils" -TrackName "CraftsmanUtils" -PrimaryColor "#3C3C3C"
#       所有 App 的占位符在下方 $apps 哈希表中定义，可直接批量生成。

param(
    [string]$AppKey,
    [string]$AppName,
    [string]$AppDesc,
    [string]$BundleName,
    [string]$TrackName,
    [string]$PrimaryColor,
    [string]$StoreCategory,
    [string]$StoreKeywords,
    [string]$DataModels,
    [string]$FeatureFlags,
    [string]$StorageInstances,
    [string]$SampleItemTitle,
    [string]$SampleItemSubtitle,
    [string]$Permissions = ""
)

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$workshop = Resolve-Path (Join-Path $scriptDir "..")
$template = Join-Path $workshop "templates\app-scaffold"
$appsDir = Join-Path $workshop "apps"
$target = Join-Path $appsDir $AppKey

Write-Host "生成 App: $AppName ($AppKey)" -ForegroundColor Cyan

# 1. 复制模板
if (Test-Path $target) {
    Remove-Item -Recurse -Force $target
}
Copy-Item -Recurse $template $target

# 2. 获取所有需要替换的文件
$files = Get-ChildItem $target -Recurse -File | Where-Object {
    $_.Extension -in '.json5', '.json', '.ts', '.ets'
}

# 3. 逐文件替换占位符
$replacements = @{
    '{{APP_KEY}}'            = $AppKey
    '{{APP_NAME}}'           = $AppName
    '{{APP_DESC}}'           = $AppDesc
    '{{BUNDLE_NAME}}'        = $BundleName
    '{{TRACK_NAME}}'         = $TrackName
    '{{PRIMARY_COLOR}}'      = $PrimaryColor
    '{{STORE_CATEGORY}}'     = $StoreCategory
    '{{STORE_KEYWORDS}}'     = $StoreKeywords
    '{{DATA_MODELS}}'        = $DataModels
    '{{FEATURE_FLAGS}}'      = $FeatureFlags
    '{{STORAGE_INSTANCES}}'  = $StorageInstances
    '{{SAMPLE_ITEM_TITLE}}'  = $SampleItemTitle
    '{{SAMPLE_ITEM_SUBTITLE}}' = $SampleItemSubtitle
    '{{PERMISSIONS}}'        = if ($Permissions) { $Permissions } else { "`n      // 本地工具 — 零权限声明`n    " }
}

foreach ($file in $files) {
    $content = Get-Content $file.FullName -Raw -Encoding UTF8
    $changed = $false
    foreach ($key in $replacements.Keys) {
        if ($content -match [regex]::Escape($key)) {
            $content = $content.Replace($key, $replacements[$key])
            $changed = $true
        }
    }
    if ($changed) {
        # 保持 UTF8 无 BOM，末尾加换行
        $utf8NoBom = New-Object System.Text.UTF8Encoding $false
        [System.IO.File]::WriteAllText($file.FullName, $content.TrimEnd() + "`n", $utf8NoBom)
    }
}

# 4. 复制 common/ 到 App 根目录（符号链接在 Windows 上不稳定，直接复制）
$commonSrc = Join-Path $workshop "common"
$commonDst = Join-Path $target "common"
if (Test-Path $commonDst) { Remove-Item -Recurse -Force $commonDst }
Copy-Item -Recurse $commonSrc $commonDst

Write-Host "  ✓ $target" -ForegroundColor Green
Write-Host "    bundleName: $BundleName" -ForegroundColor Gray
Write-Host "    track: $TrackName | color: $PrimaryColor" -ForegroundColor Gray
