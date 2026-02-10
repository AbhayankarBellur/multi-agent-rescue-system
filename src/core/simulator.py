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
from ..data.scenarios import ScenarioGenerator
from ..utils.logger import get_logger, reset_logger
from ..utils.config import SIMULATION, GRID, UI
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
    
    def __init__(self, seed: Optional[int] = None):
        """
        Initialize simulator.
        
        Args:
            seed: Random seed for determinism
        """
        self.seed = seed or SIMULATION.RANDOM_SEED
        self.timestep = 0
        self.paused = False
        self.running = True
        
        # Initialize logger
        reset_logger()
        self.logger = get_logger()
        
        # Initialize components
        self.grid = None
        self.agents: List = []
        self.risk_model = None
        self.csp_allocator = None
        self.renderer = None
        
        # Metrics
        self.total_survivors_rescued = 0
        self.total_cells_explored = 0
        
        self.logger.log_metric("Initialization", f"Seed={self.seed}")
    
    def initialize(self):
        """Initialize all simulation components."""
        self.logger._write("\n" + "="*80, "MINIMAL")
        self.logger._write("INITIALIZING SIMULATION", "MINIMAL")
        self.logger._write("="*80, "MINIMAL")
        
        # Generate scenario
        scenario_gen = ScenarioGenerator(self.seed)
        scenario = scenario_gen.generate_standard_scenario()
        
        # Initialize grid
        self.grid = Grid(
            width=scenario['width'],
            height=scenario['height'],
            seed=self.seed
        )
        scenario_gen.apply_scenario_to_grid(self.grid, scenario)
        
        self.logger.log_metric("Grid size", f"{self.grid.width}x{self.grid.height}")
        self.logger.log_metric("Initial survivors", len(scenario['survivors']))
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
            self.renderer.render(self.grid, self.agents, self.risk_model, self.timestep)
            
            # Check win condition
            if len(self.grid.survivor_positions) == 0:
                self.logger._write("\n" + "="*80, "MINIMAL")
                self.logger._write("ALL SURVIVORS RESCUED!", "MINIMAL")
                self.logger._write(f"Completed in {self.timestep} timesteps", "MINIMAL")
                self.logger._write("="*80, "MINIMAL")
                
                # Render final state one more time
                self.renderer.render(self.grid, self.agents, self.risk_model, self.timestep)
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
        
        # 3. Assign tasks via CSP (for rescue agents)
        agent_info = {
            agent.agent_id: {
                'position': agent.position,
                'type': agent.agent_type,
                'current_load': len(agent.assigned_tasks),
                'carrying': agent.carrying_survivor
            }
            for agent in self.agents
        }
        
        survivors = list(self.grid.survivor_positions)
        
        if survivors:
            allocation = self.csp_allocator.allocate(
                agent_info,
                survivors,
                self.risk_model,
                lambda p1, p2: abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])
            )
            
            self.logger.log_task_allocation(allocation)
        else:
            allocation = {}
        
        # 4. Generate plans and execute actions for each agent
        for agent in self.agents:
            # Decide action
            action = agent.decide_action(
                self.grid,
                self.risk_model,
                allocation=allocation,
                agents=agent_info
            )
            
            if action:
                # Execute action
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
        
        for agent in self.agents:
            state = agent.get_state()
            self.logger._write(f"\n{state['id']} ({state['type']}):", "MINIMAL")
            self.logger._write(f"  Steps taken: {state['steps_taken']}", "MINIMAL")
            self.logger._write(f"  Survivors rescued: {state['survivors_rescued']}", "MINIMAL")
            self.logger._write(f"  Cells explored: {state['cells_explored']}", "MINIMAL")
            self.logger._write(f"  Blocked steps: {state['blocked_steps']}", "MINIMAL")
        
        # Cleanup
        self.renderer.cleanup()
        
        self.logger._write("\n" + "="*80, "MINIMAL")
        self.logger._write("SIMULATION ENDED", "MINIMAL")
        self.logger._write("="*80 + "\n", "MINIMAL")
