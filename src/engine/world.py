"""
World and room management for The Sunken Cathedral game.
Handles room layouts, connections, and interactive elements.
"""

from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass
from enum import Enum


class Direction(Enum):
    """Cardinal directions for movement."""
    NORTH = (-1, 0)
    SOUTH = (1, 0)
    EAST = (0, 1)
    WEST = (0, -1)


@dataclass
class RoomExit:
    """Represents an exit from a room."""
    direction: Direction
    target_room_id: str
    target_position: Tuple[int, int]
    requirements: Optional[List[str]] = None  # Items or conditions needed


class Room:
    """
    Represents a single room in the Cathedral.
    Contains the ASCII map, interactive elements, and navigation.
    """
    
    def __init__(self, room_id: str, name: str, description: str):
        """
        Initialize a room.
        
        Args:
            room_id: Unique identifier for the room
            name: Display name of the room
            description: Long description for atmospheric text
        """
        self.room_id = room_id
        self.name = name
        self.description = description
        
        # ASCII map representation
        self.room_map: List[str] = []
        
        # Interactive elements (position -> item/interaction)
        self.items: Dict[Tuple[int, int], str] = {}
        self.spirits: Dict[Tuple[int, int], str] = {}
        self.fonts: Dict[Tuple[int, int], str] = {}  # Oil sources
        self.exits: Dict[Direction, RoomExit] = {}
        
        # Walkable positions (walls block movement)
        self.walkable_positions: Set[Tuple[int, int]] = set()
        
        # Messages and lore
        self.ambient_messages: List[str] = []
        self.rune_messages: Dict[Tuple[int, int], str] = {}  # Position -> rune text
    
    def set_map(self, map_lines: List[str]) -> None:
        """
        Set the ASCII map for this room and calculate walkable positions.
        
        Args:
            map_lines: List of strings representing the room layout
        """
        self.room_map = map_lines.copy()
        self._calculate_walkable_positions()
    
    def _calculate_walkable_positions(self) -> None:
        """Calculate which positions in the room are walkable."""
        self.walkable_positions.clear()
        
        for row_idx, line in enumerate(self.room_map):
            for col_idx, char in enumerate(line):
                # Check if position is walkable (not a wall or rubble)
                if char not in ['▓', '█', '▒']:  # Walls and rubble block movement
                    self.walkable_positions.add((row_idx, col_idx))
    
    def is_walkable(self, position: Tuple[int, int]) -> bool:
        """
        Check if a position is walkable.
        
        Args:
            position: (row, col) to check
            
        Returns:
            True if the position can be walked on
        """
        return position in self.walkable_positions
    
    def get_character_at(self, position: Tuple[int, int]) -> str:
        """
        Get the map character at a specific position.
        
        Args:
            position: (row, col) position to check
            
        Returns:
            The character at that position, or ' ' if out of bounds
        """
        row, col = position
        if 0 <= row < len(self.room_map) and 0 <= col < len(self.room_map[row]):
            return self.room_map[row][col]
        return ' '
    
    def add_item(self, position: Tuple[int, int], item_name: str) -> None:
        """Add an item at a specific position."""
        self.items[position] = item_name
    
    def remove_item(self, position: Tuple[int, int]) -> Optional[str]:
        """Remove and return an item from a position."""
        return self.items.pop(position, None)
    
    def add_exit(self, direction: Direction, target_room: str, 
                 target_pos: Tuple[int, int], requirements: Optional[List[str]] = None) -> None:
        """Add an exit in the specified direction."""
        self.exits[direction] = RoomExit(direction, target_room, target_pos, requirements)

    def modify_map_tile(self, position: Tuple[int, int], new_char: str) -> bool:
        """
        Modify a single character on the room map.
        
        Args:
            position: (row, col) of the tile to change
            new_char: The new character to place at the position
            
        Returns:
            True if the modification was successful, False otherwise
        """
        row, col = position
        if 0 <= row < len(self.room_map) and 0 <= col < len(self.room_map[row]):
            # Modify the string by converting to a list of characters
            row_list = list(self.room_map[row])
            row_list[col] = new_char
            self.room_map[row] = "".join(row_list)
            
            # Recalculate walkable positions since the map has changed
            self._calculate_walkable_positions()
            return True
        return False

    def check_for_room_transition(self, player, world) -> None:
        """
        Check if the player has moved to an exit and transition if necessary.
        
        Args:
            player: The player object
            world: The world object
        """
        player_pos = player.get_position()
        
        # Check if the player's new position is an exit
        for direction, exit_info in self.exits.items():
            # This is a bit simplistic; a real game might have exit positions
            # For now, let's assume moving in the exit's direction from anywhere triggers it
            # A better approach is to define exit zones or specific tiles.
            
            # Let's check if the player moved "through" a conceptual exit
            # e.g., if exit is NORTH, did the player move to the top row?
            if direction == Direction.NORTH and player_pos[0] == 0:
                world.set_current_room(exit_info.target_room_id)
                player.set_position(exit_info.target_position)
                return
            elif direction == Direction.SOUTH and player_pos[0] == len(self.room_map) - 1:
                world.set_current_room(exit_info.target_room_id)
                player.set_position(exit_info.target_position)
                return
            # Add EAST and WEST checks if needed


