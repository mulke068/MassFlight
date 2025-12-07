import sys
from PyQt6.QtWidgets import QApplication

def check_imports():
    print("Checking imports...")
    try:
        from gui.widgets.graph import GraphWidget, GraphType
        print("GraphWidget imported.")
        
        from gui.widgets.dashboard import DashboardWidget
        print("DashboardWidget imported.")
        
        from gui.window import MainWindow
        print("MainWindow imported.")
        
        print("SUCCESS: All UI components imported.")
    except Exception as e:
        print(f"FAILURE: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # creating QApplication context just in case, though imports should work without it usually
    app = QApplication(sys.argv)
    check_imports()
