# 🚀 Quick Start: Grafana Monitoring Stack

Write-Host "`n" -NoNewline
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 78) -NoNewline -ForegroundColor Cyan
Write-Host "" -ForegroundColor Cyan
Write-Host "🚀 E-COMMERCE API - GRAFANA MONITORING SETUP" -ForegroundColor Magenta
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 78) -NoNewline -ForegroundColor Cyan
Write-Host "`n" -ForegroundColor Cyan

Write-Host "This script will start the complete monitoring stack:" -ForegroundColor White
Write-Host "  ✓ Grafana (Dashboards)" -ForegroundColor Green
Write-Host "  ✓ Prometheus (Metrics)" -ForegroundColor Green
Write-Host "  ✓ Loki (Logs)" -ForegroundColor Green
Write-Host "  ✓ Promtail (Log Shipping)" -ForegroundColor Green
Write-Host ""

# Check if Docker is running
Write-Host "Checking Docker..." -ForegroundColor Yellow
try {
    docker ps | Out-Null
    Write-Host "✅ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not running or not installed" -ForegroundColor Red
    Write-Host "   Please start Docker Desktop and try again" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Starting monitoring stack..." -ForegroundColor Yellow
docker-compose up -d

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Monitoring stack started successfully!" -ForegroundColor Green
    Write-Host ""
    
    Write-Host "Waiting for services to be ready..." -ForegroundColor Yellow
    Start-Sleep -Seconds 10
    
    Write-Host ""
    Write-Host "=" -NoNewline -ForegroundColor Cyan
    Write-Host ("=" * 78) -NoNewline -ForegroundColor Cyan
    Write-Host "" -ForegroundColor Cyan
    Write-Host "📊 MONITORING SERVICES" -ForegroundColor Blue
    Write-Host "=" -NoNewline -ForegroundColor Cyan
    Write-Host ("=" * 78) -NoNewline -ForegroundColor Cyan
    Write-Host "`n" -ForegroundColor Cyan
    
    Write-Host "Grafana:     " -NoNewline -ForegroundColor Green
    Write-Host "http://localhost:3000" -ForegroundColor White
    Write-Host "             Username: admin | Password: admin123" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Prometheus:  " -NoNewline -ForegroundColor Green
    Write-Host "http://localhost:9090" -ForegroundColor White
    Write-Host ""
    Write-Host "Loki:        " -NoNewline -ForegroundColor Green
    Write-Host "http://localhost:3100" -ForegroundColor White
    Write-Host ""
    
    Write-Host "=" -NoNewline -ForegroundColor Cyan
    Write-Host ("=" * 78) -NoNewline -ForegroundColor Cyan
    Write-Host "`n" -ForegroundColor Cyan
    
    Write-Host "🎯 NEXT STEPS:" -ForegroundColor Blue
    Write-Host ""
    Write-Host "1. Start the API server:" -ForegroundColor White
    Write-Host "   python server.py" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "2. Open Grafana:" -ForegroundColor White
    Write-Host "   http://localhost:3000" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "3. View the dashboard:" -ForegroundColor White
    Write-Host "   Dashboards → E-commerce API Monitoring" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "4. Generate test traffic:" -ForegroundColor White
    Write-Host "   python chaos_test_server.py" -ForegroundColor Yellow
    Write-Host ""
    
    Write-Host "=" -NoNewline -ForegroundColor Cyan
    Write-Host ("=" * 78) -NoNewline -ForegroundColor Cyan
    Write-Host "`n" -ForegroundColor Cyan
    
    Write-Host "📚 For detailed documentation, see GRAFANA_SETUP.md" -ForegroundColor Cyan
    Write-Host ""
    
    # Check if services are actually running
    Write-Host "Verifying containers..." -ForegroundColor Yellow
    docker-compose ps
    
} else {
    Write-Host ""
    Write-Host "❌ Failed to start monitoring stack" -ForegroundColor Red
    Write-Host "   Check docker-compose logs for errors:" -ForegroundColor Yellow
    Write-Host "   docker-compose logs" -ForegroundColor Yellow
}

Write-Host ""
