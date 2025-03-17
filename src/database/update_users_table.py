"""
Database migration script to update the users table with admin authentication fields.
"""
from .db_connection import db
from src.utils.helpers import hash_password

def update_users_table():
    """Add admin authentication fields to the users table."""
    cursor = db.get_cursor()
    try:
        # Check if username column exists
        cursor.execute("SHOW COLUMNS FROM users LIKE 'username'")
        if not cursor.fetchone():
            print("Adding username column to users table...")
            cursor.execute("ALTER TABLE users ADD COLUMN username VARCHAR(50) UNIQUE")
        
        # Check if password_hash column exists
        cursor.execute("SHOW COLUMNS FROM users LIKE 'password_hash'")
        if not cursor.fetchone():
            print("Adding password_hash column to users table...")
            cursor.execute("ALTER TABLE users ADD COLUMN password_hash VARCHAR(100)")
        
        # Check if is_admin column exists
        cursor.execute("SHOW COLUMNS FROM users LIKE 'is_admin'")
        if not cursor.fetchone():
            print("Adding is_admin column to users table...")
            cursor.execute("ALTER TABLE users ADD COLUMN is_admin TINYINT(1) DEFAULT 0")
        
        # Check if email column exists
        cursor.execute("SHOW COLUMNS FROM users LIKE 'email'")
        if not cursor.fetchone():
            print("Adding email column to users table...")
            cursor.execute("ALTER TABLE users ADD COLUMN email VARCHAR(100)")
        
        db.commit()
        
        # Create admin user if it doesn't exist
        cursor.execute("SELECT id FROM users WHERE is_admin = 1")
        admin = cursor.fetchone()
        
        if not admin:
            print("Creating admin user with default password 'admin123'...")
            default_password = "admin123"
            hashed_password = hash_password(default_password)
            
            cursor.execute(
                "INSERT INTO users (name, civil_id, phone, username, password_hash, email, is_admin) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                ("Administrator", "ADMIN", "0000000000", "admin", hashed_password, "admin@gaminglounge.com", 1)
            )
            db.commit()
            print("Admin user created successfully!")
        
        print("Users table updated successfully!")
    except Exception as e:
        db.rollback()
        print(f"Error updating users table: {str(e)}")
    finally:
        cursor.close()

if __name__ == "__main__":
    update_users_table() 