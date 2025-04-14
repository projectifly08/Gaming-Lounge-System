from datetime import datetime
from .db_connection import db
from src.utils.helpers import check_password

class User:
    """User model for the gaming lounge system."""
    
    def __init__(self, id=None, name=None, civil_id=None, phone=None, created_at=None, 
                 username=None, password_hash=None, email=None, is_admin=0):
        self.id = id
        self.name = name
        self.civil_id = civil_id
        self.phone = phone
        self.created_at = created_at or datetime.now()
        self.username = username
        self.password_hash = password_hash
        self.email = email
        self.is_admin = is_admin
    
    @staticmethod
    def create(name, civil_id, phone, username=None, password_hash=None, email=None, is_admin=0):
        """Create a new user in the database."""
        cursor = db.get_cursor()
        try:
            query = """
            INSERT INTO users (name, civil_id, phone, username, password_hash, email, is_admin)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (name, civil_id, phone, username, password_hash, email, is_admin))
            db.commit()
            return cursor.lastrowid
        except Exception as e:
            db.rollback()
            raise e
        finally:
            cursor.close()
    
    @staticmethod
    def get_by_id(user_id):
        """Get a user by ID."""
        cursor = db.get_cursor()
        try:
            query = "SELECT * FROM users WHERE id = %s"
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()
            if result:
                return User(**result)
            return None
        finally:
            cursor.close()
    
    @staticmethod
    def get_by_civil_id(civil_id):
        """Get a user by civil ID."""
        cursor = db.get_cursor()
        try:
            query = "SELECT * FROM users WHERE civil_id = %s"
            cursor.execute(query, (civil_id,))
            result = cursor.fetchone()
            if result:
                return User(**result)
            return None
        finally:
            cursor.close()
    
    @staticmethod
    def get_by_phone(phone):
        """Get a user by phone number."""
        cursor = db.get_cursor()
        try:
            query = "SELECT * FROM users WHERE phone = %s"
            cursor.execute(query, (phone,))
            result = cursor.fetchone()
            if result:
                return User(**result)
            return None
        finally:
            cursor.close()
    
    @staticmethod
    def get_by_username(username):
        """Get a user by username."""
        cursor = db.get_cursor()
        try:
            query = "SELECT * FROM users WHERE username = %s"
            cursor.execute(query, (username,))
            result = cursor.fetchone()
            if result:
                return User(**result)
            return None
        finally:
            cursor.close()
    
    @staticmethod
    def get_all():
        """Get all users."""
        cursor = db.get_cursor()
        try:
            query = "SELECT * FROM users ORDER BY created_at DESC"
            cursor.execute(query)
            results = cursor.fetchall()
            return [User(**result) for result in results]
        finally:
            cursor.close()
    
    @staticmethod
    def authenticate(username, password):
        """Authenticate a user with username and password."""
        user = User.get_by_username(username)
        if user and user.password_hash and check_password(user.password_hash, password):
            return user
        return None
    
    def save(self):
        """Save changes to the user."""
        cursor = db.get_cursor()
        try:
            query = """
            UPDATE users 
            SET name = %s, civil_id = %s, phone = %s, username = %s, 
                password_hash = %s, email = %s, is_admin = %s
            WHERE id = %s
            """
            cursor.execute(query, (
                self.name, self.civil_id, self.phone, self.username,
                self.password_hash, self.email, self.is_admin, self.id
            ))
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            raise e
        finally:
            cursor.close()


class PC:
    """PC model for the gaming lounge system."""
    
    def __init__(self, id=None, pc_number=None, is_occupied=False, 
                 status='available', specs=None):
        self.id = id
        self.pc_number = pc_number
        self.is_occupied = is_occupied
        self.status = status
        self.specs = specs
    
    @staticmethod
    def get_all():
        """Get all PCs."""
        cursor = db.get_cursor()
        try:
            query = "SELECT * FROM pcs ORDER BY pc_number"
            cursor.execute(query)
            results = cursor.fetchall()
            return [PC(**result) for result in results]
        finally:
            cursor.close()
    
    @staticmethod
    def get_by_id(pc_id):
        """Get a PC by ID."""
        cursor = db.get_cursor()
        try:
            query = "SELECT * FROM pcs WHERE id = %s"
            cursor.execute(query, (pc_id,))
            result = cursor.fetchone()
            if result:
                return PC(**result)
            return None
        finally:
            cursor.close()
    
    @staticmethod
    def get_by_number(pc_number):
        """Get a PC by number."""
        cursor = db.get_cursor()
        try:
            query = "SELECT * FROM pcs WHERE pc_number = %s"
            cursor.execute(query, (pc_number,))
            result = cursor.fetchone()
            if result:
                return PC(**result)
            return None
        finally:
            cursor.close()
    
    @staticmethod
    def get_available():
        """Get all available PCs."""
        cursor = db.get_cursor()
        try:
            query = "SELECT * FROM pcs WHERE status = 'available' AND is_occupied = FALSE ORDER BY pc_number"
            cursor.execute(query)
            results = cursor.fetchall()
            return [PC(**result) for result in results]
        finally:
            cursor.close()
    
    @staticmethod
    def get_by_user_id(user_id):
        """Get the PC assigned to a user based on their most recent active session."""
        cursor = db.get_cursor()
        try:
            # First, find the most recent active session for this user
            query = """
            SELECT pc_id 
            FROM sessions 
            WHERE user_id = %s AND status = 'active' 
            ORDER BY start_time DESC 
            LIMIT 1
            """
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()
            
            if not result:
                return None  # No active session found
            
            pc_id = result['pc_id']
            
            # Now get the PC details
            query = "SELECT * FROM pcs WHERE id = %s"
            cursor.execute(query, (pc_id,))
            pc_result = cursor.fetchone()
            
            if pc_result:
                return PC(**pc_result)
            return None
        finally:
            cursor.close()
    
    def update_status(self, status, is_occupied=None):
        """Update the status of a PC."""
        cursor = db.get_cursor()
        try:
            if is_occupied is not None:
                query = "UPDATE pcs SET status = %s, is_occupied = %s WHERE id = %s"
                cursor.execute(query, (status, is_occupied, self.id))
            else:
                query = "UPDATE pcs SET status = %s WHERE id = %s"
                cursor.execute(query, (status, self.id))
            db.commit()
            self.status = status
            if is_occupied is not None:
                self.is_occupied = is_occupied
        except Exception as e:
            db.rollback()
            raise e
        finally:
            cursor.close()
    
    @staticmethod
    def create(pc_number, specs=None):
        """Create a new PC in the database."""
        cursor = db.get_cursor()
        try:
            query = """
            INSERT INTO pcs (pc_number, is_occupied, status, specs)
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (pc_number, False, 'available', specs))
            db.commit()
            return cursor.lastrowid
        except Exception as e:
            db.rollback()
            raise e
        finally:
            cursor.close()


