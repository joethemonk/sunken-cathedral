"""
Save/Load system for The Sunken Cathedral game.
Handles autosave, manual save slots, and game state persistence.
"""

import json
import os
import time
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path

from .difficulty import DifficultyLevel


@dataclass
class SaveData:
    """Container for all saveable game data."""
    player_position: Tuple[int, int]
    lantern_oil: float
    inventory: List[Optional[str]]
    current_geode: Optional[str]
    current_room_id: str
    difficulty: str  # Store as string for JSON compatibility
    total_moves: int
    save_timestamp: float
    game_version: str = "1.0"


@dataclass
class SaveSlotInfo:
    """Information about a save slot for display."""
    slot_number: int
    exists: bool
    save_time: Optional[str] = None
    total_moves: Optional[int] = None
    difficulty: Optional[str] = None
    formatted_date: Optional[str] = None


class SaveManager:
    """
    Manages game save/load operations with autosave and manual save slots.
    """
    
    def __init__(self):
        """Initialize the save manager."""
        # Create saves directory in the project root (relative to where run_game.py is)
        current_file = Path(__file__)
        project_root = current_file.parent.parent.parent  # Go up from src/engine/ to root
        self.saves_dir = project_root / "saves"
        self.max_save_slots = 5
        self.autosave_filename = "autosave.json"
        self.ensure_saves_directory()
    
    def ensure_saves_directory(self) -> None:
        """Create saves directory if it doesn't exist."""
        self.saves_dir.mkdir(exist_ok=True)
    
    def save_game(self, game_state, slot_number: Optional[int] = None) -> bool:
        """
        Save the current game state.
        
        Args:
            game_state: Current GameState object
            slot_number: Save slot (1-5), None for autosave
            
        Returns:
            True if save successful, False otherwise
        """
        try:
            # Create save data
            save_data = SaveData(
                player_position=game_state.player.get_position(),
                lantern_oil=game_state.player.get_lantern_oil(),
                inventory=game_state.player.get_inventory(),
                current_geode=game_state.player.get_current_geode(),
                current_room_id=game_state.world.current_room_id,
                difficulty=game_state.difficulty_manager.current_difficulty.value,
                total_moves=getattr(game_state, 'total_moves', 0),
                save_timestamp=time.time()
            )
            
            # Determine filename
            if slot_number is None:
                filename = self.autosave_filename
            else:
                filename = f"slot_{slot_number}.json"
            
            filepath = self.saves_dir / filename
            
            # Write save data
            with open(filepath, 'w') as f:
                json.dump(asdict(save_data), f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Error saving game: {e}")
            return False
    
    def load_game(self, slot_number: Optional[int] = None) -> Optional[SaveData]:
        """
        Load game state from a save file.
        
        Args:
            slot_number: Save slot (1-5), None for autosave
            
        Returns:
            SaveData if successful, None if failed
        """
        try:
            # Determine filename
            if slot_number is None:
                filename = self.autosave_filename
            else:
                filename = f"slot_{slot_number}.json"
            
            filepath = self.saves_dir / filename
            
            if not filepath.exists():
                return None
            
            # Load save data
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            # Convert back to SaveData object
            save_data = SaveData(**data)
            return save_data
            
        except Exception as e:
            print(f"Error loading game: {e}")
            return None
    
    def has_autosave(self) -> bool:
        """Check if an autosave file exists."""
        return (self.saves_dir / self.autosave_filename).exists()
    
    def get_save_slot_info(self, slot_number: int) -> SaveSlotInfo:
        """
        Get information about a save slot for display.
        
        Args:
            slot_number: Save slot (1-5)
            
        Returns:
            SaveSlotInfo object
        """
        filepath = self.saves_dir / f"slot_{slot_number}.json"
        
        if not filepath.exists():
            return SaveSlotInfo(slot_number=slot_number, exists=False)
        
        try:
            save_data = self.load_game(slot_number)
            if save_data is None:
                return SaveSlotInfo(slot_number=slot_number, exists=False)
            
            # Format timestamp
            save_datetime = datetime.fromtimestamp(save_data.save_timestamp)
            formatted_date = save_datetime.strftime("%Y-%m-%d %H:%M:%S")
            
            return SaveSlotInfo(
                slot_number=slot_number,
                exists=True,
                save_time=formatted_date,
                total_moves=save_data.total_moves,
                difficulty=save_data.difficulty,
                formatted_date=formatted_date
            )
            
        except Exception as e:
            print(f"Error reading save slot {slot_number}: {e}")
            return SaveSlotInfo(slot_number=slot_number, exists=False)
    
    def get_all_save_slots_info(self) -> List[SaveSlotInfo]:
        """Get information for all save slots."""
        return [self.get_save_slot_info(i) for i in range(1, self.max_save_slots + 1)]
    
    def delete_save(self, slot_number: int) -> bool:
        """
        Delete a save file.
        
        Args:
            slot_number: Save slot (1-5)
            
        Returns:
            True if deletion successful, False otherwise
        """
        try:
            filepath = self.saves_dir / f"slot_{slot_number}.json"
            if filepath.exists():
                filepath.unlink()
            return True
        except Exception as e:
            print(f"Error deleting save slot {slot_number}: {e}")
            return False
    
    def apply_save_to_game_state(self, save_data: SaveData, game_state) -> bool:
        """
        Apply loaded save data to the current game state.
        
        Args:
            save_data: The loaded save data
            game_state: Current GameState object to modify
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Restore player state
            game_state.player.set_position(save_data.player_position)
            game_state.player.set_lantern_oil(save_data.lantern_oil)
            game_state.player.set_inventory(save_data.inventory)
            game_state.player.set_current_geode(save_data.current_geode)
            
            # Restore world state
            game_state.world.current_room_id = save_data.current_room_id
            
            # Restore difficulty
            difficulty_level = DifficultyLevel(save_data.difficulty)
            game_state.difficulty_manager.set_difficulty(difficulty_level)
            
            # Restore move counter
            game_state.total_moves = save_data.total_moves
            
            return True
            
        except Exception as e:
            print(f"Error applying save data: {e}")
            return False 