from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QLineEdit, QFileDialog,
    QMessageBox, QFrame, QHeaderView, QDialog, QFormLayout,
    QComboBox, QSpinBox
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QImage, QFont, QIcon, QPainter, QPen, QColor
import os
from datetime import datetime
from src.database import Game, db

class GameDialog(QDialog):
    def __init__(self, parent=None, game_data=None):
        super().__init__(parent)
        self.game_data = game_data
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("Add/Edit Game")
        self.setMinimumWidth(400)
        self.setStyleSheet("""
            QDialog {
                background-color: #1a1a2e;
                color: white;
            }
            QLabel {
                color: #00c3ff;
                font-size: 14px;
            }
            QLineEdit, QComboBox, QSpinBox {
                background-color: #2a2a3a;
                border: 1px solid #00c3ff;
                border-radius: 5px;
                padding: 8px;
                color: white;
                font-size: 14px;
            }
            QPushButton {
                background-color: #00c3ff;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00a5eb;
            }
        """)
        
        layout = QFormLayout(self)
        layout.setSpacing(15)
        
        # Game name
        self.name_edit = QLineEdit()
        layout.addRow("Game Name:", self.name_edit)
        
        # Game description
        self.description_edit = QLineEdit()
        layout.addRow("Description:", self.description_edit)
        
        # Game type
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Action", "RPG", "Strategy", "Sports", "Racing", "FPS", "MOBA", "Other"])
        layout.addRow("Game Type:", self.type_combo)
        
        # Executable path
        self.path_edit = QLineEdit()
        self.path_edit.setReadOnly(True)
        path_button = QPushButton("Browse")
        path_button.clicked.connect(self.browse_path)
        path_layout = QHBoxLayout()
        path_layout.addWidget(self.path_edit)
        path_layout.addWidget(path_button)
        layout.addRow("Executable Path:", path_layout)
        
        # Image path
        self.image_edit = QLineEdit()
        self.image_edit.setReadOnly(True)
        image_button = QPushButton("Browse")
        image_button.clicked.connect(self.browse_image)
        image_layout = QHBoxLayout()
        image_layout.addWidget(self.image_edit)
        image_layout.addWidget(image_button)
        layout.addRow("Game Image:", image_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addRow("", button_layout)
        
        # Set existing data if editing
        if self.game_data:
            self.name_edit.setText(self.game_data.name or "")
            self.description_edit.setText(self.game_data.description or "")
            self.type_combo.setCurrentText(self.game_data.category or "Action")
            self.path_edit.setText(self.game_data.executable_path or "")
            self.image_edit.setText(self.game_data.image_path or "")
    
    def browse_path(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Game Executable", "",
            "Executable Files (*.exe);;All Files (*.*)"
        )
        if file_path:
            self.path_edit.setText(file_path)
    
    def browse_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Game Image", "",
            "Image Files (*.png *.jpg *.jpeg);;All Files (*.*)"
        )
        if file_path:
            self.image_edit.setText(file_path)
    
    def get_game_data(self):
        return {
            "name": self.name_edit.text(),
            "description": self.description_edit.text(),
            "category": self.type_combo.currentText(),
            "executable_path": self.path_edit.text(),
            "image_path": self.image_edit.text(),
            "is_available": True
        }

class GamesTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.load_games()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(20)
        
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
        
        title = QLabel("Games Management")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setStyleSheet("color: #00c3ff;")
        header_layout.addWidget(title)
        
        add_button = QPushButton("Add New Game")
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
        add_button.clicked.connect(self.add_game)
        header_layout.addWidget(add_button)
        
        layout.addWidget(header)
        
        # Games table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Image", "Game Name", "Description", "Type", "Path", "Actions"])
        
        # Set column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)  # Image column
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Name column
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # Description column
        header.setSectionResizeMode(3, QHeaderView.Fixed)  # Type column
        header.setSectionResizeMode(4, QHeaderView.Stretch)  # Path column
        header.setSectionResizeMode(5, QHeaderView.Fixed)  # Actions column
        
        # Set specific column widths
        self.table.setColumnWidth(0, 100)  # Image column
        self.table.setColumnWidth(3, 100)  # Type column
        self.table.setColumnWidth(5, 180)  # Actions column - increased from 100 to 180
        
        # Set row height
        self.table.verticalHeader().setDefaultSectionSize(80)
        
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: rgba(35, 35, 50, 0.7);
                border: none;
                border-radius: 10px;
                gridline-color: rgba(0, 195, 255, 0.2);
            }
            QTableWidget::item {
                padding: 10px;
                border-bottom: 1px solid rgba(0, 195, 255, 0.2);
            }
            QHeaderView::section {
                background-color: rgba(0, 195, 255, 0.2);
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
            }
        """)
        layout.addWidget(self.table)
    
    
    def load_games(self):
        try:
            self.games = Game.get_all()
            self.refresh_table()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load games: {str(e)}")
            self.games = []
    
    def refresh_table(self):
        self.table.setRowCount(len(self.games))
        
        for row, game in enumerate(self.games):
            # Image preview
            image_label = QLabel()
            if game.image_path and os.path.exists(game.image_path):
                pixmap = QPixmap(game.image_path)
                scaled_pixmap = pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                image_label.setPixmap(scaled_pixmap)
            image_label.setAlignment(Qt.AlignCenter)
            self.table.setCellWidget(row, 0, image_label)
            
            # Game name
            self.table.setItem(row, 1, QTableWidgetItem(game.name or ""))
            
            # Description
            self.table.setItem(row, 2, QTableWidgetItem(game.description or ""))
            
            # Game type
            self.table.setItem(row, 3, QTableWidgetItem(game.category or ""))
            
            # Path
            self.table.setItem(row, 4, QTableWidgetItem(game.executable_path or ""))
            
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(5, 5, 5, 5)
            actions_layout.setSpacing(10)
            actions_layout.setAlignment(Qt.AlignCenter)
            
            edit_button = QPushButton("Edit")
            edit_button.setMinimumWidth(70)
            edit_button.setStyleSheet("""
                QPushButton {
                    background-color: #00c3ff;
                    color: white;
                    border: none;
                    border-radius: 3px;
                    padding: 8px 15px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #00a5eb;
                }
            """)
            edit_button.clicked.connect(lambda checked, r=row: self.edit_game(r))
            
            delete_button = QPushButton("Delete")
            delete_button.setMinimumWidth(70)
            delete_button.setStyleSheet("""
                QPushButton {
                    background-color: #ff4444;
                    color: white;
                    border: none;
                    border-radius: 3px;
                    padding: 8px 15px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #ff2222;
                }
            """)
            delete_button.clicked.connect(lambda checked, r=row: self.delete_game(r))
            
            actions_layout.addWidget(edit_button)
            actions_layout.addWidget(delete_button)
            
            self.table.setCellWidget(row, 5, actions_widget)
    
    def add_game(self):
        dialog = GameDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            try:
                game_data = dialog.get_game_data()
                cursor = db.get_cursor()
                query = """
                INSERT INTO games (name, description, executable_path, image_path, category, is_available)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query, (
                    game_data["name"],
                    game_data["description"],
                    game_data["executable_path"],
                    game_data["image_path"],
                    game_data["category"],
                    game_data["is_available"]
                ))
                db.commit()
                self.load_games()
            except Exception as e:
                db.rollback()
                QMessageBox.warning(self, "Error", f"Failed to add game: {str(e)}")
    
    def edit_game(self, row):
        game = self.games[row]
        dialog = GameDialog(self, game)
        if dialog.exec_() == QDialog.Accepted:
            try:
                game_data = dialog.get_game_data()
                cursor = db.get_cursor()
                query = """
                UPDATE games 
                SET name = %s, description = %s, executable_path = %s, 
                    image_path = %s, category = %s, is_available = %s
                WHERE id = %s
                """
                cursor.execute(query, (
                    game_data["name"],
                    game_data["description"],
                    game_data["executable_path"],
                    game_data["image_path"],
                    game_data["category"],
                    game_data["is_available"],
                    game.id
                ))
                db.commit()
                self.load_games()
            except Exception as e:
                db.rollback()
                QMessageBox.warning(self, "Error", f"Failed to update game: {str(e)}")
    
    def delete_game(self, row):
        reply = QMessageBox.question(
            self, "Confirm Delete",
            "Are you sure you want to delete this game?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                game = self.games[row]
                cursor = db.get_cursor()
                query = "DELETE FROM games WHERE id = %s"
                cursor.execute(query, (game.id,))
                db.commit()
                self.load_games()
            except Exception as e:
                db.rollback()
                QMessageBox.warning(self, "Error", f"Failed to delete game: {str(e)}")
    
    def refresh_data(self):
        """Refresh the games data."""
        self.load_games() 