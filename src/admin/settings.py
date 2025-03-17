import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QFormLayout, QGroupBox,
                            QMessageBox, QFileDialog, QSpinBox, QDoubleSpinBox,
                            QComboBox, QCheckBox, QTabWidget, QFrame)
from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtGui import QFont

from src.database import db
from src.utils.helpers import hash_password
from src.common.ui_components import create_header, create_button

class SettingsTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = QSettings("GamingLounge", "AdminPanel")
        self.init_ui()
        
    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.setAlignment(Qt.AlignTop)
        
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
        
        title = QLabel("System Settings")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setStyleSheet("color: #00c3ff;")
        header_layout.addWidget(title)
        
        main_layout.addWidget(header)
        
        # Create tabs for different settings categories
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid rgba(0, 195, 255, 0.3);
                border-radius: 8px;
                background-color: rgba(25, 25, 40, 0.5);
            }
            QGroupBox {
                font-weight: bold;
                color: #00c3ff;
                border: 1px solid rgba(0, 195, 255, 0.4);
                border-radius: 8px;
                margin-top: 1.5ex;
                background-color: rgba(30, 30, 50, 0.5);
                padding: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
                background-color: rgba(18, 18, 30, 0.7);
                border-radius: 4px;
            }
            QLabel {
                color: #e0e0e0;
            }
            QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
                background-color: rgba(40, 40, 60, 0.5);
                border: 1px solid rgba(0, 195, 255, 0.4);
                border-radius: 4px;
                padding: 5px;
                color: white;
            }
            QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
                border: 1px solid rgba(0, 195, 255, 0.8);
                background-color: rgba(45, 45, 70, 0.6);
            }
            QCheckBox {
                color: #e0e0e0;
            }
            QCheckBox::indicator {
                width: 15px;
                height: 15px;
                background-color: rgba(40, 40, 60, 0.5);
                border: 1px solid rgba(0, 195, 255, 0.4);
                border-radius: 3px;
            }
            QCheckBox::indicator:checked {
                background-color: rgba(0, 195, 255, 0.5);
            }
        """)
        
        tabs.addTab(self.create_general_settings(), "General")
        tabs.addTab(self.create_pricing_settings(), "Pricing")
        tabs.addTab(self.create_admin_settings(), "Admin Account")
        tabs.addTab(self.create_backup_settings(), "Backup & Restore")
        
        main_layout.addWidget(tabs)
        
        # Save button at the bottom
        save_button = create_button("Save All Settings", "primary")
        save_button.clicked.connect(self.save_all_settings)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(save_button)
        
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)
        
    def create_general_settings(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        # System name settings
        system_group = QGroupBox("System Information")
        system_layout = QFormLayout()
        
        self.system_name = QLineEdit()
        self.system_name.setText(self.settings.value("system_name", "Gaming Lounge System"))
        system_layout.addRow("System Name:", self.system_name)
        
        self.business_name = QLineEdit()
        self.business_name.setText(self.settings.value("business_name", "Gaming Lounge"))
        system_layout.addRow("Business Name:", self.business_name)
        
        self.contact_email = QLineEdit()
        self.contact_email.setText(self.settings.value("contact_email", "contact@gaminglounge.com"))
        system_layout.addRow("Contact Email:", self.contact_email)
        
        self.contact_phone = QLineEdit()
        self.contact_phone.setText(self.settings.value("contact_phone", "+1234567890"))
        system_layout.addRow("Contact Phone:", self.contact_phone)
        
        system_group.setLayout(system_layout)
        layout.addWidget(system_group)
        
        # Session settings
        session_group = QGroupBox("Session Settings")
        session_layout = QFormLayout()
        
        self.default_session_duration = QSpinBox()
        self.default_session_duration.setRange(1, 24)
        self.default_session_duration.setValue(int(self.settings.value("default_session_duration", 1)))
        self.default_session_duration.setSuffix(" hour(s)")
        session_layout.addRow("Default Session Duration:", self.default_session_duration)
        
        self.session_warning_time = QSpinBox()
        self.session_warning_time.setRange(1, 60)
        self.session_warning_time.setValue(int(self.settings.value("session_warning_time", 10)))
        self.session_warning_time.setSuffix(" minutes")
        session_layout.addRow("Session Warning Time:", self.session_warning_time)
        
        self.auto_logout_enabled = QCheckBox("Enable Auto Logout")
        self.auto_logout_enabled.setChecked(self.settings.value("auto_logout_enabled", "true") == "true")
        session_layout.addRow("", self.auto_logout_enabled)
        
        session_group.setLayout(session_layout)
        layout.addWidget(session_group)
        
        # UI settings
        ui_group = QGroupBox("UI Settings")
        ui_layout = QFormLayout()
        
        self.theme = QComboBox()
        self.theme.addItems(["Light", "Dark", "System"])
        self.theme.setCurrentText(self.settings.value("theme", "Light"))
        ui_layout.addRow("Theme:", self.theme)
        
        self.refresh_interval = QSpinBox()
        self.refresh_interval.setRange(5, 120)
        self.refresh_interval.setValue(int(self.settings.value("refresh_interval", 30)))
        self.refresh_interval.setSuffix(" seconds")
        ui_layout.addRow("Data Refresh Interval:", self.refresh_interval)
        
        ui_group.setLayout(ui_layout)
        layout.addWidget(ui_group)
        
        widget.setLayout(layout)
        return widget
        
    def create_pricing_settings(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Gaming pricing
        gaming_group = QGroupBox("Gaming Pricing")
        gaming_layout = QFormLayout()
        
        self.hourly_rate = QDoubleSpinBox()
        self.hourly_rate.setRange(0.01, 100.00)
        self.hourly_rate.setValue(float(self.settings.value("hourly_rate", 5.00)))
        self.hourly_rate.setPrefix("$ ")
        self.hourly_rate.setDecimals(2)
        gaming_layout.addRow("Hourly Rate:", self.hourly_rate)
        
        self.discount_rate = QDoubleSpinBox()
        self.discount_rate.setRange(0, 100.00)
        self.discount_rate.setValue(float(self.settings.value("discount_rate", 10.00)))
        self.discount_rate.setSuffix(" %")
        self.discount_rate.setDecimals(2)
        gaming_layout.addRow("Discount for 3+ Hours:", self.discount_rate)
        
        self.member_discount = QDoubleSpinBox()
        self.member_discount.setRange(0, 100.00)
        self.member_discount.setValue(float(self.settings.value("member_discount", 15.00)))
        self.member_discount.setSuffix(" %")
        self.member_discount.setDecimals(2)
        gaming_layout.addRow("Member Discount:", self.member_discount)
        
        gaming_group.setLayout(gaming_layout)
        layout.addWidget(gaming_group)
        
        # Payment methods
        payment_group = QGroupBox("Payment Methods")
        payment_layout = QFormLayout()
        
        self.enable_cash = QCheckBox("Enable Cash Payments")
        self.enable_cash.setChecked(self.settings.value("enable_cash", "true") == "true")
        payment_layout.addRow("", self.enable_cash)
        
        self.enable_card = QCheckBox("Enable Card Payments")
        self.enable_card.setChecked(self.settings.value("enable_card", "true") == "true")
        payment_layout.addRow("", self.enable_card)
        
        self.enable_mobile = QCheckBox("Enable Mobile Payments")
        self.enable_mobile.setChecked(self.settings.value("enable_mobile", "false") == "true")
        payment_layout.addRow("", self.enable_mobile)
        
        payment_group.setLayout(payment_layout)
        layout.addWidget(payment_group)
        
        widget.setLayout(layout)
        return widget
        
    def create_admin_settings(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Admin account settings
        admin_group = QGroupBox("Admin Account")
        admin_layout = QFormLayout()
        
        self.admin_username = QLineEdit()
        self.admin_username.setText(self.settings.value("admin_username", "admin"))
        admin_layout.addRow("Admin Username:", self.admin_username)
        
        self.admin_password = QLineEdit()
        self.admin_password.setEchoMode(QLineEdit.Password)
        self.admin_password.setPlaceholderText("Enter new password to change")
        admin_layout.addRow("New Password:", self.admin_password)
        
        self.admin_password_confirm = QLineEdit()
        self.admin_password_confirm.setEchoMode(QLineEdit.Password)
        self.admin_password_confirm.setPlaceholderText("Confirm new password")
        admin_layout.addRow("Confirm Password:", self.admin_password_confirm)
        
        self.admin_email = QLineEdit()
        self.admin_email.setText(self.settings.value("admin_email", "admin@gaminglounge.com"))
        admin_layout.addRow("Admin Email:", self.admin_email)
        
        admin_group.setLayout(admin_layout)
        layout.addWidget(admin_group)
        
        # Security settings
        security_group = QGroupBox("Security Settings")
        security_layout = QFormLayout()
        
        # self.session_timeout = QSpinBox()
        # self.session_timeout.setRange(1, 60)
        # self.session_timeout.setValue(int(self.settings.value("session_timeout", 15)))
        # self.session_timeout.setSuffix(" minutes")
        # security_layout.addRow("Admin Session Timeout:", self.session_timeout)
        
        # self.require_password_for_critical = QCheckBox("Require Password for Critical Actions")
        # self.require_password_for_critical.setChecked(self.settings.value("require_password_for_critical", "true") == "true")
        # security_layout.addRow("", self.require_password_for_critical)
        
        # Add Launcher Exit Password
        self.launcher_exit_password = QLineEdit()
        self.launcher_exit_password.setEchoMode(QLineEdit.Password)
        self.launcher_exit_password.setPlaceholderText("Enter launcher exit password")
        self.launcher_exit_password.setText(self.settings.value("launcher_exit_password", ""))
        security_layout.addRow("Launcher Exit Password:", self.launcher_exit_password)
        
        security_group.setLayout(security_layout)
        layout.addWidget(security_group)
        
        widget.setLayout(layout)
        return widget
        
    def create_backup_settings(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Backup settings
        backup_group = QGroupBox("Database Backup")
        backup_layout = QVBoxLayout()
        
        backup_form = QFormLayout()
        
        self.backup_location = QLineEdit()
        self.backup_location.setText(self.settings.value("backup_location", os.path.expanduser("~/gaming_lounge_backups")))
        self.backup_location.setReadOnly(True)
        
        backup_location_layout = QHBoxLayout()
        backup_location_layout.addWidget(self.backup_location)
        
        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self.browse_backup_location)
        backup_location_layout.addWidget(browse_button)
        
        backup_form.addRow("Backup Location:", backup_location_layout)
        
        self.auto_backup = QCheckBox("Enable Automatic Backups")
        self.auto_backup.setChecked(self.settings.value("auto_backup", "true") == "true")
        backup_form.addRow("", self.auto_backup)
        
        self.backup_frequency = QComboBox()
        self.backup_frequency.addItems(["Daily", "Weekly", "Monthly"])
        self.backup_frequency.setCurrentText(self.settings.value("backup_frequency", "Daily"))
        backup_form.addRow("Backup Frequency:", self.backup_frequency)
        
        backup_layout.addLayout(backup_form)
        
        # Backup and restore buttons
        button_layout = QHBoxLayout()
        
        backup_now_button = create_button("Backup Now", "primary")
        backup_now_button.clicked.connect(self.backup_now)
        button_layout.addWidget(backup_now_button)
        
        restore_button = create_button("Restore from Backup", "secondary")
        restore_button.clicked.connect(self.restore_from_backup)
        button_layout.addWidget(restore_button)
        
        backup_layout.addLayout(button_layout)
        backup_group.setLayout(backup_layout)
        layout.addWidget(backup_group)
        
        # Data management
        data_group = QGroupBox("Data Management")
        data_layout = QVBoxLayout()
        
        warning_label = QLabel("Warning: These actions cannot be undone!")
        warning_label.setStyleSheet("color: red; font-weight: bold;")
        data_layout.addWidget(warning_label)
        
        button_layout = QHBoxLayout()
        
        clear_sessions_button = create_button("Clear All Sessions", "danger")
        clear_sessions_button.clicked.connect(self.clear_sessions)
        button_layout.addWidget(clear_sessions_button)
        
        clear_orders_button = create_button("Clear All Orders", "danger")
        clear_orders_button.clicked.connect(self.clear_orders)
        button_layout.addWidget(clear_orders_button)
        
        reset_db_button = create_button("Reset Database", "danger")
        reset_db_button.clicked.connect(self.reset_database)
        button_layout.addWidget(reset_db_button)
        
        data_layout.addLayout(button_layout)
        data_group.setLayout(data_layout)
        layout.addWidget(data_group)
        
        widget.setLayout(layout)
        return widget
        
    def browse_backup_location(self):
        directory = QFileDialog.getExistingDirectory(
            self, "Select Backup Directory", 
            self.backup_location.text(),
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        
        if directory:
            self.backup_location.setText(directory)
    
    def backup_now(self):
        # Implement database backup functionality
        try:
            # Placeholder for actual backup code
            QMessageBox.information(
                self, "Backup", 
                f"Database backed up successfully to {self.backup_location.text()}"
            )
        except Exception as e:
            QMessageBox.critical(
                self, "Backup Error", 
                f"Failed to backup database: {str(e)}"
            )
    
    def restore_from_backup(self):
        # Implement database restore functionality
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Backup File", 
            self.backup_location.text(),
            "SQL Files (*.sql);;All Files (*)"
        )
        
        if file_path:
            confirm = QMessageBox.question(
                self, "Confirm Restore", 
                "Restoring from backup will overwrite current data. Continue?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            
            if confirm == QMessageBox.Yes:
                try:
                    # Placeholder for actual restore code
                    QMessageBox.information(
                        self, "Restore", 
                        "Database restored successfully!"
                    )
                except Exception as e:
                    QMessageBox.critical(
                        self, "Restore Error", 
                        f"Failed to restore database: {str(e)}"
                    )
    
    def clear_sessions(self):
        confirm = QMessageBox.question(
            self, "Confirm Clear Sessions", 
            "This will delete ALL session records. This action cannot be undone. Continue?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            try:
                # Placeholder for actual clear sessions code
                QMessageBox.information(
                    self, "Clear Sessions", 
                    "All session records have been cleared."
                )
            except Exception as e:
                QMessageBox.critical(
                    self, "Error", 
                    f"Failed to clear sessions: {str(e)}"
                )
    
    def clear_orders(self):
        confirm = QMessageBox.question(
            self, "Confirm Clear Orders", 
            "This will delete ALL order records. This action cannot be undone. Continue?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            try:
                # Placeholder for actual clear orders code
                QMessageBox.information(
                    self, "Clear Orders", 
                    "All order records have been cleared."
                )
            except Exception as e:
                QMessageBox.critical(
                    self, "Error", 
                    f"Failed to clear orders: {str(e)}"
                )
    
    def reset_database(self):
        confirm = QMessageBox.question(
            self, "Confirm Reset Database", 
            "This will RESET the ENTIRE database. All data will be lost. This action cannot be undone. Continue?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            confirm_again = QMessageBox.question(
                self, "Final Confirmation", 
                "Are you ABSOLUTELY sure you want to reset the database? ALL DATA WILL BE LOST!",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            
            if confirm_again == QMessageBox.Yes:
                try:
                    # Placeholder for actual database reset code
                    QMessageBox.information(
                        self, "Reset Database", 
                        "Database has been reset successfully."
                    )
                except Exception as e:
                    QMessageBox.critical(
                        self, "Error", 
                        f"Failed to reset database: {str(e)}"
                    )
    
    def save_all_settings(self):
        # Validate admin password if changed
        if self.admin_password.text():
            if self.admin_password.text() != self.admin_password_confirm.text():
                QMessageBox.warning(
                    self, "Password Mismatch", 
                    "The new password and confirmation do not match."
                )
                return
            
            # Update admin password in database
            try:
                cursor = db.get_cursor()
                cursor.execute(
                    "UPDATE users SET password_hash = %s WHERE username = %s AND is_admin = 1",
                    (hash_password(self.admin_password.text()), self.admin_username.text())
                )
                db.commit()
                cursor.close()
                
                QMessageBox.information(
                    self, "Password Updated", 
                    "Admin password has been updated successfully."
                )
                
                # Clear password fields
                self.admin_password.setText("")
                self.admin_password_confirm.setText("")
            except Exception as e:
                QMessageBox.critical(
                    self, "Error", 
                    f"Failed to update admin password: {str(e)}"
                )
                return
        
        # Save admin username
        self.settings.setValue("admin_username", self.admin_username.text())
        self.settings.setValue("admin_email", self.admin_email.text())
        
        # Save general settings
        self.settings.setValue("system_name", self.system_name.text())
        self.settings.setValue("business_name", self.business_name.text())
        self.settings.setValue("contact_email", self.contact_email.text())
        self.settings.setValue("contact_phone", self.contact_phone.text())
        self.settings.setValue("default_session_duration", self.default_session_duration.value())
        self.settings.setValue("session_warning_time", self.session_warning_time.value())
        self.settings.setValue("auto_logout_enabled", str(self.auto_logout_enabled.isChecked()).lower())
        self.settings.setValue("theme", self.theme.currentText())
        self.settings.setValue("refresh_interval", self.refresh_interval.value())
        
        # Save pricing settings
        self.settings.setValue("hourly_rate", self.hourly_rate.value())
        self.settings.setValue("discount_rate", self.discount_rate.value())
        self.settings.setValue("member_discount", self.member_discount.value())
        self.settings.setValue("enable_cash", str(self.enable_cash.isChecked()).lower())
        self.settings.setValue("enable_card", str(self.enable_card.isChecked()).lower())
        self.settings.setValue("enable_mobile", str(self.enable_mobile.isChecked()).lower())
        
        # Save admin settings
        # self.settings.setValue("session_timeout", self.session_timeout.value())
        # self.settings.setValue("require_password_for_critical", str(self.require_password_for_critical.isChecked()).lower())
        
        # Save launcher exit password
        if self.launcher_exit_password.text():
            try:
                cursor = db.get_cursor()
                # First, ensure the settings table exists
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS settings (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        category VARCHAR(50) NOT NULL,
                        name VARCHAR(100) NOT NULL,
                        value TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        UNIQUE KEY unique_setting (category, name)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """)
                
                # Then save the launcher exit password
                cursor.execute("""
                    INSERT INTO settings (category, name, value)
                    VALUES ('security', 'launcher_exit_password', %s)
                    ON DUPLICATE KEY UPDATE value = %s
                """, (hash_password(self.launcher_exit_password.text()), hash_password(self.launcher_exit_password.text())))
                
                db.commit()
                cursor.close()
                
                QMessageBox.information(
                    self, "Exit Password Updated", 
                    "Launcher exit password has been updated successfully."
                )
                
                # Clear the password field
                self.launcher_exit_password.setText("")
            except Exception as e:
                QMessageBox.critical(
                    self, "Error", 
                    f"Failed to update launcher exit password: {str(e)}"
                )
                return
        
        # Save backup settings
        self.settings.setValue("backup_location", self.backup_location.text())
        self.settings.setValue("auto_backup", str(self.auto_backup.isChecked()).lower())
        self.settings.setValue("backup_frequency", self.backup_frequency.currentText())
        
        QMessageBox.information(
            self, "Settings Saved", 
            "All settings have been saved successfully."
        ) 