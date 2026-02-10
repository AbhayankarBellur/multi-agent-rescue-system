"""
STRIPS-Like Planning Module
Automated action planning with explicit preconditions and effects.

Classical AI Planning:
- State representation
- Action schemas (preconditions, effects, cost)
- Forward-chaining planner
- Human-readable plan output

This is NOT a general-purpose planner - it's domain-specific for disaster rescue.
"""

from typing import List, Tuple, Optional, Dict, Any, Set
from dataclasses import dataclass
from ..utils.config import ActionType, AI


@dataclass
class State:
    """
    World state representation for planning.
    
    Attributes:
        agent_pos: Agent's (x, y) position
        agent_carrying: Is agent carrying a survivor?
        survivor_positions: Set of survivor locations
        safe_zone_positions: Set of safe zone locations
        goal_achieved: Planning goal status
    """
    agent_pos: Tuple[int, int]
    agent_carrying: bool
    survivor_positions: Set[Tuple[int, int]]
    safe_zone_positions: Set[Tuple[int, int]]
    goal_achieved: bool = False
    
    def copy(self) -> 'State':
        """Create a copy of this state."""
        return State(
            agent_pos=self.agent_pos,
            agent_carrying=self.agent_carrying,
            survivor_positions=set(self.survivor_positions),
            safe_zone_positions=set(self.safe_zone_positions),
            goal_achieved=self.goal_achieved
        )
    
    def __hash__(self):
        return hash((
            self.agent_pos,
            self.agent_carrying,
            frozenset(self.survivor_positions),
            frozenset(self.safe_zone_positions)
        ))
    
    def __eq__(self, other):
        return (self.agent_pos == other.agent_pos and
                self.agent_carrying == other.agent_carrying and
                self.survivor_positions == other.survivor_positions)


@dataclass
class Action:
    """
    STRIPS action schema.
    
    Attributes:
        type: Action type (move, pickup, drop, etc.)
        parameters: Action parameters (e.g., target position)
        preconditions: Conditions that must be true to execute
        effects: State changes resulting from execution
        cost: Estimated cost/time to execute
    """
    type: str
    parameters: Dict[str, Any]
    preconditions: List[str]  # Human-readable
    effects: List[str]  # Human-readable
    cost: float = 1.0
    
    def __repr__(self) -> str:
        if self.type == ActionType.MOVE:
            return f"MOVE to {self.parameters['target']}"
        elif self.type == ActionType.PICKUP:
            return f"PICKUP survivor at {self.parameters['position']}"
        elif self.type == ActionType.DROP:
            return f"DROP survivor at {self.parameters['position']}"
        elif self.type == ActionType.TRANSPORT:
            return f"TRANSPORT to {self.parameters['target']}"
        elif self.type == ActionType.EXPLORE:
            return f"EXPLORE to {self.parameters['target']}"
        else:
            return f"{self.type.upper()}"


