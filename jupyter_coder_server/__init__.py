from .version import __version__, __author__
from .cli import main
from .coder_server import CoderServer
from .filebrowser import WebFileBrowser
from .utils import install_labextensions


def _load_jupyter_server_extension(server_app):
    server = CoderServer()
    file_browser = WebFileBrowser()

    if not server.check_install():
        server.full_install()

    if not file_browser.check_install():
        file_browser.full_install()

    server_app.log.info("Loaded extension jupyter_coder_server")


__all__ = [
    "__version__",
    "__author__",
    "CoderServer",
    "WebFileBrowser",
    "install_labextensions",
    "main",
    "_load_jupyter_server_extension",
]
