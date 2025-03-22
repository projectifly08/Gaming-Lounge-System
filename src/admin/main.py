import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTabWidget, 
    QVBoxLayout, QHBoxLayout, QStackedWidget, QLabel,
    QGraphicsDropShadowEffect, QFrame, QToolButton
)
from PyQt5.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, QTimer
from PyQt5.QtGui import (
    QIcon, QPixmap, QColor, QFont, QPalette, QBrush, 
    QLinearGradient, QTransform, QPainter, QPainterPath, QPen
)

# Import admin panel tabs
from .dashboard import DashboardTab
from .registration import RegistrationTab
from .sessions import SessionsTab
from .orders import OrdersTab
from .menu import MenuTab
from .reports import ReportsTab
from .settings import SettingsTab
from .games import GamesTab
from .login import AdminLoginWindow
from src.utils.helpers import set_background_image
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

class AdminApp:
    """Main admin application class."""
    
    def __init__(self):
        """Initialize the admin application."""
        self.app = QApplication(sys.argv)
        
        # Set the application style
        self.apply_gaming_theme()
        
        self.login_window = AdminLoginWindow(on_login_success=self.show_admin_panel)
        self.admin_window = None
    
    def run(self):
        """Run the admin application."""
        self.login_window.show()
        sys.exit(self.app.exec_())
    
    def show_admin_panel(self):
        """Show the main admin panel after successful login."""
        self.admin_window = AdminMainWindow()
        self.admin_window.showFullScreen()
    
    def apply_gaming_theme(self):
        """Apply a gaming theme to the entire application."""
        # Set fusion style for a modern look
        self.app.setStyle("Fusion")
        
        # Create a dark palette with gaming accents
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(18, 18, 30))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(25, 25, 40))
        palette.setColor(QPalette.AlternateBase, QColor(35, 35, 50))
        palette.setColor(QPalette.ToolTipBase, QColor(35, 35, 50))
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor(35, 35, 50))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.BrightText, Qt.white)
        palette.setColor(QPalette.Highlight, QColor(0, 165, 235))
        palette.setColor(QPalette.HighlightedText, Qt.white)
        palette.setColor(QPalette.Link, QColor(0, 195, 255))
        
        self.app.setPalette(palette)
        
        # Set global application stylesheet
        self.app.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI', 'Arial';
                color: white;
            }
            
            QToolTip {
                background-color: #1e1e35;
                color: #00c3ff;
                border: 1px solid #00a5eb;
                padding: 5px;
            }
            
            QScrollBar:vertical {
                border: none;
                background: rgba(35, 35, 50, 0.5);
                width: 10px;
                margin: 0px;
            }
            
            QScrollBar::handle:vertical {
                background: rgba(0, 165, 235, 0.7);
                min-height: 20px;
                border-radius: 5px;
            }
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
                height: 0px;
            }
            
            QScrollBar:horizontal {
                border: none;
                background: rgba(35, 35, 50, 0.5);
                height: 10px;
                margin: 0px;
            }
            
            QScrollBar::handle:horizontal {
                background: rgba(0, 165, 235, 0.7);
                min-width: 20px;
                border-radius: 5px;
            }
            
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                border: none;
                background: none;
                width: 0px;
            }
            
            QMainWindow {
                background-color: #12121e;
            }
            
            QMessageBox {
                background-color: #1a1a2e;
            }
        """)

class AdminMainWindow(QMainWindow):
    """Main window for the admin panel."""
    
    def __init__(self):
        """Initialize the main window."""
        super().__init__()
        
        self.setWindowTitle("The Gaming Lounge")
        self.setMinimumSize(1200, 800)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Set background image to the central widget
        set_background_image(central_widget)
        
        # Initialize all tabs
        self.setup_tabs()
        
        # Set main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create header with gaming style
        header_container = QFrame()
        header_container.setMaximumHeight(80)
        header_container.setStyleSheet("""
            background-color: rgba(18, 18, 30, 0.6);
            border-bottom: 1px solid rgba(0, 195, 255, 0.5);
            border-radius: 0px;
        """)
        
        # Add shadow to header
        header_shadow = QGraphicsDropShadowEffect()
        header_shadow.setBlurRadius(15)
        header_shadow.setColor(QColor(0, 195, 255, 100))
        header_shadow.setOffset(0, 2)
        header_container.setGraphicsEffect(header_shadow)
        
        header_layout = QHBoxLayout(header_container)
        header_layout.setContentsMargins(20, 0, 20, 0)
        
        # Create logo and title container
        logo_container = QWidget()
        logo_container_layout = QHBoxLayout(logo_container)
        logo_container_layout.setContentsMargins(0, 0, 0, 0)
        logo_container_layout.setSpacing(0)
        
        # Add logo image
        logo_label = QLabel()
        logo_label.setFixedSize(70, 70)
        logo_pixmap = QPixmap("src/assets/logo1.jpg")
        scaled_pixmap = logo_pixmap.scaled(70, 70, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo_label.setPixmap(scaled_pixmap)
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setStyleSheet("""
            background-color: transparent;
        """)
        logo_container_layout.addWidget(logo_label)
        
        # Add title with gaming style
        title_label = QLabel("THE GAMING LOUNGE")
        title_label.setFont(QFont("Segoe UI", 24, QFont.Bold))
        title_label.setStyleSheet("""
            color: #00c3ff;
            letter-spacing: 3px;
        """)
        
        # Add glow effect to the title
        title_glow = QGraphicsDropShadowEffect()
        title_glow.setBlurRadius(15)
        title_glow.setColor(QColor(0, 195, 255, 160))
        title_glow.setOffset(0, 0)
        title_label.setGraphicsEffect(title_glow)
        
        logo_container_layout.addWidget(title_label)
        logo_container_layout.addStretch()
        
        header_layout.addWidget(logo_container)
        header_layout.addStretch()
        
        
        # Add refresh button
        self.refresh_button = QToolButton()
        self.refresh_button.setToolTip("Sync All Data")
        self.refresh_button.setCursor(Qt.PointingHandCursor)
        self.refresh_button.setFixedSize(36, 36)
        self.refresh_button.setStyleSheet("""
            QToolButton {
                background-color: rgba(0, 195, 255, 0.2);
                border: 1px solid rgba(0, 195, 255, 0.5);
                border-radius: 18px;
                color: #00c3ff;
                font-size: 18px;
                font-weight: bold;
            }
            QToolButton:hover {
                background-color: rgba(0, 195, 255, 0.4);
            }
            QToolButton:pressed {
                background-color: rgba(0, 195, 255, 0.6);
            }
        """)
        
        # Load a new refresh icon image
        new_icon_path = "src/assets/refresh-icon.png"  # Update with the actual path to the new icon
        self.refresh_pixmap = QPixmap(new_icon_path)

        # Set the new icon on the refresh button
        self.refresh_button.setIcon(QIcon(self.refresh_pixmap))
        self.refresh_button.setIconSize(QSize(24, 24))
        
        # Connect refresh button
        self.refresh_button.clicked.connect(self.refresh_data)
        
        header_layout.addWidget(self.refresh_button)
        header_layout.addSpacing(50)
        
        # Add header to main layout
        main_layout.addWidget(header_container)
        
        # Add tab widget to main layout
        main_layout.addWidget(self.tabs)
        
        # Set up refresh timer for real-time updates
        self.setup_refresh_timer()
    
    def setup_tabs(self):
        """Set up the tab widget and all tabs."""
        # Create tab widget
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabPosition(QTabWidget.North)
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background-color: transparent;
            }
            
            QTabBar::tab {
                background-color: rgba(35, 35, 50, 0.7);
                color: #8a8aff;
                padding: 12px 20px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
                margin-right: 2px;
                font-size: 13px;
                font-weight: bold;
                letter-spacing: 1px;
                min-width: 130px;
            }
            
            QTabBar::tab:selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #0078d7, stop:1 rgba(0, 195, 255, 0.7));
                color: white;
            }
            
            QTabBar::tab:hover:!selected {
                background-color: rgba(45, 45, 65, 0.9);
                color: #00c3ff;
            }
        """)
        
        # Create tabs with gaming style
        self.dashboard_tab = DashboardTab()
        self.registration_tab = RegistrationTab()
        self.sessions_tab = SessionsTab()
        self.games_tab = GamesTab()
        self.orders_tab = OrdersTab()
        self.menu_tab = MenuTab()
        self.reports_tab = ReportsTab()
        self.settings_tab = SettingsTab()
        
        # Add tabs to tab widget
        self.tabs.addTab(self.dashboard_tab, "Dashboard")
        self.tabs.addTab(self.registration_tab, "Registration")
        self.tabs.addTab(self.sessions_tab, "Sessions")
        self.tabs.addTab(self.games_tab, "Games")
        self.tabs.addTab(self.orders_tab, "Orders")
        self.tabs.addTab(self.menu_tab, "Menu")
        self.tabs.addTab(self.reports_tab, "Reports")
        self.tabs.addTab(self.settings_tab, "Settings")
        
        # Save reference to the tab widget for other methods
        self.tab_widget = self.tabs
    
    def setup_refresh_timer(self):
        """Set up a timer to refresh data periodically."""
        from PyQt5.QtCore import QTimer
        
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_data)
        self.refresh_timer.start(30000)  # Refresh every 30 seconds
    
    def refresh_data(self):
        """Refresh data in all tabs."""
        current_index = self.tab_widget.currentIndex()
        
        # Refresh the current tab
        if current_index == 0:  # Dashboard
            self.dashboard_tab.refresh_data()
        elif current_index == 1:  # Registration
            self.registration_tab.refresh_data()
        elif current_index == 2:  # Sessions
            self.sessions_tab.refresh_data()
        elif current_index == 3:  # Orders
            self.orders_tab.refresh_data()
        elif current_index == 4:  # Menu
            self.menu_tab.refresh_data()
        elif current_index == 5:  # Games
            self.games_tab.refresh_data()
        elif current_index == 6:  # Reports
            self.reports_tab.refresh_data()
        
        # Always refresh dashboard data for real-time stats
        if current_index != 0:
            self.dashboard_tab.refresh_data()
            
    def showEvent(self, event):
        """Override show event to make window fullscreen and add close button."""
        super().showEvent(event)
        self.showFullScreen()
        
        # Add close button to the top-right corner
        if not hasattr(self, 'close_button'):
            self.close_button = add_close_button(self)

if __name__ == "__main__":
    app = AdminApp()
    app.run() 