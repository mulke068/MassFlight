from PyQt5.QtWidgets import QPushButton
from config.app_config import THEME


class SidebarButtonWidget(QPushButton):
    """Styled navigation button for sidebar"""
    
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.normal_color = THEME['button_normal']
        self.hover_color = THEME['button_hover']
        self.active_color = THEME['button_active']
        self.accent_color = THEME['accent']
        
        self._is_active = False
        self.update_style()
    
    def update_style(self):
        """Update button stylesheet"""
        if self._is_active:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.active_color};
                    color: white;
                    border: none;
                    padding: 15px;
                    text-align: left;
                    font-size: 14px;
                    font-weight: bold;
                    border-radius: 8px;
                    border-left: 4px solid {self.accent_color};
                }}
                QPushButton:hover {{
                    background-color: {self.active_color};
                }}
            """)
        else:
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
    
    def set_active(self, active):
        """Set button active state"""
        self._is_active = active
        self.update_style()
    
    def is_active(self):
        """Check if button is active"""
        return self._is_active