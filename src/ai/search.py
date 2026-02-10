"""
A* Search Implementation
Implements A* pathfinding with terrain penalties and risk-aware costs.

Algorithm:
- Classic A* with priority queue
- Cost function: g(n) = distance + terrain_penalty + risk_penalty
- Heuristic: h(n) = Manhattan distance × (1 + risk_factor)
- Guarantees optimal path when heuristic is admissible

This is stateless - takes grid state as input, returns path.
"""

import heapq
from typing import List, Tuple, Optional, Callable, Set, Dict
from ..utils.config import AI


class AStarNode:
    """
    A* search node with cost tracking.
    
    Attributes:
        position: (x, y) coordinates
        g_cost: Actual cost from start to this node
        h_cost: Heuristic estimated cost to goal
        f_cost: Total cost (g + h)
        parent: Previous node in path
    """
    
    def __init__(self, position: Tuple[int, int], g_cost: float, h_cost: float, 
                 parent: Optional['AStarNode'] = None):
        self.position = position
        self.g_cost = g_cost
        self.h_cost = h_cost
        self.f_cost = g_cost + h_cost
        self.parent = parent
    
    def __lt__(self, other: 'AStarNode') -> bool:
        """Comparison for priority queue (lower f_cost = higher priority)."""
        return self.f_cost < other.f_cost
    
    def __eq__(self, other: 'AStarNode') -> bool:
        return self.position == other.position
    
    def __hash__(self):
        return hash(self.position)


def manhattan_distance(pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
    """
    Calculate Manhattan distance between two positions.
    
    Args:
        pos1: First position (x, y)
        pos2: Second position (x, y)
        
    Returns:
        Manhattan distance
        
    Rationale:
        Admissible heuristic for grid-based movement (4-directional).
        Never overestimates actual cost.
    """
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])


