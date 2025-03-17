import os
import mysql.connector
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DatabaseConnection:
    """
    A singleton class to manage database connections.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            cls._instance._connection = None
        return cls._instance
    
    def connect(self):
        """Establish a connection to the MySQL database."""
        if self._connection is None or not self._connection.is_connected():
            try:
                self._connection = mysql.connector.connect(
                    host=os.getenv('DB_HOST', 'localhost'),
                    port=int(os.getenv('DB_PORT', 3306)),
                    user=os.getenv('DB_USER', 'root'),
                    password=os.getenv('DB_PASSWORD', ''),
                    database=os.getenv('DB_NAME', 'gaming_lounge_system')
                )
                return self._connection
            except mysql.connector.Error as err:
                print(f"Error connecting to MySQL: {err}")
                raise
        return self._connection
    
    def get_cursor(self):
        """Get a cursor from the connection."""
        connection = self.connect()
        return connection.cursor(dictionary=True)
    
    def close(self):
        """Close the database connection."""
        if self._connection and self._connection.is_connected():
            self._connection.close()
            self._connection = None
    
    def commit(self):
        """Commit the current transaction."""
        if self._connection and self._connection.is_connected():
            self._connection.commit()
    
    def rollback(self):
        """Rollback the current transaction."""
        if self._connection and self._connection.is_connected():
            self._connection.rollback()

# Create a global instance
db = DatabaseConnection() 