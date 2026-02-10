"""
Support Agent Implementation
Coordinates multi-agent efforts and reduces conflicts.

Strategy:
- Monitor other agents via shared environment
- Use CSP allocator to prevent task conflicts
- Navigate with highest risk tolerance to assist
- Dynamically reallocate tasks when needed
"""

from typing import Tuple, Optional, List, Any, Dict
from .base_agent import BaseAgent
from ..utils.config import AgentType, ActionType, AGENT
from ..ai.search import astar_search, compute_terrain_cost, compute_risk_cost
from ..ai.planner import STRIPSPlanner, Action


class SupportAgent(BaseAgent):
    """
    Support agent using CSP-based coordination.
    
    Goal: Optimize overall rescue efficiency
    
    Functions:
    1. Monitor agent positions and task status
    2. Identify bottlenecks or conflicts
    3. Provide pathfinding assistance
    4. Handle edge cases (stuck agents, blocked paths)
    """
    
    def __init__(self, agent_id: str, start_position: Tuple[int, int]):
        """Initialize support agent."""
        super().__init__(agent_id, AgentType.SUPPORT, start_position)
        self.planner = STRIPSPlanner()
        self.risk_threshold = AGENT.RISK_THRESHOLD_SUPPORT
        self.coordination_weight = AGENT.SUPPORT_COORDINATION_WEIGHT
        
        # Support-specific state
        self.monitored_agents: Dict[str, Dict] = {}
        self.support_targets: List[Tuple[int, int]] = []
        self.suppression_cooldown = 0  # Timesteps until can suppress again
        self.suppression_active_until = {}  # position -> timestep when suppression expires
    
    def decide_action(self, grid, risk_model, **kwargs) -> Optional[Action]:
        """
        Decide next support action.
        
        Args:
            grid: Environment grid
            risk_model: Bayesian risk model
            **kwargs: May contain 'agents' for monitoring
            
        Returns:
            Action to execute
            
        Decision logic:
        1. Monitor all agents and their tasks
        2. Identify support opportunities:
           - Clear path blockages
           - Assist high-risk operations
           - Rebalance workload
        3. Execute support action
        """
        # EMERGENCY: Check if trapped in impassable cell
        current_cell = grid.get_cell(self.position[0], self.position[1])
        if current_cell and not current_cell.is_passable():
            # Agent is trapped! Find nearest passable cell and escape
            self.logger.log_replanning(
                self.agent_id, "TRAPPED in impassable cell",
                str(self.current_plan[:1]) if self.current_plan else "None",
                "Escaping to nearest safe cell"
            )
            neighbors = grid.get_neighbors(self.position[0], self.position[1], diagonal=True)
            passable_neighbors = [
                n for n in neighbors 
                if grid.get_cell(n[0], n[1]) and grid.get_cell(n[0], n[1]).is_passable()
            ]
            
            if passable_neighbors:
                # Move to nearest passable neighbor
                escape_target = passable_neighbors[0]
                return Action(
                    type=ActionType.MOVE,
                    parameters={'target': escape_target},
                    preconditions=[],
                    effects=[],
                    cost=1.0
                )
            else:
                # Try to move to ANY neighbor (even hazardous) as last resort
                all_neighbors = grid.get_neighbors(self.position[0], self.position[1], diagonal=True)
                if all_neighbors:
                    # Prefer least hazardous neighbor
                    best_neighbor = None
                    best_risk = float('inf')
                    for nx, ny in all_neighbors:
                        cell = grid.get_cell(nx, ny)
                        if cell:
                            risk = risk_model.get_risk((nx, ny), "combined")
                            if risk < best_risk:
                                best_risk = risk
                                best_neighbor = (nx, ny)
                    
                    if best_neighbor:
                        return Action(
                            type=ActionType.MOVE,
                            parameters={'target': best_neighbor},
                            preconditions=[],
                            effects=[],
                            cost=1.0
                        )
                
                # Absolutely no escape - wait
                return Action(
                    type=ActionType.WAIT,
                    parameters={},
                    preconditions=[],
                    effects=[],
                    cost=1.0
                )
        
        # Update monitored agents
        other_agents = kwargs.get('agents', {})
        self.monitored_agents = {
            aid: info for aid, info in other_agents.items()
            if aid != self.agent_id
        }
        
        # Update suppression cooldown
        self.update_suppression_cooldown()
        
        # Priority 1: Check if hazard suppression is needed and available
        timestep = kwargs.get('timestep', 0)
        suppression_action = self.suppress_local_hazards(grid, risk_model, timestep)
        if suppression_action:
            return suppression_action
        
        # Check if need to replan
        current_state = {'survivor_positions': set(grid.survivor_positions)}
        should_replan, reason = self.planner.replan_if_needed(
            self.current_plan, self.position, current_state, self.blocked_steps
        )
        
        if should_replan or not self.current_plan:
            if reason:
                self.logger.log_replanning(
                    self.agent_id, reason,
                    str(self.current_plan[:1]) if self.current_plan else "None",
                    "Generating new support plan"
                )
            
            # Generate new support plan
            self.current_plan = self._plan_support(grid, risk_model)
        
        # Execute next action
        if self.current_plan:
            action = self.current_plan.pop(0)
            
            # Compute path if needed
            if action.type == ActionType.MOVE:
                target = action.parameters.get('target')
                if target and action.parameters.get('path') is None:
                    path, cost = self._compute_path(self.position, target, grid, risk_model)
                    action.parameters['path'] = path
                    
                    if path:
                        self.logger.log_pathfinding(
                            self.agent_id, self.position, target, path, cost, "A*"
                        )
                    
                    if path and len(path) > 1:
                        action.parameters['target'] = path[1]
                        self.current_path = path
            
            return action
        
        # No plan - patrol or wait
        return self._generate_patrol_action(grid, risk_model)
    
    def _plan_support(self, grid, risk_model) -> List[Action]:
        """
        Generate support plan.
        
        Args:
            grid: Environment grid
            risk_model: Risk model
            
        Returns:
            List of support actions
            
        Support strategies:
        1. Move to high-risk areas to scout
        2. Position near rescue agents for assistance
        3. Explore alternative paths
        """
        # Strategy 1: Support rescue agents
        support_target = self._identify_support_target(grid, risk_model)
        
        if support_target:
            plan = self.planner.plan_support(
                self.position,
                support_target,
                "positioning"
            )
            
            if plan:
                self.logger.log_planning(
                    self.agent_id,
                    f"Support positioning at {support_target}",
                    [str(a) for a in plan],
                    sum(a.cost for a in plan)
                )
            
            return plan
        
        # Strategy 2: Scout high-risk areas
        risky_areas = self._find_risky_areas(grid, risk_model)
        
        if risky_areas:
            target = risky_areas[0]
            plan = [Action(
                type=ActionType.MOVE,
                parameters={'target': target, 'path': None},
                preconditions=[f"At {self.position}"],
                effects=[f"At {target}", "Area scouted"],
                cost=1.0
            )]
            
            return plan
        
        return []
    
    def _identify_support_target(self, grid, risk_model) -> Optional[Tuple[int, int]]:
        """
        Identify where support is most needed.
        
        Args:
            grid: Environment grid
            risk_model: Risk model
            
        Returns:
            Target position for support
            
        Logic:
        - Find rescue agents
        - Position near them to assist if they get stuck
        - Prioritize agents in high-risk areas
        """
        rescue_agents = [
            info for aid, info in self.monitored_agents.items()
            if info.get('type') == AgentType.RESCUE
        ]
        
        if not rescue_agents:
            return None
        
        best_target = None
        best_priority = -1
        
        for agent_info in rescue_agents:
            agent_pos = agent_info.get('position')
            if not agent_pos:
                continue
            
            # Get risk at agent position
            risk = risk_model.get_risk(agent_pos, "combined")
            
            # Priority: higher risk = higher priority for support
            distance = abs(agent_pos[0] - self.position[0]) + abs(agent_pos[1] - self.position[1])
            
            # Don't go too close (give rescue agent space)
            if distance < 3:
                continue
            
            priority = risk * self.coordination_weight - distance * (1.0 - self.coordination_weight)
            
            if priority > best_priority:
                best_priority = priority
                # Position nearby, not exactly on agent
                best_target = self._find_nearby_position(agent_pos, grid)
        
        return best_target
    
    def _find_nearby_position(self, target: Tuple[int, int], grid) -> Tuple[int, int]:
        """
        Find a nearby passable position.
        
        Args:
            target: Target position
            grid: Environment grid
            
        Returns:
            Nearby position
        """
        neighbors = grid.get_neighbors(target[0], target[1], diagonal=True)
        
        for nx, ny in neighbors:
            cell = grid.get_cell(nx, ny)
            if cell and cell.is_passable():
                return (nx, ny)
        
        return target  # Fallback
    
    def _find_risky_areas(self, grid, risk_model) -> List[Tuple[int, int]]:
        """
        Identify high-risk areas that need scouting.
        
        Args:
            grid: Environment grid
            risk_model: Risk model
            
        Returns:
            List of risky positions
        """
        risky = []
        
        # Sample grid for high-risk cells
        for x in range(0, grid.width, 5):  # Sample every 5 cells
            for y in range(0, grid.height, 5):
                cell = grid.get_cell(x, y)
                if not cell or not cell.is_passable():
                    continue
                
                risk = risk_model.get_risk((x, y), "combined")
                
                # Moderate risk (not too dangerous, but needs attention)
                if 0.3 < risk < self.risk_threshold:
                    risky.append((x, y))
        
        # Sort by distance
        risky.sort(key=lambda pos: abs(pos[0] - self.position[0]) + abs(pos[1] - self.position[1]))
        
        return risky[:5]  # Top 5
    
    def can_suppress_hazard(self, timestep: int) -> bool:
        """
        Check if support agent can suppress hazards.
        
        Args:
            timestep: Current timestep
            
        Returns:
            True if suppression is available
        """
        return self.suppression_cooldown <= 0
    
    def suppress_local_hazards(self, grid, risk_model, timestep: int) -> Optional[Action]:
        """
        Suppress hazards in local area to assist rescue operations.
        
        Effect: Reduces risk by 0.3 in 3x3 area around agent for 5 timesteps.
        Cooldown: 10 timesteps between uses.
        
        Args:
            grid: Environment grid
            risk_model: Risk model
            timestep: Current timestep
            
        Returns:
            SUPPRESS_HAZARD action if conditions met, else None
        """
        # Check cooldown
        if self.suppression_cooldown > 0:
            return None
        
        # Check if there are nearby rescue agents or survivors that need help
        x, y = self.position
        neighbors = grid.get_neighbors(x, y, diagonal=True)
        
        # Check for high-risk area
        local_risk = risk_model.get_risk(self.position, "combined")
        
        # Only suppress if risk is significant
        if local_risk < 0.4:
            return None
        
        # Check for nearby rescue agents in coalition
        needs_suppression = False
        for agent_id, agent_info in self.monitored_agents.items():
            if agent_info.get('type') == AgentType.RESCUE:
                agent_pos = agent_info.get('position')
                if agent_pos:
                    dist = abs(agent_pos[0] - x) + abs(agent_pos[1] - y)
                    if dist <= 3:  # Within suppression range
                        needs_suppression = True
                        break
        
        # Also check for nearby survivors
        if not needs_suppression:
            for sx, sy in neighbors:
                cell = grid.get_cell(sx, sy)
                if cell and cell.has_survivor:
                    needs_suppression = True
                    break
        
        if needs_suppression:
            self.logger.log_action(
                self.agent_id,
                "SUPPRESS_HAZARD",
                f"Suppressing hazards at {self.position} for 5 timesteps (risk: {local_risk:.2f})"
            )
            
            # Mark suppression area and duration
            for nx, ny in [(x, y)] + list(neighbors):
                self.suppression_active_until[(nx, ny)] = timestep + 5
            
            # Set cooldown
            self.suppression_cooldown = 10
            
            return Action(
                type=ActionType.SUPPRESS_HAZARD,
                parameters={
                    'position': self.position,
                    'radius': 1,
                    'duration': 5,
                    'risk_reduction': 0.3
                },
                preconditions=[f"At {self.position}", f"Risk >= 0.4"],
                effects=["Local hazards suppressed", "Risk reduced by 0.3"],
                cost=1.0
            )
        
        return None
    
    def update_suppression_cooldown(self):
        """Reduce suppression cooldown each timestep."""
        if self.suppression_cooldown > 0:
            self.suppression_cooldown -= 1
    
    def get_active_suppression_at(self, position: Tuple[int, int], timestep: int) -> float:
        """
        Get active hazard suppression effect at position.
        
        Args:
            position: Position to check
            timestep: Current timestep
            
        Returns:
            Risk reduction amount (0.0 to 0.3)
        """
        if position in self.suppression_active_until:
            if timestep <= self.suppression_active_until[position]:
                return 0.3
            else:
                # Suppression expired
                del self.suppression_active_until[position]
        return 0.0
    
    def _generate_patrol_action(self, grid, risk_model) -> Action:
        """
        Generate patrol action when no specific support needed.
        
        Args:
            grid: Environment grid
            risk_model: Risk model
            
        Returns:
            Patrol action
        """
        import random
        
        neighbors = grid.get_neighbors(self.position[0], self.position[1], diagonal=True)
        
        valid_targets = []
        for nx, ny in neighbors:
            cell = grid.get_cell(nx, ny)
            if cell and cell.is_passable():
                risk = risk_model.get_risk((nx, ny), "combined")
                if risk < self.risk_threshold:
                    valid_targets.append((nx, ny))
        
        if valid_targets:
            target = random.choice(valid_targets)
            return Action(
                type=ActionType.MOVE,
                parameters={'target': target, 'path': None},
                preconditions=[],
                effects=[],
                cost=1.0
            )
        
        return Action(
            type=ActionType.WAIT,
            parameters={},
            preconditions=[],
            effects=[],
            cost=1.0
        )
    
    def _compute_path(self, start: Tuple[int, int], goal: Tuple[int, int],
                     grid, risk_model) -> Tuple[List[Tuple[int, int]], float]:
        """
        Compute path with highest risk tolerance.
        
        Args:
            start: Start position
            goal: Goal position
            grid: Environment grid
            risk_model: Risk model
            
        Returns:
            (path, cost)
        """
        def is_passable(x, y):
            cell = grid.get_cell(x, y)
            # Support agent - allow traversing hazardous cells
            return cell is not None
        
        def get_neighbors(x, y):
            return grid.get_neighbors(x, y, diagonal=False)
        
        def get_terrain_cost(x, y):
            cell = grid.get_cell(x, y)
            if not cell:
                return float('inf')
            # Support agent tolerates hazards but still prefers safer routes
            cost = compute_terrain_cost(cell)
            if cell.has_fire:
                cost += 50.0  # Lower penalty for support agent
            if cell.has_debris:
                cost += 25.0
            return cost
        
        def get_risk_cost(x, y):
            risk = risk_model.get_risk((x, y), "combined")
            # Support agent more tolerant of risk
            return compute_risk_cost(risk) * 0.3  # Even more tolerant now
        
        return astar_search(
            start, goal, is_passable, get_neighbors,
            get_terrain_cost, get_risk_cost
        )
