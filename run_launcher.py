#!/usr/bin/env python
"""
Run script for Gaming Lounge Launcher.
The application will open in full screen mode.
"""

import sys
from src.launcher.main import LauncherApp

if __name__ == "__main__":
    app = LauncherApp()
    app.run() 