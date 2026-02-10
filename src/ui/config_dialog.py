"""
Configuration Input Dialog
Simple GUI for manual parameter configuration before simulation starts.
"""

import pygame
from typing import Dict, Optional, Tuple


class ConfigDialog:
    """
    Interactive configuration dialog for simulation parameters.
    
    Allows user to input:
    - Grid width and height
    - Number of survivors
    - Hazard coverage percentage
    """
    
    def __init__(self):
        """Initialize the configuration dialog."""
        pygame.init()
        
        self.width = 600
        self.height = 500
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Simulation Configuration")
        
        # Fonts
        self.font_title = pygame.font.SysFont('Arial', 32, bold=True)
        self.font_label = pygame.font.SysFont('Arial', 20)
        self.font_input = pygame.font.SysFont('Arial', 24)
        self.font_button = pygame.font.SysFont('Arial', 22, bold=True)
        self.font_small = pygame.font.SysFont('Arial', 16)
        
        # Colors
        self.bg_color = (30, 30, 30)
        self.text_color = (255, 255, 255)
        self.input_bg = (50, 50, 50)
        self.input_active = (70, 70, 70)
        self.button_color = (50, 150, 50)
        self.button_hover = (70, 200, 70)
        
        # Input fields
        self.inputs = {
            'grid_width': {'value': '40', 'label': 'Grid Width (10-200)', 'active': False, 'rect': None},
            'grid_height': {'value': '30', 'label': 'Grid Height (10-200)', 'active': False, 'rect': None},
            'survivors': {'value': '8', 'label': 'Number of Survivors (1-50)', 'active': False, 'rect': None},
            'hazard_coverage': {'value': '10', 'label': 'Hazard Coverage % (0-50)', 'active': False, 'rect': None},
        }
        
        self.start_button_rect = None
        self.mouse_over_button = False
        
    def show(self) -> Optional[Dict]:
        """
        Display dialog and wait for user input.
        
        Returns:
            Dict with configuration or None if cancelled
        """
        clock = pygame.time.Clock()
        running = True
        
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                
                if event.type == pygame.KEYDOWN:
                    result = self._handle_keypress(event)
                    if result is not None:
                        return result
                    
                if event.type == pygame.MOUSEBUTTONDOWN:
                    result = self._handle_click(event.pos)
                    if result is not None:
                        return result
                        
                if event.type == pygame.MOUSEMOTION:
                    self._handle_mouse_motion(event.pos)
            
            # Render
            self._render()
            pygame.display.flip()
            clock.tick(30)
        
        return None
    
    def _handle_keypress(self, event):
        """Handle keyboard input."""
        # Check for Enter when no field is active - start simulation
        if event.key == pygame.K_RETURN:
            active_field = None
            for key, data in self.inputs.items():
                if data['active']:
                    active_field = key
                    break
            
            # If no field is active, or we're on the last field, start simulation
            if active_field is None:
                return self._validate_and_return()
            
            keys = list(self.inputs.keys())
            idx = keys.index(active_field)
            
            # If on last field, start simulation
            if idx == len(keys) - 1:
                data['active'] = False
                return self._validate_and_return()
            else:
                # Move to next input
                self.inputs[active_field]['active'] = False
                self.inputs[keys[idx + 1]]['active'] = True
                return None
        
        # Handle other keys for active fields
        for key, data in self.inputs.items():
            if data['active']:
                if event.key == pygame.K_BACKSPACE:
                    data['value'] = data['value'][:-1]
                elif event.key == pygame.K_TAB:
                    # Tab moves to next input
                    data['active'] = False
                    keys = list(self.inputs.keys())
                    idx = keys.index(key)
                    if idx < len(keys) - 1:
                        self.inputs[keys[idx + 1]]['active'] = True
                elif event.unicode.isdigit() and len(data['value']) < 4:
                    data['value'] += event.unicode
        
        return None
    
    def _handle_click(self, pos: Tuple[int, int]) -> Optional[Dict]:
        """Handle mouse clicks."""
        # Check input fields
        for key, data in self.inputs.items():
            if data['rect'] and data['rect'].collidepoint(pos):
                # Deactivate all others
                for k in self.inputs:
                    self.inputs[k]['active'] = False
                # Activate this one
                data['active'] = True
                return None
        
        # Check start button
        if self.start_button_rect and self.start_button_rect.collidepoint(pos):
            return self._validate_and_return()
        
        # Clicked outside - deactivate all
        for k in self.inputs:
            self.inputs[k]['active'] = False
        
        return None
    
    def _handle_mouse_motion(self, pos: Tuple[int, int]):
        """Handle mouse movement."""
        if self.start_button_rect:
            self.mouse_over_button = self.start_button_rect.collidepoint(pos)
    
    def _validate_and_return(self) -> Optional[Dict]:
        """Validate inputs and return configuration."""
        try:
            grid_width = int(self.inputs['grid_width']['value'] or '40')
            grid_height = int(self.inputs['grid_height']['value'] or '30')
            survivors = int(self.inputs['survivors']['value'] or '8')
            hazard_coverage = int(self.inputs['hazard_coverage']['value'] or '10')
            
            # Validation
            if not (10 <= grid_width <= 200):
                self._show_error("Grid width must be 10-200")
                return None
            if not (10 <= grid_height <= 200):
                self._show_error("Grid height must be 10-200")
                return None
            if not (1 <= survivors <= 50):
                self._show_error("Survivors must be 1-50")
                return None
            if not (0 <= hazard_coverage <= 50):
                self._show_error("Hazard coverage must be 0-50%")
                return None
            
            return {
                'grid_width': grid_width,
                'grid_height': grid_height,
                'survivors': survivors,
                'hazard_coverage': hazard_coverage,
            }
        except ValueError:
            self._show_error("Please enter valid numbers")
            return None
    
    def _show_error(self, message: str):
        """Show error message briefly."""
        error_text = self.font_label.render(message, True, (255, 100, 100))
        error_rect = error_text.get_rect(center=(self.width // 2, self.height - 60))
        self.screen.blit(error_text, error_rect)
        pygame.display.flip()
        pygame.time.wait(1500)
    
    def _render(self):
        """Render the dialog."""
        self.screen.fill(self.bg_color)
        
        # Title
        title = self.font_title.render("Simulation Configuration", True, self.text_color)
        title_rect = title.get_rect(center=(self.width // 2, 40))
        self.screen.blit(title, title_rect)
        
        # Instructions
        instructions = self.font_label.render("Click fields to edit. Press Enter on last field or click START", True, (180, 180, 180))
        inst_rect = instructions.get_rect(center=(self.width // 2, 85))
        self.screen.blit(instructions, inst_rect)
        
        # Input fields
        y = 130
        for key, data in self.inputs.items():
            # Label
            label = self.font_label.render(data['label'], True, self.text_color)
            self.screen.blit(label, (50, y))
            
            # Input box
            input_rect = pygame.Rect(50, y + 30, 500, 40)
            data['rect'] = input_rect
            
            # Background color based on active state
            bg_color = self.input_active if data['active'] else self.input_bg
            pygame.draw.rect(self.screen, bg_color, input_rect)
            pygame.draw.rect(self.screen, self.text_color, input_rect, 2)
            
            # Value text
            value_text = self.font_input.render(data['value'], True, self.text_color)
            self.screen.blit(value_text, (input_rect.x + 10, input_rect.y + 8))
            
            # Cursor if active
            if data['active']:
                cursor_x = input_rect.x + 15 + value_text.get_width()
                pygame.draw.line(self.screen, self.text_color, 
                               (cursor_x, input_rect.y + 8), 
                               (cursor_x, input_rect.y + 32), 2)
            
            y += 85
        
        # Start button
        button_width = 200
        button_height = 50
        button_x = (self.width - button_width) // 2
        button_y = self.height - 80
        
        self.start_button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        
        button_color = self.button_hover if self.mouse_over_button else self.button_color
        pygame.draw.rect(self.screen, button_color, self.start_button_rect, border_radius=10)
        
        button_text = self.font_button.render("START SIMULATION", True, self.text_color)
        button_text_rect = button_text.get_rect(center=self.start_button_rect.center)
        self.screen.blit(button_text, button_text_rect)
        
        # Hint below button
        hint_text = self.font_small.render("or press Enter", True, (150, 150, 150))
        hint_rect = hint_text.get_rect(center=(self.width // 2, button_y + button_height + 15))
        self.screen.blit(hint_text, hint_rect)
    
    def cleanup(self):
        """Clean up pygame resources."""
        pygame.quit()


def get_user_config() -> Optional[Dict]:
    """
    Show configuration dialog and get user input.
    
    Returns:
        Configuration dict or None if cancelled
    """
    dialog = ConfigDialog()
    config = dialog.show()
    dialog.cleanup()
    return config
