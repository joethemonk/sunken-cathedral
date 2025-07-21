"""Test file for The Sunken Cathedral game - Player action simulation tests."""

import sys
import os
from typing import Optional
from dataclasses import dataclass

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from engine.world import World, Direction, create_test_world
from engine.player import Player
from engine.parser import Parser, CommandResult
from engine.difficulty import DifficultyManager, DifficultyLevel


@dataclass
class TestGameState:
    """Minimal game state for testing without UI."""
    world: World
    player: Player
    parser: Parser
    difficulty_manager: DifficultyManager
    total_moves: int = 0


class TestGame:
    """Test game class that simulates player actions without UI."""
    
    def __init__(self):
        """Initialize test game state."""
        self.state = TestGameState(
            world=create_test_world(),
            player=Player(starting_position=(10, 20)),
            parser=Parser(),
            difficulty_manager=DifficultyManager()
        )
    
    def move_player(self, direction: Direction) -> bool:
        """Move player in specified direction."""
        success = self.state.player.try_move(direction, self.state.world)
        if success:
            self.state.total_moves += 1
            # Consume oil for movement
            self.state.player.consume_oil_for_action("move", self.state.difficulty_manager)
        return success
    
    def execute_command(self, command_text: str) -> tuple[CommandResult, str]:
        """Execute a command and return the result."""
        verb, noun = self.state.parser.parse_command(command_text)
        if verb:
            result, message = self.state.parser.execute_command(verb, noun, self.state)
            
            # Don't consume oil for beneficial commands like filling lantern
            beneficial_commands = ["fill"]
            if verb.lower() not in beneficial_commands:
                # Consume oil for most commands
                self.state.player.consume_oil_for_action("command", self.state.difficulty_manager)
            
            return result, message
        return CommandResult.INVALID, "Command not understood"
    
    def get_player_position(self) -> tuple[int, int]:
        """Get current player position."""
        return self.state.player.get_position()
    
    def get_lantern_oil(self) -> float:
        """Get current lantern oil level."""
        return self.state.player.get_lantern_oil()
    
    def has_spirit_at_position(self, pos: tuple[int, int]) -> bool:
        """Check if there's a spirit at the given position."""
        current_room = self.state.world.get_current_room()
        return pos in current_room.spirits if current_room else False
    
    def move_to_position(self, target_pos: tuple[int, int]) -> bool:
        """Move player to target position using pathfinding."""
        current_pos = self.get_player_position()
        
        # Simple pathfinding - move one step at a time toward target
        max_moves = 50  # Prevent infinite loops
        moves = 0
        
        while current_pos != target_pos and moves < max_moves:
            row_diff = target_pos[0] - current_pos[0]
            col_diff = target_pos[1] - current_pos[1]
            
            # Choose direction based on largest difference
            if abs(row_diff) >= abs(col_diff):
                if row_diff > 0:
                    direction = Direction.SOUTH
                else:
                    direction = Direction.NORTH
            else:
                if col_diff > 0:
                    direction = Direction.EAST
                else:
                    direction = Direction.WEST
            
            # Try to move
            if self.move_player(direction):
                current_pos = self.get_player_position()
            else:
                # Can't move in that direction, try another
                if direction in [Direction.NORTH, Direction.SOUTH]:
                    # Try horizontal movement
                    if col_diff > 0:
                        self.move_player(Direction.EAST)
                    elif col_diff < 0:
                        self.move_player(Direction.WEST)
                else:
                    # Try vertical movement
                    if row_diff > 0:
                        self.move_player(Direction.SOUTH)
                    elif row_diff < 0:
                        self.move_player(Direction.NORTH)
                current_pos = self.get_player_position()
            
            moves += 1
        
        return current_pos == target_pos


def test_setup():
    """Verify pytest is working."""
    assert True


def test_game_initialization():
    """Test that the game initializes correctly."""
    game = TestGame()
    
    # Check initial state
    assert game.state.world is not None
    assert game.state.player is not None
    assert game.state.parser is not None
    assert game.state.difficulty_manager is not None
    
    # Check initial player position
    pos = game.get_player_position()
    assert pos == (10, 20)
    
    # Check initial oil level
    oil = game.get_lantern_oil()
    assert oil == 100.0
    
    print("✓ Game initialization test passed")


