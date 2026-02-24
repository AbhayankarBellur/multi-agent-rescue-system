# Output Guide - Where to Find Everything

This guide explains where to find all outputs from the simulation and benchmarking system.

## Quick Reference

| What You Want | File Location | Description |
|---------------|---------------|-------------|
| Agent NLP Communications | `simulation_log.txt` | All agent messages, decisions, coordination |
| Benchmark Results | `benchmark_results_[timestamp].json` | Raw performance data |
| Performance Report | `docs/BENCHMARK_RESULTS.md` | Formatted benchmark report |
| Detailed Analysis | `docs/PERFORMANCE_ANALYSIS.md` | In-depth performance metrics |
| Full Evaluation | `docs/COMPREHENSIVE_EVALUATION.md` | Complete system evaluation |
| Visualizations | Console output | Chart file paths printed during benchmark |

---

## 1. NLP Communications & Agent Behavior

### File: `simulation_log.txt`

This is your primary source for understanding agent behavior and natural language processing.

**Contains:**
- All agent-to-agent messages
- Decision-making rationale
- Coordination protocol switches
- Task assignments and negotiations
- Real-time situation assessments

**Example Content:**
```
[T=045] EXPLORER_1: "Discovered survivor at (23, 18) - health critical!"
[T=045] COORDINATOR: "Switching to AUCTION mode - high workload detected"
[T=046] RESCUE_1: "Bidding for survivor rescue - distance: 8, capacity: 3"
[T=046] RESCUE_2: "Bidding for survivor rescue - distance: 12, capacity: 2"
[T=047] COORDINATOR: "Task assigned to RESCUE_1 (lowest cost)"
```

**How to Read:**
- `[T=XXX]` = Timestep number
- Agent names indicate who is communicating
- Messages show reasoning and coordination

---

## 2. Benchmark Results

### File: `benchmark_results_[timestamp].json`

Raw performance data in JSON format for programmatic analysis.

**Structure:**
```json
{
  "timestamp": "2026-02-17T10:42:54",
  "scenarios": {
    "easy": {
      "centralized": { "survivors_rescued": 5, "timesteps": 120, ... },
      "auction": { ... },
      "coalition": { ... },
      "hybrid": { ... }
    },
    "medium": { ... },
    "hard": { ... },
    "extreme": { ... }
  },
  "statistics": {
    "mode_switches": { ... },
    "efficiency_metrics": { ... }
  }
}
```

**Use Cases:**
- Custom analysis scripts
- Data visualization
- Statistical processing
- Comparison with other runs

---

## 3. Performance Reports

### File: `docs/BENCHMARK_RESULTS.md`

Human-readable benchmark report with formatted tables and summaries.

**Sections:**
1. **Executive Summary** - Key findings
2. **Performance by Difficulty** - Results for each scenario
3. **Protocol Comparison** - Centralized vs Auction vs Coalition vs Hybrid
4. **Mode Switching Analysis** - When and why protocols changed
5. **Efficiency Metrics** - Cells explored, time efficiency, success rates

**Example Table:**
```
| Protocol     | Rescued | Success % | Timesteps | Efficiency |
|--------------|---------|-----------|-----------|------------|
| Centralized  | 8/12    | 66.7%     | 245       | 3.2        |
| Auction      | 10/12   | 83.3%     | 198       | 4.1        |
| Coalition    | 9/12    | 75.0%     | 212       | 3.8        |
| Hybrid       | 11/12   | 91.7%     | 187       | 4.5        |
```

---

## 4. Detailed Performance Analysis

### File: `docs/PERFORMANCE_ANALYSIS.md`

In-depth analysis of system performance with detailed metrics.

**Includes:**
- Rescue efficiency analysis
- Exploration patterns
- Hazard management effectiveness
- Resource utilization
- Coordination overhead
- Scalability analysis

**Key Metrics:**
- **Rescue Rate**: Survivors rescued per timestep
- **Exploration Efficiency**: Cells explored per timestep
- **Response Time**: Average time to reach survivors
- **Coordination Cost**: Overhead of protocol switching
- **Hazard Control**: Fire/flood containment rates

---

## 5. Comprehensive Evaluation

### File: `docs/COMPREHENSIVE_EVALUATION.md`

Complete system evaluation covering all aspects.

**Sections:**
1. **System Architecture** - Design overview
2. **Agent Capabilities** - Individual agent performance
3. **Coordination Protocols** - Protocol effectiveness
4. **Scenario Analysis** - Performance across difficulties
5. **Strengths & Weaknesses** - Critical assessment
6. **Future Improvements** - Recommendations

---

## 6. Visualizations

### Generated During Benchmarks

Charts and graphs are created during benchmark execution. File paths are printed to console.

**Typical Visualizations:**
- Performance comparison charts
- Mode switching timelines
- Efficiency trend graphs
- Success rate comparisons
- Resource utilization plots

**Example Console Output:**
```
📊 Generating visualizations...
   ✓ Performance comparison: ./charts/performance_comparison_20260217.png
   ✓ Mode switching timeline: ./charts/mode_switches_20260217.png
   ✓ Efficiency trends: ./charts/efficiency_trends_20260217.png
```

