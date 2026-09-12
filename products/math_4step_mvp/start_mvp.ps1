# 4 步法训练 MVP 启动脚本
# 启动 Flask 服务器在 http://127.0.0.1:5050
# 用法: powershell -ExecutionPolicy Bypass -File start_mvp.ps1

$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot

Write-Host "[INFO] 启动 4 步法训练 MVP (Flask + 极简 HTML) ..." -ForegroundColor Cyan
Write-Host "[INFO] 端口: 5050" -ForegroundColor Cyan
Write-Host "[INFO] 数据: D:\4_data\knowledge_cards\数学\4step" -ForegroundColor Cyan
Write-Host "[INFO] 停止: Ctrl+C" -ForegroundColor Yellow
Write-Host ""

# 检查 Python 和 Flask
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host "[ERROR] Python 未安装" -ForegroundColor Red
    exit 1
}

# 检查 Flask
try {
    python -c "import flask" 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[WARN] Flask 未安装, 尝试 pip install..." -ForegroundColor Yellow
        pip install flask
    }
} catch {}

# 后台启动 Flask
$process = Start-Process -FilePath python -ArgumentList "app.py" -PassThru -NoNewWindow
Start-Sleep -Seconds 2

Write-Host "[OK] Flask 启动 (PID $($process.Id))" -ForegroundColor Green
Write-Host "[URL] http://127.0.0.1:5050" -ForegroundColor Green
Write-Host ""
Write-Host "按 Ctrl+C 停止..." -ForegroundColor Yellow

# 等用户停止
try {
    while ($process -and -not $process.HasExited) {
        Start-Sleep -Seconds 2
    }
} finally {
    if ($process -and -not $process.HasExited) {
        Stop-Process -Id $process.Id -Force
        Write-Host "[INFO] Flask 已停止" -ForegroundColor Yellow
    }
}
