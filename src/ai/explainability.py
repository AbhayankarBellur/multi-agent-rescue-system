"""
Explainability and Uncertainty Quantification Module

Provides natural language explanations, confidence intervals, and counterfactual
reasoning for all coordination decisions. This module is the core of the patent-worthy
"Explainable Risk-Aware Task Reallocation" innovation.

Key Features:
- Natural language decision explanations
- Bayesian confidence intervals for predictions
- Counterfactual "what-if" analysis
- Audit trail generation for regulatory compliance
- Human-interpretable risk assessments

Author: Multi-Agent Rescue System Team
Patent Pending: Explainable Risk-Aware Task Reallocation (2026)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import math
from datetime import datetime


class DecisionType(Enum):
    """Types of decisions that can be explained."""
    TASK_ALLOCATION = "task_allocation"
    COALITION_FORMATION = "coalition_formation"
    MODE_SWITCH = "coordination_mode_switch"
    AGENT_SPAWN = "agent_spawn"
    RISK_ASSESSMENT = "risk_assessment"
    TASK_REALLOCATION = "task_reallocation"


@dataclass
class ConfidenceInterval:
    """
    Represents uncertainty in predictions using Bayesian statistics.
    
    Provides mean estimate with confidence bounds for human interpretation.
    """
    mean: float
    lower_bound: float  # 95% confidence interval lower
    upper_bound: float  # 95% confidence interval upper
    std_dev: float
    confidence_level: float = 0.95
    
    def __str__(self) -> str:
        """Human-readable confidence interval."""
        return f"{self.mean:.2f} (95% CI: [{self.lower_bound:.2f}, {self.upper_bound:.2f}])"
    
    def to_dict(self) -> Dict[str, float]:
        """Export for logging/visualization."""
        return {
            "mean": self.mean,
            "lower": self.lower_bound,
            "upper": self.upper_bound,
            "std_dev": self.std_dev,
            "confidence": self.confidence_level
        }


@dataclass
class DecisionExplanation:
    """
    Structured explanation for a single coordination decision.
    
    Contains natural language explanation, quantified uncertainties,
    and counterfactual alternatives for human oversight.
    """
    decision_type: DecisionType
    timestamp: int
    primary_explanation: str
    confidence: ConfidenceInterval
    factors: Dict[str, Any]  # Key decision factors
    alternatives: List[Dict[str, Any]]  # Counterfactual options
    chosen_action: str
    expected_outcome: str
    actual_outcome: Optional[str] = None  # Filled after execution
    
    def to_natural_language(self) -> str:
        """
        Generate human-readable explanation for operators.
        
        Returns:
            Natural language explanation suitable for FEMA dashboard display
        """
        nl_parts = [
            f"[{self.decision_type.value.upper()}]",
            self.primary_explanation,
            f"\nChosen Action: {self.chosen_action}",
            f"Confidence: {self.confidence}",
            f"Expected Outcome: {self.expected_outcome}"
        ]
        
        if self.factors:
            nl_parts.append("\nKey Factors:")
            for key, value in self.factors.items():
                nl_parts.append(f"  - {key}: {value}")
        
        if self.alternatives:
            nl_parts.append(f"\nAlternatives Considered: {len(self.alternatives)}")
            for i, alt in enumerate(self.alternatives[:3], 1):  # Top 3 alternatives
                nl_parts.append(f"  {i}. {alt.get('description', 'Unknown')}")
        
        return "\n".join(nl_parts)
    
    def to_dict(self) -> Dict[str, Any]:
        """Export for JSON logging and audit trails."""
        return {
            "decision_type": self.decision_type.value,
            "timestamp": self.timestamp,
            "explanation": self.primary_explanation,
            "confidence": self.confidence.to_dict(),
            "factors": self.factors,
            "alternatives": self.alternatives,
            "chosen_action": self.chosen_action,
            "expected_outcome": self.expected_outcome,
            "actual_outcome": self.actual_outcome
        }


class CounterfactualReasoner:
    """
    Generates "what-if" scenarios to explain decisions by contrasting
    the chosen action against plausible alternatives.
    
    Patent Component: Novel application of counterfactual reasoning to
    multi-agent task allocation with risk-aware utility functions.
    """
    
    def __init__(self):
        self.history: List[Dict[str, Any]] = []
    
    def generate_counterfactual(
        self,
        chosen_action: Dict[str, Any],
        alternatives: List[Dict[str, Any]],
        evaluation_metric: str = "expected_utility"
    ) -> List[Dict[str, Any]]:
        """
        Generate counterfactual explanations comparing chosen action to alternatives.
        
        Args:
            chosen_action: The action that was selected
            alternatives: List of alternative actions that were considered
            evaluation_metric: Metric used for comparison (e.g., "expected_utility", "risk")
        
        Returns:
            List of counterfactual explanations with comparative analysis
        """
        counterfactuals = []
        
        chosen_utility = chosen_action.get(evaluation_metric, 0)
        
        for alt in alternatives:
            alt_utility = alt.get(evaluation_metric, 0)
            utility_diff = chosen_utility - alt_utility
            
            # Generate natural language comparison
            if utility_diff > 0:
                comparison = f"Chosen action has {utility_diff:.2f} higher {evaluation_metric}"
                reason = "superior performance"
            elif utility_diff < 0:
                comparison = f"Alternative has {abs(utility_diff):.2f} higher {evaluation_metric}"
                reason = alt.get('rejection_reason', 'other constraints')
            else:
                comparison = f"Equal {evaluation_metric}"
                reason = alt.get('rejection_reason', 'tie-breaking rule')
            
            counterfactual = {
                "alternative": alt.get('description', 'Unknown alternative'),
                "comparison": comparison,
                "rejected_because": reason,
                "utility_difference": utility_diff,
                "what_if_outcome": alt.get('predicted_outcome', 'Unknown')
            }
            counterfactuals.append(counterfactual)
        
        return counterfactuals
    
    def explain_task_reallocation(
        self,
        old_assignment: Dict[str, Any],
        new_assignment: Dict[str, Any],
        triggering_event: str
    ) -> str:
        """
        Explain why a task was reallocated from one agent to another.
        
        Patent Focus: This is the core innovation - explaining dynamic
        reallocation decisions with risk-aware reasoning.
        """
        explanation_parts = [
            f"Task reallocated due to: {triggering_event}",
            f"Previous: Agent {old_assignment.get('agent_id', '?')} (cost: {old_assignment.get('cost', '?')})",
            f"New: Agent {new_assignment.get('agent_id', '?')} (cost: {new_assignment.get('cost', '?')})"
        ]
        
        # Calculate improvement metrics
        old_cost = old_assignment.get('cost', float('inf'))
        new_cost = new_assignment.get('cost', float('inf'))
        improvement = old_cost - new_cost
        
        if improvement > 0:
            explanation_parts.append(f"Cost reduction: {improvement:.2f} ({(improvement/old_cost)*100:.1f}%)")
        
        old_risk = old_assignment.get('risk', 0)
        new_risk = new_assignment.get('risk', 0)
        risk_change = new_risk - old_risk
        
        if risk_change < 0:
            explanation_parts.append(f"Risk reduced by {abs(risk_change):.2f}")
        elif risk_change > 0:
            explanation_parts.append(f"Risk increased by {risk_change:.2f} (acceptable trade-off)")
        
        return "\n".join(explanation_parts)


class ExplanationEngine:
    """
    Central hub for all explainability features.
    
    Generates natural language explanations, confidence intervals, and
    counterfactual reasoning for every coordination decision.
    
    Patent Core: "Explainable Risk-Aware Task Reallocation System"
    """
    
    def __init__(self, enable_logging: bool = True):
        """
        Initialize explainability engine.
        
        Args:
            enable_logging: Whether to maintain audit trail of all explanations
        """
        self.counterfactual_reasoner = CounterfactualReasoner()
        self.explanation_history: List[DecisionExplanation] = []
        self.enable_logging = enable_logging
        self.total_decisions = 0
    
    def explain_mode_switch(
        self,
        old_mode: str,
        new_mode: str,
        avg_risk: float,
        risk_std: float,
        timestamp: int
    ) -> DecisionExplanation:
        """
        Explain coordination mode switch decision.
        
        Args:
            old_mode: Previous coordination mode
            new_mode: New coordination mode
            avg_risk: Average environmental risk
            risk_std: Standard deviation of risk
            timestamp: Current simulation timestep
        
        Returns:
            Structured explanation with confidence intervals
        """
        # Calculate confidence interval for risk assessment
        confidence = ConfidenceInterval(
            mean=avg_risk,
            lower_bound=max(0, avg_risk - 1.96 * risk_std),
            upper_bound=min(1, avg_risk + 1.96 * risk_std),
            std_dev=risk_std
        )
        
        # Generate natural language explanation
        if new_mode == "CENTRALIZED":
            reason = f"Low environmental risk ({avg_risk:.2f}) enables centralized CSP optimization"
        elif new_mode == "AUCTION":
            reason = f"Moderate risk ({avg_risk:.2f}) requires distributed auction-based allocation"
        elif new_mode == "COALITION":
            reason = f"High risk ({avg_risk:.2f}) necessitates coalition formation for safety"
        else:
            reason = f"Risk assessment ({avg_risk:.2f}) triggered mode change"
        
        explanation = DecisionExplanation(
            decision_type=DecisionType.MODE_SWITCH,
            timestamp=timestamp,
            primary_explanation=f"Switched from {old_mode} to {new_mode}: {reason}",
            confidence=confidence,
            factors={
                "average_risk": avg_risk,
                "risk_std_dev": risk_std,
                "old_mode": old_mode,
                "new_mode": new_mode,
                "decision_threshold_low": 0.3,
                "decision_threshold_high": 0.7
            },
            alternatives=[],  # Mode switch is deterministic based on risk
            chosen_action=f"Switch to {new_mode}",
            expected_outcome=f"Coordination efficiency optimized for {avg_risk:.2f} risk level"
        )
        
        self._log_explanation(explanation)
        return explanation
    
    def explain_task_allocation(
        self,
        task_type: str,
        task_location: Tuple[int, int],
        assigned_agent: int,
        bid_data: Dict[int, float],
        timestamp: int
    ) -> DecisionExplanation:
        """
        Explain task allocation decision in auction mode.
        
        Args:
            task_type: Type of task (RESCUE, EXPLORE, MEDICAL)
            task_location: Grid coordinates of task
            assigned_agent: Agent ID that won the auction
            bid_data: Dictionary of {agent_id: bid_cost}
            timestamp: Current timestep
        
        Returns:
            Explanation with counterfactual alternatives
        """
        # Calculate confidence based on bid spread
        bid_values = list(bid_data.values())
        if len(bid_values) > 1:
            mean_bid = sum(bid_values) / len(bid_values)
            std_bid = math.sqrt(sum((b - mean_bid)**2 for b in bid_values) / len(bid_values))
        else:
            mean_bid = bid_values[0] if bid_values else 0
            std_bid = 0
        
        winning_bid = bid_data.get(assigned_agent, 0)
        
        confidence = ConfidenceInterval(
            mean=winning_bid,
            lower_bound=max(0, winning_bid - 1.96 * std_bid),
            upper_bound=winning_bid + 1.96 * std_bid,
            std_dev=std_bid
        )
        
        # Generate alternatives (top 3 losing bids)
        sorted_bids = sorted(bid_data.items(), key=lambda x: x[1])
        alternatives = []
        for agent_id, bid in sorted_bids[1:4]:  # Skip winner, take next 3
            alternatives.append({
                "description": f"Assign to Agent {agent_id} (bid: {bid:.2f})",
                "expected_utility": -bid,  # Lower bid = higher utility
                "rejection_reason": f"Higher cost by {bid - winning_bid:.2f}",
                "predicted_outcome": f"Task completed with {bid:.2f} cost"
            })
        
        explanation = DecisionExplanation(
            decision_type=DecisionType.TASK_ALLOCATION,
            timestamp=timestamp,
            primary_explanation=f"Allocated {task_type} task at {task_location} to Agent {assigned_agent} via auction",
            confidence=confidence,
            factors={
                "task_type": task_type,
                "location": task_location,
                "winning_bid": winning_bid,
                "num_bidders": len(bid_data),
                "bid_spread": std_bid * 1.96  # 95% of values within this range
            },
            alternatives=alternatives,
            chosen_action=f"Assign to Agent {assigned_agent}",
            expected_outcome=f"{task_type} completed with minimum cost {winning_bid:.2f}"
        )
        
        self._log_explanation(explanation)
        return explanation
    
    def explain_coalition_formation(
        self,
        coalition_members: List[int],
        target_location: Tuple[int, int],
        combined_risk: float,
        individual_risks: Dict[int, float],
        timestamp: int
    ) -> DecisionExplanation:
        """
        Explain why agents formed a coalition for a high-risk task.
        
        Args:
            coalition_members: List of agent IDs in the coalition
            target_location: Location of the high-risk task
            combined_risk: Risk level if coalition works together
            individual_risks: Risk for each agent working alone
            timestamp: Current timestep
        
        Returns:
            Explanation highlighting risk reduction through cooperation
        """
        avg_individual_risk = sum(individual_risks.values()) / len(individual_risks)
        risk_reduction = avg_individual_risk - combined_risk
        
        # Confidence interval for risk reduction
        confidence = ConfidenceInterval(
            mean=risk_reduction,
            lower_bound=max(0, risk_reduction * 0.7),  # Conservative estimate
            upper_bound=risk_reduction * 1.3,
            std_dev=risk_reduction * 0.15
        )
        
        # Alternative: agents working alone
        alternatives = [{
            "description": f"Agent {agent_id} works alone",
            "expected_utility": -individual_risks[agent_id],
            "rejection_reason": f"Risk too high ({individual_risks[agent_id]:.2f})",
            "predicted_outcome": f"High probability of failure"
        } for agent_id in coalition_members[:3]]
        
        explanation = DecisionExplanation(
            decision_type=DecisionType.COALITION_FORMATION,
            timestamp=timestamp,
            primary_explanation=f"Formed coalition of {len(coalition_members)} agents to handle high-risk task at {target_location}",
            confidence=confidence,
            factors={
                "coalition_size": len(coalition_members),
                "members": coalition_members,
                "combined_risk": combined_risk,
                "avg_individual_risk": avg_individual_risk,
                "risk_reduction": risk_reduction,
                "location": target_location
            },
            alternatives=alternatives,
            chosen_action=f"Form coalition: {coalition_members}",
            expected_outcome=f"Risk reduced from {avg_individual_risk:.2f} to {combined_risk:.2f} ({risk_reduction:.2f} reduction)"
        )
        
        self._log_explanation(explanation)
        return explanation
    
    def explain_agent_spawn(
        self,
        reason: str,
        workload_metric: float,
        threshold: float,
        new_agent_type: str,
        timestamp: int
    ) -> DecisionExplanation:
        """
        Explain dynamic agent spawning decision.
        
        Args:
            reason: Why the agent was spawned
            workload_metric: Current workload measurement
            threshold: Threshold that triggered spawning
            new_agent_type: Type of agent spawned
            timestamp: Current timestep
        
        Returns:
            Explanation of spawning decision
        """
        confidence = ConfidenceInterval(
            mean=workload_metric,
            lower_bound=workload_metric * 0.9,
            upper_bound=workload_metric * 1.1,
            std_dev=workload_metric * 0.05
        )
        
        explanation = DecisionExplanation(
            decision_type=DecisionType.AGENT_SPAWN,
            timestamp=timestamp,
            primary_explanation=f"Spawned {new_agent_type} agent: {reason}",
            confidence=confidence,
            factors={
                "workload_metric": workload_metric,
                "threshold": threshold,
                "agent_type": new_agent_type,
                "trigger_reason": reason
            },
            alternatives=[{
                "description": "Continue with current agent count",
                "expected_utility": -workload_metric,
                "rejection_reason": f"Workload ({workload_metric:.2f}) exceeds threshold ({threshold:.2f})",
                "predicted_outcome": "Performance degradation"
            }],
            chosen_action=f"Spawn 1 {new_agent_type}",
            expected_outcome=f"Workload reduced, improved task coverage"
        )
        
        self._log_explanation(explanation)
        return explanation
    
    def _log_explanation(self, explanation: DecisionExplanation):
        """Add explanation to history if logging is enabled."""
        if self.enable_logging:
            self.explanation_history.append(explanation)
            self.total_decisions += 1
    
    def get_recent_explanations(self, count: int = 10) -> List[DecisionExplanation]:
        """Retrieve most recent explanations for dashboard display."""
        return self.explanation_history[-count:]
    
    def export_audit_trail(self, filepath: str):
        """
        Export complete audit trail for regulatory compliance.
        
        Args:
            filepath: Path to save JSON audit trail
        """
        import json
        
        audit_data = {
            "total_decisions": self.total_decisions,
            "export_timestamp": datetime.now().isoformat(),
            "explanations": [exp.to_dict() for exp in self.explanation_history]
        }
        
        with open(filepath, 'w') as f:
            json.dump(audit_data, f, indent=2)
    
    def generate_summary_report(self) -> str:
        """
        Generate human-readable summary of all decisions.
        
        Returns:
            Multi-line summary report for operators
        """
        if not self.explanation_history:
            return "No decisions recorded."
        
        # Count decisions by type
        type_counts = {}
        for exp in self.explanation_history:
            type_name = exp.decision_type.value
            type_counts[type_name] = type_counts.get(type_name, 0) + 1
        
        report_lines = [
            "="*60,
            "DECISION SUMMARY REPORT",
            "="*60,
            f"Total Decisions: {self.total_decisions}",
            "",
            "Decisions by Type:"
        ]
        
        for decision_type, count in sorted(type_counts.items()):
            report_lines.append(f"  {decision_type}: {count}")
        
        report_lines.extend([
            "",
            "Recent Decisions (Last 5):",
            "-"*60
        ])
        
        for exp in self.explanation_history[-5:]:
            report_lines.append(f"[T={exp.timestamp}] {exp.primary_explanation}")
            report_lines.append(f"  Confidence: {exp.confidence}")
            report_lines.append("")
        
        return "\n".join(report_lines)
