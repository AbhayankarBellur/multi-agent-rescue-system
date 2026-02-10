"""
Bayesian Risk Estimation Module
Probabilistic inference for hazard risk (fire, flood, collapse).

Theoretical Foundation:
- Maintains prior probability distributions
- Updates beliefs based on observations (Bayesian updating)
- Provides risk estimates for decision making

This is NOT a predictor - it's a belief tracker that quantifies uncertainty.
"""

from typing import Dict, Tuple, Optional
import math
from ..utils.config import AI, HAZARD


class BayesianRiskModel:
    """
    Bayesian belief network for disaster risk estimation.
    
    Models three primary risks:
    1. Fire risk - probability of fire spreading to cell
    2. Flood risk - probability of flooding
    3. Collapse risk - probability of structural failure (debris generation)
    
    Uses simple Bayesian updating:
        P(risk|observation) ∝ P(observation|risk) × P(risk)
    
    Design principle:
        Explicit probability tracking enables risk-aware decision making.
        Agents can reason about uncertainty rather than reacting to current state only.
    """
    
    def __init__(self):
        """
        Initialize risk model with prior probabilities.
        
        Priors represent baseline risk in absence of observations.
        """
        # Prior probabilities (configurable)
        self.prior_fire = AI.BAYESIAN_PRIOR_FIRE
        self.prior_flood = AI.BAYESIAN_PRIOR_FLOOD
        self.prior_collapse = AI.BAYESIAN_PRIOR_COLLAPSE
        
        # Risk maps: (x, y) -> probability
        self.fire_risk: Dict[Tuple[int, int], float] = {}
        self.flood_risk: Dict[Tuple[int, int], float] = {}
        self.collapse_risk: Dict[Tuple[int, int], float] = {}
        
        # Observation counts for confidence
        self.observation_count: Dict[Tuple[int, int], int] = {}
    
    def initialize_grid(self, width: int, height: int):
        """
        Initialize risk estimates for entire grid.
        
        Args:
            width: Grid width
            height: Grid height
        """
        for x in range(width):
            for y in range(height):
                pos = (x, y)
                self.fire_risk[pos] = self.prior_fire
                self.flood_risk[pos] = self.prior_flood
                self.collapse_risk[pos] = self.prior_collapse
                self.observation_count[pos] = 0
    
    def update_from_observation(self, position: Tuple[int, int], cell, neighbors_info: list):
        """
        Update risk estimates based on cell observation.
        
        Args:
            position: Cell coordinates
            cell: Cell object with current state
            neighbors_info: List of neighbor cell states
            
        Algorithm:
        1. Observe current cell state
        2. Observe neighbor states (hazards spread from neighbors)
        3. Apply Bayesian update: posterior ∝ likelihood × prior
        4. Normalize to keep probabilities in [0, 1]
        
        Rationale:
            Direct observations (cell currently on fire) give certainty
            Neighbor observations (fire next door) increase risk
            Repeated observations increase confidence
        """
        x, y = position
        
        # Count observations for this cell
        self.observation_count[position] = self.observation_count.get(position, 0) + 1
        
        # Update fire risk
        self.fire_risk[position] = self._compute_fire_risk(cell, neighbors_info)
        
        # Update flood risk
        self.flood_risk[position] = self._compute_flood_risk(cell, neighbors_info)
        
        # Update collapse risk
        self.collapse_risk[position] = self._compute_collapse_risk(cell, neighbors_info)
    
    def _compute_fire_risk(self, cell, neighbors_info) -> float:
        """
        Estimate fire risk using Bayesian inference.
        
        Args:
            cell: Current cell state
            neighbors_info: Neighbor states
            
        Returns:
            Fire risk probability [0.0, 1.0]
            
        Logic:
            - If cell has fire: risk = 1.0 (certainty)
            - If cell has flood: risk = 0.0 (incompatible)
            - Otherwise: compute based on neighbor fires
        """
        # Direct observation overrides inference
        if cell.has_fire:
            return 1.0
        
        if cell.has_flood or cell.is_safe_zone:
            return 0.0
        
        # Count neighbors with fire
        num_fire_neighbors = sum(1 for n in neighbors_info if n.has_fire)
        
        if num_fire_neighbors == 0:
            # No immediate threat - decay toward prior
            current = self.fire_risk.get((cell.x, cell.y), self.prior_fire)
            return current * (1.0 - AI.BAYESIAN_UPDATE_RATE) + self.prior_fire * AI.BAYESIAN_UPDATE_RATE
        
        # Bayesian update based on spreading probability
        # P(fire_next_step | neighbors_burning) = 1 - (1 - spread_rate)^n_neighbors
        # This models independent spread attempts from each neighbor
        spread_prob = 1.0 - math.pow(1.0 - HAZARD.FIRE_SPREAD_RATE, num_fire_neighbors)
        
        # If cell has debris, fire spreads faster
        if cell.has_debris:
            spread_prob = 1.0 - math.pow(1.0 - HAZARD.FIRE_SPREAD_TO_DEBRIS, num_fire_neighbors)
        
        # Weighted update: blend previous belief with new evidence
        current = self.fire_risk.get((cell.x, cell.y), self.prior_fire)
        return current * (1.0 - AI.BAYESIAN_UPDATE_RATE) + spread_prob * AI.BAYESIAN_UPDATE_RATE
    
    def _compute_flood_risk(self, cell, neighbors_info) -> float:
        """Estimate flood risk (similar logic to fire)."""
        if cell.has_flood:
            return 1.0
        
        if cell.is_safe_zone:
            return 0.0
        
        num_flood_neighbors = sum(1 for n in neighbors_info if n.has_flood)
        
        if num_flood_neighbors == 0:
            current = self.flood_risk.get((cell.x, cell.y), self.prior_flood)
            return current * (1.0 - AI.BAYESIAN_UPDATE_RATE) + self.prior_flood * AI.BAYESIAN_UPDATE_RATE
        
        spread_prob = 1.0 - math.pow(1.0 - HAZARD.FLOOD_SPREAD_RATE, num_flood_neighbors)
        
        current = self.flood_risk.get((cell.x, cell.y), self.prior_flood)
        return current * (1.0 - AI.BAYESIAN_UPDATE_RATE) + spread_prob * AI.BAYESIAN_UPDATE_RATE
    
    def _compute_collapse_risk(self, cell, neighbors_info) -> float:
        """
        Estimate structural collapse risk.
        
        Args:
            cell: Current cell
            neighbors_info: Neighbor states
            
        Returns:
            Collapse probability
            
        Rationale:
            Collapse occurs near intense fires (heat/structural damage)
            Existing debris indicates structural weakness
        """
        if cell.has_debris:
            return 1.0  # Already collapsed
        
        if cell.is_safe_zone or cell.has_survivor:
            return 0.0  # Protected areas
        
        # Count fire neighbors (fire weakens structures)
        num_fire_neighbors = sum(1 for n in neighbors_info if n.has_fire)
        
        if num_fire_neighbors == 0:
            current = self.collapse_risk.get((cell.x, cell.y), self.prior_collapse)
            return current * (1.0 - AI.BAYESIAN_UPDATE_RATE) + self.prior_collapse * AI.BAYESIAN_UPDATE_RATE
        
        # Collapse probability increases with nearby fires
        collapse_prob = 1.0 - math.pow(1.0 - HAZARD.DEBRIS_GENERATION_NEAR_FIRE, num_fire_neighbors)
        
        current = self.collapse_risk.get((cell.x, cell.y), self.prior_collapse)
        return current * (1.0 - AI.BAYESIAN_UPDATE_RATE) + collapse_prob * AI.BAYESIAN_UPDATE_RATE
    
    def get_risk(self, position: Tuple[int, int], risk_type: str = "combined") -> float:
        """
        Get risk estimate for a position.
        
        Args:
            position: Cell coordinates
            risk_type: "fire", "flood", "collapse", or "combined"
            
        Returns:
            Risk probability [0.0, 1.0]
        """
        if risk_type == "fire":
            return self.fire_risk.get(position, self.prior_fire)
        elif risk_type == "flood":
            return self.flood_risk.get(position, self.prior_flood)
        elif risk_type == "collapse":
            return self.collapse_risk.get(position, self.prior_collapse)
        else:  # combined
            # Combined risk: probability of at least one hazard
            # P(A ∪ B ∪ C) ≈ 1 - (1-P(A))(1-P(B))(1-P(C))
            fire = self.fire_risk.get(position, self.prior_fire)
            flood = self.flood_risk.get(position, self.prior_flood)
            collapse = self.collapse_risk.get(position, self.prior_collapse)
            return 1.0 - (1.0 - fire) * (1.0 - flood) * (1.0 - collapse)
    
    def get_all_risks(self, position: Tuple[int, int]) -> Dict[str, float]:
        """
        Get all risk values for a position.
        
        Args:
            position: Cell coordinates
            
        Returns:
            Dictionary with all risk types
        """
        return {
            "fire": self.get_risk(position, "fire"),
            "flood": self.get_risk(position, "flood"),
            "collapse": self.get_risk(position, "collapse"),
            "combined": self.get_risk(position, "combined")
        }
    
    def get_confidence(self, position: Tuple[int, int]) -> float:
        """
        Get confidence in risk estimate based on observation count.
        
        Args:
            position: Cell coordinates
            
        Returns:
            Confidence value [0.0, 1.0]
            
        Rationale:
            More observations = higher confidence
            Use sigmoid function for smooth interpolation
        """
        count = self.observation_count.get(position, 0)
        # Sigmoid: confidence approaches 1.0 as observations increase
        return 1.0 - math.exp(-count / 5.0)
    
    def get_risk_gradient(self, position: Tuple[int, int], grid) -> Tuple[float, float]:
        """
        Compute risk gradient (direction of increasing risk).
        
        Args:
            position: Current position
            grid: Grid object for neighbor access
            
        Returns:
            (dx, dy) gradient vector
            
        Use case:
            Agents can move away from risk gradient
            Useful for exploration and evasive maneuvering
        """
        x, y = position
        neighbors = grid.get_neighbors(x, y, diagonal=False)
        
        if not neighbors:
            return (0.0, 0.0)
        
        grad_x = 0.0
        grad_y = 0.0
        
        for nx, ny in neighbors:
            risk = self.get_risk((nx, ny), "combined")
            dx = nx - x
            dy = ny - y
            grad_x += risk * dx
            grad_y += risk * dy
        
        # Normalize
        magnitude = math.sqrt(grad_x**2 + grad_y**2)
        if magnitude > 0:
            grad_x /= magnitude
            grad_y /= magnitude
        
        return (grad_x, grad_y)