def test_player_movement():
    """Test basic player movement."""
    game = TestGame()
    initial_pos = game.get_player_position()
    
    # Test movement in each direction
    assert game.move_player(Direction.NORTH)
    new_pos = game.get_player_position()
    assert new_pos == (initial_pos[0] - 1, initial_pos[1])
    
    # Test oil consumption during movement
    initial_oil = game.get_lantern_oil()
    assert initial_oil < 100.0  # Oil should decrease after movement
    
    print("✓ Player movement test passed")


def test_fill_lantern_sequence():
    """Test complete fill lantern sequence."""
    game = TestGame()
    
    # Get initial state
    initial_oil = game.get_lantern_oil()
    font_position = (13, 36)  # Font location from world.py
    
    print(f"Initial oil level: {initial_oil:.1f}%")
    print(f"Moving to font at position {font_position}")
    
    # Move to font location
    success = game.move_to_position(font_position)
    assert success, f"Failed to move to font position {font_position}"
    
    final_pos = game.get_player_position()
    print(f"Reached position: {final_pos}")
    assert final_pos == font_position
    
    # Check oil level after movement (should be lower)
    oil_after_movement = game.get_lantern_oil()
    print(f"Oil after movement: {oil_after_movement:.1f}%")
    assert oil_after_movement < initial_oil
    
    # Execute FILL LANTERN command
    result, message = game.execute_command("FILL LANTERN")
    print(f"Command result: {result}, Message: {message}")
    
    assert result == CommandResult.SUCCESS
    assert "refill" in message.lower()
    
    # Verify oil increased to 100%
    oil_after_fill = game.get_lantern_oil()
    print(f"Oil after filling: {oil_after_fill:.1f}%")
    assert oil_after_fill == 100.0
    
    print("✓ Fill lantern sequence test passed")


def test_soothe_spirit_sequence():
    """Test the complete spirit soothing sequence."""
    print("\n=== Soothe Spirit Sequence Test ===")
    
    game = TestGame()
    
    # Get a prayer geode first
    print("Moving to geode at position (10, 10)")
    game.move_to_position((10, 10))
    
    result, message = game.execute_command("take geode")
    print(f"Take geode result: {result}, Message: {message}")
    assert result == CommandResult.SUCCESS, f"Failed to take geode: {message}"
    
    result, message = game.execute_command("use geode")
    print(f"Use geode result: {result}, Message: {message}")
    assert result == CommandResult.SUCCESS, f"Failed to use geode: {message}"
    
    # Test spirit interaction at correct position (2, 27)
    spirit_position = (2, 27)  # Updated to match the fixed position
    print("Testing spirit interaction from current position")
    
    # Verify spirit exists at the correct position
    assert game.has_spirit_at_position(spirit_position), f"No spirit found at {spirit_position}"
    
    # For testing purposes, let's manually place the player close to the spirit
    # This tests the command logic without relying on pathfinding
    test_position = (2, 26)  # Adjacent to spirit at (2, 27)
    game.state.player.set_position(test_position)
    player_pos = game.state.player.get_position()
    print(f"Player positioned at: {player_pos}")
    
    # Calculate distance to spirit
    distance = (abs(player_pos[0] - spirit_position[0]), abs(player_pos[1] - spirit_position[1]))
    print(f"Distance to spirit: {distance}")
    
    # Try to soothe the spirit
    result, message = game.execute_command("soothe spirit")
    print(f"Soothe spirit result: {result}, Message: {message}")
    
    assert result == CommandResult.SUCCESS, f"Failed to soothe spirit: {message}"
    assert "soothe the spirit" in message.lower(), f"Unexpected soothe message: {message}"
    
    print("✓ Soothe spirit sequence test passed")


