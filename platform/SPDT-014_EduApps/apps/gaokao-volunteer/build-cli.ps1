# gaokao-volunteer CLI Build Script
$ErrorActionPreference = 'Stop'
$PROJECT_ROOT = $PSScriptRoot
$HAP_OUTPUT_DIR = Join-Path $PROJECT_ROOT 'entry\build\default\outputs\default'

$env:DEVECO_SDK_HOME = 'D:\9_infra\DevEco\6.1\sdk'
$env:OHOS_BASE_SDK_HOME = 'D:\9_infra\DevEco\6.1\sdk'

$HVIGOR_BAT = 'D:\9_infra\DevEco\6.1\tools\hvigor\bin\hvigorw.bat'

Write-Host '=== gaokao-volunteer build ===' -ForegroundColor Cyan

Push-Location $PROJECT_ROOT
Write-Host '[1/2] Running hvigor...'
$hvigorCmd = @($HVIGOR_BAT, '--mode', 'module', '-p', 'product=default', 'assembleHap', '--analyze=normal', '--parallel', '--incremental')
$result = & $hvigorCmd[0] @($hvigorCmd[1..($hvigorCmd.Length-1)]) 2>&1
$exitCode = $LASTEXITCODE
$result | Select-Object -Last 40

if ($exitCode -eq 0 -or ($result -match 'BUILD SUCCESSFUL')) {
    Write-Host ('[OK] hvigor done') -ForegroundColor Green
} else {
    Write-Host ('[FAIL] hvigor exit: ' + $exitCode) -ForegroundColor Red
    Pop-Location
    exit $exitCode
}

Write-Host ''
Write-Host '[2/2] Finding HAP...'
$hapFiles = Get-ChildItem $HAP_OUTPUT_DIR -Filter '*.hap' -EA SilentlyContinue
if (-not $hapFiles) {
    Write-Host '[FAIL] No HAP found' -ForegroundColor Red
    Pop-Location
    exit 1
}
foreach ($hap in $hapFiles) {
    $sz = [math]::Round($hap.Length / 1MB, 2)
    Write-Host ('  -> {0} ({1} MB)') -f $hap.Name, $sz -ForegroundColor White
}

Pop-Location
Write-Host ''
Write-Host '=== Done ===' -ForegroundColor Cyan
