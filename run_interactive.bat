@echo off
REM Interactive launcher with GUI configuration dialog
REM Shows dialog to configure grid size, survivors, and hazards before starting

echo ================================================================================
echo AI DISASTER RESCUE SIMULATOR - INTERACTIVE MODE
echo Configure your simulation through a graphical interface!
echo ================================================================================
echo.

REM Check for virtual environment
if exist ".venv\Scripts\python.exe" (
    set PYTHON=.venv\Scripts\python.exe
) else (
    set PYTHON=python
)

REM Check pygame installation
%PYTHON% -c "import pygame" 2>nul
if %errorlevel% neq 0 (
    echo pygame not found. Installing...
    %PYTHON% -m pip install pygame
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install pygame
        pause
        exit /b 1
    )
)

echo Starting interactive configuration...
echo.

REM Run with interactive dialog
%PYTHON% -m src.main_interactive

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Simulation failed!
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo Simulation completed!
echo Check simulation_log.txt for detailed trace
echo ================================================================================
pause
