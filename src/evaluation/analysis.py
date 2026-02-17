"""
Advanced Analysis Modules
Scalability, success rate, mode switching, and agent performance analysis.
"""

from typing import Dict, List
from .statistics import StatisticalAnalyzer


class ScalabilityAnalyzer:
    """Analyze system scalability across different grid sizes."""
    
    @staticmethod
    def analyze_scalability(results: List[Dict]) -> Dict:
        """
        Analyze performance across different grid sizes.
        
        Args:
            results: Benchmark results with grid size info
            
        Returns:
            Scalability analysis
        """
        # Group by grid size (inferred from difficulty)
        size_map = {
            'easy': '20x20',
            'medium': '30x30',
            'hard': '40x40',
            'extreme': '50x50'
        }
        
        by_size = {}
        for result in results:
            size = size_map.get(result['difficulty'], 'unknown')
            if size not in by_size:
                by_size[size] = []
            by_size[size].append(result)
        
        analysis = {}
        for size, size_results in by_size.items():
            durations = [r['avg_timestep_duration'] for r in size_results]
            rescue_rates = [r['rescue_rate'] for r in size_results]
            
            analysis[size] = {
                'avg_timestep_ms': round(StatisticalAnalyzer.calculate_mean(durations) * 1000, 2),
                'avg_rescue_rate': round(StatisticalAnalyzer.calculate_mean(rescue_rates), 3),
                'sample_count': len(size_results)
            }
        
        return analysis
    
    @staticmethod
    def print_scalability_report(analysis: Dict):
        """Print formatted scalability report."""
        print("\n" + "="*70)
        print("SCALABILITY ANALYSIS")
        print("="*70 + "\n")
        
        print(f"{'Grid Size':<15} | {'Avg Timestep':<15} | {'Rescue Rate':<15} | {'Samples':<10}")
        print("-"*70)
        
        for size, stats in sorted(analysis.items()):
            print(f"{size:<15} | {stats['avg_timestep_ms']:>13.2f}ms | "
                  f"{stats['avg_rescue_rate']*100:>13.1f}% | {stats['sample_count']:<10}")
        
        print("\n" + "="*70 + "\n")


class SuccessAnalyzer:
    """Analyze rescue success patterns and failure reasons."""
    
    @staticmethod
    def analyze_success_patterns(results: List[Dict]) -> Dict:
        """
        Analyze success patterns across scenarios.
        
        Args:
            results: Benchmark results
            
        Returns:
            Success pattern analysis
        """
        by_difficulty = {}
        
        for result in results:
            diff = result['difficulty']
            if diff not in by_difficulty:
                by_difficulty[diff] = {
                    'total': 0,
                    'completed': 0,
                    'rescue_rates': [],
                    'timeout_count': 0,
                    'partial_success': 0
                }
            
            stats = by_difficulty[diff]
            stats['total'] += 1
            stats['rescue_rates'].append(result['rescue_rate'])
            
            if result['completed']:
                stats['completed'] += 1
            elif result['timesteps'] >= result['max_timesteps']:
                stats['timeout_count'] += 1
            
            if 0 < result['rescue_rate'] < 1.0:
                stats['partial_success'] += 1
        
        # Calculate summary statistics
        analysis = {}
        for diff, stats in by_difficulty.items():
            completion_rate = stats['completed'] / stats['total'] if stats['total'] > 0 else 0
            avg_rescue_rate = StatisticalAnalyzer.calculate_mean(stats['rescue_rates'])
            
            analysis[diff] = {
                'total_runs': stats['total'],
                'completed': stats['completed'],
                'completion_rate': round(completion_rate, 3),
                'avg_rescue_rate': round(avg_rescue_rate, 3),
                'timeout_count': stats['timeout_count'],
                'partial_success': stats['partial_success']
            }
        
        return analysis
    
    @staticmethod
    def print_success_report(analysis: Dict):
        """Print formatted success analysis report."""
        print("\n" + "="*80)
        print("SUCCESS RATE ANALYSIS")
        print("="*80 + "\n")
        
        print(f"{'Difficulty':<12} | {'Runs':<6} | {'Completed':<10} | {'Comp %':<8} | "
              f"{'Rescue %':<10} | {'Timeouts':<10}")
        print("-"*80)
        
        for diff, stats in sorted(analysis.items()):
            print(f"{diff:<12} | {stats['total_runs']:<6} | {stats['completed']:<10} | "
                  f"{stats['completion_rate']*100:>6.1f}% | "
                  f"{stats['avg_rescue_rate']*100:>8.1f}% | {stats['timeout_count']:<10}")
        
        print("\n" + "="*80 + "\n")


