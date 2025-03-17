from PyQt5.QtWidgets import (
    QWidget, QPushButton, QLabel, QLineEdit, QComboBox, 
    QVBoxLayout, QHBoxLayout, QGridLayout, QFrame, QMessageBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QSpacerItem,
    QSizePolicy, QScrollArea, QDialog, QApplication
)
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QTimer, QDateTime
from PyQt5.QtGui import QFont, QIcon, QPixmap, QColor, QPalette

class PrimaryButton(QPushButton):
    """A styled primary button with gaming theme."""
    
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0078d7, stop:1 #00c3ff);
                color: white;
                border: none;
                border-radius: 4px;
                padding: 3px 3px;
                font-size: 14px;
                letter-spacing: 0px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0086ef, stop:1 #19ceff);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #006acf, stop:1 #00b2e8);
            }
            QPushButton:disabled {
                background-color: rgba(25, 25, 40, 0.5);
                color: rgba(255, 255, 255, 0.5);
            }
        """)
        self.setCursor(Qt.PointingHandCursor)

class SecondaryButton(QPushButton):
    """A styled secondary button with gaming theme."""
    
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QPushButton {
                background-color: rgba(40, 40, 60, 0.7);
                color: #8a8aff;
                border: 1px solid rgba(138, 138, 255, 0.3);
                border-radius: 4px;
                padding: 3px 3px;
                font-size: 14px;
                letter-spacing: 0px;
            }
            QPushButton:hover {
                background-color: rgba(50, 50, 70, 0.9);
                border: 1px solid rgba(138, 138, 255, 0.5);
            }
            QPushButton:pressed {
                background-color: rgba(30, 30, 50, 0.9);
            }
            QPushButton:disabled {
                background-color: rgba(30, 30, 40, 0.4);
                color: rgba(138, 138, 255, 0.3);
                border: 1px solid rgba(138, 138, 255, 0.1);
            }
        """)
        self.setCursor(Qt.PointingHandCursor)

class DangerButton(QPushButton):
    """A styled danger button with gaming theme."""
    
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QPushButton {
                background-color: rgba(231, 76, 60, 0.8);
                color: white;
                border: none;
                border-radius: 4px;
                padding: 3px 3px;
                font-size: 14px;
                letter-spacing: 0px;
            }
            QPushButton:hover {
                background-color: rgba(231, 76, 60, 1.0);
            }
            QPushButton:pressed {
                background-color: rgba(192, 57, 43, 1.0);
            }
            QPushButton:disabled {
                background-color: rgba(231, 76, 60, 0.4);
                color: rgba(255, 255, 255, 0.5);
            }
        """)
        self.setCursor(Qt.PointingHandCursor)

class SuccessButton(QPushButton):
    """A styled success button with gaming theme."""
    
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QPushButton {
                background-color: rgba(46, 204, 113, 0.8);
                color: white;
                border: none;
                border-radius: 4px;
                padding: 3px 3px;
                font-size: 14px;
                letter-spacing: 0px;
            }
            QPushButton:hover {
                background-color: rgba(46, 204, 113, 1.0);
            }
            QPushButton:pressed {
                background-color: rgba(39, 174, 96, 1.0);
            }
            QPushButton:disabled {
                background-color: rgba(46, 204, 113, 0.4);
                color: rgba(255, 255, 255, 0.5);
            }
        """)
        self.setCursor(Qt.PointingHandCursor)

class StyledLineEdit(QLineEdit):
    """A styled line edit with gaming theme."""
    
    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setStyleSheet("""
            QLineEdit {
                border: 1px solid rgba(0, 195, 255, 0.5);
                border-radius: 4px;
                padding: 10px;
                background-color: rgba(25, 25, 40, 0.7);
                color: white;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #00c3ff;
                background-color: rgba(30, 30, 50, 0.9);
            }
            QLineEdit:disabled {
                background-color: rgba(20, 20, 30, 0.5);
                color: rgba(255, 255, 255, 0.5);
            }
        """)