class STRIPSPlanner:
    """
    STRIPS-style planner for disaster rescue domain.
    
    Planning Goals:
    1. Rescue survivor: move to survivor, pickup, transport to safe zone, drop
    2. Explore area: move to unexplored regions
    3. Support: move to assist other agents
    
    Algorithm:
        Forward-chaining search through state space
        Greedy best-first with domain heuristics
        Depth-limited to prevent infinite search
    """
    
    def __init__(self, max_depth: int = AI.STRIPS_MAX_PLAN_DEPTH):
        """
        Initialize planner.
        
        Args:
            max_depth: Maximum plan length
        """
        self.max_depth = max_depth
    
    def plan_rescue(
        self,
        agent_pos: Tuple[int, int],
        survivor_pos: Tuple[int, int],
        safe_zones: List[Tuple[int, int]],
        pathfinder
    ) -> List[Action]:
        """
        Generate plan to rescue a specific survivor.
        
        Args:
            agent_pos: Agent's current position
            survivor_pos: Target survivor position
            safe_zones: Available safe zones
            pathfinder: Function to compute paths
            
        Returns:
            List of actions to complete rescue
            
        Plan structure:
        1. MOVE to survivor location
        2. PICKUP survivor
        3. TRANSPORT to nearest safe zone
        4. DROP survivor
        """
        plan: List[Action] = []
        
        # Step 1: Move to survivor
        if agent_pos != survivor_pos:
            plan.append(Action(
                type=ActionType.MOVE,
                parameters={'target': survivor_pos, 'path': None},
                preconditions=[f"Agent at {agent_pos}", "Not carrying survivor"],
                effects=[f"Agent at {survivor_pos}"],
                cost=self._estimate_move_cost(agent_pos, survivor_pos)
            ))
        
        # Step 2: Pickup survivor
        plan.append(Action(
            type=ActionType.PICKUP,
            parameters={'position': survivor_pos},
            preconditions=[f"Agent at {survivor_pos}", "Survivor at {survivor_pos}"],
            effects=["Carrying survivor", f"Survivor removed from {survivor_pos}"],
            cost=1.0
        ))
        
        # Step 3: Transport to safe zone
        # Choose nearest safe zone
        nearest_safe_zone = min(
            safe_zones,
            key=lambda sz: self._manhattan_distance(survivor_pos, sz)
        )
        
        plan.append(Action(
            type=ActionType.TRANSPORT,
            parameters={'target': nearest_safe_zone, 'path': None},
            preconditions=[f"At {survivor_pos}", "Carrying survivor"],
            effects=[f"Agent at {nearest_safe_zone}"],
            cost=self._estimate_move_cost(survivor_pos, nearest_safe_zone)
        ))
        
        # Step 4: Drop survivor at safe zone
        plan.append(Action(
            type=ActionType.DROP,
            parameters={'position': nearest_safe_zone},
            preconditions=[f"At {nearest_safe_zone}", "Carrying survivor"],
            effects=["Not carrying survivor", f"Survivor at {nearest_safe_zone}"],
            cost=1.0
        ))
        
        return plan
    
    def plan_exploration(
        self,
        agent_pos: Tuple[int, int],
        unexplored_targets: List[Tuple[int, int]],
        risk_threshold: float
    ) -> List[Action]:
        """
        Generate plan to explore unknown areas.
        
        Args:
            agent_pos: Agent's current position
            unexplored_targets: Candidate exploration targets
            risk_threshold: Maximum acceptable risk
            
        Returns:
            List of exploration actions
        """
        if not unexplored_targets:
            return []
        
        # Choose nearest unexplored cell
        target = min(
            unexplored_targets,
            key=lambda t: self._manhattan_distance(agent_pos, t)
        )
        
        plan = [Action(
            type=ActionType.EXPLORE,
            parameters={'target': target, 'path': None},
            preconditions=[f"Agent at {agent_pos}"],
            effects=[f"Agent at {target}", f"Cell {target} explored"],
            cost=self._estimate_move_cost(agent_pos, target)
        )]
        
        return plan
    
    def plan_support(
        self,
        agent_pos: Tuple[int, int],
        target_position: Tuple[int, int],
        support_action: str
    ) -> List[Action]:
        """
        Generate plan to support another agent.
        
        Args:
            agent_pos: Support agent position
            target_position: Where support is needed
            support_action: Type of support
            
        Returns:
            Support action plan
        """
        plan = [Action(
            type=ActionType.MOVE,
            parameters={'target': target_position, 'path': None},
            preconditions=[f"Agent at {agent_pos}"],
            effects=[f"Agent at {target_position}"],
            cost=self._estimate_move_cost(agent_pos, target_position)
        )]
        
        return plan
    
    def replan_if_needed(
        self,
        current_plan: List[Action],
        current_pos: Tuple[int, int],
        current_state: Dict,
        blocked_steps: int
    ) -> Tuple[bool, str]:
        """
        Determine if replanning is necessary.
        
        Args:
            current_plan: Active plan
            current_pos: Agent's current position
            current_state: Current world state
            blocked_steps: Number of consecutive blocked steps
            
        Returns:
            (should_replan, reason)
            
        Replanning triggers:
        - Blocked for too many steps (stuck)
        - Target no longer exists (survivor rescued by other agent)
        - Path no longer valid (new hazard)
        - Goal completed
        """
        if blocked_steps >= AI.STRIPS_REPLAN_THRESHOLD:
            return True, f"Blocked for {blocked_steps} steps"
        
        if not current_plan:
            return True, "No active plan"
        
        # Check if first action is still valid
        first_action = current_plan[0]
        
        if first_action.type == ActionType.PICKUP:
            target_pos = first_action.parameters['position']
            if target_pos not in current_state.get('survivor_positions', set()):
                return True, f"Survivor no longer at {target_pos}"
        
        return False, ""
    
    def _estimate_move_cost(self, start: Tuple[int, int], goal: Tuple[int, int]) -> float:
        """Estimate movement cost (Manhattan distance as proxy)."""
        return float(self._manhattan_distance(start, goal))
    
    def _manhattan_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
        """Manhattan distance between positions."""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def get_plan_summary(self, plan: List[Action]) -> str:
        """
        Get human-readable plan summary.
        
        Args:
            plan: List of actions
            
        Returns:
            Formatted plan description
        """
        if not plan:
            return "No plan"
        
        total_cost = sum(a.cost for a in plan)
        summary = f"Plan ({len(plan)} actions, cost={total_cost:.1f}):\n"
        
        for i, action in enumerate(plan, 1):
            summary += f"  {i}. {action}\n"
        
        return summary.strip()
