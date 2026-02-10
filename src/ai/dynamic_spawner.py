"""
Dynamic Agent Spawning System

Automatically scales agent count based on problem size and workload.

Formula: required_agents = ceil(sqrt(grid_area) × survivor_count / 50)

Triggers:
- Spawn explorers when <60% explored by timestep 100
- Spawn rescue agents when survivors/rescue_agents > 4
- Maximum 20 total agents to prevent overcrowding

Author: Enhanced Multi-Agent System
Date: February 2026
"""

import math
from typing import List, Dict, Tuple, Optional
from ..agents.explorer import ExplorerAgent
from ..agents.rescue import RescueAgent
from ..agents.support import SupportAgent


class DynamicSpawner:
    """
    Manages dynamic agent spawning based on workload and performance.
    """
    
    def __init__(self, max_agents: int = 20):
        """
        Initialize spawner.
        
        Args:
            max_agents: Maximum total agents allowed
        """
        self.max_agents = max_agents
        self.next_explorer_id = 3  # Start after EXP-1, EXP-2
        self.next_rescue_id = 4    # Start after RES-1, RES-2, RES-3
        self.next_support_id = 2   # Start after SUP-1
        
        # Spawncooldown to prevent spam
        self.last_spawn_timestep = -10
        self.spawn_cooldown = 20  # Min timesteps between spawns
    
    def evaluate_spawning_needs(
        self,
        agents: List,
        grid,
        survivors: List[Tuple[int, int]],
        timestep: int
    ) -> Optional[str]:
        """
        Evaluate if new agents should be spawned.
        
        Args:
            agents: Current agent list
            grid: Environment grid
            survivors: Remaining survivors
            timestep: Current timestep
            
        Returns:
            Agent type to spawn ('EXPLORER', 'RESCUE', 'SUPPORT') or None
        """
        # Check max agents limit
        if len(agents) >= self.max_agents:
            return None
        
        # Check cooldown
        if timestep - self.last_spawn_timestep < self.spawn_cooldown:
            return None
        
        # Check exploration coverage
        total_cells = grid.width * grid.height
        explored_cells = sum(len(a.explored_cells) for a in agents)
        exploration_ratio = explored_cells / total_cells if total_cells > 0 else 0
        
        # Spawn explorer if exploration is lagging
        if timestep > 50 and exploration_ratio < 0.40:
            explorer_count = sum(1 for a in agents if a.agent_type == "EXPLORER")
            if explorer_count < 4:  # Max 4 explorers
                return "EXPLORER"
        
        # Count agent types
        rescue_count = sum(1 for a in agents if a.agent_type == "RESCUE")
        
        # Spawn rescue agent if overloaded
        if len(survivors) > 0:
            survivors_per_rescue = len(survivors) / rescue_count if rescue_count > 0 else float('inf')
            
            # Threshold: more than 4 survivors per rescue agent
            if survivors_per_rescue > 4 and rescue_count < 8:  # Max 8 rescue agents
                return "RESCUE"
        
        # Spawn support if we have many agents but only 1 support
        support_count = sum(1 for a in agents if a.agent_type == "SUPPORT")
        if len(agents) >= 10 and support_count < 2:
            return "SUPPORT"
        
        return None
    
    def spawn_agent(
        self,
        agent_type: str,
        grid,
        comm_network
    ):
        """
        Spawn a new agent.
        
        Args:
            agent_type: Type of agent to spawn
            grid: Environment grid
            comm_network: Communication network to register with
            
        Returns:
            New agent instance or None if spawn failed
        """
        # Find a safe spawn position
        spawn_pos = self._find_safe_spawn_position(grid)
        
        if not spawn_pos:
            return None
        
        # Create agent
        agent = None
        
        if agent_type == "EXPLORER":
            agent_id = f"EXP-{self.next_explorer_id}"
            agent = ExplorerAgent(agent_id, spawn_pos)
            self.next_explorer_id += 1
        
        elif agent_type == "RESCUE":
            agent_id = f"RES-{self.next_rescue_id}"
            agent = RescueAgent(agent_id, spawn_pos)
            self.next_rescue_id += 1
        
        elif agent_type == "SUPPORT":
            agent_id = f"SUP-{self.next_support_id}"
            agent = SupportAgent(agent_id, spawn_pos)
            self.next_support_id += 1
        
        # Set up communication
        if agent and comm_network:
            agent.set_communication_network(comm_network)
            comm_network.register_agent(agent.get_numeric_id())
        
        self.last_spawn_timestep = grid.timestep
        
        return agent
    
    def _find_safe_spawn_position(self, grid) -> Optional[Tuple[int, int]]:
        """
        Find a safe position to spawn an agent.
        
        Criteria:
        - Passable cell
        - Not in hazard
        - Preferably near safe zone
        
        Args:
            grid: Environment grid
            
        Returns:
            (x, y) position or None if no safe position found
        """
        # Try near safe zones first
        for safe_x, safe_y in grid.safe_zone_positions:
            neighbors = grid.get_neighbors(safe_x, safe_y, diagonal=True)
            
            for nx, ny in neighbors:
                cell = grid.get_cell(nx, ny)
                if cell and cell.is_passable() and not cell.is_hazardous():
                    return (nx, ny)
        
        # Fallback: try random safe positions
        import random
        for _ in range(50):  # 50 attempts
            x = random.randint(0, grid.width - 1)
            y = random.randint(0, grid.height - 1)
            cell = grid.get_cell(x, y)
            
            if cell and cell.is_passable() and not cell.is_hazardous():
                return (x, y)
        
        return None
    
    def get_spawn_stats(self) -> Dict[str, int]:
        """
        Get spawning statistics.
        
        Returns:
            Dictionary with spawn counts by type
        """
        return {
            'explorers_spawned': self.next_explorer_id - 3,
            'rescue_spawned': self.next_rescue_id - 4,
            'support_spawned': self.next_support_id - 2,
            'total_spawned': (self.next_explorer_id - 3) + (self.next_rescue_id - 4) + (self.next_support_id - 2)
        }
