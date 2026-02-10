"""
Environment Module - Grid State and Hazard Management
Manages the disaster environment including grid state, hazards, survivors, and safe zones.
No agent logic - purely environmental state and dynamics.
"""

import random
from typing import List, Tuple, Set, Optional, Dict
from ..utils.config import GRID, HAZARD, CellType


class Cell:
    """
    Represents a single cell in the disaster grid.
    
    Attributes:
        x: X-coordinate position
        y: Y-coordinate position
        terrain_type: Base terrain classification
        has_fire: Boolean indicating active fire
        has_flood: Boolean indicating flooding
        has_debris: Boolean indicating debris/collapse
        has_survivor: Boolean indicating survivor presence
        is_safe_zone: Boolean indicating safe evacuation zone
        explored: Boolean for tracking exploration state
    """
    
    def __init__(self, x: int, y: int):
        self.x: int = x
        self.y: int = y
        self.terrain_type: int = CellType.NORMAL
        self.has_fire: bool = False
        self.has_flood: bool = False
        self.has_debris: bool = False
        self.has_survivor: bool = False
        self.is_safe_zone: bool = False
        self.explored: bool = False
        
    def is_passable(self) -> bool:
        """
        Determines if an agent can move through this cell.
        
        Returns:
            True if cell can be traversed, False otherwise
        
        Rationale:
            Fire and severe debris block movement entirely.
            Flood is passable but risky (handled by A* cost function).
        """
        return not self.has_fire and not self.has_debris
    
    def is_hazardous(self) -> bool:
        """Check if cell contains any hazard."""
        return self.has_fire or self.has_flood or self.has_debris
    
    def get_state_vector(self) -> Tuple:
        """Return complete state for hashing/comparison."""
        return (
            self.has_fire,
            self.has_flood,
            self.has_debris,
            self.has_survivor,
            self.is_safe_zone,
            self.explored
        )
    
    def __repr__(self) -> str:
        hazards = []
        if self.has_fire:
            hazards.append("FIRE")
        if self.has_flood:
            hazards.append("FLOOD")
        if self.has_debris:
            hazards.append("DEBRIS")
        if self.has_survivor:
            hazards.append("SURVIVOR")
        if self.is_safe_zone:
            hazards.append("SAFE")
        
        return f"Cell({self.x},{self.y})[{','.join(hazards) if hazards else 'CLEAR'}]"


