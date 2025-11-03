# Build script for Recoder
Write-Host "Installing dependencies..." -ForegroundColor Green
python -m pip install -r requirements.txt

Write-Host "Building executable..." -ForegroundColor Green
python -m PyInstaller recoder.spec

if ($LASTEXITCODE -eq 0) {
    Write-Host "Build complete! Executable is in the 'dist' folder." -ForegroundColor Green
} else {
    Write-Host "Build failed!" -ForegroundColor Red
}

Read-Host "Press Enter to continue..."
