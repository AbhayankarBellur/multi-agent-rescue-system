@echo off
REM ============================================================================
REM Complete Test Suite - GUI + Benchmarks
REM Runs hard scenario with GUI, then comprehensive benchmarks
REM ============================================================================

echo.
echo ============================================================================
echo  AI DISASTER RESCUE SIMULATOR - COMPLETE TEST SUITE
echo ============================================================================
echo.
echo This will run:
echo   1. GUI Simulation - HARD difficulty (300 timesteps)
echo   2. Comprehensive Benchmark Suite (all scenarios)
echo.
echo Estimated time: 10-15 minutes
echo.
pause

call .venv\Scripts\activate.bat

echo.
echo ============================================================================
echo [1/2] Running GUI Simulation - HARD Scenario
echo ============================================================================
echo.
echo Configuration:
echo   - Difficulty: HARD
echo   - Grid: 40x40 (auto-configured)
echo   - Survivors: 12
echo   - Hazard Coverage: 15%%
echo   - Max Timesteps: 300
echo   - Seed: 42
echo   - Benchmark Mode: ON
echo.
echo Controls: SPACE=Pause, R=Reset, H=Risk Overlay, P=Paths, Q=Quit
echo.

python -m src.main_advanced --difficulty hard --max-timesteps 300 --seed 42 --benchmark

if errorlevel 1 (
    echo.
    echo ERROR: Simulation failed!
    pause
    exit /b 1
)

echo.
echo ============================================================================
echo [2/2] Running Comprehensive Benchmark Suite
echo ============================================================================
echo.
echo Testing all difficulty levels and coordination protocols...
echo.

python -m src.evaluation.benchmark_suite

if errorlevel 1 (
    echo.
    echo ERROR: Benchmark suite failed!
    pause
    exit /b 1
)

echo.
echo ============================================================================
echo  COMPLETE! OUTPUT LOCATIONS:
echo ============================================================================
echo.
echo 1. NLP COMMUNICATIONS (Agent Messages):
echo    - simulation_log.txt
echo    - Contains all agent decisions, coordination, and NLP
echo.
echo 2. BENCHMARK RESULTS:
echo    - benchmark_results_[timestamp].json (raw data)
echo    - docs/BENCHMARK_RESULTS.md (formatted report)
echo.
echo 3. PERFORMANCE ANALYSIS:
echo    - docs/PERFORMANCE_ANALYSIS.md (detailed metrics)
echo    - docs/COMPREHENSIVE_EVALUATION.md (full evaluation)
echo.
echo 4. VISUALIZATIONS:
echo    - Check console output for chart file locations
echo.
echo 5. STATISTICS:
echo    - Mode switching patterns in benchmark results
echo    - Efficiency metrics and comparisons
echo.
echo ============================================================================
echo.
pause
