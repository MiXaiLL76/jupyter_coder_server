from .version import __version__, __author__
from .cli import main
from .coder_server import CoderServer
from .filebrowser import WebFileBrowser
from .utils import install_labextensions

__all__ = [
    "__version__",
    "__author__",
    "CoderServer",
    "WebFileBrowser",
    "install_labextensions",
    "main",
]
