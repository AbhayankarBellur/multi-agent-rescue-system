"""
Rescue Agent Implementation
Responsible for evacuating survivors to safe zones.

Strategy:
- STRIPS planning for rescue sequences
- A* pathfinding with risk awareness
- Task assignment from CSP allocator
- Prioritize based on urgency and risk
"""

from typing import Tuple, Optional, List, Any, Dict
from .base_agent import BaseAgent
from ..utils.config import AgentType, ActionType, AGENT
from ..ai.search import astar_search, compute_terrain_cost, compute_risk_cost, find_nearest_goal
from ..ai.planner import STRIPSPlanner, Action


class RescueAgent(BaseAgent):
    """
    Rescue agent using STRIPS planning and A* navigation.
    
    Goal: Evacuate all assigned survivors to safe zones
    
    Algorithm:
    1. Receive survivor assignments from CSP allocator
    2. Generate rescue plan (move, pickup, transport, drop)
    3. Execute plan with dynamic replanning
    4. Handle blocked paths and changing hazards
    """
    
    def __init__(self, agent_id: str, start_position: Tuple[int, int]):
        """Initialize rescue agent."""
        super().__init__(agent_id, AgentType.RESCUE, start_position)
        self.planner = STRIPSPlanner()
        self.risk_threshold = AGENT.RISK_THRESHOLD_RESCUE
        self.urgency_weight = AGENT.RESCUE_URGENCY_WEIGHT
    
    def decide_action(self, grid, risk_model, **kwargs) -> Optional[Action]:
        """
        Decide next rescue action.
        
        Args:
            grid: Environment grid
            risk_model: Bayesian risk model
            **kwargs: May contain 'allocation' from CSP
            
        Returns:
            Action to execute
            
        Decision logic:
        1. Check if carrying survivor - if yes, complete delivery
        2. Check assigned tasks from CSP
        3. If no assignment, find nearest unassigned survivor
        4. Generate/continue rescue plan
        5. Execute next action
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
        
        # Update assigned tasks from CSP
        allocation = kwargs.get('allocation', {})
        if self.agent_id in allocation:
            self.assigned_tasks = allocation[self.agent_id]
        
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
                    "Generating new rescue plan"
                )
            
            # Generate new rescue plan - tries multiple survivors if needed
            self.current_plan = self._plan_rescue(grid, risk_model)
        
        # Execute next action
        if self.current_plan:
            action = self.current_plan[0]  # Peek at action, don't pop yet
            
            # Compute path if needed
            if action.type in [ActionType.MOVE, ActionType.TRANSPORT]:
                target = action.parameters.get('target')
                
                # Check if we've already reached the destination
                if self.position == target:
                    # We're at destination, consume the action and move to next
                    self.current_plan.pop(0)
                    # Execute the next action (probably PICKUP or DROP)
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
                    
                    if path:
                        self.logger.log_pathfinding(
                            self.agent_id, self.position, target, path, cost, "A*"
                        )
                    else:
                        # Path blocked - current goal unreachable
                        # Clear plan and let _plan_rescue try alternatives on next call
                        self.logger.log_replanning(
                            self.agent_id, f"No path to {target}",
                            str(action), "Switching to alternative goal"
                        )
                        self.current_plan = []
                        self.blocked_steps += 1
                        
                        # Try to move toward any passable neighbor to make progress
                        neighbors = grid.get_neighbors(self.position[0], self.position[1], diagonal=True)
                        passable = [
                            n for n in neighbors 
                            if grid.get_cell(n[0], n[1]) and grid.get_cell(n[0], n[1]).is_passable()
                        ]
                        
                        if passable:
                            # Move to nearest passable neighbor to escape dead zone
                            return Action(
                                type=ActionType.MOVE,
                                parameters={'target': passable[0]},
                                preconditions=[],
                                effects=[],
                                cost=1.0
                            )
                        else:
                            # No escape - wait
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
                    
                    # Return move action for this step (don't consume the plan action yet)
                    return Action(
                        type=action.type,
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
        
        # No plan - wait
        return Action(
            type=ActionType.WAIT,
            parameters={},
            preconditions=[],
            effects=[],
            cost=1.0
        )
    
    def _plan_rescue(self, grid, risk_model) -> List[Action]:
        """
        Generate rescue plan for assigned or nearest survivor.
        
        Args:
            grid: Environment grid
            risk_model: Risk model
            
        Returns:
            List of rescue actions
        """
        # If carrying survivor, complete delivery
        if self.carrying_survivor:
            return self._plan_delivery(grid, risk_model)
        
        # Select survivor to rescue
        target_survivor = self._select_rescue_target(grid, risk_model)
        
        if not target_survivor:
            return []  # No survivors to rescue
        
        # Get safe zones
        safe_zones = list(grid.safe_zone_positions)
        
        if not safe_zones:
            self.logger.log_error(self.agent_id, "No safe zones available!")
            return []
        
        # Generate rescue plan
        plan = self.planner.plan_rescue(
            self.position,
            target_survivor,
            safe_zones,
            None  # Pathfinder not used in planning (we compute paths during execution)
        )
        
        # Log plan
        if plan:
            self.logger.log_planning(
                self.agent_id,
                f"Rescue survivor at {target_survivor}",
                [str(a) for a in plan],
                sum(a.cost for a in plan)
            )
        
        return plan
    
    def _plan_delivery(self, grid, risk_model) -> List[Action]:
        """
        Plan to deliver currently carried survivor to safe zone.
        
        Args:
            grid: Environment grid
            risk_model: Risk model
            
        Returns:
            Transport and drop actions
        """
        safe_zones = list(grid.safe_zone_positions)
        
        # Find nearest safe zone
        _, _, best_zone = find_nearest_goal(
            self.position, safe_zones,
            lambda x, y: grid.get_cell(x, y) is not None and grid.get_cell(x, y).is_passable(),
            lambda x, y: grid.get_neighbors(x, y, diagonal=False),
            lambda x, y: compute_terrain_cost(grid.get_cell(x, y)) if grid.get_cell(x, y) else float('inf'),
            lambda x, y: compute_risk_cost(risk_model.get_risk((x, y), "combined"))
        )
        
        if best_zone is None and safe_zones:
            best_zone = safe_zones[0]  # Fallback
        
        if not best_zone:
            return []
        
        plan = [
            Action(
                type=ActionType.TRANSPORT,
                parameters={'target': best_zone, 'path': None},
                preconditions=["Carrying survivor"],
                effects=[f"At safe zone {best_zone}"],
                cost=1.0
            ),
            Action(
                type=ActionType.DROP,
                parameters={'position': best_zone},
                preconditions=[f"At {best_zone}", "Carrying survivor"],
                effects=["Survivor safe", "Not carrying survivor"],
                cost=1.0
            )
        ]
        
        return plan
    
    def _select_rescue_target(self, grid, risk_model) -> Optional[Tuple[int, int]]:
        """
        Select which survivor to rescue.
        
        Args:
            grid: Environment grid
            risk_model: Risk model
            
        Returns:
            Target survivor position
            
        Priority:
        1. Assigned tasks from CSP (but check reachability!)
        2. Nearest reachable unassigned survivor
        3. Consider risk and distance
        """
        # Collect candidate survivors
        candidates = []
        
        # Use assigned tasks first if available
        if self.assigned_tasks:
            valid_tasks = [
                pos for pos in self.assigned_tasks 
                if pos in grid.survivor_positions
            ]
            candidates.extend(valid_tasks)
        
        # Add unassigned survivors as fallback
        if not candidates:
            candidates = list(grid.survivor_positions)
        
        if not candidates:
            return None
        
        # Try to find a REACHABLE survivor from candidates
        # Sort by distance, try each one in order
        reachable_survivors = []
        
        for survivor in candidates:
            # Quick check: is survivor reachable?
            path, _ = self._compute_path(self.position, survivor, grid, risk_model)
            
            if path:  # Path exists!
                distance = abs(survivor[0] - self.position[0]) + abs(survivor[1] - self.position[1])
                risk = risk_model.get_risk(survivor, "combined")
                score = distance * (1.0 - self.urgency_weight) + risk * 100 * self.urgency_weight
                reachable_survivors.append((score, survivor))
        
        # If we found any reachable survivors, use the best one
        if reachable_survivors:
            reachable_survivors.sort(key=lambda x: x[0])
            return reachable_survivors[0][1]
        
        # All assigned survivors unreachable - find nearest unassigned
        unassigned = [s for s in grid.survivor_positions if s not in self.assigned_tasks]
        
        for survivor in unassigned:
            path, _ = self._compute_path(self.position, survivor, grid, risk_model)
            
            if path:  # Reachable unassigned survivor
                distance = abs(survivor[0] - self.position[0]) + abs(survivor[1] - self.position[1])
                risk = risk_model.get_risk(survivor, "combined")
                score = distance * (1.0 - self.urgency_weight) + risk * 100 * self.urgency_weight
                reachable_survivors.append((score, survivor))
        
        if reachable_survivors:
            reachable_survivors.sort(key=lambda x: x[0])
            return reachable_survivors[0][1]
        
        # Last resort: return any survivor (not reachable, but at least we have a goal)
        if candidates:
            return candidates[0]
        
        return None
    
    def _compute_path(self, start: Tuple[int, int], goal: Tuple[int, int],
                     grid, risk_model) -> Tuple[List[Tuple[int, int]], float]:
        """
        Compute path using risk-aware A*.
        
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
            # For rescue operations, allow traversing fire/debris cells if necessary
            # (high cost will discourage them, but they won't be blocked completely)
            return cell is not None
        
        def get_neighbors(x, y):
            return grid.get_neighbors(x, y, diagonal=False)
        
        def get_terrain_cost(x, y):
            cell = grid.get_cell(x, y)
            if not cell:
                return float('inf')
            # CRITICAL: Heavily penalize fire/debris cells so they're last resort
            cost = compute_terrain_cost(cell)
            if cell.has_fire:
                cost += 100.0  # Extreme penalty for fire
            if cell.has_debris:
                cost += 50.0   # High penalty for debris
            return cost
        
        def get_risk_cost(x, y):
            risk = risk_model.get_risk((x, y), "combined")
            return compute_risk_cost(risk)
        
        return astar_search(
            start, goal, is_passable, get_neighbors,
            get_terrain_cost, get_risk_cost
        )
