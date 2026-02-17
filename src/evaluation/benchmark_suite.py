"""
Benchmark Suite for Multi-Agent Rescue System
Automated testing across multiple scenarios and difficulties.
"""

import time
import json
from typing import Dict, List, Tuple
from datetime import datetime
from ..core.simulator import Simulator
from ..utils.logger import get_logger


class BenchmarkSuite:
    """
    Automated benchmark suite for system evaluation.
    
    Runs multiple scenarios with different seeds and collects performance metrics.
    """
    
    def __init__(self):
        """Initialize benchmark suite."""
        self.logger = get_logger()
        self.results = []
        
        # Benchmark scenarios
        self.scenarios = {
            'easy': {
                'description': 'Small grid, few hazards',
                'max_timesteps': 100,
                'expected_rescue_rate': 0.95
            },
            'medium': {
                'description': 'Medium grid, moderate hazards',
                'max_timesteps': 150,
                'expected_rescue_rate': 0.85
            },
            'hard': {
                'description': 'Large grid, many hazards',
                'max_timesteps': 200,
                'expected_rescue_rate': 0.70
            },
            'extreme': {
                'description': 'Very large grid, extreme hazards',
                'max_timesteps': 250,
                'expected_rescue_rate': 0.50
            }
        }
    
    def run_single_benchmark(self, difficulty: str, seed: int, max_timesteps: int = None) -> Dict:
        """
        Run a single benchmark scenario.
        
        Args:
            difficulty: Scenario difficulty level
            seed: Random seed for reproducibility
            max_timesteps: Maximum timesteps (overrides default)
            
        Returns:
            Dictionary with benchmark results
        """
        if max_timesteps is None:
            max_timesteps = self.scenarios[difficulty]['max_timesteps']
        
        print(f"\n{'='*80}")
        print(f"BENCHMARK: {difficulty.upper()} | Seed: {seed} | Max Timesteps: {max_timesteps}")
        print(f"{'='*80}")
        
        # Create simulator (headless mode)
        start_time = time.time()
        
        # Import here to avoid circular dependency
        import os
        os.environ['SDL_VIDEODRIVER'] = 'dummy'  # Headless mode
        
        sim = Simulator(
            seed=seed,
            coordination_mode='hybrid',
            enable_spawning=True,
            verbose=False,  # Disable explainability for speed
            difficulty=difficulty
        )
        
        sim.initialize()
        
        # Run simulation (headless)
        timestep = 0
        while sim.running and timestep < max_timesteps:
            # Execute timestep without rendering
            sim._execute_timestep()
            timestep += 1
            
            # Check win condition
            state = sim.grid.get_grid_state_summary()
            if state['survivors'] == 0:
                break
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Collect metrics
        state = sim.grid.get_grid_state_summary()
        total_rescued = sum(a.survivors_rescued for a in sim.agents)
        initial_survivors = sim.initial_survivors
        
        results = {
            'difficulty': difficulty,
            'seed': seed,
            'timesteps': timestep,
            'max_timesteps': max_timesteps,
            'duration_seconds': round(duration, 2),
            'initial_survivors': initial_survivors,
            'survivors_rescued': total_rescued,
            'survivors_remaining': state['survivors'],
            'rescue_rate': round(total_rescued / initial_survivors, 3) if initial_survivors > 0 else 0,
            'agents_spawned': len(sim.agents) - 6,  # Initial agents = 6
            'final_agent_count': len(sim.agents),
            'mode_switches': len(sim.coordinator.mode_history) if sim.coordinator else 0,
            'cells_explored': state.get('explored', 0),
            'final_fires': state['fires'],
            'final_floods': state['floods'],
            'completed': state['survivors'] == 0,
            'avg_timestep_duration': round(duration / timestep, 4) if timestep > 0 else 0
        }
        
        # Print summary
        print(f"\nRESULTS:")
        print(f"  Rescued: {total_rescued}/{initial_survivors} ({results['rescue_rate']*100:.1f}%)")
        print(f"  Timesteps: {timestep}/{max_timesteps}")
        print(f"  Agents Spawned: {results['agents_spawned']}")
        print(f"  Mode Switches: {results['mode_switches']}")
        print(f"  Duration: {duration:.2f}s")
        print(f"  Avg Timestep: {results['avg_timestep_duration']*1000:.2f}ms")
        
        return results
    
    def run_benchmark_set(self, difficulty: str, runs: int = 10, seeds: List[int] = None) -> List[Dict]:
        """
        Run multiple benchmarks for a difficulty level.
        
        Args:
            difficulty: Scenario difficulty
            runs: Number of runs
            seeds: List of seeds (auto-generated if None)
            
        Returns:
            List of result dictionaries
        """
        if seeds is None:
            # Generate seeds
            seeds = [42 + i * 100 for i in range(runs)]
        
        results = []
        for seed in seeds[:runs]:
            result = self.run_single_benchmark(difficulty, seed)
            results.append(result)
            self.results.append(result)
        
        return results
    
    def run_all_benchmarks(self, runs_per_difficulty: int = 10) -> Dict:
        """
        Run complete benchmark suite across all difficulties.
        
        Args:
            runs_per_difficulty: Number of runs per difficulty level
            
        Returns:
            Summary statistics
        """
        print(f"\n{'='*80}")
        print(f"RUNNING FULL BENCHMARK SUITE")
        print(f"Runs per difficulty: {runs_per_difficulty}")
        print(f"Total runs: {len(self.scenarios) * runs_per_difficulty}")
        print(f"{'='*80}\n")
        
        suite_start = time.time()
        
        for difficulty in self.scenarios.keys():
            print(f"\n{'='*80}")
            print(f"DIFFICULTY: {difficulty.upper()}")
            print(f"{'='*80}")
            
            self.run_benchmark_set(difficulty, runs=runs_per_difficulty)
        
        suite_duration = time.time() - suite_start
        
        # Generate summary
        summary = self.generate_summary()
        summary['total_duration_seconds'] = round(suite_duration, 2)
        summary['total_runs'] = len(self.results)
        
        print(f"\n{'='*80}")
        print(f"BENCHMARK SUITE COMPLETE")
        print(f"Total Duration: {suite_duration:.2f}s")
        print(f"Total Runs: {len(self.results)}")
        print(f"{'='*80}\n")
        
        return summary
    
    def generate_summary(self) -> Dict:
        """
        Generate summary statistics from all results.
        
        Returns:
            Dictionary with summary statistics
        """
        if not self.results:
            return {}
        
        summary = {
            'by_difficulty': {},
            'overall': {}
        }
        
        # Group by difficulty
        by_difficulty = {}
        for result in self.results:
            diff = result['difficulty']
            if diff not in by_difficulty:
                by_difficulty[diff] = []
            by_difficulty[diff].append(result)
        
        # Calculate statistics per difficulty
        for diff, results in by_difficulty.items():
            rescue_rates = [r['rescue_rate'] for r in results]
            timesteps = [r['timesteps'] for r in results]
            agents_spawned = [r['agents_spawned'] for r in results]
            mode_switches = [r['mode_switches'] for r in results]
            
            summary['by_difficulty'][diff] = {
                'runs': len(results),
                'rescue_rate': {
                    'mean': round(sum(rescue_rates) / len(rescue_rates), 3),
                    'min': round(min(rescue_rates), 3),
                    'max': round(max(rescue_rates), 3)
                },
                'timesteps': {
                    'mean': round(sum(timesteps) / len(timesteps), 1),
                    'min': min(timesteps),
                    'max': max(timesteps)
                },
                'agents_spawned': {
                    'mean': round(sum(agents_spawned) / len(agents_spawned), 1),
                    'min': min(agents_spawned),
                    'max': max(agents_spawned)
                },
                'mode_switches': {
                    'mean': round(sum(mode_switches) / len(mode_switches), 1),
                    'min': min(mode_switches),
                    'max': max(mode_switches)
                }
            }
        
        # Overall statistics
        all_rescue_rates = [r['rescue_rate'] for r in self.results]
        summary['overall'] = {
            'total_runs': len(self.results),
            'avg_rescue_rate': round(sum(all_rescue_rates) / len(all_rescue_rates), 3),
            'min_rescue_rate': round(min(all_rescue_rates), 3),
            'max_rescue_rate': round(max(all_rescue_rates), 3)
        }
        
        return summary
    
    def export_results(self, filename: str = None):
        """
        Export results to JSON file.
        
        Args:
            filename: Output filename (auto-generated if None)
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"benchmark_results_{timestamp}.json"
        
        data = {
            'timestamp': datetime.now().isoformat(),
            'results': self.results,
            'summary': self.generate_summary()
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"\n[EXPORT] Results saved to: {filename}")
        
        return filename
    
    def print_summary(self):
        """Print formatted summary to console."""
        summary = self.generate_summary()
        
        print(f"\n{'='*80}")
        print(f"BENCHMARK SUMMARY")
        print(f"{'='*80}\n")
        
        for diff, stats in summary['by_difficulty'].items():
            print(f"{diff.upper()}:")
            print(f"  Runs: {stats['runs']}")
            print(f"  Rescue Rate: {stats['rescue_rate']['mean']*100:.1f}% "
                  f"(min: {stats['rescue_rate']['min']*100:.1f}%, max: {stats['rescue_rate']['max']*100:.1f}%)")
            print(f"  Timesteps: {stats['timesteps']['mean']:.1f} "
                  f"(min: {stats['timesteps']['min']}, max: {stats['timesteps']['max']})")
            print(f"  Agents Spawned: {stats['agents_spawned']['mean']:.1f} "
                  f"(min: {stats['agents_spawned']['min']}, max: {stats['agents_spawned']['max']})")
            print(f"  Mode Switches: {stats['mode_switches']['mean']:.1f} "
                  f"(min: {stats['mode_switches']['min']}, max: {stats['mode_switches']['max']})")
            print()
        
        print(f"OVERALL:")
        print(f"  Total Runs: {summary['overall']['total_runs']}")
        print(f"  Average Rescue Rate: {summary['overall']['avg_rescue_rate']*100:.1f}%")
        print(f"  Range: {summary['overall']['min_rescue_rate']*100:.1f}% - "
              f"{summary['overall']['max_rescue_rate']*100:.1f}%")
        print(f"\n{'='*80}\n")


def main():
    """Run benchmark suite from command line."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run benchmark suite')
    parser.add_argument('--difficulty', type=str, choices=['easy', 'medium', 'hard', 'extreme', 'all'],
                       default='all', help='Difficulty level to benchmark')
    parser.add_argument('--runs', type=int, default=10, help='Number of runs per difficulty')
    parser.add_argument('--output', type=str, help='Output filename for results')
    
    args = parser.parse_args()
    
    suite = BenchmarkSuite()
    
    if args.difficulty == 'all':
        suite.run_all_benchmarks(runs_per_difficulty=args.runs)
    else:
        suite.run_benchmark_set(args.difficulty, runs=args.runs)
    
    suite.print_summary()
    suite.export_results(args.output)


if __name__ == '__main__':
    main()
