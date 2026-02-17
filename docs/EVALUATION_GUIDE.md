# 📖 EVALUATION GUIDE

**System**: Multi-Agent Disaster Rescue System  
**Module**: Evaluation & Benchmarking  
**Version**: 2.0

---

## 🎯 OVERVIEW

This guide explains how to use the evaluation and benchmarking system to assess the performance of the Multi-Agent Disaster Rescue System.

---

## 🚀 QUICK START

### Run Complete Benchmark Suite

```bash
# Run all difficulties with 10 runs each (40 total scenarios)
python -m src.evaluation.benchmark_suite --difficulty all --runs 10

# Output: benchmark_results_YYYYMMDD_HHMMSS.json
```

### Run Specific Difficulty

```bash
# Test only hard scenarios
python -m src.evaluation.benchmark_suite --difficulty hard --runs 5

# Test easy scenarios
python -m src.evaluation.benchmark_suite --difficulty easy --runs 10
```

### Custom Output File

```bash
# Specify output filename
python -m src.evaluation.benchmark_suite --difficulty all --runs 10 --output my_results.json
```

---

## 📊 BENCHMARK SUITE

### BenchmarkSuite Class

Located in `src/evaluation/benchmark_suite.py`

**Key Methods**:
- `run_single_benchmark(difficulty, seed)` - Run one scenario
- `run_benchmark_set(difficulty, runs)` - Run multiple scenarios
- `run_all_benchmarks(runs_per_difficulty)` - Complete suite
- `generate_summary()` - Statistical summary
- `export_results(filename)` - Save to JSON
- `print_summary()` - Console output

**Example Usage**:
```python
from src.evaluation.benchmark_suite import BenchmarkSuite

suite = BenchmarkSuite()

# Run 5 hard scenarios
results = suite.run_benchmark_set('hard', runs=5)

# Print summary
suite.print_summary()

# Export results
suite.export_results('my_benchmark.json')
```

---

## 📈 STATISTICAL ANALYSIS

### StatisticalAnalyzer Class

Located in `src/evaluation/statistics.py`

**Key Methods**:
- `calculate_mean(values)` - Arithmetic mean
- `calculate_std_dev(values)` - Standard deviation
- `calculate_confidence_interval(values, confidence)` - CI calculation
- `analyze_dataset(values)` - Comprehensive stats
- `compare_datasets(dataset1, dataset2)` - Comparison
- `analyze_benchmark_results(results)` - Full analysis

**Example Usage**:
```python
from src.evaluation.statistics import StatisticalAnalyzer

# Analyze rescue rates
rescue_rates = [0.8, 0.75, 0.85, 0.9, 0.7]
stats = StatisticalAnalyzer.analyze_dataset(rescue_rates)

print(f"Mean: {stats['mean']}")
print(f"Std Dev: {stats['std_dev']}")
print(f"95% CI: {stats['ci_95']}")
```

---

## 📊 VISUALIZATION

### BenchmarkVisualizer Class

Located in `src/evaluation/visualizer.py`

**Key Methods**:
- `create_bar_chart(data, title)` - ASCII bar chart
- `create_comparison_chart(datasets, title)` - Comparison chart
- `visualize_benchmark_summary(summary)` - Complete visualization
- `export_for_plotting(summary, filename)` - CSV export
- `create_performance_table(results)` - Detailed table

**Example Usage**:
```python
from src.evaluation.visualizer import BenchmarkVisualizer

# Create bar chart
data = {'easy': 90, 'medium': 80, 'hard': 70}
chart = BenchmarkVisualizer.create_bar_chart(
    data, 
    "Rescue Rates by Difficulty",
    value_label="%"
)
print(chart)

# Visualize summary
viz = BenchmarkVisualizer.visualize_benchmark_summary(summary)
print(viz)
```

---

## 🔬 ADVANCED ANALYSIS

### Analysis Modules

Located in `src/evaluation/analysis.py`

#### 1. ScalabilityAnalyzer
Analyzes performance across grid sizes.

```python
from src.evaluation.analysis import ScalabilityAnalyzer

analysis = ScalabilityAnalyzer.analyze_scalability(results)
ScalabilityAnalyzer.print_scalability_report(analysis)
```

#### 2. SuccessAnalyzer
Analyzes rescue success patterns and failure reasons.

```python
from src.evaluation.analysis import SuccessAnalyzer

analysis = SuccessAnalyzer.analyze_success_patterns(results)
SuccessAnalyzer.print_success_report(analysis)
```

#### 3. ModeAnalyzer
Analyzes coordination mode switching patterns.

```python
from src.evaluation.analysis import ModeAnalyzer

analysis = ModeAnalyzer.analyze_mode_switches(results)
ModeAnalyzer.print_mode_report(analysis)
```

#### 4. AgentAnalyzer
Analyzes agent spawning and performance.

```python
from src.evaluation.analysis import AgentAnalyzer

analysis = AgentAnalyzer.analyze_agent_performance(results)
AgentAnalyzer.print_agent_report(analysis)
```

#### 5. Comprehensive Analysis
Run all analysis modules at once.

