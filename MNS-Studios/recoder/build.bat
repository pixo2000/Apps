@echo off
echo Installing dependencies...
python -m pip install -r requirements.txt

echo Installing PyInstaller...
python -m pip install pyinstaller

echo Building executable...
python -m PyInstaller recoder.spec

echo Build complete! Executable is in the 'dist' folder.
pause
