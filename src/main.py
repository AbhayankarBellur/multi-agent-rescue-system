"""
AI-Driven Multi-Agent Disaster Rescue Simulator
Main Entry Point

A research-grade simulation demonstrating:
- A* pathfinding
- Bayesian risk estimation
- CSP task allocation
- STRIPS planning
- Multi-agent coordination

Academic rigor with full explainability.
"""

import sys
import argparse
from src.core.simulator import Simulator
from src.utils.config import SIMULATION


def main():
    """
    Main entry point for simulation.
    
    Parses command-line arguments and launches simulator.
    """
    parser = argparse.ArgumentParser(
        description="AI Disaster Rescue Simulator - Research-Grade Multi-Agent System"
    )
    
    parser.add_argument(
        '--seed',
        type=int,
        default=SIMULATION.RANDOM_SEED,
        help=f'Random seed for deterministic runs (default: {SIMULATION.RANDOM_SEED})'
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
        '--protocol',
        choices=['centralized', 'auction', 'coalition', 'hybrid'],
        default='hybrid',
        help='Coordination protocol: centralized (CSP greedy), auction (CNP), coalition (teams), hybrid (auto-select) (default: hybrid)'
    )
    
    parser.add_argument(
        '--disable-spawning',
        action='store_true',
        help='Disable dynamic agent spawning (enabled by default)'
    )
    
    args = parser.parse_args()
    
    # Update configuration
    SIMULATION.RANDOM_SEED = args.seed
    SIMULATION.MAX_TIMESTEPS = args.max_timesteps
    
    # Update log level
    from src.utils.config import LOG
    LOG.LOG_LEVEL_DETAIL = args.log_level
    
    print("="*80)
    print("AI DISASTER RESCUE SIMULATOR")
    print("A Research-Grade Multi-Agent System")
    print("="*80)
    print(f"Configuration:")
    print(f"  Random Seed: {args.seed}")
    print(f"  Max Timesteps: {args.max_timesteps}")
    print(f"  Log Level: {args.log_level}")
    print(f"  Coordination Protocol: {args.protocol.upper()}")
    print(f"  Dynamic Spawning: {'DISABLED' if args.disable_spawning else 'ENABLED'}")
    print("="*80)
    print("\nControls:")
    print("  SPACE - Pause/Resume")
    print("  R - Reset simulation")
    print("  H - Toggle risk overlay")
    print("  P - Toggle agent paths")
    print("  Q - Quit")
    print("="*80)
    print("\nInitializing...\n")
    
    try:
        # Create and initialize simulator
        simulator = Simulator(
            seed=args.seed,
            coordination_mode=args.protocol,
            enable_spawning=not args.disable_spawning
        )
        simulator.initialize()
        
        print("Simulation ready. Starting...\n")
        
        # Run simulation
        simulator.run()
        
        print("\nSimulation completed successfully.")
        print(f"See '{LOG.LOG_FILE_PATH}' for detailed logs.\n")
        
    except KeyboardInterrupt:
        print("\n\nSimulation interrupted by user.")
        sys.exit(0)
    
    except Exception as e:
        print(f"\n\nERROR: Simulation failed with exception:")
        print(f"  {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
