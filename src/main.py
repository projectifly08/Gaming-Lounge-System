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
    parser.add_argument('--user', action='store_true', help='Start the Game Launcher (User Side)')
    parser.add_argument('--pc', type=int, help='PC number for the game launcher')
    args = parser.parse_args()

    if args.admin:
        # Import and start the Admin Panel
        app = AdminApp()
        app.run()
    elif args.user:
        # Import and start the Game Launcher
        pc_number = args.pc if args.pc else 1
        app = LauncherApp(pc_number)
        app.run()
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main() 