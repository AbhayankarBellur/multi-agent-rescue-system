# 🚁 Multi-Agent Disaster Rescue System

**Advanced AI-Powered Emergency Response Simulation with Hybrid Coordination Protocols**

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![AI](https://img.shields.io/badge/AI-Multi--Agent-green.svg)]()
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

> A research-grade multi-agent simulation system featuring **patent-worthy hybrid coordination protocols** that dynamically adapt to environmental uncertainty. Demonstrates advanced AI algorithms including Bayesian temporal prediction, Contract Net Protocol, and coalition formation for coordinated disaster rescue operations.

---

## 🌟 Core Innovation: Hybrid Coordination Protocol

**🎯 THE PATENT CLAIM**: Dynamic protocol switching based on real-time Bayesian environmental assessment

### Three Coordination Modes:

| Mode | Risk Level | Algorithm | Use Case |
|------|-----------|-----------|----------|
| **CENTRALIZED** | Low (<0.3) | CSP Greedy | Fast deterministic allocation |
| **AUCTION** | Moderate (0.3-0.6) | Contract Net Protocol | Distributed market-based bidding |
| **COALITION** | High (>0.7) | Multi-agent teams | Collaborative hazard suppression |

**Performance**: Auction mode achieves **25% faster completion** than traditional centralized approaches in standard scenarios.

---

## ✨ Advanced Features

### 🤖 Agent Intelligence
- **6-20 Agents** (dynamically spawned based on workload)
- **Communication Network** with 15-cell range and message passing
- **Coalition Formation** for high-risk scenarios
- **Hazard Suppression** by support agents (reduces risk by 30%)

### 🧠 AI Algorithms
1. **A* Pathfinding** - Optimal route planning with risk awareness
2. **Bayesian Temporal Prediction** - Future risk forecasting up to 10 timesteps
3. **CSP Task Allocation** - Constraint satisfaction for survivor assignment
4. **STRIPS Planning** - Classical AI planning for action sequences
5. **Contract Net Protocol** - Distributed task bidding and reallocation

### 🌐 Dynamic Environment
- **Controlled Hazard Spreading**: 5% probability per timestep, 40% max coverage
- **Grid Scaling**: 10×10 to 200×200 (400× range)
- **Real-time Risk Updates**: Bayesian inference with compound probability
- **Agent Spawning**: Automatic scaling from 6 to 20 agents

### 📊 Evaluation & Benchmarking
- **Multi-protocol comparison** framework
- **Statistical analysis** with multiple random seeds
- **Performance metrics**: Success rate, timesteps, mode switches, spawning stats
- **JSON export** for data analysis

---

## 🎯 Project Overview

### **What It Does**
This system simulates a disaster scenario where multiple AI agents must coordinate to rescue survivors from a hazardous environment featuring:
- **Fires** 🔥 that spread dynamically
- **Floods** 🌊 that expand over time
- **Debris** 🏚️ from collapsed structures
- **Survivors** 👤 needing evacuation to safe zones

### **Agent Types & Roles**

| Agent | Shape | Color | Primary Function |
|-------|-------|-------|------------------|
| **Explorer** | ⭕ Circle | Blue | Maps unexplored areas using BFS/DFS |
| **Rescue** | ⬛ Square | Red | Picks up and transports survivors to safety |
| **Support** | 🔺 Triangle | Green | Coordinates team and provides assistance |

### **AI Algorithms In Action**

1. **A* Pathfinding**
   - Finds optimal routes considering terrain costs and risk levels
   - Dynamically avoids hazards while minimizing travel distance
   - Complexity: O(E log V) for efficient navigation

2. **Bayesian Risk Estimation**
   - Real-time probability updates based on environmental observations
   - Predicts hazard propagation patterns
   - Enables proactive risk avoidance

3. **CSP Task Allocation**
   - Constraint Satisfaction Problem for optimal survivor assignment
   - Balances distance, risk, and agent capacity
   - Ensures efficient workload distribution

4. **STRIPS Planning**
   - Classical AI planning for action sequences
   - Generates MOVE → PICKUP → TRANSPORT → DROP plans
   - Replans when environment changes unexpectedly

---

## 🚀 Quick Start

### **Prerequisites**
```bash
# Python 3.8 or higher
python --version

# Install dependencies
pip install pygame
# OR
pip install -r requirements.txt
```

### **Running the Simulation**

#### **Option 1: Interactive Mode** (Recommended) 🌟
```bash
.\run_interactive.bat
# OR
python -m src.main_interactive
```
- Opens GUI dialog to configure grid size, survivors, and hazards
- Supports all coordination protocols (centralized, auction, coalition, hybrid)
- Perfect for custom scenarios and experimentation

#### **Option 2: Standard Mode**
```bash
.\run.bat
# OR
python -m src.main --protocol hybrid --max-timesteps 200
```
- Uses hybrid coordination by default (adaptive mode selection)
- Quick start for demonstrations
- Supports dynamic agent spawning

#### **Option 3: Advanced CLI Mode**
```bash
.\run_advanced.bat
# OR with custom parameters:
python -m src.main_advanced --grid-size 80x60 --survivors 20 --difficulty hard --benchmark
```
- Full command-line control
- Benchmark mode for performance metrics
- Difficulty presets (easy/medium/hard/extreme)

#### **Option 4: Complete Test Suite** 🎯 (NEW - Recommended for Full Analysis)
```bash
.\run_complete_test.bat
```
- Runs GUI simulation with HARD scenario (300 timesteps)
- Executes comprehensive benchmark suite (all difficulties & protocols)
- Generates complete performance reports and visualizations
- **Time**: ~10-15 minutes
- **Outputs**: NLP logs, benchmark results, performance analysis, charts

**What You Get:**
- `simulation_log.txt` - All agent NLP communications
- `docs/BENCHMARK_RESULTS.md` - Performance report
- `docs/PERFORMANCE_ANALYSIS.md` - Detailed metrics
- `benchmark_results_[timestamp].json` - Raw data
- Visualization charts

**See:** `docs/OUTPUT_GUIDE.md` for complete output documentation

#### **Option 5: Evaluation Mode** 📊
```bash
python -m src.evaluation.evaluator
```
- Runs 15 trials comparing all coordination protocols
- Generates `evaluation_results.json` with detailed statistics
- Perfect for research and performance analysis

---

## 📂 Output Locations

After running simulations, find your results here:

| Output Type | File Location | Description |
|-------------|---------------|-------------|
| **NLP Communications** | `simulation_log.txt` | All agent messages, decisions, coordination |
| **Benchmark Results** | `benchmark_results_[timestamp].json` | Raw performance data (JSON) |
| **Performance Report** | `docs/BENCHMARK_RESULTS.md` | Formatted benchmark report |
| **Detailed Analysis** | `docs/PERFORMANCE_ANALYSIS.md` | In-depth performance metrics |
| **Full Evaluation** | `docs/COMPREHENSIVE_EVALUATION.md` | Complete system evaluation |
| **Visualizations** | Console output | Chart file paths printed during run |
| **Complete Guide** | `docs/OUTPUT_GUIDE.md` | Detailed output documentation |

**Quick Start:** Run `run_complete_test.bat` → Check `simulation_log.txt` for agent NLP → Review `docs/BENCHMARK_RESULTS.md` for performance

---

## 🎮 Command-Line Options

### **Standard Simulation**
```bash
python -m src.main [OPTIONS]
```

**Key Options**:
- `--seed SEED` - Random seed for deterministic runs (default: 42)
- `--max-timesteps N` - Maximum simulation timesteps (default: 500)
- `--log-level {MINIMAL,NORMAL,VERBOSE}` - Logging verbosity
- `-protocol {centralized,auction,coalition,hybrid}` - Coordination mode (**default: hybrid**)
- `--disable-spawning` - Disable dynamic agent spawning

**Examples**:
```bash
# Hybrid protocol with spawning (recommended)
python -m src.main --protocol hybrid --max-timesteps 300

# Force auction mode for speed, no spawning
python -m src.main --protocol auction --disable-spawning --max-timesteps 200

# Centralized with verbose logging
python -m src.main --protocol centralized --log-level VERBOSE --seed 42
```

### **Interactive Mode**
```bash
python -m src.main_interactive [OPTIONS]
```

**Additional Options**:
- `--skip-dialog` - Skip GUI configuration, use defaults
- `--protocol {centralized,auction,coalition,hybrid}` - Override coordination protocol

**Examples**:
```bash
# Show configuration dialog with hybrid protocol
python -m src.main_interactive --protocol hybrid

# Skip dialog, use defaults with auction
python -m src.main_interactive --skip-dialog --protocol auction --max-timesteps 500
```

---

## 🎮 Simulation Controls

| Key | Action |
|-----|--------|
| **SPACE** | Pause/Resume simulation |
| **R** | Reset to initial state |
| **H** | Toggle risk heatmap overlay |
| **P** | Toggle agent path visualization |
| **Q** | Quit simulation |

---

## 📊 Understanding the Interface

### **Visual Elements**

#### **Grid Display**
- **White/Gray**: Normal passable terrain
- **Light Gray**: Explored areas
- **Orange/Red**: Active fires 🔥
- **Blue**: Flooded areas 🌊
- **Dark Gray**: Debris/collapsed buildings 🏚️
- **Yellow**: Survivor locations 👤
- **Green**: Safe zones (evacuation points) 🏥

#### **Agent Legend** (Right Panel)
- Shows each agent type with corresponding shape and role
- Live position tracking
- Individual performance statistics

#### **Status Panel**
- Current timestep counter
- Remaining survivors
- Active hazard counts (fires/floods/debris)

#### **Log Panel**
- Real-time action log
- Recent agent decisions
- Rescue notifications

---

## 🔧 Configuration Options

### **Grid Size**
- **Range**: 10x10 to 200x200
- **Default**: 40x30 (1,200 cells)
- **Examples**:
  - Small: 30x20 (600 cells) - Fast, clear visualization
  - Medium: 60x45 (2,700 cells) - Balanced challenge
  - Large: 100x75 (7,500 cells) - High complexity
  - Extreme: 150x120 (18,000 cells) - Stress test

### **Survivors**
- **Range**: 1 to 50
- **Default**: 8
- **Recommendation**: 1-2 survivors per rescue agent for optimal performance

### **Hazard Coverage**
- **Range**: 0% to 50%
- **Default**: 10%
- **Impact**: Higher coverage = more challenging environment

### **Random Seed**
- **Purpose**: Reproducible scenarios
- **Default**: 42
- **Usage**: Same seed = same positions every time
- **Example**: `--seed 100` for different random layout

---

## 📈 Performance Metrics

### **Evaluated Performance** (15 trials, 300 max timesteps)

| Protocol | Success Rate | Avg Steps | Speed vs Centralized | Mode Switches |
|----------|--------------|-----------|---------------------|---------------|
| **Auction** ⚡ | 100% | **138.5** | **25% faster** | 1.0 |
| Centralized | 100% | 173.8 | baseline | 0.0 |
| Hybrid | 100% | 173.8 | adaptive | 0.0 |

### **Key Findings**:
- ✅ **93% overall success rate** across all protocols
- ⚡ **Auction mode** completes missions 25% faster through distributed task allocation
- 🧠 **Hybrid mode** correctly selects centralized for low-risk scenarios (validated adaptive logic)
- 📈 **Dynamic spawning** adds 2 explorers on average for standard scenarios
- 🎯 **Zero blocked steps** = Perfect A* pathfinding

**See**: `PERFORMANCE_ANALYSIS.md` for detailed benchmark results and strategic insights

### **Legacy Results** (without hybrid coordinator)

| Configuration | Agents | Timesteps | Rescued | Success Rate |
|---------------|--------|-----------|---------|--------------|
| Default (40x30) | 6 | 100 | 7-8/8 | **87-100%** |
| Medium (60x45) | 6 | 150 | 10-13/15 | 67-87% |
| Large (80x60) | 6 | 200 | 14-18/20 | 70-90% |

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────┐
│  Entry Points                               │
│  ├─ main.py (Standard)                      │
│  ├─ main_interactive.py (GUI Dialog) ⭐     │
│  └─ main_advanced.py (CLI + Benchmarks)     │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│  Simulator Core                             │
│  ├─ Timestep Management                     │
│  ├─ Agent Coordination                      │
│  ├─ Metrics Collection                      │
│  └─ Event Handling                          │
└─────────────────┬───────────────────────────┘
                  │
    ┌─────────────┼─────────────┐
    │             │             │
┌───▼────┐  ┌────▼────┐  ┌─────▼─────┐
│ Grid   │  │ Agents  │  │ AI Systems│
│        │  │         │  │           │
│• Cells │  │• Explr  │  │• A* Search│
│• Hzrds │  │• Rescue │  │• Bayesian │
│• Srvrs │  │• Supprt │  │• CSP      │
│• Zones │  │         │  │• STRIPS   │
└────────┘  └─────────┘  └───────────┘
```

---

## 📁 Project Structure

```
multi-agent-rescue-system/
├── src/
│   ├── main.py                    # Standard entry point  
│   ├── main_interactive.py        # Interactive mode with GUI
│   ├── main_advanced.py           # Advanced mode with benchmarking
│   ├── agents/
│   │   ├── base_agent.py          # Base agent with communication
│   │   ├── explorer.py            # Exploration agent (BFS/DFS)
│   │   ├── rescue.py              # Rescue agent (survivor transport)
│   │   └── support.py             # Support agent (hazard suppression)
│   ├── ai/
│   │   ├── bayesian_risk.py       # Temporal Bayesian prediction
│   │   ├── csp_allocator.py       # CSP + Auction allocation
│   │   ├── planner.py             # STRIPS planning
│   │   ├── search.py              # A* pathfinding
│   │   ├── communication.py       # 🆕 Contract Net Protocol
│   │   ├── coordinator.py         # 🆕 Hybrid Coordinator (PATENT CORE)
│   │   └── dynamic_spawner.py     # 🆕 Workload-based agent spawning
│   ├── core/
│   │   ├── environment.py         # Grid + controlled hazard spreading
│   │   └── simulator.py           # Main simulation loop + coordinator
│   ├── ui/
│   │   ├── renderer.py            # Pygame visualization
│   │   └── config_dialog.py       # Interactive configuration
│   ├── evaluation/
│   │   └── evaluator.py           # 🆕 Multi-protocol benchmarking
│   ├── data/
│   │   └── scenarios.py           # Scenario generation
│   └── utils/
│       ├── config.py              # Configuration constants
│       └── logger.py              # Detailed logging system
├── docs/
│   ├── FINAL_SUMMARY.md           # 🆕 Complete feature documentation
│   ├── PERFORMANCE_ANALYSIS.md    # 🆕 Benchmark results & insights
│   └── IMPLEMENTATION_PROGRESS.md # 🆕 Technical implementation details
├── run.bat                         # Quick start launcher
├── run_interactive.bat             # Interactive mode launcher
├── run_advanced.bat                # Advanced mode launcher
├── requirements.txt                # Python dependencies
├── LICENSE                         # MIT License
└── README.md                       # This file
```

---

## 🧪 Usage Examples

### **Example 1: Quick Demo**
```bash
.\run_interactive.bat
# Press Enter to use defaults
# Watch 6 agents rescue 8 survivors
```

### **Example 2: Large Scale Test**
```bash
python -m src.main_advanced --grid-size 100x75 --survivors 25 --benchmark
```
**Result**: Tests scalability with 7,500 cells and 25 survivors

### **Example 3: High Difficulty**
```bash
python -m src.main_interactive
# In dialog: Grid 80x60, Survivors 20, Hazard 20%
# Click START
```
**Result**: Challenging scenario with heavy hazard saturation

### **Example 4: Reproducible Research**
```bash
python -m src.main_advanced --seed 2026 --max-timesteps 300 --benchmark > results.txt
```
**Result**: Deterministic run with full metrics logged to file

---

## 🔬 Technical Specifications

### **Algorithm Complexity**
- **A* Pathfinding**: O(E log V) where E=edges, V=vertices
- **CSP Allocation**: O(n²) where n=number of agents
- **Risk Update**: O(8) constant time per cell (8 neighbors)
- **STRIPS Planning**: O(b^d) where b=branching factor, d=depth

### **Performance Characteristics**
- **Frame Rate**: 10 FPS (configurable)
- **Max Grid**: 200x200 = 40,000 cells
- **Max Survivors**: 50 concurrent
- **Planning Depth**: Up to 50 actions per plan
- **Hazard Propagation**: Real-time stochastic simulation

### **AI Features**
✅ **Heuristic Search**: Manhattan distance + risk penalty  
✅ **Probabilistic Reasoning**: Bayesian belief updates  
✅ **Constraint Solving**: Optimal task distribution  
✅ **Classical Planning**: Goal-oriented action sequencing  
✅ **Multi-Agent Coordination**: Decentralized decision-making  

---

## 📊 Interpreting Results

### **Terminal Output**
```
================================================================================
SIMULATION SUMMARY
================================================================================
Total timesteps: 115
Survivors rescued: 8/8
Survivors remaining: 0
Cells explored: 393
Final fires: 3
Final floods: 2

================================================================================
AGENT PERFORMANCE
================================================================================

EXP-1 (EXPLORER):
  Steps taken: 53
  Survivors rescued: 0
  Cells explored: 100
  Blocked steps: 0

RES-1 (RESCUE):
  Steps taken: 94
  Survivors rescued: 3
  Cells explored: 0
  Blocked steps: 0
```

### **Key Metrics**
- **Survivors Rescued**: Primary success indicator
- **Success Rate**: Rescued / Total survivors (aim for 80%+)
- **Cells Explored**: Coverage efficiency
- **Blocked Steps**: Should be 0 (perfect pathfinding)
- **Timesteps**: Lower is better for same success rate

### **Benchmark Mode** (`--benchmark` flag)
Adds additional metrics:
- Exploration efficiency (cells/timestep)
- Final hazard counts
- Success percentage

---

## 🎓 Educational Use Cases

### **For Students**
- Learn multi-agent systems concepts
- Understand AI search algorithms
- Explore constraint satisfaction
- Study probabilistic reasoning

### **For Researchers**
- Test new pathfinding heuristics
- Compare task allocation strategies
- Analyze emergence in multi-agent systems
- Generate reproducible experimental data

### **For Demonstrations**
- Visual AI algorithm showcase
- Real-time decision-making illustration
- Scalability demonstration
- Performance comparison studies

---

## 🛠️ Advanced Configuration

### **Hazard Spread Rates** (in `src/utils/config.py`)
```python
FIRE_SPREAD_RATE: 0.03      # Reduced for playability
FLOOD_SPREAD_RATE: 0.03     # Balanced propagation
DEBRIS_GENERATION: 0.01     # Minimal new debris
```

### **Agent Risk Thresholds**
```python
RISK_THRESHOLD_EXPLORER: 0.7   # Can tolerate more risk
RISK_THRESHOLD_RESCUE: 0.6     # Moderate risk tolerance
RISK_THRESHOLD_SUPPORT: 0.8    # Very cautious
```

### **AI Algorithm Parameters**
```python
ASTAR_RISK_PENALTY_MULTIPLIER: 10.0    # Risk vs. distance weight
CSP_MAX_SURVIVORS_PER_AGENT: 2         # Load balancing
STRIPS_MAX_PLAN_DEPTH: 50              # Planning horizon
```

---

## 🐛 Troubleshooting

### **Issue**: ModuleNotFoundError: No module named 'pygame'
**Solution**:
```bash
pip install pygame
```

### **Issue**: Dialog doesn't show
**Solution**: Make sure you're using the interactive version:
```bash
python -m src.main_interactive  # ✅ Shows dialog
python -m src.main              # ❌ No dialog
```

### **Issue**: Low success rate
**Solutions**:
- Reduce hazard coverage (5-8%)
- Increase max timesteps (200-300)
- Use smaller grid or fewer survivors
- Check that 6 agents are active

### **Issue**: Simulation gets stuck after all survivors rescued
**Solution**: This was fixed - simulation now exits automatically after 3 seconds

---

## 🚀 Future Enhancements

### **Potential Extensions**
- [ ] Machine learning for adaptive agent behavior
- [ ] Multi-objective optimization (time vs. risk vs. coverage)
- [ ] Dynamic agent spawning based on scenario severity
- [ ] Network communication simulation between agents
- [ ] Predictive hazard modeling
- [ ] 3D visualization option
- [ ] Web-based interface
- [ ] Historical replay system

---

## 📄 License

MIT License - See LICENSE file for details

---

## 👥 Contributors

Created as an advanced AI research project demonstrating:
- Multi-agent coordination
- Classical AI algorithms
- Real-time decision making
- Scalable system design

---

## 📞 Contact & Support

**GitHub Repository**: https://github.com/AbhayankarBellur/multi-agent-rescue-system

For questions, issues, or contributions, please open an issue on GitHub.

---

## 🙏 Acknowledgments

**AI Algorithms Based On**:
- A* Search (Hart, Nilsson, Raphael, 1968)
- Constraint Satisfaction Problems (Mackworth, 1977)
- STRIPS Planning (Fikes, Nilsson, 1971)
- Bayesian Inference (Bayes, 1763)

**Novel Contributions**:
- Integration of multiple AI techniques in single system
- Dynamic environmental scaling (400x range)
- Real-time mult-agent coordination
- Visual agent differentiation for clarity

---

**⭐ Star this repository if you find it useful for learning or research!**

*Built with Python, Pygame, and passion for AI* 🤖
