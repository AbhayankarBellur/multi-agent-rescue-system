"""
Hybrid Coordination Protocol Selector

This is the CORE PATENT NOVELTY: Dynamic protocol switching based on
environmental risk assessment and task complexity.

Coordination Modes:
1. CENTRALIZED (Low uncertainty): Fast greedy CSP allocation
2. AUCTION (Moderate uncertainty): Contract Net Protocol with bidding
3. COALITION (High risk): Multi-agent team formation for complex tasks

The system monitors environmental conditions and automatically switches
between coordination protocols to optimize performance under uncertainty.

Author: Enhanced Multi-Agent System
Date: February 2026
"""

from enum import Enum
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
import statistics
from .explainability import ExplanationEngine, DecisionExplanation


class CoordinationMode(Enum):
    """Coordination protocol options."""
    CENTRALIZED = "centralized"  # Greedy CSP allocation
    AUCTION = "auction"           # Contract Net Protocol
    COALITION = "coalition"       # Risk-aware team formation
    HYBRID = "hybrid"             # Automatic mode switching


@dataclass
class EnvironmentalAssessment:
    """
    Environmental state assessment for protocol selection.
    
    Attributes:
        avg_risk: Average risk across all positions
        max_risk: Maximum risk level
        risk_variance: Variance in risk distribution
        task_count: Number of active tasks
        agent_count: Number of available agents
        task_complexity: Estimated task difficulty
        exploration_coverage: Percentage of grid explored
    """
    avg_risk: float
    max_risk: float
    risk_variance: float
    task_count: int
    agent_count: int
    task_complexity: float
    exploration_coverage: float
    
    def uncertainty_level(self) -> str:
        """
        Classify environmental uncertainty.
        
        Returns:
            "LOW", "MODERATE", or "HIGH"
        """
        if self.avg_risk < 0.3 and self.risk_variance < 0.1:
            return "LOW"
        elif self.avg_risk < 0.6 and self.max_risk < 0.8:
            return "MODERATE"
        else:
            return "HIGH"
    
    def recommended_mode(self) -> CoordinationMode:
        """
        Recommend coordination mode based on assessment.
        
        Decision Logic:
        - LOW uncertainty: CENTRALIZED (fast, deterministic)
        - MODERATE uncertainty: AUCTION (flexible, adaptive)
        - HIGH uncertainty: COALITION (collaborative, robust)
        
        Returns:
            Recommended CoordinationMode
        """
        uncertainty = self.uncertainty_level()
        
        if uncertainty == "LOW":
            return CoordinationMode.CENTRALIZED
        elif uncertainty == "MODERATE":
            return CoordinationMode.AUCTION
        else:
            return CoordinationMode.COALITION


