# HarmonyPDT CI 鈥?Deploy 闃舵锛堝彲閫夛級
# 璁惧閮ㄧ讲: hdc install + aa start 鍐峰惎鍔ㄩ獙璇?param(
    [Parameter(Mandatory=$true)]
    [string]$BrandPrefix,        # 濡?"thinkkit-"
    [switch]$InstallOnly         # 浠呭畨瑁咃紝涓嶅惎鍔?)

$ErrorActionPreference = "Continue"
$HDC = "D:\9_infra\DevEco\6.1\sdk\default\openharmony\toolchains\hdc.exe"
$appsBase = "D:\92_products\SPDT-001_Harmony\apps"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " DEPLOY: $BrandPrefix" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# 妫€娴嬭澶?try {
    $targets = (& $HDC list targets 2>&1) -join ''
    if (-not $targets -or $targets -match "empty") {
        Write-Host "[SKIP] No device connected 鈥?hdc list targets return empty" -ForegroundColor Yellow
        exit 0
    }
    Write-Host "[DEVICE] $targets" -ForegroundColor Gray
} catch {
    Write-Host "[SKIP] hdc not available: $_" -ForegroundColor Yellow
    exit 0
}

# 鍙戠幇鍝佺墝 APP 鐨勫凡绛惧悕 HAP
$apps = Get-ChildItem $appsBase -Directory | Where-Object { $_.Name -like "$BrandPrefix*" }
$results = @()
$pass = 0
$fail = 0
$skip = 0

foreach ($app in $apps) {
    $appDir = $app.FullName
    $appName = $app.Name
    
    # 浼樺厛鎵?signed HAP锛屽啀閫€鑰屾眰 unsigned
    $hapFile = Get-ChildItem "$appDir\entry\build\default\outputs\default\*signed*.hap" -ErrorAction SilentlyContinue | Select-Object -First 1
    if (-not $hapFile) {
        $hapFile = Get-ChildItem "$appDir\entry\build\default\outputs\default\*unsigned*.hap" -ErrorAction SilentlyContinue | Select-Object -First 1
    }
    
    if (-not $hapFile) {
        Write-Host "  [SKIP] $appName 鈥?no HAP found" -ForegroundColor Yellow
        $skip++
        $results += @{ app = $appName; result = "skip"; reason = "no HAP" }
        continue
    }
    
    Write-Host "`n[DEPLOY] $appName 鈫?$($hapFile.Name) ($([math]::Round($hapFile.Length/1024,1)) KB)" -ForegroundColor Gray
    
    # 鍗歌浇鏃х増鏈紙濡傛灉瀛樺湪锛?    $bundleName = $null
    $aj = "$appDir\AppScope\app.json5"
    if (Test-Path $aj) {
        $content = Get-Content $aj -Raw
        $match = [regex]::Match($content, '"bundleName"\s*:\s*"([^"]+)"')
        if ($match.Success) {
            $bundleName = $match.Groups[1].Value
            $uninstall = & $HDC shell bm uninstall -n $bundleName 2>&1 | Out-Null
        }
    }
    
    # 瀹夎
    try {
        $install = & $HDC install $hapFile.FullName 2>&1
        if ($LASTEXITCODE -eq 0 -or $install -join '' -match "success" -or $install -join '' -match "install bundle successfully") {
            Write-Host "  [PASS] $appName 鈥?installed" -ForegroundColor Green
            $pass++
            $results += @{ app = $appName; result = "pass"; action = "install" }
            
            # 鍐峰惎鍔ㄩ獙璇?            if (-not $InstallOnly -and $bundleName) {
                $start = & $HDC shell aa start -a EntryAbility -b $bundleName 2>&1
                if ($LASTEXITCODE -eq 0 -or $start -join '' -match "start successfully") {
                    Write-Host "         鈫?cold start: OK" -ForegroundColor Green
                    $results[-1].cold_start = "pass"
                    Start-Sleep -Seconds 1
                } else {
                    Write-Host "         鈫?cold start: FAIL" -ForegroundColor Yellow
                    $results[-1].cold_start = "warn"
                }
            }
        } else {
            Write-Host "  [FAIL] $appName 鈥?install failed: $($install -join ' ')" -ForegroundColor Red
            $fail++
            $results += @{ app = $appName; result = "fail"; reason = $install -join ' ' }
        }
    } catch {
        Write-Host "  [FAIL] $appName 鈥?exception: $_" -ForegroundColor Red
        $fail++
        $results += @{ app = $appName; result = "fail"; reason = $_.ToString() }
    }
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host " DEPLOY RESULT: $BrandPrefix" -ForegroundColor Cyan
Write-Host "   Deployed: $pass | Failed: $fail | Skipped: $skip" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

exit $(if ($fail -eq 0) { 0 } else { 1 })
