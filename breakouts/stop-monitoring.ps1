# 🛑 Stop Monitoring Stack

Write-Host "`n"
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 78) -NoNewline -ForegroundColor Cyan
Write-Host "" -ForegroundColor Cyan
Write-Host "🛑 STOPPING MONITORING STACK" -ForegroundColor Red
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 78) -NoNewline -ForegroundColor Cyan
Write-Host "`n" -ForegroundColor Cyan

$choice = Read-Host "Do you want to remove volumes (delete all data)? (y/N)"

if ($choice -eq "y" -or $choice -eq "Y") {
    Write-Host ""
    Write-Host "Stopping containers and removing volumes..." -ForegroundColor Yellow
    docker-compose down -v
    Write-Host ""
    Write-Host "✅ Monitoring stack stopped and data removed" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "Stopping containers (data preserved)..." -ForegroundColor Yellow
    docker-compose down
    Write-Host ""
    Write-Host "✅ Monitoring stack stopped (data preserved)" -ForegroundColor Green
}

Write-Host ""
Write-Host "To start again, run: .\start-monitoring.ps1" -ForegroundColor Cyan
Write-Host ""
