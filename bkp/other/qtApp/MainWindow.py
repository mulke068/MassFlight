import sys
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QStackedWidget, QLabel,
                             QFrame)
from PyQt5.QtCore import Qt
import GraphWidget
import SphereWidget
import SidebarButtons
# OpenGL imports
from OpenGL.GL import *
from OpenGL.GLU import *
import logging

LOG = logging.getLogger(__name__)



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MassFlight")
        self.setGeometry(100, 100, 1400, 800)
        self.current_active_button = None
        self.set_theme()
        self.initUI()
        
    def set_theme(self):
        self.setStyleSheet("QMainWindow { background-color: #1a1a1a; } QLabel { color: white; }")
        
    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        sidebar = self.create_sidebar()
        main_layout.addWidget(sidebar)
        
        self.content_area = self.create_content_area()
        main_layout.addWidget(self.content_area)
        
        central_widget.setLayout(main_layout)
        
    def create_sidebar(self):
        sidebar = QFrame()
        sidebar.setFixedWidth(400)
        sidebar.setStyleSheet("QFrame { background-color: #252525; border-right: 2px solid #333; }")
        
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setContentsMargins(20, 40, 20, 40)
        sidebar_layout.setSpacing(15)
        
        title = QLabel("MAIN MENU")
        title.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 24px;
                font-weight: bold;
                padding: 20px 0px;
                border-bottom: 2px solid #333;
            }
        """)
        title.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(title)
        sidebar_layout.addSpacing(30)
        
        buttons_data = [
            ("World View", 0),
            ("Altitude", 1),
            ("Latitude", 2),
            ("Velocity", 3)
        ]
        
        self.buttons = []
        for text, index in buttons_data:
            btn = SidebarButtons.SidebarButton(text)
            btn.clicked.connect(lambda checked, idx=index: self.switch_page(idx))
            self.buttons.append(btn)
            sidebar_layout.addWidget(btn)
        
        sidebar_layout.addStretch()
        
        footer = QLabel("Data Analytics v1.0")
        footer.setStyleSheet("QLabel { color: #666; font-size: 12px; padding: 10px; border-top: 1px solid #333; }")
        footer.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(footer)
        
        sidebar.setLayout(sidebar_layout)
        return sidebar
        
    def create_content_area(self):
        content_frame = QFrame()
        content_frame.setStyleSheet("QFrame { background-color: #1e1e1e; }")
        
        self.stacked_widget = QStackedWidget()
        
        # Create pages - World View now uses SphereWidget
        self.pages = [
            SphereWidget.SphereWidget(),  # World View with 3D sphere
            GraphWidget.GraphWidget("Altitude Over Time"),
            GraphWidget.GraphWidget("Latitude Changes"),
            GraphWidget.GraphWidget("Velocity Trends")
        ]
        
        for page in self.pages:
            self.stacked_widget.addWidget(page)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.addWidget(self.stacked_widget)
        
        content_frame.setLayout(layout)
        return content_frame
        
    def switch_page(self, index):
        self.stacked_widget.setCurrentIndex(index)
        
        # Reset all buttons to normal state
        for btn in self.buttons:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {btn.normal_color};
                    color: white;
                    border: none;
                    padding: 15px;
                    text-align: left;
                    font-size: 14px;
                    font-weight: bold;
                    border-radius: 8px;
                }}
                QPushButton:hover {{
                    background-color: {btn.hover_color};
                }}
                QPushButton:pressed {{
                    background-color: {btn.active_color};
                }}
            """)
        
        # Set active state for clicked button
        active_btn = self.buttons[index]
        active_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {active_btn.active_color};
                color: white;
                border: none;
                padding: 15px;
                text-align: left;
                font-size: 14px;
                font-weight: bold;
                border-radius: 8px;
                border-left: 4px solid #4ecdc4;
            }}
            QPushButton:hover {{
                background-color: {active_btn.active_color};
            }}
        """)