class StyledComboBox(QComboBox):
    """A styled combo box with gaming theme."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QComboBox {
                border: 1px solid rgba(0, 195, 255, 0.5);
                border-radius: 4px;
                padding: 10px;
                background-color: rgba(25, 25, 40, 0.7);
                color: white;
                font-size: 14px;
                min-width: 200px;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 30px;
                border-left: 1px solid rgba(0, 195, 255, 0.3);
            }
            QComboBox:disabled {
                background-color: rgba(20, 20, 30, 0.5);
                color: rgba(255, 255, 255, 0.5);
            }
            QComboBox QAbstractItemView {
                background-color: rgba(25, 25, 40, 0.95);
                color: white;
                selection-background-color: rgba(0, 137, 221, 0.5);
                selection-color: white;
                border: 1px solid rgba(0, 195, 255, 0.5);
            }
        """)

class StyledLabel(QLabel):
    """A styled label with gaming theme."""
    
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: white;
            }
        """)

class HeaderLabel(QLabel):
    """A styled header label with gaming theme."""
    
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #00c3ff;
                margin-bottom: 10px;
                letter-spacing: 1px;
            }
        """)

class SubHeaderLabel(QLabel):
    """A styled subheader label with gaming theme."""
    
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #8a8aff;
                margin-bottom: 5px;
                letter-spacing: 0.5px;
            }
        """)

class Card(QFrame):
    """A styled card widget with gaming theme."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                background-color: rgba(25, 25, 40, 0.8);
                border-radius: 8px;
                border: 1px solid rgba(0, 195, 255, 0.3);
                padding: 15px;
            }
            QLabel {
                color: white;
            }
        """)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(15, 15, 15, 15)
        self.setLayout(self.layout)

class StyledTable(QTableWidget):
    """A styled table widget with gaming theme."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QTableWidget {
                border: 1px solid rgba(0, 195, 255, 0.3);
                border-radius: 4px;
                background-color: rgba(18, 18, 30, 0.7);
                gridline-color: rgba(0, 195, 255, 0.2);
                selection-background-color: rgba(0, 137, 221, 0.5);
                selection-color: white;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid rgba(0, 195, 255, 0.1);
                color: white;
            }
            QHeaderView::section {
                background-color: rgba(35, 35, 50, 0.9);
                padding: 10px;
                border: none;
                border-bottom: 1px solid rgba(0, 195, 255, 0.3);
                font-weight: bold;
                color: #00c3ff;
            }
        """)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.verticalHeader().setVisible(False)
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.setEditTriggers(QTableWidget.NoEditTriggers)
        self.setAlternatingRowColors(True)

class ConfirmDialog(QDialog):
    """A confirmation dialog with gaming theme."""
    
    def __init__(self, title, message, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(400)
        
        # Set dialog style
        self.setStyleSheet("""
            QDialog {
                background-color: rgba(18, 18, 30, 0.95);
                border: 1px solid rgba(0, 195, 255, 0.5);
                border-radius: 8px;
            }
            QLabel {
                color: white;
                font-size: 14px;
            }
        """)
        
        layout = QVBoxLayout()
        
        # Message
        label = QLabel(message)
        label.setWordWrap(True)
        layout.addWidget(label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        cancel_button = SecondaryButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        
        confirm_button = PrimaryButton("Confirm")
        confirm_button.clicked.connect(self.accept)
        
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(confirm_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)

def show_message(parent, title, message, icon=QMessageBox.Information):
    """Show a message box."""
    msg_box = QMessageBox(parent)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    msg_box.setIcon(icon)
    msg_box.setStandardButtons(QMessageBox.Ok)
    return msg_box.exec_()

def confirm_action(title, message, parent=None):
    """Show a confirmation dialog and return True if confirmed."""
    dialog = ConfirmDialog(title, message, parent)
    
    # Note: For dialogs like this, we do NOT want fullscreen, just comment for reference
    # Moved inside function to avoid circular import
    # from src.utils.helpers import make_fullscreen
    # make_fullscreen(dialog)  # Uncomment if fullscreen dialogs are desired
    
    return dialog.exec_() == QDialog.Accepted

def create_spacer():
    """Create a vertical spacer."""
    return QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

class CountdownTimer(QLabel):
    """A countdown timer label with gaming theme."""
    
    timeout = pyqtSignal()
    
    def __init__(self, end_time, parent=None):
        super().__init__(parent)
        self.end_time = end_time
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)  # Update every second
        self.update_time()
        
        self.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #00c3ff;
                font-family: 'Consolas', monospace;
            }
        """)
    
    def update_time(self):
        """Update the displayed time."""
        now = QDateTime.currentDateTime()
        end = QDateTime.fromString(self.end_time, Qt.ISODate)
        
        if now >= end:
            self.setText("Time's up!")
            self.timer.stop()
            self.timeout.emit()
            return
        
        secs_left = now.secsTo(end)
        hours = secs_left // 3600
        minutes = (secs_left % 3600) // 60
        seconds = secs_left % 60
        
        self.setText(f"{hours:02d}:{minutes:02d}:{seconds:02d}")

