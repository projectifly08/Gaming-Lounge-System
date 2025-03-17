import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QFrame, QMessageBox,
    QGridLayout, QApplication, QMainWindow, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, QSettings, QPropertyAnimation, QRect, QEasingCurve, QSize
from PyQt5.QtGui import QFont, QIcon, QPixmap, QColor, QLinearGradient, QPalette, QBrush, QPainter, QPainterPath

from src.utils.helpers import set_background_image, check_password, hash_password
from src.database import db
from src.common import add_close_button


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


class AdminLoginWindow(QMainWindow):
    """Admin login window that appears before the admin panel."""
    
    def __init__(self, on_login_success=None):
        """Initialize the admin login window."""
        super().__init__()
        
        self.on_login_success = on_login_success
        self.settings = QSettings("GamingLounge", "AdminPanel")
        
        # Initialize database if first run
        self.init_admin_account()
        
        self.setWindowTitle("Admin Login - Gaming Lounge")
        self.setMinimumSize(500, 600)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Set background image to the central widget
        set_background_image(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(50, 50, 50, 50)
        main_layout.setSpacing(20)
        
        # Create login form container with gaming theme
        login_container = QFrame()
        login_container.setObjectName("loginContainer")
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
        
        # Add title
        header_label = QLabel("THE GAMING LOUNGE")
        header_label.setFont(QFont("Segoe UI", 28, QFont.Bold))
        header_label.setStyleSheet("""
            color: #00c3ff;
            letter-spacing: 3px;
        """)
        header_label.setAlignment(Qt.AlignCenter)
        
        # Add glow effect to the header
        header_glow = QGraphicsDropShadowEffect()
        header_glow.setBlurRadius(15)
        header_glow.setColor(QColor(0, 195, 255, 160))
        header_glow.setOffset(0, 0)
        header_label.setGraphicsEffect(header_glow)
        
        logo_layout.addWidget(header_label)
        
        login_layout.addLayout(logo_layout)
        
        # Subtitle with gaming style
        subtitle = QLabel("ACCESS AUTHENTICATION REQUIRED")
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
        
        # Username field with gaming style
        username_layout = QVBoxLayout()
        username_label = QLabel("USERNAME")
        username_label.setFont(QFont("Segoe UI", 10))
        username_label.setStyleSheet("color: #00c3ff; letter-spacing: 1px;")
        username_layout.addWidget(username_label)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter admin username")
        self.username_input.setMinimumHeight(45)
        self.username_input.setStyleSheet("""
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
        username_layout.addWidget(self.username_input)
        login_layout.addLayout(username_layout)
        
        # Password field with gaming style
        password_layout = QVBoxLayout()
        password_label = QLabel("PASSWORD")
        password_label.setFont(QFont("Segoe UI", 10))
        password_label.setStyleSheet("color: #00c3ff; letter-spacing: 1px;")
        password_layout.addWidget(password_label)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter admin password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(45)
        self.password_input.setStyleSheet("""
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
        password_layout.addWidget(self.password_input)
        login_layout.addLayout(password_layout)
        
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
        login_button.clicked.connect(self.login)
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
        exit_button.clicked.connect(self.close)
        login_layout.addWidget(exit_button)
        
        # # Add decorative elements
        # decoration = QLabel("// SYSTEM ACCESS v2.4.3 //")
        # decoration.setAlignment(Qt.AlignCenter)
        # decoration.setStyleSheet("color: rgba(138, 138, 255, 0.5); font-family: 'Consolas'; letter-spacing: 1px;")
        # login_layout.addSpacing(10)
        # login_layout.addWidget(decoration)
        
        # Add login container to main layout
        main_layout.addStretch()
        main_layout.addWidget(login_container)
        main_layout.addStretch()
        
        # Set focus to username input
        self.username_input.setFocus()
        
        # Connect enter key to login
        self.username_input.returnPressed.connect(self.password_input.setFocus)
        self.password_input.returnPressed.connect(login_button.click)
    
    def init_admin_account(self):
        """Initialize admin account if it doesn't exist."""
        try:
            cursor = db.get_cursor()
            
            # Check if admin user exists
            cursor.execute("SELECT id FROM users WHERE username = 'admin' AND is_admin = 1")
            admin = cursor.fetchone()
            
            if not admin:
                # Create admin user with default password
                default_password = "admin123"
                hashed_password = hash_password(default_password)
                
                cursor.execute(
                    "INSERT INTO users (username, password_hash, name, email, is_admin) "
                    "VALUES (%s, %s, %s, %s, %s)",
                    ("admin", hashed_password, "Administrator", "admin@gaminglounge.com", 1)
                )
                db.commit()
                
                # Store admin username in settings
                self.settings.setValue("admin_username", "admin")
            
            cursor.close()
        except Exception as e:
            print(f"Error initializing admin account: {e}")
    
    def login(self):
        """Handle login button click."""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        if not username or not password:
            self.show_error_message("Please enter both username and password.")
            return
        
        try:
            cursor = db.get_cursor()
            
            # Check admin credentials
            cursor.execute(
                "SELECT id, password_hash FROM users WHERE username = %s AND is_admin = 1",
                (username,)
            )
            admin = cursor.fetchone()
            cursor.close()
            
            if admin and check_password(admin['password_hash'], password):
                # Login successful - add animation
                self.login_success_animation()
            else:
                # Login failed
                self.show_error_message("Invalid username or password.")
                self.password_input.setText("")
                self.password_input.setFocus()
        except Exception as e:
            self.show_error_message(f"Login error: {str(e)}")
    
    def login_success_animation(self):
        """Show a quick animation before proceeding to the main panel."""
        # Create a success overlay
        self.success_overlay = QFrame(self.centralWidget())
        self.success_overlay.setStyleSheet("background-color: rgba(0, 0, 0, 0.7);")
        self.success_overlay.setGeometry(0, 0, self.width(), self.height())
        
        # Create a success message
        success_layout = QVBoxLayout(self.success_overlay)
        success_msg = QLabel("ACCESS GRANTED")
        success_msg.setAlignment(Qt.AlignCenter)
        success_msg.setStyleSheet("color: #00ff00; font-size: 24px; font-weight: bold; letter-spacing: 2px;")
        success_layout.addWidget(success_msg)
        
        self.success_overlay.show()
        
        # Use a timer to delay the transition
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(1000, self.proceed_to_admin_panel)
    
    def proceed_to_admin_panel(self):
        """Proceed to the admin panel after animation."""
        if self.on_login_success:
            self.on_login_success()
        self.close()
    
    def show_error_message(self, message):
        """Show a styled error message."""
        error_dialog = QMessageBox(self)
        error_dialog.setWindowTitle("Authentication Error")
        error_dialog.setText(message)
        error_dialog.setIcon(QMessageBox.Warning)
        error_dialog.setStyleSheet("""
            QMessageBox {
                background-color: #1a1a2e;
                color: white;
            }
            QLabel {
                color: white;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0078d7, stop:1 #00c3ff);
                color: white;
                border: none;
                border-radius: 5px;
                min-width: 80px;
                min-height: 30px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0086ef, stop:1 #19ceff);
            }
        """)
        error_dialog.exec_()
            
    def showEvent(self, event):
        """Override show event to make window fullscreen and add close button."""
        super().showEvent(event)
        self.showFullScreen()
        
        # Add close button to the top-right corner
        if not hasattr(self, 'close_button'):
            self.close_button = add_close_button(self) 