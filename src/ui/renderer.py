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
        
        # Windows-specific: center the window
        import os
        if os.name == 'nt':
            os.environ['SDL_VIDEO_WINDOW_POS'] = 'center'
        
        self.window_width = width
        self.window_height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("AI Disaster Rescue Simulator")
        
        # Show startup message
        self.screen.fill((30, 30, 40))
        pygame.font.init()
        startup_font = pygame.font.SysFont('Arial', 32, bold=True)
        message_font = pygame.font.SysFont('Arial', 18)
        
        title_text = startup_font.render("AI DISASTER RESCUE SIMULATOR", True, (255, 255, 255))
        msg_text = message_font.render("Initializing simulation...", True, (200, 200, 200))
        
        self.screen.blit(title_text, (width//2 - title_text.get_width()//2, height//2 - 40))
        self.screen.blit(msg_text, (width//2 - msg_text.get_width()//2, height//2 + 20))
        pygame.display.flip()
        pygame.time.wait(1000)  # Show for 1 second
        
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
        
        # Explainability tracking
        self.last_explanation = None
        self.explanation_history = []
        
        self.logger = get_logger()
    
    def render(self, grid, agents: List, risk_model, timestep: int, coordinator=None, initial_survivors: int = 0):
        """
        Render complete frame.
        
        Args:
            grid: Environment grid
            agents: List of agent objects
            risk_model: Bayesian risk model
            timestep: Current timestep
            coordinator: Hybrid coordinator (for protocol display)
            initial_survivors: Initial survivor count (for accurate display)
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
        
        # NEW: Render communication ranges (if enabled)
        if self.show_agent_paths:  # Reuse path toggle for communication
            self._render_communication_ranges(agents)
        
        # Blit grid to screen
        self.screen.blit(self.grid_surface, (10, 10))
        
        # NEW: Render protocol indicator (top-left overlay on grid)
        if coordinator:
            self._render_protocol_indicator(coordinator, timestep)
            self._render_risk_indicator(risk_model, grid)
        
        # Render UI panels
        self._render_status_panel(timestep, grid, agents, initial_survivors)
        self._render_agent_info_panel(agents)
        self._render_log_panel()
        self._render_explanation_panel()  # NEW: Explainability display
        
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
    
    def _render_status_panel(self, timestep: int, grid, agents, initial_survivors: int = 0):
        """Render status panel with simulation info and performance metrics."""
        panel_x = self.grid_width + 30
        panel_y = 20
        
        # Timestep
        text = self.font_large.render(f"Timestep: {timestep}", True, UI.COLOR_TEXT)
        self.screen.blit(text, (panel_x, panel_y))
        panel_y += 30
        
        # Performance Metrics (FIXED: Use initial_survivors parameter)
        rescued_count = sum(a.survivors_rescued for a in agents)
        
        # Use initial_survivors if provided, otherwise calculate (fallback)
        if initial_survivors > 0:
            total_survivors = initial_survivors
        else:
            # Fallback: calculate from current state
            current_survivors = grid.get_grid_state_summary()['survivors']
            total_survivors = current_survivors + rescued_count
        
        perf_lines = [
            f"Rescued: {rescued_count}/{total_survivors}",
            f"Agents: {len(agents)}",
        ]
        
        for line in perf_lines:
            text = self.font_normal.render(line, True, (100, 255, 100))  # Green for metrics
            self.screen.blit(text, (panel_x, panel_y))
            panel_y += 20
        
        panel_y += 5
        
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
        """Render enhanced legend with agent types and protocol modes."""
        # Title
        title = self.font_large.render("Legend", True, UI.COLOR_TEXT)
        self.screen.blit(title, (panel_x, panel_y))
        panel_y += 25
        
        # Agent Types Section
        subtitle = self.font_normal.render("Agent Types:", True, (200, 200, 200))
        self.screen.blit(subtitle, (panel_x, panel_y))
        panel_y += 20
        
        # Legend entries with shapes
        legend_items = [
            ("EXPLORER", UI.COLOR_EXPLORER, "circle", "Maps area"),
            ("RESCUE", UI.COLOR_RESCUE, "square", "Saves survivors"),
            ("SUPPORT", UI.COLOR_SUPPORT, "triangle", "Coordinates"),
        ]
        
        shape_size = 8
        
        for agent_type, color, shape, description in legend_items:
            # Draw shape
            shape_x = panel_x + 10
            shape_y = panel_y + 8
            
            if shape == "circle":
                pygame.draw.circle(self.screen, color, (shape_x, shape_y), shape_size)
                pygame.draw.circle(self.screen, (255, 255, 255), (shape_x, shape_y), shape_size, 1)
            elif shape == "square":
                rect = pygame.Rect(shape_x - shape_size, shape_y - shape_size, shape_size * 2, shape_size * 2)
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, (255, 255, 255), rect, 1)
            elif shape == "triangle":
                points = [
                    (shape_x, shape_y - shape_size),
                    (shape_x - shape_size, shape_y + shape_size),
                    (shape_x + shape_size, shape_y + shape_size),
                ]
                pygame.draw.polygon(self.screen, color, points)
                pygame.draw.polygon(self.screen, (255, 255, 255), points, 1)
            
            # Draw text
            text = self.font_small.render(f"{agent_type}: {description}", True, UI.COLOR_TEXT)
            self.screen.blit(text, (shape_x + 15, shape_y - 6))
            
            panel_y += 20
        
        # Protocol Modes Section
        panel_y += 10
        subtitle = self.font_normal.render("Protocol Modes:", True, (200, 200, 200))
        self.screen.blit(subtitle, (panel_x, panel_y))
        panel_y += 20
        
        protocol_items = [
            ("CENTRALIZED", (100, 255, 100), "Low risk"),
            ("AUCTION", (255, 255, 100), "Moderate risk"),
            ("COALITION", (255, 100, 100), "High risk"),
        ]
        
        for mode, color, desc in protocol_items:
            # Color box
            box_x = panel_x + 10
            box_y = panel_y + 2
            pygame.draw.rect(self.screen, color, (box_x, box_y, 12, 12))
            pygame.draw.rect(self.screen, (255, 255, 255), (box_x, box_y, 12, 12), 1)
            
            # Text
            text = self.font_small.render(f"{mode}: {desc}", True, UI.COLOR_TEXT)
            self.screen.blit(text, (box_x + 18, box_y))
            
            panel_y += 18
    
    def _render_controls(self):
        """Render control instructions."""
        panel_y = self.window_height - 50
        
        controls = "SPACE: Pause | R: Reset | Q: Quit | H: Risk | P: Comm"
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
    
    def _render_explanation_panel(self):
        """
        Render explainability panel showing recent decisions.
        
        NEW v2.1: Natural language explanations for coordination decisions
        """
        panel_x = self.grid_width + 30
        panel_y = 600
        panel_width = 350
        panel_height = 150
        
        # Background
        pygame.draw.rect(self.screen, (40, 40, 50),
                        (panel_x - 5, panel_y - 5, panel_width, panel_height))
        pygame.draw.rect(self.screen, (100, 100, 120),
                        (panel_x - 5, panel_y - 5, panel_width, panel_height), 2)
        
        # Title
        title = self.font_normal.render("Decision Explanation", True, (255, 255, 100))
        self.screen.blit(title, (panel_x, panel_y))
        panel_y += 25
        
        if self.last_explanation:
            # Store in history
            if not self.explanation_history or self.explanation_history[-1] != self.last_explanation:
                self.explanation_history.append(self.last_explanation)
                if len(self.explanation_history) > 10:
                    self.explanation_history.pop(0)
            
            # Decision type
            decision_type = self.last_explanation.decision_type.value.replace('_', ' ').title()
            type_text = self.font_small.render(f"Type: {decision_type}", True, (200, 200, 255))
            self.screen.blit(type_text, (panel_x, panel_y))
            panel_y += 18
            
            # Primary explanation (wrapped)
            explanation = self.last_explanation.primary_explanation
            lines = self._wrap_text(explanation, 45)
            for line in lines[:3]:  # Max 3 lines
                text = self.font_small.render(line, True, (220, 220, 220))
                self.screen.blit(text, (panel_x, panel_y))
                panel_y += 15
            
            panel_y += 5
            
            # Confidence with color coding
            confidence = self.last_explanation.confidence
            conf_value = confidence.mean
            
            # Color based on confidence
            if conf_value < 0.3:
                conf_color = (100, 255, 100)  # Green = low risk/high confidence
            elif conf_value < 0.6:
                conf_color = (255, 255, 100)  # Yellow = medium
            else:
                conf_color = (255, 100, 100)  # Red = high risk/low confidence
            
            conf_text = f"Confidence: {conf_value:.2f}"
            text = self.font_small.render(conf_text, True, conf_color)
            self.screen.blit(text, (panel_x, panel_y))
            panel_y += 15
            
            # Confidence interval
            ci_text = f"95% CI: [{confidence.lower_bound:.2f}, {confidence.upper_bound:.2f}]"
            text = self.font_small.render(ci_text, True, (180, 180, 180))
            self.screen.blit(text, (panel_x, panel_y))
            
        else:
            # No explanation yet
            no_exp_text = self.font_small.render("Waiting for coordination decision...", True, (150, 150, 150))
            self.screen.blit(no_exp_text, (panel_x, panel_y))
    
    def _wrap_text(self, text: str, max_chars: int) -> List[str]:
        """
        Wrap text to fit within character limit.
        
        Args:
            text: Text to wrap
            max_chars: Maximum characters per line
            
        Returns:
            List of wrapped lines
        """
        words = text.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 <= max_chars:
                current_line.append(word)
                current_length += len(word) + 1
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
                current_length = len(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def _render_protocol_indicator(self, coordinator, timestep: int):
        """
        Render protocol indicator showing current coordination mode.
        
        NEW v2.2: Visual feedback for hybrid coordination protocol
        
        Args:
            coordinator: HybridCoordinator instance
            timestep: Current timestep
        """
        # Get current mode
        current_mode = coordinator.current_mode.value.upper()
        
        # Color coding by mode
        mode_colors = {
            'CENTRALIZED': (100, 255, 100),  # Green - safe, deterministic
            'AUCTION': (255, 255, 100),      # Yellow - moderate, flexible
            'COALITION': (255, 100, 100)     # Red - high-risk, collaborative
        }
        
        color = mode_colors.get(current_mode, (255, 255, 255))
        
        # Position: Top-left of screen (over grid)
        indicator_x = 20
        indicator_y = 20
        indicator_width = 280
        indicator_height = 50
        
        # Background box
        bg_rect = pygame.Rect(indicator_x, indicator_y, indicator_width, indicator_height)
        pygame.draw.rect(self.screen, (0, 0, 0, 180), bg_rect)  # Semi-transparent black
        pygame.draw.rect(self.screen, color, bg_rect, 3)  # Colored border
        
        # Mode text
        mode_text = self.font_large.render(f"MODE: {current_mode}", True, color)
        text_x = indicator_x + 10
        text_y = indicator_y + 8
        self.screen.blit(mode_text, (text_x, text_y))
        
        # Mode switch count
        switch_count = len(coordinator.mode_history)
        if switch_count > 0:
            switch_text = self.font_small.render(f"Switches: {switch_count}", True, (200, 200, 200))
            self.screen.blit(switch_text, (text_x, text_y + 28))
        
        # Mode switch timeline (below indicator)
        if coordinator.mode_history:
            self._render_mode_timeline(coordinator.mode_history, timestep, indicator_x, indicator_y + indicator_height + 10)
    
    def _render_mode_timeline(self, mode_history: List, current_timestep: int, start_x: int, start_y: int):
        """
        Render horizontal timeline showing mode switch history.
        
        Args:
            mode_history: List of (timestep, mode, reason) tuples
            current_timestep: Current simulation timestep
            start_x: X position to start timeline
            start_y: Y position to start timeline
        """
        if not mode_history:
            return
        
        # Timeline parameters
        timeline_width = 400
        timeline_height = 30
        circle_radius = 8
        
        # Background
        bg_rect = pygame.Rect(start_x, start_y, timeline_width, timeline_height)
        pygame.draw.rect(self.screen, (30, 30, 40), bg_rect)
        pygame.draw.rect(self.screen, (100, 100, 120), bg_rect, 1)
        
        # Title
        title = self.font_small.render("Mode History:", True, (200, 200, 200))
        self.screen.blit(title, (start_x + 5, start_y + 2))
        
        # Show last 10 switches
        recent_history = mode_history[-10:]
        
        if len(recent_history) > 0:
            # Calculate positions
            spacing = min(35, (timeline_width - 100) // len(recent_history))
            
            for i, (ts, mode, reason) in enumerate(recent_history):
                x_pos = start_x + 100 + (i * spacing)
                y_pos = start_y + timeline_height // 2
                
                # Mode color
                mode_colors = {
                    'centralized': (100, 255, 100),
                    'auction': (255, 255, 100),
                    'coalition': (255, 100, 100)
                }
                color = mode_colors.get(mode.value if hasattr(mode, 'value') else mode, (255, 255, 255))
                
                # Draw circle
                pygame.draw.circle(self.screen, color, (x_pos, y_pos), circle_radius)
                pygame.draw.circle(self.screen, (255, 255, 255), (x_pos, y_pos), circle_radius, 2)
                
                # Draw connecting line to next
                if i < len(recent_history) - 1:
                    next_x = start_x + 100 + ((i + 1) * spacing)
                    pygame.draw.line(self.screen, (100, 100, 120), (x_pos + circle_radius, y_pos), 
                                   (next_x - circle_radius, y_pos), 2)
                
                # Timestamp label (below circle)
                if i % 2 == 0:  # Only show every other to avoid crowding
                    ts_text = self.font_small.render(f"T{ts}", True, (150, 150, 150))
                    ts_rect = ts_text.get_rect(center=(x_pos, y_pos + 18))
                    self.screen.blit(ts_text, ts_rect)
    
    def _render_risk_indicator(self, risk_model, grid):
        """
        Render risk level indicator showing current average risk.
        
        Args:
            risk_model: Bayesian risk model
            grid: Environment grid
        """
        # Position: Top-right of screen
        indicator_x = self.window_width - 320
        indicator_y = 20
        indicator_width = 300
        indicator_height = 60
        
        # Calculate average risk across all cells
        total_risk = 0
        cell_count = 0
        max_risk = 0
        
        for x in range(grid.width):
            for y in range(grid.height):
                risk = risk_model.get_risk((x, y), "combined")
                total_risk += risk
                cell_count += 1
                max_risk = max(max_risk, risk)
        
        avg_risk = total_risk / cell_count if cell_count > 0 else 0
        
        # Background
        bg_rect = pygame.Rect(indicator_x, indicator_y, indicator_width, indicator_height)
        pygame.draw.rect(self.screen, (0, 0, 0, 180), bg_rect)
        pygame.draw.rect(self.screen, (150, 150, 150), bg_rect, 2)
        
        # Title
        title = self.font_normal.render("Risk Level", True, (255, 255, 255))
        self.screen.blit(title, (indicator_x + 10, indicator_y + 5))
        
        # Risk bar
        bar_x = indicator_x + 10
        bar_y = indicator_y + 30
        bar_width = indicator_width - 20
        bar_height = 20
        
        # Background bar
        pygame.draw.rect(self.screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
        
        # Risk fill (gradient from green to red)
        fill_width = int(bar_width * avg_risk)
        
        # Color based on risk level
        if avg_risk < 0.2:
            fill_color = (100, 255, 100)  # Green - LOW
        elif avg_risk < 0.5:
            fill_color = (255, 255, 100)  # Yellow - MODERATE
        else:
            fill_color = (255, 100, 100)  # Red - HIGH
        
        if fill_width > 0:
            pygame.draw.rect(self.screen, fill_color, (bar_x, bar_y, fill_width, bar_height))
        
        # Border
        pygame.draw.rect(self.screen, (200, 200, 200), (bar_x, bar_y, bar_width, bar_height), 2)
        
        # Threshold markers
        # LOW threshold at 0.2
        low_x = bar_x + int(bar_width * 0.2)
        pygame.draw.line(self.screen, (100, 255, 100), (low_x, bar_y), (low_x, bar_y + bar_height), 2)
        
        # MODERATE threshold at 0.5
        mod_x = bar_x + int(bar_width * 0.5)
        pygame.draw.line(self.screen, (255, 255, 100), (mod_x, bar_y), (mod_x, bar_y + bar_height), 2)
        
        # Risk value text
        risk_text = self.font_small.render(f"Avg: {avg_risk:.3f} | Max: {max_risk:.3f}", True, (220, 220, 220))
        self.screen.blit(risk_text, (bar_x, bar_y + bar_height + 3))
    
    def _render_communication_ranges(self, agents):
        """
        Render communication ranges for agents.
        
        Args:
            agents: List of agents
        """
        cell_size = GRID.CELL_SIZE
        comm_range = 15  # cells (from communication network)
        
        for agent in agents:
            x, y = agent.position
            center = (
                x * cell_size + cell_size // 2,
                y * cell_size + cell_size // 2
            )
            
            # Draw semi-transparent communication range circle
            range_radius = int(comm_range * cell_size)
            
            # Create surface for transparency
            comm_surface = pygame.Surface((range_radius * 2, range_radius * 2), pygame.SRCALPHA)
            
            # Draw circle on surface
            color = self._get_agent_color(agent.agent_type)
            pygame.draw.circle(comm_surface, (*color, 30), (range_radius, range_radius), range_radius)
            pygame.draw.circle(comm_surface, (*color, 100), (range_radius, range_radius), range_radius, 1)
            
            # Blit to grid surface
            self.grid_surface.blit(comm_surface, 
                                  (center[0] - range_radius, center[1] - range_radius))
    
    def cleanup(self):
        """Clean up pygame resources."""
        pygame.quit()