class World:
    """
    Manages all rooms and handles world state.
    """
    
    def __init__(self):
        """Initialize the world with empty rooms."""
        self.rooms: Dict[str, Room] = {}
        self.current_room_id: Optional[str] = None
    
    def add_room(self, room: Room) -> None:
        """Add a room to the world."""
        self.rooms[room.room_id] = room
    
    def get_room(self, room_id: str) -> Optional[Room]:
        """Get a room by its ID."""
        return self.rooms.get(room_id)
    
    def get_current_room(self) -> Optional[Room]:
        """Get the current room."""
        if self.current_room_id:
            return self.rooms.get(self.current_room_id)
        return None
    
    def set_current_room(self, room_id: str) -> bool:
        """
        Set the current room.
        
        Args:
            room_id: ID of the room to set as current
            
        Returns:
            True if successful, False if room doesn't exist
        """
        if room_id in self.rooms:
            self.current_room_id = room_id
            return True
        return False


def create_test_world() -> World:
    """
    Create a test world with the entrance room featuring the rose window.
    This matches the game design document.
    """
    world = World()
    
    # Create the entrance room - The Weeping Halls
    entrance = Room(
        room_id="entrance", 
        name="The Weeping Halls - Entrance",
        description="You enter through a fractured, rose-shaped window. The water here is "
                   "unnaturally still, and the air, miraculously, is breathable. Strange, "
                   "bioluminescent moss casts a faint glow on carved reliefs of a forgotten sea god."
    )
    
    # ASCII map for the entrance room - inspired by the game design
    entrance_map = [
        "▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓",
        "▓≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈▓▓≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈▓",
        "▓≈                L         ≈▓▓≈            ≈▓",
        "▓≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈  ≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈▓",
        "▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓",
        "▓                                           ▓",
        "▓    The rose window filters ancient        ▓",
        "▓    light through fractal patterns...      ▓",
        "▓                                           ▓",
        "▓                                           ▓",
        "▓          A lectern stands here, holding   ▓",
        "▓          what appears to be a worn scroll.▓",
        "▓                                           ▓",
        "▓                                    F      ▓",
        "▓    To the north, grand doors loom         ▓",
        "▓    shut, sealed by an ancient power.      ▓",
        "▓                                           ▓",
        "▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓",
        "",
        "A sign is carved here: ᛒᛖᚹᚪᚱᛖ ᚦᛖ ᛞᛟᛈ"
    ]
    
    entrance.set_map(entrance_map)
    
    # Add interactive elements
    # Lore item (L) at position (2, 16) - "Worn Scroll"
    entrance.add_item((2, 16), "Worn Scroll")
    
    # Add prayer geodes for spirit soothing
    entrance.add_item((10, 10), "Prayer Geode")
    entrance.add_item((6, 30), "Silver Geode")
    
    # Add additional scrolls for the multiple scroll system
    entrance.add_item((8, 35), "Ancient Scroll")
    entrance.add_item((14, 8), "Cathedral Research Scroll")
    
    # Spirit (S) at position (2, 38) - correctly positioned to match actual map location
    entrance.spirits[(2, 38)] = "Weeping Sorrow"
    
    # Font (F) at position (13, 36) - Oil source
    entrance.fonts[(13, 36)] = "Ancient Font"
    
    # Add rune message at the bottom
    entrance.rune_messages[(19, 0)] = "BEWARE THE DEEP"
    
    # Add some ambient messages
    entrance.ambient_messages = [
        "Water drips rhythmically from the vaulted ceiling.",
        "The bioluminescent moss pulses with an otherworldly glow.",
        "An ancient silence fills this sacred space.",
        "The fractured rose window casts ethereal patterns on the walls."
    ]
    
    world.add_room(entrance)
    
    # Create the North Hall
    north_hall = Room(
        room_id="north_hall",
        name="The North Hall",
        description="A long, narrow hall stretches into darkness. The air is colder here, and the sound of dripping water is more pronounced."
    )
    
    north_hall_map = [
        "▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓",
        "▓                                           ▓",
        "▓                                           ▓",
        "▓                                           ▓",
        "▓                                           ▓",
        "▓                                           ▓",
        "▓                                           ▓",
        "▓                                           ▓",
        "▓                                           ▓",
        "▓                                           ▓",
        "▓                                           ▓",
        "▓                                           ▓",
        "▓                                           ▓",
        "▓                                           ▓",
        "▓                                           ▓",
        "▓                                           ▓",
        "▓▓▓▓▓▓▓▓▓       S       ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓",
        "▓≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈▓",
        "▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓"
    ]
    north_hall.set_map(north_hall_map)
    north_hall.add_exit(Direction.SOUTH, "entrance", (5, 14)) # Exit back to entrance
    
    world.add_room(north_hall)
    
    world.set_current_room("entrance")
    
    return world 