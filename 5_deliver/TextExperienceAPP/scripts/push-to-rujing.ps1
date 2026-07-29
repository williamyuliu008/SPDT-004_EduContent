# 入境APP · 一键导入数据 v2
# 策略：hdc推到 /data/local/tmp/ → cp到沙箱 → APP读取

$hdc = "D:\9_infra\DevEco\sdk\default\openharmony\toolchains\hdc.exe"

Write-Host "检查设备连接..." -ForegroundColor Cyan
$targets = & $hdc list targets
if ($targets -eq "[Empty]" -or $targets -notmatch "VYG|127|emulator") {
    Write-Host "未检测到设备！" -ForegroundColor Red
    exit 1
}
Write-Host "设备已连接" -ForegroundColor Green

$cardJson = "D:\92_products\SPDT-004_EduContent\PT-038_TextExperience\cards\历史_v3_全16集卡片包.json"
$size = [math]::Round((Get-Item $cardJson).Length/1024, 1)

Write-Host "推送卡片包 (${size}KB)..." -ForegroundColor Cyan

# Step 1: push to system tmp (always works)
& $hdc file send $cardJson /data/local/tmp/rujing_cards.json
Write-Host "  → 已推送至 /data/local/tmp/" -ForegroundColor Green

# Step 2: copy to app sandbox
& $hdc shell "mkdir -p /data/storage/el2/base/files/"
& $hdc shell "cp /data/local/tmp/rujing_cards.json /data/storage/el2/base/files/rujing_cards.json"

# Step 3: verify
$verify = & $hdc shell "ls -la /data/storage/el2/base/files/rujing_cards.json"
if ($LASTEXITCODE -eq 0 -and $verify) {
    Write-Host "  → 已迁入沙箱: $verify" -ForegroundColor Green
} else {
    Write-Host "  → 沙箱迁入可能失败，尝试备用路径..." -ForegroundColor Yellow
    & $hdc shell "mkdir -p /data/app/el2/100/base/com.harmonystudio.rujing/files/"
    & $hdc shell "cp /data/local/tmp/rujing_cards.json /data/app/el2/100/base/com.harmonystudio.rujing/files/rujing_cards.json"
}

Write-Host ""
Write-Host "完成！入境APP → '导入' → 点击 '一键导入'" -ForegroundColor Yellow