class HybridCoordinator:
    """
    Adaptive coordination protocol manager.
    
    Monitors environmental conditions and selects optimal coordination
    protocol. This is the patent-worthy innovation - dynamic switching
    between centralized, auction, and coalition modes.
    """
    
    def __init__(self, csp_allocator, communication_network=None, enable_explanations=True):
        """
        Initialize hybrid coordinator.
        
        Args:
            csp_allocator: CSPAllocator instance
            communication_network: Communication network (optional)
            enable_explanations: Enable explainability features (NEW v2.1)
        """
        self.csp_allocator = csp_allocator
        self.communication_network = communication_network
        self.current_mode = CoordinationMode.CENTRALIZED
        self.mode_history: List[Tuple[int, CoordinationMode, str]] = []
        
        # Performance tracking
        self.mode_performance: Dict[CoordinationMode, List[float]] = {
            CoordinationMode.CENTRALIZED: [],
            CoordinationMode.AUCTION: [],
            CoordinationMode.COALITION: []
        }
        
        # NEW v2.1: Explainability engine for decision transparency
        self.explanation_engine = ExplanationEngine(enable_logging=enable_explanations) if enable_explanations else None
        self.last_explanation: Optional[DecisionExplanation] = None
    
    def assess_environment(
        self,
        risk_model,
        survivors: List[Tuple[int, int]],
        agents: Dict[str, Any],
        grid
    ) -> Tuple[EnvironmentalAssessment, Optional[Any]]:
        """
        Assess current environmental conditions with uncertainty quantification.
        
        ENHANCED v2.1: Now returns confidence intervals for risk assessment
        
        Args:
            risk_model: Bayesian risk model
            survivors: List of survivor positions
            agents: Agent information
            grid: Environment grid
            
        Returns:
            Tuple of (EnvironmentalAssessment, confidence_interval)
        """
        # Compute risk statistics with confidence intervals (NEW v2.1)
        risk_values = []
        for survivor_pos in survivors:
            risk = risk_model.get_risk(survivor_pos, "combined")
            risk_values.append(risk)
        
        # Get confidence interval for average risk
        if risk_values and hasattr(risk_model, 'get_environmental_assessment_with_confidence'):
            avg_risk, confidence_interval = risk_model.get_environmental_assessment_with_confidence(risk_values)
            max_risk = max(risk_values)
            risk_variance = statistics.variance(risk_values) if len(risk_values) > 1 else 0.0
        elif risk_values:
            avg_risk = statistics.mean(risk_values)
            max_risk = max(risk_values)
            risk_variance = statistics.variance(risk_values) if len(risk_values) > 1 else 0.0
            confidence_interval = None
        else:
            avg_risk = 0.0
            max_risk = 0.0
            risk_variance = 0.0
            confidence_interval = None
        
        # Count agents
        rescue_agent_count = sum(
            1 for info in agents.values() 
            if info.get('type') == 'RESCUE'
        )
        
        # Estimate task complexity
        task_complexity = self._estimate_task_complexity(
            survivors, agents, risk_model
        )
        
        # Compute exploration coverage
        explored_cells = sum(
            1 for info in agents.values()
            for cell in info.get('explored_cells', set())
        )
        total_cells = grid.width * grid.height
        exploration_coverage = explored_cells / total_cells if total_cells > 0 else 0.0
        
        assessment = EnvironmentalAssessment(
            avg_risk=avg_risk,
            max_risk=max_risk,
            risk_variance=risk_variance,
            task_count=len(survivors),
            agent_count=rescue_agent_count,
            task_complexity=task_complexity,
            exploration_coverage=exploration_coverage
        )
        
        return assessment, confidence_interval
    
    def select_mode(
        self,
        assessment: EnvironmentalAssessment,
        timestep: int,
        force_mode: Optional[CoordinationMode] = None,
        risk_confidence=None
    ) -> CoordinationMode:
        """
        Select coordination mode based on environmental assessment.
        
        ENHANCED v2.1: Generates natural language explanations for mode switches
        
        Args:
            assessment: Environmental assessment
            timestep: Current simulation timestep
            force_mode: Override automatic selection (for testing)
            risk_confidence: ConfidenceInterval for risk (NEW v2.1)
            
        Returns:
            Selected CoordinationMode
        """
        if force_mode and force_mode != CoordinationMode.HYBRID:
            selected = force_mode
            reason = "User-specified mode"
        else:
            selected = assessment.recommended_mode()
            reason = f"Uncertainty: {assessment.uncertainty_level()}, Risk: {assessment.avg_risk:.2f}"
        
        # Log mode change
        if selected != self.current_mode:
            self.mode_history.append((timestep, selected, reason))
            
            # NEW v2.1: Generate explanation for mode switch
            if self.explanation_engine:
                old_mode_str = self.current_mode.value.upper() if self.current_mode else "NONE"
                new_mode_str = selected.value.upper()
                
                # Get risk statistics for explanation
                if risk_confidence:
                    risk_std = risk_confidence.std_dev
                else:
                    risk_std = assessment.risk_variance ** 0.5  # Convert variance to std dev
                
                explanation = self.explanation_engine.explain_mode_switch(
                    old_mode=old_mode_str,
                    new_mode=new_mode_str,
                    avg_risk=assessment.avg_risk,
                    risk_std=risk_std,
                    timestamp=timestep
                )
                
                self.last_explanation = explanation
        
        self.current_mode = selected
        return selected
    
    def allocate_tasks(
        self,
        mode: CoordinationMode,
        agents: Dict[str, Dict],
        survivors: List[Tuple[int, int]],
        risk_model,
        distance_func,
        current_allocation: Optional[Dict[str, List[Tuple[int, int]]]] = None
    ) -> Dict[str, List[Tuple[int, int]]]:
        """
        Allocate tasks using selected coordination mode.
        
        Args:
            mode: Coordination mode to use
            agents: Agent information
            survivors: Survivor positions
            risk_model: Risk model
            distance_func: Distance function
            current_allocation: Existing allocation (for reallocation)
            
        Returns:
            Task allocation mapping
        """
        if mode == CoordinationMode.CENTRALIZED:
            # Standard greedy CSP
            return self.csp_allocator.allocate(
                agents, survivors, risk_model, distance_func
            )
        
        elif mode == CoordinationMode.AUCTION:
            # Auction-based allocation with potential reallocation
            if current_allocation:
                # Iterative auction for reallocation
                return self.csp_allocator.allocate_iterative_auction(
                    agents, survivors, risk_model, distance_func, current_allocation
                )
            else:
                # Single-round auction
                return self.csp_allocator.allocate_auction(
                    agents, survivors, risk_model, distance_func,
                    self.communication_network
                )
        
        elif mode == CoordinationMode.COALITION:
            # Coalition formation for high-risk scenarios
            return self._allocate_with_coalitions(
                agents, survivors, risk_model, distance_func
            )
        
        else:
            # Fallback to centralized
            return self.csp_allocator.allocate(
                agents, survivors, risk_model, distance_func
            )
    
    def _estimate_task_complexity(
        self,
        survivors: List[Tuple[int, int]],
        agents: Dict[str, Any],
        risk_model
    ) -> float:
        """
        Estimate overall task complexity.
        
        Complexity factors:
        - Number of survivors vs agents
        - Average risk level
        - Spatial distribution of survivors
        
        Args:
            survivors: Survivor positions
            agents: Agent information
            risk_model: Risk model
            
        Returns:
            Complexity score [0.0, 1.0]
        """
        if not survivors:
            return 0.0
        
        # Factor 1: Task overload
        rescue_agents = [a for a in agents.values() if a.get('type') == 'RESCUE']
        if rescue_agents:
            overload_ratio = len(survivors) / len(rescue_agents)
            overload_score = min(overload_ratio / 5.0, 1.0)  # Normalize to [0,1]
        else:
            overload_score = 1.0
        
        # Factor 2: Average risk
        risks = [risk_model.get_risk(pos, "combined") for pos in survivors]
        avg_risk = statistics.mean(risks) if risks else 0.0
        
        # Factor 3: Spatial dispersion
        if len(survivors) > 1:
            # Compute pairwise distances
            distances = []
            for i, pos1 in enumerate(survivors):
                for pos2 in survivors[i+1:]:
                    dist = abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
                    distances.append(dist)
            dispersion_score = min(statistics.mean(distances) / 50.0, 1.0)
        else:
            dispersion_score = 0.0
        
        # Weighted combination
        complexity = (
            0.4 * overload_score +
            0.4 * avg_risk +
            0.2 * dispersion_score
        )
        
        return min(complexity, 1.0)
    
    def _allocate_with_coalitions(
        self,
        agents: Dict[str, Dict],
        survivors: List[Tuple[int, int]],
        risk_model,
        distance_func
    ) -> Dict[str, List[Tuple[int, int]]]:
        """
        Allocate tasks with coalition formation for high-risk scenarios.
        
        Strategy:
        1. Identify high-risk survivors (risk > 0.7)
        2. Assign rescue + support agent pairs (coalitions)
        3. Assign low-risk survivors normally
        
        Args:
            agents: Agent information
            survivors: Survivor positions
            risk_model: Risk model
            distance_func: Distance function
            
        Returns:
            Coalition-aware allocation
        """
        rescue_agents = {
            aid: info for aid, info in agents.items()
            if info.get('type') == 'RESCUE'
        }
        
        support_agents = {
            aid: info for aid, info in agents.items()
            if info.get('type') == 'SUPPORT'
        }
        
        allocation: Dict[str, List[Tuple[int, int]]] = {
            aid: [] for aid in agents.keys() if agents[aid].get('type') in ['RESCUE', 'SUPPORT']
        }
        
        # Classify survivors by risk
        high_risk_survivors = []
        normal_survivors = []
        
        for survivor_pos in survivors:
            risk = risk_model.get_risk(survivor_pos, "combined")
            if risk > 0.7:
                high_risk_survivors.append(survivor_pos)
            else:
                normal_survivors.append(survivor_pos)
        
        # Allocate high-risk with coalitions
        support_allocated = set()
        for survivor_pos in high_risk_survivors:
            # Find closest rescue agent
            best_rescue = None
            best_rescue_dist = float('inf')
            
            for agent_id, agent_info in rescue_agents.items():
                if len(allocation[agent_id]) >= self.csp_allocator.max_survivors_per_agent:
                    continue
                dist = distance_func(agent_info['position'], survivor_pos)
                if dist < best_rescue_dist:
                    best_rescue_dist = dist
                    best_rescue = agent_id
            
            if best_rescue:
                allocation[best_rescue].append(survivor_pos)
                
                # Assign support agent to assist
                for support_id, support_info in support_agents.items():
                    if support_id not in support_allocated:
                        # Mark support agent as assisting this rescue
                        allocation[support_id].append(survivor_pos)
                        support_allocated.add(support_id)
                        break
        
        # Allocate normal risk survivors using standard auction
        if normal_survivors:
            normal_allocation = self.csp_allocator.allocate_auction(
                {aid: info for aid, info in agents.items() if info.get('type') == 'RESCUE'},
                normal_survivors,
                risk_model,
                distance_func
            )
            
            # Merge allocations
            for agent_id, survivor_list in normal_allocation.items():
                if agent_id in allocation:
                    allocation[agent_id].extend(survivor_list)
        
        return allocation
    
    def get_coordination_stats(self) -> Dict[str, Any]:
        """
        Get coordination statistics.
        
        Returns:
            Dictionary with coordination metrics
        """
        mode_counts = {}
        for _, mode, _ in self.mode_history:
            mode_counts[mode.value] = mode_counts.get(mode.value, 0) + 1
        
        return {
            'current_mode': self.current_mode.value,
            'mode_switches': len(self.mode_history),
            'mode_distribution': mode_counts,
            'mode_history': [
                (ts, mode.value, reason) 
                for ts, mode, reason in self.mode_history
            ]
        }
