from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, 
    QFrame, QSizePolicy, QSpacerItem, QTableWidgetItem, QMessageBox,
    QDialog, QComboBox, QLineEdit, QPushButton, QListWidget, QListWidgetItem,
    QFileDialog, QCheckBox, QDateEdit
)
from PyQt5.QtCore import Qt, QTimer, QDateTime, QDate
from PyQt5.QtGui import QFont, QColor, QIcon, QPixmap

from src.common import (
    HeaderLabel, SubHeaderLabel, Card, StyledTable, StyledLineEdit,
    StyledComboBox, PrimaryButton, SecondaryButton, DangerButton, SuccessButton,
    show_message, confirm_action, create_spacer
)
from src.database import db
from src.utils.helpers import format_currency, format_time, format_datetime

class ReportsTab(QWidget):
    """Reports tab for the admin panel."""
    
    def __init__(self):
        """Initialize the reports tab."""
        super().__init__()
        
        self.init_ui()
        self.refresh_data()
    
    def init_ui(self):
        """Initialize the user interface."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.setSpacing(25)  # Increased spacing between main sections
        
        # Header with enhanced styling
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background-color: rgba(0, 195, 255, 0.1);
                border-radius: 10px;
                padding: 15px;
            }
        """)
        header_layout = QHBoxLayout(header)
        
        title = QLabel("Reports & Analytics")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setStyleSheet("color: #00c3ff;")
        header_layout.addWidget(title)
        
        main_layout.addWidget(header)

        
        # Date Range Selection with improved styling
        date_range_card = Card()
        date_range_card.setStyleSheet("""
            QFrame {
                background-color: rgba(25, 25, 40, 0.85);
                border-radius: 10px;
                border: 1px solid rgba(0, 195, 255, 0.4);
                padding: 18px;
            }
            QLabel {
                color: white;
                font-size: 15px;
            }
        """)
        date_range_layout = QVBoxLayout()
        date_range_layout.setContentsMargins(0, 0, 0, 0)
        date_range_layout.setSpacing(15)  # Increased spacing
        
        date_range_header = SubHeaderLabel("Select Date Range")
        date_range_header.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #8a8aff;
            margin-bottom: 8px;
            letter-spacing: 0.6px;
        """)
        date_range_layout.addWidget(date_range_header)
        
        date_form_layout = QHBoxLayout()
        date_form_layout.setSpacing(20)  # Increased spacing between date elements
        
        # Start Date
        start_date_layout = QVBoxLayout()
        start_date_layout.setSpacing(8)  # Increased spacing
        start_date_label = QLabel("Start Date:")
        start_date_label.setStyleSheet("font-weight: bold;")
        start_date_label.setStyleSheet("font-weight: bold; padding: 5px;")
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDate(QDate.currentDate().addDays(-7))  # Default to 7 days ago
        self.start_date_edit.setStyleSheet("""
            QDateEdit {
                border: 1px solid rgba(0, 195, 255, 0.5);
                border-radius: 5px;
                padding: 8px;
                background-color: rgba(30, 30, 50, 0.7);
                color: white;
                font-size: 14px;
                min-width: 120px;
            }
        """)
        
        start_date_layout.addWidget(start_date_label)
        start_date_layout.addWidget(self.start_date_edit)
        
        # End Date
        end_date_layout = QVBoxLayout()
        end_date_layout.setSpacing(8)  # Increased spacing
        end_date_label = QLabel("End Date:")
        end_date_label.setStyleSheet("font-weight: bold;")
        end_date_label.setStyleSheet("font-weight: bold; padding: 5px;")
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDate(QDate.currentDate())  # Default to today
        self.end_date_edit.setStyleSheet("""
            QDateEdit {
                border: 1px solid rgba(0, 195, 255, 0.5);
                border-radius: 5px;
                padding: 8px;
                background-color: rgba(30, 30, 50, 0.7);
                color: white;
                font-size: 14px;
                min-width: 120px;
            }
        """)
        
        end_date_layout.addWidget(end_date_label)
        end_date_layout.addWidget(self.end_date_edit)
        
        # Quick Select Buttons
        quick_select_layout = QVBoxLayout()
        quick_select_layout.setSpacing(8)  # Increased spacing
        quick_select_label = QLabel("Quick Select:")
        quick_select_label.setStyleSheet("font-weight: bold;")
        quick_select_label.setStyleSheet("font-weight: bold; padding: 5px;")
        quick_buttons_layout = QHBoxLayout()
        quick_buttons_layout.setSpacing(10)  # Increased spacing
        
        today_button = SecondaryButton("Today")
        today_button.clicked.connect(self.set_today)
        
        week_button = SecondaryButton("This Week")
        week_button.clicked.connect(self.set_this_week)
        
        month_button = SecondaryButton("This Month")
        month_button.clicked.connect(self.set_this_month)
        
        quick_buttons_layout.addWidget(today_button)
        quick_buttons_layout.addWidget(week_button)
        quick_buttons_layout.addWidget(month_button)
        
        quick_select_layout.addWidget(quick_select_label)
        quick_select_layout.addLayout(quick_buttons_layout)
        
        # Generate Report Button
        generate_layout = QVBoxLayout()
        generate_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        generate_button = PrimaryButton("Generate Reports")
        generate_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0078d7, stop:1 #00c3ff);
                color: white;
                border: none;
                border-radius: 5px;
                padding: 12px 15px;
                font-size: 15px;
                letter-spacing: 0.5px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0086ef, stop:1 #19ceff);
            }
        """)
        generate_button.clicked.connect(self.generate_reports)
        generate_layout.addWidget(generate_button)
        
        # Add all layouts to date form
        date_form_layout.addLayout(start_date_layout)
        date_form_layout.addLayout(end_date_layout)
        date_form_layout.addLayout(quick_select_layout)
        date_form_layout.addLayout(generate_layout)
        
        date_range_layout.addLayout(date_form_layout)
        date_range_card.layout.addLayout(date_range_layout)
        
        main_layout.addWidget(date_range_card)
        
        # Create side-by-side layout for Revenue and Usage Statistics
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)  # Good spacing between the cards
        
        # Revenue Summary - now on the left side
        revenue_card = Card()
        revenue_card.setStyleSheet("""
            QFrame {
                background-color: rgba(25, 25, 40, 0.85);
                border-radius: 10px;
                border: 1px solid rgba(0, 195, 255, 0.4);
                padding: 18px;
            }
            QLabel {
                color: white;
                font-size: 15px;
            }
        """)
        revenue_layout = QVBoxLayout()
        revenue_layout.setContentsMargins(0, 0, 0, 0)
        revenue_layout.setSpacing(15)  # Increased spacing
        
        revenue_header = SubHeaderLabel("Revenue Summary")
        revenue_header.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #8a8aff;
            margin-bottom: 8px;
            letter-spacing: 0.6px;
        """)
        revenue_layout.addWidget(revenue_header)
        
        revenue_grid = QGridLayout()
        revenue_grid.setVerticalSpacing(15)  # Increased spacing
        revenue_grid.setHorizontalSpacing(20)
        revenue_grid.setColumnStretch(1, 1)
        
        # Gaming Revenue
        gaming_label = QLabel("Gaming Revenue:")
        gaming_label.setStyleSheet("font-size: 15px;")
        gaming_label.setStyleSheet("font-weight: bold; padding: 2px;")
        revenue_grid.addWidget(gaming_label, 0, 0)
        self.gaming_revenue_label = QLabel("$0.00")
        self.gaming_revenue_label.setStyleSheet("font-size: 15px; color: #2ecc71;")
        self.gaming_revenue_label.setStyleSheet("padding: 2px;")
        revenue_grid.addWidget(self.gaming_revenue_label, 0, 1)
        
        # Food & Services Revenue
        food_label = QLabel("Food & Services Revenue:")
        food_label.setStyleSheet("font-size: 15px;")
        food_label.setStyleSheet("font-weight: bold; padding: 2px;")
        revenue_grid.addWidget(food_label, 1, 0)
        self.food_revenue_label = QLabel("$0.00")
        self.food_revenue_label.setStyleSheet("font-size: 15px; color: #2ecc71;")
        self.food_revenue_label.setStyleSheet("padding: 2px;")
        revenue_grid.addWidget(self.food_revenue_label, 1, 1)
        
        # Divider line
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setFrameShadow(QFrame.Sunken)
        divider.setStyleSheet("background-color: rgba(138, 138, 255, 0.3); margin: 10px 0;")
        revenue_grid.addWidget(divider, 2, 0, 1, 2)
        
        # Total Revenue
        total_label = QLabel("Total Revenue:")
        total_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        total_label.setStyleSheet("font-weight: bold; padding: 2px;")
        revenue_grid.addWidget(total_label, 3, 0)
        self.total_revenue_label = QLabel("$0.00")
        self.total_revenue_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #00c3ff;")
        self.total_revenue_label.setStyleSheet("padding: 2px;")
        revenue_grid.addWidget(self.total_revenue_label, 3, 1)
        
        revenue_layout.addLayout(revenue_grid)
        revenue_card.layout.addLayout(revenue_layout)
        
        # Usage Statistics - now on the right side
        usage_card = Card()
        usage_card.setStyleSheet("""
            QFrame {
                background-color: rgba(25, 25, 40, 0.85);
                border-radius: 10px;
                border: 1px solid rgba(0, 195, 255, 0.4);
                padding: 18px;
            }
            QLabel {
                color: white;
                font-size: 15px;
            }
        """)
        usage_layout = QVBoxLayout()
        usage_layout.setContentsMargins(0, 0, 0, 0)
        usage_layout.setSpacing(15)  # Increased spacing
        
        usage_header = SubHeaderLabel("Usage Statistics")
        usage_header.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #8a8aff;
            margin-bottom: 8px;
            letter-spacing: 0.6px;
        """)
        usage_layout.addWidget(usage_header)
        
        usage_grid = QGridLayout()
        usage_grid.setVerticalSpacing(15)  # Increased spacing
        usage_grid.setHorizontalSpacing(20)
        usage_grid.setColumnStretch(1, 1)
        
        # Total Sessions
        sessions_label = QLabel("Total Sessions:")
        sessions_label.setStyleSheet("font-size: 15px;")
        sessions_label.setStyleSheet("font-weight: bold; padding: 2px;")
        usage_grid.addWidget(sessions_label, 0, 0)
        self.total_sessions_label = QLabel("0")
        self.total_sessions_label.setStyleSheet("font-size: 15px; color: #3498db;")
        self.total_sessions_label.setStyleSheet("padding: 2px;")
        usage_grid.addWidget(self.total_sessions_label, 0, 1)
        
        # Total Users
        users_label = QLabel("Total Users:")
        users_label.setStyleSheet("font-size: 15px;")
        users_label.setStyleSheet("font-weight: bold; padding: 2px;")
        usage_grid.addWidget(users_label, 1, 0)
        self.total_users_label = QLabel("0")
        self.total_users_label.setStyleSheet("font-size: 15px; color: #3498db;")
        self.total_users_label.setStyleSheet("padding: 2px;")
        usage_grid.addWidget(self.total_users_label, 1, 1)
        
        # Total Hours
        hours_label = QLabel("Total Hours:")
        hours_label.setStyleSheet("font-size: 15px;")
        hours_label.setStyleSheet("font-weight: bold; padding: 2px;")
        usage_grid.addWidget(hours_label, 2, 0)
        self.total_hours_label = QLabel("0h")
        self.total_hours_label.setStyleSheet("font-size: 15px; color: #3498db;")
        usage_grid.addWidget(self.total_hours_label, 2, 1)
        
        # Average Session Duration
        avg_label = QLabel("Average Session Duration:")
        avg_label.setStyleSheet("font-size: 15px;")
        avg_label.setStyleSheet("font-weight: bold; padding: 2px;")
        usage_grid.addWidget(avg_label, 3, 0)
        self.avg_duration_label = QLabel("0h 0m")
        self.avg_duration_label.setStyleSheet("font-size: 15px; color: #3498db;")
        self.avg_duration_label.setStyleSheet("padding: 2px;")
        usage_grid.addWidget(self.avg_duration_label, 3, 1)
        
        usage_layout.addLayout(usage_grid)
        usage_card.layout.addLayout(usage_layout)
        
        # Add both cards to the stats layout
        stats_layout.addWidget(revenue_card)
        stats_layout.addWidget(usage_card)
        
        # Add the side-by-side layout to the main layout
        main_layout.addLayout(stats_layout)
        
        # Export Button with improved styling
        export_button = PrimaryButton("Export Reports to CSV")
        export_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0078d7, stop:1 #00c3ff);
                color: white;
                border: none;
                border-radius: 5px;
                padding: 12px 15px;
                font-size: 15px;
                letter-spacing: 0.5px;
                margin-top: 10px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0086ef, stop:1 #19ceff);
            }
        """)
        export_button.clicked.connect(self.export_reports)
        main_layout.addWidget(export_button)
        
        # Add spacer at the bottom
        main_layout.addItem(create_spacer())
    
    def set_today(self):
        """Set date range to today."""
        today = QDate.currentDate()
        self.start_date_edit.setDate(today)
        self.end_date_edit.setDate(today)
    
    def set_this_week(self):
        """Set date range to this week."""
        today = QDate.currentDate()
        start_of_week = today.addDays(-(today.dayOfWeek() - 1))
        self.start_date_edit.setDate(start_of_week)
        self.end_date_edit.setDate(today)
    
    def set_this_month(self):
        """Set date range to this month."""
        today = QDate.currentDate()
        start_of_month = QDate(today.year(), today.month(), 1)
        self.start_date_edit.setDate(start_of_month)
        self.end_date_edit.setDate(today)
    
    def generate_reports(self):
        """Generate reports for the selected date range."""
        start_date = self.start_date_edit.date().toString(Qt.ISODate)
        end_date = self.end_date_edit.date().toString(Qt.ISODate)
        
        # Validate date range
        if self.start_date_edit.date() > self.end_date_edit.date():
            show_message(self, "Error", "Start date cannot be after end date.", QMessageBox.Warning)
            return
        
        # Generate reports
        self.generate_revenue_summary(start_date, end_date)
        self.generate_usage_statistics(start_date, end_date)
    
    def generate_revenue_summary(self, start_date, end_date):
        """Generate revenue summary for the selected date range."""
        cursor = db.get_cursor()
        try:
            # Get gaming revenue
            query = """
            SELECT SUM(payment_amount) as total 
            FROM sessions 
            WHERE DATE(start_time) BETWEEN %s AND %s
            """
            cursor.execute(query, (start_date, end_date))
            result = cursor.fetchone()
            
            gaming_revenue = result['total'] or 0
            self.gaming_revenue_label.setText(format_currency(gaming_revenue))
            
            # Get food & services revenue
            query = """
            SELECT SUM(total_amount) as total 
            FROM orders 
            WHERE DATE(order_time) BETWEEN %s AND %s
            """
            cursor.execute(query, (start_date, end_date))
            result = cursor.fetchone()
            
            food_revenue = result['total'] or 0
            self.food_revenue_label.setText(format_currency(food_revenue))
            
            # Calculate total
            total_revenue = gaming_revenue + food_revenue
            self.total_revenue_label.setText(format_currency(total_revenue))
        finally:
            cursor.close()
    
    def generate_usage_statistics(self, start_date, end_date):
        """Generate usage statistics for the selected date range."""
        cursor = db.get_cursor()
        try:
            # Get total sessions
            query = """
            SELECT COUNT(*) as count 
            FROM sessions 
            WHERE DATE(start_time) BETWEEN %s AND %s
            """
            cursor.execute(query, (start_date, end_date))
            result = cursor.fetchone()
            
            total_sessions = result['count'] or 0
            self.total_sessions_label.setText(str(total_sessions))
            
            # Get total users
            query = """
            SELECT COUNT(DISTINCT user_id) as count 
            FROM sessions 
            WHERE DATE(start_time) BETWEEN %s AND %s
            """
            cursor.execute(query, (start_date, end_date))
            result = cursor.fetchone()
            
            total_users = result['count'] or 0
            self.total_users_label.setText(str(total_users))
            
            # Get total hours
            query = """
            SELECT SUM(duration_minutes) as total_minutes 
            FROM sessions 
            WHERE DATE(start_time) BETWEEN %s AND %s
            """
            cursor.execute(query, (start_date, end_date))
            result = cursor.fetchone()
            
            total_minutes = result['total_minutes'] or 0
            total_hours = total_minutes / 60
            self.total_hours_label.setText(f"{total_hours:.1f}h")
            
            # Calculate average session duration
            if total_sessions > 0:
                avg_minutes = total_minutes / total_sessions
                avg_hours = int(avg_minutes // 60)
                avg_mins = int(avg_minutes % 60)
                self.avg_duration_label.setText(f"{avg_hours}h {avg_mins}m")
            else:
                self.avg_duration_label.setText("0h 0m")
        finally:
            cursor.close()
    
    def export_reports(self):
        """Export reports to CSV files."""
        # Get date range for filename
        start_date = self.start_date_edit.date().toString("yyyy-MM-dd")
        end_date = self.end_date_edit.date().toString("yyyy-MM-dd")
        
        # Ask for directory to save files
        directory = QFileDialog.getExistingDirectory(
            self, "Select Directory to Save Reports", "", QFileDialog.ShowDirsOnly
        )
        
        if not directory:
            return
        
        try:
            # Export revenue summary
            self.export_revenue_summary(directory, start_date, end_date)
            
            # Export usage statistics
            self.export_usage_statistics(directory, start_date, end_date)
            
            show_message(self, "Success", "Reports exported successfully.")
        except Exception as e:
            show_message(self, "Error", f"Failed to export reports: {str(e)}", QMessageBox.Critical)
    
    def export_revenue_summary(self, directory, start_date, end_date):
        """Export revenue summary to CSV."""
        import csv
        
        filename = f"{directory}/revenue_summary_{start_date}_to_{end_date}.csv"
        
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header
            writer.writerow(["Revenue Type", "Amount"])
            
            # Write data
            gaming_revenue = self.gaming_revenue_label.text()
            food_revenue = self.food_revenue_label.text()
            total_revenue = self.total_revenue_label.text()
            
            writer.writerow(["Gaming Revenue", gaming_revenue])
            writer.writerow(["Food & Services Revenue", food_revenue])
            writer.writerow(["Total Revenue", total_revenue])
    
    def export_usage_statistics(self, directory, start_date, end_date):
        """Export usage statistics to CSV."""
        import csv
        
        filename = f"{directory}/usage_statistics_{start_date}_to_{end_date}.csv"
        
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header
            writer.writerow(["Statistic", "Value"])
            
            # Write data
            total_sessions = self.total_sessions_label.text()
            total_users = self.total_users_label.text()
            total_hours = self.total_hours_label.text()
            avg_duration = self.avg_duration_label.text()
            
            writer.writerow(["Total Sessions", total_sessions])
            writer.writerow(["Total Users", total_users])
            writer.writerow(["Total Hours", total_hours])
            writer.writerow(["Average Session Duration", avg_duration])
    
    def refresh_data(self):
        """Refresh data in the tab."""
        # Generate reports for the current date range
        self.generate_reports() 