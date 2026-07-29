# 入境APP · 推送音频数据
# 将 PT-038 音频推送到设备

$hdc = "D:\9_infra\DevEco\sdk\default\openharmony\toolchains\hdc.exe"
$audioSrc = "D:\92_products\SPDT-004_EduContent\PT-038_TextExperience\audio"
$deviceDir = "/data/local/tmp/rujing_audio"
$sandboxDir = "/data/storage/el2/base/files/rujing_audio"

Write-Host "检查设备连接..." -ForegroundColor Cyan
$targets = & $hdc list targets
if ($targets -eq "[Empty]") { Write-Host "未检测到设备！" -ForegroundColor Red; exit 1 }
Write-Host "设备已连接" -ForegroundColor Green

Write-Host ""
Write-Host "推送音频文件..." -ForegroundColor Cyan

& $hdc shell "mkdir -p $deviceDir" 2>$null
& $hdc shell "mkdir -p $sandboxDir" 2>$null

$audios = Get-ChildItem $audioSrc -Filter "*.mp3" | Where-Object { 
    $_.Name -match "Ep0[1-4]_.*\.mp3$" -and $_.Name -notmatch "精简|精英|霸道" 
}

foreach ($a in $audios) {
    $size = [math]::Round($a.Length/1MB, 1)
    Write-Host "  推送: $($a.Name) (${size}MB)..."
    & $hdc file send $a.FullName "$deviceDir/$($a.Name)"
    & $hdc shell "cp $deviceDir/$($a.Name) $sandboxDir/$($a.Name)"
}

Write-Host ""
Write-Host "完成！音频已推送至 $deviceDir" -ForegroundColor Green