class Grid:
    """
    Main environment grid managing all cells, hazards, and environmental state.
    
    This class is responsible ONLY for:
    - Grid state management
    - Hazard propagation
    - Querying cell states
    
    NOT responsible for:
    - Agent behavior
    - Pathfinding
    - Decision making
    """
    
    def __init__(self, width: int = GRID.WIDTH, height: int = GRID.HEIGHT, seed: Optional[int] = None):
        """
        Initialize disaster environment grid.
        
        Args:
            width: Grid width in cells
            height: Grid height in cells
            seed: Random seed for deterministic behavior
        """
        self.width: int = width
        self.height: int = height
        self.timestep: int = 0
        
        if seed is not None:
            random.seed(seed)
        
        # Initialize grid
        self.cells: List[List[Cell]] = [
            [Cell(x, y) for y in range(height)]
            for x in range(width)
        ]
        
        # Track entities
        self.survivor_positions: Set[Tuple[int, int]] = set()
        self.safe_zone_positions: Set[Tuple[int, int]] = set()
        self.fire_positions: Set[Tuple[int, int]] = set()
        self.flood_positions: Set[Tuple[int, int]] = set()
        self.debris_positions: Set[Tuple[int, int]] = set()
        
    def get_cell(self, x: int, y: int) -> Optional[Cell]:
        """
        Safely retrieve cell at coordinates.
        
        Args:
            x: X-coordinate
            y: Y-coordinate
            
        Returns:
            Cell object if valid coordinates, None otherwise
        """
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.cells[x][y]
        return None
    
    def is_valid_position(self, x: int, y: int) -> bool:
        """Check if coordinates are within grid bounds."""
        return 0 <= x < self.width and 0 <= y < self.height
    
    def get_neighbors(self, x: int, y: int, diagonal: bool = False) -> List[Tuple[int, int]]:
        """
        Get valid neighboring cell coordinates.
        
        Args:
            x: X-coordinate
            y: Y-coordinate
            diagonal: Include diagonal neighbors
            
        Returns:
            List of (x, y) tuples for valid neighbors
        """
        neighbors = []
        
        # Cardinal directions
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        
        # Add diagonal directions if requested
        if diagonal:
            directions.extend([(-1, -1), (-1, 1), (1, -1), (1, 1)])
        
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if self.is_valid_position(nx, ny):
                neighbors.append((nx, ny))
        
        return neighbors
    
    def add_fire(self, x: int, y: int) -> bool:
        """
        Add fire to a cell.
        
        Args:
            x, y: Cell coordinates
            
        Returns:
            True if fire was added successfully
        """
        cell = self.get_cell(x, y)
        if cell and not cell.has_flood:  # Fire cannot exist in flooded cells
            cell.has_fire = True
            self.fire_positions.add((x, y))
            return True
        return False
    
    def add_flood(self, x: int, y: int) -> bool:
        """Add flood to a cell, extinguishing any fire."""
        cell = self.get_cell(x, y)
        if cell:
            if cell.has_fire:
                self.remove_fire(x, y)
            cell.has_flood = True
            self.flood_positions.add((x, y))
            return True
        return False
    
    def add_debris(self, x: int, y: int) -> bool:
        """Add debris/collapse to a cell."""
        cell = self.get_cell(x, y)
        if cell and not cell.has_survivor and not cell.is_safe_zone:
            cell.has_debris = True
            self.debris_positions.add((x, y))
            return True
        return False
    
    def add_survivor(self, x: int, y: int) -> bool:
        """Place a survivor at coordinates."""
        cell = self.get_cell(x, y)
        if cell and not cell.has_debris and not cell.has_fire:
            cell.has_survivor = True
            self.survivor_positions.add((x, y))
            return True
        return False
    
    def add_safe_zone(self, x: int, y: int) -> bool:
        """Designate a cell as a safe evacuation zone."""
        cell = self.get_cell(x, y)
        if cell:
            cell.is_safe_zone = True
            self.safe_zone_positions.add((x, y))
            # Safe zones are always passable
            cell.has_debris = False
            cell.has_fire = False
            cell.has_flood = False
            return True
        return False
    
    def remove_fire(self, x: int, y: int):
        """Remove fire from a cell."""
        cell = self.get_cell(x, y)
        if cell and cell.has_fire:
            cell.has_fire = False
            self.fire_positions.discard((x, y))
    
    def remove_survivor(self, x: int, y: int):
        """Remove survivor from a cell (rescued)."""
        cell = self.get_cell(x, y)
        if cell and cell.has_survivor:
            cell.has_survivor = False
            self.survivor_positions.discard((x, y))
    
    def propagate_hazards(self):
        """
        Execute one timestep of hazard propagation.
        
        DISABLED: Hazards now remain in fixed positions for predictability.
        This allows agents to actually reach survivors without the grid
        becoming 95%+ blocked by spreading fires and debris.
        """
        # Hazard spreading disabled - hazards stay in initial positions
        # This makes the simulation more predictable and allows rescue missions
        # to actually succeed.
        
        self.timestep += 1
    
    def get_grid_state_summary(self) -> Dict:
        """
        Return comprehensive grid state for logging/analysis.
        
        Returns:
            Dictionary with counts of all entity types
        """
        return {
            "timestep": self.timestep,
            "fires": len(self.fire_positions),
            "floods": len(self.flood_positions),
            "debris": len(self.debris_positions),
            "survivors": len(self.survivor_positions),
            "safe_zones": len(self.safe_zone_positions),
        }
    
    def __repr__(self) -> str:
        return f"Grid({self.width}x{self.height}, t={self.timestep})"
