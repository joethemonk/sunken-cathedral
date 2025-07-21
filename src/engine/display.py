"""
Display system for The Sunken Cathedral game.
Handles ASCII rendering with ANSI color codes and split-screen layout.
"""

import os
import sys
from typing import List, Dict, Tuple, Optional
from enum import Enum


class Color(Enum):
    """ANSI color codes for game elements."""
    RESET = "\033[0m"
    PLAYER = "\033[33m"      # Yellow
    WATER = "\033[34m"       # Blue  
    WALLS = "\033[37m"       # White
    WALLS_ALT = "\033[90m"   # Gray
    ITEMS = "\033[36m"       # Cyan
    SPIRITS = "\033[35m"     # Magenta
    SACRED = "\033[32m"      # Green
    DANGER = "\033[31m"      # Red


class Display:
    """
    Manages the split-screen display for the game.
    Left side: ASCII game world
    Right side: Status panel
    """
    
    def __init__(self, map_width: int = 43, map_height: int = 20, status_width: int = 25):
        """
        Initialize the display system.
        
        Args:
            map_width: Width of the map display area
            map_height: Height of the map display area  
            status_width: Width of the status panel
        """
        self.map_width = map_width
        self.map_height = map_height
        self.status_width = status_width
        self.total_width = map_width + 3 + status_width  # +3 for separator
        
        # Screen buffer for efficient updates
        self.screen_buffer: List[List[str]] = []
        self.previous_buffer: List[List[str]] = []
        
        self._initialize_buffers()
        
    def _initialize_buffers(self) -> None:
        """Initialize the screen buffers."""
        self.screen_buffer = [[' ' for _ in range(self.total_width)] 
                             for _ in range(self.map_height + 5)]  # +5 for command area
        self.previous_buffer = [[' ' for _ in range(self.total_width)] 
                               for _ in range(self.map_height + 5)]
    
    def clear_screen(self) -> None:
        """Clear the terminal screen."""
        os.system('clear' if os.name == 'posix' else 'cls')
        
    def hide_cursor(self) -> None:
        """Hide the terminal cursor."""
        sys.stdout.write("\033[?25l")
        sys.stdout.flush()
        
    def show_cursor(self) -> None:
        """Show the terminal cursor."""
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()
        
    def set_cursor_position(self, row: int, col: int) -> None:
        """Move cursor to specific position."""
        sys.stdout.write(f"\033[{row + 1};{col + 1}H")
        sys.stdout.flush()
        
    def render_map(self, room_map: List[str], player_pos: Tuple[int, int]) -> None:
        """
        Render the game map with the player position.
        
        Args:
            room_map: List of strings representing the room layout
            player_pos: (row, col) position of the player
        """
        for row_idx, line in enumerate(room_map):
            if row_idx >= self.map_height:
                break
                
            # Clear the row in buffer
            for col in range(self.map_width):
                self.screen_buffer[row_idx][col] = ' '
                
            # Render each character with appropriate color
            for col_idx, char in enumerate(line):
                if col_idx >= self.map_width:
                    break
                    
                # Check if player is at this position
                if (row_idx, col_idx) == player_pos:
                    colored_char = f"{Color.PLAYER.value}☺{Color.RESET.value}"
                else:
                    colored_char = self._colorize_char(char)
                    
                # Store in buffer (we'll handle coloring during actual rendering)
                self.screen_buffer[row_idx][col_idx] = colored_char
    
    def _colorize_char(self, char: str) -> str:
        """Apply appropriate color to a character based on its meaning."""
        color_map = {
            '▓': Color.WALLS.value,
            '█': Color.WALLS.value,
            '▒': Color.WALLS_ALT.value,
            '≈': Color.WATER.value,
            'L': Color.ITEMS.value,
            'G': Color.ITEMS.value,
            'S': Color.SPIRITS.value,
            'F': Color.SACRED.value,
        }
        
        if char in color_map:
            return f"{color_map[char]}{char}{Color.RESET.value}"
        else:
            return char
    
    def render_status_panel(self, lantern_oil: float, geode: Optional[str], 
                           inventory: List[Optional[str]], 
                           current_command: str = "") -> None:
        """
        Render the status panel on the right side.
        
        Args:
            lantern_oil: Current oil percentage (0-100)
            geode: Currently equipped geode or None
            inventory: List of inventory items (4 slots)
            current_command: Command being typed
        """
        status_col = self.map_width + 3  # Start after map and separator
        
        # Title
        title = "The Sunken Cathedral"
        self._write_to_buffer(0, status_col, title)
        
        # Oil status
        oil_color = Color.DANGER.value if lantern_oil < 20 else Color.RESET.value
        oil_text = f"LANTERN OIL: {oil_color}{lantern_oil:.0f}%{Color.RESET.value}"
        self._write_to_buffer(2, status_col, oil_text)
        
        # Geode status
        geode_text = f"GEODE: {geode if geode else '[None]'}"
        self._write_to_buffer(3, status_col, geode_text)
        
        # Inventory
        self._write_to_buffer(5, status_col, "INVENTORY:")
        for i, item in enumerate(inventory):
            item_text = f"- {item if item else '[empty]'}"
            self._write_to_buffer(6 + i, status_col, item_text)
            
        # Command input area (at bottom)
        if current_command:
            self._write_to_buffer(self.map_height + 1, 0, f"> {current_command}_")
        else:
            self._write_to_buffer(self.map_height + 1, 0, "> ")
    
    def _write_to_buffer(self, row: int, col: int, text: str) -> None:
        """Write text to the screen buffer at specified position."""
        if row >= len(self.screen_buffer) or col >= len(self.screen_buffer[0]):
            return
            
        for i, char in enumerate(text):
            if col + i < len(self.screen_buffer[row]):
                self.screen_buffer[row][col + i] = char
    
    def render_separator(self) -> None:
        """Render the vertical separator between map and status panel."""
        sep_col = self.map_width
        for row in range(self.map_height):
            self._write_to_buffer(row, sep_col, "  |  ")
    
    def update_display(self) -> None:
        """Update only the changed parts of the display for efficiency."""
        changes_made = False
        
        for row in range(len(self.screen_buffer)):
            for col in range(len(self.screen_buffer[row])):
                current_char = self.screen_buffer[row][col]
                previous_char = self.previous_buffer[row][col]
                
                if current_char != previous_char:
                    if not changes_made:
                        changes_made = True
                        
                    self.set_cursor_position(row, col)
                    sys.stdout.write(current_char)
                    self.previous_buffer[row][col] = current_char
        
        if changes_made:
            sys.stdout.flush()
    
    def full_render(self, room_map: List[str], player_pos: Tuple[int, int],
                   lantern_oil: float, geode: Optional[str], 
                   inventory: List[Optional[str]], current_command: str = "") -> None:
        """
        Perform a complete screen render.
        
        Args:
            room_map: The current room's ASCII map
            player_pos: Player's position as (row, col)
            lantern_oil: Current oil percentage
            geode: Currently equipped geode
            inventory: Player's inventory items
            current_command: Command being typed
        """
        # Clear buffer
        self._initialize_buffers()
        
        # Render all components
        self.render_map(room_map, player_pos)
        self.render_separator()
        self.render_status_panel(lantern_oil, geode, inventory, current_command)
        
        # Update display
        self.update_display()
    
    def display_message(self, message: str, row_offset: int = 0) -> None:
        """
        Display a message below the map area.
        
        Args:
            message: The message to display
            row_offset: Additional row offset from the standard message area
        """
        message_row = self.map_height + 2 + row_offset
        self._write_to_buffer(message_row, 0, message)
        self.update_display()
        
    def clear_message_area(self) -> None:
        """Clear the message area below the map."""
        for row in range(self.map_height + 2, len(self.screen_buffer)):
            for col in range(self.map_width):
                self.screen_buffer[row][col] = ' ' 