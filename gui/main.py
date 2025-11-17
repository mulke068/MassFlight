import logging
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT) 

from interface import MyApp

LOG = logging.getLogger(__name__)


# ROOT = os.path.dirname(os.path.dirname(__file__))



if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    # Run the application
    myApp = MyApp()

    myApp.mainloop()