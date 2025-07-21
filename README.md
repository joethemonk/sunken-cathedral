# The Sunken Cathedral

A Castle Adventure style text adventure game inspired by classic 1980s adventures.

## Quick Start

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the game:
   ```bash
   python run_game.py
   ```
   
   Or alternatively:
   ```bash
   cd src && python main.py
   ```

## Controls

- **Arrow keys**: Move your character (☺) around
- **Any letter**: Start typing a command
- **ESC or Q**: Quit the game

## Commands

- `TAKE [item]` - Pick up an item
- `DROP [item]` - Drop an item from inventory  
- `USE [item]` - Use or equip an item
- `READ [item]` - Read a scroll or examine text
- `FILL LANTERN` - Refill lantern at a font (F)
- `SHINE LANTERN` - Use lantern to pass barriers
- `SOOTHE SPIRIT` - Calm a drowned sorrow
- `HELP` - Show help

## Game Symbols

- `☺` - You, the Lamplighter
- `▓ █` - Walls, Rubble  
- `▒` - Doors, Gates, Psychic Barriers
- `≈` - Deep Water (impassable without light)
- `L` - Lore Item (Scroll, Tablet)
- `G` - Prayer Geode
- `S` - Drowned Sorrow (Spirit)
- `F` - Consecrated Font (Oil Source)

## Gameplay Tips

- Your lantern oil decreases with each action you take - watch the percentage!
- Find fonts (F) to refill your lantern with `FILL LANTERN`
- Take your time - no time pressure! The game pauses when you're thinking
- Read scrolls to learn the lore
- Deep water (≈) cannot be entered without oil in your lantern
- You have 4 inventory slots

## Story

You are the last Lamplighter, drawn by a sorrowful beacon from the depths of the sea. Navigate the Sunken Cathedral, manage your sacred oil, and uncover the mystery of this ancient place.

## Technical Notes

This is a prototype focusing on the core framework. The game currently includes:
- Real-time arrow key movement
- Turn-based command system
- Split-screen ASCII display with proper text pagination
- Difficulty selection system (Explorer, Story, Easy, Hard)
- Lantern oil consumption based on difficulty
- Basic inventory management
- Settings menu accessible during gameplay
- One test room (the entrance)

## Requirements

- Python 3.7+
- pygame (for graphics and input)
- No terminal requirements - runs in its own window! 