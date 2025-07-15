import argparse

try:
    from jupyter_coder_server.version import __version__
    from jupyter_coder_server.coder_server import CoderServer
    from jupyter_coder_server.filebrowser import WebFileBrowser

except ImportError:
    from .coder_server import CoderServer
    from .filebrowser import WebFileBrowser

    __version__ = "__dev__"


def main():
    config = argparse.ArgumentParser(prog="jupyter_coder_server")
    config.add_argument(
        "--version", action="version", version=f"%(prog)s: {__version__}"
    )
    config.add_argument(
        "--install",
        action="store_true",
        help="Install coder-server, extensions, settings and Web File Browser",
    )
    config.add_argument(
        "--install-server", action="store_true", help="Install coder-server"
    )
    config.add_argument(
        "--install-extensions", action="store_true", help="Install extensions"
    )
    config.add_argument(
        "--install-settings", action="store_true", help="Install settings"
    )
    config.add_argument(
        "--install-filebrowser", action="store_true", help="Install Web File Browser"
    )
    config.add_argument(
        "--patch-tornado", action="store_true", help="Monkey patch tornado.websocket"
    )
    config.add_argument(
        "--remove", action="store_true", help="Remove coder-server and Web File Browser"
    )
    config.add_argument(
        "--remove-server", action="store_true", help="Remove coder-server"
    )
    config.add_argument(
        "--remove-filebrowser", action="store_true", help="Remove Web File Browser"
    )

    args = config.parse_args()

    server = CoderServer()
    file_browser = WebFileBrowser()

    if args.install or args.install_server:
        server.install_server()

    if args.install or args.install_settings:
        server.install_settings()

    if args.install or args.patch_tornado:
        server.patch_tornado()

    if args.install or args.install_extensions:
        server.install_extensions()

    if args.install or args.install_filebrowser:
        file_browser.install_filebrowser()

    if args.remove or args.remove_server:
        server.clean_up(full=True)

    if args.remove or args.remove_filebrowser:
        file_browser.clean_up(full=True)
