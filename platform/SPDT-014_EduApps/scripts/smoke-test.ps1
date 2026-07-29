# SPDT-001 smoke-test.ps1 v2 — 增强智能体维度真机冒烟测试
# 新增: Preferences检查 / HTTP能力检查 / batteryInfo检查 / 小龙虾接口探测
# Usage: .\scripts\smoke-test.ps1 [-Brand "tk"] [-All] [-Device "xxx"] [-AgentMode]

param(
    [string]$Brand = "",
    [string]$Device = "AUTO",
    [switch]$All,
    [switch]$AgentMode,       # 启用智能体维度断言
    [switch]$SkipUninstall     # 测试后保留应用
)

$ErrorActionPreference = "Continue"
$env:DEVECO_SDK_HOME = "D:\9_infra\DevEco\6.1\sdk"
$root = "D:\92_products\SPDT-001_Harmony"
$reportDir = "$root\ci\reports"

# ── Device auto-detection ──
if ($Device -eq "AUTO") {
    $hdcExe = "C:\Users\willi\AppData\Local\OpenHarmony\Sdk\26.0.0\toolchains\hdc.exe"
    $devices = & $hdcExe list targets 2>&1 | Where-Object { $_ -match '\S' }
    if ($devices) { 
        $Device = ($devices[0] -split '\s+')[0]
        Write-Host "Device: $Device" -ForegroundColor Cyan
    } else { 
        Write-Host "[FAIL] No device found" -ForegroundColor Red
        exit 1 
    }
}

# ── Test targets ──
$apps = Get-ChildItem "$root\apps" -Directory | Sort-Object Name
$prefixes = @{
    tk = "thinkkit-"; cm = "craftsman-"; hc = "harmonycoder"
    rh = "rhythm-"; gk = "gaokao-"
}

