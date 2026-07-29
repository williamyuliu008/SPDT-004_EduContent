# SPDT-001 ci-daily.ps1 — 每日 CI 全流程 (cron 8:00 CST)
# Usage: .\scripts\ci-daily.ps1 [-Deploy] [-Brand "thinkkit"] [-SkipPreflight]

param(
    [switch]$Deploy,
    [string]$Brand = "",
    [switch]$SkipPreflight,
    [switch]$DryRun           # 仅报告状态，不实际构建
)

$ErrorActionPreference = "Continue"
$root = "D:\92_products\SPDT-001_Harmony"
$env:DEVECO_SDK_HOME = "D:\9_infra\DevEco\6.1\sdk"
$env:OHOS_BASE_SDK_HOME = "D:\9_infra\DevEco\6.1\sdk"
$reportDir = "$root\ci\reports"
$ts = Get-Date -Format 'yyyyMMdd-HHmm'

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " SPDT-001 Daily CI  —  $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan
if ($Deploy) { Write-Host " Deploy: ENABLED" -ForegroundColor Yellow }
if ($Brand) { Write-Host " Brand : $Brand" -ForegroundColor Yellow }

# ── Stage 1: PREFLIGHT ──
$stageResults = @{}
$overallPass = $true

if (-not $SkipPreflight) {
    Write-Host "`n=== STAGE 1/5: PREFLIGHT ===" -ForegroundColor Cyan
    $pfArgs = @("-ScanAll")
    if ($Brand) { $pfArgs = @("-BrandPrefix", $Brand) }
    $pf = & "$root\ci\stages\preflight.ps1" @pfArgs 2>&1
    $pfText = $pf -join "`n"
    if ($pfText -match "PREFLIGHT RESULT:.*?(\d+) pass.*?(\d+) fail") {
        $stageResults.preflight = @{ pass = [int]$Matches[1]; fail = [int]$Matches[2] }
        $pfStatus = if ($Matches[2] -eq "0") { "PASS" } else { "FAIL" }
        Write-Host "PREFLIGHT: $pfStatus ($($Matches[1]) pass, $($Matches[2]) fail)" -ForegroundColor $(if($Matches[2] -eq "0"){'Green'}else{'Red'})
        if ($Matches[2] -ne "0") { $overallPass = $false }
    }
} else {
    Write-Host "`n=== STAGE 1/5: PREFLIGHT (skipped) ===" -ForegroundColor DarkGray
}

# ── Stage 2: BUILD ──
Write-Host "`n=== STAGE 2/5: BUILD ===" -ForegroundColor Cyan
if ($DryRun) {
    Write-Host "DRY RUN: skipping actual build" -ForegroundColor Yellow
} else {
    $pyArgs = @("D:\92_products\SPDT-001_Harmony\apps\build-all.py")
    if ($Brand) { $pyArgs += "--brand"; $pyArgs += $Brand }
    $pyArgs += "--parallel"; $pyArgs += "4"
    $buildOutput = & python $pyArgs 2>&1
    $buildText = $buildOutput -join "`n"
    Write-Host $buildText
    
    if ($buildText -match "Pass:\s*(\d+).*?Fail:\s*(\d+)") {
        $stageResults.build = @{ pass = [int]$Matches[1]; fail = [int]$Matches[2] }
        if ($Matches[2] -ne "0") { $overallPass = $false }
    } elseif ($buildText -match "(\d+) pass.*?(\d+) fail") {
        $stageResults.build = @{ pass = [int]$Matches[1]; fail = [int]$Matches[2] }
        if ($Matches[2] -ne "0") { $overallPass = $false }
    }
}

# ── Stage 3: SIGN ──
Write-Host "`n=== STAGE 3/5: SIGN ===" -ForegroundColor Cyan
# DevEco 6.1 auto-signs during build; this stage verifies signatures
$signedCount = 0
$unsignedCount = 0
Get-ChildItem "$root\apps" -Directory | ForEach-Object {
    $haps = Get-ChildItem "$($_.FullName)\entry\build\default\outputs\default\*-signed.hap" -EA SilentlyContinue
    if ($haps) { $signedCount++ } else { $unsignedCount++ }
}
Write-Host "Signed HAPs: $signedCount | Unsigned: $unsignedCount"
$stageResults.sign = @{ signed = $signedCount; unsigned = $unsignedCount }

# ── Stage 4: Deploy (optional) ──
if ($Deploy) {
    Write-Host "`n=== STAGE 4/5: DEPLOY ===" -ForegroundColor Cyan
    $deviceArgs = @("`"$root\scripts\deploy-all.ps1`"")
    if ($Brand) { $deviceArgs += "-Brand"; $deviceArgs += $Brand }
    $deviceArgs += "-SkipBuild"
    $deployOutput = & powershell -ExecutionPolicy Bypass -File ($deviceArgs -join ' ') 2>&1
    $deployText = $deployOutput -join "`n"
    Write-Host $deployText
    if ($deployText -match "(\d+) deployed.*?(\d+) failed") {
        $stageResults.deploy = @{ pass = [int]$Matches[1]; fail = [int]$Matches[2] }
    }
} else {
    Write-Host "`n=== STAGE 4/5: DEPLOY (skipped) ===" -ForegroundColor DarkGray
}

# ── Stage 5: OMAS Heartbeat ──
Write-Host "`n=== STAGE 5/5: OMAS HEARTBEAT ===" -ForegroundColor Cyan
$pdtIds = @("HDT-001-TK","HDT-001-CM","HDT-001-HC","HDT-001-RH","HDT-001-GK")
foreach ($pdt in $pdtIds) {
    $checker = "D:\6_agent_project\omas\tools\registry_checker.py"
    if (Test-Path $checker) {
        $hb = & python $checker --touch $pdt 2>&1 | Select-Object -Last 1
        Write-Host "  $pdt : $($hb -join ' ')" -ForegroundColor DarkGray
    } else {
        Write-Host "  $pdt : checker not found" -ForegroundColor DarkGray
    }
}

# ── Report ──
Write-Host ""
Write-Host "========================================" -ForegroundColor White
Write-Host " CI RESULT: $(if($overallPass){'ALL PASS'}else{'ISSUES FOUND'})" -ForegroundColor $(if($overallPass){'Green'}else{'Red'})
Write-Host "========================================" -ForegroundColor White

# Save report
New-Item -ItemType Directory -Force $reportDir | Out-Null
$report = @{
    timestamp = (Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
    brand = if ($Brand) { $Brand } else { "all" }
    stages = $stageResults
    overall = if ($overallPass) { "pass" } else { "fail" }
    deploy = $Deploy
}
$report | ConvertTo-Json -Depth 3 | Out-File "$reportDir\ci-daily-$ts.json" -Encoding utf8
Write-Host "Report: $reportDir\ci-daily-$ts.json" -ForegroundColor Cyan

exit $(if ($overallPass) { 0 } else { 1 })