---

## 7. Real-Time Console Output

### During Simulation

The console shows real-time progress:

```
[T=100] Status: 5/12 rescued | Fires: 23 | Floods: 18 | Mode: AUCTION
[T=150] Status: 8/12 rescued | Fires: 31 | Floods: 22 | Mode: COALITION
[T=200] Status: 11/12 rescued | Fires: 28 | Floods: 19 | Mode: HYBRID
```

**Information Displayed:**
- Current timestep
- Survivors rescued
- Active hazards
- Current coordination mode
- Agent positions and states

---

## 8. Explanation Audit

### File: `explanation_audit.json`

Tracks all agent explanations and decision rationale.

**Purpose:**
- Verify explainability requirements
- Audit decision-making process
- Ensure transparency

**Structure:**
```json
{
  "decisions": [
    {
      "timestep": 45,
      "agent": "RESCUE_1",
      "action": "move_to_survivor",
      "explanation": "Survivor at (23,18) has critical health...",
      "reasoning": "Closest available rescue agent..."
    }
  ]
}
```

---

## Running the Complete Test Suite

### Option 1: Complete Test (Recommended)

```batch
run_complete_test.bat
```

**This runs:**
1. GUI simulation with HARD scenario (300 timesteps)
2. Comprehensive benchmark suite (all scenarios)

**Outputs:**
- `simulation_log.txt` - Latest run NLP communications
- `benchmark_results_[timestamp].json` - Raw data
- `docs/BENCHMARK_RESULTS.md` - Formatted report
- `docs/PERFORMANCE_ANALYSIS.md` - Detailed analysis
- All visualizations

### Option 2: Individual Components

**GUI Only:**
```batch
run_interactive.bat
```

**Advanced Simulation:**
```batch
run_advanced.bat
```

**Benchmarks Only:**
```batch
python -m src.evaluation.benchmark_suite
```

---

## Quick Analysis Workflow

1. **Run Complete Test:**
   ```batch
   run_complete_test.bat
   ```

2. **Check Agent Behavior:**
   - Open `simulation_log.txt`
   - Search for specific agents or timesteps
   - Review coordination messages

3. **Review Performance:**
   - Open `docs/BENCHMARK_RESULTS.md`
   - Check success rates and efficiency
   - Compare protocols

4. **Deep Dive:**
   - Open `docs/PERFORMANCE_ANALYSIS.md`
   - Review detailed metrics
   - Identify bottlenecks

5. **Visualize:**
   - Check console for chart locations
   - Open generated PNG files
   - Compare trends

---

## File Organization

```
project/
├── simulation_log.txt              # Latest NLP communications
├── benchmark_results_*.json        # Raw benchmark data
├── explanation_audit.json          # Decision audit trail
├── docs/
│   ├── BENCHMARK_RESULTS.md       # Formatted report
│   ├── PERFORMANCE_ANALYSIS.md    # Detailed analysis
│   ├── COMPREHENSIVE_EVALUATION.md # Full evaluation
│   └── OUTPUT_GUIDE.md            # This file
├── charts/                         # Generated visualizations
│   ├── performance_*.png
│   ├── mode_switches_*.png
│   └── efficiency_*.png
└── src/                           # Source code
```

---

## Tips for Analysis

### Finding Specific Information

**Agent Communications:**
```batch
findstr "RESCUE_1" simulation_log.txt
```

**Mode Switches:**
```batch
findstr "Switching to" simulation_log.txt
```

**Critical Events:**
```batch
findstr "critical" simulation_log.txt
```

### Comparing Runs

1. Save benchmark results with descriptive names
2. Use JSON diff tools to compare
3. Track improvements over time

### Performance Tuning

1. Check `PERFORMANCE_ANALYSIS.md` for bottlenecks
2. Review mode switching patterns
3. Adjust configuration in `src/utils/config.py`
4. Re-run benchmarks to verify improvements

---

## Troubleshooting

**No simulation_log.txt?**
- Check if simulation completed
- Verify LOG.LOG_FILE_PATH in config

**Missing benchmark results?**
- Ensure benchmark suite completed
- Check for error messages in console

**No visualizations?**
- Verify matplotlib is installed
- Check console for error messages
- Ensure write permissions in charts/ directory

---

## Summary

| Output Type | Primary File | Purpose |
|-------------|--------------|---------|
| NLP/Communications | `simulation_log.txt` | Agent behavior & coordination |
| Raw Data | `benchmark_results_*.json` | Programmatic analysis |
| Performance Report | `docs/BENCHMARK_RESULTS.md` | Quick overview |
| Detailed Analysis | `docs/PERFORMANCE_ANALYSIS.md` | Deep dive |
| Full Evaluation | `docs/COMPREHENSIVE_EVALUATION.md` | Complete assessment |
| Visualizations | `charts/*.png` | Graphical analysis |

**Start here:** Run `run_complete_test.bat` and check `simulation_log.txt` for NLP communications, then review `docs/BENCHMARK_RESULTS.md` for performance summary.
