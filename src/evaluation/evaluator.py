"""
Evaluation Framework for Multi-Agent Rescue System

Runs comparative benchmarks across coordination protocols.

Author: Enhanced Multi-Agent System
Date: February 2026
"""

import sys
import time
import json
from typing import Dict, List
from src.core.simulator import Simulator
from src.utils.config import SIMULATION, LOG


class EvaluationFramework:
    """
    Benchmarking and evaluation system for coordination protocols.
    """
    
    def __init__(self):
        """Initialize evaluation framework."""
        self.results = []
    
    def run_trial(
        self,
        protocol: str,
        seed: int,
        max_timesteps: int,
        scenario_name: str
    ) -> Dict:
        """
        Run a single trial.
        
        Args:
            protocol: Coordination protocol to test
            seed: Random seed
            max_timesteps: Maximum timesteps
            scenario_name: Name of scenario
            
        Returns:
            Trial results dictionary
        """
        # Suppress UI for batch testing
        LOG.LOG_LEVEL_DETAIL = "MINIMAL"
        
        # Create simulator
        start_time = time.time()
        
        try:
            simulator = Simulator(
                seed=seed,
                coordination_mode=protocol,
                enable_spawning=True
            )
            simulator.initialize()
            
            # Run simulation (without pygame display)
            timestep = 0
            while timestep < max_timesteps and len(simulator.grid.survivor_positions) > 0:
                simulator.execute_timestep()
                timestep += 1
            
            end_time = time.time()
            
            # Collect results
            results = {
                'protocol': protocol,
                'seed': seed,
                'scenario': scenario_name,
                'timesteps': timestep,
                'survivors_rescued': simulator.total_survivors_rescued,
                'survivors_remaining': len(simulator.grid.survivor_positions),
                'cells_explored': simulator.total_cells_explored,
                'final_agents': len(simulator.agents),
                'execution_time': end_time - start_time,
                'success': len(simulator.grid.survivor_positions) == 0
            }
            
            # Get coordination stats
            if simulator.coordinator:
                coord_stats = simulator.coordinator.get_coordination_stats()
                results['coordination'] = coord_stats
            
            # Get spawning stats
            if simulator.spawner:
                spawn_stats = simulator.spawner.get_spawn_stats()
                results['spawning'] = spawn_stats
            
            return results
            
        except Exception as e:
            return {
                'protocol': protocol,
                'seed': seed,
                'scenario': scenario_name,
                'error': str(e),
                'success': False
            }
    
    def run_comparison(
        self,
        protocols: List[str],
        seeds: List[int],
        max_timesteps: int = 200,
        scenario: str = "standard"
    ):
        """
        Run comparative evaluation across protocols.
        
        Args:
            protocols: List of protocols to test
            seeds: List of random seeds for trials
            max_timesteps: Maximum timesteps per trial
            scenario: Scenario name
        """
        print("=" * 80)
        print("MULTI-AGENT RESCUE SYSTEM - COMPARATIVE EVALUATION")
        print("=" * 80)
        print(f"\nProtocols: {', '.join(p.upper() for p in protocols)}")
        print(f"Trials per protocol: {len(seeds)}")
        print(f"Max timesteps: {max_timesteps}")
        print(f"Scenario: {scenario}")
        print("\nRunning trials...\n")
        
        total_trials = len(protocols) * len(seeds)
        completed = 0
        
        for protocol in protocols:
            for seed in seeds:
                completed += 1
                print(f"[{completed}/{total_trials}] Running {protocol.upper()} with seed {seed}...", end=" ")
                
                result = self.run_trial(protocol, seed, max_timesteps, scenario)
                self.results.append(result)
                
                if result.get('success'):
                    print(f"[OK] Success in {result['timesteps']} steps")
                else:
                    if 'error' in result:
                        print(f"[FAIL] Error: {result['error']}")
                    else:
                        print(f"[INCOMPLETE] ({result['survivors_rescued']}/{result['survivors_rescued'] + result['survivors_remaining']} rescued)")
        
        print("\n" + "=" * 80)
        print("EVALUATION COMPLETE")
        print("=" * 80)
        
        self._print_summary()
        self._save_results()
    
    def _print_summary(self):
        """Print summary statistics."""
        print("\nSUMMARY STATISTICS\n")
        
        protocols = {}
        
        for result in self.results:
            if 'error' in result:
                continue
            
            protocol = result['protocol']
            
            if protocol not in protocols:
                protocols[protocol] = {
                    'success_count': 0,
                    'total_count': 0,
                    'avg_timesteps': 0,
                    'avg_survivors_rescued': 0,
                    'mode_switches': []
                }
            
            protocols[protocol]['total_count'] += 1
            
            if result.get('success'):
                protocols[protocol]['success_count'] += 1
            
            protocols[protocol]['avg_timesteps'] += result.get('timesteps', 0)
            protocols[protocol]['avg_survivors_rescued'] += result.get('survivors_rescued', 0)
            
            if 'coordination' in result:
                protocols[protocol]['mode_switches'].append(
                    result['coordination'].get('mode_switches', 0)
                )
        
        # Compute averages
        for protocol, stats in protocols.items():
            count = stats['total_count']
            if count > 0:
                stats['avg_timesteps'] /= count
                stats['avg_survivors_rescued'] /= count
                stats['success_rate'] = stats['success_count'] / count * 100
        
        # Print table
        print(f"{'Protocol':<15} {'Success Rate':<15} {'Avg Steps':<12} {'Avg Rescued':<12} {'Mode Switches':<15}")
        print("-" * 80)
        
        for protocol in sorted(protocols.keys()):
            stats = protocols[protocol]
            
            switches = stats['mode_switches']
            avg_switches = sum(switches) / len(switches) if switches else 0
            
            print(f"{protocol.upper():<15} "
                  f"{stats['success_rate']:>6.1f}%        "
                  f"{stats['avg_timesteps']:>8.1f}    "
                  f"{stats['avg_survivors_rescued']:>8.1f}    "
                  f"{avg_switches:>8.1f}")
        
        print()
    
    def _save_results(self, filename: str = "evaluation_results.json"):
        """Save results to JSON file."""
        with open(filename, 'w') as f:
            json.dump({
                'results': self.results,
                'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
            }, f, indent=2)
        
        print(f"\n[SAVED] Results saved to {filename}\n")


def main():
    """Run evaluation from command line."""
    evaluator = EvaluationFramework()
    
    # Test all protocols with 5 different seeds
    protocols = ['centralized', 'auction', 'hybrid']
    seeds = [42, 123, 456, 789, 1024]
    
    evaluator.run_comparison(
        protocols=protocols,
        seeds=seeds,
        max_timesteps=300,
        scenario="standard"
    )


if __name__ == "__main__":
    main()
