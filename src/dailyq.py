#!/usr/bin/env python3
"""DailyQApp main entry point."""

import sys

def main(name=None):
    if name is None:
        # If no name provided, try to get from command line
        if len(sys.argv) > 1:
            name = sys.argv[1]
        else:
            name = "Traveler"
    print(f"Welcome to DailyQ, {name}!")

if __name__ == "__main__":
    main()
