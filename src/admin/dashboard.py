from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, 
    QFrame, QSizePolicy, QSpacerItem, QTableWidgetItem
)
from PyQt5.QtCore import Qt, QTimer, QDate
from PyQt5.QtGui import QFont, QColor

from src.common import (
    HeaderLabel, SubHeaderLabel, Card, StyledTable, 
    PrimaryButton, create_spacer, PCStatusWidget
)
from src.database import db, PC, Session, Order
from src.utils.helpers import format_currency, format_time

class DashboardTab(QWidget):
    """Dashboard tab for the admin panel."""
    
    def __init__(self):
        """Initialize the dashboard tab."""
        super().__init__()
        
        self.init_ui()
        self.refresh_data()
    
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
        
        title = QLabel("Dashboard")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setStyleSheet("color: #00c3ff;")
        header_layout.addWidget(title)
        
        main_layout.addWidget(header)

        # Main content and sidebar layout
        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)
        
        # Left main content area
        left_content = QVBoxLayout()
        left_content.setSpacing(20)
        
        # Stats cards
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)
        
        # PC Status Card
        self.pc_status_card = Card()
        pc_status_layout = QVBoxLayout()
        pc_status_layout.setContentsMargins(0, 0, 0, 0)
        
        pc_status_header = SubHeaderLabel("PC Status")
        pc_status_layout.addWidget(pc_status_header)
        
        self.occupied_label = QLabel("Occupied: 0")
        self.available_label = QLabel("Available: 0")
        self.maintenance_label = QLabel("Maintenance: 0")
        
        pc_status_layout.addWidget(self.occupied_label)
        pc_status_layout.addWidget(self.available_label)
        pc_status_layout.addWidget(self.maintenance_label)
        
        self.pc_status_card.layout.addLayout(pc_status_layout)
        stats_layout.addWidget(self.pc_status_card, 1)
        
        # Active Sessions Card
        self.sessions_card = Card()
        sessions_layout = QVBoxLayout()
        sessions_layout.setContentsMargins(0, 0, 0, 0)
        
        sessions_header = SubHeaderLabel("Active Sessions")
        sessions_layout.addWidget(sessions_header)
        
        self.active_sessions_label = QLabel("Active Sessions: 0")
        self.total_time_label = QLabel("Total Play Time: 0h 0m")
        
        sessions_layout.addWidget(self.active_sessions_label)
        sessions_layout.addWidget(self.total_time_label)
        
        self.sessions_card.layout.addLayout(sessions_layout)
        stats_layout.addWidget(self.sessions_card, 1)
        
        # Revenue Card
        self.revenue_card = Card()
        revenue_layout = QVBoxLayout()
        revenue_layout.setContentsMargins(0, 0, 0, 0)
        
        revenue_header = SubHeaderLabel("Today's Revenue")
        revenue_layout.addWidget(revenue_header)
        
        self.gaming_revenue_label = QLabel("Gaming: $0.00")
        self.food_revenue_label = QLabel("Food & Services: $0.00")
        self.total_revenue_label = QLabel("Total: $0.00")
        self.total_revenue_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        
        revenue_layout.addWidget(self.gaming_revenue_label)
        revenue_layout.addWidget(self.food_revenue_label)
        revenue_layout.addWidget(self.total_revenue_label)
        
        self.revenue_card.layout.addLayout(revenue_layout)
        stats_layout.addWidget(self.revenue_card, 1)
        
        # Registrations Card
        self.registrations_card = Card()
        registrations_layout = QVBoxLayout()
        registrations_layout.setContentsMargins(0, 0, 0, 0)
        
        registrations_header = SubHeaderLabel("Registrations")
        registrations_layout.addWidget(registrations_header)
        
        self.today_registrations_label = QLabel("Today: 0")
        self.week_registrations_label = QLabel("This Week: 0")
        self.month_registrations_label = QLabel("This Month: 0")
        
        registrations_layout.addWidget(self.today_registrations_label)
        registrations_layout.addWidget(self.week_registrations_label)
        registrations_layout.addWidget(self.month_registrations_label)
        
        self.registrations_card.layout.addLayout(registrations_layout)
        stats_layout.addWidget(self.registrations_card, 1)
        
        main_layout.addLayout(stats_layout)
        
        # Create main content areas with right sidebar
        main_content_layout = QHBoxLayout()
        
        # Left main content area (for reports, activity, etc.)
        left_area = QVBoxLayout()
        left_area.setSpacing(20)
        
        # Recent Activity
        activity_card = Card()
        activity_layout = QVBoxLayout()
        activity_layout.setContentsMargins(0, 0, 0, 0)
        
        activity_header = SubHeaderLabel("Recent Activity")
        activity_layout.addWidget(activity_header)
        
        # Activity table
        self.activity_table = StyledTable()
        self.activity_table.setColumnCount(4)
        self.activity_table.setHorizontalHeaderLabels(["Time", "Type", "Details", "Status"])

        self.activity_table.horizontalHeader().setStyleSheet("""
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

        self.activity_table.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)
        self.activity_table.horizontalHeader().setFixedHeight(50)
        
        activity_layout.addWidget(self.activity_table)
        activity_card.layout.addLayout(activity_layout)
        
        left_area.addWidget(activity_card)
        
        # Right sidebar for PC Status
        right_sidebar = QVBoxLayout()
        right_sidebar.setSpacing(15)
        
        # PC Status sidebar card
        pc_sidebar_card = Card()
        pc_sidebar_layout = QVBoxLayout()
        pc_sidebar_layout.setContentsMargins(0, 0, 0, 0)
        
        pc_sidebar_header = SubHeaderLabel("PC Status")
        pc_sidebar_header.setAlignment(Qt.AlignCenter)
        pc_sidebar_layout.addWidget(pc_sidebar_header)
        
        # PC Grid in a more compact format
        self.pc_grid = QGridLayout()
        self.pc_grid.setSpacing(8)
        pc_sidebar_layout.addLayout(self.pc_grid)
        
        pc_sidebar_card.layout.addLayout(pc_sidebar_layout)
        right_sidebar.addWidget(pc_sidebar_card)
        
        # Add a stretch to push the PC grid to the top
        right_sidebar.addStretch()
        
        # Add left and right areas to main content layout
        main_content_layout.addLayout(left_area, 7)  # 70% width
        main_content_layout.addLayout(right_sidebar, 3)  # 30% width
        
        main_layout.addLayout(main_content_layout)
    
    def refresh_data(self):
        """Refresh all data in the dashboard."""
        self.refresh_stats()
        self.refresh_pc_grid()
        self.refresh_activity_table()
    
    def refresh_stats(self):
        """Refresh all statistics."""
        self.refresh_pc_status()
        self.refresh_sessions_data()
        self.refresh_revenue_data()
        self.refresh_registrations_data()
    
    def refresh_pc_status(self):
        """Refresh PC status statistics."""
        cursor = db.get_cursor()
        try:
            # Get PC counts by status
            query = """
            SELECT 
                SUM(CASE WHEN status = 'occupied' THEN 1 ELSE 0 END) as occupied,
                SUM(CASE WHEN status = 'available' THEN 1 ELSE 0 END) as available,
                SUM(CASE WHEN status = 'maintenance' THEN 1 ELSE 0 END) as maintenance
            FROM pcs
            """
            cursor.execute(query)
            result = cursor.fetchone()
            
            if result:
                self.occupied_label.setText(f"Occupied: {result['occupied'] or 0}")
                self.available_label.setText(f"Available: {result['available'] or 0}")
                self.maintenance_label.setText(f"Maintenance: {result['maintenance'] or 0}")
        finally:
            cursor.close()
    
    def refresh_sessions_data(self):
        """Refresh active sessions data."""
        cursor = db.get_cursor()
        try:
            # Get active sessions count
            query = "SELECT COUNT(*) as count FROM sessions WHERE status = 'active'"
            cursor.execute(query)
            result = cursor.fetchone()
            
            if result:
                self.active_sessions_label.setText(f"Active Sessions: {result['count'] or 0}")
            
            # Get total play time
            query = """
            SELECT SUM(duration_minutes) as total_minutes 
            FROM sessions 
            WHERE status = 'active'
            """
            cursor.execute(query)
            result = cursor.fetchone()
            
            if result and result['total_minutes']:
                hours = result['total_minutes'] // 60
                minutes = result['total_minutes'] % 60
                self.total_time_label.setText(f"Total Play Time: {hours}h {minutes}m")
            else:
                self.total_time_label.setText("Total Play Time: 0h 0m")
        finally:
            cursor.close()
    
    def refresh_revenue_data(self):
        """Refresh revenue data."""
        cursor = db.get_cursor()
        try:
            today = QDate.currentDate().toString(Qt.ISODate)
            
            # Get gaming revenue
            query = """
            SELECT SUM(payment_amount) as total 
            FROM sessions 
            WHERE DATE(start_time) = %s
            """
            cursor.execute(query, (today,))
            result = cursor.fetchone()
            
            gaming_revenue = result['total'] or 0
            self.gaming_revenue_label.setText(f"Gaming: {format_currency(gaming_revenue)}")
            
            # Get food & services revenue
            query = """
            SELECT SUM(total_amount) as total 
            FROM orders 
            WHERE DATE(order_time) = %s
            """
            cursor.execute(query, (today,))
            result = cursor.fetchone()
            
            food_revenue = result['total'] or 0
            self.food_revenue_label.setText(f"Food & Services: {format_currency(food_revenue)}")
            
            # Calculate total
            total_revenue = gaming_revenue + food_revenue
            self.total_revenue_label.setText(f"Total: {format_currency(total_revenue)}")
        finally:
            cursor.close()
    
    def refresh_registrations_data(self):
        """Refresh registrations data."""
        cursor = db.get_cursor()
        try:
            today = QDate.currentDate().toString(Qt.ISODate)
            
            # Get today's registrations
            query = """
            SELECT COUNT(*) as count 
            FROM users 
            WHERE DATE(created_at) = %s
            """
            cursor.execute(query, (today,))
            result = cursor.fetchone()
            
            self.today_registrations_label.setText(f"Today: {result['count'] or 0}")
            
            # Get this week's registrations
            query = """
            SELECT COUNT(*) as count 
            FROM users 
            WHERE YEARWEEK(created_at, 1) = YEARWEEK(CURDATE(), 1)
            """
            cursor.execute(query)
            result = cursor.fetchone()
            
            self.week_registrations_label.setText(f"This Week: {result['count'] or 0}")
            
            # Get this month's registrations
            query = """
            SELECT COUNT(*) as count 
            FROM users 
            WHERE YEAR(created_at) = YEAR(CURDATE()) AND MONTH(created_at) = MONTH(CURDATE())
            """
            cursor.execute(query)
            result = cursor.fetchone()
            
            self.month_registrations_label.setText(f"This Month: {result['count'] or 0}")
        finally:
            cursor.close()
    
    def refresh_pc_grid(self):
        """Refresh PC grid."""
        # Clear existing widgets
        while self.pc_grid.count():
            item = self.pc_grid.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        # Get all PCs
        pcs = PC.get_all()
        
        # Add PC widgets to grid
        row, col = 0, 0
        max_cols = 3  # Fewer PCs per row for the sidebar
        
        for pc in pcs:
            # Create a smaller PC status widget
            pc_widget = PCStatusWidget(pc.pc_number, pc.status)
            pc_widget.setFixedSize(60, 60)  # Smaller size for sidebar
            pc_widget.clicked.connect(self.on_pc_clicked)
            
            self.pc_grid.addWidget(pc_widget, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
    
    def refresh_activity_table(self):
        """Refresh recent activity table."""
        cursor = db.get_cursor()
        try:
            # Clear existing rows
            self.activity_table.setRowCount(0)
            
            # Get recent sessions
            query = """
            SELECT 
                s.id, 
                s.start_time, 
                'Session' as type,
                CONCAT('User: ', u.name, ', PC: ', p.pc_number) as details,
                s.status
            FROM sessions s
            JOIN users u ON s.user_id = u.id
            JOIN pcs p ON s.pc_id = p.id
            ORDER BY s.start_time DESC
            LIMIT 5
            """
            cursor.execute(query)
            sessions = cursor.fetchall()
            
            # Get recent orders
            query = """
            SELECT 
                o.id, 
                o.order_time, 
                'Order' as type,
                CONCAT('PC: ', p.pc_number, ', Items: ', COUNT(oi.id)) as details,
                o.status
            FROM orders o
            JOIN sessions s ON o.session_id = s.id
            JOIN pcs p ON s.pc_id = p.id
            JOIN order_items oi ON o.id = oi.order_id
            GROUP BY o.id
            ORDER BY o.order_time DESC
            LIMIT 5
            """
            cursor.execute(query)
            orders = cursor.fetchall()
            
            # Combine and sort
            activities = sorted(
                sessions + orders,
                key=lambda x: x['start_time'] if 'start_time' in x else x['order_time'],
                reverse=True
            )[:10]  # Get top 10
            
            # Add to table
            for i, activity in enumerate(activities):
                self.activity_table.insertRow(i)
                
                # Time
                time_str = activity['start_time'].strftime("%H:%M:%S") if 'start_time' in activity else activity['order_time'].strftime("%H:%M:%S")
                self.activity_table.setItem(i, 0, QTableWidgetItem(time_str))
                
                # Type
                self.activity_table.setItem(i, 1, QTableWidgetItem(activity['type']))
                
                # Details
                details = activity['details']
                # Convert bytearray to string if needed
                if isinstance(details, bytearray):
                    details = details.decode('utf-8')
                self.activity_table.setItem(i, 2, QTableWidgetItem(details))
                
                # Status
                status_item = QTableWidgetItem(activity['status'].capitalize())
                
                # Color code status
                if activity['status'] == 'active' or activity['status'] == 'delivered':
                    status_item.setForeground(QColor('#2ecc71'))  # Green
                elif activity['status'] == 'pending' or activity['status'] == 'preparing':
                    status_item.setForeground(QColor('#f39c12'))  # Yellow
                elif activity['status'] == 'paused':
                    status_item.setForeground(QColor('#3498db'))  # Blue
                elif activity['status'] == 'terminated' or activity['status'] == 'cancelled':
                    status_item.setForeground(QColor('#e74c3c'))  # Red
                
                self.activity_table.setItem(i, 3, status_item)
        finally:
            cursor.close()
    
    def on_pc_clicked(self, pc_number):
        """Handle PC widget click."""
        # Switch to Sessions tab and focus on the selected PC
        main_window = self.window()
        if main_window:
            tab_widget = main_window.findChild(QTabWidget)
            if tab_widget:
                # Switch to Sessions tab (index 2)
                tab_widget.setCurrentIndex(2)
                
                # Focus on the selected PC
                sessions_tab = tab_widget.widget(2)
                if hasattr(sessions_tab, 'select_pc'):
                    sessions_tab.select_pc(pc_number) 