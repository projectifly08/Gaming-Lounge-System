from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, 
    QFrame, QSizePolicy, QSpacerItem, QTableWidgetItem, QMessageBox,
    QDialog, QComboBox, QLineEdit, QPushButton, QListWidget, QListWidgetItem,
    QFileDialog, QCheckBox, QHeaderView
)
from PyQt5.QtCore import Qt, QTimer, QDateTime
from PyQt5.QtGui import QFont, QColor, QIcon, QPixmap

from src.common import (
    HeaderLabel, SubHeaderLabel, Card, StyledTable, StyledLineEdit,
    StyledComboBox, PrimaryButton, SecondaryButton, DangerButton, SuccessButton,
    show_message, confirm_action, create_spacer
)
from src.database import db, MenuItem
from src.utils.helpers import format_currency

class MenuItemDialog(QDialog):
    """Dialog for adding or editing a menu item."""
    
    def __init__(self, item_id=None, parent=None):
        super().__init__(parent)
        
        self.item_id = item_id
        self.item = None
        
        if item_id:
            self.item = MenuItem.get_by_id(item_id)
            if not self.item:
                show_message(parent, "Error", "Menu item not found.", QMessageBox.Critical)
                self.reject()
                return
            
            self.setWindowTitle("Edit Menu Item")
        else:
            self.setWindowTitle("Add Menu Item")
        
        self.setMinimumWidth(500)
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        # Form fields
        form_grid = QGridLayout()
        form_grid.setColumnStretch(1, 1)
        form_grid.setVerticalSpacing(15)
        form_grid.setHorizontalSpacing(10)
        
        # Name
        name_label = QLabel("Name:")
        self.name_input = StyledLineEdit(placeholder="Enter item name")
        form_grid.addWidget(name_label, 0, 0)
        form_grid.addWidget(self.name_input, 0, 1)
        
        # Description
        description_label = QLabel("Description:")
        self.description_input = StyledLineEdit(placeholder="Enter item description")
        form_grid.addWidget(description_label, 1, 0)
        form_grid.addWidget(self.description_input, 1, 1)
        
        # Price
        price_label = QLabel("Price:")
        self.price_input = StyledLineEdit(placeholder="Enter price (e.g. 5.99)")
        form_grid.addWidget(price_label, 2, 0)
        form_grid.addWidget(self.price_input, 2, 1)
        
        # Category
        category_label = QLabel("Category:")
        self.category_combo = StyledComboBox()
        
        # Add categories
        categories = ["food", "drink", "accessory", "service"]
        for category in categories:
            self.category_combo.addItem(category.capitalize(), category)
        
        form_grid.addWidget(category_label, 3, 0)
        form_grid.addWidget(self.category_combo, 3, 1)
        
        # Available
        available_label = QLabel("Available:")
        self.available_checkbox = QCheckBox()
        self.available_checkbox.setChecked(True)
        form_grid.addWidget(available_label, 4, 0)
        form_grid.addWidget(self.available_checkbox, 4, 1)
        
        # Image
        image_label = QLabel("Image:")
        self.image_path_input = StyledLineEdit(placeholder="Image path (optional)")
        self.image_path_input.setReadOnly(True)
        
        browse_button = SecondaryButton("Browse...")
        browse_button.clicked.connect(self.browse_image)
        
        image_layout = QHBoxLayout()
        image_layout.addWidget(self.image_path_input)
        image_layout.addWidget(browse_button)
        
        form_grid.addWidget(image_label, 5, 0)
        form_grid.addLayout(image_layout, 5, 1)
        
        layout.addLayout(form_grid)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        cancel_button = SecondaryButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        
        save_button = PrimaryButton("Save")
        save_button.clicked.connect(self.save_item)
        
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(save_button)
        
        layout.addLayout(button_layout)
        
        # Fill form if editing
        if self.item:
            self.name_input.setText(self.item.name)
            self.description_input.setText(self.item.description or "")
            self.price_input.setText(str(self.item.price))
            
            # Set category
            index = self.category_combo.findData(self.item.category)
            if index >= 0:
                self.category_combo.setCurrentIndex(index)
            
            self.available_checkbox.setChecked(self.item.available)
            
            if self.item.image_path:
                self.image_path_input.setText(self.item.image_path)
    
    def browse_image(self):
        """Browse for an image file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "", "Image Files (*.png *.jpg *.jpeg *.gif)"
        )
        
        if file_path:
            self.image_path_input.setText(file_path)
    
    def save_item(self):
        """Save the menu item."""
        # Validate form
        name = self.name_input.text().strip()
        description = self.description_input.text().strip()
        price_text = self.price_input.text().strip()
        category = self.category_combo.currentData()
        available = self.available_checkbox.isChecked()
        image_path = self.image_path_input.text().strip()
        
        if not name:
            show_message(self, "Error", "Please enter a name.", QMessageBox.Warning)
            self.name_input.setFocus()
            return
        
        try:
            price = float(price_text)
            if price <= 0:
                raise ValueError("Price must be positive")
        except ValueError:
            show_message(self, "Error", "Please enter a valid price.", QMessageBox.Warning)
            self.price_input.setFocus()
            return
        
        try:
            if self.item:
                # Update existing item
                self.item.name = name
                self.item.description = description
                self.item.price = price
                self.item.category = category
                self.item.available = available
                self.item.image_path = image_path if image_path else None
                
                self.item.update()
                show_message(self, "Success", "Menu item updated successfully.")
            else:
                # Create new item
                item_id = MenuItem.create(
                    name, description, price, category, 
                    image_path if image_path else None
                )
                show_message(self, "Success", "Menu item added successfully.")
            
            self.accept()
        except Exception as e:
            show_message(self, "Error", f"Failed to save menu item: {str(e)}", QMessageBox.Critical)

class MenuTab(QWidget):
    """Menu management tab for the admin panel."""
    
    def __init__(self):
        """Initialize the menu tab."""
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
        
        title = QLabel("Menu Management")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setStyleSheet("color: #00c3ff;")
        header_layout.addWidget(title)
        
        # Add Item Button
        add_button = QPushButton("Add New Menu Item")
        add_button.setStyleSheet("""
            QPushButton {
                background-color: #00c3ff;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00a5eb;
            }
        """)
        add_button.clicked.connect(self.add_menu_item)
        header_layout.addWidget(add_button)
        
        main_layout.addWidget(header)
        
        # Category Tabs
        categories_layout = QHBoxLayout()
        categories_layout.setSpacing(20)
        
        # Food Items
        food_card = Card()
        food_layout = QVBoxLayout()
        food_layout.setContentsMargins(0, 0, 0, 0)
        
        food_header = SubHeaderLabel("Food Items")
        food_layout.addWidget(food_header)
        
        self.food_table = StyledTable()
        self.food_table.setColumnCount(5)
        self.food_table.setHorizontalHeaderLabels([
            "Name", "Description", "Price", "Available", "Actions"
        ])

        self.food_table.horizontalHeader().setStyleSheet("""
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

        self.food_table.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)
        self.food_table.horizontalHeader().setFixedHeight(50)
        
        # Set column widths - make Actions column wider
        self.setup_table_columns(self.food_table)
        
        food_layout.addWidget(self.food_table)
        food_card.layout.addLayout(food_layout)
        
        categories_layout.addWidget(food_card)
        
        # Drink Items
        drink_card = Card()
        drink_layout = QVBoxLayout()
        drink_layout.setContentsMargins(0, 0, 0, 0)
        
        drink_header = SubHeaderLabel("Drink Items")
        drink_layout.addWidget(drink_header)
        
        self.drink_table = StyledTable()
        self.drink_table.setColumnCount(5)
        self.drink_table.setHorizontalHeaderLabels([
            "Name", "Description", "Price", "Available", "Actions"
        ])

        self.drink_table.horizontalHeader().setStyleSheet("""
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

        self.drink_table.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)
        self.drink_table.horizontalHeader().setFixedHeight(50)
        
        # Set column widths - make Actions column wider
        self.setup_table_columns(self.drink_table)
        
        drink_layout.addWidget(self.drink_table)
        drink_card.layout.addLayout(drink_layout)
        
        categories_layout.addWidget(drink_card)
        
        main_layout.addLayout(categories_layout)
        
        # Accessories and Services
        accessories_services_layout = QHBoxLayout()
        accessories_services_layout.setSpacing(20)
        
        # Accessories
        accessory_card = Card()
        accessory_layout = QVBoxLayout()
        accessory_layout.setContentsMargins(0, 0, 0, 0)
        
        accessory_header = SubHeaderLabel("Accessories")
        accessory_layout.addWidget(accessory_header)
        
        self.accessory_table = StyledTable()
        self.accessory_table.setColumnCount(5)
        self.accessory_table.setHorizontalHeaderLabels([
            "Name", "Description", "Price", "Available", "Actions"
        ])

        self.accessory_table.horizontalHeader().setStyleSheet("""
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

        self.accessory_table.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)
        self.accessory_table.horizontalHeader().setFixedHeight(50)
        
        # Set column widths - make Actions column wider
        self.setup_table_columns(self.accessory_table)
        
        accessory_layout.addWidget(self.accessory_table)
        accessory_card.layout.addLayout(accessory_layout)
        
        accessories_services_layout.addWidget(accessory_card)
        
        # Services
        service_card = Card()
        service_layout = QVBoxLayout()
        service_layout.setContentsMargins(0, 0, 0, 0)
        
        service_header = SubHeaderLabel("Services")
        service_layout.addWidget(service_header)
        
        self.service_table = StyledTable()
        self.service_table.setColumnCount(5)
        self.service_table.setHorizontalHeaderLabels([
            "Name", "Description", "Price", "Available", "Actions"
        ])

        self.service_table.horizontalHeader().setStyleSheet("""
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

        self.service_table.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)
        self.service_table.horizontalHeader().setFixedHeight(50)
        
        # Set column widths - make Actions column wider
        self.setup_table_columns(self.service_table)
        
        service_layout.addWidget(self.service_table)
        service_card.layout.addLayout(service_layout)
        
        accessories_services_layout.addWidget(service_card)
        
        main_layout.addLayout(accessories_services_layout)
        
        # Add spacer at the bottom
        main_layout.addItem(create_spacer())
    
    def setup_table_columns(self, table):
        """Set up column widths for a table."""
        # Make the Actions column wider
        table.horizontalHeader().setStretchLastSection(False)
        table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Fixed)
        table.setColumnWidth(4, 180)  # Set Actions column width to 180px
        
        # Set other columns to stretch
        for i in range(4):
            table.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)
    
    def refresh_data(self):
        """Refresh data in the tab."""
        self.refresh_category_table(self.food_table, "food")
        self.refresh_category_table(self.drink_table, "drink")
        self.refresh_category_table(self.accessory_table, "accessory")
        self.refresh_category_table(self.service_table, "service")
    
    def refresh_category_table(self, table, category):
        """Refresh a category table."""
        # Get items for the category
        items = MenuItem.get_by_category(category)
        
        # Clear existing rows
        table.setRowCount(0)
        
        # Add to table
        for i, item in enumerate(items):
            table.insertRow(i)
            
            # Name
            table.setItem(i, 0, QTableWidgetItem(item.name))
            
            # Description
            table.setItem(i, 1, QTableWidgetItem(item.description or ""))
            
            # Price
            table.setItem(i, 2, QTableWidgetItem(format_currency(item.price)))
            
            # Available
            available_item = QTableWidgetItem("Yes" if item.available else "No")
            if not item.available:
                available_item.setForeground(QColor('#e74c3c'))  # Red
            table.setItem(i, 3, available_item)
            
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(2, 0, 2, 0)  # Reduced horizontal margins
            actions_layout.setSpacing(2)  # Reduced spacing between buttons
            
            # Edit button
            edit_button = SecondaryButton("Edit")
            edit_button.clicked.connect(lambda _, item_id=item.id: self.edit_menu_item(item_id))
            actions_layout.addWidget(edit_button)
            
            # Toggle availability button
            if item.available:
                toggle_button = DangerButton("Disable")
            else:
                toggle_button = SuccessButton("Enable")
            
            toggle_button.clicked.connect(lambda _, item_id=item.id, available=item.available: 
                                         self.toggle_availability(item_id, available))
            actions_layout.addWidget(toggle_button)
            
            table.setCellWidget(i, 4, actions_widget)
    
    def add_menu_item(self):
        """Add a new menu item."""
        dialog = MenuItemDialog(parent=self)
        if dialog.exec_():
            self.refresh_data()
    
    def edit_menu_item(self, item_id):
        """Edit a menu item."""
        dialog = MenuItemDialog(item_id, parent=self)
        if dialog.exec_():
            self.refresh_data()
    
    def toggle_availability(self, item_id, current_available):
        """Toggle the availability of a menu item."""
        try:
            item = MenuItem.get_by_id(item_id)
            if item:
                item.available = not current_available
                item.update()
                self.refresh_data()
        except Exception as e:
            show_message(self, "Error", f"Failed to update item: {str(e)}", QMessageBox.Critical) 