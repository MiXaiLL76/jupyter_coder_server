import os
import sys

CODE_SERVER_RELEASES = (
    "https://api.github.com/repos/coder/code-server/releases/{version}"
)
CODE_SERVER_VERSION = os.environ.get("CODE_SERVER_VERSION", "latest")
CODE_SERVER_INSTALL_DIR = os.environ.get("CODE_SERVER_INSTALL_DIR", "~/.local")

FILE_BROWSER_RELEASES = (
    "https://api.github.com/repos/filebrowser/filebrowser/releases/{version}"
)
FILE_BROWSER_VERSION = os.environ.get("FILE_BROWSER_VERSION", "latest")

DEFAULT_EXTENSIONS = [
    "ms-python.python",
    "ms-toolsai.jupyter",
    "charliermarsh.ruff",
]

DEFAULT_SETTINGS = {
    "User": {
        "window.menuBarVisibility": "classic",
        "workbench.startupEditor": "none",
        "files.autoSave": "onWindowChange",
        "explorer.confirmDragAndDrop": False,
        "ruff.path": [os.path.join(os.path.dirname(sys.executable), "ruff")],
        "editor.defaultFormatter": "charliermarsh.ruff",
        "notebook.defaultFormatter": "charliermarsh.ruff",
        "ruff.interpreter": [sys.executable],
        "editor.formatOnSave": True,
        "notebook.formatOnSave.enabled": True,
        "terminal.integrated.fontFamily": "Consolas",
        "terminal.integrated.detectLocale": "off",
    },
    "Machine": {
        "workbench.startupEditor": "none",
        "terminal.integrated.detectLocale": "off",
        "python.defaultInterpreterPath": sys.executable,
    },
}
