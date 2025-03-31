import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                           QLabel, QLineEdit, QPushButton, QStackedWidget, QMessageBox, 
                           QFrame, QGraphicsDropShadowEffect, QDialog, QGridLayout, QScrollArea, QSpinBox, QTableWidgetItem)
from PyQt5.QtCore import Qt, QTimer, QSettings
from PyQt5.QtGui import QColor, QFont, QPixmap, QPainter, QPainterPath
from ..database import db, User, Session, PC, Order
from src.utils.helpers import set_background_image, verify_password
import os
from src.common import add_close_button
from datetime import datetime, timedelta
from src.common.ui_components import StyledTable

class RoundedImageLabel(QLabel):
    """A QLabel that displays images with rounded corners."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.radius = 20

    def paintEvent(self, event):
        if not self.pixmap():
            return super().paintEvent(event)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Create rounded rect path
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), self.radius, self.radius)
        
        # Set the clip path
        painter.setClipPath(path)
        
        # Draw the pixmap
        scaled_pixmap = self.pixmap().scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        x = (self.width() - scaled_pixmap.width()) // 2
        y = (self.height() - scaled_pixmap.height()) // 2
        painter.drawPixmap(x, y, scaled_pixmap)

class ModernButton(QPushButton):
    """Custom button with modern styling."""
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
        """)

