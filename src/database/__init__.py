from .db_connection import db
from .models import User, PC, Session, MenuItem, Order, Game

__all__ = ['db', 'User', 'PC', 'Session', 'MenuItem', 'Order', 'Game']

def init_db():
    """Initialize the database with required tables."""
    cursor = get_cursor()
    try:
        # Create settings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                id INT AUTO_INCREMENT PRIMARY KEY,
                category VARCHAR(50) NOT NULL,
                name VARCHAR(100) NOT NULL,
                value TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                UNIQUE KEY unique_setting (category, name)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        
        # Insert default settings if they don't exist
        cursor.execute("""
            INSERT INTO settings (category, name, value) VALUES
            ('security', 'launcher_exit_password', ''),
            ('admin', 'session_timeout', '15'),
            ('admin', 'require_password_for_critical', 'true')
            ON DUPLICATE KEY UPDATE value = VALUES(value)
        """)
        
        db.commit()
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        db.rollback()
    finally:
        cursor.close() 