class PCStatusWidget(QWidget):
    """A widget to display PC status."""
    
    clicked = pyqtSignal(int)
    
    def __init__(self, pc_number, status="available", parent=None):
        super().__init__(parent)
        self.pc_number = pc_number
        self.status = status
        
        # Default size, can be overridden
        self.setFixedSize(100, 100)
        self.setCursor(Qt.PointingHandCursor)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)  # Smaller margins
        layout.setSpacing(0)
        
        # Create a centered PC number label
        self.pc_label = QLabel(f"PC {pc_number}")
        self.pc_label.setAlignment(Qt.AlignCenter)
        self.pc_label.setStyleSheet("""
            font-weight: bold; 
            font-size: 18px;  /* Slightly smaller font */
            color: white;
            padding: 0px;     /* No padding needed for smaller widget */
        """)
        
        layout.addWidget(self.pc_label)
        layout.addStretch()
        
        self.setLayout(layout)
        self.update_style()
        
    def resizeEvent(self, event):
        """Handle resize events to adjust font size."""
        super().resizeEvent(event)
        # Adjust font size based on widget size
        if self.width() <= 60:  # If small mode
            self.pc_label.setStyleSheet("""
                font-weight: bold; 
                font-size: 14px;  /* Smaller font for small widget */
                color: white;
                padding: 0px;
            """)
        else:
            self.pc_label.setStyleSheet("""
                font-weight: bold; 
                font-size: 18px;
                color: white;
                padding: 0px;
            """)
    
    def update_status(self, status):
        """Update the PC status."""
        self.status = status
        self.update_style()
    
    def update_style(self):
        """Update the widget style based on status."""
        if self.status == "available":
            # Enhanced green with better styling
            self.setStyleSheet("""
                QWidget {
                    background-color: rgba(46, 204, 113, 0.9);
                    border: 2px solid rgba(46, 204, 113, 1.0);
                    border-radius: 8px;  /* Smaller radius for smaller widget */
                }
                QLabel {
                    color: white;
                    background-color: transparent;
                }
            """)
        elif self.status == "occupied":
            # Enhanced red with better styling
            self.setStyleSheet("""
                QWidget {
                    background-color: rgba(231, 76, 60, 0.9);
                    border: 2px solid rgba(231, 76, 60, 1.0);
                    border-radius: 8px;  /* Smaller radius for smaller widget */
                }
                QLabel {
                    color: white;
                    background-color: transparent;
                }
            """)
        else:
            # Yellow for maintenance with better styling
            self.setStyleSheet("""
                QWidget {
                    background-color: rgba(243, 156, 18, 0.9);
                    border: 2px solid rgba(243, 156, 18, 1.0);
                    border-radius: 8px;  /* Smaller radius for smaller widget */
                }
                QLabel {
                    color: white;
                    background-color: transparent;
                }
            """)
    
    def mousePressEvent(self, event):
        """Handle mouse press event."""
        self.clicked.emit(self.pc_number)
        super().mousePressEvent(event)

