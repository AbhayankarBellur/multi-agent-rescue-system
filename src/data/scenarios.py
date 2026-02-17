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

    def generate_high_risk_scenario(self, grid_size: Tuple[int, int] = (40, 40)) -> dict:
        """
        Generate HIGH-RISK scenario to force mode switching.
        
        Parameters designed to trigger auction and coalition modes:
        - 40×40 grid (larger area)
        - 15 survivors (high workload)
        - 35% hazard density (high risk)
        - Aggressive hazard spreading
        
        Args:
            grid_size: Grid dimensions (width, height)
            
        Returns:
            High-risk scenario dictionary
        """
        width, height = grid_size
        total_cells = width * height
        hazard_density = 0.35  # 35% coverage
        
        # Calculate hazard counts
        total_hazards = int(total_cells * hazard_density)
        num_fires = total_hazards // 3
        num_floods = total_hazards // 3
        num_debris = total_hazards - num_fires - num_floods
        
        # Safe zones
        safe_zones = [
            (3, 3),
            (width - 4, 3),
            (3, height - 4),
            (width - 4, height - 4)
        ]
        
        # Survivors - distributed across grid
        survivors = []
        for i in range(15):
            x = random.randint(8, width - 9)
            y = random.randint(8, height - 9)
            pos = (x, y)
            if pos not in safe_zones and pos not in survivors:
                survivors.append(pos)
        
        # Fires - clustered for high risk
        fires = []
        for i in range(num_fires):
            x = random.randint(5, width - 6)
            y = random.randint(5, height - 6)
            pos = (x, y)
            if pos not in safe_zones and pos not in survivors:
                fires.append(pos)
        
        # Floods
        floods = []
        for i in range(num_floods):
            x = random.randint(5, width - 6)
            y = random.randint(5, height - 6)
            pos = (x, y)
            if pos not in safe_zones and pos not in survivors and pos not in fires:
                floods.append(pos)
        
        # Debris
        debris = []
        for i in range(num_debris):
            x = random.randint(5, width - 6)
            y = random.randint(5, height - 6)
            pos = (x, y)
            if pos not in safe_zones and pos not in survivors:
                debris.append(pos)
        
        # Agent positions
        agent_positions = {
            'explorer': (5, 3),
            'rescue': (3, 5),
            'support': (4, 4)
        }
        
        return {
            'width': width,
            'height': height,
            'safe_zones': safe_zones,
            'survivors': survivors,
            'fires': fires,
            'floods': floods,
            'debris': debris,
            'agent_positions': agent_positions,
            'seed': self.seed,
            'difficulty': 'high',
            'hazard_density': hazard_density
        }
    
    def generate_extreme_scenario(self, grid_size: Tuple[int, int] = (60, 60)) -> dict:
        """
        Generate EXTREME scenario for stress testing.
        
        Parameters:
        - 60×60 grid
        - 25 survivors
        - 40% hazard density
        - Maximum challenge
        
        Args:
            grid_size: Grid dimensions
            
        Returns:
            Extreme scenario dictionary
        """
        width, height = grid_size
        total_cells = width * height
        hazard_density = 0.40  # 40% coverage
        
        total_hazards = int(total_cells * hazard_density)
        num_fires = total_hazards // 3
        num_floods = total_hazards // 3
        num_debris = total_hazards - num_fires - num_floods
        
        # Safe zones
        safe_zones = [
            (3, 3),
            (width - 4, 3),
            (3, height - 4),
            (width - 4, height - 4),
            (width // 2, 3),  # Extra safe zone
            (width // 2, height - 4)
        ]
        
        # Survivors
        survivors = []
        for i in range(25):
            x = random.randint(10, width - 11)
            y = random.randint(10, height - 11)
            pos = (x, y)
            if pos not in safe_zones and pos not in survivors:
                survivors.append(pos)
        
        # Hazards - dense placement
        fires = []
        for i in range(num_fires):
            x = random.randint(5, width - 6)
            y = random.randint(5, height - 6)
            pos = (x, y)
            if pos not in safe_zones and pos not in survivors:
                fires.append(pos)
        
        floods = []
        for i in range(num_floods):
            x = random.randint(5, width - 6)
            y = random.randint(5, height - 6)
            pos = (x, y)
            if pos not in safe_zones and pos not in survivors and pos not in fires:
                floods.append(pos)
        
        debris = []
        for i in range(num_debris):
            x = random.randint(5, width - 6)
            y = random.randint(5, height - 6)
            pos = (x, y)
            if pos not in safe_zones and pos not in survivors:
                debris.append(pos)
        
        agent_positions = {
            'explorer': (5, 3),
            'rescue': (3, 5),
            'support': (4, 4)
        }
        
        return {
            'width': width,
            'height': height,
            'safe_zones': safe_zones,
            'survivors': survivors,
            'fires': fires,
            'floods': floods,
            'debris': debris,
            'agent_positions': agent_positions,
            'seed': self.seed,
            'difficulty': 'extreme',
            'hazard_density': hazard_density
        }
    
    def generate_scenario_by_difficulty(self, difficulty: str = 'medium') -> dict:
        """
        Generate scenario based on difficulty level.
        
        Args:
            difficulty: One of 'easy', 'medium', 'hard', 'extreme', 'nightmare'
            
        Returns:
            Scenario dictionary
        """
        if difficulty == 'easy':
            # Small grid, few survivors, low hazards
            return self._generate_custom_scenario(
                grid_size=(20, 20),
                num_survivors=5,
                hazard_density=0.10
            )
        
        elif difficulty == 'medium':
            # Standard scenario
            return self.generate_standard_scenario()
        
        elif difficulty == 'hard':
            # High-risk scenario
            return self.generate_high_risk_scenario()
        
        elif difficulty == 'extreme':
            # Extreme scenario
            return self.generate_extreme_scenario()
        
        elif difficulty == 'nightmare':
            # Maximum difficulty
            return self._generate_custom_scenario(
                grid_size=(80, 80),
                num_survivors=40,
                hazard_density=0.45
            )
        
        else:
            # Default to medium
            return self.generate_standard_scenario()
    
    def _generate_custom_scenario(self, grid_size: Tuple[int, int],
                                  num_survivors: int,
                                  hazard_density: float) -> dict:
        """
        Generate custom scenario with specific parameters.
        
        Args:
            grid_size: Grid dimensions
            num_survivors: Number of survivors
            hazard_density: Hazard coverage (0.0-0.5)
            
        Returns:
            Custom scenario dictionary
        """
        width, height = grid_size
        total_cells = width * height
        total_hazards = int(total_cells * hazard_density)
        
        num_fires = total_hazards // 3
        num_floods = total_hazards // 3
        num_debris = total_hazards - num_fires - num_floods
        
        # Safe zones
        margin = max(3, width // 20)
        safe_zones = [
            (margin, margin),
            (width - margin - 1, margin),
            (margin, height - margin - 1),
            (width - margin - 1, height - margin - 1)
        ]
        
        # Survivors
        survivors = []
        for i in range(num_survivors):
            x = random.randint(margin + 2, width - margin - 3)
            y = random.randint(margin + 2, height - margin - 3)
            pos = (x, y)
            if pos not in safe_zones and pos not in survivors:
                survivors.append(pos)
        
        # Hazards
        fires = []
        for i in range(num_fires):
            x = random.randint(margin, width - margin - 1)
            y = random.randint(margin, height - margin - 1)
            pos = (x, y)
            if pos not in safe_zones and pos not in survivors:
                fires.append(pos)
        
        floods = []
        for i in range(num_floods):
            x = random.randint(margin, width - margin - 1)
            y = random.randint(margin, height - margin - 1)
            pos = (x, y)
            if pos not in safe_zones and pos not in survivors and pos not in fires:
                floods.append(pos)
        
        debris = []
        for i in range(num_debris):
            x = random.randint(margin, width - margin - 1)
            y = random.randint(margin, height - margin - 1)
            pos = (x, y)
            if pos not in safe_zones and pos not in survivors:
                debris.append(pos)
        
        agent_positions = {
            'explorer': (margin + 1, margin),
            'rescue': (margin, margin + 1),
            'support': (margin + 1, margin + 1)
        }
        
        return {
            'width': width,
            'height': height,
            'safe_zones': safe_zones,
            'survivors': survivors,
            'fires': fires,
            'floods': floods,
            'debris': debris,
            'agent_positions': agent_positions,
            'seed': self.seed,
            'difficulty': 'custom',
            'hazard_density': hazard_density
        }
