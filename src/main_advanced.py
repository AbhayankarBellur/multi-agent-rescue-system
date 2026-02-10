"""
AI-Driven Multi-Agent Disaster Rescue Simulator
Advanced Entry Point with Dynamic Configuration

Patent-worthy features:
- Dynamic grid sizing (10x10 to 200x200)
- Dynamic survivor count (1-50)
- Dynamic hazard coverage (0-50%)
- Difficulty presets
- Performance benchmarking
- Multi-objective optimization
"""

import sys
import argparse
from src.core.simulator import Simulator
from src.utils.config import SIMULATION, GRID, HAZARD


def parse_grid_size(value):
    """Parse grid size in format WIDTHxHEIGHT"""
    try:
        width, height = map(int, value.lower().split('x'))
        if width < 10 or height < 10:
            raise ValueError("Grid dimensions must be at least 10x10")
        if width > 200 or height > 200:
            raise ValueError("Grid dimensions cannot exceed 200x200")
        return (width, height)
    except:
        raise argparse.ArgumentTypeError(
            "Grid size must be in format WIDTHxHEIGHT (e.g., 50x40)"
        )


def apply_difficulty_preset(difficulty):
    """Apply difficulty preset configurations"""
    presets = {
        'easy': {
            'hazard_coverage': 5,
            'fire_spread': 0.02,
            'flood_spread': 0.02,
            'debris_gen': 0.005,
            'survivors': 6,
            'description': 'Low hazard density, slow spread'
        },
        'medium': {
            'hazard_coverage': 10,
            'fire_spread': 0.03,
            'flood_spread': 0.03,
            'debris_gen': 0.01,
            'survivors': 8,
            'description': 'Moderate challenge (default)'
        },
        'hard': {
            'hazard_coverage': 15,
            'fire_spread': 0.05,
            'flood_spread': 0.04,
            'debris_gen': 0.02,
            'survivors': 12,
            'description': 'High hazard density and spread rates'
        },
        'extreme': {
            'hazard_coverage': 20,
            'fire_spread': 0.07,
            'flood_spread': 0.06,
            'debris_gen': 0.03,
            'survivors': 15,
            'description': 'Maximum challenge - research grade'
        }
    }
    
    return presets.get(difficulty.lower(), presets['medium'])


