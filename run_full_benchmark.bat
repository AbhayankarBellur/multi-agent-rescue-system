@echo off
REM ============================================================================
REM AI Disaster Rescue Simulator - Full Benchmark Suite
REM ============================================================================
REM This script runs a complete simulation and benchmark cycle:
REM 1. Runs GUI simulation with HARD scenario (300 timesteps)
REM 2. Executes comprehensive benchmark suite
REM 3. Generates performance analysis and visualizations
REM ============================================================================

echo.
echo ============================================================================
echo  AI DISASTER RESCUE SIMULATOR - FULL BENCHMARK SUITE
echo ============================================================================
echo.
echo This will:
echo   1. Run GUI simulation with HARD scenario (300 timesteps)
echo   2. Execute comprehensive benchmarks
echo   3. Generate performance analysis
echo.
echo Estimated time: 10-15 minutes
echo.
pause

REM Activate virtual environment
echo.
echo [1/3] Activating virtual environment...
call .venv\Scripts\activate.bat

REM Run GUI simulation with hard scenario
echo.
echo ============================================================================
echo [2/3] Running GUI Simulation - HARD Scenario (300 timesteps)
echo ============================================================================
echo.
echo Configuration:
echo   - Grid: 40x40 (1600 cells)
echo   - Survivors: 15
echo   - Hazard Density: 35%%
echo   - Max Timesteps: 300
echo   - Coordination: Hybrid (auto-switching)
echo   - Dynamic Spawning: Enabled
echo.
echo Controls:
echo   SPACE - Pause/Resume
echo   R - Reset
echo   H - Toggle risk overlay
echo   P - Toggle paths
echo   Q - Quit
echo.

python -c "from src.core.simulator import Simulator; from src.data.scenarios import ScenarioGenerator; from src.utils.config import GRID, SIMULATION; gen = ScenarioGenerator(seed=42); scenario = gen.generate_high_risk_scenario((40, 40)); GRID.WIDTH = 40; GRID.HEIGHT = 40; SIMULATION.MAX_TIMESTEPS = 300; sim = Simulator(seed=42, coordination_mode='hybrid', enable_spawning=True); sim.initialize(); sim.grid.clear(); gen.apply_scenario_to_grid(sim.grid, scenario); sim.run()"

if errorlevel 1 (
    echo.
    echo ERROR: Simulation failed!
    pause
    exit /b 1
)

echo.
echo Simulation complete! Check simulation_log.txt for NLP communications.
echo.

REM Run benchmark suite
echo.
echo ============================================================================
echo [3/3] Running Comprehensive Benchmark Suite
echo ============================================================================
echo.
echo This will test:
echo   - Multiple difficulty levels (easy, medium, hard, extreme)
echo   - All coordination protocols (centralized, auction, coalition, hybrid)
echo   - Performance metrics and statistics
echo   - Visualization generation
echo.

python -m src.evaluation.benchmark_suite

if errorlevel 1 (
    echo.
    echo ERROR: Benchmark suite failed!
    pause
    exit /b 1
)

REM Summary
echo.
echo ============================================================================
echo  BENCHMARK COMPLETE!
echo ============================================================================
echo.
echo Output Locations:
echo.
echo 1. NLP COMMUNICATIONS:
echo    - simulation_log.txt (latest run)
echo    - Contains all agent messages, decisions, and coordination
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
echo    - Check console output for chart locations
echo    - Performance graphs and comparisons
echo.
echo 5. STATISTICS:
echo    - Statistical analysis in benchmark results
echo    - Mode switching patterns
echo    - Efficiency metrics
echo.
echo ============================================================================
echo.
echo Key Files to Review:
echo   1. simulation_log.txt - See agent NLP communications
echo   2. docs/BENCHMARK_RESULTS.md - Performance summary
echo   3. docs/PERFORMANCE_ANALYSIS.md - Detailed analysis
echo   4. benchmark_results_*.json - Raw data for further analysis
echo.
echo ============================================================================
echo.
pause
