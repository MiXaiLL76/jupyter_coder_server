from .version import __version__, __author__
from .serverproxy import setup_jupyter_coder_server, setup_filebrowser
from .cli import main

__all__ = [
    "__version__",
    "__author__",
    "setup_jupyter_coder_server",
    "setup_filebrowser",
    "main",
]