def euclidean_distance(pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
    """Calculate Euclidean distance (for diagonal movement)."""
    return ((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)**0.5


def astar_search(
    start: Tuple[int, int],
    goal: Tuple[int, int],
    is_passable: Callable[[int, int], bool],
    get_neighbors: Callable[[int, int], List[Tuple[int, int]]],
    get_terrain_cost: Callable[[int, int], float],
    get_risk_cost: Callable[[int, int], float],
    heuristic: str = "manhattan"
) -> Tuple[List[Tuple[int, int]], float]:
    """
    A* pathfinding with terrain and risk awareness.
    
    Args:
        start: Starting position (x, y)
        goal: Goal position (x, y)
        is_passable: Function to check if cell is traversable
        get_neighbors: Function to get neighboring cells
        get_terrain_cost: Function returning terrain penalty [0, inf)
        get_risk_cost: Function returning risk penalty [0, inf)
        heuristic: "manhattan" or "euclidean"
        
    Returns:
        Tuple of (path, total_cost) where path is list of waypoints
        Empty list if no path exists
        
    Algorithm:
    1. Initialize open set (priority queue) with start node
    2. Expand node with lowest f_cost
    3. For each neighbor:
       - Calculate g_cost = parent.g + step_cost + terrain_penalty + risk_penalty
       - Calculate h_cost using heuristic
       - Add to open set if not visited or found cheaper path
    4. Reconstruct path from goal to start via parent pointers
    
    Cost function design:
        Base cost = 1.0 per step
        Terrain penalty (debris/flood) makes difficult cells expensive
        Risk penalty (fire/collapse probability) discourages dangerous routes
        Total cost balances safety and efficiency
    """
    # Validate inputs
    if not is_passable(start[0], start[1]):
        return [], float('inf')
    if not is_passable(goal[0], goal[1]):
        return [], float('inf')
    
    # Choose heuristic function
    heuristic_func = euclidean_distance if heuristic == "euclidean" else manhattan_distance
    
    # Initialize data structures
    open_set: List[AStarNode] = []
    closed_set: Set[Tuple[int, int]] = set()
    g_costs: Dict[Tuple[int, int], float] = {start: 0.0}
    
    # Add start node
    start_h = heuristic_func(start, goal)
    start_node = AStarNode(start, 0.0, start_h, None)
    heapq.heappush(open_set, start_node)
    
    # Main search loop
    while open_set:
        # Get node with lowest f_cost
        current = heapq.heappop(open_set)
        
        # Check if goal reached
        if current.position == goal:
            return _reconstruct_path(current), current.g_cost
        
        # Skip if already processed
        if current.position in closed_set:
            continue
        
        # Mark as processed
        closed_set.add(current.position)
        
        # Expand neighbors
        neighbors = get_neighbors(current.position[0], current.position[1])
        
        for neighbor_pos in neighbors:
            nx, ny = neighbor_pos
            
            # Skip impassable cells
            if not is_passable(nx, ny):
                continue
            
            # Skip if already processed
            if neighbor_pos in closed_set:
                continue
            
            # Calculate costs
            step_cost = 1.0  # Base movement cost
            terrain_cost = get_terrain_cost(nx, ny)
            risk_cost = get_risk_cost(nx, ny)
            
            # Total cost to reach this neighbor
            tentative_g = current.g_cost + step_cost + terrain_cost + risk_cost
            
            # Check if this is a better path
            if neighbor_pos not in g_costs or tentative_g < g_costs[neighbor_pos]:
                g_costs[neighbor_pos] = tentative_g
                
                # Calculate heuristic with risk weighting
                base_h = heuristic_func(neighbor_pos, goal)
                risk_factor = get_risk_cost(nx, ny) / AI.ASTAR_RISK_PENALTY_MULTIPLIER
                h_cost = base_h * (1.0 + AI.ASTAR_HEURISTIC_RISK_WEIGHT * risk_factor)
                
                # Create and add neighbor node
                neighbor_node = AStarNode(neighbor_pos, tentative_g, h_cost, current)
                heapq.heappush(open_set, neighbor_node)
    
    # No path found
    return [], float('inf')


def _reconstruct_path(node: AStarNode) -> List[Tuple[int, int]]:
    """
    Reconstruct path from goal to start via parent pointers.
    
    Args:
        node: Goal node with parent chain
        
    Returns:
        List of positions from start to goal
    """
    path = []
    current = node
    
    while current is not None:
        path.append(current.position)
        current = current.parent
    
    # Reverse to get start-to-goal order
    path.reverse()
    return path


def compute_terrain_cost(cell) -> float:
    """
    Calculate terrain penalty for a cell.
    
    Args:
        cell: Cell object from environment
        
    Returns:
        Penalty value (0 = no penalty, higher = more difficult)
        
    Rationale:
        Debris is very difficult to traverse (structural obstacles)
        Flood is moderately difficult (water resistance)
        Fire is impassable (blocked by is_passable check)
    """
    if cell.has_debris:
        return AI.ASTAR_TERRAIN_PENALTY_DEBRIS
    if cell.has_flood:
        return AI.ASTAR_TERRAIN_PENALTY_FLOOD
    return 0.0


def compute_risk_cost(risk_value: float) -> float:
    """
    Calculate risk penalty from probability estimate.
    
    Args:
        risk_value: Risk probability [0.0, 1.0]
        
    Returns:
        Cost penalty proportional to risk
        
    Rationale:
        Exponential penalty - high risk cells are heavily avoided
        Multiplier controls risk-aversion vs path efficiency tradeoff
    """
    return risk_value * AI.ASTAR_RISK_PENALTY_MULTIPLIER


def find_nearest_goal(
    start: Tuple[int, int],
    goals: List[Tuple[int, int]],
    is_passable: Callable[[int, int], bool],
    get_neighbors: Callable[[int, int], List[Tuple[int, int]]],
    get_terrain_cost: Callable[[int, int], float],
    get_risk_cost: Callable[[int, int], float]
) -> Tuple[Optional[Tuple[int, int]], List[Tuple[int, int]], float]:
    """
    Find nearest reachable goal from multiple options.
    
    Args:
        start: Starting position
        goals: List of possible goal positions
        (other args same as astar_search)
        
    Returns:
        Tuple of (best_goal, path, cost)
        (None, [], inf) if no goals are reachable
        
    Rationale:
        Agents often have multiple possible targets (survivors, safe zones)
        This finds the optimal choice considering both distance and risk
    """
    best_goal = None
    best_path = []
    best_cost = float('inf')
    
    for goal in goals:
        path, cost = astar_search(
            start, goal, is_passable, get_neighbors,
            get_terrain_cost, get_risk_cost
        )
        
        if path and cost < best_cost:
            best_goal = goal
            best_path = path
            best_cost = cost
    
    return best_goal, best_path, best_cost
