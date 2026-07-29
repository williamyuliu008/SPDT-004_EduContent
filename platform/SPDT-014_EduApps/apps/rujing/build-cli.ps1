# rujing HarmonyOS App - CLI Build Script
# Usage: .\build-cli.ps1 [-deploy]
$ErrorActionPreference = 'Stop'
$PROJECT_ROOT = $PSScriptRoot
$HAP_OUTPUT_DIR = Join-Path $PROJECT_ROOT 'entry\build\default\outputs\default'

# SDK env (flat SDK requires these)
$env:DEVECO_SDK_HOME = 'D:\9_infra\DevEco\6.1\sdk'
$env:OHOS_BASE_SDK_HOME = 'D:\9_infra\DevEco\6.1\sdk'

$HVIGOR_BAT = 'D:\9_infra\DevEco\6.1\tools\hvigor\bin\hvigorw.bat'

Write-Host '=== rujing CLI build ===' -ForegroundColor Cyan
Write-Host 'Project:' $PROJECT_ROOT

Write-Host ''
Write-Host '[1/3] Running hvigor...' -ForegroundColor Yellow
$hvigorCmd = @(
    $HVIGOR_BAT,
    '--mode', 'module',
    '-p', 'product=default',
    'assembleHap',
    '--analyze=normal',
    '--parallel',
    '--incremental'
)

$startTime = Get-Date
$result = & $hvigorCmd[0] @($hvigorCmd[1..($hvigorCmd.Length-1)]) 2>&1
$exitCode = $LASTEXITCODE
$elapsed = ((Get-Date) - $startTime).TotalSeconds

$result | ForEach-Object { $_ }

if ($exitCode -eq 0 -or ($result -match 'BUILD SUCCESSFUL')) {
    Write-Host ''
    Write-Host ('[OK] hvigor done in {0:N1}s' -f $elapsed) -ForegroundColor Green
} else {
    Write-Host ''
    Write-Host ('[FAIL] hvigor exit: ' + $exitCode) -ForegroundColor Red
    exit $exitCode
}

Write-Host ''
Write-Host '[2/3] Finding HAP...' -ForegroundColor Yellow
$hapFiles = Get-ChildItem $HAP_OUTPUT_DIR -Filter '*.hap' -EA SilentlyContinue
if (-not $hapFiles) {
    Write-Host '[FAIL] No HAP found: ' + $HAP_OUTPUT_DIR -ForegroundColor Red
    exit 1
}
foreach ($hap in $hapFiles) {
    $sz = [math]::Round($hap.Length / 1MB, 2)
    Write-Host ('  -> {0} ({1} MB) {2}' -f $hap.Name, $sz, $hap.LastWriteTime) -ForegroundColor White
}

if ($args -contains '-deploy') {
    Write-Host ''
    Write-Host '[3/3] Deploying...' -ForegroundColor Yellow
    $hdc = 'C:\Users\willi\AppData\Local\OpenHarmony\Sdk\26.0.0\toolchains\hdc.exe'
    $signed = Get-ChildItem $HAP_OUTPUT_DIR -Filter '*-signed.hap' | Select-Object -First 1
    if ($signed) {
        Write-Host ('  Installing: {0}' -f $signed.Name)
        & $hdc install $signed.FullName
        if ($LASTEXITCODE -eq 0) {
            Write-Host '  Install OK, launching...' -ForegroundColor Green
            & $hdc shell aa start -a EntryAbility -b com.harmonystudio.rujing
        } else {
            Write-Host ('  Install failed (hdc: {0})' -f $LASTEXITCODE) -ForegroundColor Red
        }
    } else {
        Write-Host '[WARN] No signed HAP, skipping deploy' -ForegroundColor Yellow
    }
}

Write-Host ''
Write-Host '=== Done ===' -ForegroundColor Cyan