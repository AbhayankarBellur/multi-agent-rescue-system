"""
Explorer Agent Implementation
Responsible for discovering unknown areas and updating the shared risk model.

Strategy:
- BFS/DFS exploration of unexplored regions
- Bayesian belief updates for risk assessment
- Avoid high-risk areas while exploring
- Feed observations into shared risk model
"""

from typing import Tuple, Optional, List, Any, Dict
from .base_agent import BaseAgent
from ..utils.config import AgentType, ActionType, AGENT
from ..ai.search import astar_search, compute_terrain_cost, compute_risk_cost
from ..ai.planner import STRIPSPlanner, Action
import random


class ExplorerAgent(BaseAgent):
    """
    Explorer agent using BFS/DFS exploration and Bayesian risk updating.
    
    Goal: Maximize explored area while maintaining safety
    
    Algorithm:
    1. Identify unexplored frontier cells
    2. Select exploration target (nearest, lowest risk)
    3. Plan path using A*
    4. Execute movement
    5. Update risk beliefs from observations
    """
    
    def __init__(self, agent_id: str, start_position: Tuple[int, int]):
        """Initialize explorer agent."""
        super().__init__(agent_id, AgentType.EXPLORER, start_position)
        self.planner = STRIPSPlanner()
        self.exploration_frontier: List[Tuple[int, int]] = []
        self.risk_threshold = AGENT.RISK_THRESHOLD_EXPLORER
        self.curiosity_weight = AGENT.EXPLORER_CURIOSITY_WEIGHT
    
    def decide_action(self, grid, risk_model, **kwargs) -> Optional[Any]:
        """
        Decide next exploration action.
        
        Args:
            grid: Environment grid
            risk_model: Bayesian risk model
            
        Returns:
            Action to execute
            
        Decision logic:
        1. If current plan exists and valid, continue executing
        2. If blocked too long or no plan, replan
        3. Identify exploration targets (unexplored frontiers)
        4. Select best target (balance distance and risk)
        5. Generate exploration plan
        """
        from ..ai.planner import Action
        
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
        
        # Check if need to replan
        current_state = {'survivor_positions': set(grid.survivor_positions)}
        should_replan, reason = self.planner.replan_if_needed(
            self.current_plan, self.position, current_state, self.blocked_steps
        )
        
        if should_replan or not self.current_plan:
            if reason:
                self.logger.log_replanning(self.agent_id, reason, str(self.current_plan), "Generating new exploration plan")
            
            # Generate new exploration plan
            self.current_plan = self._plan_exploration(grid, risk_model)
        
        # Execute next action in plan
        if self.current_plan:
            action = self.current_plan[0]  # Peek at action, don't pop yet
            
            # If action needs path, compute it
            if action.type in [ActionType.EXPLORE, ActionType.MOVE]:
                target = action.parameters.get('target')
                
                # Check if we've already reached the destination
                if self.position == target:
                    # We're at destination, consume the action
                    self.current_plan.pop(0)
                    # Mark cell as explored  
                    self.cells_explored += 1
                    # Continue to next action if any
                    if self.current_plan:
                        action = self.current_plan.pop(0)
                        return action
                    else:
                        return Action(
                            type=ActionType.WAIT,
                            parameters={},
                            preconditions=[],
                            effects=[],
                            cost=1.0
                        )
                
                # Not at destination yet - continue moving
                if action.parameters.get('path') is None:
                    path, cost = self._compute_path(self.position, target, grid, risk_model)
                    action.parameters['path'] = path
                    
                    # Log pathfinding
                    if path:
                        self.logger.log_pathfinding(
                            self.agent_id, self.position, target, path, cost, "A*"
                        )
                    
                    # If no path, replan
                    if not path:
                        self.current_plan = []
                        return Action(
                            type=ActionType.WAIT,
                            parameters={},
                            preconditions=[],
                            effects=[],
                            cost=1.0
                        )
                
                # Have path - move one step
                path = action.parameters.get('path')
                if path and len(path) > 1:
                    # Move to next step in path
                    next_step = path[1]
                    # Update path to remove first element
                    action.parameters['path'] = path[1:]
                    
                    # Return move action for this step
                    return Action(
                        type=ActionType.EXPLORE,
                        parameters={'target': next_step},
                        preconditions=[],
                        effects=[],
                        cost=1.0
                    )
            else:
                # Not a movement action - just execute it
                self.current_plan.pop(0)
                return action
            
            return action
        
        # No valid plan - wait
        return Action(
            type=ActionType.WAIT,
            parameters={},
            preconditions=[],
            effects=[],
            cost=1.0
        )
    
    def _plan_exploration(self, grid, risk_model) -> List[Any]:
        """
        Generate exploration plan.
        
        Args:
            grid: Environment grid
            risk_model: Risk model
            
        Returns:
            List of exploration actions
        """
        # Update exploration frontier
        self._update_frontier(grid)
        
        if not self.exploration_frontier:
            # Everything explored - patrol randomly
            return self._generate_patrol_plan(grid, risk_model)
        
        # Select best exploration target
        target = self._select_exploration_target(grid, risk_model)
        
        if not target:
            return []
        
        # Generate plan
        plan = self.planner.plan_exploration(
            self.position,
            [target],
            self.risk_threshold
        )
        
        # Log planning
        if plan:
            self.logger.log_planning(
                self.agent_id,
                f"Explore frontier cell {target}",
                [str(a) for a in plan],
                sum(a.cost for a in plan)
            )
        
        return plan
    
    def _update_frontier(self, grid):
        """
        Update list of frontier cells (unexplored but adjacent to explored).
        
        Args:
            grid: Environment grid
            
        Rationale:
            BFS exploration - frontier is the boundary between known and unknown
        """
        frontier = set()
        
        # Find all unexplored cells adjacent to explored cells
        for x, y in self.explored_cells:
            neighbors = grid.get_neighbors(x, y, diagonal=False)
            for nx, ny in neighbors:
                cell = grid.get_cell(nx, ny)
                if cell and (nx, ny) not in self.explored_cells:
                    # Check if passable (don't target impassable cells)
                    if cell.is_passable():
                        frontier.add((nx, ny))
        
        self.exploration_frontier = list(frontier)
    
    def _select_exploration_target(self, grid, risk_model) -> Optional[Tuple[int, int]]:
        """
        Select best exploration target from frontier.
        
        Args:
            grid: Environment grid
            risk_model: Risk model
            
        Returns:
            Best target position or None
            
        Selection criteria:
        - Minimize distance (exploration efficiency)
        - Minimize risk (safety)
        - Weight by curiosity parameter
        """
        if not self.exploration_frontier:
            return None
        
        best_target = None
        best_score = float('inf')
        
        for target in self.exploration_frontier:
            # Compute distance
            distance = abs(target[0] - self.position[0]) + abs(target[1] - self.position[1])
            
            # Get risk
            risk = risk_model.get_risk(target, "combined")
            
            # Check risk threshold
            if risk > self.risk_threshold:
                continue
            
            # Combined score (lower is better)
            score = distance * (1.0 - self.curiosity_weight) + risk * 100 * self.curiosity_weight
            
            if score < best_score:
                best_score = score
                best_target = target
        
        return best_target
    
    def _generate_patrol_plan(self, grid, risk_model) -> List[Any]:
        """
        Generate patrol plan when all areas explored.
        
        Returns:
            Random movement plan
        """
        from ..ai.planner import Action
        
        # Pick random nearby safe cell
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
            return [Action(
                type=ActionType.MOVE,
                parameters={'target': target, 'path': None},
                preconditions=[],
                effects=[],
                cost=1.0
            )]
        
        return []
    
    def _compute_path(self, start: Tuple[int, int], goal: Tuple[int, int], 
                     grid, risk_model) -> Tuple[List[Tuple[int, int]], float]:
        """
        Compute path using A* with risk awareness.
        
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
            # Allow traversing all cells (even hazardous) - cost will reflect danger
            return cell is not None
        
        def get_neighbors(x, y):
            return grid.get_neighbors(x, y, diagonal=False)
        
        def get_terrain_cost(x, y):
            cell = grid.get_cell(x, y)
            if not cell:
                return float('inf')
            # Penalize hazardous cells but still allow traversal
            cost = compute_terrain_cost(cell)
            if cell.has_fire:
                cost += 100.0
            if cell.has_debris:
                cost += 50.0
            return cost
        
        def get_risk_cost(x, y):
            risk = risk_model.get_risk((x, y), "combined")
            return compute_risk_cost(risk)
        
        return astar_search(
            start, goal, is_passable, get_neighbors,
            get_terrain_cost, get_risk_cost
        )
