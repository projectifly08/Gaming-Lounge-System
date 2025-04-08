from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, 
    QFrame, QSizePolicy, QSpacerItem, QTableWidgetItem, QMessageBox,
    QDialog, QComboBox, QLineEdit, QPushButton, QListWidget, QListWidgetItem,
    QFileDialog, QCheckBox, QHeaderView, QTabWidget, QScrollArea
)
from PyQt5.QtCore import Qt, QTimer, QDateTime
from PyQt5.QtGui import QFont, QColor, QIcon, QPixmap

from src.common import (
    HeaderLabel, SubHeaderLabel, Card, StyledTable, StyledLineEdit,
    StyledComboBox, PrimaryButton, SecondaryButton, DangerButton, SuccessButton,
    show_message, confirm_action, create_spacer
)
from src.database import db, MenuItem, MenuItemExtra, MenuItemTakeout
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
        layout.setSpacing(15)
        
        # Create tabs
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 10px;
            }
            QTabBar::tab {
                background-color: #f2f2f2;
                border: 1px solid #cccccc;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 8px 12px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 1px solid white;
            }
            QTabBar::tab:hover:!selected {
                background-color: #e6e6e6;
            }
        """)
        
        # Basic info tab
        basic_tab = QWidget()
        basic_layout = QVBoxLayout(basic_tab)
        
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
        
        basic_layout.addLayout(form_grid)
        
        # Extras tab
        extras_tab = QWidget()
        extras_layout = QVBoxLayout(extras_tab)
        
        extras_header = QHBoxLayout()
        extras_title = QLabel("Extras (Additional Options with Extra Cost)")
        extras_title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        extras_header.addWidget(extras_title)
        
        add_extra_button = PrimaryButton("Add Extra")
        add_extra_button.clicked.connect(self.add_extra)
        extras_header.addWidget(add_extra_button)
        
        extras_layout.addLayout(extras_header)
        
        # Table for extras
        self.extras_table = StyledTable()
        self.extras_table.setColumnCount(4)
        self.extras_table.setHorizontalHeaderLabels(["Name", "Price", "Available", "Actions"])
        self.extras_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.extras_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.extras_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.extras_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        
        extras_layout.addWidget(self.extras_table)
        
        # Takeouts tab
        takeouts_tab = QWidget()
        takeouts_layout = QVBoxLayout(takeouts_tab)
        
        takeouts_header = QHBoxLayout()
        takeouts_title = QLabel("Takeouts (Ingredients customer can remove)")
        takeouts_title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        takeouts_header.addWidget(takeouts_title)
        
        add_takeout_button = PrimaryButton("Add Takeout")
        add_takeout_button.clicked.connect(self.add_takeout)
        takeouts_header.addWidget(add_takeout_button)
        
        takeouts_layout.addLayout(takeouts_header)
        
        # Table for takeouts
        self.takeouts_table = StyledTable()
        self.takeouts_table.setColumnCount(3)
        self.takeouts_table.setHorizontalHeaderLabels(["Name", "Available", "Actions"])
        self.takeouts_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.takeouts_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.takeouts_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        
        takeouts_layout.addWidget(self.takeouts_table)
        
        # Add tabs to tab widget
        tabs.addTab(basic_tab, "Basic Info")
        tabs.addTab(extras_tab, "Extras")
        tabs.addTab(takeouts_tab, "Takeouts")
        
        layout.addWidget(tabs)
        
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
                
            # Load extras and takeouts if item exists
            self.load_extras()
            self.load_takeouts()
            
    def load_extras(self):
        """Load extras for the current menu item."""
        if not self.item:
            return
            
        # Clear the table
        self.extras_table.setRowCount(0)
        
        # Get extras for this menu item
        extras = MenuItemExtra.get_by_menu_item(self.item.id)
        
        # Add to table
        for i, extra in enumerate(extras):
            self.extras_table.insertRow(i)
            
            # Name
            self.extras_table.setItem(i, 0, QTableWidgetItem(extra.name))
            
            # Price
            self.extras_table.setItem(i, 1, QTableWidgetItem(format_currency(extra.price)))
            
            # Available
            available_item = QTableWidgetItem("Yes" if extra.available else "No")
            if not extra.available:
                available_item.setForeground(QColor('#e74c3c'))  # Red
            self.extras_table.setItem(i, 2, available_item)
            
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(2, 0, 2, 0)
            actions_layout.setSpacing(2)
            
            # Edit button
            edit_button = SecondaryButton("Edit")
            edit_button.clicked.connect(lambda _, extra_id=extra.id: self.edit_extra(extra_id))
            actions_layout.addWidget(edit_button)
            
            # Delete button
            delete_button = DangerButton("Delete")
            delete_button.clicked.connect(lambda _, extra_id=extra.id: self.delete_extra(extra_id))
            actions_layout.addWidget(delete_button)
            
            self.extras_table.setCellWidget(i, 3, actions_widget)
            
    def browse_image(self):
        """Browse for an image file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "", "Image Files (*.png *.jpg *.jpeg *.gif)"
        )
        
        if file_path:
            self.image_path_input.setText(file_path)
            
    def load_takeouts(self):
        """Load takeouts for the current menu item."""
        if not self.item:
            return
            
        # Clear the table
        self.takeouts_table.setRowCount(0)
        
        # Get takeouts for this menu item
        takeouts = MenuItemTakeout.get_by_menu_item(self.item.id)
        
        # Add to table
        for i, takeout in enumerate(takeouts):
            self.takeouts_table.insertRow(i)
            
            # Name
            self.takeouts_table.setItem(i, 0, QTableWidgetItem(takeout.name))
            
            # Available
            available_item = QTableWidgetItem("Yes" if takeout.available else "No")
            if not takeout.available:
                available_item.setForeground(QColor('#e74c3c'))  # Red
            self.takeouts_table.setItem(i, 1, available_item)
            
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(2, 0, 2, 0)
            actions_layout.setSpacing(2)
            
            # Edit button
            edit_button = SecondaryButton("Edit")
            edit_button.clicked.connect(lambda _, takeout_id=takeout.id: self.edit_takeout(takeout_id))
            actions_layout.addWidget(edit_button)
            
            # Delete button
            delete_button = DangerButton("Delete")
            delete_button.clicked.connect(lambda _, takeout_id=takeout.id: self.delete_takeout(takeout_id))
            actions_layout.addWidget(delete_button)
            
            self.takeouts_table.setCellWidget(i, 2, actions_widget)
            
    def add_extra(self):
        """Add a new extra option to the menu item."""
        if not self.item:
            show_message(self, "Error", "Please save the menu item first before adding extras.", QMessageBox.Warning)
            return
            
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Extra Option")
        dialog.setMinimumWidth(300)
        
        layout = QVBoxLayout(dialog)
        
        # Name
        name_label = QLabel("Name:")
        name_input = StyledLineEdit(placeholder="Enter extra name")
        layout.addWidget(name_label)
        layout.addWidget(name_input)
        
        # Price
        price_label = QLabel("Price:")
        price_input = StyledLineEdit(placeholder="Enter price (e.g. 1.99)")
        layout.addWidget(price_label)
        layout.addWidget(price_input)
        
        # Buttons
        button_layout = QHBoxLayout()
        cancel_button = SecondaryButton("Cancel")
        cancel_button.clicked.connect(dialog.reject)
        
        save_button = PrimaryButton("Save")
        save_button.clicked.connect(dialog.accept)
        
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(save_button)
        
        layout.addLayout(button_layout)
        
        if dialog.exec_() == QDialog.Accepted:
            name = name_input.text().strip()
            price_text = price_input.text().strip()
            
            if not name:
                show_message(self, "Error", "Please enter a name for the extra.", QMessageBox.Warning)
                return
            
            try:
                price = float(price_text)
                if price <= 0:
                    raise ValueError("Price must be positive")
            except ValueError:
                show_message(self, "Error", "Please enter a valid price.", QMessageBox.Warning)
                return
                
            try:
                # Create the extra
                MenuItemExtra.create(self.item.id, name, price)
                
                # Refresh the extras table
                self.load_extras()
                
                show_message(self, "Success", "Extra option added successfully.")
            except Exception as e:
                show_message(self, "Error", f"Failed to add extra: {str(e)}", QMessageBox.Critical)
                
    def edit_extra(self, extra_id):
        """Edit an existing extra option."""
        extra = MenuItemExtra.get_by_id(extra_id)
        if not extra:
            show_message(self, "Error", "Extra option not found.", QMessageBox.Critical)
            return
            
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Extra Option")
        dialog.setMinimumWidth(300)
        
        layout = QVBoxLayout(dialog)
        
        # Name
        name_label = QLabel("Name:")
        name_input = StyledLineEdit(placeholder="Enter extra name")
        name_input.setText(extra.name)
        layout.addWidget(name_label)
        layout.addWidget(name_input)
        
        # Price
        price_label = QLabel("Price:")
        price_input = StyledLineEdit(placeholder="Enter price (e.g. 1.99)")
        price_input.setText(str(extra.price))
        layout.addWidget(price_label)
        layout.addWidget(price_input)
        
        # Available
        available_layout = QHBoxLayout()
        available_label = QLabel("Available:")
        available_checkbox = QCheckBox()
        available_checkbox.setChecked(extra.available)
        available_layout.addWidget(available_label)
        available_layout.addWidget(available_checkbox)
        layout.addLayout(available_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        cancel_button = SecondaryButton("Cancel")
        cancel_button.clicked.connect(dialog.reject)
        
        save_button = PrimaryButton("Save")
        save_button.clicked.connect(dialog.accept)
        
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(save_button)
        
        layout.addLayout(button_layout)
        
        if dialog.exec_() == QDialog.Accepted:
            name = name_input.text().strip()
            price_text = price_input.text().strip()
            available = available_checkbox.isChecked()
            
            if not name:
                show_message(self, "Error", "Please enter a name for the extra.", QMessageBox.Warning)
                return
            
            try:
                price = float(price_text)
                if price <= 0:
                    raise ValueError("Price must be positive")
            except ValueError:
                show_message(self, "Error", "Please enter a valid price.", QMessageBox.Warning)
                return
                
            try:
                # Update the extra
                extra.name = name
                extra.price = price
                extra.available = available
                extra.update()
                
                # Refresh the extras table
                self.load_extras()
                
                show_message(self, "Success", "Extra option updated successfully.")
            except Exception as e:
                show_message(self, "Error", f"Failed to update extra: {str(e)}", QMessageBox.Critical)
                
    def delete_extra(self, extra_id):
        """Delete an extra option."""
        if not confirm_action("Delete Extra", "Are you sure you want to delete this extra option?", self):
            return
            
        try:
            extra = MenuItemExtra.get_by_id(extra_id)
            if extra:
                extra.delete()
                self.load_extras()
                show_message(self, "Success", "Extra option deleted successfully.")
        except Exception as e:
            show_message(self, "Error", f"Failed to delete extra: {str(e)}", QMessageBox.Critical)
            
    def add_takeout(self):
        """Add a new takeout option to the menu item."""
        if not self.item:
            show_message(self, "Error", "Please save the menu item first before adding takeouts.", QMessageBox.Warning)
            return
            
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Takeout Option")
        dialog.setMinimumWidth(300)
        
        layout = QVBoxLayout(dialog)
        
        # Name
        name_label = QLabel("Name:")
        name_input = StyledLineEdit(placeholder="Enter takeout name (e.g. 'No onions')")
        layout.addWidget(name_label)
        layout.addWidget(name_input)
        
        # Buttons
        button_layout = QHBoxLayout()
        cancel_button = SecondaryButton("Cancel")
        cancel_button.clicked.connect(dialog.reject)
        
        save_button = PrimaryButton("Save")
        save_button.clicked.connect(dialog.accept)
        
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(save_button)
        
        layout.addLayout(button_layout)
        
        if dialog.exec_() == QDialog.Accepted:
            name = name_input.text().strip()
            
            if not name:
                show_message(self, "Error", "Please enter a name for the takeout.", QMessageBox.Warning)
                return
                
            try:
                # Create the takeout
                MenuItemTakeout.create(self.item.id, name)
                
                # Refresh the takeouts table
                self.load_takeouts()
                
                show_message(self, "Success", "Takeout option added successfully.")
            except Exception as e:
                show_message(self, "Error", f"Failed to add takeout: {str(e)}", QMessageBox.Critical)
                
    def edit_takeout(self, takeout_id):
        """Edit an existing takeout option."""
        takeout = MenuItemTakeout.get_by_id(takeout_id)
        if not takeout:
            show_message(self, "Error", "Takeout option not found.", QMessageBox.Critical)
            return
            
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Takeout Option")
        dialog.setMinimumWidth(300)
        
        layout = QVBoxLayout(dialog)
        
        # Name
        name_label = QLabel("Name:")
        name_input = StyledLineEdit(placeholder="Enter takeout name")
        name_input.setText(takeout.name)
        layout.addWidget(name_label)
        layout.addWidget(name_input)
        
        # Available
        available_layout = QHBoxLayout()
        available_label = QLabel("Available:")
        available_checkbox = QCheckBox()
        available_checkbox.setChecked(takeout.available)
        available_layout.addWidget(available_label)
        available_layout.addWidget(available_checkbox)
        layout.addLayout(available_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        cancel_button = SecondaryButton("Cancel")
        cancel_button.clicked.connect(dialog.reject)
        
        save_button = PrimaryButton("Save")
        save_button.clicked.connect(dialog.accept)
        
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(save_button)
        
        layout.addLayout(button_layout)
        
        if dialog.exec_() == QDialog.Accepted:
            name = name_input.text().strip()
            available = available_checkbox.isChecked()
            
            if not name:
                show_message(self, "Error", "Please enter a name for the takeout.", QMessageBox.Warning)
                return
                
            try:
                # Update the takeout
                takeout.name = name
                takeout.available = available
                takeout.update()
                
                # Refresh the takeouts table
                self.load_takeouts()
                
                show_message(self, "Success", "Takeout option updated successfully.")
            except Exception as e:
                show_message(self, "Error", f"Failed to update takeout: {str(e)}", QMessageBox.Critical)
                
    def delete_takeout(self, takeout_id):
        """Delete a takeout option."""
        if not confirm_action("Delete Takeout", "Are you sure you want to delete this takeout option?", self):
            return
            
        try:
            takeout = MenuItemTakeout.get_by_id(takeout_id)
            if takeout:
                takeout.delete()
                self.load_takeouts()
                show_message(self, "Success", "Takeout option deleted successfully.")
        except Exception as e:
            show_message(self, "Error", f"Failed to delete takeout: {str(e)}", QMessageBox.Critical)
    
    def save_item(self):
        """Save the menu item and its extras/takeouts."""
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
                self.item = MenuItem.get_by_id(item_id)
                show_message(self, "Success", "Menu item added successfully.")
                
                # Refresh extras and takeouts for the new item
                self.load_extras()
                self.load_takeouts()
            
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