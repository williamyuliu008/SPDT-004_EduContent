# rujing Build - Debug mode
$ErrorActionPreference = 'Stop'
$PROJECT_ROOT = $PSScriptRoot

$env:JAVA_HOME = 'D:\3_infra\DevEco\6.1\jbr'
$env:PATH = 'D:\3_infra\DevEco\6.1\jbr\bin;' + $env:PATH
$env:DEVECO_SDK_HOME = 'D:\3_infra\DevEco\6.1\sdk'
$env:OHOS_BASE_SDK_HOME = 'D:\3_infra\DevEco\6.1\sdk'

Write-Host "=== rujing build debug ===" -ForegroundColor Cyan

$HVIGOR = 'D:\3_infra\DevEco\6.1\tools\hvigor\bin\hvigorw.bat'

$result = & $HVIGOR --mode module -p product=default assembleHap --no-daemon --stacktrace 2>&1
$exitCode = $LASTEXITCODE

$result | ForEach-Object { $_ }

if ($exitCode -eq 0) {
    Write-Host "BUILD SUCCESSFUL" -ForegroundColor Green
} else {
    Write-Host "BUILD FAILED (exit $exitCode)" -ForegroundColor Red
}
exit $exitCode
