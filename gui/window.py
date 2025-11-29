
from PyQt5.QtWidgets import QMainWindow, QHBoxLayout, QVBoxLayout, QStackedWidget, QFrame, QWidget
from config.app_config import APP_NAME, WINDOW_HEIGHT, WINDOW_WIDTH, THEME
from .widgets import sphere as sphere
from .widgets import graph as graph
from .widgets import sidebar as sidebar
import logging

LOG = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setWindowTitle(APP_NAME)
        self.setGeometry(100,100, WINDOW_WIDTH, WINDOW_HEIGHT)
        self.pages = []
        self.setStyleSheet(f"QMainWindow {{ background-color: {THEME['background']}; }} QLabel {{ color: {THEME['text']}; }}")

        self.initUI()

        LOG.info("Main window initialized")
    
    def initUI(self):
        main_layout = QHBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.sidebar_area())
        main_layout.addWidget(self.content_area())

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_widget.setLayout(main_layout)
    
    def sidebar_area(self):
        sidebar_frame = QFrame()
        sidebar_frame.setFixedWidth(400)
        sidebar_frame.setStyleSheet(f"QFrame {{ background-color: {THEME['sidebar']}; border-right: 2px solid #333; }}")
        
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setContentsMargins(20, 40, 20, 40)
        sidebar_layout.setSpacing(15)
        
        buttons_data = [
            ("World View", 0),
            ("Altitude", 1),
            ("Latitude", 2),
            ("Velocity", 3)
        ]
        
        self.button_group = []
        for text, index in buttons_data:
            button = sidebar.SidebarButton(text)
            button.clicked.connect(lambda checked, idx=index: self.switch_page(idx))
            self.button_group.append(button)
            sidebar_layout.addWidget(button)

        sidebar_frame.setLayout(sidebar_layout)
        return sidebar_frame

    def content_area(self):
        content_frame = QFrame()
        content_frame.setStyleSheet(f"QFrame {{ background-color: {THEME['background']}; }}")
        
        self.stacked_widget = QStackedWidget()
        
        self.pages = [
            sphere.SphereWidget(),
            graph.GraphWidget(graph_type='Altitude'),
            graph.GraphWidget(graph_type='Latitude'),
            graph.GraphWidget(graph_type='Velocity')
            
        ]
        for page in self.pages:
            self.stacked_widget.addWidget(page)
        
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.addWidget(self.stacked_widget)
        
        content_frame.setLayout(content_layout)
        return content_frame

    def page_switch(self, index):
        self.stacked_widget.setCurrentIndex(index)
        
        for button in self.button_group:
            sidebar.SidebarButton()

        LOG.info(f"Switched to page {index}")


    def closeEvent(self, a0):
        LOG.info("Application closing")
        a0.accept()
        return super().closeEvent(a0)