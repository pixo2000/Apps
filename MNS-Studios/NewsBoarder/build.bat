@echo off
echo ========================================
echo NewsBoarder Build Script
echo ========================================
echo.

echo Step 1: Installing dependencies...
pip install -r requirements.txt
echo.

echo Step 2: Creating icon...
python create_icon.py
echo.

echo Step 3: Building executable...
pyinstaller NewsBoarder.spec --clean
echo.

if exist "dist\NewsBoarder.exe" (
    echo ========================================
    echo BUILD SUCCESSFUL!
    echo ========================================
    echo.
    echo Executable location: dist\NewsBoarder.exe
    echo.
    explorer.exe dist
) else (
    echo ========================================
    echo BUILD FAILED!
    echo ========================================
    echo Check the output above for errors.
)

pause
