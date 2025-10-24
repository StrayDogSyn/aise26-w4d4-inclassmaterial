# PowerShell script to run the server
Write-Host "Starting E-commerce API Server..." -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Activate virtual environment and run server
& "C:/Users/EHunt/Repos/AISE/AISE-Curriculum-Weekly/.venv/Scripts/python.exe" starter_code.py
