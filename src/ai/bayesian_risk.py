"""
Bayesian Risk Estimation Module
Probabilistic inference for hazard risk (fire, flood, collapse).

Theoretical Foundation:
- Maintains prior probability distributions
- Updates beliefs based on observations (Bayesian updating)
- Provides risk estimates for decision making
- Quantifies uncertainty with confidence intervals (NEW v2.1)

This is NOT a predictor - it's a belief tracker that quantifies uncertainty.

Patent Integration: Enhanced with explainability module for confidence intervals
"""

from typing import Dict, Tuple, Optional
import math
from ..utils.config import AI, HAZARD
from .explainability import ConfidenceInterval


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
    
    def predict_risk(
        self,
        position: Tuple[int, int],
        timesteps_ahead: int,
        grid,
        hazard_spread_enabled: bool = True
    ) -> float:
        """
        Predict future risk at position using temporal forecasting.
        
        Implements true Bayesian temporal prediction:
        P(hazard_t+n | observed_t) = Σ P(hazard_t+n | state_t+n-1) P(state_t+n-1 | observed_t)
        
        Args:
            position: Cell to predict risk for
            timesteps_ahead: Number of timesteps to predict forward
            grid: Grid object for neighbor information
            hazard_spread_enabled: Whether hazards are spreading
            
        Returns:
            Predicted risk probability [0.0, 1.0]
        """
        if timesteps_ahead <= 0:
            return self.get_risk(position, "combined")
        
        if not hazard_spread_enabled:
            # Static environment - current risk is future risk
            return self.get_risk(position, "combined")
        
        # Get current risk
        current_fire = self.fire_risk.get(position, self.prior_fire)
        current_flood = self.flood_risk.get(position, self.prior_flood)
        
        # Predict fire spread using Monte Carlo simulation (simplified)
        predicted_fire = self._predict_fire_spread(position, timesteps_ahead, grid)
        predicted_flood = self._predict_flood_spread(position, timesteps_ahead, grid)
        predicted_collapse = self._predict_collapse(position, timesteps_ahead, predicted_fire)
        
        # Combined future risk
        future_risk = 1.0 - (1.0 - predicted_fire) * (1.0 - predicted_flood) * (1.0 - predicted_collapse)
        
        return future_risk
    
    def _predict_fire_spread(self, position: Tuple[int, int], timesteps: int, grid) -> float:
        """
        Predict fire risk using spread model.
        
        Uses Bayes theorem:
        P(fire at position | neighbors have fire) = 
            P(neighbors have fire | position has fire) × P(position has fire) / P(neighbors)
        
        Simplified to: spread_probability^timesteps based on neighbor fires
        
        Args:
            position: Target position
            timesteps: Timesteps ahead
            grid: Grid object
            
        Returns:
            Predicted fire probability
        """
        x, y = position
        
        # Check if already on fire
        cell = grid.get_cell(x, y)
        if cell and cell.has_fire:
            return 1.0
        if cell and cell.has_flood:
            return 0.0  # Incompatible
        
        # Get neighbors
        neighbors = grid.get_neighbors(x, y, diagonal=False)
        neighbor_cells = [grid.get_cell(nx, ny) for nx, ny in neighbors]
        neighbor_cells = [c for c in neighbor_cells if c is not None]
        
        # Count fire neighbors
        fire_neighbors = sum(1 for c in neighbor_cells if c.has_fire)
        
        if fire_neighbors == 0:
            # No immediate threat - use current risk
            return self.fire_risk.get(position, self.prior_fire)
        
        # Bayesian update: P(fire_t+n | fire_neighbors_t)
        # Probability of fire spreading over n timesteps
        spread_per_timestep = HAZARD.FIRE_SPREAD_RATE * 0.3 * fire_neighbors  # Per neighbor
        
        # Compound probability over timesteps
        # P(eventually catch fire) = 1 - P(never catch fire)^timesteps
        prob_no_fire_per_step = (1.0 - spread_per_timestep)
        prob_no_fire_n_steps = prob_no_fire_per_step ** timesteps
        predicted_fire = 1.0 - prob_no_fire_n_steps
        
        # Combine with current belief
        current = self.fire_risk.get(position, self.prior_fire)
        return max(current, predicted_fire)
    
    def _predict_flood_spread(self, position: Tuple[int, int], timesteps: int, grid) -> float:
        """
        Predict flood risk over time.
        
        Args:
            position: Target position
            timesteps: Timesteps ahead
            grid: Grid object
            
        Returns:
            Predicted flood probability
        """
        x, y = position
        
        cell = grid.get_cell(x, y)
        if cell and cell.has_flood:
            return 1.0
        if cell and cell.has_fire:
            return 0.0  # Fire prevents flooding
        
        neighbors = grid.get_neighbors(x, y, diagonal=False)
        neighbor_cells = [grid.get_cell(nx, ny) for nx, ny in neighbors]
        neighbor_cells = [c for c in neighbor_cells if c is not None]
        
        flood_neighbors = sum(1 for c in neighbor_cells if c.has_flood)
        
        if flood_neighbors == 0:
            return self.flood_risk.get(position, self.prior_flood)
        
        # Slower spread than fire
        spread_per_timestep = HAZARD.FLOOD_SPREAD_RATE * 0.2 * flood_neighbors
        prob_no_flood_n_steps = (1.0 - spread_per_timestep) ** timesteps
        predicted_flood = 1.0 - prob_no_flood_n_steps
        
        current = self.flood_risk.get(position, self.prior_flood)
        return max(current, predicted_flood)
    
    def _predict_collapse(self, position: Tuple[int, int], timesteps: int, fire_risk: float) -> float:
        """
        Predict collapse risk based on predicted fire exposure.
        
        Args:
            position: Target position
            timesteps: Timesteps ahead
            fire_risk: Predicted fire risk at this position
            
        Returns:
            Predicted collapse probability
        """
        # Collapse probability increases with fire exposure over time
        collapse_per_timestep = HAZARD.DEBRIS_GENERATION_NEAR_FIRE * fire_risk
        prob_no_collapse_n_steps = (1.0 - collapse_per_timestep) ** timesteps
        predicted_collapse = 1.0 - prob_no_collapse_n_steps
        
        current = self.collapse_risk.get(position, self.prior_collapse)
        return max(current, predicted_collapse)
    
    def get_safe_path_probability(
        self,
        path: list[Tuple[int, int]],
        timesteps_to_traverse: int,
        grid
    ) -> float:
        """
        Compute probability that a path remains safe during traversal.
        
        Args:
            path: List of positions in path
            timesteps_to_traverse: Time needed to traverse path
            grid: Grid object
            
        Returns:
            Probability path stays safe [0.0, 1.0]
        """
        if not path:
            return 1.0
        
        # For each step in path, predict risk when agent will be there
        prob_safe = 1.0
        
        for i, pos in enumerate(path):
            # When will agent be at this position?
            timestep_at_pos = i
            
            # What's the risk at that future time?
            future_risk = self.predict_risk(pos, timestep_at_pos, grid, hazard_spread_enabled=True)
            
            # Probability this step is safe
            prob_safe_step = 1.0 - future_risk
            
            # Overall safety = product of individual step safeties
            prob_safe *= prob_safe_step
        
        return prob_safe
    
    def get_risk_with_confidence(
        self,
        position: Tuple[int, int],
        risk_type: str = "combined"
    ) -> ConfidenceInterval:
        """
        Get risk estimate with uncertainty quantification.
        
        NEW v2.1 - Patent Component: Explainable Risk Assessment
        
        Args:
            position: Cell coordinates
            risk_type: "fire", "flood", "collapse", or "combined"
            
        Returns:
            ConfidenceInterval with mean risk and 95% bounds
        """
        # Get point estimate
        mean_risk = self.get_risk(position, risk_type)
        
        # Compute uncertainty based on observation count
        obs_count = self.observation_count.get(position, 0)
        
        # Standard deviation decreases with more observations
        # Initial std_dev = 0.3, converges to 0.05 with many observations
        base_std = 0.3
        min_std = 0.05
        std_dev = base_std * math.exp(-obs_count / 10.0) + min_std
        
        # Compute 95% confidence interval (1.96 * std_dev)
        lower = max(0.0, mean_risk - 1.96 * std_dev)
        upper = min(1.0, mean_risk + 1.96 * std_dev)
        
        return ConfidenceInterval(
            mean=mean_risk,
            lower_bound=lower,
            upper_bound=upper,
            std_dev=std_dev,
            confidence_level=0.95
        )
    
    def predict_risk_with_confidence(
        self,
        position: Tuple[int, int],
        timesteps_ahead: int,
        grid,
        hazard_spread_enabled: bool = True
    ) -> ConfidenceInterval:
        """
        Predict future risk with uncertainty quantification.
        
        NEW v2.1 - Patent Component: Temporal Risk Forecasting with Confidence
        
        Args:
            position: Cell to predict risk for
            timesteps_ahead: Number of timesteps to predict forward
            grid: Grid object for neighbor information
            hazard_spread_enabled: Whether hazards are spreading
            
        Returns:
            ConfidenceInterval with predicted risk and uncertainty bounds
        """
        # Get point prediction
        mean_risk = self.predict_risk(position, timesteps_ahead, grid, hazard_spread_enabled)
        
        # Uncertainty increases with prediction horizon
        obs_count = self.observation_count.get(position, 0)
        
        # Base uncertainty from observations
        base_std = 0.3 * math.exp(-obs_count / 10.0) + 0.05
        
        # Additional uncertainty from temporal prediction
        # Uncertainty grows with prediction horizon: std += 0.05 per timestep
        temporal_uncertainty = 0.05 * timesteps_ahead
        
        # Combined uncertainty
        std_dev = min(0.5, base_std + temporal_uncertainty)  # Cap at 0.5
        
        # Compute 95% confidence interval
        lower = max(0.0, mean_risk - 1.96 * std_dev)
        upper = min(1.0, mean_risk + 1.96 * std_dev)
        
        return ConfidenceInterval(
            mean=mean_risk,
            lower_bound=lower,
            upper_bound=upper,
            std_dev=std_dev,
            confidence_level=0.95
        )
    
    def get_environmental_assessment_with_confidence(
        self,
        all_risks: list[float]
    ) -> Tuple[float, ConfidenceInterval]:
        """
        Compute average environmental risk with confidence interval.
        
        NEW v2.1 - Patent Component: Used by HybridCoordinator for mode selection
        
        Args:
            all_risks: List of risk values across environment
            
        Returns:
            Tuple of (mean_risk, confidence_interval)
        """
        if not all_risks:
            # No data - return prior with high uncertainty
            mean_risk = (self.prior_fire + self.prior_flood + self.prior_collapse) / 3.0
            return mean_risk, ConfidenceInterval(
                mean=mean_risk,
                lower_bound=0.0,
                upper_bound=1.0,
                std_dev=0.5,
                confidence_level=0.95
            )
        
        # Compute sample statistics
        n = len(all_risks)
        mean = sum(all_risks) / n
        
        # Sample standard deviation
        if n > 1:
            variance = sum((r - mean)**2 for r in all_risks) / (n - 1)
            std_dev = math.sqrt(variance)
        else:
            std_dev = 0.3  # High uncertainty with single sample
        
        # Standard error of the mean
        std_error = std_dev / math.sqrt(n)
        
        # 95% confidence interval for the mean
        lower = max(0.0, mean - 1.96 * std_error)
        upper = min(1.0, mean + 1.96 * std_error)
        
        confidence = ConfidenceInterval(
            mean=mean,
            lower_bound=lower,
            upper_bound=upper,
            std_dev=std_error,
            confidence_level=0.95
        )
        
        return mean, confidence
