import logging


LOG = logging.getLogger(__name__)


class OffscreenRenderer:
    def __init__(self, width = 600, height = 400):
        self.width = width
        self.height = height
        
        self.window = None
        self.scene = None
        