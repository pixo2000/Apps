@echo off
REM Batch file to launch Lanis Stundenplan Rechner on Windows
REM This makes it easier for users to start the application

echo Lanis Stundenplan Rechner
echo ========================

REM Check if we're in the right directory
if not exist "main.py" (
    echo Error: main.py not found. Please run this from the StundenplanRechner directory.
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist ".venv\Scripts\python.exe" (
    if exist "C:\Users\pixo2000\Documents\Coding\Github\Apps\.venv\Scripts\python.exe" (
        echo Using shared virtual environment...
        set PYTHON_CMD=C:\Users\pixo2000\Documents\Coding\Github\Apps\.venv\Scripts\python.exe
    ) else (
        echo Error: Python virtual environment not found.
        echo Please set up the environment first.
        pause
        exit /b 1
    )
) else (
    set PYTHON_CMD=.venv\Scripts\python.exe
)

REM Start the application
echo Starting Lanis Stundenplan Rechner...
%PYTHON_CMD% launcher.py

pause
