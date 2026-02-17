"""
Benchmark Visualizer
Creates ASCII charts and exports data for external visualization.
"""

from typing import Dict, List


class BenchmarkVisualizer:
    """
    Visualizer for benchmark results.
    
    Creates ASCII charts and exports data for plotting tools.
    """
    
    @staticmethod
    def create_bar_chart(data: Dict[str, float], title: str = "Bar Chart", 
                        width: int = 50, value_label: str = "") -> str:
        """
        Create ASCII bar chart.
        
        Args:
            data: Dictionary of {label: value}
            title: Chart title
            width: Maximum bar width in characters
            value_label: Label for values (e.g., "%", "ms")
            
        Returns:
            ASCII bar chart as string
        """
        if not data:
            return "No data to display"
        
        max_value = max(data.values())
        max_label_len = max(len(str(k)) for k in data.keys())
        
        chart = f"\n{'='*70}\n{title}\n{'='*70}\n\n"
        
        for label, value in data.items():
            bar_length = int((value / max_value) * width) if max_value > 0 else 0
            bar = '█' * bar_length
            padding = ' ' * (max_label_len - len(str(label)))
            chart += f"{label}{padding} | {bar} {value:.1f}{value_label}\n"
        
        chart += f"\n{'='*70}\n"
        return chart
    
    @staticmethod
    def create_comparison_chart(datasets: Dict[str, Dict[str, float]], 
                               title: str = "Comparison Chart") -> str:
        """
        Create comparison chart for multiple datasets.
        
        Args:
            datasets: Dictionary of {dataset_name: {metric: value}}
            title: Chart title
            
        Returns:
            ASCII comparison chart
        """
        if not datasets:
            return "No data to display"
        
        chart = f"\n{'='*80}\n{title}\n{'='*80}\n\n"
        
        # Get all unique metrics
        all_metrics = set()
        for dataset in datasets.values():
            all_metrics.update(dataset.keys())
        
        # Create table header
        dataset_names = list(datasets.keys())
        header = f"{'Metric':<20}"
        for name in dataset_names:
            header += f" | {name:<15}"
        chart += header + "\n"
        chart += "-" * 80 + "\n"
        
        # Create rows
        for metric in sorted(all_metrics):
            row = f"{metric:<20}"
            for name in dataset_names:
                value = datasets[name].get(metric, 0)
                row += f" | {value:<15.2f}"
            chart += row + "\n"
        
        chart += f"\n{'='*80}\n"
        return chart
    
    @staticmethod
    def visualize_benchmark_summary(summary: Dict) -> str:
        """
        Create comprehensive visualization of benchmark summary.
        
        Args:
            summary: Summary dictionary from BenchmarkSuite
            
        Returns:
            Formatted visualization string
        """
        output = "\n" + "="*80 + "\n"
        output += "BENCHMARK VISUALIZATION\n"
        output += "="*80 + "\n"
        
        if 'by_difficulty' not in summary:
            return output + "\nNo data available\n"
        
        # Rescue Rate by Difficulty
        rescue_rates = {
            diff: stats['rescue_rate']['mean'] * 100
            for diff, stats in summary['by_difficulty'].items()
        }
        output += BenchmarkVisualizer.create_bar_chart(
            rescue_rates,
            "Rescue Rate by Difficulty",
            width=40,
            value_label="%"
        )
        
        # Agents Spawned by Difficulty
        agents_spawned = {
            diff: stats['agents_spawned']['mean']
            for diff, stats in summary['by_difficulty'].items()
        }
        output += BenchmarkVisualizer.create_bar_chart(
            agents_spawned,
            "Average Agents Spawned by Difficulty",
            width=40,
            value_label=" agents"
        )
        
        # Mode Switches by Difficulty
        mode_switches = {
            diff: stats['mode_switches']['mean']
            for diff, stats in summary['by_difficulty'].items()
        }
        output += BenchmarkVisualizer.create_bar_chart(
            mode_switches,
            "Average Mode Switches by Difficulty",
            width=40,
            value_label=" switches"
        )
        
        # Timesteps by Difficulty
        timesteps = {
            diff: stats['timesteps']['mean']
            for diff, stats in summary['by_difficulty'].items()
        }
        output += BenchmarkVisualizer.create_bar_chart(
            timesteps,
            "Average Timesteps by Difficulty",
            width=40,
            value_label=" steps"
        )
        
        return output
    
    @staticmethod
    def export_for_plotting(summary: Dict, filename: str = "plot_data.csv"):
        """
        Export data in CSV format for external plotting tools.
        
        Args:
            summary: Summary dictionary from BenchmarkSuite
            filename: Output CSV filename
        """
        if 'by_difficulty' not in summary:
            print("No data to export")
            return
        
        with open(filename, 'w') as f:
            # Header
            f.write("difficulty,rescue_rate_mean,rescue_rate_std,timesteps_mean,timesteps_std,")
            f.write("agents_spawned_mean,agents_spawned_std,mode_switches_mean,mode_switches_std\n")
            
            # Data rows
            for diff, stats in summary['by_difficulty'].items():
                f.write(f"{diff},")
                f.write(f"{stats['rescue_rate']['mean']},")
                f.write(f"{stats['rescue_rate'].get('std', 0)},")
                f.write(f"{stats['timesteps']['mean']},")
                f.write(f"{stats['timesteps'].get('std', 0)},")
                f.write(f"{stats['agents_spawned']['mean']},")
                f.write(f"{stats['agents_spawned'].get('std', 0)},")
                f.write(f"{stats['mode_switches']['mean']},")
                f.write(f"{stats['mode_switches'].get('std', 0)}\n")
        
        print(f"\n[EXPORT] Plot data saved to: {filename}")
    
    @staticmethod
    def create_performance_table(results: List[Dict]) -> str:
        """
        Create formatted performance table.
        
        Args:
            results: List of benchmark results
            
        Returns:
            Formatted table string
        """
        if not results:
            return "No results to display"
        
        table = "\n" + "="*100 + "\n"
        table += "DETAILED PERFORMANCE TABLE\n"
        table += "="*100 + "\n\n"
        
        # Header
        table += f"{'Difficulty':<12} | {'Seed':<8} | {'Rescued':<10} | {'Rate':<8} | "
        table += f"{'Steps':<8} | {'Agents':<8} | {'Switches':<10} | {'Time':<8}\n"
        table += "-"*100 + "\n"
        
        # Rows
        for r in results:
            table += f"{r['difficulty']:<12} | "
            table += f"{r['seed']:<8} | "
            table += f"{r['survivors_rescued']}/{r['initial_survivors']:<7} | "
            table += f"{r['rescue_rate']*100:>6.1f}% | "
            table += f"{r['timesteps']:<8} | "
            table += f"{r['agents_spawned']:<8} | "
            table += f"{r['mode_switches']:<10} | "
            table += f"{r['duration_seconds']:>6.2f}s\n"
        
        table += "\n" + "="*100 + "\n"
        return table
