# HarmonyPDT CI 鈥?Build 闃舵
# 鎵归噺缂栬瘧鎸囧畾鍝佺墝涓嬫墍鏈?APP
param(
    [Parameter(Mandatory=$true)]
    [string]$BrandPrefix,        # 濡?"thinkkit-", "craftsman-", "rhythm-", "gaokao-"
    [switch]$Parallel            # 骞惰缂栬瘧锛堥粯璁や覆琛屼互鍑忓皯璧勬簮鍐茬獊锛?)

$ErrorActionPreference = "Continue"
$APP_ROOT = "D:\92_products\SPDT-001_Harmony\apps"
$HVIGORW = "D:\9_infra\DevEco\6.1\tools\hvigor\bin\hvigorw.bat"
$SDK_HOME = "D:\9_infra\DevEco\6.1\sdk"
$NODE_PATH = "D:\9_infra\DevEco\6.1\tools\node"
$REPORT_DIR = "D:\92_products\SPDT-001_Harmony\ci\reports"

$env:OHOS_SDK_HOME = $SDK_HOME
$env:PATH = "$NODE_PATH;$env:PATH"

# 纭繚鎶ュ憡鐩綍瀛樺湪
if (-not (Test-Path $REPORT_DIR)) {
    New-Item -ItemType Directory -Path $REPORT_DIR -Force | Out-Null
}

$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$reportFile = "$REPORT_DIR\build-$BrandPrefix-$timestamp.json"

# 鍙戠幇鍝佺墝 APP
$apps = Get-ChildItem $APP_ROOT -Directory | Where-Object { $_.Name -like "$BrandPrefix*" }
if (-not $apps) {
    Write-Host "[SKIP] BUILD: No apps found for prefix '$BrandPrefix'" -ForegroundColor Yellow
    exit 0
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " BUILD: $BrandPrefix ($($apps.Count) apps)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$results = @()
$pass = 0
$fail = 0
$startTime = Get-Date

function Build-One {
    param([string]$appName, [string]$appDir)
    
    Write-Host "`n[BUILD] $appName..." -ForegroundColor Gray
    $appStart = Get-Date
    
    Push-Location $appDir
    try {
        $output = & $HVIGORW assembleHap 2>&1
        $buildLog = $output -join "`n"
        $elapsed = [math]::Round(((Get-Date) - $appStart).TotalSeconds, 1)
        
        if ($buildLog -match "BUILD SUCCESSFUL") {
            # 鎻愬彇 HAP 鏂囦欢
            $hap = Get-ChildItem "$appDir\entry\build\default\outputs\default\*unsigned*.hap" -ErrorAction SilentlyContinue | Select-Object -First 1
            $hapName = if ($hap) { $hap.Name } else { "unknown" }
            $hapSize = if ($hap) { [math]::Round($hap.Length / 1024, 1) } else { 0 }
            
            # 鎻愬彇璀﹀憡璁℃暟
            $warnCount = ([regex]::Matches($buildLog, "WARN:")).Count
            
            Write-Host "  [PASS] $appName 鈥?$hapName ($hapSize KB) | ${elapsed}s | $warnCount warning(s)" -ForegroundColor Green
            
            return @{
                app = $appName
                result = "pass"
                hap = $hapName
                size_kb = $hapSize
                duration_s = $elapsed
                warnings = $warnCount
                errors = 0
            }
        } else {
            # 鎻愬彇閿欒淇℃伅
            $errMatch = [regex]::Match($buildLog, "ERROR:.*?(?=\r?\n)")
            $errMsg = if ($errMatch.Success) { $errMatch.Value.Trim() } else { "build failed" }
            
            Write-Host "  [FAIL] $appName 鈥?${elapsed}s 鈥?$errMsg" -ForegroundColor Red
            
            return @{
                app = $appName
                result = "fail"
                hap = ""
                size_kb = 0
                duration_s = $elapsed
                warnings = 0
                errors = 1
                error_msg = $errMsg
            }
        }
    } catch {
        Write-Host "  [FAIL] $appName 鈥?exception: $_" -ForegroundColor Red
        return @{
            app = $appName
            result = "fail"
            hap = ""
            size_kb = 0
            duration_s = 0
            warnings = 0
            errors = 1
            error_msg = $_.ToString()
        }
    } finally {
        Pop-Location
    }
}

# 缂栬瘧鎵€鏈?APP
if ($Parallel) {
    # 骞惰妯″紡: 浣跨敤 PowerShell Jobs
    Write-Host "Running in parallel mode..."
    $jobs = @()
    foreach ($app in $apps) {
        $jobName = $app.Name
        $jobDir = $app.FullName
        $jobs += Start-Job -Name $jobName -ScriptBlock {
            param($n, $d, $h, $s, $p)
            $env:OHOS_SDK_HOME = $s
            $env:PATH = "$p;$env:PATH"
            Push-Location $d
            try {
                $out = & $h assembleHap 2>&1
                $log = $out -join "`n"
                if ($log -match "BUILD SUCCESSFUL") {
                    $hapFile = Get-ChildItem "$d\entry\build\default\outputs\default\*unsigned*.hap" -ErrorAction SilentlyContinue | Select-Object -First 1
                    "$n|pass|$($hapFile?.Name ?? 'unknown')|$([math]::Round(($hapFile?.Length ?? 0)/1024,1))|0"
                } else {
                    "$n|fail||0|1"
                }
            } catch {
                "$n|fail||0|1"
            } finally {
                Pop-Location
            }
        } -ArgumentList $app.Name, $app.FullName, $HVIGORW, $SDK_HOME, $NODE_PATH
    }
    
    # 绛夊緟鎵€鏈?Job 瀹屾垚
    $jobs | Wait-Job | Out-Null
    foreach ($job in $jobs) {
        $result = $job | Receive-Job
        $parts = $result -split '\|'
        $results += @{
            app = $parts[0]
            result = $parts[1]
            hap = $parts[2]
            size_kb = [double]$parts[3]
            warnings = [int]$parts[4]
            duration_s = 0
        }
        if ($parts[1] -eq "pass") { $pass++ } else { $fail++ }
        $job | Remove-Job -Force
    }
} else {
    # 涓茶妯″紡
    foreach ($app in $apps) {
        $r = Build-One $app.Name $app.FullName
        $results += $r
        if ($r.result -eq "pass") { $pass++ } else { $fail++ }
    }
}

$totalElapsed = [math]::Round(((Get-Date) - $startTime).TotalSeconds, 1)

# 杈撳嚭缁撴灉
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host " BUILD RESULT: $BrandPrefix" -ForegroundColor Cyan
Write-Host "   Pass: $pass | Fail: $fail | Total: $($apps.Count) | ${totalElapsed}s" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# 鍐欏叆 JSON 鎶ュ憡
$report = @{
    brand = $BrandPrefix.TrimEnd('-')
    timestamp = $timestamp
    total = $apps.Count
    pass = $pass
    fail = $fail
    duration_s = $totalElapsed
    results = $results
} | ConvertTo-Json -Depth 3

Set-Content $reportFile $report -Encoding UTF8
Write-Host "Report: $reportFile" -ForegroundColor Gray

exit $(if ($fail -eq 0) { 0 } else { 1 })
