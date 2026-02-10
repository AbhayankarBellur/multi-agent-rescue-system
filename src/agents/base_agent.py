"""
Base Agent Architecture
Defines the interface and common functionality for all agents.

Agent Lifecycle:
1. Perceive environment
2. Update beliefs (Bayesian)
3. Plan/decide actions
4. Execute action
5. Log decision rationale

This is an abstract base - concrete agents implement specific behaviors.
"""

from typing import Tuple, Optional, Dict, List, Any
from abc import ABC, abstractmethod
from ..utils.logger import get_logger
from ..utils.config import AGENT, AgentType


class BaseAgent(ABC):
    """
    Abstract base class for all disaster rescue agents.
    
    Common functionality:
    - Perception
    - Belief tracking
    - Action execution interface
    - Logging
    
    Subclasses implement:
    - Specific decision logic
    - Planning strategies
    - Role-specific behaviors
    """
    
    def __init__(self, agent_id: str, agent_type: str, start_position: Tuple[int, int]):
        """
        Initialize agent.
        
        Args:
            agent_id: Unique identifier
            agent_type: Agent type (EXPLORER, RESCUE, SUPPORT)
            start_position: Initial (x, y) position
        """
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.position = start_position
        
        # State tracking
        self.carrying_survivor = False
        self.current_plan: List[Any] = []
        self.current_path: List[Tuple[int, int]] = []
        self.target_position: Optional[Tuple[int, int]] = None
        self.assigned_tasks: List[Any] = []
        
        # Performance metrics
        self.steps_taken = 0
        self.blocked_steps = 0
        self.survivors_rescued = 0
        self.cells_explored = 0
        
        # Belief state (what agent knows about world)
        self.known_survivors: List[Tuple[int, int]] = []
        self.known_hazards: Dict[str, List[Tuple[int, int]]] = {
            'fire': [],
            'flood': [],
            'debris': []
        }
        self.explored_cells: set = set()
        
        # Communication system (injected by simulator)
        self.communication_network = None
        self.pending_messages: List[Any] = []
        self.coalition_members: List[int] = []  # IDs of agents in same coalition
        
        self.logger = get_logger()
    
    def perceive(self, grid, risk_model) -> Dict[str, Any]:
        """
        Perceive local environment.
        
        Args:
            grid: Environment grid
            risk_model: Bayesian risk model
            
        Returns:
            Dictionary of observations
            
        Perception includes:
        - Current cell state
        - Neighboring cells
        - Risk estimates
        - Visible survivors/hazards
        """
        x, y = self.position
        cell = grid.get_cell(x, y)
        
        if not cell:
            return {}
        
        # Get neighbors
        neighbors = grid.get_neighbors(x, y, diagonal=True)
        neighbor_cells = [grid.get_cell(nx, ny) for nx, ny in neighbors]
        neighbor_cells = [c for c in neighbor_cells if c is not None]
        
        # Observe current cell
        observations = {
            'position': self.position,
            'cell_passable': cell.is_passable(),
            'cell_hazardous': cell.is_hazardous(),
            'has_fire': cell.has_fire,
            'has_flood': cell.has_flood,
            'has_debris': cell.has_debris,
            'has_survivor': cell.has_survivor,
            'is_safe_zone': cell.is_safe_zone,
        }
        
        # Observe neighbors
        observations['neighbor_fires'] = sum(1 for c in neighbor_cells if c.has_fire)
        observations['neighbor_floods'] = sum(1 for c in neighbor_cells if c.has_flood)
        observations['neighbor_debris'] = sum(1 for c in neighbor_cells if c.has_debris)
        observations['neighbor_survivors'] = sum(1 for c in neighbor_cells if c.has_survivor)
        
        # Get risk estimates
        observations['risk'] = risk_model.get_all_risks(self.position)
        
        # Mark as explored
        self.explored_cells.add(self.position)
        
        return observations
    
    def update_beliefs(self, observations: Dict, grid, risk_model):
        """
        Update agent's beliefs based on observations.
        
        Args:
            observations: Perception output
            grid: Environment grid
            risk_model: Risk model to update
        """
        x, y = self.position
        
        # Update risk beliefs
        neighbors = grid.get_neighbors(x, y, diagonal=True)
        neighbor_cells = [grid.get_cell(nx, ny) for nx, ny in neighbors if grid.get_cell(nx, ny)]
        risk_model.update_from_observation(self.position, grid.get_cell(x, y), neighbor_cells)
        
        # Update known survivors
        for nx, ny in neighbors:
            cell = grid.get_cell(nx, ny)
            if cell and cell.has_survivor:
                pos = (nx, ny)
                if pos not in self.known_survivors:
                    self.known_survivors.append(pos)
        
        # Update known hazards
        for nx, ny in neighbors:
            cell = grid.get_cell(nx, ny)
            if not cell:
                continue
            
            pos = (nx, ny)
            if cell.has_fire and pos not in self.known_hazards['fire']:
                self.known_hazards['fire'].append(pos)
            if cell.has_flood and pos not in self.known_hazards['flood']:
                self.known_hazards['flood'].append(pos)
            if cell.has_debris and pos not in self.known_hazards['debris']:
                self.known_hazards['debris'].append(pos)
    
    def move_to(self, target: Tuple[int, int], grid) -> bool:
        """
        Attempt to move one step toward target.
        
        Args:
            target: Target position
            grid: Environment grid
            
        Returns:
            True if move successful, False if blocked
        """
        if self.position == target:
            return True
        
        # Get target cell
        cell = grid.get_cell(target[0], target[1])
        
        # SPECIAL CASE: If we're in an impassable cell, allow escape to ANY neighbor
        current_cell = grid.get_cell(self.position[0], self.position[1])
        if current_cell and not current_cell.is_passable():
            # Allow moving to any cell (even risky ones) to escape
            if cell:  # Target exists
                self.position = target
                self.steps_taken += 1
                self.blocked_steps = 0
                return True
            else:
                self.blocked_steps += 1
                return False
        
        # NORMAL CASE: Must move to passable cell
        if not cell or not cell.is_passable():
            # Rescue/Support agents can traverse hazardous cells as a last resort
            if cell and self.agent_type in (AgentType.RESCUE, AgentType.SUPPORT):
                self.position = target
                self.steps_taken += 1
                self.blocked_steps = 0
                return True
            self.blocked_steps += 1
            return False
        
        # Move
        self.position = target
        self.steps_taken += 1
        self.blocked_steps = 0
        return True
    
    def execute_action(self, action, grid) -> Tuple[bool, str]:
        """
        Execute a planned action.
        
        Args:
            action: Action object from planner
            grid: Environment grid
            
        Returns:
            (success, result_message)
        """
        from ..utils.config import ActionType
        
        if action.type == ActionType.MOVE:
            target = action.parameters.get('target')
            if target and self.move_to(target, grid):
                return True, f"Moved to {target}"
            else:
                return False, f"Blocked at {self.position}"
        
        elif action.type == ActionType.PICKUP:
            pos = action.parameters.get('position')
            cell = grid.get_cell(pos[0], pos[1])
            if cell and cell.has_survivor and self.position == pos:
                self.carrying_survivor = True
                grid.remove_survivor(pos[0], pos[1])
                return True, f"Picked up survivor at {pos}"
            return False, "Cannot pickup survivor"
        
        elif action.type == ActionType.DROP:
            pos = action.parameters.get('position')
            cell = grid.get_cell(pos[0], pos[1])
            if cell and cell.is_safe_zone and self.carrying_survivor and self.position == pos:
                self.carrying_survivor = False
                self.survivors_rescued += 1
                return True, f"Dropped survivor at safe zone {pos}"
            return False, "Cannot drop survivor"
        
        elif action.type == ActionType.TRANSPORT:
            # Transport is multi-step movement while carrying
            target = action.parameters.get('target')
            if target and self.move_to(target, grid):
                return True, f"Transporting to {target}"
            else:
                return False, f"Blocked during transport"
        
        elif action.type == ActionType.EXPLORE:
            target = action.parameters.get('target')
            if target and self.move_to(target, grid):
                self.cells_explored += 1
                return True, f"Explored {target}"
            else:
                return False, f"Cannot reach exploration target"
        
        elif action.type == ActionType.WAIT:
            # Agent waits (does nothing this turn)
            return True, f"Waiting at {self.position}"
        
        return False, f"Unknown action type: {action.type}"
    
    @abstractmethod
    def decide_action(self, grid, risk_model, **kwargs) -> Optional[Any]:
        """
        Decide next action (implemented by subclasses).
        
        Args:
            grid: Environment grid
            risk_model: Bayesian risk model
            **kwargs: Additional context
            
        Returns:
            Action object or None
        """
        pass
    
    def get_state(self) -> Dict[str, Any]:
        """
        Get complete agent state for logging/display.
        
        Returns:
            Dictionary of agent state
        """
        return {
            'id': self.agent_id,
            'type': self.agent_type,
            'position': self.position,
            'carrying_survivor': self.carrying_survivor,
            'steps_taken': self.steps_taken,
            'blocked_steps': self.blocked_steps,
            'survivors_rescued': self.survivors_rescued,
            'cells_explored': self.cells_explored,
            'current_plan_length': len(self.current_plan),
            'assigned_tasks': len(self.assigned_tasks),
            'coalition_size': len(self.coalition_members),
            'pending_messages': len(self.pending_messages),
        }
    
    def set_communication_network(self, network):
        """
        Inject communication network into agent.
        
        Args:
            network: CommunicationNetwork instance
        """
        self.communication_network = network
    
    def send_message(self, message, agent_positions: Dict[int, Tuple[int, int]]):
        """
        Send a message through the communication network.
        
        Args:
            message: Message object to send
            agent_positions: Current positions of all agents
        """
        if self.communication_network:
            self.communication_network.send_message(message, agent_positions)
    
    def receive_messages(self, msg_type=None):
        """
        Retrieve messages from communication network.
        
        Args:
            msg_type: Optional filter for message type
            
        Returns:
            List of messages
        """
        if self.communication_network:
            messages = self.communication_network.receive_messages(
                int(self.agent_id.split('_')[1]) if '_' in self.agent_id else 0,
                msg_type
            )
            self.pending_messages = messages
            return messages
        return []
    
    def get_numeric_id(self) -> int:
        """
        Extract numeric ID from agent_id string.
        
        Returns:
            Integer agent ID
        """
        if '_' in self.agent_id:
            return int(self.agent_id.split('_')[1])
        return 0
    
    def __repr__(self) -> str:
        return f"{self.agent_type}Agent({self.agent_id}) at {self.position}"
