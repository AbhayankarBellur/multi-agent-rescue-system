"""
Scenario Generator and Loader
Creates diverse disaster scenarios with configurable parameters.
Ensures deterministic generation via random seeds.
"""

import random
from typing import List, Tuple, Optional
from ..core.environment import Grid
from ..utils.config import SIMULATION, GRID


class ScenarioGenerator:
    """
    Generates disaster scenarios with controllable parameters.
    
    Scenarios include:
    - Initial hazard placement
    - Survivor distribution
    - Safe zone locations
    - Agent starting positions
    
    Design: Deterministic generation for reproducible experiments
    """
    
    def __init__(self, seed: Optional[int] = None):
        """
        Initialize scenario generator.
        
        Args:
            seed: Random seed for deterministic generation
        """
        self.seed = seed or SIMULATION.RANDOM_SEED
        random.seed(self.seed)
    
    def generate_standard_scenario(self) -> dict:
        """
        Generate standard disaster scenario.
        
        Returns:
            Dictionary with scenario configuration
        """
        width = GRID.WIDTH
        height = GRID.HEIGHT
        
        # Divide grid into regions for structured placement
        center_x, center_y = width // 2, height // 2
        
        # Place safe zones at corners
        safe_zones = self._generate_safe_zones(width, height)
        
        # Place survivors in middle regions
        survivors = self._generate_survivors(width, height, safe_zones)
        
        # Place initial hazards
        fires = self._generate_fires(width, height, safe_zones, survivors)
        floods = self._generate_floods(width, height, safe_zones, survivors, fires)
        debris = self._generate_debris(width, height, safe_zones, survivors)
        
        # Agent starting positions (near safe zones)
        agent_positions = self._generate_agent_positions(width, height, safe_zones)
        
        return {
            'width': width,
            'height': height,
            'safe_zones': safe_zones,
            'survivors': survivors,
            'fires': fires,
            'floods': floods,
            'debris': debris,
            'agent_positions': agent_positions,
            'seed': self.seed
        }
    
    def _generate_safe_zones(self, width: int, height: int) -> List[Tuple[int, int]]:
        """
        Generate safe zone positions.
        
        Args:
            width: Grid width
            height: Grid height
            
        Returns:
            List of safe zone positions
            
        Strategy: Place at grid edges for maximum separation
        """
        safe_zones = []
        margin = 3
        
        # Place in corners or edges
        positions = [
            (margin, margin),  # Top-left
            (width - margin - 1, margin),  # Top-right
            (margin, height - margin - 1),  # Bottom-left
            (width - margin - 1, height - margin - 1),  # Bottom-right
        ]
        
        # Select subset
        num_zones = min(SIMULATION.NUM_SAFE_ZONES, len(positions))
        safe_zones = random.sample(positions, num_zones)
        
        return safe_zones
    
    def _generate_survivors(self, width: int, height: int, 
                           safe_zones: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """
        Generate survivor positions.
        
        Args:
            width, height: Grid dimensions
            safe_zones: Safe zone positions to avoid
            
        Returns:
            List of survivor positions
        """
        survivors = []
        attempts = 0
        max_attempts = 1000
        
        while len(survivors) < SIMULATION.NUM_SURVIVORS and attempts < max_attempts:
            x = random.randint(5, width - 6)
            y = random.randint(5, height - 6)
            pos = (x, y)
            
            # Don't place on safe zones or existing survivors
            if pos not in safe_zones and pos not in survivors:
                # Check not too close to safe zones
                min_dist_to_safe = min(
                    abs(x - sx) + abs(y - sy) for sx, sy in safe_zones
                )
                
                if min_dist_to_safe > 5:
                    survivors.append(pos)
            
            attempts += 1
        
        return survivors
    
    def _generate_fires(self, width: int, height: int,
                       safe_zones: List[Tuple[int, int]],
                       survivors: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """Generate initial fire positions."""
        fires = []
        attempts = 0
        max_attempts = 1000
        
        while len(fires) < SIMULATION.NUM_INITIAL_FIRES and attempts < max_attempts:
            x = random.randint(1, width - 2)
            y = random.randint(1, height - 2)
            pos = (x, y)
            
            # Don't place on safe zones or survivors
            if pos not in safe_zones and pos not in survivors:
                fires.append(pos)
            
            attempts += 1
        
        return fires
    
    def _generate_floods(self, width: int, height: int,
                        safe_zones: List[Tuple[int, int]],
                        survivors: List[Tuple[int, int]],
                        fires: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """Generate initial flood positions."""
        floods = []
        attempts = 0
        max_attempts = 1000
        
        while len(floods) < SIMULATION.NUM_INITIAL_FLOODS and attempts < max_attempts:
            x = random.randint(1, width - 2)
            y = random.randint(1, height - 2)
            pos = (x, y)
            
            # Don't place on safe zones, survivors, or fires
            if (pos not in safe_zones and pos not in survivors and 
                pos not in fires):
                floods.append(pos)
            
            attempts += 1
        
        return floods
    
    def _generate_debris(self, width: int, height: int,
                        safe_zones: List[Tuple[int, int]],
                        survivors: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """Generate initial debris positions."""
        debris = []
        attempts = 0
        max_attempts = 1000
        
        while len(debris) < SIMULATION.NUM_INITIAL_DEBRIS and attempts < max_attempts:
            x = random.randint(1, width - 2)
            y = random.randint(1, height - 2)
            pos = (x, y)
            
            # Don't place on safe zones or survivors
            if pos not in safe_zones and pos not in survivors:
                debris.append(pos)
            
            attempts += 1
        
        return debris
    
    def _generate_agent_positions(self, width: int, height: int,
                                 safe_zones: List[Tuple[int, int]]) -> dict:
        """
        Generate starting positions for agents.
        
        Args:
            width, height: Grid dimensions
            safe_zones: Safe zone positions
            
        Returns:
            Dictionary mapping agent types to positions
        """
        positions = {}
        
        # Start agents near (but not on) safe zones
        if safe_zones:
            base_zone = safe_zones[0]
            
            # Explorer
            positions['explorer'] = (base_zone[0] + 1, base_zone[1])
            
            # Rescue
            positions['rescue'] = (base_zone[0], base_zone[1] + 1)
            
            # Support
            positions['support'] = (base_zone[0] + 1, base_zone[1] + 1)
        else:
            # Fallback if no safe zones
            positions['explorer'] = (5, 5)
            positions['rescue'] = (5, 6)
            positions['support'] = (6, 5)
        
        return positions
    
    def apply_scenario_to_grid(self, grid: Grid, scenario: dict):
        """
        Apply scenario configuration to grid.
        
        Args:
            grid: Grid instance to configure
            scenario: Scenario dictionary from generate_*
        """
        # Add safe zones
        for x, y in scenario['safe_zones']:
            grid.add_safe_zone(x, y)
        
        # Add survivors
        for x, y in scenario['survivors']:
            grid.add_survivor(x, y)
        
        # Add fires
        for x, y in scenario['fires']:
            grid.add_fire(x, y)
        
        # Add floods
        for x, y in scenario['floods']:
            grid.add_flood(x, y)
        
        # Add debris
        for x, y in scenario['debris']:
            grid.add_debris(x, y)
