# SPDT-001 deploy-all.ps1 鈥?CLI 鎵归噺閮ㄧ讲鑴氭湰
param(
  [string]$Brand = "",
  [string]$Device = "7GL0226313016118",
  [switch]$SkipBuild,
  [switch]$ListOnly
)

$root = "D:\92_products\SPDT-001_Harmony"
$apps = Get-ChildItem "$root\apps" -Directory | Sort-Object Name

# Filter by brand prefix
if ($Brand) {
  $brands = @{tk="thinkkit-"; cm="craftsman-"; hc="harmonycoder"; rh="rhythm-"; gk="gaokao-"}
  $prefix = $brands[$Brand.ToLower()]
  if (-not $prefix) { Write-Host "Unknown brand: $Brand (use: tk/cm/hc/rh/gk)"; exit 1 }
  $apps = $apps | Where-Object { $_.Name -like "$prefix*" }
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " SPDT-001 Deploy 路 $($apps.Count) apps" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan

if ($ListOnly) {
  $apps | ForEach-Object { Write-Host "  $($_.Name)" }
  exit 0
}

$pass = 0; $fail = 0
foreach ($app in $apps) {
  Write-Host "[DEPLOY] $($app.Name)" -ForegroundColor Cyan -NoNewline
  Push-Location $app.FullName
  
  $args = @("run", "--device", $Device, "--build-mode", "debug")
  if ($SkipBuild) { $args += "--skip-build" }
  
  $result = devecocli @args 2>&1
  if ($LASTEXITCODE -eq 0) { 
    Write-Host " 鉁? -ForegroundColor Green
    $pass++ 
  } else { 
    Write-Host " 鉁? -ForegroundColor Red
    ($result | Select-Object -Last 2) | ForEach-Object { Write-Host "  $_" -ForegroundColor Red }
    $fail++ 
  }
  Pop-Location
}

Write-Host "`n========================================" -ForegroundColor White
Write-Host " $pass deployed, $fail failed" -ForegroundColor $(if($fail -eq 0){'Green'}else{'Red'})
Write-Host "========================================" -ForegroundColor White
