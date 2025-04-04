#!/usr/bin/env python3
import os
import sys
import mysql.connector
from dotenv import load_dotenv

# Add the parent directory to the path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

def get_db_connection():
    """Establish a connection to the MySQL database."""
    try:
        # Extract credentials from environment variables with defaults
        host = os.getenv('DB_HOST', 'localhost')
        port = int(os.getenv('DB_PORT', 3306))
        user = os.getenv('DB_USER', 'root')
        password = os.getenv('DB_PASSWORD', '')
        
        # Print connection information (without password)
        print(f"Attempting to connect to MySQL at {host}:{port} with user '{user}'")
        
        connection = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
        )
        print("Successfully connected to MySQL server")
        return connection
    except mysql.connector.Error as err:
        if err.errno == 1045:  # Access denied error
            print("\nERROR: Access denied to MySQL.")
            print("Please check your credentials in the .env file:")
            print(f"  - Current user: {user}")
            print(f"  - Host: {host}:{port}")
            print("\nTo fix this issue:")
            print("1. Make sure your MySQL server is running")
            print("2. Verify that the username and password in your .env file are correct")
            print("3. Try creating a new user specifically for this application:")
            print("   CREATE USER 'gaming_user'@'localhost' IDENTIFIED BY 'password';")
            print("   GRANT ALL PRIVILEGES ON gaming_lounge_system.* TO 'gaming_user'@'localhost';")
            print("   FLUSH PRIVILEGES;")
            print("\nFor more detailed instructions, please see the docs/mysql_setup.md file.")
        elif err.errno == 2003:  # Can't connect error
            print("\nERROR: Could not connect to MySQL server.")
            print(f"Attempted to connect to: {host}:{port}")
            print("\nTo fix this issue:")
            print("1. Make sure your MySQL server is installed and running")
            print("2. Check if the hostname and port in your .env file are correct")
            print("3. Verify that no firewall is blocking the connection")
            print("\nFor more detailed instructions, please see the docs/mysql_setup.md file.")
        else:
            print(f"\nERROR connecting to MySQL: {err}")
            print("For troubleshooting steps, please see the docs/mysql_setup.md file.")
        
        sys.exit(1)

def create_database():
    """Create the gaming_lounge_system database if it doesn't exist."""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        db_name = os.getenv('DB_NAME', 'gaming_lounge_system')
        
        try:
            print(f"Creating database '{db_name}' if it doesn't exist...")
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
            print(f"Database '{db_name}' created or already exists.")
            
            # Use the database
            cursor.execute(f"USE {db_name}")
            
            # Create tables
            create_tables(cursor)
            
            # Insert sample data if needed
            insert_sample_data(cursor)
            
            # Commit changes
            connection.commit()
            print("All database operations completed successfully!")
            
        except mysql.connector.Error as err:
            connection.rollback()
            if err.errno == 1044:  # Access denied for creating/using database
                print(f"\nERROR: Access denied for creating or using database '{db_name}'")
                print("Your MySQL user doesn't have sufficient privileges.")
                print("\nTo fix this issue, log in to MySQL as an admin user and run:")
                print(f"GRANT ALL PRIVILEGES ON {db_name}.* TO '{os.getenv('DB_USER', 'root')}'@'localhost';")
                print("FLUSH PRIVILEGES;")
            else:
                print(f"\nERROR: {err}")
                print("For troubleshooting steps, please see the docs/mysql_setup.md file.")
            sys.exit(1)
        finally:
            cursor.close()
            connection.close()
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        print("For troubleshooting steps, please see the docs/mysql_setup.md file.")
        sys.exit(1)

