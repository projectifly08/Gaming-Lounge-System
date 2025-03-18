#!/usr/bin/env python3
import os
import sys
import argparse
from dotenv import load_dotenv
from src.admin import AdminApp
from src.launcher import LauncherApp

# Load environment variables
load_dotenv()

def main():
    """
    Main entry point for the Gaming Lounge Management System.
    Parses command line arguments and starts either admin or user interface.
    """
    parser = argparse.ArgumentParser(description='Gaming Lounge Management System')
    parser.add_argument('--admin', action='store_true', help='Start the Admin Panel')
    parser.add_argument('--launcher', action='store_true', help='Start the Game Launcher')
    args = parser.parse_args()

    if args.admin:
        # Import and start the Admin Panel
        app = AdminApp()
        app.run()
    elif args.launcher:
        # Import and start the Game Launcher
        app = LauncherApp()
        app.run()
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main() 