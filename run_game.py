#!/usr/bin/env python3
"""
Simple script to run The Sunken Cathedral game with proper error handling.
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from main_pygame import main
    if __name__ == "__main__":
        main()
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running this from the game directory and have installed requirements.txt")
    sys.exit(1)
except KeyboardInterrupt:
    print("\nGame interrupted by user")
    sys.exit(0)
except Exception as e:
    print(f"Unexpected error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1) 