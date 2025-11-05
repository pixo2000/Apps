# Build script for NewsBoarder
# Compiles the Python application to an executable with icon

Write-Host "NewsBoarder Build Script" -ForegroundColor Cyan
Write-Host "========================" -ForegroundColor Cyan
Write-Host ""

# Check if required packages are installed
Write-Host "Step 1: Checking dependencies..." -ForegroundColor Yellow

$requiredPackages = @("pyinstaller", "pillow")
$missingPackages = @()

foreach ($package in $requiredPackages) {
    $installed = pip show $package 2>$null
    if (-not $installed) {
        $missingPackages += $package
    }
}

if ($missingPackages.Count -gt 0) {
    Write-Host "Missing packages: $($missingPackages -join ', ')" -ForegroundColor Red
    Write-Host "Installing missing packages..." -ForegroundColor Yellow
    foreach ($package in $missingPackages) {
        pip install $package
    }
}

Write-Host "All dependencies are installed!" -ForegroundColor Green
Write-Host ""

# Step 2: Create icon from SVG
Write-Host "Step 2: Creating icon file..." -ForegroundColor Yellow
python create_icon.py

if (-not (Test-Path "icon.ico")) {
    Write-Host "ERROR: Icon creation failed!" -ForegroundColor Red
    exit 1
}

Write-Host "Icon created successfully!" -ForegroundColor Green
Write-Host ""

# Step 3: Build executable
Write-Host "Step 3: Building executable..." -ForegroundColor Yellow
pyinstaller NewsBoarder.spec --clean

if (Test-Path "dist\NewsBoarder.exe") {
    Write-Host ""
    Write-Host "========================" -ForegroundColor Green
    Write-Host "BUILD SUCCESSFUL!" -ForegroundColor Green
    Write-Host "========================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Executable location: dist\NewsBoarder.exe" -ForegroundColor Cyan
    Write-Host ""
    
    # Open dist folder
    explorer.exe dist
} else {
    Write-Host ""
    Write-Host "========================" -ForegroundColor Red
    Write-Host "BUILD FAILED!" -ForegroundColor Red
    Write-Host "========================" -ForegroundColor Red
    Write-Host "Check the output above for errors." -ForegroundColor Red
}