```python
from src.evaluation.analysis import run_comprehensive_analysis

comprehensive = run_comprehensive_analysis(results)
```

---

## 📋 METRICS EXPLAINED

### Rescue Rate
- **Definition**: Percentage of survivors rescued
- **Formula**: `rescued / total_survivors`
- **Range**: 0.0 to 1.0 (0% to 100%)
- **Target**: >70% for hard scenarios

### Timesteps
- **Definition**: Number of simulation steps to completion
- **Range**: 1 to max_timesteps
- **Lower is better** (faster completion)

### Agents Spawned
- **Definition**: Number of agents dynamically added
- **Range**: 0 to max_agents - initial_agents
- **Optimal**: 1-3 for most scenarios

### Mode Switches
- **Definition**: Number of coordination protocol changes
- **Range**: 0 to unlimited
- **Typical**: 2-4 for hard scenarios
- **Indicates**: System adaptability

### Duration
- **Definition**: Real-time execution time (seconds)
- **Affected by**: Grid size, agent count, complexity
- **Use for**: Performance optimization

### Efficiency
- **Definition**: Rescue rate per agent
- **Formula**: `rescue_rate / final_agent_count`
- **Higher is better** (more efficient agents)

---

## 🎓 INTERPRETING RESULTS

### Good Performance Indicators
- ✅ Rescue rate >70% for hard scenarios
- ✅ Mode switches 2-4 per scenario
- ✅ Agents spawned 1-3 per scenario
- ✅ Completion within max timesteps
- ✅ Low standard deviation (<0.1)

### Warning Signs
- ⚠️ Rescue rate <50%
- ⚠️ No mode switches (not adapting)
- ⚠️ No agents spawned (not scaling)
- ⚠️ High variance (>0.15)
- ⚠️ Frequent timeouts

### Optimization Opportunities
- 🔧 Low rescue rate → Tune spawning thresholds
- 🔧 No mode switches → Adjust risk thresholds
- 🔧 High timestep duration → Optimize pathfinding
- 🔧 Many timeouts → Increase max timesteps

---

## 📁 OUTPUT FILES

### benchmark_results_[timestamp].json
Complete benchmark results with:
- Individual run data
- Summary statistics
- Timestamp and configuration

**Structure**:
```json
{
  "timestamp": "2026-02-17T10:42:54",
  "results": [
    {
      "difficulty": "hard",
      "seed": 42,
      "rescue_rate": 0.733,
      "timesteps": 185,
      ...
    }
  ],
  "summary": {
    "by_difficulty": {...},
    "overall": {...}
  }
}
```

### plot_data.csv
CSV format for external plotting tools (Excel, Python, R).

**Columns**:
- difficulty
- rescue_rate_mean
- rescue_rate_std
- timesteps_mean
- timesteps_std
- agents_spawned_mean
- agents_spawned_std
- mode_switches_mean
- mode_switches_std

---

## 🔧 CUSTOMIZATION

### Add Custom Scenarios

Edit `src/evaluation/benchmark_suite.py`:

```python
self.scenarios['custom'] = {
    'description': 'Custom scenario',
    'max_timesteps': 300,
    'expected_rescue_rate': 0.60
}
```

### Add Custom Metrics

Modify `run_single_benchmark()` to track additional metrics:

```python
results['custom_metric'] = calculate_custom_metric(sim)
```

### Custom Analysis

Create new analyzer class in `src/evaluation/analysis.py`:

```python
class CustomAnalyzer:
    @staticmethod
    def analyze_custom(results):
        # Your analysis logic
        pass
```

---

## 🎯 BEST PRACTICES

1. **Run Multiple Seeds**: Use 10+ runs for statistical significance
2. **Test All Difficulties**: Ensure robustness across scenarios
3. **Monitor Variance**: Low variance indicates consistency
4. **Compare Baselines**: Track improvements over time
5. **Document Changes**: Note configuration changes in results
6. **Export Data**: Save results for future comparison
7. **Visualize Trends**: Use charts to identify patterns

---

## 🐛 TROUBLESHOOTING

### Issue: Benchmark runs too slowly
**Solution**: Reduce runs per difficulty or use headless mode

### Issue: High variance in results
**Solution**: Increase number of runs, check for randomness issues

### Issue: No mode switches observed
**Solution**: Check risk thresholds, use harder scenarios

### Issue: Memory errors on large grids
**Solution**: Reduce grid size or optimize memory usage

---

## 📚 REFERENCES

- **Benchmark Results**: `docs/BENCHMARK_RESULTS.md`
- **Implementation Progress**: `docs/IMPLEMENTATION_PROGRESS.md`
- **Performance Analysis**: `docs/PERFORMANCE_ANALYSIS.md`

---

## 🤝 CONTRIBUTING

To add new evaluation features:

1. Create new analyzer in `src/evaluation/analysis.py`
2. Add tests in benchmark suite
3. Update this guide with usage instructions
4. Document metrics in BENCHMARK_RESULTS.md

---

**Last Updated**: February 2026  
**Version**: 2.0  
**Maintainer**: System Development Team
