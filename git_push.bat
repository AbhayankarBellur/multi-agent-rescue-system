@echo off
REM Git setup and push script for multi-agent-rescue-system

echo ================================================================================
echo GIT SETUP AND PUSH TO REPOSITORY
echo ================================================================================
echo.

REM Check if git is installed
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Git is not installed!
    echo Please install Git from: https://git-scm.com/
    pause
    exit /b 1
)

echo Step 1: Initializing Git repository...
git init

echo.
echo Step 2: Adding all files...
git add .

echo.
echo Step 3: Creating initial commit...
git commit -m "Initial commit: Multi-Agent Disaster Rescue System

- 6 intelligent agents (2 Explorers, 3 Rescue, 1 Support)
- Advanced AI: A* pathfinding, Bayesian risk, CSP allocation, STRIPS planning
- Dynamic grid scaling (10x10 to 200x200)
- Interactive GUI configuration
- Visual agent differentiation with shapes and colors
- 87-100%% rescue success rate at default settings
- Comprehensive documentation and examples"

echo.
echo Step 4: Adding remote repository...
git remote add origin https://github.com/AbhayankarBellur/multi-agent-rescue-system.git

echo.
echo Step 5: Pushing to GitHub...
echo NOTE: You may need to authenticate with GitHub
echo.

REM Check if main branch exists, if not use master
git branch -M main

REM Push to remote
git push -u origin main

if %errorlevel% equ 0 (
    echo.
    echo ================================================================================
    echo SUCCESS! Repository pushed to GitHub
    echo ================================================================================
    echo.
    echo Repository URL: https://github.com/AbhayankarBellur/multi-agent-rescue-system
    echo.
    echo Next steps:
    echo 1. Visit the repository on GitHub
    echo 2. Add a repository description
    echo 3. Add topics: ai, multi-agent-system, disaster-rescue, pygame, python
    echo 4. Enable GitHub Pages if desired
    echo.
) else (
    echo.
    echo ================================================================================
    echo PUSH FAILED
    echo ================================================================================
    echo.
    echo Possible reasons:
    echo 1. Authentication required - Please set up GitHub credentials
    echo 2. Repository doesn't exist - Create it on GitHub first
    echo 3. Network connectivity issues
    echo.
    echo To push manually:
    echo   git push -u origin main
    echo.
)

pause
