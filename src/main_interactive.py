"""
Interactive Main Entry Point with GUI Configuration
Shows a configuration dialog before starting the simulation.
"""

import sys
import argparse
from src.core.simulator import Simulator
from src.utils.config import GRID, SIMULATION, HAZARD, UI
from src.ui.config_dialog import get_user_config


def main():
    """Main entry point with interactive configuration."""
    
    # Check for command-line override
    parser = argparse.ArgumentParser(description='AI Disaster Rescue Simulator - Interactive Mode')
    parser.add_argument('--skip-dialog', action='store_true', 
                       help='Skip configuration dialog, use defaults')
    parser.add_argument('--seed', type=int, default=42,
                       help='Random seed for reproducibility')
    parser.add_argument('--max-timesteps', type=int, default=1000,
                       help='Maximum timesteps to run')
    parser.add_argument('--protocol', choices=['centralized', 'auction', 'coalition', 'hybrid'],
                       default='hybrid', help='Coordination protocol (default: hybrid)')
    parser.add_argument('--disable-spawning', action='store_true',
                       help='Disable dynamic agent spawning')
    
    args = parser.parse_args()
    
    # Show configuration dialog unless skipped
    if not args.skip_dialog:
        print("Opening configuration dialog...")
        config = get_user_config()
        
        if config is None:
            print("Configuration cancelled. Exiting.")
            return
        
        # Apply configuration
        GRID.WIDTH = config['grid_width']
        GRID.HEIGHT = config['grid_height']
        SIMULATION.NUM_SURVIVORS = config['survivors']
        
        # Calculate hazard counts from percentage
        total_cells = GRID.WIDTH * GRID.HEIGHT
        hazard_cells = int(total_cells * config['hazard_coverage'] / 100)
        SIMULATION.NUM_INITIAL_FIRES = max(1, hazard_cells // 3)
        SIMULATION.NUM_INITIAL_FLOODS = max(1, hazard_cells // 3)
        SIMULATION.NUM_INITIAL_DEBRIS = max(1, hazard_cells // 3)
        
        # Update UI window size
        UI.WINDOW_WIDTH = GRID.WIDTH * GRID.CELL_SIZE + UI.LOG_PANEL_WIDTH + 20
        UI.WINDOW_HEIGHT = max(800, GRID.HEIGHT * GRID.CELL_SIZE + 40)
        
        print("\n" + "="*80)
        print("🚁 AI DISASTER RESCUE SIMULATOR - Interactive Configuration")
        print("="*80)
        print(f"\n📊 Your Configuration:")
        print(f"   Grid Size: {GRID.WIDTH}x{GRID.HEIGHT} ({GRID.WIDTH * GRID.HEIGHT} cells)")
        print(f"   Survivors: {SIMULATION.NUM_SURVIVORS}")
        print(f"   Initial Hazards: {SIMULATION.NUM_INITIAL_FIRES} fires, {SIMULATION.NUM_INITIAL_FLOODS} floods, {SIMULATION.NUM_INITIAL_DEBRIS} debris")
        print(f"   Hazard Coverage: {config['hazard_coverage']}%")
        print(f"   Random Seed: {args.seed}")
        print(f"   Max Timesteps: {args.max_timesteps}")
        print(f"   Coordination: {args.protocol.upper()}")
        print(f"   Dynamic Spawning: {'DISABLED' if args.disable_spawning else 'ENABLED'}")
        print("\n🎮 Controls:")
        print("   SPACE - Pause/Resume")
        print("   R - Reset simulation")
        print("   H - Toggle risk overlay")
        print("   P - Toggle agent paths")
        print("   Q - Quit")
        print("="*80)
        print("\n🔄 Starting simulation...\n")
    else:
        print("Using default configuration...")
    
    # Set runtime parameters
    SIMULATION.RANDOM_SEED = args.seed
    SIMULATION.MAX_TIMESTEPS = args.max_timesteps
    
    # Create and run simulator with hybrid coordinator
    simulator = Simulator(
        seed=args.seed,
        coordination_mode=args.protocol,
        enable_spawning=not args.disable_spawning
    )
    simulator.initialize()
    simulator.run()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSimulation interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