def apply_dark_theme(app):
    """Apply a dark theme to the application."""
    app.setStyle("Fusion")
    
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.WindowText, Qt.white)
    dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
    dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
    dark_palette.setColor(QPalette.ToolTipText, Qt.white)
    dark_palette.setColor(QPalette.Text, Qt.white)
    dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ButtonText, Qt.white)
    dark_palette.setColor(QPalette.BrightText, Qt.red)
    dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.HighlightedText, Qt.black)
    
    app.setPalette(dark_palette)
    
    app.setStyleSheet("""
        QToolTip { 
            color: #ffffff; 
            background-color: #2a82da; 
            border: 1px solid white; 
        }
    """)

def apply_light_theme(app):
    """Apply a light theme to the application."""
    app.setStyle("Fusion")
    
    light_palette = QPalette()
    app.setPalette(light_palette)
    
    app.setStyleSheet("""
        QToolTip { 
            color: #ffffff; 
            background-color: #2a82da; 
            border: 1px solid white; 
        }
    """)

# Add the missing functions
def create_header(text, level=1):
    """
    Create a header label with the given text and level.
    
    Args:
        text (str): The text to display in the header
        level (int): The header level (1 for main header, 2 for subheader)
        
    Returns:
        QLabel: The header label widget
    """
    if level == 1:
        header = HeaderLabel(text)
    else:
        header = SubHeaderLabel(text)
    
    return header

def create_button(text, button_type="primary", icon=None):
    """
    Create a button with the specified text and style.
    
    Args:
        text (str): The text to display on the button
        button_type (str): The type of button ('primary', 'secondary', 'danger', 'success')
        icon (QIcon, optional): An icon to display on the button
        
    Returns:
        QPushButton: The styled button widget
    """
    if button_type.lower() == "primary":
        button = PrimaryButton(text)
    elif button_type.lower() == "secondary":
        button = SecondaryButton(text)
    elif button_type.lower() == "danger":
        button = DangerButton(text)
    elif button_type.lower() == "success":
        button = SuccessButton(text)
    else:
        button = PrimaryButton(text)
    
    if icon:
        button.setIcon(icon)
    
    return button

class CloseButton(QPushButton):
    """A styled close button for the top-right corner of windows."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(30, 30)  # Reduced from 40x40 to 30x30
        self.setToolTip("Close")
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("""
            QPushButton {
                background-color: rgba(30, 30, 50, 0.7);
                color: #00c3ff;
                border: 1px solid rgba(0, 195, 255, 0.5);
                border-radius: 15px;  /* Reduced from 20px to match the smaller size */
                font-size: 14px;  /* Reduced from 16px */
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 60, 60, 0.8);
                color: white;
                border: 1px solid rgba(255, 60, 60, 0.8);
            }
            QPushButton:pressed {
                background-color: rgba(200, 40, 40, 1.0);
                color: white;
            }
        """)
        self.setText("✕")
        
        # Connect the close button to the parent window's close method
        self.clicked.connect(self.close_window)
    
    def close_window(self):
        """Close the parent window."""
        parent_window = self.get_parent_window()
        if parent_window:
            parent_window.close()
    
    def get_parent_window(self):
        """Get the parent window (QMainWindow or QDialog)."""
        parent = self.parent()
        while parent:
            if hasattr(parent, 'close') and callable(parent.close):
                return parent
            parent = parent.parent()
        return None

def add_close_button(window):
    """
    Add a close button to the top-right corner of a window.
    
    Args:
        window: The window to add the close button to
        
    Returns:
        The close button that was added
    """
    close_button = CloseButton(window)
    
    # Position the button in the top-right corner with some margin
    close_button.move(window.width() - close_button.width() - 15, 15)  # Reduced margins from 20 to 15
    
    # Make sure the button stays in the top-right corner when window is resized
    window.resizeEvent = lambda event: [
        # Call the original resizeEvent if it exists
        window.__class__.resizeEvent(window, event) if hasattr(window.__class__, 'resizeEvent') else None,
        # Update the button position
        close_button.move(window.width() - close_button.width() - 15, 15)  # Reduced margins from 20 to 15
    ]
    
    close_button.raise_()  # Ensure it's on top of other widgets
    close_button.show()
    
    return close_button 