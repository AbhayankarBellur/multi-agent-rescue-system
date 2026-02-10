"""
Configuration and Constants Module
Centralizes all configurable parameters for deterministic, reproducible simulations.
No magic numbers - all parameters are explicitly named and documented.
"""

from dataclasses import dataclass
from typing import Tuple


@dataclass
class GridConfig:
    """Grid and environment configuration."""
    WIDTH: int = 40
    HEIGHT: int = 30
    CELL_SIZE: int = 20  # pixels per cell for rendering


@dataclass
class HazardConfig:
    """Hazard propagation parameters."""
    # Fire spread probabilities
    FIRE_SPREAD_RATE: float = 0.03  # Further reduced for playability
    FIRE_SPREAD_TO_DEBRIS: float = 0.08  # Reduced chain reactions
    FIRE_DECAY_RATE: float = 0.15  # Faster decay
    
    # Flood spread probabilities
    FLOOD_SPREAD_RATE: float = 0.03  # Further reduced
    FLOOD_DECAY_RATE: float = 0.08  # Faster receding
    
    # Collapse/debris generation
    DEBRIS_GENERATION_NEAR_FIRE: float = 0.01  # Minimal debris generation


@dataclass
class AgentConfig:
    """Agent behavior parameters."""
    # Movement
    ACTIONS_PER_TIMESTEP: int = 1
    
    # Risk thresholds (0.0 - 1.0)
    RISK_THRESHOLD_EXPLORER: float = 0.7
    RISK_THRESHOLD_RESCUE: float = 0.6
    RISK_THRESHOLD_SUPPORT: float = 0.8
    
    # Agent-specific parameters
    EXPLORER_CURIOSITY_WEIGHT: float = 0.8  # Weight for unexplored areas
    RESCUE_URGENCY_WEIGHT: float = 0.9      # Weight for immediate rescue
    SUPPORT_COORDINATION_WEIGHT: float = 0.7 # Weight for assistance


@dataclass
class AIConfig:
    """AI algorithm parameters."""
    # A* search
    ASTAR_TERRAIN_PENALTY_DEBRIS: float = 5.0
    ASTAR_TERRAIN_PENALTY_FLOOD: float = 3.0
    ASTAR_RISK_PENALTY_MULTIPLIER: float = 10.0
    ASTAR_HEURISTIC_RISK_WEIGHT: float = 1.0
    
    # Bayesian risk estimation
    BAYESIAN_PRIOR_FIRE: float = 0.1
    BAYESIAN_PRIOR_FLOOD: float = 0.1
    BAYESIAN_PRIOR_COLLAPSE: float = 0.05
    BAYESIAN_UPDATE_RATE: float = 0.3
    
    # CSP allocation
    CSP_MAX_SURVIVORS_PER_AGENT: int = 2
    CSP_RISK_CONSTRAINT_THRESHOLD: float = 0.65
    CSP_DISTANCE_WEIGHT: float = 0.6
    CSP_RISK_WEIGHT: float = 0.4
    
    # STRIPS planning
    STRIPS_MAX_PLAN_DEPTH: int = 50
    STRIPS_REPLAN_THRESHOLD: int = 5  # Replan if blocked for N steps


@dataclass
class SimulationConfig:
    """Simulation runtime parameters."""
    TARGET_FPS: int = 10
    TIMESTEPS_PER_SECOND: int = 1
    MAX_TIMESTEPS: int = 1000
    RANDOM_SEED: int = 42  # For deterministic runs
    
    # Survivor and safe zone configuration
    NUM_SURVIVORS: int = 8
    NUM_SAFE_ZONES: int = 2
    NUM_INITIAL_FIRES: int = 3
    NUM_INITIAL_FLOODS: int = 2
    NUM_INITIAL_DEBRIS: int = 5


@dataclass
class UIConfig:
    """User interface configuration."""
    WINDOW_WIDTH: int = 1400
    WINDOW_HEIGHT: int = 800
    
    # Panel dimensions
    LOG_PANEL_WIDTH: int = 400
    STATUS_PANEL_HEIGHT: int = 150
    
    # Colors (RGB)
    COLOR_NORMAL: Tuple[int, int, int] = (240, 240, 240)
    COLOR_FIRE: Tuple[int, int, int] = (255, 69, 0)
    COLOR_FLOOD: Tuple[int, int, int] = (30, 144, 255)
    COLOR_DEBRIS: Tuple[int, int, int] = (105, 105, 105)
    COLOR_SURVIVOR: Tuple[int, int, int] = (255, 215, 0)
    COLOR_SAFE_ZONE: Tuple[int, int, int] = (50, 205, 50)
    COLOR_EXPLORED: Tuple[int, int, int] = (200, 200, 200)
    COLOR_UNEXPLORED: Tuple[int, int, int] = (100, 100, 100)
    
    # Agent colors - highly distinct for visibility
    COLOR_EXPLORER: Tuple[int, int, int] = (0, 150, 255)  # Blue - for exploration
    COLOR_RESCUE: Tuple[int, int, int] = (255, 50, 50)    # Red - for rescue urgency
    COLOR_SUPPORT: Tuple[int, int, int] = (50, 255, 50)   # Green - for support
    
    # UI elements
    COLOR_BACKGROUND: Tuple[int, int, int] = (40, 40, 40)
    COLOR_TEXT: Tuple[int, int, int] = (255, 255, 255)
    COLOR_PANEL_BG: Tuple[int, int, int] = (60, 60, 60)
    
    # Risk heatmap (alpha channel for overlay)
    RISK_HEATMAP_ALPHA: int = 128
    
    # Font sizes
    FONT_SIZE_NORMAL: int = 12
    FONT_SIZE_SMALL: int = 10
    FONT_SIZE_LARGE: int = 16


@dataclass
class LogConfig:
    """Logging configuration."""
    LOG_TO_FILE: bool = True
    LOG_TO_CONSOLE: bool = True
    LOG_FILE_PATH: str = "simulation_log.txt"
    LOG_LEVEL_DETAIL: str = "VERBOSE"  # Options: VERBOSE, NORMAL, MINIMAL


# Global configuration instances
GRID = GridConfig()
HAZARD = HazardConfig()
AGENT = AgentConfig()
AI = AIConfig()
SIMULATION = SimulationConfig()
UI = UIConfig()
LOG = LogConfig()


# Cell type enumeration
class CellType:
    """Enumeration of all possible cell types in the grid."""
    NORMAL = 0
    FIRE = 1
    FLOOD = 2
    DEBRIS = 3
    SURVIVOR = 4
    SAFE_ZONE = 5
    EXPLORED = 6
    UNEXPLORED = 7


# Agent type enumeration
class AgentType:
    """Enumeration of agent types."""
    EXPLORER = "EXPLORER"
    RESCUE = "RESCUE"
    SUPPORT = "SUPPORT"


# Action types
class ActionType:
    """STRIPS action types."""
    MOVE = "move"
    PICKUP = "pickup"
    TRANSPORT = "transport"
    DROP = "drop"
    EXPLORE = "explore"
    WAIT = "wait"
