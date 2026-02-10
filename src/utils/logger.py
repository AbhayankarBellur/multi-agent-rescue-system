"""
Explainable Logging System
Provides comprehensive, timestep-based logging for full system traceability.
Every decision, calculation, and state change is recorded for academic review.
"""

import os
from datetime import datetime
from typing import Any, Dict, Optional, List
from ..utils.config import LOG


class SimulationLogger:
    """
    Central logging system for all simulation events.
    
    Logs include:
    - Agent perception and decisions
    - Risk estimations
    - Path planning details
    - Task allocations
    - Replanning rationale
    - Performance metrics
    
    Design principle: Full explainability - any reviewer should be able to
    understand WHY each agent made each decision at each timestep.
    """
    
    def __init__(self, log_file: Optional[str] = None):
        """
        Initialize logger.
        
        Args:
            log_file: Path to log file. If None, uses config default.
        """
        self.log_file = log_file or LOG.LOG_FILE_PATH
        self.console_enabled = LOG.LOG_TO_CONSOLE
        self.file_enabled = LOG.LOG_TO_FILE
        self.detail_level = LOG.LOG_LEVEL_DETAIL
        
        # Timestamped log entries
        self.entries: List[str] = []
        
        # Initialize log file
        if self.file_enabled:
            self._init_log_file()
    
    def _init_log_file(self):
        """Create/clear log file with header."""
        with open(self.log_file, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("AI DISASTER RESCUE SIMULATOR - EXECUTION LOG\n")
            f.write(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Detail Level: {self.detail_level}\n")
            f.write("=" * 80 + "\n\n")
    
    def _write(self, message: str, level: str = "NORMAL"):
        """
        Write message to log.
        
        Args:
            message: Log message
            level: MINIMAL, NORMAL, or VERBOSE
        """
        # Filter by detail level
        if level == "VERBOSE" and self.detail_level == "MINIMAL":
            return
        if level == "NORMAL" and self.detail_level == "MINIMAL":
            return
        
        # Add to memory
        self.entries.append(message)
        
        # Console output
        if self.console_enabled:
            print(message)
        
        # File output
        if self.file_enabled:
            with open(self.log_file, 'a') as f:
                f.write(message + "\n")
    
    def log_timestep(self, timestep: int, grid_state: Dict):
        """
        Log timestep boundary and environment state.
        
        Args:
            timestep: Current simulation timestep
            grid_state: Dictionary from Grid.get_grid_state_summary()
        """
        self._write("\n" + "=" * 80, "MINIMAL")
        self._write(f"TIMESTEP {timestep}", "MINIMAL")
        self._write("=" * 80, "MINIMAL")
        self._write(
            f"Environment: {grid_state['fires']} fires, {grid_state['floods']} floods, "
            f"{grid_state['debris']} debris, {grid_state['survivors']} survivors remaining",
            "NORMAL"
        )
    
    def log_agent_perception(self, agent_id: str, position: tuple, observations: Dict):
        """
        Log what an agent perceives.
        
        Args:
            agent_id: Agent identifier
            position: Current (x, y) position
            observations: Dictionary of perceived state
        """
        self._write(f"\n[{agent_id}] PERCEPTION at {position}:", "VERBOSE")
        for key, value in observations.items():
            self._write(f"  - {key}: {value}", "VERBOSE")
    
    def log_risk_estimation(self, agent_id: str, position: tuple, risk_values: Dict[str, float]):
        """
        Log Bayesian risk calculations.
        
        Args:
            agent_id: Agent identifier
            position: Position being evaluated
            risk_values: Dictionary of risk types and probabilities
        """
        self._write(
            f"[{agent_id}] RISK at {position}: " +
            ", ".join([f"{k}={v:.3f}" for k, v in risk_values.items()]),
            "VERBOSE"
        )
    
    def log_task_allocation(self, allocations: Dict[str, Any]):
        """
        Log CSP task allocation results.
        
        Args:
            allocations: Dictionary mapping agents to assigned tasks
        """
        self._write("\nCSP TASK ALLOCATION:", "NORMAL")
        for agent, task in allocations.items():
            self._write(f"  {agent} -> {task}", "NORMAL")
    
    def log_planning(self, agent_id: str, goal: str, plan: List[str], cost: float):
        """
        Log STRIPS planning output.
        
        Args:
            agent_id: Agent identifier
            goal: High-level goal description
            plan: List of action strings
            cost: Estimated plan cost
        """
        self._write(f"\n[{agent_id}] PLANNING for goal: {goal}", "NORMAL")
        self._write(f"  Plan (cost={cost:.2f}):", "NORMAL")
        for i, action in enumerate(plan, 1):
            self._write(f"    {i}. {action}", "VERBOSE")
    
    def log_pathfinding(self, agent_id: str, start: tuple, goal: tuple, 
                       path: List[tuple], cost: float, algorithm: str = "A*"):
        """
        Log pathfinding results.
        
        Args:
            agent_id: Agent identifier
            start: Starting position
            goal: Goal position
            path: List of waypoints
            cost: Total path cost
            algorithm: Algorithm used
        """
        self._write(
            f"[{agent_id}] {algorithm} PATH: {start} -> {goal}, "
            f"length={len(path)}, cost={cost:.2f}",
            "NORMAL"
        )
        if self.detail_level == "VERBOSE" and path:
            path_str = " -> ".join([f"({x},{y})" for x, y in path[:10]])
            if len(path) > 10:
                path_str += f" ... ({len(path)} total waypoints)"
            self._write(f"  Route: {path_str}", "VERBOSE")
    
    def log_action(self, agent_id: str, action: str, position: tuple, result: str):
        """
        Log action execution.
        
        Args:
            agent_id: Agent identifier
            action: Action taken
            position: Position where action occurred
            result: Outcome description
        """
        # Make result more readable
        if "Unknown action type" in result:
            result = "⚠️ Unhandled action"
        elif "Waiting at" in result:
            result = "Waiting"
        
        self._write(
            f"[{agent_id}] ACTION: {action} at {position} -> {result}",
            "NORMAL"
        )
    
    def log_replanning(self, agent_id: str, reason: str, old_plan: Optional[str], new_plan: str):
        """
        Log replanning event with rationale.
        
        Args:
            agent_id: Agent identifier
            reason: Why replanning was triggered
            old_plan: Previous plan (if any)
            new_plan: New plan
        """
        self._write(f"\n[{agent_id}] REPLANNING triggered:", "NORMAL")
        self._write(f"  Reason: {reason}", "NORMAL")
        if old_plan:
            self._write(f"  Old plan: {old_plan}", "VERBOSE")
        self._write(f"  New plan: {new_plan}", "NORMAL")
    
    def log_decision(self, agent_id: str, decision_type: str, 
                    inputs: Dict, output: Any, rationale: str):
        """
        Log high-level decision with full context.
        
        Args:
            agent_id: Agent identifier
            decision_type: Type of decision
            inputs: Input parameters
            output: Decision output
            rationale: Explanation of why this decision was made
        """
        self._write(f"\n[{agent_id}] DECISION: {decision_type}", "NORMAL")
        self._write(f"  Inputs: {inputs}", "VERBOSE")
        self._write(f"  Output: {output}", "NORMAL")
        self._write(f"  Rationale: {rationale}", "NORMAL")
    
    def log_metric(self, metric_name: str, value: Any):
        """
        Log performance or evaluation metric.
        
        Args:
            metric_name: Name of metric
            value: Metric value
        """
        self._write(f"METRIC: {metric_name} = {value}", "NORMAL")
    
    def log_error(self, agent_id: str, error: str):
        """Log error or exceptional condition."""
        self._write(f"[{agent_id}] ERROR: {error}", "MINIMAL")
    
    def log_summary(self, summary: Dict):
        """
        Log final simulation summary.
        
        Args:
            summary: Dictionary of summary statistics
        """
        self._write("\n" + "=" * 80, "MINIMAL")
        self._write("SIMULATION SUMMARY", "MINIMAL")
        self._write("=" * 80, "MINIMAL")
        for key, value in summary.items():
            self._write(f"{key}: {value}", "MINIMAL")
    
    def get_recent_entries(self, n: int = 50) -> List[str]:
        """
        Get most recent log entries for UI display.
        
        Args:
            n: Number of entries to retrieve
            
        Returns:
            List of recent log strings
        """
        return self.entries[-n:] if len(self.entries) > n else self.entries


# Global logger instance
_global_logger: Optional[SimulationLogger] = None


def get_logger() -> SimulationLogger:
    """Get or create global logger instance."""
    global _global_logger
    if _global_logger is None:
        _global_logger = SimulationLogger()
    return _global_logger


def reset_logger(log_file: Optional[str] = None):
    """Reset global logger with new configuration."""
    global _global_logger
    _global_logger = SimulationLogger(log_file)
