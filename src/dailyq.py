#!/usr/bin/env python3
"""DailyQApp main entry point."""

import sys

__version__ = "0.1.0"

def main(name=None):
    if name is None:
        # If no name provided, try to get from command line
        if len(sys.argv) > 1:
            # Check for help flag
            if sys.argv[1] in ('-h', '--help'):
                print(f"Usage: {sys.argv[0]} [name]")
                print("Print a welcome message.")
                print("\nArguments:")
                print("  name    Optional name to greet (default: Traveler)")
                sys.exit(0)
            # If first argument does not look like a flag, treat as name
            elif not sys.argv[1].startswith('-'):
                name = sys.argv[1]
            # else it's a flag we don't understand, ignore and default
        # else no arguments, default
        if name is None:
            name = "Traveler"
    print(f"Welcome to DailyQ, {name}!")

if __name__ == "__main__":
    main()
