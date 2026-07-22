# MOCOWEST Landing Page - Run Script
Write-Host "Starting MOCOWEST Landing Page..." -ForegroundColor Cyan

# Check if Python is installed
try {
    python --version 2>$null | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "Python not found" }
} catch {
    Write-Host "Python is not installed. Please install Python 3.8 or higher." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Create virtual environment if it doesn't exist
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .env\Scripts\Activate.ps1

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install --no-cache-dir -r requirements.txt

# Run the application
Write-Host "Starting Flask application..." -ForegroundColor Cyan
Write-Host "Open http://localhost:5000 in your browser" -ForegroundColor Green
python app.py