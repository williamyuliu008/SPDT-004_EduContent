# HarmonyPDT CI - Report Stage v3
# Per-brand build statistics: summary + HAP size tracking
param(
    [Parameter(Mandatory=$true)]
    [string]$BrandPrefix,
    [string]$BuildReportPath
)

$APP_ROOT = "D:\92_products\SPDT-001_Harmony\apps"
$REPORT_DIR = "D:\92_products\SPDT-001_Harmony\ci\reports"
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$dateStamp = Get-Date -Format "yyyyMMdd-HHmmss"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " REPORT: $BrandPrefix" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

if (-not (Test-Path $REPORT_DIR)) {
    New-Item -ItemType Directory -Path $REPORT_DIR -Force | Out-Null
}

$apps = Get-ChildItem $APP_ROOT -Directory | Where-Object { $_.Name.StartsWith($BrandPrefix) }
$reportData = @()

foreach ($app in $apps) {
    $appDir = $app.FullName
    $appName = $app.Name
    
    $unsigned = Get-ChildItem "$appDir\entry\build\default\outputs\default\*unsigned*.hap" -ErrorAction SilentlyContinue | Select-Object -First 1
    $signed = Get-ChildItem "$appDir\entry\build\default\outputs\default\*signed*.hap" -ErrorAction SilentlyContinue | Select-Object -First 1
    
    $entry = @{
        app = $appName
        compiled = $null -ne $unsigned
        signed = $null -ne $signed
        unsigned_kb = if ($unsigned) { [math]::Round($unsigned.Length / 1024, 1) } else { 0 }
        signed_kb = if ($signed) { [math]::Round($signed.Length / 1024, 1) } else { 0 }
    }
    $reportData += $entry
}

$compiledCount = ($reportData | Where-Object { $_.compiled }).Count
$signedCount = ($reportData | Where-Object { $_.signed }).Count
$compiledItems = $reportData | Where-Object { $_.compiled }
$signedItems = $reportData | Where-Object { $_.signed }
$totalHapSize = if ($compiledItems) { ($compiledItems | Measure-Object -Property unsigned_kb -Sum).Sum } else { 0 }
$totalSignedSize = if ($signedItems) { ($signedItems | Measure-Object -Property signed_kb -Sum).Sum } else { 0 }

Write-Host ""
Write-Host "--- Build Summary: $($BrandPrefix.TrimEnd('-')) at $timestamp ---" -ForegroundColor White
Write-Host ("{0,-24} {1,10} {2,10} {3,10}" -f "APP", "COMPILED", "SIGNED", "HAP(KB)") -ForegroundColor Cyan
Write-Host ("{0,-24} {1,10} {2,10} {3,10}" -f "------------------------", "--------", "--------", "--------") -ForegroundColor DarkGray

foreach ($r in $reportData) {
    $compiledStr = if ($r.compiled) { "PASS" } else { "FAIL" }
    $signedStr = if ($r.signed) { "PASS" } else { "FAIL" }
    $color = if ($r.compiled) { "Green" } else { "Red" }
    Write-Host ("{0,-24} {1,10} {2,10} {3,10}" -f $r.app, $compiledStr, $signedStr, $r.unsigned_kb) -ForegroundColor $color
}

Write-Host ("{0,-24} {1,10} {2,10} {3,10}" -f "------------------------", "--------", "--------", "--------") -ForegroundColor DarkGray
Write-Host ("Total: $($apps.Count) apps | $compiledCount compiled | $signedCount signed") -ForegroundColor White
Write-Host ("HAP: $([math]::Round($totalHapSize,1)) KB (unsigned) | $([math]::Round($totalSignedSize,1)) KB (signed)") -ForegroundColor White

$jsonReport = @{
    brand = $BrandPrefix.TrimEnd('-')
    timestamp = $timestamp
    summary = @{
        total = $apps.Count
        compiled = $compiledCount
        signed = $signedCount
        total_unsigned_kb = [math]::Round($totalHapSize, 1)
        total_signed_kb = [math]::Round($totalSignedSize, 1)
    }
    apps = $reportData
} | ConvertTo-Json -Depth 2

$jsonFile = "$REPORT_DIR\report-$($BrandPrefix.TrimEnd('-'))-$dateStamp.json"
Set-Content $jsonFile $jsonReport -Encoding UTF8

$mdLines = @()
$mdLines += "# $($BrandPrefix.TrimEnd('-')) Build Report"
$mdLines += ""
$mdLines += "> Generated: $timestamp | Total: $($apps.Count) apps"
$mdLines += ""
$mdLines += "## Summary"
$mdLines += ""
$mdLines += "| Metric | Value |"
$mdLines += "|:---|---|"
$mdLines += "| Compiled | $compiledCount / $($apps.Count) |"
$mdLines += "| Signed | $signedCount / $($apps.Count) |"
$mdLines += "| HAP Total (unsigned) | $([math]::Round($totalHapSize, 1)) KB |"
$mdLines += "| HAP Total (signed) | $([math]::Round($totalSignedSize, 1)) KB |"
$mdLines += ""
$mdLines += "## App Details"
$mdLines += ""
$mdLines += "| APP | Compiled | Signed | HAP(KB) |"
$mdLines += "|:---|:---|:---|:---|"
foreach ($r in $reportData) {
    $c = if ($r.compiled) { "PASS" } else { "FAIL" }
    $s = if ($r.signed) { "PASS" } else { "FAIL" }
    $mdLines += "| $($r.app) | $c | $s | $($r.unsigned_kb) |"
}

$mdFile = "$REPORT_DIR\report-$($BrandPrefix.TrimEnd('-'))-$dateStamp.md"
Set-Content $mdFile ($mdLines -join "`n") -Encoding UTF8

Write-Host ""
Write-Host "Reports:" -ForegroundColor Gray
Write-Host "  JSON: $jsonFile" -ForegroundColor Gray
Write-Host "  MD:   $mdFile" -ForegroundColor Gray
Write-Host "========================================" -ForegroundColor Cyan

exit 0
