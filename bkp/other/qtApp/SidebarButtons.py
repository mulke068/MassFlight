

from PyQt5.QtWidgets import QPushButton
from OpenGL.GL import *
from OpenGL.GLU import *

class SidebarButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.normal_color = "#2d3848"
        self.hover_color = "#3f4e63"
        self.active_color = "#56687e"
        
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.normal_color};
                color: white;
                border: none;
                padding: 15px;
                text-align: left;
                font-size: 14px;
                font-weight: bold;
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background-color: {self.hover_color};
            }}
            QPushButton:pressed {{
                background-color: {self.active_color};
            }}
        """)

