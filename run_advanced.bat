@echo off
REM AI Disaster Rescue Simulator - Advanced Launcher
REM Patent-Worthy Multi-Agent System with Dynamic Configuration

echo ================================================================================
echo    AI DISASTER RESCUE SIMULATOR - Advanced Multi-Agent System
echo ================================================================================
echo.

REM Check for virtual environment
if exist ".venv\Scripts\python.exe" (
    set PYTHON=".venv\Scripts\python.exe"
    echo [OK] Using virtual environment Python
) else (
    set PYTHON=python
    echo [OK] Using system Python
)

REM Check pygame installation
%PYTHON% -c "import pygame" 2>nul
if %errorlevel% neq 0 (
    echo.
    echo [INSTALL] Installing pygame dependency...
    pip install pygame
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install pygame
        pause
        exit /b 1
    )
)

echo.
echo ================================================================================
echo CONFIGURATION OPTIONS (customize by editing this file):
echo.
echo   Grid Size: Modify --grid-size WIDTHxHEIGHT (e.g., 60x45, 100x80)
echo   Survivors: Modify --survivors N (e.g., 12, 20, 30)
echo   Hazards: Modify --hazard-coverage PERCENT (e.g., 15, 25)
echo   Difficulty: Use --difficulty easy/medium/hard/extreme
echo   Benchmark: Add --benchmark for performance metrics
echo.
echo Current: Default settings (40x30 grid, 8 survivors, 10%% hazards)
echo ================================================================================
echo.

REM Run with default or custom settings (modify the line below)
%PYTHON% -m src.main_advanced --seed 42 --max-timesteps 200 --log-level NORMAL

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Simulation failed! Check error messages above.
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo [SUCCESS] Simulation completed! Check simulation_log.txt for detailed trace
echo ================================================================================
pause
