# Quick Start Guide

## Run Complete Test Suite

```batch
run_complete_test.bat
```

This will:
1. Run GUI simulation with HARD scenario (300 timesteps)
2. Execute comprehensive benchmarks
3. Generate all reports and visualizations

**Time:** ~10-15 minutes

---

## Where to Find Outputs

### 1. Agent NLP Communications
**File:** `simulation_log.txt`
- All agent messages and decisions
- Coordination protocol switches
- Real-time reasoning

### 2. Performance Results
**File:** `docs/BENCHMARK_RESULTS.md`
- Success rates by difficulty
- Protocol comparisons
- Efficiency metrics

### 3. Detailed Analysis
**File:** `docs/PERFORMANCE_ANALYSIS.md`
- In-depth performance metrics
- Resource utilization
- Scalability analysis

### 4. Raw Data
**File:** `benchmark_results_[timestamp].json`
- Complete benchmark data
- For custom analysis

### 5. Complete Guide
**File:** `docs/OUTPUT_GUIDE.md`
- Detailed explanation of all outputs
- Analysis workflows
- Troubleshooting tips

---

## Alternative Run Options

### GUI Only (Interactive)
```batch
run_interactive.bat
```

### Advanced Simulation (Configurable)
```batch
run_advanced.bat
```

### Benchmarks Only
```batch
python -m src.evaluation.benchmark_suite
```

---

## Key Files Summary

| File | Purpose |
|------|---------|
| `simulation_log.txt` | Agent NLP communications |
| `docs/BENCHMARK_RESULTS.md` | Performance report |
| `docs/PERFORMANCE_ANALYSIS.md` | Detailed metrics |
| `docs/OUTPUT_GUIDE.md` | Complete output guide |
| `benchmark_results_*.json` | Raw data |

---

**Start Here:** Run `run_complete_test.bat` then check `simulation_log.txt` for NLP and `docs/BENCHMARK_RESULTS.md` for performance.
