"""
Core Simulation Loop
Integrates all AI components and manages simulation execution.

Execution Flow:
1. Initialize environment
2. Initialize agents
3. Initialize Bayesian priors
4. LOOP (time step):
   - Propagate hazards
   - Update risk probabilities
   - Assign tasks via CSP
   - Generate plans via STRIPS
   - Compute paths via A*
   - Execute one action per agent
   - Update environment
   - Render UI
"""

import pygame
from typing import List, Dict, Optional
from ..core.environment import Grid
from ..agents.explorer import ExplorerAgent
from ..agents.rescue import RescueAgent
from ..agents.support import SupportAgent
from ..ai.bayesian_risk import BayesianRiskModel
from ..ai.csp_allocator import CSPAllocator
from ..ai.coordinator import HybridCoordinator, CoordinationMode
from ..ai.communication import CommunicationNetwork
from ..ai.dynamic_spawner import DynamicSpawner
from ..data.scenarios import ScenarioGenerator
from ..utils.logger import get_logger, reset_logger
from ..utils.config import SIMULATION, GRID, UI, ActionType
from ..ui.renderer import Renderer


class Simulator:
    """
    Main simulation orchestrator.
    
    Responsibilities:
    - Initialize all components
    - Execute timestep loop
    - Coordinate agent actions
    - Track metrics
    - Handle UI and user input
    """
    
    def __init__(self, seed: Optional[int] = None, coordination_mode: Optional[str] = None, enable_spawning: bool = True, verbose: bool = True, difficulty: Optional[str] = None):
        """
        Initialize simulator.
        
        Args:
            seed: Random seed for determinism
            coordination_mode: Force coordination mode ('centralized', 'auction', 'coalition', 'hybrid'/None)
            enable_spawning: Enable dynamic agent spawning
            verbose: Enable explainability and detailed logging
            difficulty: Scenario difficulty ('easy', 'medium', 'hard', 'extreme', 'nightmare')
        """
        self.seed = seed or SIMULATION.RANDOM_SEED
        self.timestep = 0
        self.paused = False
        self.running = True
        self.enable_spawning = enable_spawning
        self.verbose = verbose  # Enable explainability by default
        self.difficulty = difficulty  # Scenario difficulty
        
        # Parse coordination mode
        if coordination_mode:
            mode_map = {
                'centralized': CoordinationMode.CENTRALIZED,
                'auction': CoordinationMode.AUCTION,
                'coalition': CoordinationMode.COALITION,
                'hybrid': None
            }
            self.force_mode = mode_map.get(coordination_mode.lower(), None)
        else:
            self.force_mode = None
        
        # Initialize logger
        reset_logger()
        self.logger = get_logger()
        
        # Initialize components
        self.grid = None
        self.agents: List = []
        self.risk_model = None
        self.csp_allocator = None
        self.coordinator = None  # Hybrid coordinator
        self.comm_network = None  # Communication network
        self.spawner = None  # Dynamic agent spawner
        self.renderer = None
        
        # Track allocation for reallocation
        self.current_allocation = {}
        
        # Metrics
        self.total_survivors_rescued = 0
        self.total_cells_explored = 0
        self.initial_survivors = 0  # Track initial survivor count
        
        self.logger.log_metric("Initialization", f"Seed={self.seed}")
    
    def initialize(self):
        """Initialize all simulation components."""
        self.logger._write("\n" + "="*80, "MINIMAL")
        self.logger._write("INITIALIZING SIMULATION", "MINIMAL")
        self.logger._write("="*80, "MINIMAL")
        
        # Generate scenario based on difficulty
        scenario_gen = ScenarioGenerator(self.seed)
        
        if self.difficulty:
            scenario = scenario_gen.generate_scenario_by_difficulty(self.difficulty)
            self.logger.log_metric("Scenario", f"Difficulty={self.difficulty.upper()}")
        else:
            scenario = scenario_gen.generate_standard_scenario()
            self.logger.log_metric("Scenario", "Standard")
        
        # Initialize grid
        self.grid = Grid(
            width=scenario['width'],
            height=scenario['height'],
            seed=self.seed
        )
        scenario_gen.apply_scenario_to_grid(self.grid, scenario)
        
        # Store initial survivor count
        self.initial_survivors = len(scenario['survivors'])
        
        self.logger.log_metric("Grid size", f"{self.grid.width}x{self.grid.height}")
        self.logger.log_metric("Initial survivors", self.initial_survivors)
        self.logger.log_metric("Safe zones", len(scenario['safe_zones']))
        
        # Initialize risk model
        self.risk_model = BayesianRiskModel()
        self.risk_model.initialize_grid(self.grid.width, self.grid.height)
        
        # Initialize agents - more rescue agents for better success rate
        agent_positions = scenario['agent_positions']
        
        self.agents = [
            ExplorerAgent("EXP-1", agent_positions['explorer']),
            ExplorerAgent("EXP-2", agent_positions['explorer']),  # 2nd explorer
            RescueAgent("RES-1", agent_positions['rescue']),
            RescueAgent("RES-2", agent_positions['rescue']),      # 2nd rescue
            RescueAgent("RES-3", agent_positions['rescue']),      # 3rd rescue
            SupportAgent("SUP-1", agent_positions['support']),
        ]
        
        self.logger.log_metric("Agents initialized", len(self.agents))
        
        # Initialize CSP allocator
        self.csp_allocator = CSPAllocator()
        
        # Initialize communication network
        self.comm_network = CommunicationNetwork(
            communication_range=15.0,
            enable_broadcast=True
        )
        
        # Initialize hybrid coordinator (with explainability enabled by default)
        self.coordinator = HybridCoordinator(
            self.csp_allocator,
            self.comm_network,
            enable_explanations=True  # NEW v2.1: Enable explainability by default
        )
        
        # Initialize dynamic spawner
        if self.enable_spawning:
            self.spawner = DynamicSpawner(max_agents=20)
        
        # Inject communication network into agents
        for agent in self.agents:
            agent.set_communication_network(self.comm_network)
            self.comm_network.register_agent(agent.get_numeric_id())
        
        # Log coordination mode
        if self.force_mode:
            mode_name = self.force_mode.value.upper()
            self.logger.log_metric("Coordinator mode", f"{mode_name} (forced)")
        else:
            self.logger.log_metric("Coordinator mode", "HYBRID (auto-select)")
        
        # Initialize renderer
        self.renderer = Renderer(UI.WINDOW_WIDTH, UI.WINDOW_HEIGHT)
        
        self.logger._write("Initialization complete\n", "MINIMAL")
    
    def run(self):
        """
        Main simulation loop.
        
        Executes timesteps until completion or user exit.
        """
        clock = pygame.time.Clock()
        
        while self.running and self.timestep < SIMULATION.MAX_TIMESTEPS:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                else:
                    command = self.renderer.handle_event(event)
                    if command == "QUIT":
                        self.running = False
                    elif command == "PAUSE":
                        self.paused = not self.paused
                    elif command == "RESET":
                        self.reset()
            
            # Execute timestep if not paused
            if not self.paused:
                self.execute_timestep()
            
            # Render
            self.renderer.render(self.grid, self.agents, self.risk_model, self.timestep, self.coordinator, self.initial_survivors)
            
            # Check win condition
            if len(self.grid.survivor_positions) == 0:
                self.logger._write("\n" + "="*80, "MINIMAL")
                self.logger._write("ALL SURVIVORS RESCUED!", "MINIMAL")
                self.logger._write(f"Completed in {self.timestep} timesteps", "MINIMAL")
                self.logger._write("="*80, "MINIMAL")
                
                # Render final state one more time
                self.renderer.render(self.grid, self.agents, self.risk_model, self.timestep, self.coordinator, self.initial_survivors)
                pygame.display.flip()
                
                # Wait 3 seconds to show completion message, then exit
                pygame.time.wait(3000)
                self.running = False
            
            # Control frame rate
            clock.tick(SIMULATION.TARGET_FPS)
        
        # Finalize
        self.finalize()
    
    def execute_timestep(self):
        """
        Execute one simulation timestep.
        
        This is the core integration point for all AI components.
        """
        # Log timestep start
        grid_state = self.grid.get_grid_state_summary()
        self.logger.log_timestep(self.timestep, grid_state)
        
        # 1. Propagate hazards
        self.grid.propagate_hazards()
        
        # Update communication network timestep
        self.comm_network.advance_timestep()
        
        # Get current survivor positions (needed for spawning and coordination)
        survivors = list(self.grid.survivor_positions)
        
        # Dynamic agent spawning (if enabled)
        if self.spawner:
            spawn_type = self.spawner.evaluate_spawning_needs(
                self.agents,
                self.grid,
                survivors,
                self.timestep
            )
            
            if spawn_type:
                new_agent = self.spawner.spawn_agent(
                    spawn_type,
                    self.grid,
                    self.comm_network
                )
                
                if new_agent:
                    self.agents.append(new_agent)
                    self.logger.log_metric(
                        f"T{self.timestep} Agent Spawned",
                        f"{new_agent.agent_id} ({spawn_type}) at {new_agent.position}"
                    )
        
        # 2. Update risk probabilities for all agents
        for agent in self.agents:
            observations = agent.perceive(self.grid, self.risk_model)
            agent.update_beliefs(observations, self.grid, self.risk_model)
            
            self.logger.log_agent_perception(
                agent.agent_id,
                agent.position,
                observations
            )
            
            risk_values = self.risk_model.get_all_risks(agent.position)
            self.logger.log_risk_estimation(
                agent.agent_id,
                agent.position,
                risk_values
            )
        
        # 3. Assign tasks via HYBRID COORDINATOR
        agent_info = {
            agent.agent_id: {
                'position': agent.position,
                'type': agent.agent_type,
                'current_load': len(agent.assigned_tasks),
                'carrying': agent.carrying_survivor,
                'explored_cells': agent.explored_cells
            }
            for agent in self.agents
        }
        
        if survivors:
            # Assess environment for protocol selection (now with confidence intervals)
            assessment, risk_confidence = self.coordinator.assess_environment(
                self.risk_model,
                survivors,
                agent_info,
                self.grid
            )
            
            # Select coordination mode (with explanation generation)
            selected_mode = self.coordinator.select_mode(
                assessment,
                self.timestep,
                force_mode=self.force_mode,
                risk_confidence=risk_confidence
            )
            
            # Log explanation if available (NEW v2.1 - ENABLED)
            if self.coordinator.last_explanation:
                explanation_text = self.coordinator.last_explanation.to_natural_language()
                self.logger._write(f"\n--- COORDINATION DECISION ---\n{explanation_text}\n", "NORMAL")
                
                # Store for GUI display
                if self.renderer:
                    self.renderer.last_explanation = self.coordinator.last_explanation
            
            # Allocate tasks using selected protocol
            allocation = self.coordinator.allocate_tasks(
                selected_mode,
                agent_info,
                survivors,
                self.risk_model,
                lambda p1, p2: abs(p1[0] - p2[0]) + abs(p1[1] - p2[1]),
                current_allocation=self.current_allocation
            )
            
            # Store for reallocation
            self.current_allocation = allocation
            
            # Log coordination details
            self.logger.log_task_allocation(allocation)
            if self.timestep % 10 == 0:  # Log mode every 10 timesteps
                self.logger.log_metric(
                    f"T{self.timestep} Coord Mode",
                    f"{selected_mode.value} (risk={assessment.avg_risk:.2f}, uncertainty={assessment.uncertainty_level()})"
                )
        else:
            allocation = {}
            self.current_allocation = {}
        
        # 4. Generate plans and execute actions for each agent
        for agent in self.agents:
            # Decide action (pass timestep for suppression)
            action = agent.decide_action(
                self.grid,
                self.risk_model,
                allocation=allocation,
                agents=agent_info,
                timestep=self.timestep
            )
            
            if action:
                # Handle SUPPRESS_HAZARD action (support agent special action)
                if action.type == ActionType.SUPPRESS_HAZARD:
                    # Support agent tracks suppression internally
                    # Just log the action
                    self.logger.log_action(
                        agent.agent_id,
                        "SUPPRESS_HAZARD",
                        agent.position,
                        f"Suppressing hazards in 3x3 area for 5 timesteps (reduction: 0.3)"
                    )
                    success = True
                    result = "Hazard suppression active"
                else:
                    # Execute normal action
                    success, result = agent.execute_action(action, self.grid)
                    
                    self.logger.log_action(
                        agent.agent_id,
                        str(action),
                        agent.position,
                        result
                    )
                
                # Update metrics
                if agent.agent_type == "RESCUE":
                    self.total_survivors_rescued = sum(
                        a.survivors_rescued for a in self.agents
                    )
                
                self.total_cells_explored = sum(
                    len(a.explored_cells) for a in self.agents
                )
        
        # Increment timestep
        self.timestep += 1
    
    def _execute_timestep(self):
        """Alias for execute_timestep (used by benchmark suite for headless mode)."""
        self.execute_timestep()
    
    def reset(self):
        """Reset simulation to initial state."""
        self.logger._write("\n=== SIMULATION RESET ===\n", "MINIMAL")
        self.timestep = 0
        self.paused = False
        reset_logger()
        self.logger = get_logger()
        self.initialize()
    
    def finalize(self):
        """Finalize simulation and generate summary."""
        # Summary metrics
        summary = {
            "Total timesteps": self.timestep,
            "Survivors rescued": self.total_survivors_rescued,
            "Survivors remaining": len(self.grid.survivor_positions),
            "Cells explored": self.total_cells_explored,
            "Final fires": len(self.grid.fire_positions),
            "Final floods": len(self.grid.flood_positions),
        }
        
        self.logger.log_summary(summary)
        
        # Agent metrics
        self.logger._write("\n" + "="*80, "MINIMAL")
        self.logger._write("AGENT PERFORMANCE", "MINIMAL")
        self.logger._write("="*80, "MINIMAL")
        
        if self.spawner:
            spawn_stats = self.spawner.get_spawn_stats()
            if spawn_stats['total_spawned'] > 0:
                self.logger._write(f"\nDynamic Spawning: {spawn_stats['total_spawned']} agents spawned", "MINIMAL")
                self.logger._write(f"  Explorers: {spawn_stats['explorers_spawned']}", "MINIMAL")
                self.logger._write(f"  Rescue: {spawn_stats['rescue_spawned']}", "MINIMAL")
                self.logger._write(f"  Support: {spawn_stats['support_spawned']}", "MINIMAL")
        
        self.logger._write(f"\nFinal agent count: {len(self.agents)}", "MINIMAL")
        
        for agent in self.agents:
            state = agent.get_state()
            self.logger._write(f"\n{state['id']} ({state['type']}):", "MINIMAL")
            self.logger._write(f"  Steps taken: {state['steps_taken']}", "MINIMAL")
            self.logger._write(f"  Survivors rescued: {state['survivors_rescued']}", "MINIMAL")
            self.logger._write(f"  Cells explored: {state['cells_explored']}", "MINIMAL")
            self.logger._write(f"  Blocked steps: {state['blocked_steps']}", "MINIMAL")
        
        # Cleanup
        self.renderer.cleanup()
        
        # NEW v2.1: Generate explainability report
        if self.coordinator and self.coordinator.explanation_engine:
            self.logger._write("\n" + "="*80, "MINIMAL")
            self.logger._write("DECISION EXPLAINABILITY REPORT (v2.1)", "MINIMAL")
            self.logger._write("="*80, "MINIMAL")
            
            # Generate summary report
            summary_report = self.coordinator.explanation_engine.generate_summary_report()
            self.logger._write(summary_report, "MINIMAL")
            
            # Export full audit trail to JSON (for regulatory compliance)
            try:
                audit_filepath = "explanation_audit.json"
                self.coordinator.explanation_engine.export_audit_trail(audit_filepath)
                self.logger._write(f"\n[SAVED] Full audit trail exported to: {audit_filepath}", "MINIMAL")
            except Exception as e:
                self.logger._write(f"\n[WARNING] Could not export audit trail: {e}", "MINIMAL")
        
        self.logger._write("\n" + "="*80, "MINIMAL")
        self.logger._write("SIMULATION ENDED", "MINIMAL")
        self.logger._write("="*80 + "\n", "MINIMAL")
