from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, 
    QFrame, QSizePolicy, QSpacerItem, QTableWidgetItem, QMessageBox,
    QDialog, QComboBox, QLineEdit, QPushButton, QHeaderView
)
from PyQt5.QtCore import Qt, QTimer, QDateTime
from PyQt5.QtGui import QFont, QColor

from src.common import (
    HeaderLabel, SubHeaderLabel, Card, StyledTable, StyledLineEdit,
    StyledComboBox, PrimaryButton, SecondaryButton, DangerButton, SuccessButton,
    show_message, confirm_action, create_spacer, PCStatusWidget, CountdownTimer
)
from src.database import db, User, PC, Session
from src.utils.helpers import (
    format_currency, format_time, get_duration_options, 
    get_payment_methods, calculate_price_for_duration,
    calculate_time_left, format_time_left, format_datetime
)

class ExtendSessionDialog(QDialog):
    """Dialog for extending a session."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Extend Session")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        # Duration selection
        duration_layout = QHBoxLayout()
        duration_label = QLabel("Additional Time:")
        self.duration_combo = StyledComboBox()
        
        # Add duration options
        for option in get_duration_options():
            self.duration_combo.addItem(
                f"{option['label']} - {format_currency(option['price'])}",
                option['value']
            )
        
        duration_layout.addWidget(duration_label)
        duration_layout.addWidget(self.duration_combo)
        
        layout.addLayout(duration_layout)
        
        # Payment method
        payment_layout = QHBoxLayout()
        payment_label = QLabel("Payment Method:")
        self.payment_combo = StyledComboBox()
        
        # Add payment methods
        for method in get_payment_methods():
            self.payment_combo.addItem(method)
        
        payment_layout.addWidget(payment_label)
        payment_layout.addWidget(self.payment_combo)
        
        layout.addLayout(payment_layout)
        
        # Price display
        self.price_label = QLabel("Price: $0.00")
        self.price_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(self.price_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        cancel_button = SecondaryButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        
        extend_button = PrimaryButton("Extend Session")
        extend_button.clicked.connect(self.accept)
        
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(extend_button)
        
        layout.addLayout(button_layout)
        
        # Connect signals
        self.duration_combo.currentIndexChanged.connect(self.update_price)
        
        # Initial price update
        self.update_price()
    
    def update_price(self):
        """Update the displayed price based on selected duration."""
        # Get selected duration
        duration = self.duration_combo.currentData()
        
        # Calculate price
        price = calculate_price_for_duration(duration)
        
        # Update price label
        self.price_label.setText(f"Price: {format_currency(price)}")
    
    def get_values(self):
        """Get the selected values."""
        return {
            'duration': self.duration_combo.currentData(),
            'payment_method': self.payment_combo.currentText(),
            'price': calculate_price_for_duration(self.duration_combo.currentData())
        }

class SessionsTab(QWidget):
    """Sessions tab for the admin panel."""
    
    def __init__(self):
        """Initialize the sessions tab."""
        super().__init__()
        
        self.init_ui()
        self.refresh_data()
        
        # Set up timer for countdown updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_countdowns)
        self.timer.start(1000)  # Update every second
    
    def init_ui(self):
        """Initialize the user interface."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.setSpacing(20)
        
        # Header
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background-color: rgba(0, 195, 255, 0.1);
                border-radius: 10px;
                padding: 15px;
            }
        """)
        header_layout = QHBoxLayout(header)
        
        title = QLabel("Session & Time Management")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setStyleSheet("color: #00c3ff;")
        header_layout.addWidget(title)
        
        main_layout.addWidget(header)
        
        # Active Sessions
        active_card = Card()
        active_layout = QVBoxLayout()
        active_layout.setContentsMargins(0, 0, 0, 0)
        
        active_header = SubHeaderLabel("Active Sessions")
        active_layout.addWidget(active_header)
        
        self.active_table = StyledTable()
        self.active_table.setColumnCount(8)
        self.active_table.setHorizontalHeaderLabels([
            "User", "PC", "Start Time", "End Time", "Duration", "Time Left", "Status", "Actions"
        ])

        self.active_table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: rgba(0, 195, 255, 0.1);
                color: #00c3ff;
                padding: 0px;
                margin: 0px;
                border: none;
                font-size: 12px;
                font-weight: bold;
            }
        """)

        self.active_table.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)
        self.active_table.horizontalHeader().setFixedHeight(50)
        
        # Set column widths - make Actions column wider
        self.active_table.horizontalHeader().setStretchLastSection(False)
        self.active_table.horizontalHeader().setSectionResizeMode(7, QHeaderView.Fixed)
        self.active_table.setColumnWidth(7, 250)  # Set Actions column width to 250px
        
        # Set other columns to stretch
        for i in range(7):
            self.active_table.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)
        
        active_layout.addWidget(self.active_table)
        active_card.layout.addLayout(active_layout)
        
        main_layout.addWidget(active_card)
        
        # Session History
        history_card = Card()
        history_layout = QVBoxLayout()
        history_layout.setContentsMargins(0, 0, 0, 0)
        
        history_header = SubHeaderLabel("Session History")
        history_layout.addWidget(history_header)
        
        self.history_table = StyledTable()
        self.history_table.setColumnCount(7)
        self.history_table.setHorizontalHeaderLabels([
            "User", "PC", "Start Time", "End Time", "Duration", "Payment", "Status"
        ])

        self.history_table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: rgba(0, 195, 255, 0.1);
                color: #00c3ff;
                padding: 0px;
                margin: 0px;
                border: none;
                font-size: 12px;
                font-weight: bold;
            }
        """)

        self.history_table.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)
        self.history_table.horizontalHeader().setFixedHeight(50)
        
        history_layout.addWidget(self.history_table)
        history_card.layout.addLayout(history_layout)
        
        main_layout.addWidget(history_card)
        
        # Add spacer at the bottom
        main_layout.addItem(create_spacer())
    
    def refresh_data(self):
        """Refresh data in the tab."""
        self.refresh_active_sessions()
        self.refresh_session_history()
    
    def refresh_active_sessions(self):
        """Refresh active sessions table."""
        cursor = db.get_cursor()
        try:
            # Clear existing rows
            self.active_table.setRowCount(0)
            
            # Get active sessions
            query = """
            SELECT 
                s.id,
                u.name as user_name,
                p.pc_number,
                s.start_time,
                s.end_time,
                s.duration_minutes,
                s.status,
                s.payment_method,
                s.payment_amount
            FROM sessions s
            JOIN users u ON s.user_id = u.id
            JOIN pcs p ON s.pc_id = p.id
            WHERE s.status IN ('active', 'paused')
            ORDER BY s.start_time DESC
            """
            cursor.execute(query)
            results = cursor.fetchall()
            
            # Add to table
            for i, result in enumerate(results):
                self.active_table.insertRow(i)
                
                # User
                self.active_table.setItem(i, 0, QTableWidgetItem(result['user_name']))
                
                # PC
                self.active_table.setItem(i, 1, QTableWidgetItem(f"PC {result['pc_number']}"))
                
                # Start Time
                start_time = result['start_time'].strftime("%H:%M:%S")
                self.active_table.setItem(i, 2, QTableWidgetItem(start_time))
                
                # End Time
                end_time = result['end_time'].strftime("%H:%M:%S") if result['end_time'] else ""
                self.active_table.setItem(i, 3, QTableWidgetItem(end_time))
                
                # Duration
                duration = format_time(result['duration_minutes'])
                self.active_table.setItem(i, 4, QTableWidgetItem(duration))
                
                # Time Left
                time_left = format_time_left(result['end_time'])
                time_left_item = QTableWidgetItem(time_left)
                
                # Color code time left
                minutes_left = calculate_time_left(result['end_time'])
                if minutes_left < 5:
                    time_left_item.setForeground(QColor('#e74c3c'))  # Red
                elif minutes_left < 15:
                    time_left_item.setForeground(QColor('#f39c12'))  # Yellow
                else:
                    time_left_item.setForeground(QColor('#2ecc71'))  # Green
                
                self.active_table.setItem(i, 5, time_left_item)
                
                # Status
                status_item = QTableWidgetItem(result['status'].capitalize())
                
                # Color code status
                if result['status'] == 'active':
                    status_item.setForeground(QColor('#2ecc71'))  # Green
                elif result['status'] == 'paused':
                    status_item.setForeground(QColor('#3498db'))  # Blue
                
                self.active_table.setItem(i, 6, status_item)
                
                # Actions
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(2, 0, 2, 0)  # Reduced horizontal margins
                actions_layout.setSpacing(2)  # Reduced spacing between buttons
                
                # Store session ID in the widget
                actions_widget.setProperty("session_id", result['id'])
                
                if result['status'] == 'active':
                    # Pause button
                    pause_button = SecondaryButton("Pause")
                    pause_button.clicked.connect(lambda _, sid=result['id']: self.pause_session(sid))
                    actions_layout.addWidget(pause_button)
                else:
                    # Resume button
                    resume_button = SuccessButton("Resume")
                    resume_button.clicked.connect(lambda _, sid=result['id']: self.resume_session(sid))
                    actions_layout.addWidget(resume_button)
                
                # Extend button
                extend_button = PrimaryButton("Extend")
                extend_button.clicked.connect(lambda _, sid=result['id']: self.extend_session(sid))
                actions_layout.addWidget(extend_button)
                
                # Terminate button
                terminate_button = DangerButton("Terminate")
                terminate_button.clicked.connect(lambda _, sid=result['id']: self.terminate_session(sid))
                actions_layout.addWidget(terminate_button)
                
                self.active_table.setCellWidget(i, 7, actions_widget)
        finally:
            cursor.close()
    
    def refresh_session_history(self):
        """Refresh session history table."""
        cursor = db.get_cursor()
        try:
            # Clear existing rows
            self.history_table.setRowCount(0)
            
            # Get completed/terminated sessions
            query = """
            SELECT 
                s.id,
                u.name as user_name,
                p.pc_number,
                s.start_time,
                s.end_time,
                s.duration_minutes,
                s.status,
                s.payment_method,
                s.payment_amount
            FROM sessions s
            JOIN users u ON s.user_id = u.id
            JOIN pcs p ON s.pc_id = p.id
            WHERE s.status IN ('completed', 'terminated')
            ORDER BY s.start_time DESC
            LIMIT 20
            """
            cursor.execute(query)
            results = cursor.fetchall()
            
            # Add to table
            for i, result in enumerate(results):
                self.history_table.insertRow(i)
                
                # User
                self.history_table.setItem(i, 0, QTableWidgetItem(result['user_name']))
                
                # PC
                self.history_table.setItem(i, 1, QTableWidgetItem(f"PC {result['pc_number']}"))
                
                # Start Time
                start_time = result['start_time'].strftime("%H:%M:%S")
                self.history_table.setItem(i, 2, QTableWidgetItem(start_time))
                
                # End Time
                end_time = result['end_time'].strftime("%H:%M:%S") if result['end_time'] else ""
                self.history_table.setItem(i, 3, QTableWidgetItem(end_time))
                
                # Duration
                duration = format_time(result['duration_minutes'])
                self.history_table.setItem(i, 4, QTableWidgetItem(duration))
                
                # Payment
                payment = f"{result['payment_method']} - {format_currency(result['payment_amount'])}"
                self.history_table.setItem(i, 5, QTableWidgetItem(payment))
                
                # Status
                status_item = QTableWidgetItem(result['status'].capitalize())
                
                # Color code status
                if result['status'] == 'completed':
                    status_item.setForeground(QColor('#2ecc71'))  # Green
                elif result['status'] == 'terminated':
                    status_item.setForeground(QColor('#e74c3c'))  # Red
                
                self.history_table.setItem(i, 6, status_item)
        finally:
            cursor.close()
    
    def update_countdowns(self):
        """Update countdown timers in the active sessions table."""
        for i in range(self.active_table.rowCount()):
            # Get end time from the table
            end_time_item = self.active_table.item(i, 3)
            if not end_time_item or not end_time_item.text():
                continue
            
            # Get status from the table
            status_item = self.active_table.item(i, 6)
            if not status_item or status_item.text().lower() != "active":
                continue
            
            # Parse end time
            end_time_str = end_time_item.text()
            today = QDateTime.currentDateTime().date().toString(Qt.ISODate)
            end_time = QDateTime.fromString(f"{today} {end_time_str}", "yyyy-MM-dd HH:mm:ss")
            
            # Calculate time left
            now = QDateTime.currentDateTime()
            if now >= end_time:
                # Session has ended
                time_left_item = QTableWidgetItem("Time's up!")
                time_left_item.setForeground(QColor('#e74c3c'))  # Red
                self.active_table.setItem(i, 5, time_left_item)
                
                # Get session ID and auto-terminate
                actions_widget = self.active_table.cellWidget(i, 7)
                if actions_widget:
                    session_id = actions_widget.property("session_id")
                    if session_id:
                        self.complete_session(session_id)
            else:
                # Update time left
                secs_left = now.secsTo(end_time)
                hours = secs_left // 3600
                minutes = (secs_left % 3600) // 60
                seconds = secs_left % 60
                
                time_left = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                time_left_item = QTableWidgetItem(time_left)
                
                # Color code time left
                if secs_left < 300:  # Less than 5 minutes
                    time_left_item.setForeground(QColor('#e74c3c'))  # Red
                elif secs_left < 900:  # Less than 15 minutes
                    time_left_item.setForeground(QColor('#f39c12'))  # Yellow
                else:
                    time_left_item.setForeground(QColor('#2ecc71'))  # Green
                
                self.active_table.setItem(i, 5, time_left_item)
    
    def pause_session(self, session_id):
        """Pause a session."""
        try:
            session = Session.get_by_id(session_id)
            if session:
                session.update_status('paused')
                self.refresh_data()
        except Exception as e:
            show_message(self, "Error", f"Failed to pause session: {str(e)}", QMessageBox.Critical)
    
    def resume_session(self, session_id):
        """Resume a paused session."""
        try:
            session = Session.get_by_id(session_id)
            if session:
                session.update_status('active')
                self.refresh_data()
        except Exception as e:
            show_message(self, "Error", f"Failed to resume session: {str(e)}", QMessageBox.Critical)
    
    def extend_session(self, session_id):
        """Extend a session."""
        dialog = ExtendSessionDialog(self)
        if dialog.exec_():
            values = dialog.get_values()
            
            try:
                session = Session.get_by_id(session_id)
                if session:
                    session.extend_time(
                        values['duration'],
                        values['price'],
                        values['payment_method']
                    )
                    self.refresh_data()
                    
                    show_message(
                        self, 
                        "Success", 
                        f"Session extended by {format_time(values['duration'])}.\n"
                        f"Additional charge: {format_currency(values['price'])}"
                    )
            except Exception as e:
                show_message(self, "Error", f"Failed to extend session: {str(e)}", QMessageBox.Critical)
    
    def terminate_session(self, session_id):
        """Terminate a session."""
        if confirm_action("Terminate Session", "Are you sure you want to terminate this session?", self):
            try:
                session = Session.get_by_id(session_id)
                if session:
                    session.update_status('terminated')
                    self.refresh_data()
            except Exception as e:
                show_message(self, "Error", f"Failed to terminate session: {str(e)}", QMessageBox.Critical)
    
    def complete_session(self, session_id):
        """Complete a session (automatically called when time is up)."""
        try:
            session = Session.get_by_id(session_id)
            if session:
                session.update_status('completed')
                self.refresh_data()
        except Exception as e:
            print(f"Failed to complete session: {str(e)}")
    
    def select_pc(self, pc_number):
        """Select a PC in the active sessions table."""
        for i in range(self.active_table.rowCount()):
            pc_item = self.active_table.item(i, 1)
            if pc_item and pc_item.text() == f"PC {pc_number}":
                self.active_table.selectRow(i)
                break 