class ExitPasswordDialog(QDialog):
    """Dialog for exit password verification."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Exit Verification")
        self.setModal(True)
        self.setFixedSize(400, 250)
        self.setStyleSheet("""
            QDialog {
                background-color: #1a1a2e;
                color: white;
                border: 1px solid rgba(0, 195, 255, 0.5);
                border-radius: 10px;
            }
            QLabel {
                color: white;
                font-size: 14px;
            }
            QLineEdit {
                border: 1px solid rgba(0, 195, 255, 0.5);
                border-radius: 5px;
                padding: 8px 15px;
                background-color: rgba(25, 25, 40, 0.7);
                color: white;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #00c3ff;
                background-color: rgba(30, 30, 50, 0.9);
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0078d7, stop:1 #00c3ff);
                color: white;
                border: none;
                border-radius: 5px;
                min-width: 80px;
                min-height: 30px;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0086ef, stop:1 #19ceff);
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # Title with glowing effect
        title = QLabel("SECURITY VERIFICATION")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #00c3ff; letter-spacing: 2px; margin-bottom: 10px;")
        
        # Add glow effect to the title
        glow = QGraphicsDropShadowEffect()
        glow.setBlurRadius(15)
        glow.setColor(QColor(0, 195, 255, 160))
        glow.setOffset(0, 0)
        title.setGraphicsEffect(glow)
        
        layout.addWidget(title)
        
        # Add message
        message = QLabel("Please enter the exit password:")
        message.setAlignment(Qt.AlignCenter)
        layout.addWidget(message)
        
        # Password input
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Enter exit password")
        layout.addWidget(self.password_input)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        self.exit_button = QPushButton("Exit")
        self.exit_button.clicked.connect(self.accept)
        button_layout.addWidget(self.exit_button)
        
        layout.addLayout(button_layout)
        
        # Connect enter key to submit
        self.password_input.returnPressed.connect(self.exit_button.click)
        
    def get_password(self):
        """Return the entered password."""
        return self.password_input.text()

class GameCard(QFrame):
    """A card widget to display a game with icon and launch button."""
    def __init__(self, game, parent=None):
        super().__init__(parent)
        self.game = game
        self.setFixedSize(180, 220)
        self.setStyleSheet("""
            QFrame {
                background-color: rgba(25, 25, 40, 0.7);
                border: 1px solid rgba(0, 195, 255, 0.5);
                border-radius: 10px;
            }
            QFrame:hover {
                background-color: rgba(35, 35, 50, 0.8);
                border: 1px solid rgba(0, 195, 255, 0.8);
            }
            QLabel {
                color: white;
                background-color: transparent;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0078d7, stop:1 #00c3ff);
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0086ef, stop:1 #19ceff);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #006acf, stop:1 #00b2e8);
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        # Game Icon
        self.icon_label = QLabel()
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setFixedSize(120, 120)
        
        # Use image if available, otherwise use a placeholder
        image_path = self.get_game_attribute(['image_path', 'icon_path'])
        if image_path and os.path.exists(image_path):
            pixmap = QPixmap(image_path)
        else:
            # Use a default game icon
            pixmap = QPixmap("src/assets/game_icon.png")
            if not os.path.exists("src/assets/game_icon.png"):
                # Create a colored rectangle as fallback
                pixmap = QPixmap(120, 120)
                pixmap.fill(QColor("#0078d7"))
        
        scaled_pixmap = pixmap.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.icon_label.setPixmap(scaled_pixmap)
        
        # Center the icon
        icon_container = QWidget()
        icon_layout = QHBoxLayout(icon_container)
        icon_layout.setAlignment(Qt.AlignCenter)
        icon_layout.addWidget(self.icon_label)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(icon_container)
        
        # Game Name
        game_name = self.get_game_attribute(['name', 'title'])
        self.name_label = QLabel(game_name or "Unknown Game")
        self.name_label.setAlignment(Qt.AlignCenter)
        self.name_label.setWordWrap(True)
        self.name_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.name_label.setStyleSheet("color: #00c3ff;")
        layout.addWidget(self.name_label)
        
        # Launch Button
        self.launch_button = QPushButton("LAUNCH")
        self.launch_button.setCursor(Qt.PointingHandCursor)
        self.launch_button.clicked.connect(self.launch_game)
        layout.addWidget(self.launch_button)
    
    def get_game_attribute(self, possible_keys):
        """Get a game attribute by trying different possible column names."""
        if isinstance(self.game, dict):
            for key in possible_keys:
                if key in self.game and self.game[key]:
                    return self.game[key]
        else:
            for key in possible_keys:
                if hasattr(self.game, key) and getattr(self.game, key):
                    return getattr(self.game, key)
        return None
    
    def launch_game(self):
        """Launch the game executable."""
        try:
            import subprocess
            
            # Get the executable path
            exe_path = self.get_game_attribute(['executable_path', 'path', 'exe_path'])
            
            if exe_path:
                # Show a launching message
                QMessageBox.information(
                    self, 
                    "Launching Game",
                    f"Launching {self.name_label.text()}...\nPlease wait.",
                    QMessageBox.Ok
                )
                
                # Start the game process
                subprocess.Popen(exe_path, shell=True)
            else:
                QMessageBox.warning(
                    self,
                    "Game Error",
                    f"Could not find executable path for {self.name_label.text()}.",
                    QMessageBox.Ok
                )
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Launch Error", 
                f"Failed to launch game: {str(e)}",
                QMessageBox.Ok
            )

class MenuItemCard(QFrame):
    """A card widget to display a menu item with pricing and order button."""
    def __init__(self, menu_item, parent=None):
        super().__init__(parent)
        self.menu_item = menu_item
        self.parent_window = parent
        self.setFixedSize(250, 240)  # Increased width and height for better visibility
        self.setStyleSheet("""
            QFrame {
                background-color: rgba(25, 25, 40, 0.9);  /* Increased opacity for better contrast */
                border: 2px solid rgba(0, 195, 255, 0.5);  /* Thicker border */
                border-radius: 10px;
                padding: 10px;
                margin: 10px;
            }
            QFrame:hover {
                background-color: rgba(35, 35, 50, 0.95);
                border: 2px solid rgba(0, 195, 255, 0.8);
            }
            QLabel {
                color: white;
                background-color: transparent;
                padding: 2px;
                margin: 2px;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ff5722, stop:1 #ff9800);
                color: white;
                border: none;
                border-radius: 5px;
                padding: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ff7043, stop:1 #ffb74d);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #e64a19, stop:1 #f57c00);
            }
            QSpinBox {
                background-color: rgba(40, 40, 60, 0.7);
                border: 1px solid rgba(0, 195, 255, 0.5);
                border-radius: 5px;
                padding: 5px;
                color: white;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                background-color: rgba(0, 195, 255, 0.5);
                border-radius: 3px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)  # Increased margins
        layout.setSpacing(8)  # Increased spacing
        
        # Menu Item Name
        item_name = self.get_item_attribute(['name'])
        self.name_label = QLabel(item_name or "Unknown Item")
        self.name_label.setAlignment(Qt.AlignCenter)
        self.name_label.setWordWrap(True)
        self.name_label.setFont(QFont("Segoe UI", 14, QFont.Bold))  # Larger font
        self.name_label.setStyleSheet("color: #00c3ff; margin-bottom: 10px;")
        self.name_label.setMinimumHeight(45)  # Ensure enough height for text
        layout.addWidget(self.name_label)
        
        # Category
        category = self.get_item_attribute(['category'])
        if category:
            category_label = QLabel(f"Category: {category.capitalize()}")
            category_label.setAlignment(Qt.AlignCenter)
            category_label.setFont(QFont("Segoe UI", 11))  # Increased font size
            category_label.setMinimumHeight(35)  # Fixed height
            layout.addWidget(category_label)
        
        # Price
        price = self.get_item_attribute(['price'])
        if price:
            price_label = QLabel(f"Price: ${float(price):.2f}")
            price_label.setAlignment(Qt.AlignCenter)
            price_label.setFont(QFont("Segoe UI", 13, QFont.Bold))  # Increased font size
            price_label.setStyleSheet("color: #ffc107; margin: 5px 0;")  # Added margin
            price_label.setMinimumHeight(35)  # Fixed height
            layout.addWidget(price_label)
        
        # Spacer
        layout.addSpacing(5)
        
        # Quantity selection
        quantity_layout = QHBoxLayout()
        quantity_layout.setContentsMargins(5, 5, 5, 5)
        quantity_label = QLabel("Qty:")
        quantity_label.setFont(QFont("Segoe UI", 12)) 
        quantity_label.setMinimumHeight(30)  # Increased font size
        quantity_layout.addWidget(quantity_label)
        
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setMinimum(1)
        self.quantity_spin.setMaximum(10)
        self.quantity_spin.setValue(1)
        self.quantity_spin.setFixedHeight(30)  # Fixed height
        quantity_layout.addWidget(self.quantity_spin)
        layout.addLayout(quantity_layout)
        
        layout.addSpacing(10)  # More space between quantity and button
        
        # Order Button
        self.order_button = QPushButton("ORDER")
        self.order_button.setFont(QFont("Segoe UI", 12, QFont.Bold))  # Increased font size
        self.order_button.setCursor(Qt.PointingHandCursor)
        self.order_button.setMinimumHeight(35)  # Increased height
        self.order_button.clicked.connect(self.place_order)
        layout.addWidget(self.order_button)
    
    def get_item_attribute(self, possible_keys):
        """Get a menu item attribute by trying different possible column names."""
        if isinstance(self.menu_item, dict):
            for key in possible_keys:
                if key in self.menu_item and self.menu_item[key]:
                    return self.menu_item[key]
        else:
            for key in possible_keys:
                if hasattr(self.menu_item, key) and getattr(self.menu_item, key):
                    return getattr(self.menu_item, key)
        return None
    
    def place_order(self):
        """Place an order for this menu item."""
        cursor = None
        try:
            # Check for active user session
            if not self.parent_window.current_user or not self.parent_window.current_session:
                QMessageBox.warning(self, "Error", "No active user session found.")
                return
            
            # Get item details
            item_id = self.get_item_attribute(['id'])
            item_name = self.name_label.text()
            item_price = float(self.get_item_attribute(['price']))
            quantity = self.quantity_spin.value()
            
            # Get user ID
            user_id = None
            if hasattr(self.parent_window.current_user, 'id'):
                user_id = self.parent_window.current_user.id
            elif isinstance(self.parent_window.current_user, dict) and 'id' in self.parent_window.current_user:
                user_id = self.parent_window.current_user['id']
            
            if not user_id:
                QMessageBox.warning(self, "Error", "Cannot determine user ID.")
                return
                
            # Get session ID
            session_id = None
            if isinstance(self.parent_window.current_session, dict) and 'id' in self.parent_window.current_session:
                session_id = self.parent_window.current_session['id']
            elif hasattr(self.parent_window.current_session, 'id'):
                session_id = self.parent_window.current_session.id
            
            if not session_id:
                QMessageBox.warning(self, "Error", "Cannot determine session ID.")
                return
            
            # Verify the menu item is still available
            cursor = db.get_cursor()
            try:
                # Check if item exists and is active
                cursor.execute("SELECT * FROM menu_items WHERE id = %s", (item_id,))
                menu_item = cursor.fetchone()
                
                if not menu_item:
                    QMessageBox.warning(self, "Error", "This menu item is no longer available.")
                    return
            except Exception as e:
                print(f"Menu item verification error: {str(e)}")
                # Continue anyway if verification fails
            
            # Calculate total amount
            total_amount = item_price * quantity
            
            # First create the order with appropriate values
            cursor.execute("""
                INSERT INTO orders (session_id, status, total_amount)
                VALUES (%s, %s, %s)
            """, (
                session_id,
                'pending',
                total_amount
            ))
            
            order_id = cursor.lastrowid
            
            # Then add the order item
            cursor.execute("""
                INSERT INTO order_items (order_id, menu_item_id, quantity, price)
                VALUES (%s, %s, %s, %s)
            """, (
                order_id,
                item_id,
                quantity,
                item_price
            ))
            
            db.commit()
            
            # Show success message with order details
            QMessageBox.information(
                self, 
                "Order Placed", 
                f"Your order for {quantity} x {item_name} has been placed!\n\n"
                f"Total: ${total_amount:.2f}\n"
                "Your order status is now 'pending'. Staff will deliver your order shortly.",
                QMessageBox.Ok
            )

            self.parent_window.load_user_orders()
            
            # Reset quantity to 1 after successful order
            self.quantity_spin.setValue(1)
            
        except Exception as e:
            if cursor and db:
                db.rollback()
            QMessageBox.critical(
                self, 
                "Order Error", 
                f"Failed to place order: {str(e)}"
                "\nPlease try again or contact staff for assistance.",
                QMessageBox.Ok
            )
            import traceback
            traceback.print_exc()
        finally:
            if cursor:
                cursor.close()


class LauncherMainWindow(QMainWindow):
    def __init__(self, pc_number=None):
        super().__init__()
        self.pc_number = pc_number
        self.current_user = None
        self.current_session = None
        self.remaining_time = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        
        # Add orders refresh timer
        self.orders_refresh_timer = QTimer()
        self.orders_refresh_timer.timeout.connect(self.load_user_orders)
        
        # Exit password tracking
        self.exit_password_attempts = 0
        self.exit_password_locked_until = None
        
        self.setWindowTitle("Gaming Lounge Launcher")
        self.setMinimumSize(800, 600)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1E1E1E;
            }
            QLabel {
                color: white;
                font-size: 14px;
            }
            QLineEdit {
                padding: 10px;
                border: 2px solid #2196F3;
                border-radius: 5px;
                background-color: #2C3E50;
                color: white;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #64B5F6;
            }
            QMessageBox {
                background-color: #2C3E50;
                color: white;
            }
            QMessageBox QLabel {
                color: white;
                font-size: 14px;
            }
            QMessageBox QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 12px;
                min-width: 80px;
            }
            QMessageBox QPushButton:hover {
                background-color: #1976D2;
            }
            QMessageBox QPushButton:pressed {
                background-color: #0D47A1;
            }
        """)

        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Set background image to the central widget
        set_background_image(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(50, 50, 50, 50)
        main_layout.setSpacing(20)
        
        # Create stacked widget for different pages
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)
        
        # Create and add pages
        self.login_page = self.create_login_page()
        self.main_page = self.create_main_page()
        self.food_menu_page = self.create_food_menu_page()
        
        self.stacked_widget.addWidget(self.login_page)
        self.stacked_widget.addWidget(self.main_page)
        self.stacked_widget.addWidget(self.food_menu_page)
        
        # Show login page initially
        self.stacked_widget.setCurrentWidget(self.login_page)
        
        # Make window fullscreen
        self.showFullScreen()

        # Add close button
        self.close_button = add_close_button(self)
    
    def create_login_page(self):
        """Create the login page with modern gaming styling."""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignCenter)
        
        # Create login form container with gaming theme
        login_container = QFrame()
        login_container.setObjectName("loginContainer")
        login_container.setMinimumWidth(800)
        login_container.setMinimumHeight(700)
        login_container.setStyleSheet("""
            #loginContainer {
                background-color: rgba(18, 18, 30, 0.85);
                border: 1px solid rgba(0, 195, 255, 0.5);
                border-radius: 15px;
                padding: 20px;
            }
        """)
        
        # Add shadow effect to the login container
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 195, 255, 160))
        shadow.setOffset(0, 0)
        login_container.setGraphicsEffect(shadow)
        
        login_layout = QVBoxLayout(login_container)
        login_layout.setContentsMargins(30, 30, 30, 30)
        login_layout.setSpacing(20)
        
        # Logo/Header with gaming style
        logo_layout = QVBoxLayout()
        logo_layout.setAlignment(Qt.AlignCenter)
        logo_layout.setSpacing(0)
        
        # Add logo image
        logo_label = RoundedImageLabel()
        logo_label.setFixedSize(150, 150)
        logo_pixmap = QPixmap("src/assets/logo.jpg")
        logo_label.setPixmap(logo_pixmap)
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setStyleSheet("""
            background-color: transparent;
            margin: 0 auto;
        """)
        
        # Center the logo in its container
        logo_container = QWidget()
        logo_container_layout = QHBoxLayout(logo_container)
        logo_container_layout.setAlignment(Qt.AlignCenter)
        logo_container_layout.addWidget(logo_label)
        logo_container_layout.setContentsMargins(0, 0, 0, 0)
        logo_layout.addWidget(logo_container)
        
        # Add title (with massive size emphasis)
        header_label = QLabel("WELCOME TO\nTHE GAMING LOUNGE")
        header_label.setFont(QFont("Segoe UI", 38, QFont.Bold))
        header_label.setStyleSheet("""
            color: #00c3ff;
            letter-spacing: 3px;
            font-size: 48px !important;
            font-weight: bold;
            line-height: 1.2;
            padding: 10px;
        """)
        header_label.setWordWrap(True)
        header_label.setMinimumHeight(80)
        header_label.setAlignment(Qt.AlignCenter)
        
        # Add glow effect to the header
        header_glow = QGraphicsDropShadowEffect()
        header_glow.setBlurRadius(20)
        header_glow.setColor(QColor(0, 195, 255, 200))
        header_glow.setOffset(0, 0)
        header_label.setGraphicsEffect(header_glow)
        
        logo_layout.addWidget(header_label)
        
        login_layout.addLayout(logo_layout)
        
        # Subtitle with gaming style
        subtitle = QLabel("LAUNCHER AUTHENTICATION")
        subtitle.setFont(QFont("Segoe UI", 10))
        subtitle.setStyleSheet("color: #8a8aff; letter-spacing: 2px;")
        subtitle.setAlignment(Qt.AlignCenter)
        login_layout.addWidget(subtitle)
        
        # Add decorative line
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("background-color: rgba(0, 195, 255, 0.5); border: none; height: 1px;")
        login_layout.addWidget(line)
        
        login_layout.addSpacing(20)
        
        # User ID field with gaming style
        user_id_layout = QVBoxLayout()
        user_id_label = QLabel("CIVIL ID / PHONE NUMBER")
        user_id_label.setFont(QFont("Segoe UI", 10))
        user_id_label.setStyleSheet("color: #00c3ff; letter-spacing: 1px;")
        user_id_layout.addWidget(user_id_label)
        
        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText("Enter your Civil ID or Phone Number")
        self.login_input.setMinimumHeight(45)
        self.login_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid rgba(0, 195, 255, 0.5);
                border-radius: 5px;
                padding: 8px 15px;
                background-color: rgba(25, 25, 40, 0.7);
                color: white;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #00c3ff;
                background-color: rgba(30, 30, 50, 0.9);
            }
        """)
        user_id_layout.addWidget(self.login_input)
        login_layout.addLayout(user_id_layout)
        
        login_layout.addSpacing(25)
        
        # Login button with gaming style
        login_button = QPushButton("LOGIN")
        login_button.setMinimumHeight(50)
        login_button.setCursor(Qt.PointingHandCursor)
        login_button.setFont(QFont("Segoe UI", 12, QFont.Bold))
        login_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0078d7, stop:1 #00c3ff);
                color: white;
                border: none;
                border-radius: 5px;
                letter-spacing: 1px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0086ef, stop:1 #19ceff);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #006acf, stop:1 #00b2e8);
            }
        """)
        login_button.clicked.connect(self.handle_login)
        login_layout.addWidget(login_button)
        
        # Exit button with gaming style
        exit_button = QPushButton("EXIT")
        exit_button.setMinimumHeight(40)
        exit_button.setCursor(Qt.PointingHandCursor)
        exit_button.setFont(QFont("Segoe UI", 10))
        exit_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(40, 40, 60, 0.7);
                color: #8a8aff;
                border: 1px solid rgba(138, 138, 255, 0.3);
                border-radius: 5px;
                letter-spacing: 1px;
            }
            QPushButton:hover {
                background-color: rgba(50, 50, 70, 0.9);
                border: 1px solid rgba(138, 138, 255, 0.5);
            }
            QPushButton:pressed {
                background-color: rgba(30, 30, 50, 0.9);
            }
        """)
        exit_button.clicked.connect(self.attempt_close)
        login_layout.addWidget(exit_button)
        
        # Add login container to main layout
        layout.addStretch()
        layout.addWidget(login_container)
        layout.addStretch()
        
        # Set focus to login input
        self.login_input.setFocus()
        
        return page
    
    def create_main_page(self):
        """Create the main page with game launcher and session timer."""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Top bar with user info and timer
        top_bar = QFrame()
        top_bar.setObjectName("topBar")
        top_bar.setStyleSheet("""
            #topBar {
                background-color: rgba(18, 18, 30, 0.85);
                border: 1px solid rgba(0, 195, 255, 0.5);
                border-radius: 10px;
                padding: 10px;
            }
        """)
        top_bar_layout = QHBoxLayout(top_bar)
        
        # User info
        self.user_label = QLabel()
        self.user_label.setStyleSheet("font-size: 16px; font-weight: bold; color: white;")
        top_bar_layout.addWidget(self.user_label)
        
        # Add Order Food button
        order_food_button = QPushButton("ORDER FOOD")
        order_food_button.setCursor(Qt.PointingHandCursor)
        order_food_button.setFixedWidth(150)
        order_food_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ff5722, stop:1 #ff9800);
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ff7043, stop:1 #ffb74d);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #e64a19, stop:1 #f57c00);
            }
        """)
        order_food_button.clicked.connect(self.show_food_menu)
        top_bar_layout.addWidget(order_food_button)
        
        # Timer
        self.timer_label = QLabel()
        self.timer_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #00c3ff;")
        self.timer_label.setAlignment(Qt.AlignRight)
        top_bar_layout.addWidget(self.timer_label)
        
        layout.addWidget(top_bar)
        
        # Games section title
        games_title = QLabel("AVAILABLE GAMES")
        games_title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        games_title.setStyleSheet("color: #00c3ff; margin-top: 10px;")
        games_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(games_title)
        
        # Decorative line
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("background-color: rgba(0, 195, 255, 0.5); border: none; height: 2px;")
        layout.addWidget(line)
        
        # Games grid
        self.games_container = QWidget()
        self.games_container.setStyleSheet("""
                background-color: rgba(18, 18, 30, 0.85);
                border: 1px solid rgba(0, 195, 255, 0.5);
                border-radius: 10px;
                padding: 10px;
        """)
        self.games_layout = QGridLayout(self.games_container)
        self.games_layout.setContentsMargins(10, 10, 10, 10)
        self.games_layout.setSpacing(20)
        
        # Games will be dynamically populated in load_games method
        
        # Add games container to scrollable area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.games_container)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background: rgba(25, 25, 40, 0.5);
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: rgba(0, 195, 255, 0.7);
                min-height: 30px;
                border-radius: 6px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        layout.addWidget(scroll_area)
        
        return page
    
    def create_food_menu_page(self):
        """Create the food menu page with available items and order status."""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header with title and back button
        header = QHBoxLayout()
        
        # Back button
        back_button = QPushButton("◀ BACK TO GAMES")
        back_button.setCursor(Qt.PointingHandCursor)
        back_button.setFixedWidth(200)
        back_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(30, 30, 50, 0.7);
                color: white;
                border: 1px solid rgba(0, 195, 255, 0.5);
                border-radius: 5px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(40, 40, 60, 0.8);
                border: 1px solid rgba(0, 195, 255, 0.8);
            }
        """)
        back_button.clicked.connect(self.show_main_page)
        header.addWidget(back_button)
        
        # Title
        title = QLabel("FOOD & DRINKS MENU")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setStyleSheet("color: #ff9800;")
        title.setAlignment(Qt.AlignCenter)
        header.addWidget(title)
        
        # Placeholder for user info
        user_info = QLabel()
        user_info.setFixedWidth(200)
        header.addWidget(user_info)
        
        layout.addLayout(header)
        
        # Decorative line
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("background-color: rgba(255, 152, 0, 0.5); border: none; height: 2px;")
        layout.addWidget(line)
        
        # Container for menu items
        menu_container = QWidget()
        menu_container.setStyleSheet("""
            background-color: rgba(18, 18, 30, 0.85);
            border: 1px solid rgba(255, 152, 0, 0.5);
            border-radius: 10px;
            padding: 10px;
        """)
        self.menu_layout = QGridLayout(menu_container)
        self.menu_layout.setContentsMargins(10, 10, 10, 10)
        self.menu_layout.setSpacing(20)
        
        # Menu items will be dynamically populated in load_menu_items method
        
        # Add menu container to scrollable area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(menu_container)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background: rgba(25, 25, 40, 0.5);
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: rgba(255, 152, 0, 0.7);
                min-height: 30px;
                border-radius: 6px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        layout.addWidget(scroll_area, 1)
        
        # Order Status Section
        order_status_section = QWidget()
        order_status_layout = QVBoxLayout(order_status_section)

        # Header with refresh button
        header_layout = QHBoxLayout()
        
        # Title
        order_status_header = QLabel("Your Orders")
        order_status_header.setFont(QFont("Segoe UI", 16, QFont.Bold))
        order_status_header.setStyleSheet("color: #00c3ff;")
        header_layout.addWidget(order_status_header)
        
        # Add stretch to push refresh button to the right
        header_layout.addStretch()
        
        # Refresh button with icon
        refresh_button = QPushButton("🔄")
        refresh_button.setCursor(Qt.PointingHandCursor)
        refresh_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(0, 195, 255, 0.2);
                color: #00c3ff;
                border: 1px solid rgba(0, 195, 255, 0.5);
                border-radius: 5px;
                padding: 5px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(0, 195, 255, 0.3);
                border: 1px solid rgba(0, 195, 255, 0.8);
            }
            QPushButton:pressed {
                background-color: rgba(0, 195, 255, 0.4);
            }
        """)
        refresh_button.clicked.connect(self.load_user_orders)
        header_layout.addWidget(refresh_button)
        
        order_status_layout.addLayout(header_layout)

        # Orders table
        self.orders_table = StyledTable()
        self.orders_table.setColumnCount(4)
        self.orders_table.setHorizontalHeaderLabels(["Order #", "Items", "Status", "Action"])
        order_status_layout.addWidget(self.orders_table)

        layout.addWidget(order_status_section)

        return page
    
    def handle_login(self):
        """Handle user login."""
        login_id = self.login_input.text().strip()
        
        if not login_id:
            self.show_message("Error", "Please enter your Civil ID or Phone Number", QMessageBox.Warning)
            return
        
        # Try to find user by civil ID or phone
        user = User.get_by_civil_id(login_id) or User.get_by_phone(login_id)
        
        if not user:
            self.show_message("Login Failed", "User not found. Please check your credentials.", QMessageBox.Warning)
            return
        
        # Check if user has an active PC assignment
        assigned_pc = PC.get_by_user_id(user.id)

        if assigned_pc:
            # User has an existing active session with a PC
            # Check if user is trying to login from the correct PC
            default_pc = int(os.getenv('DEFAULT_PC_NUMBER', 1))
            if assigned_pc.pc_number != default_pc:
                self.show_message("Wrong PC", 
                    f"You are assigned to PC #{assigned_pc.pc_number} but trying to login from PC #{default_pc}. "
                    "Please use your assigned PC.", QMessageBox.Warning)
                return

            self.show_message("Login Successful", 
                           f"Welcome back, {user.name}! You are assigned to PC #{assigned_pc.pc_number}.",
                           QMessageBox.Information)
            
            # Set self.pc_number to the assigned PC number
            self.pc_number = assigned_pc.pc_number

            assigned_pc.update_status('occupied', True)

            try:
                # Get active session and calculate remaining time
                cursor = db.get_cursor()
                query = """
                SELECT * FROM sessions 
                WHERE user_id = %s AND pc_id = %s AND status = 'active'
                ORDER BY start_time DESC LIMIT 1
                """
                cursor.execute(query, (user.id, assigned_pc.id))
                session_data = cursor.fetchone()
                cursor.close()
                
                if session_data:
                    # Found an active session
                    self.current_user = user
                    self.current_session = session_data
                    
                    # Calculate remaining time
                    if 'end_time' in session_data and session_data['end_time']:
                        # Convert end_time to datetime if it's a string
                        if isinstance(session_data['end_time'], str):
                            end_time = datetime.strptime(session_data['end_time'], "%Y-%m-%d %H:%M:%S")
                        else:
                            end_time = session_data['end_time']
                        
                        # Calculate remaining seconds
                        now = datetime.now()
                        if end_time > now:
                            remaining_seconds = int((end_time - now).total_seconds())
                            self.remaining_time = remaining_seconds
                        else:
                            # Session expired but still active in database
                            self.remaining_time = 0
                    else:
                        # No end_time in session, fallback to duration_minutes
                        duration_minutes = session_data.get('duration_minutes', 60)
                        start_time = session_data.get('start_time', datetime.now())
                        
                        # Convert start_time to datetime if it's a string
                        if isinstance(start_time, str):
                            start_time = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
                            
                        # Calculate elapsed time
                        elapsed_seconds = int((datetime.now() - start_time).total_seconds())
                        total_seconds = duration_minutes * 60
                        self.remaining_time = max(0, total_seconds - elapsed_seconds)
                else:
                    # No active session found, create default one-hour timer
                    self.remaining_time = 3600  # Default to 1 hour

                

                # Update UI
                self.user_label.setText(f"Welcome, {user.name} - PC #{assigned_pc.pc_number}")
                self.update_timer()
                self.timer.start(1000)  # Update every second
                
                # Load games
                self.load_games()
                
                # Switch to main page
                self.stacked_widget.setCurrentWidget(self.main_page)

            except Exception as e:
                self.show_message("Error", f"No active session found. Please contact staff. {str(e)}", QMessageBox.Critical)
                import traceback
                traceback.print_exc()

        else:
            # If no PC is automatically assigned, use the pc_number provided to the launcher
            if not self.pc_number:
                self.show_message("Error", "No PC number assigned. Please contact staff.", QMessageBox.Warning)
                return
            
            if not pc:
                self.show_message("Error", f"PC #{self.pc_number} does not exist. Please contact staff.", QMessageBox.Warning)
                return
            
            if pc.is_occupied:
                self.show_message("Error", f"PC #{self.pc_number} is already occupied. Please contact staff.", QMessageBox.Warning)
                return
            
            self.show_message("Error", "No PC number assigned. Please contact staff.", QMessageBox.Warning)
            return
                
                

    def update_timer(self):
        """Update the session timer."""
        if self.remaining_time is None:
            return
        
        if self.remaining_time <= 0:
            self.end_session()
            return
        
        # Show warnings when time is running low
        if self.remaining_time == 300:  # 5 minutes warning
            self.timer_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #FFA500;")  # Orange
            self.show_message("Time Warning", "Your session will end in 5 minutes. Please save your progress.", QMessageBox.Warning)
        elif self.remaining_time == 60:  # 1 minute warning
            self.timer_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #FF0000;")  # Red
            self.show_message("Time Warning", "Your session will end in 1 minute! Please finish up now.", QMessageBox.Critical)
            
        hours = self.remaining_time // 3600
        minutes = (self.remaining_time % 3600) // 60
        seconds = self.remaining_time % 60
        
        self.timer_label.setText(f"Time Remaining: {hours:02d}:{minutes:02d}:{seconds:02d}")
        self.remaining_time -= 1
    
    def end_session(self):
        """End the current session and log out the user when time expires."""
        try:
            # Stop the orders refresh timer
            if self.orders_refresh_timer.isActive():
                self.orders_refresh_timer.stop()
            
            # Update session status in database
            if self.current_session:
                # Check if session has an ID field or is a dictionary
                if isinstance(self.current_session, dict) and 'id' in self.current_session:
                    session_id = self.current_session['id']
                    cursor = db.get_cursor()
                    cursor.execute(
                        "UPDATE sessions SET status = 'completed' WHERE id = %s",
                        (session_id,)
                    )
                    db.commit()
                    cursor.close()
                elif hasattr(self.current_session, 'id') and hasattr(self.current_session, 'update_status'):
                    # Use the method if available
                    self.current_session.update_status('completed')
            
            # Update PC status in database
            if self.pc_number:
                try:
                    cursor = db.get_cursor()
                    cursor.execute(
                        "UPDATE pcs SET is_occupied = FALSE, status = 'available' WHERE pc_number = %s",
                        (self.pc_number,)
                    )
                    db.commit()
                    cursor.close()
                except Exception as e:
                    print(f"Error updating PC status: {str(e)}")
            
            # Stop the timer
            if self.timer.isActive():
                self.timer.stop()
            
            # Clean up resources
            self.current_user = None
            self.current_session = None
            self.remaining_time = None
            
            # Show session ended message
            self.show_message(
                "Session Ended", 
                "Your session has ended. This PC will be locked in 5 seconds. Thank you for playing!",
                QMessageBox.Information
            )
            
            # Clear login input and refresh login page
            self.login_input.clear()
            self.login_input.setFocus()
            
            # Switch back to login page
            self.stacked_widget.setCurrentWidget(self.login_page)
            
            # Lock the PC after a short delay to allow the user to see the message
            QTimer.singleShot(5000, self.lock_workstation)
            
        except Exception as e:
            # Log the error but still try to logout
            print(f"Error during session end: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # Make sure we still switch to login screen even if there's an error
            self.stacked_widget.setCurrentWidget(self.login_page)
            
            # Still try to lock the PC
            QTimer.singleShot(5000, self.lock_workstation)
            
    def lock_workstation(self):
        """Lock the Windows workstation."""
        try:
            import ctypes
            ctypes.windll.user32.LockWorkStation()
        except Exception as e:
            print(f"Error locking workstation: {str(e)}")
            try:
                # Fallback method using os.system
                import os
                os.system('rundll32.exe user32.dll,LockWorkStation')
            except Exception as e2:
                print(f"Fallback locking method failed: {str(e2)}")

    def show_message(self, title, message, icon=QMessageBox.Information):
        """Show a styled message box."""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(icon)
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #1a1a2e;
                color: white;
            }
            QLabel {
                color: white;
                font-size: 14px;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0078d7, stop:1 #00c3ff);
                color: white;
                border: none;
                border-radius: 5px;
                min-width: 80px;
                min-height: 30px;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0086ef, stop:1 #19ceff);
            }
        """)
        return msg_box.exec_()

    def closeEvent(self, event):
        """Override close event to require password for exit."""
        # Check if exit is locked due to too many failed attempts
        if self.exit_password_locked_until:
            now = datetime.now()
            if now < self.exit_password_locked_until:
                time_remaining = (self.exit_password_locked_until - now).total_seconds()
                minutes = int(time_remaining // 60)
                seconds = int(time_remaining % 60)
                self.show_message(
                    "Exit Locked",
                    f"Too many failed attempts. Exit is locked for {minutes}:{seconds:02d}.",
                    QMessageBox.Warning
                )
                event.ignore()
                return
            else:
                # Reset if lock time has expired
                self.exit_password_locked_until = None
                self.exit_password_attempts = 0
        
        # Skip password check for development/debug
        if os.getenv('LAUNCHER_DEBUG') == '1':
            event.accept()
            return
            
        # Check if a password is set in settings
        stored_password = self.get_exit_password()
        if not stored_password:
            # No password set, allow exit
            event.accept()
            return
            
        # Show password dialog
        dialog = ExitPasswordDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            entered_password = dialog.get_password()
            
            # Check if password is correct
            if self.verify_exit_password(entered_password, stored_password):
                # Password correct, allow exit
                self.exit_password_attempts = 0
                event.accept()
            else:
                # Password incorrect
                self.exit_password_attempts += 1
                remaining_attempts = 3 - self.exit_password_attempts
                
                if remaining_attempts > 0:
                    # Still have attempts left
                    self.show_message(
                        "Incorrect Password",
                        f"The password is incorrect. {remaining_attempts} attempts remaining.",
                        QMessageBox.Warning
                    )
                    event.ignore()
                else:
                    # Lock the exit function for 5 minutes
                    self.exit_password_locked_until = datetime.now() + timedelta(minutes=5)
                    self.show_message(
                        "Exit Locked",
                        "Too many failed attempts. Exit is locked for 5 minutes.",
                        QMessageBox.Critical
                    )
                    self.exit_password_attempts = 0
                    event.ignore()
        else:
            # User canceled, don't exit
            event.ignore()
            
    def get_exit_password(self):
        """Get the exit password from settings table."""
        try:
            cursor = db.get_cursor()
            cursor.execute("SELECT value FROM settings WHERE category = 'security' AND name = 'launcher_exit_password'")
            result = cursor.fetchone()
            cursor.close()
            
            if result and 'value' in result:
                return result['value']
            return ""  # Return empty string if no password set
        except Exception as e:
            print(f"Error fetching exit password: {str(e)}")
            return ""  # Return empty string on error
            
    def verify_exit_password(self, entered_password, stored_password):
        """Verify if the entered password matches the stored password."""
        # First check if the stored password is hashed (starts with $)
        if stored_password.startswith('$'):
            # Hashed password, use verify_password helper
            try:
                return verify_password(stored_password, entered_password)
            except:
                # If verification fails, fall back to direct comparison
                return entered_password == stored_password
        else:
            # Plain text password (not recommended, but supported for backward compatibility)
            return entered_password == stored_password

    def attempt_close(self):
        """Attempt to close the application."""
        self.close()

    def load_games(self):
        """Load games from the database and display them in the grid."""
        try:
            cursor = db.get_cursor()
            
            # Check if is_available or is_active column exists
            cursor.execute("DESCRIBE games")
            columns = [column['Field'] for column in cursor.fetchall()]
            
            # Adapt query based on available columns
            if 'is_available' in columns:
                availability_column = 'is_available'
            elif 'is_active' in columns:
                availability_column = 'is_active'
            else:
                availability_column = None
            
            # Build the query based on schema
            if availability_column:
                query = f"SELECT * FROM games WHERE {availability_column} = TRUE ORDER BY name"
            else:
                query = "SELECT * FROM games ORDER BY name"
                
            cursor.execute(query)
            games = cursor.fetchall()
            cursor.close()
            
            # Clear existing games
            for i in reversed(range(self.games_layout.count())):
                widget = self.games_layout.itemAt(i).widget()
                if widget:
                    widget.setParent(None)
            
            if games:
                # Calculate grid dimensions
                cols = 4  # Number of columns in the grid
                for i, game in enumerate(games):
                    row = i // cols
                    col = i % cols
                    game_card = GameCard(game, self)
                    self.games_layout.addWidget(game_card, row, col)
            else:
                # No games found
                no_games_label = QLabel("No games available")
                no_games_label.setAlignment(Qt.AlignCenter)
                no_games_label.setStyleSheet("color: white; font-size: 16px;")
                self.games_layout.addWidget(no_games_label, 0, 0)
        except Exception as e:
            self.show_message("Error", f"Failed to load games: {str(e)}", QMessageBox.Critical)
            import traceback
            traceback.print_exc()

    def show_food_menu(self):
        """Show the food menu page and load menu items."""
        self.load_menu_items()
        # Load user orders
        self.load_user_orders()
        # Start orders refresh timer (refresh every 1 seconds)
        self.orders_refresh_timer.start(1000)
        self.stacked_widget.setCurrentWidget(self.food_menu_page)

    def show_main_page(self):
        """Return to the main games page."""
        # Stop orders refresh timer when leaving food menu
        # self.orders_refresh_timer.stop()
        self.stacked_widget.setCurrentWidget(self.main_page)

    def load_menu_items(self):
        """Load menu items from the database and display them."""
        try:
            # Clear existing items
            for i in reversed(range(self.menu_layout.count())): 
                self.menu_layout.itemAt(i).widget().setParent(None)
            
            # Get menu items from database
            cursor = db.get_cursor()
            
            # Check table structure for availability and image fields
            cursor.execute("DESCRIBE menu_items")
            columns = [column['Field'] for column in cursor.fetchall()]
            
            # Determine availability field
            availability_field = None
            if 'available' in columns:
                availability_field = 'available = TRUE'
            elif 'is_active' in columns:
                availability_field = 'is_active = TRUE'
            elif 'is_available' in columns:
                availability_field = 'is_available = TRUE'
            
            # Determine image field
            image_field = None
            if 'image_path' in columns:
                image_field = 'image_path'
            elif 'image' in columns:
                image_field = 'image'
            
            # Build query based on available fields
            query = "SELECT id, name, price, description, category"
            if image_field:
                query += f", {image_field}"
            
            query += " FROM menu_items"
            if availability_field:
                query += f" WHERE {availability_field}"
            query += " ORDER BY category, name"
            
            cursor.execute(query)
            menu_items = cursor.fetchall()
            cursor.close()
            
            if menu_items:
                # Group items by category
                categories = {}
                for item in menu_items:
                    category = item.get('category', 'other')
                    if category not in categories:
                        categories[category] = []
                    categories[category].append(item)
                
                # Add category headers and items
                row = 0
                cols = 3  # Number of columns in the grid
                
                for category, items in categories.items():
                    # Add category header
                    category_label = QLabel(category.upper())
                    category_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
                    category_label.setStyleSheet("color: #ff9800;")
                    self.menu_layout.addWidget(category_label, row, 0, 1, cols)
                    row += 1
                    
                    # Add items in this category
                    col = 0
                    for item in items:
                        # Create item card
                        card = QFrame()
                        card.setFixedSize(300, 400)  # Fixed size for consistency
                        card.setStyleSheet("""
                            QFrame {
                                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                    stop:0 rgba(30, 30, 50, 0.9),
                                    stop:1 rgba(20, 20, 35, 0.95));
                                border: 2px solid rgba(255, 152, 0, 0.3);
                                border-radius: 15px;
                                padding: 15px;
                            }
                            QFrame:hover {
                                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                    stop:0 rgba(40, 40, 60, 0.95),
                                    stop:1 rgba(30, 30, 45, 0.98));
                                border: 2px solid rgba(255, 152, 0, 0.8);
                                transform: translateY(-5px);
                            }
                        """)
                        
                        # Add shadow effect to the card
                        shadow = QGraphicsDropShadowEffect()
                        shadow.setBlurRadius(20)
                        shadow.setColor(QColor(255, 152, 0, 100))
                        shadow.setOffset(0, 5)
                        card.setGraphicsEffect(shadow)
                        
                        # Create layout for the card
                        card_layout = QVBoxLayout(card)
                        card_layout.setContentsMargins(15, 15, 15, 15)
                        card_layout.setSpacing(15)
                        
                        # Image container with rounded corners
                        if image_field and item.get(image_field):
                            image_container = QFrame()
                            image_container.setFixedHeight(200)
                            image_container.setStyleSheet("""
                                QFrame {
                                    background-color: rgba(40, 40, 60, 0.5);
                                    border-radius: 10px;
                                    border: 1px solid rgba(255, 152, 0, 0.3);
                                }
                            """)
                            image_layout = QVBoxLayout(image_container)
                            image_layout.setContentsMargins(5, 5, 5, 5)
                            
                            image_label = QLabel()
                            pixmap = QPixmap(item[image_field])
                            if not pixmap.isNull():
                                scaled_pixmap = pixmap.scaled(250, 180, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                                image_label.setPixmap(scaled_pixmap)
                                image_label.setAlignment(Qt.AlignCenter)
                                image_layout.addWidget(image_label)
                            
                            card_layout.addWidget(image_container)
                        
                        # Item name with modern styling
                        name_label = QLabel(item['name'])
                        name_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
                        name_label.setStyleSheet("""
                            color: #ff9800;
                            letter-spacing: 1px;
                            text-shadow: 0 0 10px rgba(255, 152, 0, 0.3);
                        """)
                        name_label.setAlignment(Qt.AlignCenter)
                        card_layout.addWidget(name_label)
                        
                        # Item description with modern styling
                        if item.get('description'):
                            desc_label = QLabel(item['description'])
                            desc_label.setWordWrap(True)
                            desc_label.setFont(QFont("Segoe UI", 11))
                            desc_label.setStyleSheet("""
                                color: #cccccc;
                                background-color: rgba(40, 40, 60, 0.3);
                                border-radius: 5px;
                                padding: 8px;
                            """)
                            desc_label.setAlignment(Qt.AlignCenter)
                            card_layout.addWidget(desc_label)
                        
                        # Price and order button container with modern styling
                        price_container = QWidget()
                        price_container.setStyleSheet("""
                            QWidget {
                                background-color: rgba(40, 40, 60, 0.5);
                                border-radius: 10px;
                                padding: 10px;
                            }
                        """)
                        price_layout = QHBoxLayout(price_container)
                        price_layout.setContentsMargins(10, 10, 10, 10)
                        price_layout.setSpacing(15)
                        
                        # Price with modern styling
                        price_label = QLabel(f"₹{float(item['price']):.2f}")
                        price_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
                        price_label.setStyleSheet("""
                            color: #00c853;
                            text-shadow: 0 0 10px rgba(0, 200, 83, 0.3);
                        """)
                        price_layout.addWidget(price_label)
                        
                        # Order button with modern styling
                        order_button = QPushButton("ORDER NOW")
                        order_button.setCursor(Qt.PointingHandCursor)
                        order_button.setFixedWidth(120)
                        order_button.setStyleSheet("""
                            QPushButton {
                                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                                    stop:0 #ff9800, stop:1 #ff5722);
                                color: white;
                                border: none;
                                border-radius: 8px;
                                padding: 10px 15px;
                                font-weight: bold;
                                font-size: 12px;
                                letter-spacing: 1px;
                            }
                            QPushButton:hover {
                                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                                    stop:0 #ffa726, stop:1 #ff7043);
                                transform: scale(1.05);
                            }
                            QPushButton:pressed {
                                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                                    stop:0 #f57c00, stop:1 #f4511e);
                                transform: scale(0.95);
                            }
                        """)
                        order_button.clicked.connect(lambda checked, item_id=item['id'], name=item['name'], price=item['price']: 
                            self.show_order_dialog(item_id, name, price))
                        price_layout.addWidget(order_button)
                        
                        card_layout.addWidget(price_container)
                        self.menu_layout.addWidget(card, row, col)
                        
                        col += 1
                        if col >= cols:
                            col = 0
                            row += 1
                    
                    # Add spacer after category
                    row += 1
            else:
                # No menu items found
                no_items_label = QLabel("No menu items available")
                no_items_label.setAlignment(Qt.AlignCenter)
                no_items_label.setStyleSheet("color: white; font-size: 16px;")
                self.menu_layout.addWidget(no_items_label, 0, 0)
                
        except Exception as e:
            self.show_message("Error", f"Failed to load menu items: {str(e)}", QMessageBox.Critical)
            import traceback
            traceback.print_exc()

    def load_user_orders(self):
        """Load the user's orders into the table."""
        if not self.current_user or not self.current_session:
            self.show_message("Error", "No user or session found. Please log in again.", QMessageBox.Critical)
            return

        self.orders_table.setRowCount(0)
        orders = Order.get_by_session(self.current_session['id'])

        for i, order in enumerate(orders):
            self.orders_table.insertRow(i)
            self.orders_table.setItem(i, 0, QTableWidgetItem(str(order.id)))
            items_text = ", ".join([f"{item['quantity']} x {item['name']}" for item in order.items])
            self.orders_table.setItem(i, 1, QTableWidgetItem(items_text))
            self.orders_table.setItem(i, 2, QTableWidgetItem(order.status.capitalize()))

            # Add cancel button for pending orders
            if order.status == 'pending':
                cancel_button = QPushButton("Cancel Order")
                cancel_button.clicked.connect(lambda _, order_id=order.id: self.cancel_order(order_id))
                cancel_button.setStyleSheet("""
                    QPushButton {
                        background-color: #ff4c4c;
                        color: white;
                        border: none;
                        border-radius: 5px;
                        padding: 5px 10px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #ff6666;
                    }
                    QPushButton:pressed {
                        background-color: #cc0000;
                    }
                """)
                self.orders_table.setCellWidget(i, 3, cancel_button)

    def cancel_order(self, order_id):
        """Cancel a pending order."""
        try:
            order = Order.get_by_id(order_id)
            if order and order.status == 'pending':
                order.update_status('cancelled')
                self.show_message("Success", "Order cancelled successfully.", QMessageBox.Information)
                self.load_user_orders()  # Refresh orders
            else:
                self.show_message("Error", "Order cannot be cancelled.", QMessageBox.Warning)
        except Exception as e:
            self.show_message("Error", f"Failed to cancel order: {str(e)}", QMessageBox.Critical)

    def show_order_dialog(self, item_id, name, price):
        """Show dialog to confirm order with quantity selection."""
        try:
            # Check for active user session
            if not self.current_user or not self.current_session:
                self.show_message("Error", "No active user session found.", QMessageBox.Warning)
                return
            
            dialog = QDialog(self)
            dialog.setWindowTitle("Place Order")
            dialog.setFixedWidth(400)
            dialog.setStyleSheet("""
                QDialog {
                    background-color: #1a1a2e;
                    color: white;
                    border: 1px solid rgba(255, 152, 0, 0.5);
                    border-radius: 10px;
                }
                QLabel {
                    color: white;
                    font-size: 14px;
                }
                QSpinBox {
                    background-color: rgba(40, 40, 60, 0.7);
                    border: 1px solid rgba(255, 152, 0, 0.5);
                    border-radius: 5px;
                    padding: 5px;
                    color: white;
                }
                QSpinBox::up-button, QSpinBox::down-button {
                    background-color: rgba(255, 152, 0, 0.5);
                    border-radius: 3px;
                }
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ff9800, stop:1 #ff5722);
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 8px 15px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ffa726, stop:1 #ff7043);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #f57c00, stop:1 #f4511e);
                }
            """)
            
            layout = QVBoxLayout(dialog)
            layout.setSpacing(15)
            
            # Item name
            name_label = QLabel(name)
            name_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
            name_label.setStyleSheet("color: #ff9800;")
            layout.addWidget(name_label)
            
            # Price
            price_label = QLabel(f"Price: ₹{float(price):.2f}")
            price_label.setFont(QFont("Segoe UI", 14))
            layout.addWidget(price_label)
            
            # Quantity selection
            quantity_layout = QHBoxLayout()
            quantity_label = QLabel("Quantity:")
            quantity_label.setFont(QFont("Segoe UI", 12))
            quantity_layout.addWidget(quantity_label)
            
            quantity_spin = QSpinBox()
            quantity_spin.setMinimum(1)
            quantity_spin.setMaximum(10)
            quantity_spin.setValue(1)
            quantity_spin.setFixedWidth(100)
            quantity_layout.addWidget(quantity_spin)
            
            layout.addLayout(quantity_layout)
            
            # Total amount
            total_label = QLabel(f"Total: ₹{float(price):.2f}")
            total_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
            total_label.setStyleSheet("color: #00c853;")
            layout.addWidget(total_label)
            
            # Update total when quantity changes
            def update_total():
                total = float(price) * quantity_spin.value()
                total_label.setText(f"Total: ₹{total:.2f}")
            
            quantity_spin.valueChanged.connect(update_total)
            
            # Buttons
            button_layout = QHBoxLayout()
            
            cancel_button = QPushButton("Cancel")
            cancel_button.clicked.connect(dialog.reject)
            button_layout.addWidget(cancel_button)
            
            confirm_button = QPushButton("Confirm Order")
            confirm_button.clicked.connect(dialog.accept)
            button_layout.addWidget(confirm_button)
            
            layout.addLayout(button_layout)
            
            if dialog.exec_() == QDialog.Accepted:
                quantity = quantity_spin.value()
                total_amount = float(price) * quantity
                
                # Create order in database
                cursor = db.get_cursor()
                try:
                    # Create the order
                    cursor.execute("""
                        INSERT INTO orders (session_id, status, total_amount)
                        VALUES (%s, %s, %s)
                    """, (
                        self.current_session['id'],
                        'pending',
                        total_amount
                    ))
                    
                    order_id = cursor.lastrowid
                    
                    # Add order item
                    cursor.execute("""
                        INSERT INTO order_items (order_id, menu_item_id, quantity, price)
                        VALUES (%s, %s, %s, %s)
                    """, (
                        order_id,
                        item_id,
                        quantity,
                        price
                    ))
                    
                    db.commit()
                    
                    # Show success message
                    self.show_message(
                        "Order Placed",
                        f"Your order for {quantity} x {name} has been placed!\n\n"
                        f"Total: ₹{total_amount:.2f}\n"
                        "Your order status is now 'pending'. Staff will deliver your order shortly.",
                        QMessageBox.Information
                    )
                    
                    # Refresh orders table
                    self.load_user_orders()
                    
                except Exception as e:
                    db.rollback()
                    self.show_message("Error", f"Failed to place order: {str(e)}", QMessageBox.Critical)
                    import traceback
                    traceback.print_exc()
                finally:
                    cursor.close()
                    
        except Exception as e:
            self.show_message("Error", f"Failed to show order dialog: {str(e)}", QMessageBox.Critical)
            import traceback
            traceback.print_exc()


class LauncherApp:
    def __init__(self, pc_number=None):
        self.app = QApplication(sys.argv)
        self.window = LauncherMainWindow(pc_number)
    
    def run(self):
        self.window.showFullScreen()
        return self.app.exec_() 