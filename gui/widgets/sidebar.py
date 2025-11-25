#472-469

from PyQt5.QtWidgets import QPushButton
import logging

from config.app_config import THEME

logger = logging.getLogger(__name__)

class SidebarButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.normal_color = THEME['button_normal']
        self.hover_color = THEME['button_hover']
        self.active_color = THEME['button_active']
        self.text_color = THEME['text']
        self.left_border_color = THEME['left_border_color']

        self._is_active = False
        self.update_style()
        

    def update_style(self):
        if self._is_active:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.active_color};
                    color: {self.text_color};
                    border: none;
                    padding: 15px;
                    text-align: left;
                    font-size: 14px;
                    font-weight: bold;
                    border-radius: 8px;
                    left-border: 5px solid {self.left_border_color};
                }}
                QPushButton:hover {{
                    background-color: {self.hover_color};
                }}
                QPushButton:pressed {{
                    background-color: {self.active_color};
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.normal_color};
                    color: {self.text_color};
                    border: none;
                    padding: 15px;
                    text-align: left;
                    font-size: 14px;
                    border-radius: 8px;
                    left-border: 5px solid transparent;
                }}
                QPushButton:hover {{
                    background-color: {self.hover_color};
                }}
                QPushButton:pressed {{
                    background-color: {self.active_color};
                }}
            """)
    
    def set_active(self, active):
        self._is_active = active
        self.update_style()
        
    def is_active(self) -> bool:
        return self._is_active
    