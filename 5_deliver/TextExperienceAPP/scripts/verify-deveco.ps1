# verify-deveco.ps1 — Post-install environment check (EN)
param([switch]$Json)

$allOk = $true
$results = @{ hvigorw = $false; hdc = $false; node = $false; build = "skipped" }

Write-Host "=== DevEco Studio Environment Check ===" -ForegroundColor Cyan

# 1. hvigorw
Write-Host "[1/4] hvigorw..."
$p1 = "$env:LOCALAPPDATA\Huawei\DevEcoStudio\bin\hvigorw.bat"
$p2 = "$env:APPDATA\Huawei\DevEcoStudio\bin\hvigorw.bat"
$p3 = "C:\Program Files\Huawei\DevEcoStudio\bin\hvigorw.bat"
$found1 = $false
foreach ($p in @($p1,$p2,$p3)) { if (Test-Path $p) { Write-Host "  OK: $p" -ForegroundColor Green; $found1=$true; break } }
if (-not $found1) { $g = Get-Command hvigorw -ErrorAction SilentlyContinue; if ($g) { Write-Host "  OK: PATH - $($g.Source)" -ForegroundColor Green; $found1=$true } }
if (-not $found1) { Write-Host "  FAIL: hvigorw not found" -ForegroundColor Red; $allOk=$false }
$results.hvigorw = $found1

# 2. hdc
Write-Host "[2/4] hdc..."
$h1 = "$env:LOCALAPPDATA\Huawei\DevEcoStudio\sdk\default\openharmony\toolchains\hdc.exe"
$h2 = "$env:APPDATA\Huawei\DevEcoStudio\sdk\default\openharmony\toolchains\hdc.exe"
$h3 = "C:\Program Files\Huawei\DevEcoStudio\sdk\default\openharmony\toolchains\hdc.exe"
$found2 = $false
foreach ($p in @($h1,$h2,$h3)) { if (Test-Path $p) { Write-Host "  OK: $p" -ForegroundColor Green; $found2=$true; break } }
$gh = Get-Command hdc -ErrorAction SilentlyContinue
if ($gh -and -not $found2) { Write-Host "  OK: PATH - $($gh.Source)" -ForegroundColor Green; $found2=$true }
if (-not $found2) { Write-Host "  WARN: hdc not found (optional, only needed for device testing)" -ForegroundColor Yellow }
$results.hdc = $found2

# 3. Node.js
Write-Host "[3/4] Node.js..."
$n = Get-Command node -ErrorAction SilentlyContinue
if ($n) { $nv = node -v; Write-Host "  OK: $($n.Source) - $nv" -ForegroundColor Green }
else { Write-Host "  FAIL: Node.js not found" -ForegroundColor Red; $allOk=$false }
$results.node = ($n -ne $null)

# 4. Test build
Write-Host "[4/4] Test build (craftsman-utils)..."
$proj = "D:\92_products\SPDT-001_Harmony\apps\craftsman-utils"
if (Test-Path $proj) {
    $bs = Join-Path $PSScriptRoot "build.ps1"
    if (Test-Path $bs) {
        $out = & powershell -ExecutionPolicy Bypass -File $bs -ProjectPath $proj -Mode debug 2>&1
        if ($LASTEXITCODE -eq 0) { Write-Host "  OK: Build SUCCESS" -ForegroundColor Green; $results.build="pass" }
        else { Write-Host "  FAIL: Build errors found" -ForegroundColor Red; $results.build="fail"; $allOk=$false }
    } else { Write-Host "  SKIP: build.ps1 not found" -ForegroundColor Yellow }
} else { Write-Host "  SKIP: project not found" -ForegroundColor Yellow }

# Summary
Write-Host ""
Write-Host "=== RESULT ===" -ForegroundColor Cyan
Write-Host "hvigorw : $(if($results.hvigorw){'OK'}else{'FAIL'})" -ForegroundColor $(if($results.hvigorw){'Green'}else{'Red'})
Write-Host "hdc     : $(if($results.hdc){'OK'}else{'N/A'})" -ForegroundColor $(if($results.hdc){'Green'}else{'Yellow'})
Write-Host "node    : $(if($results.node){'OK'}else{'FAIL'})" -ForegroundColor $(if($results.node){'Green'}else{'Red'})
Write-Host "build   : $($results.build)" -ForegroundColor $(if($results.build-eq'pass'){'Green'}else{'Yellow'})
Write-Host ""

if ($allOk) {
    Write-Host "*** ALL CHECKS PASSED - Ready to build! ***" -ForegroundColor Green
} else {
    Write-Host "*** Some checks FAILED - see above ***" -ForegroundColor Red
}

if ($Json) { $results | ConvertTo-Json }
exit $(if($allOk){0}else{1})
