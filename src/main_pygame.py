"""
Main entry point for The Sunken Cathedral game - Pygame version.
Castle Adventure style text adventure with pygame-based retro terminal interface.
"""

import pygame
import sys
import time
from typing import Optional, List
from dataclasses import dataclass

from engine.display_pygame import PygameDisplay
from engine.world import World, Direction, create_test_world
from engine.player import Player
from engine.parser import Parser, CommandResult
from engine.difficulty import DifficultyManager, DifficultyLevel
from engine.pagination import Paginator, PagedContent, create_text_content
from engine.save_manager import SaveManager


@dataclass
class GameState:
    """Container for all game state."""
    world: World
    player: Player
    display: PygameDisplay
    parser: Parser
    difficulty_manager: DifficultyManager
    save_manager: SaveManager
    running: bool = True
    paused: bool = False
    last_message: str = ""
    message_timer: float = 0.0
    total_moves: int = 0


class Game:
    """
    Main game class for The Sunken Cathedral - Pygame version.
    Handles the game loop, pygame events, and display updates.
    """
    
    def __init__(self):
        """Initialize the game."""
        # Initialize game components
        self.state = GameState(
            world=create_test_world(),
            player=Player(starting_position=(10, 20)),  # Start in a good position in the entrance
            display=PygameDisplay(),
            parser=Parser(),
            difficulty_manager=DifficultyManager(),
            save_manager=SaveManager()
        )
        
        # Movement direction mapping for pygame keys (arrows only - no WASD to avoid conflicts with typing)
        self.direction_map = {
            pygame.K_UP: Direction.NORTH,
            pygame.K_DOWN: Direction.SOUTH,
            pygame.K_LEFT: Direction.WEST,
            pygame.K_RIGHT: Direction.EAST,
        }
        
        # Key repeat functionality for movement
        self.keys_held = set()
        self.last_move_time = 0
        self.move_delay = 0.15  # Seconds between moves when holding key
        
        # Game timing
        self.clock = pygame.time.Clock()
        self.last_update = time.time()
        
        # Check for continue game option
        if not self._show_continue_game_option():
            # Show difficulty selection and welcome screens for new game
            self._show_difficulty_selection_new()
            self._show_welcome_screen()
    
    def _show_continue_game_option(self) -> bool:
        """
        Show continue game option if autosave exists.
        
        Returns:
            True if game was continued (loaded), False if starting new game
        """
        if not self.state.save_manager.has_autosave():
            return False
        
        # Clear screen
        self.state.display.screen.fill((0, 0, 0))
        
        # Show continue game dialog
        title = "CONTINUE GAME"
        message = "An autosave was found. Would you like to continue?"
        options = ["Continue from autosave", "Start new game"]
        
        selected_index = 0  # Default to continue
        
        while True:
            # Clear screen
            self.state.display.screen.fill((0, 0, 0))
            
            # Draw title
            self.state.display.draw_text_at_pixel(title, 50, 50, (255, 255, 85))
            
            # Draw message
            self.state.display.draw_text_at_pixel(message, 50, 100, (255, 255, 255))
            
            # Draw options with selection highlighting
            for i, option in enumerate(options):
                y_pos = 150 + i * 30
                color = (255, 255, 255)
                
                if i == selected_index:
                    # Draw selection background
                    selection_rect = pygame.Rect(45, y_pos - 5, 400, 25)
                    pygame.draw.rect(self.state.display.screen, (32, 32, 64), selection_rect)
                    color = (255, 255, 255)
                    option = f"> {option}"
                else:
                    option = f"  {option}"
                
                self.state.display.draw_text_at_pixel(option, 50, y_pos, color)
            
            # Draw controls
            controls = "[^][v] select [Enter] confirm [Esc] new game"
            self.state.display.draw_text_at_pixel(controls, 50, 250, (128, 128, 128))
            
            pygame.display.flip()
            
            # Handle input
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._quit_game()
                    return True
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected_index = (selected_index - 1) % len(options)
                    elif event.key == pygame.K_DOWN:
                        selected_index = (selected_index + 1) % len(options)
                    elif event.key == pygame.K_RETURN:
                        if selected_index == 0:  # Continue
                            return self._load_autosave()
                        else:  # New game
                            return False
                    elif event.key == pygame.K_ESCAPE:
                        return False  # Start new game
    
    def _load_autosave(self) -> bool:
        """
        Load the autosave file.
        
        Returns:
            True if load successful, False otherwise
        """
        save_data = self.state.save_manager.load_game()  # None = autosave
        
        if save_data is None:
            self._set_message("Failed to load autosave. Starting new game.", 3.0)
            return False
        
        if self.state.save_manager.apply_save_to_game_state(save_data, self.state):
            self._set_message(f"Game loaded! Total moves: {save_data.total_moves}", 3.0)
            return True
        else:
            self._set_message("Failed to apply save data. Starting new game.", 3.0)
            return False
    
    def _autosave(self) -> None:
        """Perform an autosave (silent)."""
        self.state.save_manager.save_game(self.state)  # None = autosave
    
    def _show_difficulty_selection(self) -> None:
        """Show the difficulty selection screen with pagination."""
        selected_index = 0
        current_page = 0
        difficulties = list(DifficultyLevel)
        
        # Calculate how many lines we can fit on screen
        line_height = 25
        start_y = 50
        max_lines = (self.state.display.screen_height - start_y - 100) // line_height  # Leave space for controls
        
        while True:
            # Clear screen
            self.state.display.screen.fill((0, 0, 0))
            
            if current_page == 0:
                # Page 1: Title and first two difficulties
                content_lines = [
                    "THE SUNKEN CATHEDRAL",
                    "",
                    "SELECT DIFFICULTY LEVEL",
                    "",
                ]
                
                # Add first two difficulties
                for i in range(2):
                    if i < len(difficulties):
                        level = difficulties[i]
                        settings = self.state.difficulty_manager.get_all_difficulties()[level]
                        marker = ">>> " if i == selected_index else "    "
                        content_lines.append(f"{marker}{settings.name}")
                        content_lines.append(f"    {settings.description}")
                        content_lines.append("")
                
                content_lines.extend([
                    "",
                    "Controls:",
                    "- Up/Down: Select difficulty",
                    "- Right Arrow: Next page",
                    "- Enter: Confirm selection",
                    "- ESC: Quit"
                ])
                
            else:
                # Page 2: Remaining difficulties
                content_lines = [
                    "DIFFICULTY SELECTION (Page 2)",
                    "",
                ]
                
                # Add remaining difficulties
                for i in range(2, len(difficulties)):
                    level = difficulties[i]
                    settings = self.state.difficulty_manager.get_all_difficulties()[level]
                    marker = ">>> " if i == selected_index else "    "
                    content_lines.append(f"{marker}{settings.name}")
                    content_lines.append(f"    {settings.description}")
                    content_lines.append("")
                
                content_lines.extend([
                    "",
                    "Controls:",
                    "- Up/Down: Select difficulty",
                    "- Left Arrow: Previous page", 
                    "- Enter: Confirm selection",
                    "- ESC: Quit"
                ])
            
            # Display the content
            for i, line in enumerate(content_lines):
                if i * line_height + start_y > self.state.display.screen_height - 50:
                    break  # Don't draw beyond screen
                
                color = (255, 255, 85) if i == 0 else (255, 255, 255)  # Title in yellow
                if line.startswith(">>>"):
                    color = (85, 255, 85)  # Selected in green
                
                self.state.display.draw_text_at_pixel(line, 50, start_y + i * line_height, color)
            
            # Add page indicator
            page_indicator = f"Page {current_page + 1} of 2"
            self.state.display.draw_text_at_pixel(page_indicator, 50, self.state.display.screen_height - 30, (128, 128, 128))
            
            pygame.display.flip()
            
            # Handle input
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected_index = (selected_index - 1) % len(difficulties)
                        # Switch pages if needed
                        if selected_index < 2 and current_page == 1:
                            current_page = 0
                        elif selected_index >= 2 and current_page == 0:
                            current_page = 1
                    elif event.key == pygame.K_DOWN:
                        selected_index = (selected_index + 1) % len(difficulties)
                        # Switch pages if needed
                        if selected_index < 2 and current_page == 1:
                            current_page = 0
                        elif selected_index >= 2 and current_page == 0:
                            current_page = 1
                    elif event.key == pygame.K_LEFT:
                        if current_page > 0:
                            current_page = 0
                    elif event.key == pygame.K_RIGHT:
                        if current_page < 1:
                            current_page = 1
                    elif event.key == pygame.K_RETURN:
                        # Set the selected difficulty
                        selected_difficulty = difficulties[selected_index]
                        self.state.difficulty_manager.set_difficulty(selected_difficulty)
                        return
                    elif event.key == pygame.K_ESCAPE:
                        self._quit_game()
                        return
    
    def _show_difficulty_selection_new(self) -> None:
        """Show the difficulty selection screen using the pagination system."""
        difficulties = list(DifficultyLevel)
        
        # Build content for pagination
        content_lines = [
            "THE SUNKEN CATHEDRAL",
            "",
            "SELECT DIFFICULTY LEVEL",
            "",
            "Choose your preferred challenge level:",
            ""
        ]
        
        content_colors = [
            (255, 255, 85),  # Title in yellow
            (255, 255, 255),
            (255, 255, 85),  # Subtitle in yellow
            (255, 255, 255),
            (255, 255, 255),
            (255, 255, 255)
        ]
        
        selectable_indices = []
        
        # Add difficulty options
        for i, level in enumerate(difficulties):
            settings = self.state.difficulty_manager.get_all_difficulties()[level]
            
            # Add selectable option line
            option_line = f">>> {settings.name}"
            content_lines.append(option_line)
            content_colors.append((85, 255, 85))  # Green for selectable
            selectable_indices.append(len(content_lines) - 1)
            
            # Add description
            content_lines.append(f"    {settings.description}")
            content_colors.append((200, 200, 200))  # Light gray for description
            
            # Add spacing
            content_lines.append("")
            content_colors.append((255, 255, 255))
        
        # Add instructions
        content_lines.extend([
            "",
            "Instructions:",
            "- Use Up/Down arrows to select difficulty",
            "- Press Enter to confirm your choice",
            "- Press ESC to quit the game",
            "",
            "You can change difficulty anytime during the game",
            "using the SETTINGS command."
        ])
        
        for _ in range(8):  # Add colors for instruction lines
            content_colors.append((128, 128, 128))  # Gray for instructions
        
        # Create paged content
        paged_content = PagedContent(
            lines=content_lines,
            colors=content_colors,
            title=""  # Title is already in the content
        )
        
        # Create paginator
        paginator = Paginator(self.state.display, lines_per_page=15)
        
        # Show with selection
        def on_difficulty_selected(line_index: int):
            # Find which difficulty was selected
            selection_index = selectable_indices.index(line_index)
            selected_difficulty = difficulties[selection_index]
            self.state.difficulty_manager.set_difficulty(selected_difficulty)
        
        result = paginator.show_paged_content(
            paged_content, 
            on_selection=on_difficulty_selected,
            selectable_lines=selectable_indices
        )
        
        if result is None:
            # User pressed ESC - quit
            pygame.quit()
            sys.exit()
    
    def _show_welcome_screen(self) -> None:
        """Show the game introduction screen using pagination."""
        welcome_text = [
            "A Castle Adventure Style Game",
            "",
            "You are the last Lamplighter of the Meridian Chain,",
            "heir to seven generations of mystical guardians who tend",
            "the Beacon Lights upon the Threshold Cliffs.",
            "",
            "CONTROLS:",
            "- Arrow Keys: Move around",
            "- Any letter: Start typing a command", 
            "- ESC or Q: Quit the game",
            "",
            "IMPORTANT:",
            "- Your lantern oil decreases with each action",
            "- Find fonts (F) to refill with 'FILL LANTERN'",
            "- Take your time - no time pressure!",
            "- Use 'SETTINGS' to change difficulty anytime",
            "- Use 'HELP' command for more information",
            "- Use 'SAVE' to save your progress",
            "- Use 'LOAD' to load a saved game",
            "",
            "GAME SYMBOLS:",
            "- ☺ : You, the Lamplighter",
            "- ▓ █ : Walls, Rubble",
            "- ≈ : Deep Water (impassable without oil)",
            "- L : Lore Item (Scroll, Tablet)",
            "- G : Prayer Geode",
            "- S : Drowned Sorrow (Spirit)",
            "- F : Consecrated Font (Oil Source)",
            "",
            "THE STORY:",
            "",
            "For seven generations, your bloodline has maintained the",
            "Beacon Chain—thirteen mystical lighthouses that stand upon",
            "the Threshold Cliffs, their flames visible only to those",
            "born with the Sight of Sorrows. These are no ordinary lights",
            "that guide earthly ships, but consecrated flames that help",
            "lost souls cross from the realm of the living to eternal rest.",
            "",
            "Your family's duty was passed down through ancient bloodline",
            "bonds, inscribed in your very soul at birth. Each Lamplighter",
            "can feel the sacred duty as a constant, gentle pull—like a",
            "compass needle drawn to magnetic north. You have felt this",
            "calling all your life, though its full meaning remained hidden",
            "until this fateful night.",
            "",
            "Three nights ago, a storm of impossible magnitude struck",
            "your coastal watch. The tempest howled not with earthly winds",
            "but with the voices of countless trapped spirits. When dawn",
            "broke, the sea had drawn back, revealing spires of ancient",
            "stone that had lain hidden beneath the waves for centuries.",
            "",
            "The Sunken Cathedral now rises from the exposed seabed,",
            "its gothic towers piercing the surface like accusing fingers.",
            "From its highest spire pulses a beacon of spectral blue—",
            "a light that you come to realize only you can see, calling",
            "with the same mystical frequency as your sacred flames.",
            "",
            "Armed with the Meridian Light—your ancestral lantern whose",
            "consecrated oil creates a sphere of blessed air around its",
            "bearer—you descend from the cliffs to walk upon the sea floor",
            "as if it were dry land. The lantern's power protects you",
            "from crushing depths and allows you to breathe within the",
            "Cathedral's flooded halls, where ancient magic maintains",
            "pockets of sacred air.",
            "",
            "The beacon calls to you with increasing urgency. You must",
            "reach it. You must understand its sorrow. You must fulfill",
            "the duty that seven generations of your family died to",
            "protect—and give the Cathedral's trapped souls their peace."
        ]
        
        # Create paginated content
        content = create_text_content(
            welcome_text, 
            title="THE SUNKEN CATHEDRAL",
            title_color=(255, 255, 85),
            text_color=(255, 255, 255)
        )
        
                # Show with auto-continue (auto-calculate lines per page)
        paginator = Paginator(self.state.display)
        result = paginator.show_paged_content(content, auto_continue=True)
        
        if result == "QUIT_REQUESTED":
            # User quit during welcome screen
            self._quit_game()
    
    def show_paginated_text(self, text_lines: List[str], title: str = "") -> None:
        """
        Helper method to show any paginated text with auto-continue.
        
        Args:
            text_lines: List of text lines to display
            title: Optional title for the content
        """
        content = create_text_content(text_lines, title)
        paginator = Paginator(self.state.display)  # Auto-calculate lines per page
        result = paginator.show_paged_content(content, auto_continue=True)
        
        if result == "QUIT_REQUESTED":
            self._quit_game()
    
    def _show_help_screen(self) -> None:
        """Show the help screen using pagination."""
        help_text = [
            "AVAILABLE COMMANDS:",
            "",
            "TAKE [item]    - Pick up an item",
            "DROP [item]    - Drop an item from inventory",
            "USE [item]     - Use or equip an item", 
            "READ [item]    - Read a scroll or examine text",
            "FILL LANTERN   - Refill lantern at a font",
            "SHINE LANTERN  - Use lantern to pass barriers",
            "SOOTHE SPIRIT  - Calm a drowned sorrow",
            "GO [direction] - Move in a direction",
            "SETTINGS       - Open settings menu",
            "SAVE           - Save your game",
            "LOAD           - Load a saved game",
            "HELP           - Show this help",
            "",
            "CONTROLS:",
            "- Arrow keys: Move around",
            "- Any letter: Start typing a command",
            "- F11: Toggle fullscreen mode",
            "- ESC or Q: Quit the game",
            "",
            "GAMEPLAY:",
            "- Your lantern oil decreases with each action you take",
            "- Movement and commands consume oil based on difficulty",
            "- Find fonts (F) to refill your lantern with FILL LANTERN",
            "- Take your time - the game pauses when you're thinking!",
            "- Use SETTINGS to change difficulty level anytime",
            "",
            "GAME SYMBOLS:",
            "- ☺ : You, the Lamplighter",
            "- ▓ █ : Walls, Rubble",
            "- ≈ : Deep Water (impassable without oil)",
            "- L : Lore Item (Scroll, Tablet)", 
            "- G : Prayer Geode",
            "- S : Drowned Sorrow (Spirit)",
            "- F : Consecrated Font (Oil Source)",
            "",
            "TIPS:",
            "- Approach spirits carefully - wrong interactions drain oil",
            "- Read scrolls to learn the Cathedral's lore",
            "- Deep water cannot be entered without oil in your lantern",
            "- You have 4 inventory slots - manage them wisely",
            "- Different difficulties have different oil consumption rates"
        ]
        
        self.show_paginated_text(help_text, "HELP - THE SUNKEN CATHEDRAL")
    
    def start(self) -> None:
        """Start the game."""
        try:
            self._game_loop()
        except Exception as e:
            print(f"Game error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self._cleanup()
    
    def _cleanup(self) -> None:
        """Clean up resources."""
        if hasattr(self.state, 'display') and self.state.display:
            self.state.display.cleanup()
    
    def _handle_pygame_events(self) -> None:
        """Handle all pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.state.running = False
                
            elif event.type == pygame.KEYDOWN:
                self._handle_keydown(event)
                # Track movement keys being held
                if event.key in self.direction_map:
                    self.keys_held.add(event.key)
                    
            elif event.type == pygame.KEYUP:
                # Track movement keys being released
                if event.key in self.direction_map:
                    self.keys_held.discard(event.key)
    
    def _handle_keydown(self, event) -> None:
        """Handle keydown events."""
        # Handle quit keys
        if event.key == pygame.K_ESCAPE:
            self._quit_game()
            return
        elif event.key == pygame.K_q and not self.state.display.is_typing_command:
            self._quit_game()
            return
        
        # Handle fullscreen toggle
        elif event.key == pygame.K_F11:
            self.state.display.toggle_fullscreen()
            return
        
        # If typing a command, handle command input
        if self.state.display.is_typing_command:
            self._handle_command_input_key(event)
        else:
            # Handle movement and command triggers
            self._handle_gameplay_key(event)
    
    def _handle_command_input_key(self, event) -> None:
        """Handle keyboard input while typing a command."""
        if event.key == pygame.K_RETURN:
            # Execute the command
            command = self.state.display.finish_command_input()
            self._execute_command(command)
            
        elif event.key == pygame.K_BACKSPACE:
            self.state.display.backspace_command()
            
        elif event.key == pygame.K_ESCAPE:
            self.state.display.cancel_command_input()
            
        elif event.unicode and event.unicode.isprintable():
            # Add character to command
            self.state.display.add_command_char(event.unicode)
    
    def _handle_gameplay_key(self, event) -> None:
        """Handle keyboard input during normal gameplay."""
        # Handle movement keys
        if event.key in self.direction_map:
            direction = self.direction_map[event.key]
            if self.state.player.try_move(direction, self.state.world):
                # Movement successful - consume oil for movement
                if not self.state.player.consume_oil_for_action("move", self.state.difficulty_manager):
                    self._handle_oil_depletion()
                # Increment move counter and autosave
                self.state.total_moves += 1
                self._autosave()
                # Set timing for key repeat
                self.last_move_time = time.time()
            else:
                self._set_message("You can't go that way.", 2.0)
        
        # Handle command input trigger (any letter key starts command mode)
        elif event.unicode and event.unicode.isalpha():
            self.state.display.start_command_input()
            self.state.display.add_command_char(event.unicode)
    
    def _execute_command(self, command: str) -> None:
        """Execute a parsed command."""
        if not command.strip():
            return
            
        verb, noun = self.state.parser.parse_command(command)
        
        if verb:
            result, message = self.state.parser.execute_command(verb, noun, self.state)
            
            # Handle special commands
            if message == "OPEN_SETTINGS_MENU":
                self._show_settings_menu()
            elif message == "SHOW_HELP_SCREEN":
                self._show_help_screen()
            elif message == "OPEN_SAVE_MENU":
                self._show_save_menu()
            elif message == "OPEN_LOAD_MENU":
                self._show_load_menu()
            elif message == "SHOW_SCROLL_CONTENT":
                self._show_scroll_content()
            else:
                # For reading/lore messages, display much longer
                if "You read" in message or "scroll" in message.lower() or len(message) > 200:
                    self._set_message(message, 50.0)  # 10x longer for reading
                else:
                    self._set_message(message, 5.0)
            
            # Consume oil for executing a command (except help, settings, save, load)
            if verb not in ["help", "settings", "save", "load"]:
                if not self.state.player.consume_oil_for_action("command", self.state.difficulty_manager):
                    self._handle_oil_depletion()
                # Increment move counter and autosave for action commands
                self.state.total_moves += 1
                self._autosave()
        else:
            self._set_message("I don't understand that command. Type 'help' for help.", 3.0)
    
    def _set_message(self, message: str, duration: float) -> None:
        """Set a temporary message to display."""
        self.state.last_message = message
        self.state.message_timer = time.time() + duration
    
    def _quit_game(self) -> None:
        """Quit the game gracefully with confirmation."""
        if self._show_quit_confirmation():
            self._show_farewell_and_quit()
    
    def _show_quit_confirmation(self) -> bool:
        """Show quit confirmation dialog. Returns True if user confirms quit."""
        # Clear screen
        self.state.display.screen.fill((0, 0, 0))
        
        # Show confirmation dialog
        title = "QUIT GAME"
        message = "Are you sure you want to quit?"
        saved_notice = "(Your progress has been saved)"
        options = ["Yes, quit the game", "No, continue playing"]
        
        selected_index = 1  # Default to "No"
        
        while True:
            # Clear screen
            self.state.display.screen.fill((0, 0, 0))
            
            # Draw title
            self.state.display.draw_text_at_pixel(title, 50, 50, (255, 255, 85))
            
            # Draw message  
            self.state.display.draw_text_at_pixel(message, 50, 100, (255, 255, 255))
            
            # Draw saved notice
            self.state.display.draw_text_at_pixel(saved_notice, 50, 130, (128, 255, 128))
            
            # Draw options with selection highlighting
            for i, option in enumerate(options):
                y_pos = 170 + i * 30  # Moved down to accommodate saved notice
                color = (255, 255, 255)
                
                if i == selected_index:
                    # Draw selection background
                    selection_rect = pygame.Rect(45, y_pos - 5, 400, 25)
                    pygame.draw.rect(self.state.display.screen, (32, 32, 64), selection_rect)
                    color = (255, 255, 255)
                    option = f"> {option}"
                else:
                    option = f"  {option}"
                
                self.state.display.draw_text_at_pixel(option, 50, y_pos, color)
            
            # Draw controls
            controls = "[^][v] select [Enter] confirm [Esc] cancel"
            self.state.display.draw_text_at_pixel(controls, 50, 250, (128, 128, 128))
            
            pygame.display.flip()
            
            # Handle input
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return True  # Force quit if window closed
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected_index = (selected_index - 1) % len(options)
                    elif event.key == pygame.K_DOWN:
                        selected_index = (selected_index + 1) % len(options)
                    elif event.key == pygame.K_RETURN:
                        return selected_index == 0  # True if "Yes" selected
                    elif event.key == pygame.K_ESCAPE:
                        return False  # Cancel quit
    
    def _show_farewell_and_quit(self) -> None:
        """Show farewell message for 5 seconds then quit."""
        # Clear screen
        self.state.display.screen.fill((0, 0, 0))
        
        # Farewell messages (multiple lines for atmosphere)
        farewell_lines = [
            "",
            "",
            "The light of your lantern fades...",
            "",
            "The ancient waters reclaim their silence...", 
            "",
            "Until the Cathedral calls again...",
            "",
            "",
            "Farewell, Lamplighter."
        ]
        
        # Show farewell message
        line_height = 30
        start_y = 150
        
        for i, line in enumerate(farewell_lines):
            color = (255, 255, 85) if "Lamplighter" in line else (255, 255, 255)
            self.state.display.draw_text_at_pixel(line, 50, start_y + i * line_height, color)
        
        pygame.display.flip()
        
        # Wait for 5 seconds
        start_time = time.time()
        while time.time() - start_time < 5.0:
            # Handle events to prevent window from becoming unresponsive
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    # Allow immediate quit if user closes window
                    pygame.quit()
                    sys.exit()
            time.sleep(0.1)
        
        # Actually quit
        self.state.running = False
        self._cleanup()
        sys.exit()
    
    def _game_loop(self) -> None:
        """Main game loop."""
        while self.state.running:
            current_time = time.time()
            
            # Handle pygame events
            self._handle_pygame_events()
            
            # Update game state
            self._update_game(current_time)
            
            # Render the game
            self._render_game()
            
            # Control frame rate (30 FPS)
            self.clock.tick(30)
    
    def _update_game(self, current_time: float) -> None:
        """Update game state."""
        # Handle continuous movement when keys are held
        if not self.state.display.is_typing_command and self.keys_held:
            if current_time - self.last_move_time >= self.move_delay:
                # Move in the direction of the most recently pressed key
                if self.keys_held:
                    key = next(iter(self.keys_held))  # Get any held key
                    direction = self.direction_map[key]
                    
                    if self.state.player.try_move(direction, self.state.world):
                        # Movement successful - consume oil for movement
                        if not self.state.player.consume_oil_for_action("move", self.state.difficulty_manager):
                            self._handle_oil_depletion()
                        # Increment move counter and autosave
                        self.state.total_moves += 1
                        self._autosave()
                        self.last_move_time = current_time
                    else:
                        # Hit wall, show message but don't keep trying
                        self.keys_held.clear()
                        self._set_message("You can't go that way.", 2.0)
        
        # Clear expired messages
        if self.state.message_timer > 0 and current_time > self.state.message_timer:
            self.state.last_message = ""
            self.state.message_timer = 0
    
    def _handle_oil_depletion(self) -> None:
        """Handle when lantern oil is completely depleted."""
        self._set_message("Your lantern flickers and dies. The crushing darkness overwhelms you...", 10.0)
        # In a full game, this would reset player to last safe location
        # For now, we'll just continue but warn the player
    
    def _render_game(self) -> None:
        """Render the current game state."""
        current_room = self.state.world.get_current_room()
        if not current_room:
            return
        
        # Render the full screen
        self.state.display.full_render(
            room_map=current_room.room_map,
            player_pos=self.state.player.get_position(),
            lantern_oil=self.state.player.get_lantern_oil(),
            geode=self.state.player.get_current_geode(),
            inventory=self.state.player.get_inventory(),
            message=self.state.last_message,
            command_input=self.state.display.command_input if self.state.display.is_typing_command else "",
            difficulty_name=self.state.difficulty_manager.get_difficulty_name(),
            room_items=current_room.items
        )
    
    def _show_settings_menu(self) -> None:
        """Show the settings menu."""
        selected_index = 0
        menu_options = ["Difficulty Level", "Back to Game"]
        
        while True:
            # Clear screen
            self.state.display.screen.fill((0, 0, 0))
            
            # Title
            title_lines = [
                "SETTINGS MENU",
                "",
                f"Current Difficulty: {self.state.difficulty_manager.get_difficulty_name()}",
                "",
            ]
            
            # Menu options
            option_lines = []
            for i, option in enumerate(menu_options):
                marker = ">>> " if i == selected_index else "    "
                option_lines.append(f"{marker}{option}")
            
            option_lines.extend([
                "",
                "Controls:",
                "- Up/Down arrows: Navigate menu",
                "- Enter: Select option",
                "- ESC: Back to game"
            ])
            
            all_lines = title_lines + option_lines
            line_height = 30
            start_y = 100
            
            for i, line in enumerate(all_lines):
                color = (255, 255, 85) if i == 0 else (255, 255, 255)  # Title in yellow
                if line.startswith(">>>"):
                    color = (85, 255, 85)  # Selected in green
                
                self.state.display.draw_text_at_pixel(line, 50, start_y + i * line_height, color)
            
            pygame.display.flip()
            
            # Handle input
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._quit_game()
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected_index = (selected_index - 1) % len(menu_options)
                    elif event.key == pygame.K_DOWN:
                        selected_index = (selected_index + 1) % len(menu_options)
                    elif event.key == pygame.K_RETURN:
                        if selected_index == 0:  # Difficulty Level
                            self._show_difficulty_menu()
                        elif selected_index == 1:  # Back to Game
                            return
                    elif event.key == pygame.K_ESCAPE:
                        return
    
    def _show_difficulty_menu(self) -> None:
        """Show the difficulty selection menu using pagination."""
        difficulties = list(DifficultyLevel)
        current_difficulty = self.state.difficulty_manager.current_difficulty
        
        # Build content
        content_lines = [
            "CHANGE DIFFICULTY",
            "",
            f"Current: {self.state.difficulty_manager.get_difficulty_name()}",
            "",
            "Select a new difficulty level:",
            ""
        ]
        
        content_colors = [
            (255, 255, 85),  # Title
            (255, 255, 255),
            (85, 255, 255),  # Current difficulty in cyan
            (255, 255, 255),
            (255, 255, 255),
            (255, 255, 255)
        ]
        
        selectable_indices = []
        
        # Add difficulty options
        for i, level in enumerate(difficulties):
            settings = self.state.difficulty_manager.get_all_difficulties()[level]
            current_marker = " (CURRENT)" if level == current_difficulty else ""
            
            # Add selectable option line
            option_line = f">>> {settings.name}{current_marker}"
            content_lines.append(option_line)
            if level == current_difficulty:
                content_colors.append((85, 255, 255))  # Current in cyan
            else:
                content_colors.append((85, 255, 85))  # Others in green
            selectable_indices.append(len(content_lines) - 1)
            
            # Add description
            content_lines.append(f"    {settings.description}")
            content_colors.append((200, 200, 200))
            
            # Add spacing
            content_lines.append("")
            content_colors.append((255, 255, 255))
        
        # Add instructions
        content_lines.extend([
            "",
            "Instructions:",
            "- Use Up/Down arrows to select difficulty",
            "- Press Enter to apply new difficulty",
            "- Press ESC to cancel"
        ])
        
        for _ in range(5):
            content_colors.append((128, 128, 128))
        
        # Create paged content
        paged_content = PagedContent(
            lines=content_lines,
            colors=content_colors,
            title=""
        )
        
        # Create paginator
        paginator = Paginator(self.state.display, lines_per_page=15)
        
        # Show with selection
        def on_difficulty_selected(line_index: int):
            selection_index = selectable_indices.index(line_index)
            selected_difficulty = difficulties[selection_index]
            self.state.difficulty_manager.set_difficulty(selected_difficulty)
            self._set_message(f"Difficulty changed to {self.state.difficulty_manager.get_difficulty_name()}!", 3.0)
        
        result = paginator.show_paged_content(
            paged_content,
            on_selection=on_difficulty_selected,
            selectable_lines=selectable_indices
        )
        
        if result == "QUIT_REQUESTED":
            self._quit_game()
    
    def _show_save_menu(self) -> None:
        """Show the save game menu."""
        save_slots = self.state.save_manager.get_all_save_slots_info()
        
        # Build content for display
        content_lines = [
            "SAVE GAME",
            "",
            "Select a save slot:",
            ""
        ]
        
        content_colors = [
            (255, 255, 85),  # Title
            (255, 255, 255),
            (255, 255, 255),
            (255, 255, 255)
        ]
        
        selectable_indices = []
        
        for slot_info in save_slots:
            # Add selectable slot line
            if slot_info.exists:
                slot_line = f">>> Slot {slot_info.slot_number}: {slot_info.formatted_date}"
                detail_line = f"    Moves: {slot_info.total_moves}, Difficulty: {slot_info.difficulty}"
                content_lines.extend([slot_line, detail_line, ""])
                content_colors.extend([(85, 255, 85), (200, 200, 200), (255, 255, 255)])
            else:
                slot_line = f">>> Slot {slot_info.slot_number}: Empty"
                content_lines.extend([slot_line, ""])
                content_colors.extend([(85, 255, 85), (255, 255, 255)])
            
            if slot_info.exists:
                selectable_indices.append(len(content_lines) - 3)  # The slot line (before detail and blank)
            else:
                selectable_indices.append(len(content_lines) - 2)  # The slot line (before blank)
        
        # Add instructions
        content_lines.extend([
            "",
            "Instructions:",
            "- Use Up/Down arrows to select slot",
            "- Press Enter to save to selected slot",
            "- Press ESC to cancel"
        ])
        
        for _ in range(5):
            content_colors.append((128, 128, 128))
        
        # Create paged content
        paged_content = PagedContent(
            lines=content_lines,
            colors=content_colors,
            title=""
        )
        
        # Create paginator
        paginator = Paginator(self.state.display, lines_per_page=15)
        
        # Show with selection
        def on_slot_selected(line_index: int):
            # Find which slot was selected
            slot_number = None
            for i, idx in enumerate(selectable_indices):
                if idx == line_index:
                    slot_number = i + 1
                    break
            
            if slot_number:
                if self.state.save_manager.save_game(self.state, slot_number):
                    self._set_message(f"Game saved to slot {slot_number}!", 3.0)
                else:
                    self._set_message(f"Failed to save to slot {slot_number}.", 3.0)
        
        result = paginator.show_paged_content(
            paged_content,
            on_selection=on_slot_selected,
            selectable_lines=selectable_indices
        )
        
        if result == "QUIT_REQUESTED":
            self._quit_game()
    
    def _show_load_menu(self) -> None:
        """Show the load game menu."""
        save_slots = self.state.save_manager.get_all_save_slots_info()
        
        # Filter to only existing saves
        existing_slots = [slot for slot in save_slots if slot.exists]
        
        if not existing_slots:
            self._set_message("No saved games found.", 3.0)
            return
        
        # Build content for display
        content_lines = [
            "LOAD GAME",
            "",
            "Select a save to load:",
            ""
        ]
        
        content_colors = [
            (255, 255, 85),  # Title
            (255, 255, 255),
            (255, 255, 255),
            (255, 255, 255)
        ]
        
        selectable_indices = []
        
        for slot_info in existing_slots:
            slot_line = f">>> Slot {slot_info.slot_number}: {slot_info.formatted_date}"
            detail_line = f"    Moves: {slot_info.total_moves}, Difficulty: {slot_info.difficulty}"
            
            content_lines.extend([slot_line, detail_line, ""])
            content_colors.extend([(85, 255, 85), (200, 200, 200), (255, 255, 255)])
            
            selectable_indices.append(len(content_lines) - 3)  # The slot line
        
        # Add instructions
        content_lines.extend([
            "",
            "Instructions:",
            "- Use Up/Down arrows to select save",
            "- Press Enter to load selected save",
            "- Press ESC to cancel"
        ])
        
        for _ in range(5):
            content_colors.append((128, 128, 128))
        
        # Create paged content
        paged_content = PagedContent(
            lines=content_lines,
            colors=content_colors,
            title=""
        )
        
        # Create paginator
        paginator = Paginator(self.state.display, lines_per_page=15)
        
        # Show with selection
        def on_slot_selected(line_index: int):
            # Find which slot was selected
            slot_number = None
            for i, idx in enumerate(selectable_indices):
                if idx == line_index:
                    slot_number = existing_slots[i].slot_number
                    break
            
            if slot_number:
                save_data = self.state.save_manager.load_game(slot_number)
                if save_data and self.state.save_manager.apply_save_to_game_state(save_data, self.state):
                    self._set_message(f"Game loaded from slot {slot_number}!", 3.0)
                else:
                    self._set_message(f"Failed to load from slot {slot_number}.", 3.0)
        
        result = paginator.show_paged_content(
            paged_content,
            on_selection=on_slot_selected,
            selectable_lines=selectable_indices
        )
        
        if result == "QUIT_REQUESTED":
            self._quit_game()
    
    def _show_scroll_content(self) -> None:
        """Show the worn scroll content with full-screen display and decorations."""
        # Create scroll content with much more detailed lore
        scroll_text = [
            "From the final testament of Keeper Aldara Westmere,",
            "Last Lightkeeper of the Meridian Chain",
            "Recorded in the thirteenth year of the Deep Silence",
            "",
            "To my successor, whose blood calls to the ancient duty:",
            "",
            "Know this truth, for it shall be your burden as it was mine,",
            "and my father's, and his father's before him, stretching back",
            "seven generations to the founding of our vigil.",
            "",
            "We are the Lamplighters, keepers of the Consecrated Flames.",
            "Our family tends not ordinary lighthouses, but the Beacon Chain—",
            "thirteen mystical lights that burn upon the Threshold Cliffs,",
            "visible only to those born with the Sight of Sorrows.",
            "",
            "These lights serve no earthly vessel, for they guide souls",
            "across the ethereal waters that separate the living from",
            "the realm of unquiet dead. Each flame burns with oil blessed",
            "by ancient rites, fed from fonts that spring from holy ground.",
            "",
            "But the sea holds deeper mysteries than even we knew.",
            "",
            "A great maelstrom arose from the depths, unlike any natural",
            "phenomenon our records describe. The very ocean floor convulsed,",
            "and the ancient barriers that held back the past were broken.",
            "When the waters finally stilled, what had been hidden for",
            "centuries was laid bare beneath the moonlight.",
            "",
            "The Sunken Cathedral rises from the depths, its spires",
            "piercing the waves like accusatory fingers. This is no",
            "natural structure—it predates our order, predates memory",
            "itself. Its stones whisper with accumulated sorrow,",
            "its halls echo with prayers that were never finished.",
            "",
            "From its highest tower burns a beacon of spectral blue,",
            "visible only to those who bear our bloodline. It calls",
            "with the same frequency as our sacred flames, but its",
            "purpose is not guidance—it is a cry for help.",
            "",
            "The pull grows stronger each night. I feel it now as I write,",
            "tugging at my very soul. Soon, I must answer its summons,",
            "as you too shall when your time comes. The Cathedral's beacon",
            "does not merely shine—it mourns, and that mourning speaks",
            "of ancient wrongs that demand correction, of souls trapped",
            "between realms who cannot find their way to rest.",
            "",
            "To reach the Cathedral, you must carry our ancestral lantern,",
            "the Meridian Light, whose flame burns with oil consecrated",
            "at the founding of our order. This lantern creates a sphere",
            "of sacred air that allows the bearer to walk upon the sea",
            "floor as if it were dry land, protected from the crushing",
            "depths by the same power that maintains the air within",
            "the Cathedral's submerged halls.",
            "",
            "Trust in the Light, for it is the only protection against",
            "the Drowned Sorrows—spirits of those who perished in the",
            "Cathedral's fall. They hunger for the warmth of living",
            "souls but can be calmed by one who carries the proper",
            "blessing and speaks the words of ancient peace.",
            "",
            "Remember always: the lights must never die. In darkness,",
            "sorrow grows, and the barriers between realms weaken.",
            "Follow the beacon's call with courage, for you carry",
            "not just our family's duty, but the hopes of all souls",
            "who seek final rest.",
            "",
            "Go with the blessing of seven generations, child of the light.",
            "Bring peace to the deep.",
            "",
            "—Aldara Westmere",
            "Keeper of the Meridian Chain",
            "Last of the Old Watch"
        ]
        
        # Create decorated scroll content with ASCII borders
        decorated_content = self._create_scroll_decoration(scroll_text)
        
        # Show with pagination
        content = create_text_content(
            decorated_content,
            title="THE WORN SCROLL",
            title_color=(255, 255, 85),
            text_color=(210, 180, 140)  # Parchment color
        )
        
        paginator = Paginator(self.state.display)
        result = paginator.show_paged_content(content, auto_continue=True)
        
        if result == "QUIT_REQUESTED":
            self._quit_game()
    
    def _create_scroll_decoration(self, text_lines: List[str]) -> List[str]:
        """Add ASCII scroll decorations to text content with proper word wrapping."""
        decorated_lines = []
        
        # Top scroll decoration (narrower to fit on screen)
        decorated_lines.extend([
            "  ╔══════════════════════════════════════════════════════════╗",
            " ╔╣                    ANCIENT SCROLL                     ╠╗",
            "╔╝                                                        ╚╗",
            "║                                                          ║",
        ])
        
        # Content with side decorations and proper word wrapping
        max_content_width = 54  # Leave room for scroll borders and padding
        
        for line in text_lines:
            if len(line.strip()) == 0:
                # Empty line
                decorated_lines.append("║" + " " * 58 + "║")
            elif len(line) <= max_content_width:
                # Line fits, just center or left-align it
                if len(line.strip()) < 40:
                    # Center short lines
                    padding = (58 - len(line)) // 2
                    decorated_line = "║" + " " * padding + line + " " * (58 - padding - len(line)) + "║"
                else:
                    # Left-align longer lines with padding
                    decorated_line = "║  " + line.ljust(54) + "  ║"
                decorated_lines.append(decorated_line)
            else:
                # Line is too long, wrap it properly at word boundaries
                words = line.split()
                current_line = ""
                
                for word in words:
                    # Check if adding this word would exceed the limit
                    test_line = current_line + (" " if current_line else "") + word
                    if len(test_line) <= max_content_width:
                        current_line = test_line
                    else:
                        # Current line is full, add it and start a new line
                        if current_line:
                            decorated_line = "║  " + current_line.ljust(54) + "  ║"
                            decorated_lines.append(decorated_line)
                        current_line = word
                
                # Add the last line if there's anything left
                if current_line:
                    decorated_line = "║  " + current_line.ljust(54) + "  ║"
                    decorated_lines.append(decorated_line)
        
        # Bottom scroll decoration
        decorated_lines.extend([
            "║                                                          ║",
            "╚╗                                                        ╔╝",
            " ╚╣                     END OF SCROLL                    ╠╝",
            "  ╚══════════════════════════════════════════════════════════╝"
        ])
        
        return decorated_lines


def main() -> None:
    """Main entry point."""
    try:
        game = Game()
        game.start()
    except Exception as e:
        print(f"Error starting game: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main() 