class Session:
    """Session model for the gaming lounge system."""
    
    def __init__(self, id=None, user_id=None, pc_id=None, start_time=None, 
                 end_time=None, duration_minutes=None, status='active', 
                 payment_method=None, payment_amount=None):
        self.id = id
        self.user_id = user_id
        self.pc_id = pc_id
        self.start_time = start_time or datetime.now()
        self.end_time = end_time
        self.duration_minutes = duration_minutes
        self.status = status
        self.payment_method = payment_method
        self.payment_amount = payment_amount
    
    @staticmethod
    def create(user_id, pc_id, duration_minutes, payment_method, payment_amount):
        """Create a new session."""
        cursor = db.get_cursor()
        try:
            # Calculate end time based on duration
            query = """
            INSERT INTO sessions (user_id, pc_id, duration_minutes, payment_method, payment_amount, 
                                 start_time, end_time, status)
            VALUES (%s, %s, %s, %s, %s, %s, DATE_ADD(%s, INTERVAL %s MINUTE), 'active')
            """
            cursor.execute(query, (user_id, pc_id, duration_minutes, payment_method, 
                                  payment_amount, datetime.now(), datetime.now(), duration_minutes))
            session_id = cursor.lastrowid
            
            # Update PC status
            query = "UPDATE pcs SET status = 'occupied', is_occupied = TRUE WHERE id = %s"
            cursor.execute(query, (pc_id,))
            
            db.commit()
            
            # After commit
            query = "SELECT * FROM sessions WHERE id = %s"
            cursor.execute(query, (session_id,))
            session_data = cursor.fetchone()
            if session_data:
                return Session(**session_data)
            return session_id  # Fallback
        except Exception as e:
            db.rollback()
            raise e
        finally:
            cursor.close()
    
    @staticmethod
    def get_by_id(session_id):
        """Get a session by ID."""
        cursor = db.get_cursor()
        try:
            query = "SELECT * FROM sessions WHERE id = %s"
            cursor.execute(query, (session_id,))
            result = cursor.fetchone()
            if result:
                return Session(**result)
            return None
        finally:
            cursor.close()
    
    @staticmethod
    def get_active_sessions():
        """Get all active sessions."""
        cursor = db.get_cursor()
        try:
            query = """
            SELECT s.*, u.name as user_name, p.pc_number 
            FROM sessions s
            JOIN users u ON s.user_id = u.id
            JOIN pcs p ON s.pc_id = p.id
            WHERE s.status = 'active'
            ORDER BY s.start_time DESC
            """
            cursor.execute(query)
            return cursor.fetchall()
        finally:
            cursor.close()
    
    @staticmethod
    def get_active_by_pc(pc_id):
        """Get active session for a PC."""
        cursor = db.get_cursor()
        try:
            query = """
            SELECT * FROM sessions 
            WHERE pc_id = %s AND status = 'active'
            """
            cursor.execute(query, (pc_id,))
            result = cursor.fetchone()
            if result:
                return Session(**result)
            return None
        finally:
            cursor.close()
    
    @staticmethod
    def get_active_by_user(user_id):
        """Get active session for a user."""
        cursor = db.get_cursor()
        try:
            query = """
            SELECT * FROM sessions 
            WHERE user_id = %s AND status = 'active'
            """
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()
            if result:
                return Session(**result)
            return None
        finally:
            cursor.close()
    
    def update_status(self, status):
        """Update the status of a session."""
        cursor = db.get_cursor()
        try:
            query = "UPDATE sessions SET status = %s WHERE id = %s"
            cursor.execute(query, (status, self.id))
            
            # If session is completed or terminated, free up the PC
            if status in ('completed', 'terminated'):
                query = "UPDATE pcs SET status = 'available', is_occupied = FALSE WHERE id = %s"
                cursor.execute(query, (self.pc_id,))
            
            db.commit()
            self.status = status
        except Exception as e:
            db.rollback()
            raise e
        finally:
            cursor.close()
    
    def extend_time(self, additional_minutes, payment_amount, payment_method):
        """Extend the session time."""
        cursor = db.get_cursor()
        try:
            query = """
            UPDATE sessions 
            SET end_time = DATE_ADD(end_time, INTERVAL %s MINUTE),
                duration_minutes = duration_minutes + %s,
                payment_amount = payment_amount + %s
            WHERE id = %s
            """
            cursor.execute(query, (additional_minutes, additional_minutes, 
                                  payment_amount, self.id))
            db.commit()
            self.duration_minutes += additional_minutes
            self.payment_amount += payment_amount
        except Exception as e:
            db.rollback()
            raise e
        finally:
            cursor.close()


