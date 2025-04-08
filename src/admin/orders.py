from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, 
    QFrame, QSizePolicy, QSpacerItem, QTableWidgetItem, QMessageBox,
    QDialog, QComboBox, QLineEdit, QPushButton, QListWidget, QListWidgetItem,
    QDialogButtonBox, QHeaderView
)
from PyQt5.QtCore import Qt, QTimer, QDateTime
from PyQt5.QtGui import QFont, QColor, QIcon

from src.common import (
    HeaderLabel, SubHeaderLabel, Card, StyledTable, StyledLineEdit,
    StyledComboBox, PrimaryButton, SecondaryButton, DangerButton, SuccessButton,
    show_message, confirm_action, create_spacer
)
from src.database import db, Order, MenuItem
from src.utils.helpers import format_currency, format_datetime

class OrderDetailsDialog(QDialog):
    """Dialog for viewing order details."""
    
    def __init__(self, order_id, parent=None):
        super().__init__(parent)
        
        self.order_id = order_id
        self.order = Order.get_by_id(order_id)
        
        if not self.order:
            show_message(parent, "Error", "Order not found.", QMessageBox.Critical)
            self.reject()
            return
        
        self.setWindowTitle(f"Order #{order_id} Details")
        self.setMinimumWidth(500)
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        # Order info
        info_layout = QGridLayout()
        
        # PC Number and User
        info_layout.addWidget(QLabel("PC Number:"), 0, 0)
        info_layout.addWidget(QLabel(f"PC {self.order.pc_number}"), 0, 1)
        
        info_layout.addWidget(QLabel("User:"), 1, 0)
        info_layout.addWidget(QLabel(self.order.user_name), 1, 1)
        
        # Order time
        info_layout.addWidget(QLabel("Order Time:"), 2, 0)
        info_layout.addWidget(QLabel(format_datetime(self.order.order_time)), 2, 1)
        
        # Status
        info_layout.addWidget(QLabel("Status:"), 3, 0)
        status_label = QLabel(self.order.status.capitalize())
        
        # Color code status
        if self.order.status == 'ready':
            status_label.setStyleSheet("color: #e67e22;")  # Orange
        elif self.order.status == 'delivered':
            status_label.setStyleSheet("color: #2ecc71;")  # Green
        elif self.order.status == 'preparing':
            status_label.setStyleSheet("color: #f39c12;")  # Yellow
        elif self.order.status == 'pending':
            status_label.setStyleSheet("color: #3498db;")  # Blue
        elif self.order.status == 'cancelled':
            status_label.setStyleSheet("color: #e74c3c;")  # Red
        
        info_layout.addWidget(status_label, 3, 1)
        
        # Delivery time (if delivered)
        if self.order.status == 'delivered' and self.order.delivery_time:
            info_layout.addWidget(QLabel("Delivery Time:"), 4, 0)
            info_layout.addWidget(QLabel(format_datetime(self.order.delivery_time)), 4, 1)
        
        layout.addLayout(info_layout)
        
        # Order items
        items_header = SubHeaderLabel("Order Items")
        layout.addWidget(items_header)
        
        items_table = StyledTable()
        items_table.setColumnCount(5)
        items_table.setHorizontalHeaderLabels(["Item", "Category", "Quantity", "Extras/Takeouts", "Price"])
        
        # Add items to table
        for i, item in enumerate(self.order.items):
            items_table.insertRow(i)
            
            items_table.setItem(i, 0, QTableWidgetItem(item['name']))
            items_table.setItem(i, 1, QTableWidgetItem(item['category'].capitalize()))
            items_table.setItem(i, 2, QTableWidgetItem(str(item['quantity'])))
            
            # Display extras and takeouts
            extras_takeouts_text = ""
            
            # Add extras with prices if any
            if 'extras' in item and item['extras']:
                extras_names = [f"{extra['name']} (+{format_currency(extra['price'])})" for extra in item['extras']]
                extras_takeouts_text += "Extras: " + ", ".join(extras_names)
            
            # Add takeouts if any
            if 'takeouts' in item and item['takeouts']:
                if extras_takeouts_text:
                    extras_takeouts_text += "\n"
                takeouts_names = [takeout['name'] for takeout in item['takeouts']]
                extras_takeouts_text += "Takeouts: " + ", ".join(takeouts_names)
            
            # If no extras or takeouts
            if not extras_takeouts_text:
                extras_takeouts_text = "-"
                
            extras_item = QTableWidgetItem(extras_takeouts_text)
            extras_item.setToolTip(extras_takeouts_text)  # Add tooltip to show full text on hover
            items_table.setItem(i, 3, extras_item)
            
            # Calculate item total
            item_total = item['price'] * item['quantity']
            
            # Add extras cost if any
            if 'extras' in item and item['extras']:
                for extra in item['extras']:
                    item_total += extra['price'] * item['quantity']
            
            items_table.setItem(i, 4, QTableWidgetItem(format_currency(item_total)))
        
        # Adjust the column widths
        items_table.horizontalHeader().setStretchLastSection(False)
        items_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)  # Item name stretches
        items_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)  # Extras/Takeouts stretches
        
        # Enable text wrapping and adjust row heights
        items_table.setWordWrap(True)
        for i in range(items_table.rowCount()):
            items_table.resizeRowToContents(i)
        
        layout.addWidget(items_table)
        
        # Total
        total_label = QLabel(f"Total: {format_currency(self.order.total_amount)}")
        total_label.setStyleSheet("font-weight: bold; font-size: 16px; margin-top: 10px;")
        layout.addWidget(total_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        close_button = SecondaryButton("Close")
        close_button.clicked.connect(self.reject)
        
        # Add status change buttons if not delivered or cancelled
        if self.order.status not in ('delivered', 'cancelled'):
            if self.order.status == 'pending':
                prepare_button = PrimaryButton("Mark as Preparing")
                prepare_button.clicked.connect(self.mark_as_preparing)
                button_layout.addWidget(prepare_button)
            
            if self.order.status in ('pending', 'preparing'):
                ready_button = PrimaryButton("Mark as Ready")
                ready_button.clicked.connect(self.mark_as_ready)
                button_layout.addWidget(ready_button)
                
                deliver_button = SuccessButton("Mark as Delivered")
                deliver_button.clicked.connect(self.mark_as_delivered)
                button_layout.addWidget(deliver_button)
                
                cancel_button = DangerButton("Cancel Order")
                cancel_button.clicked.connect(self.cancel_order)
                button_layout.addWidget(cancel_button)

            if self.order.status == 'ready':
                deliver_button = SuccessButton("Mark as Delivered")
                deliver_button.clicked.connect(self.mark_as_delivered)
                button_layout.addWidget(deliver_button)
        
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
    
    def mark_as_preparing(self):
        """Mark the order as preparing."""
        try:
            self.order.update_status('preparing')
            show_message(self, "Success", "Order marked as preparing.")
            self.accept()
        except Exception as e:
            show_message(self, "Error", f"Failed to update order: {str(e)}", QMessageBox.Critical)
    
    def mark_as_delivered(self):
        """Mark the order as delivered."""
        try:
            self.order.update_status('delivered')
            show_message(self, "Success", "Order marked as delivered.")
            self.accept()
        except Exception as e:
            show_message(self, "Error", f"Failed to update order: {str(e)}", QMessageBox.Critical)
    
    def cancel_order(self):
        """Cancel the order."""
        if confirm_action("Cancel Order", "Are you sure you want to cancel this order?", self):
            try:
                self.order.update_status('cancelled')
                show_message(self, "Success", "Order cancelled.")
                self.accept()
            except Exception as e:
                show_message(self, "Error", f"Failed to cancel order: {str(e)}", QMessageBox.Critical)

    def mark_as_ready(self):
        """Mark the order as ready."""
        try:
            self.order.update_status('ready')
            show_message(self, "Success", "Order marked as ready.", QMessageBox.Information)
            self.accept()
        except Exception as e:
            show_message(self, "Error", f"Failed to update order: {str(e)}", QMessageBox.Critical)

class OrdersTab(QWidget):
    """Orders tab for the admin panel."""
    
    def __init__(self):
        """Initialize the orders tab."""
        super().__init__()
        
        self.init_ui()
        self.refresh_data()
        
        # Set up timer for auto-refresh
        self.timer = QTimer(self)
        self.timer.timeout.connect(lambda: self.refresh_data())
        self.timer.start(5000)  # Refresh every 5 seconds
    
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
        
        title = QLabel("Food & Extra Service Orders")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setStyleSheet("color: #00c3ff;")
        header_layout.addWidget(title)
        
        main_layout.addWidget(header)
        
        # Pending Orders
        pending_card = Card()
        pending_layout = QVBoxLayout()
        pending_layout.setContentsMargins(0, 0, 0, 0)
        
        pending_header = SubHeaderLabel("Pending & Preparing Orders")
        pending_layout.addWidget(pending_header)
        
        self.pending_table = StyledTable()
        self.pending_table.setColumnCount(6)
        self.pending_table.setHorizontalHeaderLabels([
            "Order #", "PC", "User", "Time", "Items", "Status"
        ])

        self.pending_table.horizontalHeader().setStyleSheet("""
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

        self.pending_table.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)
        self.pending_table.horizontalHeader().setFixedHeight(50)
        
        # Double-click to view details
        self.pending_table.cellDoubleClicked.connect(self.view_order_details)
        
        pending_layout.addWidget(self.pending_table)
        pending_card.layout.addLayout(pending_layout)
        
        main_layout.addWidget(pending_card)
        
        # Order History
        history_card = Card()
        history_layout = QVBoxLayout()
        history_layout.setContentsMargins(0, 0, 0, 0)
        
        history_header = SubHeaderLabel("Order History")
        history_layout.addWidget(history_header)
        
        self.history_table = StyledTable()
        self.history_table.setColumnCount(7)
        self.history_table.setHorizontalHeaderLabels([
            "Order #", "PC", "User", "Order Time", "Delivery Time", "Total", "Status"
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
        
        # Double-click to view details
        self.history_table.cellDoubleClicked.connect(self.view_order_details)
        
        history_layout.addWidget(self.history_table)
        history_card.layout.addLayout(history_layout)
        
        main_layout.addWidget(history_card)
        
        # Add spacer at the bottom
        main_layout.addItem(create_spacer())
    
    def refresh_data(self):
        """Refresh data in the tab."""
        self.refresh_pending_orders()
        self.refresh_order_history()
    
    def refresh_pending_orders(self):
        """Refresh pending orders table."""
        # Get pending orders
        orders = Order.get_pending_orders()
        
        # Clear existing rows
        self.pending_table.setRowCount(0)
        
        # Add to table
        for i, order in enumerate(orders):
            self.pending_table.insertRow(i)
            
            # Order #
            order_id_item = QTableWidgetItem(str(order.id))
            order_id_item.setData(Qt.UserRole, order.id)  # Store order ID for double-click
            self.pending_table.setItem(i, 0, order_id_item)
            
            # PC
            self.pending_table.setItem(i, 1, QTableWidgetItem(f"PC {order.pc_number}"))
            
            # User
            self.pending_table.setItem(i, 2, QTableWidgetItem(order.user_name))
            
            # Time
            order_time = order.order_time.strftime("%H:%M:%S")
            self.pending_table.setItem(i, 3, QTableWidgetItem(order_time))
            
            # Items with extras and takeouts
            items_text_parts = []
            for item in order.items:
                item_text = f"{item['quantity']} x {item['name']}"
                
                # Add extras summary if any
                if 'extras' in item and item['extras']:
                    extras_count = len(item['extras'])
                    item_text += f" (+{extras_count} extras)"
                
                # Add takeouts summary if any
                if 'takeouts' in item and item['takeouts']:
                    takeouts_count = len(item['takeouts'])
                    item_text += f" (-{takeouts_count} takeouts)"
                
                items_text_parts.append(item_text)
            
            items_text = ", ".join(items_text_parts)
            items_item = QTableWidgetItem(items_text)
            items_item.setToolTip(items_text)  # Add tooltip to show full text on hover
            self.pending_table.setItem(i, 4, items_item)
            
            # Status
            status_item = QTableWidgetItem(order.status.capitalize())
            
            # Color code status
            if order.status == 'preparing':
                status_item.setForeground(QColor('#f39c12'))  # Yellow
            elif order.status == 'pending':
                status_item.setForeground(QColor('#3498db'))  # Blue
            elif order.status == 'ready':
                status_item.setForeground(QColor('#e67e22'))  # Orange
            
            self.pending_table.setItem(i, 5, status_item)
        
        # Enable text wrapping and auto-adjust row heights
        self.pending_table.setWordWrap(True)
        for i in range(self.pending_table.rowCount()):
            self.pending_table.resizeRowToContents(i)
    
    def refresh_order_history(self):
        """Refresh order history table."""
        cursor = db.get_cursor()
        try:
            # Clear existing rows
            self.history_table.setRowCount(0)
            
            # Get completed orders
            query = """
            SELECT 
                o.id,
                p.pc_number,
                u.name as user_name,
                o.order_time,
                o.delivery_time,
                o.total_amount,
                o.status
            FROM orders o
            JOIN sessions s ON o.session_id = s.id
            JOIN users u ON s.user_id = u.id
            JOIN pcs p ON s.pc_id = p.id
            WHERE o.status IN ('delivered', 'cancelled')
            ORDER BY o.order_time DESC
            LIMIT 20
            """
            cursor.execute(query)
            results = cursor.fetchall()
            
            # Add to table
            for i, result in enumerate(results):
                self.history_table.insertRow(i)
                
                # Order #
                order_id_item = QTableWidgetItem(str(result['id']))
                order_id_item.setData(Qt.UserRole, result['id'])  # Store order ID for double-click
                self.history_table.setItem(i, 0, order_id_item)
                
                # PC
                self.history_table.setItem(i, 1, QTableWidgetItem(f"PC {result['pc_number']}"))
                
                # User
                self.history_table.setItem(i, 2, QTableWidgetItem(result['user_name']))
                
                # Order Time
                order_time = result['order_time'].strftime("%H:%M:%S")
                self.history_table.setItem(i, 3, QTableWidgetItem(order_time))
                
                # Delivery Time
                delivery_time = result['delivery_time'].strftime("%H:%M:%S") if result['delivery_time'] else "-"
                self.history_table.setItem(i, 4, QTableWidgetItem(delivery_time))
                
                # Total
                self.history_table.setItem(i, 5, QTableWidgetItem(format_currency(result['total_amount'])))
                
                # Status
                status_item = QTableWidgetItem(result['status'].capitalize())
                
                # Color code status
                if result['status'] == 'delivered':
                    status_item.setForeground(QColor('#2ecc71'))  # Green
                elif result['status'] == 'cancelled':
                    status_item.setForeground(QColor('#e74c3c'))  # Red
                
                self.history_table.setItem(i, 6, status_item)
        finally:
            cursor.close()
    
    def view_order_details(self, row, column):
        """View order details when a row is double-clicked."""
        # Get the order ID from the first column
        table = self.sender()
        order_id_item = table.item(row, 0)
        
        if order_id_item:
            order_id = order_id_item.data(Qt.UserRole)
            
            # Show order details dialog
            dialog = OrderDetailsDialog(order_id, self)
            if dialog.exec_():
                # Refresh data if order was updated
                self.refresh_data() 