def main():
    """
    Advanced entry point with full configuration options.
    """
    parser = argparse.ArgumentParser(
        description="AI Disaster Rescue Simulator - Advanced Multi-Agent System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m src.main_advanced
  python -m src.main_advanced --grid-size 80x60 --survivors 20
  python -m src.main_advanced --hazard-coverage 25 --max-timesteps 500
  python -m src.main_advanced --difficulty extreme --seed 123
  python -m src.main_advanced --benchmark --grid-size 100x75
        """
    )
    
    # Grid Configuration
    parser.add_argument(
        '--grid-size',
        type=parse_grid_size,
        default=None,
        help='Grid dimensions as WIDTHxHEIGHT (e.g., 50x40, range: 10-200)'
    )
    
    # Scenario Configuration
    parser.add_argument(
        '--survivors',
        type=int,
        default=None,
        help='Number of survivors to rescue (default: 8, range: 1-50)'
    )
    
    parser.add_argument(
        '--hazard-coverage',
        type=float,
        default=None,
        help='Initial hazard coverage percentage (default: 10, range: 0-50)'
    )
    
    parser.add_argument(
        '--difficulty',
        choices=['easy', 'medium', 'hard', 'extreme'],
        default=None,
        help='Difficulty preset (overrides other hazard settings)'
    )
    
    # Simulation Parameters
    parser.add_argument(
        '--seed',
        type=int,
        default=SIMULATION.RANDOM_SEED,
        help=f'Random seed for reproducibility (default: {SIMULATION.RANDOM_SEED})'
    )
    
    parser.add_argument(
        '--max-timesteps',
        type=int,
        default=SIMULATION.MAX_TIMESTEPS,
        help=f'Maximum simulation timesteps (default: {SIMULATION.MAX_TIMESTEPS})'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['MINIMAL', 'NORMAL', 'VERBOSE'],
        default='NORMAL',
        help='Logging detail level (default: NORMAL)'
    )
    
    parser.add_argument(
        '--benchmark',
        action='store_true',
        help='Run in benchmark mode with performance metrics'
    )
    
    args = parser.parse_args()
    
    # Apply difficulty preset if specified
    if args.difficulty:
        preset = apply_difficulty_preset(args.difficulty)
        print(f"\n🎯 Difficulty Preset: {args.difficulty.upper()}")
        print(f"   {preset['description']}")
        
        # Apply preset values (can be overridden by explicit arguments)
        if args.hazard_coverage is None:
            args.hazard_coverage = preset['hazard_coverage']
        if args.survivors is None:
            args.survivors = preset['survivors']
        
        HAZARD.FIRE_SPREAD_RATE = preset['fire_spread']
        HAZARD.FLOOD_SPREAD_RATE = preset['flood_spread']
        HAZARD.DEBRIS_GENERATION_NEAR_FIRE = preset['debris_gen']
    
    # Update grid configuration
    if args.grid_size:
        GRID.WIDTH, GRID.HEIGHT = args.grid_size
        # Adjust UI to fit grid
        from src.utils.config import UI
        UI.WINDOW_WIDTH = GRID.WIDTH * GRID.CELL_SIZE + UI.LOG_PANEL_WIDTH
        UI.WINDOW_HEIGHT = GRID.HEIGHT * GRID.CELL_SIZE + UI.STATUS_PANEL_HEIGHT
    
    # Update scenario configuration
    if args.survivors is not None:
        if args.survivors < 1 or args.survivors > 50:
            print("ERROR: Survivors must be between 1 and 50")
            sys.exit(1)
        SIMULATION.NUM_SURVIVORS = args.survivors
    
    if args.hazard_coverage is not None:
        if args.hazard_coverage < 0 or args.hazard_coverage > 50:
            print("ERROR: Hazard coverage must be between 0 and 50 percent")
            sys.exit(1)
        # Convert percentage to initial hazard counts
        total_cells = GRID.WIDTH * GRID.HEIGHT
        hazard_cells = int(total_cells * args.hazard_coverage / 100)
        SIMULATION.NUM_INITIAL_FIRES = max(1, hazard_cells // 3)
        SIMULATION.NUM_INITIAL_FLOODS = max(1, hazard_cells // 3)
        SIMULATION.NUM_INITIAL_DEBRIS = max(1, hazard_cells // 3)
    
    # Update simulation parameters
    SIMULATION.RANDOM_SEED = args.seed
    SIMULATION.MAX_TIMESTEPS = args.max_timesteps
    
    # Update log level
    from src.utils.config import LOG
    LOG.LOG_LEVEL_DETAIL = args.log_level
    
    # Display configuration
    print("="*80)
    print("🚁 AI DISASTER RESCUE SIMULATOR - Advanced Multi-Agent System")
    print("="*80)
    print(f"\n📊 Configuration:")
    print(f"   Grid Size: {GRID.WIDTH}x{GRID.HEIGHT} ({GRID.WIDTH * GRID.HEIGHT:,} cells)")
    print(f"   Survivors: {SIMULATION.NUM_SURVIVORS}")
    print(f"   Initial Hazards: {SIMULATION.NUM_INITIAL_FIRES} fires, "
          f"{SIMULATION.NUM_INITIAL_FLOODS} floods, {SIMULATION.NUM_INITIAL_DEBRIS} debris")
    hazard_pct = ((SIMULATION.NUM_INITIAL_FIRES + SIMULATION.NUM_INITIAL_FLOODS + 
                   SIMULATION.NUM_INITIAL_DEBRIS) / (GRID.WIDTH * GRID.HEIGHT)) * 100
    print(f"   Hazard Coverage: {hazard_pct:.1f}%")
    print(f"   Max Timesteps: {args.max_timesteps:,}")
    print(f"   Random Seed: {args.seed}")
    print(f"   Benchmark Mode: {'ON' if args.benchmark else 'OFF'}")
    
    print(f"\n🎮 Controls:")
    print(f"   SPACE - Pause/Resume")
    print(f"   R - Reset simulation")
    print(f"   H - Toggle risk overlay")
    print(f"   P - Toggle agent paths")
    print(f"   Q - Quit")
    
    print("="*80)
    print("\n🔄 Initializing simulation...\n")
    
    try:
        # Create and initialize simulator
        simulator = Simulator(seed=args.seed)
        simulator.benchmark_mode = args.benchmark
        simulator.initialize()
        
        print("✅ Simulation ready. Starting...\n")
        
        # Run simulation
        simulator.run()
        
        # Display results
        print("\n" + "="*80)
        print("✅ SIMULATION COMPLETED")
        print("="*80)
        
        if args.benchmark:
            print(f"\n📈 Performance Metrics:")
            print(f"   Survivors Rescued: {simulator.total_survivors_rescued}/{SIMULATION.NUM_SURVIVORS}")
            success_rate = (simulator.total_survivors_rescued / SIMULATION.NUM_SURVIVORS) * 100 if SIMULATION.NUM_SURVIVORS > 0 else 0
            print(f"   Success Rate: {success_rate:.1f}%")
            print(f"   Total Timesteps: {simulator.timestep}")
            print(f"   Cells Explored: {simulator.total_cells_explored}")
            efficiency = simulator.total_cells_explored / simulator.timestep if simulator.timestep > 0 else 0
            print(f"   Exploration Efficiency: {efficiency:.2f} cells/timestep")
            print(f"   Final Hazards: {len(simulator.grid.fire_positions)} fires, "
                  f"{len(simulator.grid.flood_positions)} floods")
        
        print(f"\n📝 Detailed logs: {LOG.LOG_FILE_PATH}")
        print("="*80 + "\n")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Simulation interrupted by user.")
        sys.exit(0)
    
    except Exception as e:
        print(f"\n\n❌ ERROR: Simulation failed")
        print(f"   {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
