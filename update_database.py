#!/usr/bin/env python
"""
Run database update scripts
"""
from src.database.update_users_table import update_users_table

if __name__ == "__main__":
    print("Running database updates...")
    update_users_table()
    print("Database updates completed.") 