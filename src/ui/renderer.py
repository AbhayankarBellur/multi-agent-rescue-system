"""
User Interface - Pygame-based Visualization
Renders grid, agents, risk overlays, and status information.

UI Components:
- Main grid display
- Risk heatmap overlay
- Agent positions and paths
- Status panels
- Log display
- Control buttons

Design: UI ONLY displays - no logic modifications
"""

import pygame
from typing import Dict, List, Tuple, Optional
import math
from ..utils.config import UI, GRID, CellType, AgentType
from ..utils.logger import get_logger


class Renderer:
    """
    Main rendering engine for simulation visualization.
    
    Responsibilities:
    - Render grid cells with color coding
    - Overlay risk heatmap
    - Draw agents and paths
    - Display status information
    - Show decision logs
    
    NOT responsible for:
    - Game logic
    - Agent decisions
    - State modifications
    """
    
    def __init__(self, width: int, height: int):
        """
        Initialize renderer.
        
        Args:
            width: Window width in pixels
            height: Window height in pixels
        """
        pygame.init()
        
        self.window_width = width
        self.window_height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("AI Disaster Rescue Simulator")
        
        # Grid rendering area
        self.grid_width = GRID.WIDTH * GRID.CELL_SIZE
        self.grid_height = GRID.HEIGHT * GRID.CELL_SIZE
        self.grid_surface = pygame.Surface((self.grid_width, self.grid_height))
        
        # Fonts
        pygame.font.init()
        self.font_normal = pygame.font.SysFont('Arial', UI.FONT_SIZE_NORMAL)
        self.font_small = pygame.font.SysFont('Arial', UI.FONT_SIZE_SMALL)
        self.font_large = pygame.font.SysFont('Arial', UI.FONT_SIZE_LARGE, bold=True)
        
        # UI state
        self.show_risk_overlay = True
        self.show_agent_paths = True
        self.show_labels = True
        
        self.logger = get_logger()
    
    def render(self, grid, agents: List, risk_model, timestep: int):
        """
        Render complete frame.
        
        Args:
            grid: Environment grid
            agents: List of agent objects
            risk_model: Bayesian risk model
            timestep: Current timestep
        """
        # Clear screen
        self.screen.fill(UI.COLOR_BACKGROUND)
        
        # Render grid
        self._render_grid(grid)
        
        # Render risk overlay
        if self.show_risk_overlay:
            self._render_risk_overlay(grid, risk_model)
        
        # Render agents and paths
        self._render_agents(grid, agents)
        
        # Blit grid to screen
        self.screen.blit(self.grid_surface, (10, 10))
        
        # Render UI panels
        self._render_status_panel(timestep, grid, agents)
        self._render_agent_info_panel(agents)
        self._render_log_panel()
        
        # Render controls
        self._render_controls()
        
        # Update display
        pygame.display.flip()
    
    def _render_grid(self, grid):
        """
        Render grid cells with color coding.
        
        Args:
            grid: Environment grid
        """
        cell_size = GRID.CELL_SIZE
        
        for x in range(grid.width):
            for y in range(grid.height):
                cell = grid.get_cell(x, y)
                if not cell:
                    continue
                
                # Determine cell color
                color = self._get_cell_color(cell)
                
                # Draw cell
                rect = pygame.Rect(
                    x * cell_size,
                    y * cell_size,
                    cell_size,
                    cell_size
                )
                pygame.draw.rect(self.grid_surface, color, rect)
                
                # Draw grid lines
                pygame.draw.rect(self.grid_surface, (200, 200, 200), rect, 1)
    
    def _get_cell_color(self, cell) -> Tuple[int, int, int]:
        """
        Determine color for a cell based on state.
        
        Args:
            cell: Cell object
            
        Returns:
            RGB color tuple
        """
        # Priority order for multiple states
        if cell.is_safe_zone:
            return UI.COLOR_SAFE_ZONE
        if cell.has_fire:
            return UI.COLOR_FIRE
        if cell.has_survivor:
            return UI.COLOR_SURVIVOR
        if cell.has_debris:
            return UI.COLOR_DEBRIS
        if cell.has_flood:
            return UI.COLOR_FLOOD
        if cell.explored:
            return UI.COLOR_EXPLORED
        return UI.COLOR_NORMAL
    
    def _render_risk_overlay(self, grid, risk_model):
        """
        Render semi-transparent risk heatmap.
        
        Args:
            grid: Environment grid
            risk_model: Risk model
        """
        overlay = pygame.Surface((self.grid_width, self.grid_height))
        overlay.set_alpha(UI.RISK_HEATMAP_ALPHA)
        cell_size = GRID.CELL_SIZE
        
        for x in range(grid.width):
            for y in range(grid.height):
                risk = risk_model.get_risk((x, y), "combined")
                
                # Color from green (low risk) to red (high risk)
                if risk > 0.01:
                    red = int(255 * risk)
                    green = int(255 * (1 - risk))
                    color = (red, green, 0)
                    
                    rect = pygame.Rect(
                        x * cell_size,
                        y * cell_size,
                        cell_size,
                        cell_size
                    )
                    pygame.draw.rect(overlay, color, rect)
        
        self.grid_surface.blit(overlay, (0, 0))
    
    def _render_agents(self, grid, agents):
        """
        Render agent positions and paths with distinct shapes.
        
        Args:
            grid: Environment grid
            agents: List of agents
        """
        cell_size = GRID.CELL_SIZE
        
        for agent in agents:
            x, y = agent.position
            
            # Draw path if available
            if self.show_agent_paths and agent.current_path:
                self._draw_path(agent.current_path, agent.agent_type)
            
            # Calculate center position
            center = (
                x * cell_size + cell_size // 2,
                y * cell_size + cell_size // 2
            )
            
            # Get agent color
            color = self._get_agent_color(agent.agent_type)
            
            # Draw different shapes for different agent types
            size = cell_size // 2
            
            if agent.agent_type == "EXPLORER":
                # Circle for Explorer (blue)
                pygame.draw.circle(self.grid_surface, color, center, size)
                pygame.draw.circle(self.grid_surface, (255, 255, 255), center, size, 2)
            elif agent.agent_type == "RESCUE":
                # Square for Rescue (red)
                rect = pygame.Rect(center[0] - size, center[1] - size, size * 2, size * 2)
                pygame.draw.rect(self.grid_surface, color, rect)
                pygame.draw.rect(self.grid_surface, (255, 255, 255), rect, 2)
            elif agent.agent_type == "SUPPORT":
                # Triangle for Support (green)
                points = [
                    (center[0], center[1] - size),  # Top
                    (center[0] - size, center[1] + size),  # Bottom left
                    (center[0] + size, center[1] + size),  # Bottom right
                ]
                pygame.draw.polygon(self.grid_surface, color, points)
                pygame.draw.polygon(self.grid_surface, (255, 255, 255), points, 2)
            
            # Draw label if enabled
            if self.show_labels:
                label = agent.agent_id[-1]  # Last character (number)
                text = self.font_small.render(label, True, (0, 0, 0))
                text_rect = text.get_rect(center=center)
                self.grid_surface.blit(text, text_rect)
    
    def _draw_path(self, path: List[Tuple[int, int]], agent_type: str):
        """Draw agent's planned path."""
        if len(path) < 2:
            return
        
        cell_size = GRID.CELL_SIZE
        color = self._get_agent_color(agent_type)
        
        points = [
            (x * cell_size + cell_size // 2, y * cell_size + cell_size // 2)
            for x, y in path[:10]  # Show first 10 steps
        ]
        
        if len(points) >= 2:
            pygame.draw.lines(self.grid_surface, color, False, points, 2)
    
    def _get_agent_color(self, agent_type: str) -> Tuple[int, int, int]:
        """Get color for agent type."""
        if agent_type == "EXPLORER":
            return UI.COLOR_EXPLORER
        elif agent_type == "RESCUE":
            return UI.COLOR_RESCUE
        elif agent_type == "SUPPORT":
            return UI.COLOR_SUPPORT
        return (255, 255, 255)
    
    def _render_status_panel(self, timestep: int, grid, agents):
        """Render status panel with simulation info."""
        panel_x = self.grid_width + 30
        panel_y = 20
        
        # Timestep
        text = self.font_large.render(f"Timestep: {timestep}", True, UI.COLOR_TEXT)
        self.screen.blit(text, (panel_x, panel_y))
        panel_y += 30
        
        # Grid state
        state = grid.get_grid_state_summary()
        info_lines = [
            f"Survivors: {state['survivors']}",
            f"Fires: {state['fires']}",
            f"Floods: {state['floods']}",
            f"Debris: {state['debris']}",
        ]
        
        for line in info_lines:
            text = self.font_normal.render(line, True, UI.COLOR_TEXT)
            self.screen.blit(text, (panel_x, panel_y))
            panel_y += 20
        
        # Separator
        panel_y += 10
        pygame.draw.line(self.screen, UI.COLOR_TEXT, 
                        (panel_x, panel_y), 
                        (panel_x + 250, panel_y), 1)
        panel_y += 15
        
        # Legend section
        self._render_legend(panel_x, panel_y)
    
    def _render_agent_info_panel(self, agents):
        """Render agent status information."""
        panel_x = self.grid_width + 30
        panel_y = 200
        
        title = self.font_large.render("Agents", True, UI.COLOR_TEXT)
        self.screen.blit(title, (panel_x, panel_y))
        panel_y += 30
        
        for agent in agents:
            state = agent.get_state()
            
            # Agent name
            name_text = self.font_normal.render(
                f"{state['id']} ({state['type']})",
                True,
                self._get_agent_color(state['type'])
            )
            self.screen.blit(name_text, (panel_x, panel_y))
            panel_y += 18
            
            # Stats
            stats = [
                f"  Pos: {state['position']}",
                f"  Rescued: {state['survivors_rescued']}",
                f"  Explored: {state['cells_explored']}",
            ]
            
            for stat in stats:
                text = self.font_small.render(stat, True, UI.COLOR_TEXT)
                self.screen.blit(text, (panel_x, panel_y))
                panel_y += 15
            
            panel_y += 5
    
    def _render_log_panel(self):
        """Render recent log entries."""
        panel_x = self.grid_width + 30
        panel_y = 500
        panel_width = 350
        panel_height = 250
        
        # Background
        pygame.draw.rect(self.screen, UI.COLOR_PANEL_BG,
                        (panel_x - 5, panel_y - 5, panel_width, panel_height))
        
        # Title
        title = self.font_normal.render("Recent Log", True, UI.COLOR_TEXT)
        self.screen.blit(title, (panel_x, panel_y))
        panel_y += 20
        
        # Log entries
        entries = self.logger.get_recent_entries(12)
        
        for entry in entries[-12:]:  # Last 12 entries
            # Truncate long lines
            if len(entry) > 50:
                entry = entry[:47] + "..."
            
            text = self.font_small.render(entry, True, UI.COLOR_TEXT)
            self.screen.blit(text, (panel_x, panel_y))
            panel_y += 14
            
            if panel_y > 500 + panel_height - 20:
                break
    
    def _render_legend(self, panel_x: int, panel_y: int):
        """Render agent type legend with shapes."""
        # Title
        title = self.font_large.render("Agent Legend", True, UI.COLOR_TEXT)
        self.screen.blit(title, (panel_x, panel_y))
        panel_y += 30
        
        # Legend entries with shapes
        legend_items = [
            ("EXPLORER", UI.COLOR_EXPLORER, "circle", "Explores & maps area"),
            ("RESCUE", UI.COLOR_RESCUE, "square", "Rescues survivors"),
            ("SUPPORT", UI.COLOR_SUPPORT, "triangle", "Coordinates team"),
        ]
        
        shape_size = 10
        
        for agent_type, color, shape, description in legend_items:
            # Draw shape
            shape_x = panel_x + 10
            shape_y = panel_y + 10
            
            if shape == "circle":
                pygame.draw.circle(self.screen, color, (shape_x, shape_y), shape_size)
                pygame.draw.circle(self.screen, (255, 255, 255), (shape_x, shape_y), shape_size, 2)
            elif shape == "square":
                rect = pygame.Rect(shape_x - shape_size, shape_y - shape_size, shape_size * 2, shape_size * 2)
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, (255, 255, 255), rect, 2)
            elif shape == "triangle":
                points = [
                    (shape_x, shape_y - shape_size),
                    (shape_x - shape_size, shape_y + shape_size),
                    (shape_x + shape_size, shape_y + shape_size),
                ]
                pygame.draw.polygon(self.screen, color, points)
                pygame.draw.polygon(self.screen, (255, 255, 255), points, 2)
            
            # Draw text
            text = self.font_small.render(f"{agent_type}", True, color)
            self.screen.blit(text, (shape_x + 20, shape_y - 8))
            
            # Draw description
            desc_text = self.font_small.render(description, True, UI.COLOR_TEXT)
            self.screen.blit(desc_text, (shape_x + 20, shape_y + 5))
            
            panel_y += 35
    
    def _render_controls(self):
        """Render control instructions."""
        panel_y = self.window_height - 50
        
        controls = "SPACE: Pause | R: Reset | Q: Quit | H: Toggle Risk Overlay"
        text = self.font_small.render(controls, True, UI.COLOR_TEXT)
        text_rect = text.get_rect(center=(self.window_width // 2, panel_y))
        self.screen.blit(text, text_rect)
    
    def handle_event(self, event) -> Optional[str]:
        """
        Handle user input events.
        
        Args:
            event: Pygame event
            
        Returns:
            Command string or None
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                return "PAUSE"
            elif event.key == pygame.K_r:
                return "RESET"
            elif event.key == pygame.K_q:
                return "QUIT"
            elif event.key == pygame.K_h:
                self.show_risk_overlay = not self.show_risk_overlay
                return None
            elif event.key == pygame.K_p:
                self.show_agent_paths = not self.show_agent_paths
                return None
        
        return None
    
    def cleanup(self):
        """Clean up pygame resources."""
        pygame.quit()
