
from PyQt5.QtWidgets import QMainWindow

from config.app_config import APP_NAME, WINDOW_HEIGHT, WINDOW_WIDTH
from gui.engine.sphere import Sphere
from gui.widgets.graph import GraphWidget
from gui.widgets.sidebar import SidebarButton
import logging

LOG = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setWindowTitle(APP_NAME)
        self.setGeometry(100,100, WINDOW_WIDTH, WINDOW_HEIGHT)
        
        self.pages = []
        
        self.set_theme()
        self.initUI()

        LOG.info("Main window initialized")
    
    def initUI(self):
        pass
    
    def sidebar(self):
        pass

    def content_area(self):
        
        self.pages = [
            Sphere(),
            
        ]
        pass
    
    def page_switch(self, index):
        LOG.info(f"Switched to page {index}")
        pass

    def set_theme(self):
        pass

    def closeEvent(self, a0):
        LOG.info("Application closing")
        a0.accept()
        return super().closeEvent(a0)