class ModeAnalyzer:
    """Analyze coordination mode switching patterns."""
    
    @staticmethod
    def analyze_mode_switches(results: List[Dict]) -> Dict:
        """
        Analyze mode switching patterns.
        
        Args:
            results: Benchmark results
            
        Returns:
            Mode switch analysis
        """
        by_difficulty = {}
        
        for result in results:
            diff = result['difficulty']
            if diff not in by_difficulty:
                by_difficulty[diff] = {
                    'switch_counts': [],
                    'rescue_rates': [],
                    'with_switches': 0,
                    'without_switches': 0
                }
            
            stats = by_difficulty[diff]
            switch_count = result['mode_switches']
            stats['switch_counts'].append(switch_count)
            stats['rescue_rates'].append(result['rescue_rate'])
            
            if switch_count > 0:
                stats['with_switches'] += 1
            else:
                stats['without_switches'] += 1
        
        # Calculate correlations
        analysis = {}
        for diff, stats in by_difficulty.items():
            avg_switches = StatisticalAnalyzer.calculate_mean(stats['switch_counts'])
            avg_rescue_rate = StatisticalAnalyzer.calculate_mean(stats['rescue_rates'])
            
            analysis[diff] = {
                'avg_switches': round(avg_switches, 2),
                'avg_rescue_rate': round(avg_rescue_rate, 3),
                'runs_with_switches': stats['with_switches'],
                'runs_without_switches': stats['without_switches'],
                'switch_frequency': round(stats['with_switches'] / len(stats['switch_counts']), 3)
                    if stats['switch_counts'] else 0
            }
        
        return analysis
    
    @staticmethod
    def print_mode_report(analysis: Dict):
        """Print formatted mode switching report."""
        print("\n" + "="*80)
        print("MODE SWITCHING ANALYSIS")
        print("="*80 + "\n")
        
        print(f"{'Difficulty':<12} | {'Avg Switches':<14} | {'Rescue Rate':<13} | "
              f"{'Switch Freq':<12}")
        print("-"*80)
        
        for diff, stats in sorted(analysis.items()):
            print(f"{diff:<12} | {stats['avg_switches']:>12.2f} | "
                  f"{stats['avg_rescue_rate']*100:>11.1f}% | "
                  f"{stats['switch_frequency']*100:>10.1f}%")
        
        print("\n" + "="*80 + "\n")


class AgentAnalyzer:
    """Analyze agent performance and spawning effectiveness."""
    
    @staticmethod
    def analyze_agent_performance(results: List[Dict]) -> Dict:
        """
        Analyze agent spawning and performance.
        
        Args:
            results: Benchmark results
            
        Returns:
            Agent performance analysis
        """
        by_difficulty = {}
        
        for result in results:
            diff = result['difficulty']
            if diff not in by_difficulty:
                by_difficulty[diff] = {
                    'agents_spawned': [],
                    'rescue_rates': [],
                    'final_agent_counts': []
                }
            
            stats = by_difficulty[diff]
            stats['agents_spawned'].append(result['agents_spawned'])
            stats['rescue_rates'].append(result['rescue_rate'])
            stats['final_agent_counts'].append(result['final_agent_count'])
        
        # Calculate statistics
        analysis = {}
        for diff, stats in by_difficulty.items():
            avg_spawned = StatisticalAnalyzer.calculate_mean(stats['agents_spawned'])
            avg_rescue_rate = StatisticalAnalyzer.calculate_mean(stats['rescue_rates'])
            avg_final_count = StatisticalAnalyzer.calculate_mean(stats['final_agent_counts'])
            
            # Calculate efficiency (rescue rate per agent)
            efficiency = avg_rescue_rate / avg_final_count if avg_final_count > 0 else 0
            
            analysis[diff] = {
                'avg_agents_spawned': round(avg_spawned, 2),
                'avg_final_agent_count': round(avg_final_count, 1),
                'avg_rescue_rate': round(avg_rescue_rate, 3),
                'efficiency_per_agent': round(efficiency, 4)
            }
        
        return analysis
    
    @staticmethod
    def print_agent_report(analysis: Dict):
        """Print formatted agent performance report."""
        print("\n" + "="*80)
        print("AGENT PERFORMANCE ANALYSIS")
        print("="*80 + "\n")
        
        print(f"{'Difficulty':<12} | {'Spawned':<10} | {'Final Count':<13} | "
              f"{'Rescue Rate':<13} | {'Efficiency':<12}")
        print("-"*80)
        
        for diff, stats in sorted(analysis.items()):
            print(f"{diff:<12} | {stats['avg_agents_spawned']:>8.2f} | "
                  f"{stats['avg_final_agent_count']:>11.1f} | "
                  f"{stats['avg_rescue_rate']*100:>11.1f}% | "
                  f"{stats['efficiency_per_agent']:>10.4f}")
        
        print("\n" + "="*80 + "\n")


def run_comprehensive_analysis(results: List[Dict]):
    """
    Run all analysis modules on benchmark results.
    
    Args:
        results: List of benchmark results
    """
    print("\n" + "="*80)
    print("COMPREHENSIVE BENCHMARK ANALYSIS")
    print("="*80)
    
    # Scalability Analysis
    scalability = ScalabilityAnalyzer.analyze_scalability(results)
    ScalabilityAnalyzer.print_scalability_report(scalability)
    
    # Success Analysis
    success = SuccessAnalyzer.analyze_success_patterns(results)
    SuccessAnalyzer.print_success_report(success)
    
    # Mode Switching Analysis
    modes = ModeAnalyzer.analyze_mode_switches(results)
    ModeAnalyzer.print_mode_report(modes)
    
    # Agent Performance Analysis
    agents = AgentAnalyzer.analyze_agent_performance(results)
    AgentAnalyzer.print_agent_report(agents)
    
    return {
        'scalability': scalability,
        'success': success,
        'modes': modes,
        'agents': agents
    }
