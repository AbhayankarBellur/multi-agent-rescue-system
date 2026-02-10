@echo off
REM Quick launcher for AI Disaster Rescue Simulator
REM Double-click this file to run the simulation

echo ================================================================================
echo AI DISASTER RESCUE SIMULATOR
echo Research-Grade Multi-Agent System
echo ================================================================================
echo.
echo Starting simulation...
echo.

REM Use virtual environment Python if available, otherwise system Python
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" -m src.main --seed 42 --max-timesteps 200 --log-level NORMAL
) else (
    python -m src.main --seed 42 --max-timesteps 200 --log-level NORMAL
)

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Simulation failed!
    echo Make sure pygame is installed: pip install pygame
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo Simulation completed successfully!
echo Check simulation_log.txt for detailed execution trace
echo ================================================================================
pause

python -c "import pygame" 2>nul
if %errorlevel% neq 0 (
    echo pygame not found. Installing...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

echo.
echo ================================================================================
echo Starting simulation...
echo.
echo Controls:
echo   SPACE - Pause/Resume
echo   R - Reset
echo   H - Toggle risk overlay
echo   P - Toggle agent paths
echo   Q - Quit
echo ================================================================================
echo.

python -m src.main

if %errorlevel% neq 0 (
    echo.
    echo ================================================================================
    echo ERROR: Simulation failed to run
    echo Check the error messages above
    echo ================================================================================
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo Simulation ended successfully
echo Check simulation_log.txt for detailed execution trace
echo ================================================================================
pause
