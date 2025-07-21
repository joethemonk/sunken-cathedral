"""
Main entry point for The Sunken Cathedral game.
Castle Adventure style text adventure with real-time movement and command parsing.
"""

import sys
import time
import threading
import signal
from typing import Optional
from dataclasses import dataclass

try:
    from pynput import keyboard
except ImportError:
    print("Error: pynput not installed. Please run: pip install pynput")
    sys.exit(1)

from engine.display import Display
from engine.world import World, Direction, create_test_world
from engine.player import Player
from engine.parser import Parser, CommandResult


@dataclass
class GameState:
    """Container for all game state."""
    world: World
    player: Player
    display: Display
    parser: Parser
    running: bool = True
    paused: bool = False
    last_message: str = ""
    message_timer: float = 0.0


class Game:
    """
    Main game class for The Sunken Cathedral.
    Handles the game loop, input processing, and display updates.
    """
    
    def __init__(self):
        """Initialize the game."""
        # Initialize game components
        self.state = GameState(
            world=create_test_world(),
            player=Player(starting_position=(10, 20)),  # Start in a good position in the entrance
            display=Display(),
            parser=Parser()
        )
        
        # Movement direction mapping
        self.direction_map = {
            keyboard.Key.up: Direction.NORTH,
            keyboard.Key.down: Direction.SOUTH,
            keyboard.Key.left: Direction.WEST,
            keyboard.Key.right: Direction.EAST
        }
        
        # Input handling
        self.keyboard_listener: Optional[keyboard.Listener] = None
        self.command_thread: Optional[threading.Thread] = None
        self.waiting_for_command = False
        
        # Game timing
        self.last_update = time.time()
        self.update_frequency = 30  # 30 FPS for smooth movement
        
        # Setup signal handler for graceful exit
        signal.signal(signal.SIGINT, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle Ctrl+C gracefully."""
        self.state.running = False
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        sys.exit(0)
    
    def start(self) -> None:
        """Start the game."""
        try:
            self._setup_display()
            self._start_input_handling()
            self._game_loop()
        except KeyboardInterrupt:
            pass
        finally:
            self._cleanup()
    
    def _setup_display(self) -> None:
        """Initialize the display system."""
        self.state.display.clear_screen()
        self.state.display.hide_cursor()
        self._show_initial_message()
    
    def _show_initial_message(self) -> None:
        """Show the game introduction."""
        intro_text = ("Welcome to The Sunken Cathedral\n\n"
                     "You are the last Lamplighter, drawn by a sorrowful beacon\n"
                     "from the depths of the sea. Use arrow keys to move,\n"
                     "type commands to interact with the world.\n\n"
                     "CONTROLS:\n"
                     "- Arrow keys: Move around\n"
                     "- Any letter: Start typing a command\n"
                     "- ESC or Q: Quit the game\n"
                     "- Type 'help' for a list of commands\n\n"
                     "Press Enter to begin...")
        
        print(intro_text)
        input()  # Wait for keypress
        self.state.display.clear_screen()
    
    def _start_input_handling(self) -> None:
        """Start the keyboard input listener."""
        self.keyboard_listener = keyboard.Listener(
            on_press=self._on_key_press,
            on_release=self._on_key_release
        )
        self.keyboard_listener.start()
    
    def _on_key_press(self, key) -> None:
        """Handle key press events."""
        if not self.state.running:
            return
            
        # Handle quit keys
        if key == keyboard.Key.esc:
            self._quit_game()
            return
        elif hasattr(key, 'char') and key.char and key.char.lower() == 'q':
            if not self.state.paused:  # Only quit with 'q' if not typing a command
                self._quit_game()
                return
            
        if self.state.paused:
            return
            
        # Handle movement keys
        if key in self.direction_map:
            direction = self.direction_map[key]
            if self.state.player.try_move(direction, self.state.world):
                # Movement successful - no message needed
                pass
            else:
                self._set_message("You can't go that way.", 2.0)
        
        # Handle command input trigger (any letter key starts command mode)
        elif hasattr(key, 'char') and key.char and key.char.isalpha():
            if not self.waiting_for_command:
                self._start_command_input(key.char)
    
    def _on_key_release(self, key) -> None:
        """Handle key release events."""
        pass
    
    def _start_command_input(self, first_char: str) -> None:
        """Start command input mode."""
        self.waiting_for_command = True
        self.state.paused = True
        
        # Start command input in a separate thread
        self.command_thread = threading.Thread(
            target=self._handle_command_input,
            args=(first_char,),
            daemon=True
        )
        self.command_thread.start()
    
    def _handle_command_input(self, first_char: str) -> None:
        """Handle command input in a separate thread."""
        try:
            # Stop keyboard listener to avoid conflicts
            if self.keyboard_listener:
                self.keyboard_listener.stop()
            
            # Show current game state before command input
            print("\n" + "="*50)
            print("COMMAND MODE - Type your command and press Enter")
            print("="*50)
            
            # Get the command
            full_command = self.state.parser.get_command_input(first_char)
            
            # Parse and execute the command
            verb, noun = self.state.parser.parse_command(full_command)
            
            if verb:
                result, message = self.state.parser.execute_command(verb, noun, self.state)
                self._set_message(message, 5.0)
            else:
                self._set_message("I don't understand that command. Type 'help' for help.", 3.0)
                
        except Exception as e:
            self._set_message(f"Error processing command: {str(e)}", 3.0)
        finally:
            # Restart keyboard listener
            self._start_input_handling()
            self.waiting_for_command = False
            self.state.paused = False
            
            # Clear screen and force full re-render
            self.state.display.clear_screen()
    
    def _set_message(self, message: str, duration: float) -> None:
        """Set a temporary message to display."""
        self.state.last_message = message
        self.state.message_timer = time.time() + duration
    
    def _quit_game(self) -> None:
        """Quit the game gracefully."""
        self.state.running = False
        self._set_message("Farewell, Lamplighter...", 1.0)
    
    def _game_loop(self) -> None:
        """Main game loop."""
        while self.state.running:
            current_time = time.time()
            delta_time = current_time - self.last_update
            
            # Update at fixed frequency
            if delta_time >= 1.0 / self.update_frequency:
                self._update_game(delta_time)
                self._render_game()
                self.last_update = current_time
            else:
                # Sleep briefly to prevent busy waiting
                time.sleep(0.001)
    
    def _update_game(self, delta_time: float) -> None:
        """Update game state."""
        if not self.state.paused:
            # Update lantern oil consumption
            if not self.state.player.update_oil_consumption():
                # Oil depleted - handle game over condition
                self._handle_oil_depletion()
        
        # Clear expired messages
        if self.state.message_timer > 0 and time.time() > self.state.message_timer:
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
        
        # Get current command being typed (if any)
        current_command = ""
        if self.state.parser.is_typing:
            current_command = self.state.parser.current_command
        
        # Render the full screen
        self.state.display.full_render(
            room_map=current_room.room_map,
            player_pos=self.state.player.get_position(),
            lantern_oil=self.state.player.get_lantern_oil(),
            geode=self.state.player.get_current_geode(),
            inventory=self.state.player.get_inventory(),
            current_command=current_command
        )
        
        # Display any active message
        if self.state.last_message:
            self.state.display.display_message(self.state.last_message)
    
    def _cleanup(self) -> None:
        """Clean up resources."""
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        self.state.display.show_cursor()
        self.state.display.clear_screen()
        print("Thanks for playing The Sunken Cathedral!")


def main() -> None:
    """Main entry point."""
    print("The Sunken Cathedral - A Castle Adventure Style Game")
    print("=" * 50)
    
    try:
        game = Game()
        game.start()
    except Exception as e:
        print(f"Error starting game: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 