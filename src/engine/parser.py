"""
Command parser for The Sunken Cathedral game.
Handles two-word verb-noun commands that pause gameplay.
"""

import sys
from typing import Dict, List, Optional, Tuple, Callable
from enum import Enum


class CommandResult(Enum):
    """Results of command execution."""
    SUCCESS = "success"
    FAILURE = "failure"
    INVALID = "invalid"
    NOT_FOUND = "not_found"


class Parser:
    """
    Handles command parsing and execution for the game.
    Supports two-word verb-noun commands that pause the real-time gameplay.
    """
    
    def __init__(self):
        """Initialize the parser with command mappings."""
        # Valid verbs and their synonyms
        self.verbs: Dict[str, List[str]] = {
            'take': ['take', 'get', 'pick', 'grab'],
            'drop': ['drop', 'leave', 'place'],
            'use': ['use', 'activate', 'employ'],
            'read': ['read', 'examine', 'look'],
            'fill': ['fill', 'refill'],
            'shine': ['shine', 'light', 'illuminate'],
            'soothe': ['soothe', 'calm', 'comfort'],
            'open': ['open', 'unlock'],
            'go': ['go', 'move', 'walk'],
            'help': ['help', 'commands', '?'],
            'settings': ['settings', 'options', 'config'],
            'save': ['save', 'savegame'],
            'load': ['load', 'loadgame']
        }
        
        # Valid nouns and their synonyms
        self.nouns: Dict[str, List[str]] = {
            'lantern': ['lantern', 'lamp', 'light'],
            'scroll': ['scroll', 'paper', 'parchment'],
            'geode': ['geode', 'crystal', 'stone'],
            'spirit': ['spirit', 'ghost', 'sorrow'],
            'font': ['font', 'fountain', 'basin'],
            'key': ['key'],
            'door': ['door', 'gate', 'passage'],
            'inventory': ['inventory', 'items', 'bag'],
            'north': ['north', 'n'],
            'south': ['south', 's'], 
            'east': ['east', 'e'],
            'west': ['west', 'w']
        }
        
        # Current command being typed
        self.current_command = ""
        self.is_typing = False
    
    def normalize_word(self, word: str) -> Optional[str]:
        """
        Normalize a word to its canonical form.
        
        Args:
            word: Input word to normalize
            
        Returns:
            Canonical form of the word, or None if not recognized
        """
        word = word.lower().strip()
        
        # Check verbs
        for canonical, synonyms in self.verbs.items():
            if word in synonyms:
                return canonical
        
        # Check nouns
        for canonical, synonyms in self.nouns.items():
            if word in synonyms:
                return canonical
        
        return word  # Return as-is if not in our dictionary
    
    def parse_command(self, command_text: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Parse a command into verb and noun.
        
        Args:
            command_text: Raw command text
            
        Returns:
            Tuple of (verb, noun) or (None, None) if invalid
        """
        words = command_text.strip().lower().split()
        
        if len(words) == 0:
            return None, None
        elif len(words) == 1:
            # Single word commands (like "help")
            verb = self.normalize_word(words[0])
            return verb, None
        elif len(words) == 2:
            # Two word commands (verb noun)
            verb = self.normalize_word(words[0])
            noun = self.normalize_word(words[1])
            return verb, noun
        else:
            # Too many words - take first two
            verb = self.normalize_word(words[0])
            noun = self.normalize_word(words[1])
            return verb, noun
    
    def get_command_input(self, first_char: str = "") -> str:
        """
        Get command input - simplified for pygame version.
        This method is no longer used in pygame version but kept for compatibility.
        
        Args:
            first_char: The first character already typed
            
        Returns:
            Complete command string
        """
        # This method is no longer used in pygame version
        # Command input is handled directly in the pygame main loop
        return ""
    
    def execute_command(self, verb: str, noun: Optional[str], game_state) -> Tuple[CommandResult, str]:
        """
        Execute a parsed command.
        
        Args:
            verb: The action verb
            noun: The target noun (can be None)
            game_state: Current game state object
            
        Returns:
            Tuple of (result, message)
        """
        try:
            if verb == "help":
                return self._help_command()
            elif verb == "take":
                return self._take_command(noun, game_state)
            elif verb == "drop":
                return self._drop_command(noun, game_state)
            elif verb == "use":
                return self._use_command(noun, game_state)
            elif verb == "read":
                return self._read_command(noun, game_state)
            elif verb == "fill":
                return self._fill_command(noun, game_state)
            elif verb == "shine":
                return self._shine_command(noun, game_state)
            elif verb == "soothe":
                return self._soothe_command(noun, game_state)
            elif verb == "go":
                return self._go_command(noun, game_state)
            elif verb == "settings":
                return self._settings_command(noun, game_state)
            elif verb == "save":
                return self._save_command(noun, game_state)
            elif verb == "load":
                return self._load_command(noun, game_state)
            else:
                return CommandResult.INVALID, f"I don't understand '{verb}'."
                
        except Exception as e:
            return CommandResult.FAILURE, f"Something went wrong: {str(e)}"
    
    def _help_command(self) -> Tuple[CommandResult, str]:
        """Display help information."""
        # Return a special marker that the main game will intercept to show paginated help
        return CommandResult.SUCCESS, "SHOW_HELP_SCREEN"
    
    def _take_command(self, noun: Optional[str], game_state) -> Tuple[CommandResult, str]:
        """Handle take/pick up commands."""
        if not noun:
            return CommandResult.INVALID, "Take what?"
        
        # Try to pick up item at current position
        picked_item = game_state.player.pick_up_item(game_state.world)
        if picked_item:
            return CommandResult.SUCCESS, f"You take the {picked_item}."
        else:
            return CommandResult.NOT_FOUND, "There's nothing here to take."
    
    def _drop_command(self, noun: Optional[str], game_state) -> Tuple[CommandResult, str]:
        """Handle drop commands."""
        if not noun:
            return CommandResult.INVALID, "Drop what?"
        
        # Find the item in inventory (handle partial matches)
        inventory = game_state.player.get_inventory()
        item_to_drop = None
        
        for item in inventory:
            if item and noun.lower() in item.lower():
                item_to_drop = item
                break
        
        if not item_to_drop:
            return CommandResult.NOT_FOUND, f"You don't have a {noun}."
        
        if game_state.player.drop_item(item_to_drop, game_state.world):
            return CommandResult.SUCCESS, f"You drop the {item_to_drop}."
        else:
            return CommandResult.FAILURE, "You can't drop that here."
    
    def _use_command(self, noun: Optional[str], game_state) -> Tuple[CommandResult, str]:
        """Handle use commands."""
        if not noun:
            return CommandResult.INVALID, "Use what?"
        
        if noun == "geode":
            # Find any geode in inventory
            inventory = game_state.player.get_inventory()
            for item in inventory:
                if item and "geode" in item.lower():
                    if game_state.player.equip_geode(item):
                        return CommandResult.SUCCESS, f"You attune the {item} to your lantern."
                    break
            return CommandResult.NOT_FOUND, "You don't have a geode."
        
        return CommandResult.INVALID, f"You can't use the {noun}."
    
    def _read_command(self, noun: Optional[str], game_state) -> Tuple[CommandResult, str]:
        """Handle read commands."""
        if not noun:
            return CommandResult.INVALID, "Read what?"
        
        if noun == "scroll":
            if game_state.player.has_item("Worn Scroll"):
                # Return special marker to trigger full-screen scroll display
                return CommandResult.SUCCESS, "SHOW_SCROLL_CONTENT"
            else:
                return CommandResult.NOT_FOUND, "You don't have a scroll to read."
        
        return CommandResult.INVALID, f"You can't read the {noun}."
    
    def _fill_command(self, noun: Optional[str], game_state) -> Tuple[CommandResult, str]:
        """Handle fill lantern commands."""
        if noun != "lantern":
            return CommandResult.INVALID, "Fill what? (Try 'FILL LANTERN')"
        
        # Check if player is at a font
        current_room = game_state.world.get_current_room()
        player_pos = game_state.player.get_position()
        
        if current_room and player_pos in current_room.fonts:
            game_state.player.refill_lantern()
            return CommandResult.SUCCESS, "You refill your lantern with sacred oil. The flame burns bright once more."
        else:
            return CommandResult.NOT_FOUND, "There's no font here to refill your lantern."
    
    def _shine_command(self, noun: Optional[str], game_state) -> Tuple[CommandResult, str]:
        """Handle shine lantern commands."""
        if noun != "lantern":
            return CommandResult.INVALID, "Shine what? (Try 'SHINE LANTERN')"
        
        if game_state.player.is_lantern_depleted():
            return CommandResult.FAILURE, "Your lantern has no oil to shine."
        
        return CommandResult.SUCCESS, "Your lantern glows with sacred light."
    
    def _soothe_command(self, noun: Optional[str], game_state) -> Tuple[CommandResult, str]:
        """Handle soothe spirit commands."""
        if noun != "spirit":
            return CommandResult.INVALID, "Soothe what? (Try 'SOOTHE SPIRIT')"
        
        # Check if there's a spirit nearby
        current_room = game_state.world.get_current_room()
        player_pos = game_state.player.get_position()
        
        if current_room:
            # Check for spirits in adjacent positions
            for spirit_pos in current_room.spirits:
                row_diff = abs(spirit_pos[0] - player_pos[0])
                col_diff = abs(spirit_pos[1] - player_pos[1])
                if row_diff <= 1 and col_diff <= 1:  # Adjacent or same position
                    current_geode = game_state.player.get_current_geode()
                    if current_geode:
                        # For now, assume the geode is correct (in full game, check geode type)
                        # Remove the spirit from the room
                        del current_room.spirits[spirit_pos]
                        return CommandResult.SUCCESS, f"You soothe the spirit with your {current_geode}. It fades peacefully."
                    else:
                        # Wrong approach - spirit lashes out and drains oil
                        if hasattr(game_state, 'difficulty_manager'):
                            game_state.player.consume_oil_for_action("spirit_penalty", game_state.difficulty_manager)
                        penalty_msg = "The spirit lashes out! Your lantern flickers as its anguish drains your oil."
                        return CommandResult.FAILURE, f"You need a prayer geode to soothe the spirit. {penalty_msg}"
        
        return CommandResult.NOT_FOUND, "There's no spirit here to soothe."
    
    def _go_command(self, noun: Optional[str], game_state) -> Tuple[CommandResult, str]:
        """Handle movement commands."""
        if not noun:
            return CommandResult.INVALID, "Go where? (north, south, east, west)"
        
        direction_map = {
            'north': 'north',
            'south': 'south', 
            'east': 'east',
            'west': 'west',
            'n': 'north',
            's': 'south',
            'e': 'east', 
            'w': 'west'
        }
        
        direction = direction_map.get(noun)
        if not direction:
            return CommandResult.INVALID, f"I don't understand the direction '{noun}'."
        
        return CommandResult.SUCCESS, f"Use the arrow keys to move {direction}."
    
    def _settings_command(self, noun: Optional[str], game_state) -> Tuple[CommandResult, str]:
        """Handle settings command - opens settings menu."""
        # Return a special marker that the main game will intercept
        return CommandResult.SUCCESS, "OPEN_SETTINGS_MENU"
    
    def _save_command(self, noun: Optional[str], game_state) -> Tuple[CommandResult, str]:
        """Handle save command - opens save menu."""
        # Return a special marker that the main game will intercept
        return CommandResult.SUCCESS, "OPEN_SAVE_MENU"
    
    def _load_command(self, noun: Optional[str], game_state) -> Tuple[CommandResult, str]:
        """Handle load command - opens load menu."""
        # Return a special marker that the main game will intercept
        return CommandResult.SUCCESS, "OPEN_LOAD_MENU" 