def create_tables(cursor):
    """Create the necessary tables for the application."""
    try:
        print("Creating database tables...")
        
        # Users table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            civil_id VARCHAR(20) UNIQUE NOT NULL,
            phone VARCHAR(15) NOT NULL,
            password_hash VARCHAR(255) DEFAULT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # PCs table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS pcs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            pc_number INT UNIQUE NOT NULL,
            is_occupied BOOLEAN DEFAULT FALSE,
            status ENUM('available', 'occupied', 'maintenance') DEFAULT 'available',
            specs TEXT
        )
        """)
        
        # Sessions table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            pc_id INT NOT NULL,
            start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            end_time TIMESTAMP NULL,
            duration_minutes INT NOT NULL,
            status ENUM('active', 'paused', 'completed', 'terminated') DEFAULT 'active',
            payment_method ENUM('Cash', 'Apple Pay', 'KNET') NOT NULL,
            payment_amount DECIMAL(10, 2) NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (pc_id) REFERENCES pcs(id) ON DELETE CASCADE
        )
        """)
        
        # Menu Items table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS menu_items (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            description TEXT,
            price DECIMAL(10, 2) NOT NULL,
            category ENUM('food', 'drink', 'accessory', 'service') NOT NULL,
            available BOOLEAN DEFAULT TRUE,
            image_path VARCHAR(255) DEFAULT NULL
        )
        """)
        
        # Orders table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INT AUTO_INCREMENT PRIMARY KEY,
            session_id INT NOT NULL,
            status ENUM('pending', 'preparing', 'delivered', 'cancelled', 'ready') DEFAULT 'pending',
            order_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            delivery_time TIMESTAMP NULL,
            total_amount DECIMAL(10, 2) NOT NULL,
            FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
        )
        """)
        
        # Order Items table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            id INT AUTO_INCREMENT PRIMARY KEY,
            order_id INT NOT NULL,
            menu_item_id INT NOT NULL,
            quantity INT NOT NULL,
            price DECIMAL(10, 2) NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
            FOREIGN KEY (menu_item_id) REFERENCES menu_items(id) ON DELETE CASCADE
        )
        """)

        # Games table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS games (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            description TEXT,
            executable_path VARCHAR(255) NOT NULL,
            image_path VARCHAR(255),
            category VARCHAR(50),
            is_available BOOLEAN DEFAULT TRUE
        )
        """)
        
        print("All tables created successfully.")
    except mysql.connector.Error as err:
        print(f"\nERROR creating tables: {err}")
        raise

def insert_sample_data(cursor):
    """Insert sample data for testing."""
    try:
        print("Checking if sample data needs to be inserted...")
        
        # Check if we already have pcs
        cursor.execute("SELECT COUNT(*) FROM pcs")
        if cursor.fetchone()[0] == 0:
            print("Inserting sample PC data...")
            # Insert 20 PCs
            for i in range(1, 21):
                cursor.execute("""
                INSERT INTO pcs (pc_number, specs) 
                VALUES (%s, 'Intel i7-10700K, RTX 3080, 32GB RAM, 1TB SSD')
                """, (i,))
        
        # Check if we already have menu items
        cursor.execute("SELECT COUNT(*) FROM menu_items")
        if cursor.fetchone()[0] == 0:
            print("Inserting sample menu items...")
            # Insert food items
            food_items = [
                ("Burger", "Classic beef burger with cheese", 5.99, "food"),
                ("Pizza", "Pepperoni pizza", 8.99, "food"),
                ("Fries", "Crispy french fries", 2.99, "food"),
                ("Sandwich", "Chicken sandwich", 4.99, "food")
            ]
            for item in food_items:
                cursor.execute("""
                INSERT INTO menu_items (name, description, price, category) 
                VALUES (%s, %s, %s, %s)
                """, item)
            
            # Insert drink items
            drink_items = [
                ("Cola", "Cold cola drink", 1.99, "drink"),
                ("Water", "Mineral water", 0.99, "drink"),
                ("Coffee", "Hot coffee", 2.99, "drink"),
                ("Energy Drink", "Energy drink", 3.99, "drink")
            ]
            for item in drink_items:
                cursor.execute("""
                INSERT INTO menu_items (name, description, price, category) 
                VALUES (%s, %s, %s, %s)
                """, item)
            
            # Insert accessory items
            accessory_items = [
                ("Gaming Mouse", "High precision gaming mouse", 5.99, "accessory"),
                ("Gaming Headset", "Noise cancelling headset", 7.99, "accessory"),
                ("Controller", "Game controller", 6.99, "accessory")
            ]
            for item in accessory_items:
                cursor.execute("""
                INSERT INTO menu_items (name, description, price, category) 
                VALUES (%s, %s, %s, %s)
                """, item)
            
            # Insert service items
            service_items = [
                ("Massage", "15 minute shoulder massage", 9.99, "service"),
                ("Tech Support", "Technical assistance", 4.99, "service")
            ]
            for item in service_items:
                cursor.execute("""
                INSERT INTO menu_items (name, description, price, category) 
                VALUES (%s, %s, %s, %s)
                """, item)
        
        # Check if we already have games
        cursor.execute("SELECT COUNT(*) FROM games")
        if cursor.fetchone()[0] == 0:
            print("Inserting sample games...")
            # Insert games
            game_items = [
                ("Fortnite", "Battle Royale game", "C:\\Games\\Fortnite\\Fortnite.exe", "Battle Royale"),
                ("Call of Duty", "First-person shooter", "C:\\Games\\CallOfDuty\\ModernWarfare.exe", "FPS"),
                ("League of Legends", "MOBA game", "C:\\Games\\LeagueOfLegends\\LeagueClient.exe", "MOBA"),
                ("FIFA 2023", "Football simulation", "C:\\Games\\FIFA23\\FIFA23.exe", "Sports"),
                ("Minecraft", "Sandbox game", "C:\\Games\\Minecraft\\Minecraft.exe", "Sandbox"),
                ("Counter-Strike 2", "Tactical shooter", "C:\\Games\\CS2\\cs2.exe", "FPS"),
                ("GTA V", "Action-adventure", "C:\\Games\\GTAV\\PlayGTAV.exe", "Action"),
                ("Valorant", "Tactical shooter", "C:\\Games\\Riot Games\\Valorant\\VALORANT.exe", "FPS")
            ]
            for game in game_items:
                cursor.execute("""
                INSERT INTO games (name, description, executable_path, category) 
                VALUES (%s, %s, %s, %s)
                """, game)
        
            print("Sample data inserted successfully.")
        else:
            print("Sample data already exists, skipping insertion.")
    except mysql.connector.Error as err:
        print(f"\nERROR inserting sample data: {err}")
        raise

