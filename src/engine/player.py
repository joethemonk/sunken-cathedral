"""
Player management for The Sunken Cathedral game.
Handles player state, inventory, movement, and lantern oil.
"""

import time
from typing import List, Optional, Tuple
from dataclasses import dataclass
from .world import World, Direction


@dataclass
class PlayerState:
    """Represents the current state of the player."""
    position: Tuple[int, int]
    lantern_oil: float  # Percentage (0-100)
    current_geode: Optional[str]
    inventory: List[Optional[str]]
    last_oil_update: float  # Timestamp for oil consumption


class Player:
    """
    Manages the player character state and actions.
    The Lamplighter exploring the Sunken Cathedral.
    """
    
    def __init__(self, starting_position: Tuple[int, int] = (10, 20)):
        """
        Initialize the player.
        
        Args:
            starting_position: Initial (row, col) position in the room
        """
        self.state = PlayerState(
            position=starting_position,
            lantern_oil=100.0,  # Start with full lantern
            current_geode=None,
            inventory=[None, None, None, None],  # 4 inventory slots
            last_oil_update=time.time()
        )
        
        # Oil consumption rate (percentage per second)
        self.oil_consumption_rate = 0.5  # Loses 0.5% oil per second
        
        # Starting inventory - worn scroll as mentioned in game design
        self.state.inventory[0] = "Worn Scroll"
    
    def get_position(self) -> Tuple[int, int]:
        """Get the current player position."""
        return self.state.position
    
    def set_position(self, position: Tuple[int, int]) -> None:
        """Set the player position."""
        self.state.position = position
    
    def get_lantern_oil(self) -> float:
        """Get current lantern oil percentage."""
        return self.state.lantern_oil
    
    def set_lantern_oil(self, oil_level: float) -> None:
        """Set the lantern oil level."""
        self.state.lantern_oil = max(0.0, min(100.0, oil_level))
    
    def set_inventory(self, inventory: List[Optional[str]]) -> None:
        """Set the entire inventory."""
        # Ensure inventory has exactly 4 slots
        if len(inventory) != 4:
            raise ValueError("Inventory must have exactly 4 slots")
        self.state.inventory = inventory.copy()
    
    def set_current_geode(self, geode: Optional[str]) -> None:
        """Set the currently equipped geode."""
        self.state.current_geode = geode
    
    def consume_oil_for_action(self, action_type: str = "move", difficulty_manager=None) -> bool:
        """
        Consume oil for a specific action (turn-based).
        
        Args:
            action_type: Type of action ("move", "command", etc.)
            difficulty_manager: DifficultyManager instance for getting costs
            
        Returns:
            True if oil is still available, False if depleted
        """
        if difficulty_manager:
            # Use difficulty-based costs
            if action_type == "move":
                oil_cost = difficulty_manager.get_move_cost()
            elif action_type == "command":
                oil_cost = difficulty_manager.get_command_cost()
            elif action_type == "spirit_penalty":
                oil_cost = difficulty_manager.get_spirit_penalty()
            else:
                oil_cost = difficulty_manager.get_move_cost()  # Default to move cost
        else:
            # Fallback to original costs
            oil_costs = {
                "move": 0.5,
                "command": 0.3,
                "special": 1.0
            }
            oil_cost = oil_costs.get(action_type, 0.5)
        
        self.state.lantern_oil = max(0.0, self.state.lantern_oil - oil_cost)
        return self.state.lantern_oil > 0
    
    def refill_lantern(self, amount: float = 100.0) -> None:
        """
        Refill the lantern oil.
        
        Args:
            amount: Amount to add (defaults to full refill)
        """
        self.state.lantern_oil = min(100.0, self.state.lantern_oil + amount)
    
    def try_move(self, direction: Direction, world: World) -> bool:
        """
        Attempt to move the player in the specified direction.
        
        Args:
            direction: Direction to move
            world: Current world state
            
        Returns:
            True if movement was successful, False otherwise
        """
        current_room = world.get_current_room()
        if not current_room:
            return False
        
        # Calculate new position
        row_offset, col_offset = direction.value
        current_row, current_col = self.state.position
        new_position = (current_row + row_offset, current_col + col_offset)
        
        # Check if the new position is within map bounds
        if (new_position[0] < 0 or new_position[0] >= len(current_room.room_map) or
            new_position[1] < 0):
            return False
        
        # Check if any row has enough columns
        if new_position[0] < len(current_room.room_map):
            if new_position[1] >= len(current_room.room_map[new_position[0]]):
                return False
        
        # Check if position is walkable
        if not current_room.is_walkable(new_position):
            return False
        
        # Special case: Deep water requires light
        char_at_pos = current_room.get_character_at(new_position)
        if char_at_pos == '≈' and self.state.lantern_oil <= 0:
            return False  # Cannot enter deep water without oil
        
        # Movement successful
        self.state.position = new_position
        
        # Check for room transition after moving
        current_room.check_for_room_transition(self, world)
        
        return True
    
    def get_inventory(self) -> List[Optional[str]]:
        """Get the current inventory."""
        return self.state.inventory.copy()
    
    def add_item(self, item_name: str) -> bool:
        """
        Add an item to inventory.
        
        Args:
            item_name: Name of the item to add
            
        Returns:
            True if item was added, False if inventory full
        """
        for i in range(len(self.state.inventory)):
            if self.state.inventory[i] is None:
                self.state.inventory[i] = item_name
                return True
        return False  # Inventory full
    
    def remove_item(self, item_name: str) -> bool:
        """
        Remove an item from inventory.
        
        Args:
            item_name: Name of the item to remove
            
        Returns:
            True if item was removed, False if not found
        """
        for i in range(len(self.state.inventory)):
            if self.state.inventory[i] == item_name:
                self.state.inventory[i] = None
                return True
        return False
    
    def has_item(self, item_name: str) -> bool:
        """
        Check if player has a specific item.
        
        Args:
            item_name: Name of the item to check
            
        Returns:
            True if player has the item
        """
        return item_name in self.state.inventory
    
    def get_current_geode(self) -> Optional[str]:
        """Get the currently equipped geode."""
        return self.state.current_geode
    
    def equip_geode(self, geode_name: str) -> bool:
        """
        Equip a geode if it's in inventory.
        
        Args:
            geode_name: Name of the geode to equip
            
        Returns:
            True if geode was equipped, False if not in inventory
        """
        if self.has_item(geode_name):
            self.state.current_geode = geode_name
            return True
        return False
    
    def unequip_geode(self) -> None:
        """Unequip the current geode."""
        self.state.current_geode = None
    
    def is_lantern_depleted(self) -> bool:
        """Check if the lantern oil is completely depleted."""
        return self.state.lantern_oil <= 0
    
    def get_oil_warning_level(self) -> str:
        """
        Get the warning level for oil status.
        
        Returns:
            'critical', 'low', 'medium', or 'good'
        """
        if self.state.lantern_oil <= 0:
            return 'critical'
        elif self.state.lantern_oil <= 10:
            return 'critical'
        elif self.state.lantern_oil <= 25:
            return 'low'
        elif self.state.lantern_oil <= 50:
            return 'medium'
        else:
            return 'good'
    
    def get_inventory_count(self) -> int:
        """Get the number of items currently in inventory."""
        return sum(1 for item in self.state.inventory if item is not None)
    
    def get_free_inventory_slots(self) -> int:
        """Get the number of free inventory slots."""
        return 4 - self.get_inventory_count()
    
    def drop_item(self, item_name: str, world: World) -> bool:
        """
        Drop an item at the current position.
        
        Args:
            item_name: Name of the item to drop
            world: Current world state
            
        Returns:
            True if item was dropped, False if not found or can't drop here
        """
        if not self.has_item(item_name):
            return False
        
        current_room = world.get_current_room()
        if not current_room:
            return False
        
        # Remove from inventory and add to room
        if self.remove_item(item_name):
            current_room.add_item(self.state.position, item_name)
            return True
        
        return False
    
    def pick_up_item(self, world: World) -> Optional[str]:
        """
        Pick up an item at the current position or adjacent positions.
        
        Args:
            world: Current world state
            
        Returns:
            Name of the picked up item, or None if no item or inventory full
        """
        current_room = world.get_current_room()
        if not current_room:
            return None
        
        # Check positions: current position first, then adjacent positions
        positions_to_check = [self.state.position]
        
        # Add adjacent positions
        current_row, current_col = self.state.position
        for row_offset in [-1, 0, 1]:
            for col_offset in [-1, 0, 1]:
                if row_offset == 0 and col_offset == 0:
                    continue  # Skip current position (already added)
                adj_pos = (current_row + row_offset, current_col + col_offset)
                positions_to_check.append(adj_pos)
        
        # Try to find an item at any of these positions
        for pos in positions_to_check:
            item_name = current_room.remove_item(pos)
            if item_name and self.add_item(item_name):
                return item_name
            elif item_name:
                # Couldn't add to inventory, put it back
                current_room.add_item(pos, item_name)
        
        return None 