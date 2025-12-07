import os

# weather manager
MAX_FETCH_ATTEMPTS = 5
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_FILE = os.path.join(_project_root, "assets", "stations.json")