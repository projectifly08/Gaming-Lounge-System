#!/usr/bin/env python
"""
Run script for Gaming Lounge Admin Panel.
The application will open in full screen mode.
"""

from src.admin.main import AdminApp

if __name__ == "__main__":
    app = AdminApp()
    app.run() 