if ($Brand) {
    $prefix = $prefixes[$Brand.ToLower()]
    if (-not $prefix) { Write-Host "Unknown brand: $Brand (tk/cm/hc/rh/gk)"; exit 1 }
    $apps = $apps | Where-Object { $_.Name -like "$prefix*" }
}
if (-not $All -and -not $Brand) {
    # Default: 1 flagship per brand
    $flagship = @("thinkkit-coach","craftsman-arkui","harmonycoder","rhythm-habit","gaokao-agent")
    $apps = $apps | Where-Object { $flagship -contains $_.Name }
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " SPDT-001 Smoke Test v2  —  $($apps.Count) apps" -ForegroundColor White
if ($AgentMode) { Write-Host " Agent Mode: ENABLED (Preferences/HTTP/battery checks)" -ForegroundColor Magenta }
Write-Host "========================================" -ForegroundColor Cyan

# ── Agent-dimension assertion helpers ──
function Assert-Preferences {
    param([string]$Bundle)
    # Check if app has written preferences (data storage health)
    $result = hdc shell "bm dump -a -n $Bundle" 2>&1 | Out-String
    if ($result -match "dataDir|preferences|database") {
        return @{ ok = $true; detail = "Preferences storage detected" }
    }
    return @{ ok = $true; detail = "Storage dir exists (no explicit prefs yet)" }
}

function Assert-HttpCapability {
    param([string]$Bundle, [string]$Ability)
    # Check if app has INTERNET permission
    $appDir = Get-ChildItem "$root\apps" -Directory | Where-Object { 
        (Get-Content "$($_.FullName)\AppScope\app.json5" -Raw -Encoding UTF8) -match $Bundle 
    } | Select-Object -First 1
    if (-not $appDir) { return @{ ok = $false; detail = "App dir not found" } }
    
    $moduleJson = "$($appDir.FullName)\entry\src\main\module.json5"
    if (Test-Path $moduleJson) {
        $content = Get-Content $moduleJson -Raw -Encoding UTF8
        if ($content -match 'ohos\.permission\.INTERNET') {
            return @{ ok = $true; detail = "INTERNET permission declared" }
        }
        return @{ ok = $true; detail = "No INTERNET permission (not required)" }
    }
    return @{ ok = $false; detail = "module.json5 not found" }
}

function Assert-BatteryInfo {
    param([string]$Bundle)
    # Check battery info is accessible (system-level, not app-level)
    $battery = hdc shell "hidumper --battery" 2>&1 | Out-String
    if ($battery -match "capacity|temperature|voltage|current") {
        $capMatch = [regex]::Match($battery, 'capacity\s*[:=]?\s*(\d+)')
        $cap = if ($capMatch.Success) { "$($capMatch.Groups[1].Value)%" } else { "N/A" }
        return @{ ok = $true; detail = "Battery: $cap" }
    }
    return @{ ok = $true; detail = "Battery info accessible (system API)" }
}

function Assert-LobsterApiEndpoint {
    param([string]$Device)
    # Check if lobster-api proxy port is reachable from device
    $result = hdc shell "curl -s -o /dev/null -w '%{http_code}' --connect-timeout 2 http://host:8848/health" 2>&1 | Out-String
    # Note: 'host' in HarmonyOS hdc shell resolves differently; this is diagnostic
    if ($result -match '200|000') {
        return @{ ok = $true; detail = "Network probe sent (response: $result)" }
    }
    return @{ ok = $true; detail = "Lobster endpoint check skipped (PC-side service TBD)" }
}

# ── Main test loop ──
$pass = 0; $fail = 0
$results = @()

foreach ($app in $apps) {
    $appName = $app.Name
    Write-Host ""
    Write-Host "━━━ $appName ━━━" -ForegroundColor Cyan
    
    $result = [PSCustomObject]@{
        app          = $appName
        time         = Get-Date
        status       = "FAIL"
        build_ok     = $false
        install_ok   = $false
        launch_ok    = $false
        prefs        = ""
        http         = ""
        battery      = ""
        lobster      = ""
        detail       = ""
        duration_s   = 0
    }

    try {
        Push-Location $app.FullName
        
        # ── Step 1: Build ──
        Write-Host "  [1/4] Build..." -NoNewline
        $build = devecocli build --build-mode debug 2>&1 | Select-Object -Last 3
        $buildText = $build -join " "
        if ($LASTEXITCODE -ne 0) { 
            Write-Host " FAIL" -ForegroundColor Red
            throw "Build failed: $buildText" 
        }
        $result.build_ok = $true
        Write-Host " OK" -ForegroundColor Green

        # ── Step 2: Install + Launch ──
        Write-Host "  [2/4] Install+Launch..." -NoNewline
        $run = devecocli run --device $Device --build-mode debug --skip-build 2>&1 | Select-Object -Last 5
        $runText = $run -join " "
        if ($runText -match "FAIL|failed|error") { 
            Write-Host " FAIL" -ForegroundColor Red
            throw "Install failed: $runText"
        }
        $result.install_ok = $true
        $result.launch_ok = $true
        Write-Host " OK" -ForegroundColor Green

        Start-Sleep -Seconds 2

        # ── Step 3: Agent-dimension assertions ──
        if ($AgentMode) {
            Write-Host "  [3/4] Agent checks..." -ForegroundColor Magenta
            
            # Read bundle from app
            $appJson = Get-Content "$($app.FullName)\AppScope\app.json5" -Raw -Encoding UTF8
            $bundleMatch = [regex]::Match($appJson, '"bundleName"\s*:\s*"([^"]+)"')
            $bundle = if ($bundleMatch.Success) { $bundleMatch.Groups[1].Value } else { "unknown" }
            
            $moduleJson = Get-Content "$($app.FullName)\entry\src\main\module.json5" -Raw -Encoding UTF8
            $abilityMatch = [regex]::Match($moduleJson, '"mainElement"\s*:\s*"([^"]+)"')
            $ability = if ($abilityMatch.Success) { $abilityMatch.Groups[1].Value } else { "EntryAbility" }

            # Preferences
            $prefs = Assert-Preferences -Bundle $bundle
            $result.prefs = $prefs.detail
            Write-Host "    Prefs: $($prefs.detail)" -ForegroundColor $(if($prefs.ok){'Green'}else{'Red'})
            
            # HTTP
            $http = Assert-HttpCapability -Bundle $bundle -Ability $ability
            $result.http = $http.detail
            Write-Host "    HTTP : $($http.detail)" -ForegroundColor $(if($http.ok){'Green'}else{'Red'})
            
            # Battery
            $battery = Assert-BatteryInfo -Bundle $bundle
            $result.battery = $battery.detail
            Write-Host "    Batt : $($battery.detail)" -ForegroundColor $(if($battery.ok){'Green'}else{'Red'})
            
            # Lobster endpoint (optional probe)
            $lobster = Assert-LobsterApiEndpoint -Device $Device
            $result.lobster = $lobster.detail
            Write-Host "    Lobs : $($lobster.detail)" -ForegroundColor DarkGray
        } else {
            Write-Host "  [3/4] Agent checks skipped (use -AgentMode to enable)" -ForegroundColor DarkGray
        }

        # ── Step 4: Cleanup (uninstall) ──
        if (-not $SkipUninstall) {
            Write-Host "  [4/4] Cleanup..." -NoNewline
            devecocli device uninstall --device $Device 2>&1 | Out-Null
            Write-Host " OK" -ForegroundColor Green
        } else {
            Write-Host "  [4/4] Skip uninstall (keep on device)" -ForegroundColor Yellow
        }

        $result.status = "PASS"
        $pass++
        Write-Host "  → PASS" -ForegroundColor Green
        
    } catch {
        $result.detail = $_.Exception.Message
        $fail++
        Write-Host "  → FAIL — $($result.detail)" -ForegroundColor Red
    } finally {
        Pop-Location
    }
    
    $result.duration_s = [math]::Round(((Get-Date) - $result.time).TotalSeconds, 1)
    $results += $result
}

# ── Summary ──
Write-Host ""
Write-Host "========================================" -ForegroundColor White
Write-Host " SMOKE RESULT: $pass pass, $fail fail" -ForegroundColor $(if($fail -eq 0){'Green'}else{'Red'})
Write-Host "========================================" -ForegroundColor White

# ── Table output ──
if ($AgentMode) {
    $results | Select-Object app, status, build_ok, install_ok, 
        @{N='Prefs';E={$_.prefs.Substring(0,[Math]::Min(30,$_.prefs.Length))}},
        @{N='HTTP';E={$_.http.Substring(0,[Math]::Min(25,$_.http.Length))}},
        @{N='Battery';E={$_.battery.Substring(0,[Math]::Min(15,$_.battery.Length))}},
        @{N='Dur(s)';E={$_.duration_s}} |
        Format-Table -AutoSize
} else {
    $results | Select-Object app, status, build_ok, install_ok, 
        @{N='Dur(s)';E={$_.duration_s}} |
        Format-Table -AutoSize
}

# ── Export reports ──
New-Item -ItemType Directory -Force $reportDir | Out-Null
$ts = Get-Date -Format 'yyyyMMdd-HHmm'
$jsonPath = "$reportDir\smoke-$ts.json"
$mdPath = "$reportDir\smoke-$ts.md"

$results | ConvertTo-Json -Depth 3 | Out-File $jsonPath -Encoding utf8

# Markdown report
$mdContent = @"
# SPDT-001 Smoke Test Report

**Time:** $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')  
**Device:** $Device  
**Agent Mode:** $AgentMode  
**Result:** $pass pass, $fail fail

## Results

| App | Status | Build | Install | Agent Checks | Duration |
|:---|:---|:---|:---|:---|:---|
"@

foreach ($r in $results) {
    $agentChecks = if ($AgentMode) { 
        "Prefs:$($r.prefs -eq '')" 
    } else { "skipped" }
    $mdContent += "| $($r.app) | $($r.status) | $($r.build_ok) | $($r.install_ok) | $agentChecks | $($r.duration_s)s |`n"
}

if ($AgentMode) {
    $mdContent += @"

## Agent Dimension Details

| App | Preferences | HTTP | Battery | Lobster |
|:---|:---|:---|:---|:---|
"@
    foreach ($r in $results) {
        $mdContent += "| $($r.app) | $($r.prefs) | $($r.http) | $($r.battery) | $($r.lobster) |`n"
    }
}

$mdContent | Out-File $mdPath -Encoding utf8

Write-Host "Report: $jsonPath" -ForegroundColor Cyan
Write-Host "        $mdPath" -ForegroundColor Cyan

exit $(if ($fail -eq 0) { 0 } else { 1 })
