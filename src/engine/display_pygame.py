"""
Pygame-based display system for The Sunken Cathedral game.
Creates a retro terminal-like interface with full control over rendering and input.
"""

import pygame
import sys
from typing import List, Optional, Tuple
from enum import Enum


class Color:
    """Color definitions for the retro terminal look."""
    # Background colors (dark theme)
    BLACK = (0, 0, 0)
    DARK_GRAY = (32, 32, 32)
    
    # Text colors (bright on dark)
    WHITE = (255, 255, 255)
    GRAY = (128, 128, 128)
    
    # Game element colors (matching ANSI codes)
    PLAYER = (255, 255, 85)      # Bright Yellow
    WATER = (85, 85, 255)        # Bright Blue  
    WALLS = (255, 255, 255)      # White
    WALLS_ALT = (128, 128, 128)  # Gray
    ITEMS = (85, 255, 255)       # Bright Cyan
    SPIRITS = (255, 85, 255)     # Bright Magenta
    SACRED = (85, 255, 85)       # Bright Green
    DANGER = (255, 85, 85)       # Bright Red


class PygameDisplay:
    """
    Pygame-based display system that mimics a retro computer terminal.
    Maintains the split-screen layout: game map on left, status panel on right.
    """
    
    def __init__(self, map_width: int = 43, map_height: int = 18, status_width: int = 25):
        """
        Initialize the pygame display system.
        
        Args:
            map_width: Width of the map display area in characters
            map_height: Height of the map display area in characters
            status_width: Width of the status panel in characters
        """
        pygame.init()
        
        # Display dimensions
        self.map_width = map_width
        self.map_height = map_height
        self.status_width = status_width
        self.total_width = map_width + 3 + status_width  # +3 for separator
        
        # Font settings for retro terminal look
        self.char_width = 12
        self.char_height = 20
        self.font_size = 16
        
        # Try to load a monospace font, fall back to default
        try:
            self.font = pygame.font.Font("assets/fonts/mono.ttf", self.font_size)
        except:
            # Use system monospace font
            self.font = pygame.font.Font(None, self.font_size)
            # Try some common monospace fonts
            for font_name in ['consolas', 'courier', 'monaco', 'menlo']:
                try:
                    self.font = pygame.font.SysFont(font_name, self.font_size)
                    break
                except:
                    continue
        
        # Calculate actual character dimensions from font
        test_surface = self.font.render('M', True, Color.WHITE)
        self.char_width = test_surface.get_width()
        self.char_height = test_surface.get_height()
        
        # Screen dimensions
        self.screen_width = self.total_width * self.char_width + 40  # +40 for padding
        self.screen_height = (self.map_height + 8) * self.char_height + 40  # +8 for UI space
        
        # Create the display window with fullscreen support
        self.is_fullscreen = False
        self.windowed_size = (self.screen_width, self.screen_height)
        self.screen = pygame.display.set_mode(
            self.windowed_size, 
            pygame.RESIZABLE | pygame.SCALED
        )
        pygame.display.set_caption("The Sunken Cathedral")
        
        # Set window icon if available
        try:
            icon = pygame.image.load("assets/icon.png")
            pygame.display.set_icon(icon)
        except:
            pass  # Icon file not found, that's okay
        
        # Display areas
        self.map_area = pygame.Rect(20, 20, map_width * self.char_width, map_height * self.char_height)
        self.status_area = pygame.Rect(
            20 + (map_width + 3) * self.char_width, 
            20, 
            status_width * self.char_width, 
            map_height * self.char_height
        )
        self.message_area = pygame.Rect(
            20, 
            20 + (map_height + 1) * self.char_height,
            self.total_width * self.char_width,
            4 * self.char_height
        )
        
        # Game state
        self.current_message = ""
        self.command_input = ""
        self.is_typing_command = False
        
        # Clear screen to black
        self.screen.fill(Color.BLACK)
        pygame.display.flip()
    
    def get_color_for_char(self, char: str) -> Tuple[int, int, int]:
        """Get the appropriate color for a game character."""
        color_map = {
            '▓': Color.WALLS,
            '█': Color.WALLS,
            '▒': Color.WALLS_ALT,
            '≈': Color.WATER,
            'L': Color.ITEMS,
            'G': Color.ITEMS,
            'S': Color.SPIRITS,
            'F': Color.SACRED,
            '☺': Color.PLAYER,
        }
        return color_map.get(char, Color.WHITE)
    
    def draw_text(self, text: str, x: int, y: int, color: Tuple[int, int, int] = Color.WHITE) -> None:
        """
        Draw text at the specified character position.
        
        Args:
            text: Text to draw
            x: Character column position
            y: Character row position
            color: RGB color tuple
        """
        pixel_x = x * self.char_width + self.map_area.left
        pixel_y = y * self.char_height + self.map_area.top
        
        text_surface = self.font.render(text, True, color)
        self.screen.blit(text_surface, (pixel_x, pixel_y))
    
    def draw_text_at_pixel(self, text: str, x: int, y: int, color: Tuple[int, int, int] = Color.WHITE) -> None:
        """Draw text at exact pixel coordinates."""
        text_surface = self.font.render(text, True, color)
        self.screen.blit(text_surface, (x, y))
    
    def render_map(self, room_map: List[str], player_pos: Tuple[int, int], room_items: dict = None) -> None:
        """
        Render the game map with the player position and dynamic items.
        
        Args:
            room_map: List of strings representing the room layout
            player_pos: (row, col) position of the player
            room_items: Dictionary of {position: item_name} for dynamic items
        """
        # Clear map area
        pygame.draw.rect(self.screen, Color.BLACK, self.map_area)
        
        if room_items is None:
            room_items = {}
        
        for row_idx, line in enumerate(room_map):
            if row_idx >= self.map_height:
                break
                
            for col_idx, char in enumerate(line):
                if col_idx >= self.map_width:
                    break
                
                # Check if player is at this position
                if (row_idx, col_idx) == player_pos:
                    self.draw_text('☺', col_idx, row_idx, Color.PLAYER)
                # Check if there's an item at this position
                elif (row_idx, col_idx) in room_items:
                    item_name = room_items[(row_idx, col_idx)]
                    if "geode" in item_name.lower():
                        self.draw_text('G', col_idx, row_idx, Color.ITEMS)
                    elif "scroll" in item_name.lower():
                        self.draw_text('L', col_idx, row_idx, Color.ITEMS)
                    else:
                        # Default to 'I' for unknown items
                        self.draw_text('I', col_idx, row_idx, Color.ITEMS)
                else:
                    color = self.get_color_for_char(char)
                    self.draw_text(char, col_idx, row_idx, color)
    
    def render_status_panel(self, lantern_oil: float, geode: Optional[str], 
                           inventory: List[Optional[str]], difficulty_name: str = "Hard") -> None:
        """
        Render the status panel on the right side.
        
        Args:
            lantern_oil: Current oil percentage (0-100)
            geode: Currently equipped geode or None
            inventory: List of inventory items (4 slots)
        """
        # Clear status area
        pygame.draw.rect(self.screen, Color.BLACK, self.status_area)
        
        # Calculate starting position for status text
        status_x = self.status_area.left
        status_y = self.status_area.top
        line_height = self.char_height
        
        # Title
        self.draw_text_at_pixel("The Sunken Cathedral", status_x, status_y, Color.WHITE)
        
        # Oil status with color coding
        oil_color = Color.DANGER if lantern_oil < 20 else Color.WHITE
        oil_text = f"LANTERN OIL: {lantern_oil:.0f}%"
        self.draw_text_at_pixel(oil_text, status_x, status_y + line_height * 2, oil_color)
        
        # Geode status
        geode_text = f"GEODE: {geode if geode else '[None]'}"
        self.draw_text_at_pixel(geode_text, status_x, status_y + line_height * 3, Color.WHITE)
        
        # Difficulty level
        difficulty_text = f"DIFFICULTY: {difficulty_name}"
        self.draw_text_at_pixel(difficulty_text, status_x, status_y + line_height * 4, Color.GRAY)
        
        # Inventory
        self.draw_text_at_pixel("INVENTORY:", status_x, status_y + line_height * 6, Color.WHITE)
        for i, item in enumerate(inventory):
            item_text = f"- {item if item else '[empty]'}"
            item_color = Color.ITEMS if item else Color.GRAY
            self.draw_text_at_pixel(item_text, status_x, status_y + line_height * (7 + i), item_color)
    
    def render_separator(self) -> None:
        """Render the vertical separator between map and status panel."""
        sep_x = self.map_area.right + 10
        sep_y = self.map_area.top
        sep_height = self.map_area.height
        
        # Draw a simple vertical line
        pygame.draw.line(self.screen, Color.GRAY, 
                        (sep_x, sep_y), 
                        (sep_x, sep_y + sep_height), 2)
    
    def render_message_area(self, message: str = "", command_input: str = "") -> None:
        """
        Render the message and command input area at the bottom.
        
        Args:
            message: Current message to display
            command_input: Current command being typed
        """
        # Clear message area
        pygame.draw.rect(self.screen, Color.BLACK, self.message_area)
        
        msg_x = self.message_area.left
        msg_y = self.message_area.top
        line_height = self.char_height
        
        # Display current message
        if message:
            # Split message into lines if too long
            max_chars = self.total_width - 2
            lines = []
            words = message.split(' ')
            current_line = ""
            
            for word in words:
                if len(current_line + word + " ") <= max_chars:
                    current_line += word + " "
                else:
                    if current_line:
                        lines.append(current_line.strip())
                    current_line = word + " "
            
            if current_line:
                lines.append(current_line.strip())
            
            # Draw message lines
            for i, line in enumerate(lines[:3]):  # Max 3 lines
                self.draw_text_at_pixel(line, msg_x, msg_y + i * line_height, Color.WHITE)
        
        # Command input area
        if self.is_typing_command:
            prompt = f"> {command_input}_"
            self.draw_text_at_pixel(prompt, msg_x, msg_y + 3 * line_height, Color.SACRED)
        else:
            self.draw_text_at_pixel("> ", msg_x, msg_y + 3 * line_height, Color.GRAY)
    
    def full_render(self, room_map: List[str], player_pos: Tuple[int, int],
                   lantern_oil: float, geode: Optional[str], 
                   inventory: List[Optional[str]], message: str = "", command_input: str = "", 
                   difficulty_name: str = "Hard", room_items: dict = None) -> None:
        """
        Perform a complete screen render.
        
        Args:
            room_map: The current room's ASCII map
            player_pos: Player's position as (row, col)
            lantern_oil: Current oil percentage
            geode: Currently equipped geode
            inventory: Player's inventory items
            message: Current message to display
            command_input: Current command being typed
            room_items: Dictionary of {position: item_name} for dynamic items
        """
        # Clear entire screen
        self.screen.fill(Color.BLACK)
        
        # Render all components
        self.render_map(room_map, player_pos, room_items)
        self.render_separator()
        self.render_status_panel(lantern_oil, geode, inventory, difficulty_name)
        self.render_message_area(message, command_input)
        
        # Update display
        pygame.display.flip()
    
    def set_message(self, message: str) -> None:
        """Set the current message to display."""
        self.current_message = message
    
    def start_command_input(self) -> None:
        """Start command input mode."""
        self.is_typing_command = True
        self.command_input = ""
    
    def add_command_char(self, char: str) -> None:
        """Add a character to the current command."""
        if len(self.command_input) < 50:  # Reasonable limit
            self.command_input += char
    
    def backspace_command(self) -> None:
        """Remove the last character from the command."""
        if self.command_input:
            self.command_input = self.command_input[:-1]
    
    def finish_command_input(self) -> str:
        """Finish command input and return the command."""
        command = self.command_input
        self.command_input = ""
        self.is_typing_command = False
        return command
    
    def cancel_command_input(self) -> None:
        """Cancel command input."""
        self.command_input = ""
        self.is_typing_command = False
    
    def toggle_fullscreen(self) -> None:
        """Toggle between fullscreen and windowed mode."""
        if self.is_fullscreen:
            # Switch to windowed mode
            self.screen = pygame.display.set_mode(
                self.windowed_size, 
                pygame.RESIZABLE | pygame.SCALED
            )
            self.is_fullscreen = False
        else:
            # Switch to fullscreen mode
            self.screen = pygame.display.set_mode(
                (0, 0), 
                pygame.FULLSCREEN | pygame.SCALED
            )
            self.is_fullscreen = True
        
        # Set caption again (sometimes needed after mode change)
        pygame.display.set_caption("The Sunken Cathedral")
    
    def cleanup(self) -> None:
        """Clean up pygame resources."""
        pygame.quit() 