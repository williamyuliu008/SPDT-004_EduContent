# SPDT-001 sync-signing.ps1 — 批量 DevEco Studio Sync 签名注入
# 策略: 通过 devecostudio CLI 打开项目 → DevEco 自动 Sync 注入 signingConfigs
# 这是 DevEco 6.1 唯一的 CLI 自动签名路径
# Usage: .\automation\sync-signing.ps1 [-BatchSize 5] [-Timeout 60]

param(
    [int]$BatchSize = 5,         # 每批打开的项目数
    [int]$Timeout = 60,          # 每批等待时间（秒）
    [switch]$ListOnly            # 仅列出未签名 APP
)

$root = "D:\92_products\SPDT-001_Harmony"
$devecoBin = "D:\9_infra\DevEco\6.1\bin\devecostudio.bat"

# ── Discover unsigned apps ──
function Get-Brand($appName) {
    if ($appName -like "thinkkit-*") { return "ThinkKit" }
    if ($appName -like "craftsman-*") { return "Craftsman" }
    if ($appName -like "harmonycoder*") { return "HarmonyCoder" }
    if ($appName -like "rhythm-*") { return "RhythmHabit" }
    if ($appName -like "gaokao-*") { return "GaokaoAgent" }
    return "unknown"
}

$unsigned = @()
Get-ChildItem "$root\apps" -Directory | ForEach-Object {
    $bp = "$($_.FullName)\build-profile.json5"
    if (Test-Path $bp) {
        $content = Get-Content $bp -Raw -Encoding UTF8
        if ($content -notmatch '"certpath"') {
            $unsigned += @{
                name = $_.Name
                path = $_.FullName
                brand = (Get-Brand $_.Name)
            }
        }
    }
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " SPDT-001 DevEco Sync Signing" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Unsigned: $($unsigned.Count) apps" -ForegroundColor Yellow
Write-Host ""

if ($ListOnly) {
    $unsigned | ForEach-Object { Write-Host "  [$($_.brand)] $($_.name)" }
    exit 0
}

if ($unsigned.Count -eq 0) {
    Write-Host "All apps signed!" -ForegroundColor Green
    exit 0
}

# ── Batch Sync ──
Write-Host "Strategy: Open $BatchSize projects at a time in DevEco Studio"
Write-Host "  DevEco auto-Sync will inject signingConfigs on first open"
Write-Host "  Wait ${Timeout}s per batch for Sync to complete"
Write-Host ""

$batches = [math]::Ceiling($unsigned.Count / $BatchSize)
$processed = 0
$synced = 0

for ($i = 0; $i -lt $unsigned.Count; $i += $BatchSize) {
    $batch = $unsigned[$i..([Math]::Min($i + $BatchSize - 1, $unsigned.Count - 1))]
    $batchNum = [math]::Floor($i / $BatchSize) + 1
    
    Write-Host "=== Batch $batchNum / $batches ($($batch.Count) apps) ===" -ForegroundColor Cyan
    
    # Open each project in DevEco Studio
    $pids = @()
    foreach ($app in $batch) {
        Write-Host "  Opening: $($app.name)..." -NoNewline
        $process = Start-Process -FilePath $devecoBin -ArgumentList "`"$($app.path)`"" -PassThru
        $pids += $process.Id
        Write-Host " PID $($process.Id)" -ForegroundColor DarkGray
        Start-Sleep -Seconds 2  # Stagger opens to avoid resource spike
    }
    
    # Wait for Sync to complete (DevEco auto-injects signing on first open)
    Write-Host "  Waiting ${Timeout}s for Sync..."
    Start-Sleep -Seconds $Timeout
    
    # Check results
    foreach ($app in $batch) {
        $bp = "$($app.path)\build-profile.json5"
        $content = Get-Content $bp -Raw -Encoding UTF8
        if ($content -match '"certpath"') {
            Write-Host "  [SIGNED] $($app.name)" -ForegroundColor Green
            $synced++
        } else {
            Write-Host "  [UNSIGNED] $($app.name) - may need longer wait or manual check" -ForegroundColor Red
        }
        $processed++
    }
    
    # Close DevEco Studio instances (release memory)
    Write-Host "  Closing DevEco Studio instances..."
    foreach ($pid in $pids) {
        try {
            Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
        } catch {}
    }
    Start-Sleep -Seconds 3
    
    Write-Host ""
}

# ── Summary ──
Write-Host "========================================" -ForegroundColor White
Write-Host " SYNC RESULT: $synced / $processed signed" -ForegroundColor $(if($synced -eq $processed){'Green'}else{'Yellow'})
Write-Host "========================================" -ForegroundColor White

# Check remaining unsigned
$remaining = @()
Get-ChildItem "$root\apps" -Directory | ForEach-Object {
    $bp = "$($_.FullName)\build-profile.json5"
    if (Test-Path $bp) {
        $content = Get-Content $bp -Raw -Encoding UTF8
        if ($content -notmatch '"certpath"') {
            $remaining += $_.Name
        }
    }
}

if ($remaining.Count -gt 0) {
    Write-Host "`nRemaining unsigned ($($remaining.Count)):" -ForegroundColor Red
    $remaining | ForEach-Object { Write-Host "  $_" -ForegroundColor Yellow }
    Write-Host "`nManual step: Open these in DevEco Studio GUI manually" -ForegroundColor Yellow
}

Write-Host "`nNext: python $root\apps\build-all.py --parallel 4" -ForegroundColor Cyan
