import os
import bcrypt
from datetime import datetime, timedelta

# Import PyQt5 modules for the background image functionality
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPalette, QBrush, QPixmap
from PyQt5.QtCore import Qt

def hash_password(password):
    """Hash a password for storing."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def check_password(stored_password, provided_password):
    """Check a stored password against a provided password."""
    return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password.encode('utf-8'))

# Alias for check_password for semantic compatibility
verify_password = check_password

def format_currency(amount):
    """Format a currency amount."""
    return f"${amount:.2f}"

def format_time(minutes):
    """Format minutes into hours and minutes."""
    hours = minutes // 60
    mins = minutes % 60
    if hours > 0:
        return f"{hours}h {mins}m"
    return f"{mins}m"

def format_datetime(dt):
    """Format a datetime object."""
    if not dt:
        return ""
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def calculate_time_left(end_time):
    """Calculate time left in minutes."""
    if not end_time:
        return 0
    
    now = datetime.now()
    if now > end_time:
        return 0
    
    delta = end_time - now
    return int(delta.total_seconds() // 60)

def format_time_left(end_time):
    """Format time left as a string."""
    minutes_left = calculate_time_left(end_time)
    return format_time(minutes_left)

def format_time_remaining(time_delta):
    """
    Format a timedelta object into a human-readable string showing hours, minutes, and seconds.
    
    Args:
        time_delta (timedelta): The time remaining as a timedelta object
        
    Returns:
        str: A formatted string representation of the time remaining (e.g., "2h 30m 15s")
    """
    # Extract total seconds
    total_seconds = int(time_delta.total_seconds())
    
    # Break down into hours, minutes, seconds
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    
    # Format the string based on remaining time
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes:02d}:{seconds:02d}"

def get_duration_options():
    """Get standard duration options."""
    return [
        {"label": "1 Hour", "value": 60, "price": 5.00},
        {"label": "2 Hours", "value": 120, "price": 9.00},
        {"label": "3 Hours", "value": 180, "price": 12.00},
        {"label": "5 Hours", "value": 300, "price": 18.00}
    ]

def get_payment_methods():
    """Get available payment methods."""
    return ["Cash", "Apple Pay", "KNET"]

def calculate_price_for_duration(minutes):
    """Calculate price for a given duration."""
    options = get_duration_options()
    for option in options:
        if option["value"] == minutes:
            return option["price"]
    
    # If not a standard option, calculate based on hourly rate
    return round((minutes / 60) * 5.00, 2)

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller."""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

def set_background_image(widget):
    """
    Set the background image for a widget using bg.jpg from assets folder.
    
    Args:
        widget (QWidget): The widget to set the background for
    """
    try:
        # Get the absolute path to the background image
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
        bg_path = os.path.join(root_dir, 'src', 'assets', 'bg.jpg')
        
        # Create a pixmap from the background image file
        bg_pixmap = QPixmap(bg_path)
        
        # Set the background image using QPalette
        palette = QPalette()
        palette.setBrush(QPalette.Background, QBrush(bg_pixmap.scaled(
            widget.size(),
            Qt.KeepAspectRatioByExpanding,
            Qt.SmoothTransformation
        )))
        widget.setAutoFillBackground(True)
        widget.setPalette(palette)
        
        # Add resize event handler to ensure background stays properly scaled
        def resize_event_handler(event):
            new_pixmap = bg_pixmap.scaled(
                widget.size(),
                Qt.KeepAspectRatioByExpanding,
                Qt.SmoothTransformation
            )
            new_palette = widget.palette()
            new_palette.setBrush(QPalette.Background, QBrush(new_pixmap))
            widget.setPalette(new_palette)
            
            # Call original resize event if it exists
            if hasattr(widget, 'original_resize_event'):
                widget.original_resize_event(event)
        
        # Store original resize event if it exists
        if hasattr(widget, 'resizeEvent'):
            widget.original_resize_event = widget.resizeEvent
        
        # Set our custom resize event
        widget.resizeEvent = resize_event_handler
        
        # Print a debug message
        print(f"Background image set from: {bg_path}")
        
        return True
    except Exception as e:
        print(f"Error setting background image: {e}")
        return False

def make_fullscreen(window):
    """
    Make a window display in full screen mode.
    Can be used with QMainWindow, QDialog, or any QWidget-based window.
    
    Args:
        window: The window to set to full screen
    """
    # You can use this for QMainWindow, QDialog, or any QWidget
    window.showFullScreen()
    
    # For smaller dialogs that shouldn't be fullscreen but should be centered
    # window.setWindowState(window.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
    # center_point = QGuiApplication.primaryScreen().geometry().center()
    # window_rect = window.frameGeometry()
    # window_rect.moveCenter(center_point)
    # window.move(window_rect.topLeft())
    
    return window 