def test_connection():
    """Test database connection with credentials from .env file."""
    print("\nTesting database connection with current .env settings...")
    try:
        host = os.getenv('DB_HOST', 'localhost')
        port = int(os.getenv('DB_PORT', 3306))
        user = os.getenv('DB_USER', 'root')
        password = os.getenv('DB_PASSWORD', '')
        db_name = os.getenv('DB_NAME', 'gaming_lounge_system')
        
        print(f"Connecting to MySQL at {host}:{port} with user '{user}'...")
        
        # First try connecting without specifying a database
        connection = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password
        )
        print("✓ Successfully connected to MySQL server")
        
        # Check if database exists
        cursor = connection.cursor()
        cursor.execute(f"SHOW DATABASES LIKE '{db_name}'")
        if cursor.fetchone():
            print(f"✓ Database '{db_name}' exists")
            
            # Try connecting with the database
            cursor.execute(f"USE {db_name}")
            print(f"✓ Successfully accessed database '{db_name}'")
            
            # Check a few tables
            cursor.execute("SHOW TABLES")
            tables = [table[0] for table in cursor.fetchall()]
            if tables:
                print(f"✓ Found tables: {', '.join(tables)}")
            else:
                print("! No tables found in the database")
        else:
            print(f"! Database '{db_name}' does not exist yet (it will be created)")
        
        cursor.close()
        connection.close()
        print("\nConnection test completed successfully!")
        return True
    except mysql.connector.Error as err:
        if err.errno == 1045:  # Access denied
            print("\n✗ ERROR: Access denied to MySQL.")
            print(f"  Attempted to connect as user '{user}' to {host}:{port}")
        elif err.errno == 2003:  # Can't connect
            print("\n✗ ERROR: Could not connect to MySQL server.")
            print(f"  Attempted to connect to {host}:{port}")
        else:
            print(f"\n✗ ERROR: {err}")
        
        print("\nPlease check your MySQL credentials in the .env file.")
        print("For troubleshooting help, refer to docs/mysql_setup.md")
        return False

if __name__ == "__main__":
    print("=== Gaming Lounge Database Initialization ===")
    
    # First test the connection
    if test_connection():
        try:
            print("\nInitializing database...")
            create_database()
            print("\nDatabase initialization completed successfully!")
        except Exception as e:
            print(f"\nFailed to initialize database: {e}")
            print("For troubleshooting help, refer to docs/mysql_setup.md")
            sys.exit(1)
    else:
        print("\nDatabase connection test failed. Please fix the issues before continuing.")
        sys.exit(1) 