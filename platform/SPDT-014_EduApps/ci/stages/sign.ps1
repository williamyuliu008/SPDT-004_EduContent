# HarmonyPDT CI 鈥?Sign 闃舵
# 鑷姩绛惧悕: 閬嶅巻 unsigned HAP 鈫?hap-sign-tool.jar 绛惧悕
param(
    [Parameter(Mandatory=$true)]
    [string]$BrandPrefix         # 濡?"thinkkit-", "craftsman-"
)

$ErrorActionPreference = "Continue"
$java = "D:\9_infra\DevEco\6.1\jbr\bin\java.exe"
$jar = "D:\9_infra\DevEco\6.1\sdk\default\openharmony\toolchains\lib\hap-sign-tool.jar"
$lib = "D:\9_infra\DevEco\6.1\sdk\default\openharmony\toolchains\lib"
$work = "D:\92_products\SPDT-001_Harmony\signing"
$appsBase = "D:\92_products\SPDT-001_Harmony\apps"
$pw = "123456"
$ks = "$work\debug-ks.p12"
$template = "$lib\UnsgnedDebugProfileTemplate.json"

# Bundle name 鏄犲皠琛紙涓?sign-all.ps1 鍚屾锛?$bundleMap = @{
    "craftsman-arkui"     = "com.harmonystudio.craftsman.arkui"
    "craftsman-ohpm"      = "com.harmonystudio.craftsman.ohpm"
    "craftsman-utils"     = "com.harmonystudio.craftsman.utils"
    "craftsman-utils-v2"  = "com.harmonystudio.craftsman.utilsv2"
    "thinkkit-coach"      = "com.harmonystudio.thinkkit.coach"
    "thinkkit-flashcard"  = "com.harmonystudio.thinkkit.flashcard"
    "thinkkit-mindmap"    = "com.harmonystudio.thinkkit.mindmap"
    "thinkkit-reader"     = "com.harmonystudio.thinkkit.reader"
    "thinkkit-zknote"     = "com.harmonystudio.thinkkit.zknote"
    "thinkkit-quiz"       = "com.thinkkit.quiz"
    "rhythm-habit"        = "com.harmonystudio.rhythm.habit"
    "harmonycoder"        = "com.harmonystudio.harmonycoder"
    "gaokao-agent"        = "com.harmonystudio.gaokao.agent"
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " SIGN: $BrandPrefix" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# 纭繚 keystore 鍒濆鍖?if (-not (Test-Path $ks)) {
    Write-Host "Creating debug keystore..."
    & $java -jar $jar generate-keypair -keyAlias "debugKey" -keyPwd $pw -keyAlg ECC -keySize NIST-P-256 -keystoreFile $ks -keystorePwd $pw 2>&1 | Out-Null
    & $java -jar $jar generate-ca -keyAlias "ca-root" -keyPwd $pw -keyAlg ECC -keySize NIST-P-256 -subject "C=CN,O=PDT,OU=Dev,CN=Root CA" -validity 3650 -signAlg SHA256withECDSA -keystoreFile $ks -keystorePwd $pw -outFile "$work\root.cer" 2>&1 | Out-Null
    & $java -jar $jar generate-ca -keyAlias "ca-sub" -keyPwd $pw -keyAlg ECC -keySize NIST-P-256 -issuer "C=CN,O=PDT,OU=Dev,CN=Root CA" -issuerKeyAlias "ca-root" -issuerKeyPwd $pw -subject "C=CN,O=PDT,OU=Dev,CN=App Sign CA" -validity 3650 -signAlg SHA256withECDSA -keystoreFile $ks -keystorePwd $pw -outFile "$work\sub.cer" 2>&1 | Out-Null
    & $java -jar $jar generate-app-cert -keyAlias "debugKey" -keyPwd $pw -issuer "C=CN,O=PDT,OU=Dev,CN=App Sign CA" -issuerKeyAlias "ca-sub" -issuerKeyPwd $pw -subject "C=CN,O=HarmonyPDT,OU=Dev,CN=Debug" -validity 3650 -signAlg SHA256withECDSA -rootCaCertFile "$work\root.cer" -subCaCertFile "$work\sub.cer" -keystoreFile $ks -keystorePwd $pw -outForm certChain -outFile "$work\app-cert.cer" 2>&1 | Out-Null
    Write-Host "Keystore initialised."
}