def test_complete_gameplay_sequence():
    """Test a complete gameplay sequence combining all actions."""
    game = TestGame()
    
    print("\n=== Complete Gameplay Sequence Test ===")
    
    initial_oil = game.get_lantern_oil()
    print(f"Starting oil level: {initial_oil:.1f}%")
    
    # Step 1: Get a prayer geode
    print("\n1. Getting prayer geode...")
    geode_pos = (10, 10)
    game.move_to_position(geode_pos)
    game.execute_command("TAKE GEODE")
    game.execute_command("USE GEODE")
    
    # Step 2: Move to font and refill lantern
    print("\n2. Refilling lantern at font...")
    font_pos = (13, 36)
    game.move_to_position(font_pos)
    oil_before_fill = game.get_lantern_oil()
    result, message = game.execute_command("FILL LANTERN")
    oil_after_fill = game.get_lantern_oil()
    
    assert result == CommandResult.SUCCESS
    assert oil_after_fill == 100.0
    print(f"Oil: {oil_before_fill:.1f}% → {oil_after_fill:.1f}%")
    
    # Step 3: Move to spirit and soothe it
    print("\n3. Soothing spirit...")
    # For testing purposes, manually position near spirit
    game.state.player.set_position((2, 26))  # Adjacent to spirit at (2, 27)
    
    result, message = game.execute_command("soothe spirit")
    print(f"Soothe result: {result}")
    assert result == CommandResult.SUCCESS, f"Failed to soothe spirit: {message}"
    
    print(f"Final oil level: {game.get_lantern_oil():.1f}%")
    print(f"Total moves: {game.state.total_moves}")
    
    print("✓ Complete gameplay sequence test passed")


def test_invalid_commands():
    """Test handling of invalid commands."""
    game = TestGame()
    
    # Test invalid command
    result, message = game.execute_command("INVALID COMMAND")
    assert result == CommandResult.INVALID
    
    # Test command without required geode
    result, message = game.execute_command("SOOTHE SPIRIT")
    assert result in [CommandResult.FAILURE, CommandResult.NOT_FOUND]
    
    # Test fill lantern away from font
    result, message = game.execute_command("FILL LANTERN")
    assert result == CommandResult.NOT_FOUND
    
    print("✓ Invalid commands test passed")


def test_spirit_position_fix():
    """Test that the spirit position matches the 'S' on the map and soothing works."""
    print("\n=== Spirit Position Fix Test ===")
    
    game = TestGame()
    
    # Check that the spirit exists at the expected position
    current_room = game.state.world.get_current_room()
    assert (2, 27) in current_room.spirits, f"Spirit not found at position (2, 27). Spirits at: {list(current_room.spirits.keys())}"
    
    # Move player near the spirit
    game.state.player.set_position((2, 26))  # Right next to the spirit
    
    # Get a prayer geode and equip it
    game.move_to_position((10, 10))  # Go to prayer geode
    result, message = game.execute_command("take geode")
    assert result == CommandResult.SUCCESS, f"Failed to take geode: {message}"
    
    result, message = game.execute_command("use geode")
    assert result == CommandResult.SUCCESS, f"Failed to use geode: {message}"
    
    # Move back to the spirit
    game.state.player.set_position((2, 26))  # Position next to spirit
    
    # Try to soothe the spirit
    result, message = game.execute_command("soothe spirit")
    print(f"Soothe result: {result}, Message: {message}")
    
    assert result == CommandResult.SUCCESS, f"Failed to soothe spirit: {message}"
    assert "soothe the spirit" in message.lower(), f"Unexpected soothe message: {message}"
    
    # Verify spirit was removed
    assert (2, 27) not in current_room.spirits, "Spirit was not removed after soothing"
    
    print("✓ Spirit position fix test passed")


if __name__ == "__main__":
    """Run tests if script is executed directly."""
    print("Running Sunken Cathedral game tests...\n")
    
    test_setup()
    test_game_initialization() 
    test_player_movement()
    test_fill_lantern_sequence()
    test_soothe_spirit_sequence()
    test_complete_gameplay_sequence()
    test_invalid_commands()
    test_spirit_position_fix()
    
    print("\n🎉 All tests passed! Game mechanics are working correctly.")
