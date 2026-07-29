# HarmonyPDT CI - Preflight Stage v3
# Validates project integrity for specified brand (or all brands)
param(
    [string]$BrandPrefix,
    [string]$BrandColor,
    [switch]$ScanAll
)

$appsRoot = "D:\92_products\SPDT-001_Harmony\apps"
$pass = 0
$fail = 0

$prefixes = @("thinkkit-", "craftsman-", "harmonycoder", "rhythm-", "gaokao-")

function GetColor($p) {
    switch ($p) {
        "thinkkit-"    { return "#5B8C5A" }
        "craftsman-"   { return "#E87A2A" }
        "harmonycoder" { return "#7B2D8E" }
        "rhythm-"      { return "#3B82B0" }
        "gaokao-"      { return "#C44536" }
        default        { return "" }
    }
}

function GetBrand($p) {
    switch ($p) {
        "thinkkit-"    { return "ThinkKit" }
        "craftsman-"   { return "Craftsman" }
        "harmonycoder" { return "HarmonyCoder" }
        "rhythm-"      { return "RhythmHabit" }
        "gaokao-"      { return "GaokaoAgent" }
        default        { return "" }
    }
}

function GetPrefix($appName) {
    foreach ($p in $prefixes) {
        if ($appName.StartsWith($p)) { return $p }
    }
    return $null
}

if ($ScanAll) {
    Write-Host "=== PREFLIGHT: ALL BRANDS ===" -ForegroundColor Cyan
} elseif ($BrandPrefix) {
    Write-Host "=== PREFLIGHT: $BrandPrefix ===" -ForegroundColor Cyan
} else {
    Write-Host "=== PREFLIGHT: ALL BRANDS (default) ===" -ForegroundColor Cyan
}

if ($ScanAll -or (-not $BrandPrefix)) {
    $apps = Get-ChildItem $appsRoot -Directory | Where-Object { Test-Path (Join-Path $_.FullName "build-profile.json5") }
} else {
    $apps = Get-ChildItem $appsRoot -Directory | Where-Object { $_.Name.StartsWith($BrandPrefix) -and (Test-Path (Join-Path $_.FullName "build-profile.json5")) }
}

if (-not $apps) {
    Write-Host "[FAIL] No apps found" -ForegroundColor Red
    exit 1
}
Write-Host "Found $($apps.Count) apps"

foreach ($app in $apps) {
    $dir = $app.FullName
    $name = $app.Name
    Write-Host ""
    Write-Host "[CHECK] $name" -ForegroundColor Yellow
    $ok = $true
    
    $pref = GetPrefix $name
    $col = if ($BrandColor) { $BrandColor } else { GetColor $pref }
    $brand = GetBrand $pref

    # 1. build-profile.json5
    $bp = "$dir\build-profile.json5"
    if (Test-Path $bp) {
        $c = Get-Content $bp -Raw -Encoding UTF8
        if ($c -match "compatibleSdkVersion.*24" -or $c -match "5\.0\.\d+\(24\)" -or $c -match "6\.1\.1\(24\)") {
            Write-Host "  [PASS] build-profile.json5 - API 24" -ForegroundColor Green
        } else {
            Write-Host "  [WARN] build-profile.json5 - SDK version?" -ForegroundColor Yellow
        }
    } else {
        Write-Host "  [FAIL] build-profile.json5 - MISSING" -ForegroundColor Red
        $ok = $false
    }

    # 2. oh-package.json5
    $ohp = "$dir\oh-package.json5"
    if (Test-Path $ohp) {
        $c = Get-Content $ohp -Raw -Encoding UTF8
        if ($c -match "modelVersion.*26") {
            Write-Host "  [PASS] oh-package.json5 - modelVersion 26" -ForegroundColor Green
        } else {
            Write-Host "  [WARN] oh-package.json5 - modelVersion != 26" -ForegroundColor Yellow
        }
    } else {
        Write-Host "  [FAIL] oh-package.json5 - MISSING" -ForegroundColor Red
        $ok = $false
    }

    # 3. hvigor-config.json5
    $hc = "$dir\hvigor\hvigor-config.json5"
    if (Test-Path $hc) {
        $c = Get-Content $hc -Raw -Encoding UTF8
        if ($c -match "modelVersion.*26") {
            Write-Host "  [PASS] hvigor-config.json5 - modelVersion 26" -ForegroundColor Green
        } else {
            Write-Host "  [WARN] hvigor-config.json5 - modelVersion != 26" -ForegroundColor Yellow
        }
    } else {
        Write-Host "  [FAIL] hvigor-config.json5 - MISSING" -ForegroundColor Red
        $ok = $false
    }

    # 4. AppScope/app.json5
    $aj = "$dir\AppScope\app.json5"
    if (Test-Path $aj) {
        $c = Get-Content $aj -Raw -Encoding UTF8
        if ($c -match "bundleName") {
            Write-Host "  [PASS] AppScope/app.json5 - bundleName OK" -ForegroundColor Green
        } else {
            Write-Host "  [FAIL] AppScope/app.json5 - no bundleName" -ForegroundColor Red
            $ok = $false
        }
    } else {
        Write-Host "  [FAIL] AppScope/app.json5 - MISSING" -ForegroundColor Red
        $ok = $false
    }

    # 5. module.json5
    $mj = "$dir\entry\src\main\module.json5"
    if (Test-Path $mj) {
        Write-Host "  [PASS] module.json5 - OK" -ForegroundColor Green
    } else {
        Write-Host "  [FAIL] module.json5 - MISSING" -ForegroundColor Red
        $ok = $false
    }

    # 6. pages
    $pages = Get-ChildItem "$dir\entry\src\main\ets\pages\*.ets" -ErrorAction SilentlyContinue
    if ($pages) {
        Write-Host "  [PASS] pages/ - $($pages.Count) files" -ForegroundColor Green
    } else {
        Write-Host "  [FAIL] pages/ - no .ets files" -ForegroundColor Red
        $ok = $false
    }

    # 7. brand color
    if ($col -and $brand) {
        $cfg = "$dir\entry\src\main\ets\app.config.ts"
        if (Test-Path $cfg) {
            Write-Host "  [PASS] brand color - $brand ($col)" -ForegroundColor Green
        } else {
            Write-Host "  [WARN] app.config.ts not found" -ForegroundColor Yellow
        }
    }

    # 8. cross-brand pollution
    $allEts = Get-ChildItem "$dir\entry\src\main\ets" -Recurse -Filter "*.ets" -ErrorAction SilentlyContinue
    $imps = ""
    if ($allEts) {
        $imps = ($allEts | ForEach-Object { Get-Content $_.FullName -Raw -Encoding UTF8 }) -join "`n"
    }
    
    $pollution = $false
    foreach ($ob in $prefixes) {
        if ($ob -eq $pref) { continue }
        if ($imps -match "${ob}/" -or $imps -match "from.*$ob") {
            Write-Host "  [FAIL] Cross-brand pollution: $ob" -ForegroundColor Red
            $pollution = $true
        }
    }
    if (-not $pollution) {
        Write-Host "  [PASS] No cross-brand pollution" -ForegroundColor Green
    } else {
        $ok = $false
    }

    if ($ok) { $pass++ } else { $fail++ }
}

Write-Host ""
Write-Host "=== PREFLIGHT RESULT: $pass pass, $fail fail ===" -ForegroundColor $(if ($fail -eq 0) { "Green" } else { "Red" })
exit $(if ($fail -eq 0) { 0 } else { 1 })
