@echo off
REM Combat Simulator - Windows Launch Script

echo Combat Simulator - Launch Script
echo.

REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.8 or higher from https://www.python.org/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

REM Check Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] Python %PYTHON_VERSION% detected
echo.

REM Check if dependencies are installed
python -c "import rich" >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [INFO] Installing dependencies...
    python -m pip install -r requirements.txt
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Failed to install dependencies.
        pause
        exit /b 1
    )
    echo.
)

REM Launch the game
echo [OK] Launching Combat Simulator...
echo.
python cli.py

REM Pause at the end if there was an error
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Combat Simulator exited with an error.
    pause
)
