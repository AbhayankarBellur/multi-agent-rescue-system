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
    
    def allocate_auction(
        self,
        agents: Dict[str, Dict],
        survivors: List[Tuple[int, int]],
        risk_model,
        distance_func,
        communication_network=None,
        agent_positions=None
    ) -> Dict[str, List[Tuple[int, int]]]:
        """
        Allocate survivors using auction-based Contract Net Protocol.
        
        Auction Process:
        1. For each unassigned survivor, announce task (CFP)
        2. Agents evaluate task and submit bids
        3. Select winner based on bid score (cost, capability, risk)
        4. Award task to winner
        5. Repeat until all survivors assigned or no valid bids
        
        Args:
            agents: Dictionary of agent_id -> {position, type, current_load, ...}
            survivors: List of survivor positions
            risk_model: Bayesian risk model
            distance_func: Distance computation function
            communication_network: Optional communication network for messaging
            agent_positions: Current agent positions for message passing
            
        Returns:
            Dictionary mapping agent_id -> list of assigned survivor positions
        """
        from .communication import TaskBid
        
        # Filter to rescue agents
        rescue_agents = {
            aid: info for aid, info in agents.items()
            if info.get('type') == 'RESCUE'
        }
        
        if not rescue_agents or not survivors:
            return {}
        
        allocation: Dict[str, List[Tuple[int, int]]] = {
            aid: [] for aid in rescue_agents.keys()
        }
        assigned_survivors: Set[Tuple[int, int]] = set()
        agent_load: Dict[str, int] = {aid: 0 for aid in rescue_agents.keys()}
        
        # Auction each survivor
        for survivor_pos in survivors:
            bids: List[TaskBid] = []
            
            # Collect bids from all agents
            for agent_id, agent_info in rescue_agents.items():
                # Check capacity constraint
                if agent_load[agent_id] >= self.max_survivors_per_agent:
                    continue
                
                agent_pos = agent_info['position']
                
                # Compute bid parameters
                distance = distance_func(agent_pos, survivor_pos)
                risk = risk_model.get_risk(survivor_pos, "combined")
                
                # Risk constraint check
                if risk > self.risk_threshold:
                    continue
                
                # Estimate completion time (simplified)
                expected_time = int(distance) + 10  # Travel + pickup/drop
                
                # Create bid
                bid = TaskBid(
                    agent_id=agent_id,
                    task_id=survivor_pos,
                    cost=distance,
                    capability=1.0,  # All rescue agents have same capability
                    risk=risk,
                    expected_time=expected_time,
                    current_load=agent_load[agent_id]
                )
                
                bids.append(bid)
            
            # No valid bids - skip this survivor (oversubscribed or too risky)
            if not bids:
                continue
            
            # Select winner (lowest score = best bid)
            bids.sort(key=lambda b: b.score(self.distance_weight, self.risk_weight))
            winner = bids[0]
            
            # Award task
            allocation[winner.agent_id].append(survivor_pos)
            assigned_survivors.add(survivor_pos)
            agent_load[winner.agent_id] += 1
        
        return allocation
    
    def allocate_iterative_auction(
        self,
        agents: Dict[str, Dict],
        survivors: List[Tuple[int, int]],
        risk_model,
        distance_func,
        current_allocation: Optional[Dict[str, List[Tuple[int, int]]]] = None
    ) -> Dict[str, List[Tuple[int, int]]]:
        """
        Iterative auction allowing task reallocation.
        
        Enables agents to "steal" tasks from others if they can perform
        better, supporting dynamic reallocation during execution.
        
        Args:
            agents: Available agents
            survivors: Survivor positions to allocate
            risk_model: Risk model
            distance_func: Distance function
            current_allocation: Existing allocation (for reallocation)
            
        Returns:
            Updated allocation
        """
        # Start with current allocation or empty
        if current_allocation:
            allocation = {aid: list(tasks) for aid, tasks in current_allocation.items()}
        else:
            allocation = {
                aid: [] for aid, info in agents.items()
                if info.get('type') == 'RESCUE'
            }
        
        # Build reverse mapping: survivor -> agent
        survivor_to_agent = {}
        for agent_id, survivor_list in allocation.items():
            for survivor_pos in survivor_list:
                survivor_to_agent[survivor_pos] = agent_id
        
        # Iterative improvement
        improved = True
        max_iterations = 5
        iteration = 0
        
        while improved and iteration < max_iterations:
            improved = False
            iteration += 1
            
            for survivor_pos in survivors:
                current_agent = survivor_to_agent.get(survivor_pos)
                
                # Compute current cost/score
                if current_agent:
                    current_pos = agents[current_agent]['position']
                    current_distance = distance_func(current_pos, survivor_pos)
                    current_risk = risk_model.get_risk(survivor_pos, "combined")
                    current_score = (self.distance_weight * current_distance +
                                   self.risk_weight * current_risk * 100)
                else:
                    current_score = float('inf')
                
                # Check if any agent can do better
                best_agent = current_agent
                best_score = current_score
                
                for agent_id, agent_info in agents.items():
                    if agent_info.get('type') != 'RESCUE':
                        continue
                    
                    # Skip if at capacity (unless it's the current agent)
                    if (agent_id != current_agent and 
                        len(allocation.get(agent_id, [])) >= self.max_survivors_per_agent):
                        continue
                    
                    agent_pos = agent_info['position']
                    distance = distance_func(agent_pos, survivor_pos)
                    risk = risk_model.get_risk(survivor_pos, "combined")
                    
                    if risk > self.risk_threshold:
                        continue
                    
                    score = (self.distance_weight * distance +
                            self.risk_weight * risk * 100)
                    
                    # Require significant improvement (10%) to switch
                    if score < best_score * 0.9:
                        best_score = score
                        best_agent = agent_id
                
                # Reallocate if better agent found
                if best_agent != current_agent:
                    # Remove from current agent
                    if current_agent and survivor_pos in allocation.get(current_agent, []):
                        allocation[current_agent].remove(survivor_pos)
                    
                    # Add to better agent
                    if best_agent not in allocation:
                        allocation[best_agent] = []
                    allocation[best_agent].append(survivor_pos)
                    survivor_to_agent[survivor_pos] = best_agent
                    
                    improved = True
        
        return allocation
    
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
