from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, 
    QFrame, QSizePolicy, QSpacerItem, QTableWidgetItem, QMessageBox, QInputDialog, QDialog, QDialogButtonBox
)
from PyQt5.QtCore import Qt, QTimer, QDate
from PyQt5.QtGui import QFont, QColor

from src.common import (
    HeaderLabel, SubHeaderLabel, Card, StyledTable, StyledLineEdit,
    StyledComboBox, PrimaryButton, SecondaryButton, DangerButton, SuccessButton,
    show_message, confirm_action, create_spacer, PCStatusWidget
)
from src.database import db, User, PC, Session
from src.utils.helpers import (
    format_currency, format_time, get_duration_options, 
    get_payment_methods, calculate_price_for_duration
)

class RegistrationTab(QWidget):
    """Registration tab for the admin panel."""
    
    def __init__(self):
        """Initialize the registration tab."""
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
        
        title = QLabel("User Registration & PC Assignment")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setStyleSheet("color: #00c3ff;")
        header_layout.addWidget(title)
        
        main_layout.addWidget(header)

        # Registration form and PC grid
        form_pc_layout = QHBoxLayout()
        form_pc_layout.setSpacing(20)
        
        # Registration form
        registration_card = Card()
        registration_layout = QVBoxLayout()
        registration_layout.setContentsMargins(0, 0, 0, 0)
        
        form_header = SubHeaderLabel("Register New User")
        registration_layout.addWidget(form_header)
        
        # Form fields
        form_grid = QGridLayout()
        form_grid.setColumnStretch(1, 1)
        form_grid.setVerticalSpacing(15)
        form_grid.setHorizontalSpacing(10)
        
        # Name
        name_label = QLabel("Name:")
        self.name_input = StyledLineEdit(placeholder="Enter user name")
        form_grid.addWidget(name_label, 0, 0)
        form_grid.addWidget(self.name_input, 0, 1)
        
        # Civil ID
        civil_id_label = QLabel("Civil ID:")
        self.civil_id_input = StyledLineEdit(placeholder="Enter civil ID number")
        form_grid.addWidget(civil_id_label, 1, 0)
        form_grid.addWidget(self.civil_id_input, 1, 1)
        
        # Phone
        phone_label = QLabel("Phone:")
        self.phone_input = StyledLineEdit(placeholder="Enter phone number")
        form_grid.addWidget(phone_label, 2, 0)
        form_grid.addWidget(self.phone_input, 2, 1)
        
        # Duration
        duration_label = QLabel("Duration:")
        self.duration_combo = StyledComboBox()
        
        # Add duration options
        for option in get_duration_options():
            self.duration_combo.addItem(
                f"{option['label']} - {format_currency(option['price'])}",
                option['value']
            )
        
        form_grid.addWidget(duration_label, 3, 0)
        form_grid.addWidget(self.duration_combo, 3, 1)
        
        # Payment Method
        payment_label = QLabel("Payment Method:")
        self.payment_combo = StyledComboBox()
        
        # Add payment methods
        for method in get_payment_methods():
            self.payment_combo.addItem(method)
        
        form_grid.addWidget(payment_label, 4, 0)
        form_grid.addWidget(self.payment_combo, 4, 1)
        
        # PC Selection
        pc_label = QLabel("PC Number:")
        self.pc_combo = StyledComboBox()
        
        # PC options will be populated in refresh_data
        
        form_grid.addWidget(pc_label, 5, 0)
        form_grid.addWidget(self.pc_combo, 5, 1)
        
        # Add form grid to layout
        registration_layout.addLayout(form_grid)
        
        # Price display
        self.price_label = QLabel("Total Price: $0.00")
        self.price_label.setStyleSheet("font-weight: bold; font-size: 16px; margin-top: 10px;")
        registration_layout.addWidget(self.price_label)
        
        # Register button
        register_button = PrimaryButton("Register User & Assign PC")
        register_button.clicked.connect(self.register_user)
        registration_layout.addWidget(register_button)
        
        # Add to card
        registration_card.layout.addLayout(registration_layout)
        
        # Add to main layout
        form_pc_layout.addWidget(registration_card, 1)
        
        # PC Grid
        pc_grid_card = Card()
        pc_grid_layout = QVBoxLayout()
        pc_grid_layout.setContentsMargins(0, 0, 0, 0)
        
        pc_grid_header_layout = QHBoxLayout()
        pc_grid_header = SubHeaderLabel("PC Status")
        pc_grid_header_layout.addWidget(pc_grid_header)
        
        # Add PC button
        add_pc_button = PrimaryButton("Add PC")
        add_pc_button.setFixedWidth(100)
        add_pc_button.setFixedHeight(50)
        add_pc_button.clicked.connect(self.add_pc)
        pc_grid_header_layout.addWidget(add_pc_button)
        
        pc_grid_layout.addLayout(pc_grid_header_layout)
        
        self.pc_grid = QGridLayout()
        self.pc_grid.setSpacing(10)
        
        # PC widgets will be added in refresh_data
        
        pc_grid_layout.addLayout(self.pc_grid)
        pc_grid_card.layout.addLayout(pc_grid_layout)
        
        form_pc_layout.addWidget(pc_grid_card, 1)
        
        main_layout.addLayout(form_pc_layout)
        
        # Recent Registrations
        recent_card = Card()
        recent_layout = QVBoxLayout()
        recent_layout.setContentsMargins(0, 0, 0, 0)
        
        # recent_header = SubHeaderLabel("Recent Registrations")
        # recent_layout.addWidget(recent_header)
        
        self.recent_table = StyledTable()
        self.recent_table.setColumnCount(6)
        self.recent_table.setFixedHeight(200)
        self.recent_table.setHorizontalHeaderLabels([
            "Name", "Civil ID", "Phone", "PC", "Duration", "Payment Method"
        ])
        
        # Style the table headers
        self.recent_table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: rgba(0, 195, 255, 0.1);
                color: #00c3ff;
                padding: 0px;
                margin: 0px;
                border: none;
                font-size: 12px;
            }
        """)
        
        # Set header properties
        self.recent_table.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)
        self.recent_table.horizontalHeader().setFixedHeight(50)
        
        recent_layout.addWidget(self.recent_table)
        recent_card.layout.addLayout(recent_layout)
        
        main_layout.addWidget(recent_card)
        
        # Connect signals
        self.duration_combo.currentIndexChanged.connect(self.update_price)
        
        # Add spacer at the bottom
        main_layout.addItem(create_spacer())
    
    def refresh_data(self):
        """Refresh data in the tab."""
        self.refresh_pc_combo()
        self.refresh_pc_grid()
        self.refresh_recent_registrations()
        self.update_price()
    
    def refresh_pc_combo(self):
        """Refresh PC combo box with available PCs."""
        self.pc_combo.clear()
        
        # Get available PCs
        available_pcs = PC.get_available()
        
        if not available_pcs:
            self.pc_combo.addItem("No PCs available")
            return
        
        # Add PCs to combo box
        for pc in available_pcs:
            self.pc_combo.addItem(f"PC {pc.pc_number}", pc.id)
    
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
        max_cols = 4  # 4 PCs per row
        
        for pc in pcs:
            pc_widget = PCStatusWidget(pc.pc_number, pc.status)
            pc_widget.clicked.connect(self.on_pc_clicked)
            
            self.pc_grid.addWidget(pc_widget, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
    
    def refresh_recent_registrations(self):
        """Refresh recent registrations table."""
        cursor = db.get_cursor()
        try:
            # Clear existing rows
            self.recent_table.setRowCount(0)
            
            # Get recent sessions with user and PC info
            query = """
            SELECT 
                u.name, 
                u.civil_id, 
                u.phone, 
                p.pc_number, 
                s.duration_minutes, 
                s.payment_method
            FROM sessions s
            JOIN users u ON s.user_id = u.id
            JOIN pcs p ON s.pc_id = p.id
            ORDER BY s.start_time DESC
            LIMIT 10
            """
            cursor.execute(query)
            results = cursor.fetchall()
            
            # Add to table
            for i, result in enumerate(results):
                self.recent_table.insertRow(i)
                
                self.recent_table.setItem(i, 0, QTableWidgetItem(result['name']))
                self.recent_table.setItem(i, 1, QTableWidgetItem(result['civil_id']))
                self.recent_table.setItem(i, 2, QTableWidgetItem(result['phone']))
                self.recent_table.setItem(i, 3, QTableWidgetItem(str(result['pc_number'])))
                self.recent_table.setItem(i, 4, QTableWidgetItem(format_time(result['duration_minutes'])))
                self.recent_table.setItem(i, 5, QTableWidgetItem(result['payment_method']))
        finally:
            cursor.close()
    
    def update_price(self):
        """Update the displayed price based on selected duration."""
        if self.duration_combo.count() == 0:
            return
        
        # Get selected duration
        duration = self.duration_combo.currentData()
        
        # Calculate price
        price = calculate_price_for_duration(duration)
        
        # Update price label
        self.price_label.setText(f"Total Price: {format_currency(price)}")
    
    def register_user(self):
        """Register a new user and assign a PC."""
        # Get form values
        name = self.name_input.text().strip()
        civil_id = self.civil_id_input.text().strip()
        phone = self.phone_input.text().strip()

        try:
            # Check if user already exists
            existing_user = User.get_by_phone(phone)
            
            if existing_user:
                user_id = existing_user.id
                name, civil_id, phone = existing_user.name, existing_user.civil_id, existing_user.phone
            else:
                # Validate form
                if not name:
                    show_message(self, "Error", "Please enter a name.", QMessageBox.Warning)
                    self.name_input.setFocus()
                    return
                
                if not civil_id:
                    show_message(self, "Error", "Please enter a civil ID.", QMessageBox.Warning)
                    self.civil_id_input.setFocus()
                    return
                
                if not phone:
                    show_message(self, "Error", "Please enter a phone number.", QMessageBox.Warning)
                    self.phone_input.setFocus()
                    return
                
                # Create new user
                user_id = User.create(name, civil_id, phone)


            if self.pc_combo.count() == 0 or self.pc_combo.currentText() == "No PCs available":
                show_message(self, "Error", "No PCs available for assignment.", QMessageBox.Warning)
                return

            
            # Get selected values
            duration = self.duration_combo.currentData()
            payment_method = self.payment_combo.currentText()
            pc_id = self.pc_combo.currentData()
            
            # Calculate price
            price = calculate_price_for_duration(duration)
        
        
            
            # Create session
            session_id = Session.create(user_id, pc_id, duration, payment_method, price)
            
            # Show success message
            show_message(
                self, 
                "Success", 
                f"User registered and assigned to PC {self.pc_combo.currentText()}.\n"
                f"Session started for {format_time(duration)}.\n"
                f"Total: {format_currency(price)}"
            )
            
            # Clear form
            self.name_input.clear()
            self.civil_id_input.clear()
            self.phone_input.clear()
            
            # Refresh data
            self.refresh_data()
            
        except Exception as e:
            show_message(self, "Error", f"Failed to register user: {str(e)}", QMessageBox.Critical)
    
    def on_pc_clicked(self, pc_number):
        """Handle PC widget click."""
        # Find PC in combo box and select it
        for i in range(self.pc_combo.count()):
            if f"PC {pc_number}" == self.pc_combo.itemText(i):
                self.pc_combo.setCurrentIndex(i)
                break 
    
    def add_pc(self):
        """Handle adding a new PC."""
        # Create a dialog for entering PC number and specs
        dialog = QDialog(self)
        dialog.setWindowTitle("Add PC")
        layout = QVBoxLayout(dialog)

        # PC Number input
        pc_number_label = QLabel("Enter PC Number:")
        pc_number_input = StyledLineEdit()
        layout.addWidget(pc_number_label)
        layout.addWidget(pc_number_input)

        # PC Specs input
        pc_specs_label = QLabel("Enter PC Specs (optional):")
        pc_specs_input = StyledLineEdit()
        layout.addWidget(pc_specs_label)
        layout.addWidget(pc_specs_input)

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(button_box)

        # Connect buttons
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)

        # Show dialog
        if dialog.exec() == QDialog.Accepted:
            pc_number = pc_number_input.text().strip()
            pc_specs = pc_specs_input.text().strip()

            if not pc_number.isdigit() or int(pc_number) <= 0:
                show_message(self, "Error", "Invalid PC number.", QMessageBox.Warning)
                return

            pc_number = int(pc_number)

            # Check if PC number already exists
            if PC.get_by_number(pc_number):
                show_message(self, "Error", f"PC {pc_number} already exists.", QMessageBox.Warning)
                return

            try:
                # Create new PC with specs
                PC.create(pc_number, specs=pc_specs)
                show_message(self, "Success", f"PC {pc_number} added successfully.", QMessageBox.Information)

                # Refresh PC grid
                self.refresh_pc_grid()
            except Exception as e:
                show_message(self, "Error", f"Failed to add PC: {str(e)}", QMessageBox.Critical) 