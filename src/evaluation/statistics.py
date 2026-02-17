"""
Statistical Analysis for Benchmark Results
Calculates mean, std dev, confidence intervals, and significance tests.
"""

import math
from typing import Dict, List


class StatisticalAnalyzer:
    """
    Statistical analysis for benchmark results.
    
    Provides mean, standard deviation, confidence intervals, and more.
    """
    
    @staticmethod
    def calculate_mean(values: List[float]) -> float:
        """Calculate arithmetic mean."""
        if not values:
            return 0.0
        return sum(values) / len(values)
    
    @staticmethod
    def calculate_std_dev(values: List[float]) -> float:
        """Calculate standard deviation."""
        if len(values) < 2:
            return 0.0
        
        mean = StatisticalAnalyzer.calculate_mean(values)
        variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
        return math.sqrt(variance)
    
    @staticmethod
    def calculate_confidence_interval(values: List[float], confidence: float = 0.95) -> tuple:
        """
        Calculate confidence interval.
        
        Args:
            values: List of values
            confidence: Confidence level (default 0.95 for 95%)
            
        Returns:
            Tuple of (lower_bound, upper_bound)
        """
        if len(values) < 2:
            mean = StatisticalAnalyzer.calculate_mean(values)
            return (mean, mean)
        
        mean = StatisticalAnalyzer.calculate_mean(values)
        std_dev = StatisticalAnalyzer.calculate_std_dev(values)
        n = len(values)
        
        # Use t-distribution critical value (approximation for 95% CI)
        # For large n, t ≈ 1.96; for small n, use conservative estimate
        if n >= 30:
            t_critical = 1.96
        elif n >= 10:
            t_critical = 2.26
        else:
            t_critical = 2.78
        
        margin_of_error = t_critical * (std_dev / math.sqrt(n))
        
        return (
            round(mean - margin_of_error, 3),
            round(mean + margin_of_error, 3)
        )
    
    @staticmethod
    def calculate_percentile(values: List[float], percentile: float) -> float:
        """
        Calculate percentile value.
        
        Args:
            values: List of values
            percentile: Percentile (0-100)
            
        Returns:
            Value at percentile
        """
        if not values:
            return 0.0
        
        sorted_values = sorted(values)
        index = (percentile / 100) * (len(sorted_values) - 1)
        
        if index.is_integer():
            return sorted_values[int(index)]
        else:
            lower = sorted_values[int(index)]
            upper = sorted_values[int(index) + 1]
            fraction = index - int(index)
            return lower + (upper - lower) * fraction
    
    @staticmethod
    def analyze_dataset(values: List[float]) -> Dict:
        """
        Comprehensive statistical analysis of a dataset.
        
        Args:
            values: List of values
            
        Returns:
            Dictionary with statistical measures
        """
        if not values:
            return {
                'count': 0,
                'mean': 0.0,
                'std_dev': 0.0,
                'min': 0.0,
                'max': 0.0,
                'median': 0.0,
                'q1': 0.0,
                'q3': 0.0,
                'ci_95': (0.0, 0.0)
            }
        
        sorted_values = sorted(values)
        
        return {
            'count': len(values),
            'mean': round(StatisticalAnalyzer.calculate_mean(values), 3),
            'std_dev': round(StatisticalAnalyzer.calculate_std_dev(values), 3),
            'min': round(min(values), 3),
            'max': round(max(values), 3),
            'median': round(StatisticalAnalyzer.calculate_percentile(values, 50), 3),
            'q1': round(StatisticalAnalyzer.calculate_percentile(values, 25), 3),
            'q3': round(StatisticalAnalyzer.calculate_percentile(values, 75), 3),
            'ci_95': StatisticalAnalyzer.calculate_confidence_interval(values)
        }
    
    @staticmethod
    def compare_datasets(dataset1: List[float], dataset2: List[float], 
                        name1: str = "Dataset 1", name2: str = "Dataset 2") -> Dict:
        """
        Compare two datasets statistically.
        
        Args:
            dataset1: First dataset
            dataset2: Second dataset
            name1: Name of first dataset
            name2: Name of second dataset
            
        Returns:
            Dictionary with comparison results
        """
        stats1 = StatisticalAnalyzer.analyze_dataset(dataset1)
        stats2 = StatisticalAnalyzer.analyze_dataset(dataset2)
        
        mean_diff = stats1['mean'] - stats2['mean']
        mean_diff_pct = (mean_diff / stats2['mean'] * 100) if stats2['mean'] != 0 else 0
        
        return {
            name1: stats1,
            name2: stats2,
            'comparison': {
                'mean_difference': round(mean_diff, 3),
                'mean_difference_pct': round(mean_diff_pct, 1),
                'better': name1 if stats1['mean'] > stats2['mean'] else name2
            }
        }
    
    @staticmethod
    def analyze_benchmark_results(results: List[Dict]) -> Dict:
        """
        Analyze benchmark results with comprehensive statistics.
        
        Args:
            results: List of benchmark result dictionaries
            
        Returns:
            Dictionary with statistical analysis
        """
        if not results:
            return {}
        
        # Extract metrics
        rescue_rates = [r['rescue_rate'] for r in results]
        timesteps = [r['timesteps'] for r in results]
        agents_spawned = [r['agents_spawned'] for r in results]
        mode_switches = [r['mode_switches'] for r in results]
        durations = [r['duration_seconds'] for r in results]
        
        return {
            'rescue_rate': StatisticalAnalyzer.analyze_dataset(rescue_rates),
            'timesteps': StatisticalAnalyzer.analyze_dataset(timesteps),
            'agents_spawned': StatisticalAnalyzer.analyze_dataset(agents_spawned),
            'mode_switches': StatisticalAnalyzer.analyze_dataset(mode_switches),
            'duration_seconds': StatisticalAnalyzer.analyze_dataset(durations)
        }
    
    @staticmethod
    def print_analysis(analysis: Dict, title: str = "Statistical Analysis"):
        """
        Print formatted statistical analysis.
        
        Args:
            analysis: Analysis dictionary from analyze_dataset
            title: Title for the analysis
        """
        print(f"\n{'='*60}")
        print(f"{title}")
        print(f"{'='*60}")
        
        for metric, stats in analysis.items():
            if isinstance(stats, dict) and 'mean' in stats:
                print(f"\n{metric.upper().replace('_', ' ')}:")
                print(f"  Count: {stats['count']}")
                print(f"  Mean: {stats['mean']:.3f}")
                print(f"  Std Dev: {stats['std_dev']:.3f}")
                print(f"  Min: {stats['min']:.3f}")
                print(f"  Max: {stats['max']:.3f}")
                print(f"  Median: {stats['median']:.3f}")
                print(f"  Q1: {stats['q1']:.3f}")
                print(f"  Q3: {stats['q3']:.3f}")
                print(f"  95% CI: [{stats['ci_95'][0]:.3f}, {stats['ci_95'][1]:.3f}]")
        
        print(f"\n{'='*60}\n")
