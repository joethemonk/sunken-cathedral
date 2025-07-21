"""
Difficulty system for The Sunken Cathedral game.
Manages different difficulty levels affecting oil consumption and combat.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict


class DifficultyLevel(Enum):
    """Available difficulty levels."""
    EXPLORER = "explorer"
    STORY = "story"
    EASY = "easy"
    HARD = "hard"


@dataclass
class DifficultySettings:
    """Settings for a specific difficulty level."""
    name: str
    description: str
    move_oil_cost: float      # Oil cost per movement
    command_oil_cost: float   # Oil cost per command
    spirit_penalty: float     # Oil penalty for wrong spirit interaction
    max_health: int          # Maximum health (for future combat)
    combat_damage_multiplier: float  # Damage multiplier for combat


class DifficultyManager:
    """
    Manages difficulty levels and their effects on gameplay.
    """
    
    def __init__(self):
        """Initialize the difficulty manager with predefined levels."""
        self.difficulty_settings: Dict[DifficultyLevel, DifficultySettings] = {
            DifficultyLevel.EXPLORER: DifficultySettings(
                name="Explorer Mode",
                description="No oil consumption, minimal combat damage. Focus on story and exploration.",
                move_oil_cost=0.0,
                command_oil_cost=0.0,
                spirit_penalty=0.1,  # Very tiny penalty
                max_health=100,
                combat_damage_multiplier=0.1
            ),
            DifficultyLevel.STORY: DifficultySettings(
                name="Story Mode", 
                description="Very low oil consumption. Enjoy the narrative without pressure.",
                move_oil_cost=0.01,
                command_oil_cost=0.005,
                spirit_penalty=1.0,
                max_health=100,
                combat_damage_multiplier=0.3
            ),
            DifficultyLevel.EASY: DifficultySettings(
                name="Easy",
                description="Low oil consumption. Good for new players.",
                move_oil_cost=0.1,
                command_oil_cost=0.05,
                spirit_penalty=2.0,
                max_health=100,
                combat_damage_multiplier=0.5
            ),
            DifficultyLevel.HARD: DifficultySettings(
                name="Hard",
                description="Standard oil consumption. The intended challenge.",
                move_oil_cost=0.5,
                command_oil_cost=0.3,
                spirit_penalty=5.0,
                max_health=100,
                combat_damage_multiplier=1.0
            )
        }
        
        # Start with Hard difficulty (current settings)
        self.current_difficulty = DifficultyLevel.HARD
    
    def get_current_settings(self) -> DifficultySettings:
        """Get the current difficulty settings."""
        return self.difficulty_settings[self.current_difficulty]
    
    def set_difficulty(self, level: DifficultyLevel) -> None:
        """Set the current difficulty level."""
        self.current_difficulty = level
    
    def get_difficulty_name(self) -> str:
        """Get the name of the current difficulty."""
        return self.difficulty_settings[self.current_difficulty].name
    
    def get_all_difficulties(self) -> Dict[DifficultyLevel, DifficultySettings]:
        """Get all available difficulty levels."""
        return self.difficulty_settings.copy()
    
    def get_move_cost(self) -> float:
        """Get oil cost for movement at current difficulty."""
        return self.difficulty_settings[self.current_difficulty].move_oil_cost
    
    def get_command_cost(self) -> float:
        """Get oil cost for commands at current difficulty."""
        return self.difficulty_settings[self.current_difficulty].command_oil_cost
    
    def get_spirit_penalty(self) -> float:
        """Get oil penalty for wrong spirit interactions."""
        return self.difficulty_settings[self.current_difficulty].spirit_penalty
    
    def get_combat_damage_multiplier(self) -> float:
        """Get damage multiplier for combat at current difficulty."""
        return self.difficulty_settings[self.current_difficulty].combat_damage_multiplier 