function Sign-One {
    param([string]$appName, [string]$bundleName)
    
    $appDir = "$appsBase\$appName"
    $unsigned = Get-ChildItem "$appDir\entry\build\default\outputs\default\*unsigned*.hap" -ErrorAction SilentlyContinue | Select-Object -First 1
    
    if (-not $unsigned) {
        Write-Host "  [SKIP] $appName 鈥?no unsigned HAP" -ForegroundColor Yellow
        return @{ app = $appName; result = "skip"; reason = "no unsigned HAP" }
    }
    
    $signed = "$appDir\entry\build\default\outputs\default\$appName-signed.hap"
    
    # 鍒涘缓 profile
    $profileJson = (Get-Content $template -Raw) -replace 'com.OpenHarmony.app.test', $bundleName
    $profileJsonPath = "$work\profile-$appName.json"
    Set-Content $profileJsonPath $profileJson -NoNewline
    
    # 绛惧悕 profile
    $p7b = "$work\profile-$appName.p7b"
    & $java -jar $jar sign-profile -mode localSign -keyAlias "openharmony application profile debug" -keyPwd $pw -profileCertFile "$lib\OpenHarmonyProfileDebug.pem" -inFile $profileJsonPath -signAlg SHA256withECDSA -keystoreFile "$lib\OpenHarmony.p12" -keystorePwd $pw -outFile $p7b 2>&1 | Out-Null
    
    # 绛惧悕 HAP
    try {
        $result = & $java -jar $jar sign-app -mode localSign -keyAlias "debugKey" -keyPwd $pw -appCertFile "$work\app-cert.cer" -profileFile $p7b -inFile $unsigned.FullName -signAlg SHA256withECDSA -keystoreFile $ks -keystorePwd $pw -outFile $signed -compatibleVersion 12 2>&1
        
        if ((Test-Path $signed) -and ($result -join '') -match "sign-app success") {
            $sizeKb = [math]::Round((Get-Item $signed).Length / 1024, 1)
            Write-Host "  [SIGNED] $appName 鈫?$sizeKb KB" -ForegroundColor Green
            return @{ app = $appName; result = "pass"; size_kb = $sizeKb }
        } else {
            Write-Host "  [FAIL] $appName 鈥?sign-app failed" -ForegroundColor Red
            return @{ app = $appName; result = "fail"; reason = "sign-app failed" }
        }
    } catch {
        Write-Host "  [FAIL] $appName 鈥?exception: $_" -ForegroundColor Red
        return @{ app = $appName; result = "fail"; reason = $_.ToString() }
    }
}

# 鍙戠幇鍝佺墝 APP 骞堕€愪釜绛惧悕
$apps = Get-ChildItem $appsBase -Directory | Where-Object { $_.Name -like "$BrandPrefix*" }
$results = @()
$pass = 0
$fail = 0
$skip = 0

foreach ($app in $apps) {
    $bn = $bundleMap[$app.Name]
    if (-not $bn) {
        Write-Host "  [SKIP] $($app.Name) 鈥?unknown bundleName" -ForegroundColor Yellow
        $skip++
        $results += @{ app = $app.Name; result = "skip"; reason = "unknown bundleName" }
        continue
    }
    
    $r = Sign-One $app.Name $bn
    $results += $r
    switch ($r.result) {
        "pass" { $pass++ }
        "fail" { $fail++ }
        "skip" { $skip++ }
    }
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host " SIGN RESULT: $BrandPrefix" -ForegroundColor Cyan
Write-Host "   Signed: $pass | Failed: $fail | Skipped: $skip" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

exit $(if ($fail -eq 0) { 0 } else { 1 })
