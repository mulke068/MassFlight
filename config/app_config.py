class AppConfig:
    # Application configurations
    VERSION = "v0.7"
    APP_NAME = "MassFlight"

    # Default color palettes
    APPARENCE_MODE = "System"
    LIGHTMODE_BUTTON_COLOR = "#CECECE"
    LIGHTMODE_TEXT_COLOR = "#000000"
    DARKMODE_BUTTON_COLOR = "#313131"
    DARKMODE_TEXT_COLOR = "#FFFFFF"

    # Window configurations
    WINDOW_WIDTH = 1000
    WINDOW_HEIGHT = 900
    MIN_WINDOW_WIDTH = 600
    MIN_WINDOW_HEIGHT = 500

    # Button configurations
    BUTTON_PADDING_X = 10
    BUTTON_PADDING_Y = 10

    # Graph configurations
    GRAPH_DPI = 100
    GRAPH_FIGURE_SIZE = (6, 5)


    # 3D Visualization configurations
    # Control sensitivity
    ZOOM_RESOLUTION = 0.5
    ROTATION_SENSITIVITY = 0.5
    PANNING_SENSITIVITY = 0.01
    FOCAL_LENGTH = 60  # Field of view for 3D perspective