class MenuItem:
    """Menu item model for the gaming lounge system."""
    
    def __init__(self, id=None, name=None, description=None, price=None, 
                 category=None, available=True, image_path=None):
        self.id = id
        self.name = name
        self.description = description
        self.price = price
        self.category = category
        self.available = available
        self.image_path = image_path
    
    @staticmethod
    def get_all():
        """Get all menu items."""
        cursor = db.get_cursor()
        try:
            query = "SELECT * FROM menu_items ORDER BY category, name"
            cursor.execute(query)
            results = cursor.fetchall()
            return [MenuItem(**result) for result in results]
        finally:
            cursor.close()
    
    @staticmethod
    def get_by_category(category):
        """Get menu items by category."""
        cursor = db.get_cursor()
        try:
            query = "SELECT * FROM menu_items WHERE category = %s AND available = TRUE ORDER BY name"
            cursor.execute(query, (category,))
            results = cursor.fetchall()
            return [MenuItem(**result) for result in results]
        finally:
            cursor.close()
    
    @staticmethod
    def get_by_id(item_id):
        """Get a menu item by ID."""
        cursor = db.get_cursor()
        try:
            query = "SELECT * FROM menu_items WHERE id = %s"
            cursor.execute(query, (item_id,))
            result = cursor.fetchone()
            if result:
                return MenuItem(**result)
            return None
        finally:
            cursor.close()
    
    @staticmethod
    def create(name, description, price, category, image_path=None):
        """Create a new menu item."""
        cursor = db.get_cursor()
        try:
            query = """
            INSERT INTO menu_items (name, description, price, category, image_path)
            VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, (name, description, price, category, image_path))
            db.commit()
            return cursor.lastrowid
        except Exception as e:
            db.rollback()
            raise e
        finally:
            cursor.close()
    
    def update(self):
        """Update a menu item."""
        cursor = db.get_cursor()
        try:
            query = """
            UPDATE menu_items 
            SET name = %s, description = %s, price = %s, category = %s, 
                available = %s, image_path = %s
            WHERE id = %s
            """
            cursor.execute(query, (self.name, self.description, self.price, 
                                  self.category, self.available, 
                                  self.image_path, self.id))
            db.commit()
        except Exception as e:
            db.rollback()
            raise e
        finally:
            cursor.close()


class MenuItemExtra:
    """Model for menu item extras."""
    
    def __init__(self, id=None, menu_item_id=None, name=None, price=None, available=True):
        self.id = id
        self.menu_item_id = menu_item_id
        self.name = name
        self.price = price
        self.available = available
    
    @staticmethod
    def get_by_menu_item(menu_item_id):
        """Get all extras for a menu item."""
        cursor = db.get_cursor()
        try:
            query = "SELECT * FROM item_extras WHERE menu_item_id = %s AND available = TRUE"
            cursor.execute(query, (menu_item_id,))
            results = cursor.fetchall()
            return [MenuItemExtra(**result) for result in results]
        finally:
            cursor.close()
    
    @staticmethod
    def get_by_id(extra_id):
        """Get an extra by ID."""
        cursor = db.get_cursor()
        try:
            query = "SELECT * FROM item_extras WHERE id = %s"
            cursor.execute(query, (extra_id,))
            result = cursor.fetchone()
            if result:
                return MenuItemExtra(**result)
            return None
        finally:
            cursor.close()
    
    @staticmethod
    def create(menu_item_id, name, price):
        """Create a new menu item extra."""
        cursor = db.get_cursor()
        try:
            query = """
            INSERT INTO item_extras (menu_item_id, name, price)
            VALUES (%s, %s, %s)
            """
            cursor.execute(query, (menu_item_id, name, price))
            db.commit()
            return cursor.lastrowid
        except Exception as e:
            db.rollback()
            raise e
        finally:
            cursor.close()
    
    def update(self):
        """Update a menu item extra."""
        cursor = db.get_cursor()
        try:
            query = """
            UPDATE item_extras 
            SET name = %s, price = %s, available = %s
            WHERE id = %s
            """
            cursor.execute(query, (self.name, self.price, self.available, self.id))
            db.commit()
        except Exception as e:
            db.rollback()
            raise e
        finally:
            cursor.close()
    
    def delete(self):
        """Delete a menu item extra."""
        cursor = db.get_cursor()
        try:
            query = "DELETE FROM item_extras WHERE id = %s"
            cursor.execute(query, (self.id,))
            db.commit()
        except Exception as e:
            db.rollback()
            raise e
        finally:
            cursor.close()


class MenuItemTakeout:
    """Model for menu item takeouts."""
    
    def __init__(self, id=None, menu_item_id=None, name=None, available=True):
        self.id = id
        self.menu_item_id = menu_item_id
        self.name = name
        self.available = available
    
    @staticmethod
    def get_by_menu_item(menu_item_id):
        """Get all takeouts for a menu item."""
        cursor = db.get_cursor()
        try:
            query = "SELECT * FROM item_takeouts WHERE menu_item_id = %s AND available = TRUE"
            cursor.execute(query, (menu_item_id,))
            results = cursor.fetchall()
            return [MenuItemTakeout(**result) for result in results]
        finally:
            cursor.close()
    
    @staticmethod
    def get_by_id(takeout_id):
        """Get a takeout by ID."""
        cursor = db.get_cursor()
        try:
            query = "SELECT * FROM item_takeouts WHERE id = %s"
            cursor.execute(query, (takeout_id,))
            result = cursor.fetchone()
            if result:
                return MenuItemTakeout(**result)
            return None
        finally:
            cursor.close()
    
    @staticmethod
    def create(menu_item_id, name):
        """Create a new menu item takeout."""
        cursor = db.get_cursor()
        try:
            query = """
            INSERT INTO item_takeouts (menu_item_id, name)
            VALUES (%s, %s)
            """
            cursor.execute(query, (menu_item_id, name))
            db.commit()
            return cursor.lastrowid
        except Exception as e:
            db.rollback()
            raise e
        finally:
            cursor.close()
    
    def update(self):
        """Update a menu item takeout."""
        cursor = db.get_cursor()
        try:
            query = """
            UPDATE item_takeouts 
            SET name = %s, available = %s
            WHERE id = %s
            """
            cursor.execute(query, (self.name, self.available, self.id))
            db.commit()
        except Exception as e:
            db.rollback()
            raise e
        finally:
            cursor.close()
    
    def delete(self):
        """Delete a menu item takeout."""
        cursor = db.get_cursor()
        try:
            query = "DELETE FROM item_takeouts WHERE id = %s"
            cursor.execute(query, (self.id,))
            db.commit()
        except Exception as e:
            db.rollback()
            raise e
        finally:
            cursor.close()


class Order:
    """Order model for the gaming lounge system."""
    
    def __init__(self, id=None, session_id=None, status='pending', 
                 order_time=None, delivery_time=None, total_amount=0):
        self.id = id
        self.session_id = session_id
        self.status = status
        self.order_time = order_time or datetime.now()
        self.delivery_time = delivery_time
        self.total_amount = total_amount
        self.items = []
    
    @staticmethod
    def create(session_id, items):
        """
        Create a new order.
        
        Args:
            session_id: The session ID
            items: List of dicts with:
                - menu_item_id: The menu item ID
                - quantity: The quantity
                - extras: List of extra IDs (optional)
                - takeouts: List of takeout IDs (optional)
        """
        cursor = db.get_cursor()
        try:
            # Calculate total amount
            total_amount = 0
            for item in items:
                menu_item_id = item['menu_item_id']
                quantity = item['quantity']
                extras = item.get('extras', [])
                
                # Get menu item price
                cursor.execute("SELECT price FROM menu_items WHERE id = %s", (menu_item_id,))
                result = cursor.fetchone()
                if result:
                    item_price = result['price']
                    item_total = item_price * quantity
                    
                    # Add extras cost
                    for extra_id in extras:
                        cursor.execute("SELECT price FROM item_extras WHERE id = %s", (extra_id,))
                        extra_result = cursor.fetchone()
                        if extra_result:
                            item_total += extra_result['price'] * quantity
                    
                    total_amount += item_total
            
            # Create order
            cursor.execute("""
            INSERT INTO orders (session_id, order_time, total_amount)
            VALUES (%s, %s, %s)
            """, (session_id, datetime.now(), total_amount))
            
            order_id = cursor.lastrowid
            
            # Add order items with extras and takeouts
            for item in items:
                menu_item_id = item['menu_item_id']
                quantity = item['quantity']
                extras = item.get('extras', [])
                takeouts = item.get('takeouts', [])
                
                # Get menu item price
                cursor.execute("SELECT price FROM menu_items WHERE id = %s", (menu_item_id,))
                result = cursor.fetchone()
                if result:
                    price = result['price']
                    
                    # Insert order item
                    cursor.execute("""
                    INSERT INTO order_items (order_id, menu_item_id, quantity, price)
                    VALUES (%s, %s, %s, %s)
                    """, (order_id, menu_item_id, quantity, price))
                    
                    order_item_id = cursor.lastrowid
                    
                    # Add extras
                    for extra_id in extras:
                        cursor.execute("SELECT price FROM item_extras WHERE id = %s", (extra_id,))
                        extra_result = cursor.fetchone()
                        if extra_result:
                            extra_price = extra_result['price']
                            cursor.execute("""
                            INSERT INTO order_item_extras (order_item_id, extra_id, price)
                            VALUES (%s, %s, %s)
                            """, (order_item_id, extra_id, extra_price))
                    
                    # Add takeouts
                    for takeout_id in takeouts:
                        cursor.execute("""
                        INSERT INTO order_item_takeouts (order_item_id, takeout_id)
                        VALUES (%s, %s)
                        """, (order_item_id, takeout_id))
            
            db.commit()
            return order_id
        except Exception as e:
            db.rollback()
            raise e
        finally:
            cursor.close()
    
    @staticmethod
    def get_by_id(order_id):
        """Get an order by ID with additional details."""
        cursor = db.get_cursor()
        try:
            query = """
            SELECT o.*, s.id as session_id, u.name as user_name, p.pc_number
            FROM orders o
            JOIN sessions s ON o.session_id = s.id
            JOIN users u ON s.user_id = u.id
            JOIN pcs p ON s.pc_id = p.id
            WHERE o.id = %s
            """
            cursor.execute(query, (order_id,))
            result = cursor.fetchone()
            if not result:
                return None

            order = Order(
                id=result['id'],
                session_id=result['session_id'],
                status=result['status'],
                order_time=result['order_time'],
                delivery_time=result['delivery_time'],
                total_amount=result['total_amount']
            )

            # Add additional info
            order.user_name = result['user_name']
            order.pc_number = result['pc_number']

            # Get order items with extras and takeouts
            query = """
            SELECT oi.*, mi.name, mi.category
            FROM order_items oi
            JOIN menu_items mi ON oi.menu_item_id = mi.id
            WHERE oi.order_id = %s
            """
            cursor.execute(query, (order.id,))
            order_items = cursor.fetchall()
            
            # Process order items and add extras/takeouts
            order.items = []
            for item in order_items:
                item_dict = dict(item)
                
                # Get extras for this order item
                extras_query = """
                SELECT oie.*, ie.name, ie.price
                FROM order_item_extras oie
                JOIN item_extras ie ON oie.extra_id = ie.id
                WHERE oie.order_item_id = %s
                """
                cursor.execute(extras_query, (item['id'],))
                item_dict['extras'] = cursor.fetchall()
                
                # Get takeouts for this order item
                takeouts_query = """
                SELECT oit.*, it.name
                FROM order_item_takeouts oit
                JOIN item_takeouts it ON oit.takeout_id = it.id
                WHERE oit.order_item_id = %s
                """
                cursor.execute(takeouts_query, (item['id'],))
                item_dict['takeouts'] = cursor.fetchall()
                
                order.items.append(item_dict)

            return order
        finally:
            cursor.close()
    
    @staticmethod
    def get_by_session(session_id):
        """Get orders for a session."""
        cursor = db.get_cursor()
        try:
            query = "SELECT * FROM orders WHERE session_id = %s ORDER BY order_time DESC"
            cursor.execute(query, (session_id,))
            results = cursor.fetchall()
            
            orders = []
            for result in results:
                order = Order(**result)
                
                # Get order items with extras and takeouts
                query = """
                SELECT oi.*, mi.name, mi.category
                FROM order_items oi
                JOIN menu_items mi ON oi.menu_item_id = mi.id
                WHERE oi.order_id = %s
                """
                cursor.execute(query, (order.id,))
                order_items = cursor.fetchall()
                
                # Process order items and add extras/takeouts
                order.items = []
                for item in order_items:
                    item_dict = dict(item)
                    
                    # Get extras for this order item
                    extras_query = """
                    SELECT oie.*, ie.name, ie.price
                    FROM order_item_extras oie
                    JOIN item_extras ie ON oie.extra_id = ie.id
                    WHERE oie.order_item_id = %s
                    """
                    cursor.execute(extras_query, (item['id'],))
                    item_dict['extras'] = cursor.fetchall()
                    
                    # Get takeouts for this order item
                    takeouts_query = """
                    SELECT oit.*, it.name
                    FROM order_item_takeouts oit
                    JOIN item_takeouts it ON oit.takeout_id = it.id
                    WHERE oit.order_item_id = %s
                    """
                    cursor.execute(takeouts_query, (item['id'],))
                    item_dict['takeouts'] = cursor.fetchall()
                    
                    order.items.append(item_dict)
                
                orders.append(order)
            
            return orders
        finally:
            cursor.close()
    
    @staticmethod
    def get_pending_orders():
        """Get all pending orders."""
        cursor = db.get_cursor()
        try:
            query = """
            SELECT o.*, s.id as session_id, u.name as user_name, p.pc_number
            FROM orders o
            JOIN sessions s ON o.session_id = s.id
            JOIN users u ON s.user_id = u.id
            JOIN pcs p ON s.pc_id = p.id
            WHERE o.status = 'pending' OR o.status = 'preparing' OR o.status = 'ready'
            ORDER BY o.order_time
            """
            cursor.execute(query)
            results = cursor.fetchall()
            
            orders = []
            for result in results:
                order = Order(
                    id=result['id'],
                    session_id=result['session_id'],
                    status=result['status'],
                    order_time=result['order_time'],
                    delivery_time=result['delivery_time'],
                    total_amount=result['total_amount']
                )
                
                # Add additional info
                order.user_name = result['user_name']
                order.pc_number = result['pc_number']
                
                # Get order items with extras and takeouts
                query = """
                SELECT oi.*, mi.name, mi.category
                FROM order_items oi
                JOIN menu_items mi ON oi.menu_item_id = mi.id
                WHERE oi.order_id = %s
                """
                cursor.execute(query, (order.id,))
                order_items = cursor.fetchall()
                
                # Process order items and add extras/takeouts
                order.items = []
                for item in order_items:
                    item_dict = dict(item)
                    
                    # Get extras for this order item
                    extras_query = """
                    SELECT oie.*, ie.name, ie.price
                    FROM order_item_extras oie
                    JOIN item_extras ie ON oie.extra_id = ie.id
                    WHERE oie.order_item_id = %s
                    """
                    cursor.execute(extras_query, (item['id'],))
                    item_dict['extras'] = cursor.fetchall()
                    
                    # Get takeouts for this order item
                    takeouts_query = """
                    SELECT oit.*, it.name
                    FROM order_item_takeouts oit
                    JOIN item_takeouts it ON oit.takeout_id = it.id
                    WHERE oit.order_item_id = %s
                    """
                    cursor.execute(takeouts_query, (item['id'],))
                    item_dict['takeouts'] = cursor.fetchall()
                    
                    order.items.append(item_dict)
                
                orders.append(order)
            
            return orders
        finally:
            cursor.close()
    
    def update_status(self, status):
        """Update the status of an order."""
        cursor = db.get_cursor()
        try:
            if status == 'delivered':
                query = """
                UPDATE orders 
                SET status = %s, delivery_time = %s
                WHERE id = %s
                """
                cursor.execute(query, (status, datetime.now(), self.id))
            else:
                query = """
                UPDATE orders 
                SET status = %s
                WHERE id = %s
                """
                cursor.execute(query, (status, self.id))
            db.commit()
            self.status = status
            if status == 'delivered':
                self.delivery_time = datetime.now()
        except Exception as e:
            db.rollback()
            raise e
        finally:
            cursor.close()


class Game:
    """Game model for the gaming lounge system."""
    
    def __init__(self, id=None, name=None, description=None, executable_path=None,
                 image_path=None, category=None, is_available=True):
        self.id = id
        self.name = name
        self.description = description
        self.executable_path = executable_path
        self.image_path = image_path
        self.category = category
        self.is_available = is_available
    
    @staticmethod
    def get_all():
        """Get all games."""
        cursor = db.get_cursor()
        try:
            query = "SELECT * FROM games WHERE is_available = TRUE ORDER BY name"
            cursor.execute(query)
            results = cursor.fetchall()
            return [Game(**result) for result in results]
        finally:
            cursor.close()
    
    @staticmethod
    def get_by_id(game_id):
        """Get a game by ID."""
        cursor = db.get_cursor()
        try:
            query = "SELECT * FROM games WHERE id = %s"
            cursor.execute(query, (game_id,))
            result = cursor.fetchone()
            if result:
                return Game(**result)
            return None
        finally:
            cursor.close()
    
    @staticmethod
    def get_by_category(category):
        """Get games by category."""
        cursor = db.get_cursor()
        try:
            query = "SELECT * FROM games WHERE category = %s AND is_available = TRUE ORDER BY name"
            cursor.execute(query, (category,))
            results = cursor.fetchall()
            return [Game(**result) for result in results]
        finally:
            cursor.close() 