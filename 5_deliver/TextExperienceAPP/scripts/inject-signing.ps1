# SPDT-001 inject-signing.ps1 — 批量 DevEco 签名配置注入
# 为 16 个未签名 APP 自动注入 signingConfigs
# 策略: 通过 devecocli run (debug mode) 触发 DevEco 自动签名生成
# Usage: .\scripts\inject-signing.ps1 [-DryRun] [-Parallel <n>]

param(
    [switch]$DryRun,
    [int]$Parallel = 3,
    [string]$Device = "7GL0226313016118"
)

$ErrorActionPreference = "Continue"
$root = "D:\92_products\SPDT-001_Harmony"
$env:DEVECO_SDK_HOME = "D:\9_infra\DevEco\6.1\sdk"
$env:OHOS_BASE_SDK_HOME = "D:\9_infra\DevEco\6.1\sdk"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " SPDT-001 Signing Config Injection" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Device : $Device"
Write-Host "Mode   : $(if($DryRun){'DRY RUN'}else{'INJECT'})"
Write-Host ""

function Get-Brand($appName) {
    if ($appName -like "thinkkit-*") { return "ThinkKit" }
    if ($appName -like "craftsman-*") { return "Craftsman" }
    if ($appName -like "harmonycoder*") { return "HarmonyCoder" }
    if ($appName -like "rhythm-*") { return "RhythmHabit" }
    if ($appName -like "gaokao-*") { return "GaokaoAgent" }
    return "unknown"
}

# Discover unsigned apps
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

Write-Host "Unsigned apps: $($unsigned.Count)" -ForegroundColor Yellow
foreach ($u in $unsigned) {
    Write-Host "  [WARN] $($u.name)  [$($u.brand)]" -ForegroundColor Yellow
}

if ($DryRun) {
    Write-Host "`n=== DRY RUN COMPLETE (no changes) ===" -ForegroundColor Cyan
    Write-Host "`nTo actually inject signing configs, remove -DryRun flag."
    Write-Host "`nRecommended approaches:"
    Write-Host "  A. DevEco Studio GUI: Open each app → File → Sync → Close (auto-injects)"
    Write-Host "  B. devecocli batch: Run this script without -DryRun"
    Write-Host "  C. Manual: Copy signingConfigs from a signed app, update cert paths"
    exit 0
}

if ($unsigned.Count -eq 0) {
    Write-Host "All apps already have signing configs!" -ForegroundColor Green
    exit 0
}

# Strategy: Run 'devecocli build' on each unsigned app
# DevEco CLI 6.1 should auto-generate debug signing on first build
Write-Host "`n=== Injecting signing configs ===" -ForegroundColor Cyan

$pass = 0; $fail = 0
$injected = @()

# Try method A: devecocli build (should trigger auto-signing)
foreach ($u in $unsigned) {
    Write-Host "`n[INJECT] $($u.name)..." -ForegroundColor Cyan -NoNewline
    Push-Location $u.path
    
    try {
        # Method 1: devecocli build (debug mode triggers auto-signing)
        $result = devecocli build --build-mode debug 2>&1
        $text = $result -join " "
        
        if ($LASTEXITCODE -eq 0) {
            # Check if signingConfigs was injected
            $bp = "$($u.path)\build-profile.json5"
            $content = Get-Content $bp -Raw -Encoding UTF8
            if ($content -match '"certpath"') {
                Write-Host " SIGNED" -ForegroundColor Green
                $pass++
                $injected += @{ name = $u.name; method = "devecocli-build" }
            } else {
                # Build succeeded but no signing — try Method 2
                Write-Host " BUILT (no sign)" -ForegroundColor Yellow
                
                # Method 2: Run devecocli run to force auto-signing
                Write-Host "  Trying devecocli run..." -ForegroundColor DarkGray -NoNewline
                $runResult = devecocli run --device $Device --build-mode debug 2>&1
                
                $bp = "$($u.path)\build-profile.json5"
                $content = Get-Content $bp -Raw -Encoding UTF8
                if ($content -match '"certpath"') {
                    Write-Host " SIGNED" -ForegroundColor Green
                    $pass++
                    $injected += @{ name = $u.name; method = "devecocli-run" }
                } else {
                    Write-Host " STILL UNSIGNED" -ForegroundColor Red
                    $fail++
                    $injected += @{ name = $u.name; method = "FAILED" }
                }
            }
        } else {
            Write-Host " BUILD FAILED" -ForegroundColor Red
            $fail++
            $injected += @{ name = $u.name; method = "BUILD_FAILED" }
        }
    } catch {
        Write-Host " ERROR: $_" -ForegroundColor Red
        $fail++
    } finally {
        Pop-Location
    }
}

# Summary
Write-Host ""
Write-Host "========================================" -ForegroundColor White
Write-Host " INJECT RESULT: $pass injected, $fail failed" -ForegroundColor $(if($fail -eq 0){'Green'}else{'Red'})
Write-Host "========================================" -ForegroundColor White

foreach ($i in $injected) {
    $icon = if ($i.method -eq "FAILED" -or $i.method -eq "BUILD_FAILED") { "[FAIL]" } else { "[OK]" }
    Write-Host "  $icon $($i.name) — $($i.method)"
}

if ($fail -gt 0) {
    Write-Host "`nFailed apps need DevEco Studio GUI Sync:" -ForegroundColor Yellow
    $injected | Where-Object { $_.method -eq "FAILED" -or $_.method -eq "BUILD_FAILED" } | ForEach-Object {
        Write-Host "  → Open in DevEco Studio: $($_.name)" -ForegroundColor Yellow
    }
    Write-Host "`nSteps: File → Open Project → select app folder → wait for Sync → close" -ForegroundColor DarkGray
}

# Export
$report = @{
    timestamp = (Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
    total = $unsigned.Count
    pass = $pass
    fail = $fail
    results = $injected
}
$reportPath = "$root\ci\reports\signing-inject-$(Get-Date -Format 'yyyyMMdd-HHmm').json"
New-Item -ItemType Directory -Force (Split-Path $reportPath) | Out-Null
$report | ConvertTo-Json -Depth 3 | Out-File $reportPath -Encoding utf8
Write-Host "Report: $reportPath" -ForegroundColor Cyan

exit $(if ($fail -eq 0) { 0 } else { 1 })
