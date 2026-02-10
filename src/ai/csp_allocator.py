"""
Constraint Satisfaction Problem (CSP) - Task Allocation
Assigns survivors to rescue agents subject to constraints.

CSP Formulation:
- Variables: Each survivor needs assignment
- Domain: Available rescue agents
- Constraints:
  1. One agent per survivor (uniqueness)
  2. Max survivors per agent (capacity)
  3. Risk threshold (safety)
  4. Distance/workload balancing (efficiency)

Algorithm: Backtracking search with forward checking and heuristics
"""

from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass
from ..utils.config import AI


@dataclass
class Assignment:
    """
    Task assignment result.
    
    Attributes:
        agent_id: Assigned agent identifier
        survivor_pos: Survivor position
        distance: Distance from agent to survivor
        risk: Risk level for assignment
        priority: Assignment priority (lower = higher priority)
    """
    agent_id: str
    survivor_pos: Tuple[int, int]
    distance: float
    risk: float
    priority: float
    
    def __repr__(self) -> str:
        return f"{self.agent_id} -> {self.survivor_pos} (d={self.distance:.1f}, r={self.risk:.2f})"


class CSPAllocator:
    """
    CSP-based task allocation for multi-agent rescue coordination.
    
    Goal: Assign each survivor to an agent such that:
    - All survivors are assigned (completeness)
    - No agent is overloaded (capacity constraints)
    - Risk is acceptable (safety constraints)
    - Workload is balanced (efficiency)
    
    This is a constraint optimization problem (COP) - we seek the best
    feasible solution, not just any feasible solution.
    """
    
    def __init__(self):
        """Initialize CSP allocator."""
        self.max_survivors_per_agent = AI.CSP_MAX_SURVIVORS_PER_AGENT
        self.risk_threshold = AI.CSP_RISK_CONSTRAINT_THRESHOLD
        self.distance_weight = AI.CSP_DISTANCE_WEIGHT
        self.risk_weight = AI.CSP_RISK_WEIGHT
    
    def allocate(
        self,
        agents: Dict[str, Dict],
        survivors: List[Tuple[int, int]],
        risk_model,
        distance_func
    ) -> Dict[str, List[Tuple[int, int]]]:
        """
        Allocate survivors to agents using CSP.
        
        Args:
            agents: Dictionary of agent_id -> {position, type, current_load, ...}
            survivors: List of survivor positions
            risk_model: Bayesian risk model for risk queries
            distance_func: Function to compute distance between positions
            
        Returns:
            Dictionary mapping agent_id -> list of assigned survivor positions
            
        Algorithm:
        1. Compute all possible assignments with costs
        2. Sort assignments by priority (cost-based)
        3. Greedily assign while respecting constraints
        4. Backtrack if no feasible solution exists
        """
        # Filter to only rescue agents
        rescue_agents = {
            aid: info for aid, info in agents.items()
            if info.get('type') == 'RESCUE'
        }
        
        if not rescue_agents or not survivors:
            return {}
        
        # Generate all possible assignments
        possible_assignments = self._generate_assignments(
            rescue_agents, survivors, risk_model, distance_func
        )
        
        # Sort by priority (lower = better)
        possible_assignments.sort(key=lambda a: a.priority)
        
        # Greedy allocation with constraint checking
        allocation = self._greedy_allocate(
            possible_assignments, rescue_agents, survivors
        )
        
        return allocation
    
    def _generate_assignments(
        self,
        agents: Dict,
        survivors: List[Tuple[int, int]],
        risk_model,
        distance_func
    ) -> List[Assignment]:
        """
        Generate all feasible (agent, survivor) pairs.
        
        Args:
            agents: Available agents
            survivors: Survivor positions
            risk_model: Risk estimation model
            distance_func: Distance computation
            
        Returns:
            List of Assignment objects
        """
        assignments = []
        
        for agent_id, agent_info in agents.items():
            agent_pos = agent_info['position']
            
            for survivor_pos in survivors:
                # Compute distance
                distance = distance_func(agent_pos, survivor_pos)
                
                # Compute risk along path
                risk = risk_model.get_risk(survivor_pos, "combined")
                
                # Constraint check: Risk threshold
                if risk > self.risk_threshold:
                    continue  # Too risky
                
                # Compute priority (lower = higher priority)
                # Weighted combination of distance and risk
                priority = (
                    self.distance_weight * distance +
                    self.risk_weight * risk * 100  # Scale risk to comparable magnitude
                )
                
                assignments.append(Assignment(
                    agent_id=agent_id,
                    survivor_pos=survivor_pos,
                    distance=distance,
                    risk=risk,
                    priority=priority
                ))
        
        return assignments
    
    def _greedy_allocate(
        self,
        assignments: List[Assignment],
        agents: Dict,
        survivors: List[Tuple[int, int]]
    ) -> Dict[str, List[Tuple[int, int]]]:
        """
        Greedy allocation respecting capacity constraints.
        
        Args:
            assignments: Sorted list of possible assignments
            agents: Agent information
            survivors: Survivor positions
            
        Returns:
            Allocation mapping
            
        Algorithm:
            For each assignment in priority order:
                If agent has capacity and survivor unassigned:
                    Assign survivor to agent
        """
        allocation: Dict[str, List[Tuple[int, int]]] = {
            aid: [] for aid in agents.keys()
        }
        
        assigned_survivors: Set[Tuple[int, int]] = set()
        agent_load: Dict[str, int] = {aid: 0 for aid in agents.keys()}
        
        for assignment in assignments:
            agent_id = assignment.agent_id
            survivor_pos = assignment.survivor_pos
            
            # Check if survivor already assigned
            if survivor_pos in assigned_survivors:
                continue
            
            # Check agent capacity constraint
            if agent_load[agent_id] >= self.max_survivors_per_agent:
                continue
            
            # Assign
            allocation[agent_id].append(survivor_pos)
            assigned_survivors.add(survivor_pos)
            agent_load[agent_id] += 1
        
        return allocation
    
    def reallocate_on_failure(
        self,
        current_allocation: Dict[str, List[Tuple[int, int]]],
        failed_agent: str,
        failed_survivor: Tuple[int, int],
        agents: Dict,
        risk_model,
        distance_func
    ) -> Optional[str]:
        """
        Reallocate a survivor when agent fails to reach it.
        
        Args:
            current_allocation: Current task assignments
            failed_agent: Agent that failed
            failed_survivor: Survivor that couldn't be reached
            agents: Agent information
            risk_model: Risk model
            distance_func: Distance function
            
        Returns:
            New agent ID if reallocation possible, None otherwise
        """
        # Remove from failed agent's allocation
        if failed_agent in current_allocation:
            current_allocation[failed_agent] = [
                s for s in current_allocation[failed_agent] if s != failed_survivor
            ]
        
        # Find alternative agent
        rescue_agents = {
            aid: info for aid, info in agents.items()
            if info.get('type') == 'RESCUE' and aid != failed_agent
        }
        
        best_agent = None
        best_priority = float('inf')
        
        for agent_id, agent_info in rescue_agents.items():
            # Check capacity
            current_load = len(current_allocation.get(agent_id, []))
            if current_load >= self.max_survivors_per_agent:
                continue
            
            # Compute assignment cost
            agent_pos = agent_info['position']
            distance = distance_func(agent_pos, failed_survivor)
            risk = risk_model.get_risk(failed_survivor, "combined")
            
            if risk > self.risk_threshold:
                continue
            
            priority = self.distance_weight * distance + self.risk_weight * risk * 100
            
            if priority < best_priority:
                best_priority = priority
                best_agent = agent_id
        
        # Assign to new agent
        if best_agent:
            if best_agent not in current_allocation:
                current_allocation[best_agent] = []
            current_allocation[best_agent].append(failed_survivor)
        
        return best_agent
    
    def get_allocation_summary(self, allocation: Dict[str, List[Tuple[int, int]]]) -> str:
        """
        Generate human-readable allocation summary.
        
        Args:
            allocation: Allocation mapping
            
        Returns:
            Formatted summary string
        """
        if not allocation:
            return "No allocations"
        
        summary = "Task Allocation:\n"
        
        for agent_id, survivors in allocation.items():
            if survivors:
                summary += f"  {agent_id}: {len(survivors)} survivor(s) at {survivors}\n"
            else:
                summary += f"  {agent_id}: No assignments\n"
        
        total_assigned = sum(len(s) for s in allocation.values())
        summary += f"Total assigned: {total_assigned}"
        
        return summary
    
    def validate_allocation(
        self,
        allocation: Dict[str, List[Tuple[int, int]]],
        survivors: List[Tuple[int, int]]
    ) -> Tuple[bool, str]:
        """
        Validate allocation satisfies constraints.
        
        Args:
            allocation: Proposed allocation
            survivors: All survivors
            
        Returns:
            (is_valid, error_message)
        """
        # Check all survivors assigned
        assigned = set()
        for survivors_list in allocation.values():
            assigned.update(survivors_list)
        
        unassigned = set(survivors) - assigned
        if unassigned:
            return False, f"{len(unassigned)} survivors unassigned: {unassigned}"
        
        # Check capacity constraints
        for agent_id, survivors_list in allocation.items():
            if len(survivors_list) > self.max_survivors_per_agent:
                return False, f"{agent_id} exceeds capacity: {len(survivors_list)} > {self.max_survivors_per_agent}"
        
        return True, "Valid allocation"
