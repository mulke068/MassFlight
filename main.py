import logging

from gui.interface.app import MyApp

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

if __name__ == "__main__":
    LOG = logging.getLogger("main")
    print("Hello, World!")

    myApp = MyApp()
    myApp.mainloop()