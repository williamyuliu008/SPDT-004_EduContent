# ============================================================
# 自动化平台包装脚本
# 用法（PowerShell）:
#   .\run.ps1                        # 交互模式
#   .\run.ps1 TC_001_video_play      # 运行指定用例
# ============================================================
$env:PATH = "C:\Users\willi\AppData\Local\OpenHarmony\Sdk\26.0.0\toolchains;" + $env:PATH
Set-Location "D:\92_products\SPDT-001_Harmony\automation"

if ($Args[0]) {
    $tc = $Args[0]
    Write-Host "[Hypium] 运行用例: $tc"
    python -m hypium run -l $tc -ta screenshot:true
} else {
    Write-Host "[Hypium] 进入交互模式（输入 help run 查看命令）"
    python -m hypium
}
