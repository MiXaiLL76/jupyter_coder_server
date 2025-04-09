import requests
import logging
import os
import pathlib
from tornado import websocket
import json
import argparse

try:
    from jupyter_code_server.version import __version__
    from jupyter_code_server.options import (
        CODE_SERVER_RELEASES,
        CODE_SERVER_VERSION,
        DEFAULT_EXTENSIONS,
        DEFAULT_SETTINGS,
    )
except ImportError:
    from options import (
        CODE_SERVER_RELEASES,
        CODE_SERVER_VERSION,
        DEFAULT_EXTENSIONS,
        DEFAULT_SETTINGS,
    )

    __version__ = "__dev__"

LOGGER = logging.getLogger("jupyter_code_server")
LOGGER.setLevel(logging.INFO)
logging.debug("logger")


def install_server():
    """
    https://coder.com/docs/code-server/install
    """
    LOGGER.info(f"CODE_SERVER_VERSION: {CODE_SERVER_VERSION}")

    response = requests.get(
        CODE_SERVER_RELEASES.format(version=CODE_SERVER_VERSION),
        headers={"Accept": "application/vnd.github+json"},
    )

    assert response.status_code == 200, response.text

    release_dict = response.json()

    latest_tag = release_dict["tag_name"]
    LOGGER.info(f"latest_tag: {latest_tag}")

    if latest_tag.startswith("v"):
        latest_tag = latest_tag[1:]

    download_url = None
    for assets in release_dict["assets"]:
        if assets["name"] == f"code-server-{latest_tag}-linux-amd64.tar.gz":
            download_url = assets["browser_download_url"]
            LOGGER.info(f"download_url: {download_url}")
            break

    assert download_url is not None, "download_url is None"

    package_file = os.path.expanduser("~/.local/lib/code-server/package.json")

    if os.path.exists(package_file):
        LOGGER.warning("code-server is already installed")
        with open(package_file, "r") as f:
            package_json = json.load(f)
            installed_version = package_json["version"]
            LOGGER.info(f"installed_version: {installed_version}")
            if installed_version == latest_tag:
                LOGGER.info("code-server is already up to date")
                return
            else:
                LOGGER.info("code-server is outdated")
                LOGGER.info("updating code-server")

    pathlib.Path(os.path.expanduser("~/.local/bin/")).mkdir(parents=True, exist_ok=True)
    pathlib.Path(os.path.expanduser("~/.local/lib/")).mkdir(parents=True, exist_ok=True)

    os.system(f"curl -fL {download_url} | tar -C ~/.local/lib -xz")
    os.system("rm -rf ~/.local/lib/code-server ~/.local/bin/code-server")
    os.system(
        f"mv ~/.local/lib/code-server-{latest_tag}-linux-amd64 ~/.local/lib/code-server"
    )
    os.system("ln -s ~/.local/lib/code-server/bin/code-server ~/.local/bin/code-server")


def install_extensions():
    """
    https://coder.com/docs/user-guides/workspace-access/vscode#adding-extensions-to-custom-images
    """
    code_server_string = [
        "code-server",
        "--disable-telemetry",
        "--disable-update-check",
        "--disable-workspace-trust",
        "--extensions-dir ~/.local/share/code-server/extensions",
        "--install-extension",
        "{extension}",
    ]
    pathlib.Path(os.path.expanduser("~/.local/share/code-server/extensions")).mkdir(
        parents=True, exist_ok=True
    )

    for extension in DEFAULT_EXTENSIONS:
        LOGGER.info(f"installing extension: {extension}")
        os.system(" ".join(code_server_string).format(extension=extension))


def install_settings():
    for profile in ["User", "Machine"]:
        pathlib.Path(
            os.path.expanduser(f"~/.local/share/code-server/{profile}/")
        ).mkdir(parents=True, exist_ok=True)

        settings_file = os.path.expanduser(
            f"~/.local/share/code-server/{profile}/settings.json"
        )
        settings = {}
        if os.path.exists(settings_file):
            LOGGER.warning(f"settings.json allready exists for {profile}")

            with open(settings_file) as fd:
                settings = json.load(fd)

        for key, value in DEFAULT_SETTINGS[profile].items():
            if key not in settings:
                settings[key] = value

        with open(settings_file, "w") as f:
            json.dump(settings, f, indent=4)

        LOGGER.info(f"settings.json for {profile} installed")


def patch_tornado():
    if websocket._default_max_message_size == 10 * 1024 * 1024:
        LOGGER.info("monkey patch for tornado.websocket")

        with open(websocket.__file__) as fd:
            data = fd.read()
            data = data.replace(
                "_default_max_message_size = 10 * 1024 * 1024",
                "_default_max_message_size = 1024 * 1024 * 1024",
            )

        with open(websocket.__file__, "w") as fd:
            fd.write(data)

        LOGGER.info("DONE!")


def install_all():
    install_server()
    install_settings()
    patch_tornado()
    install_extensions()


def main():
    config = argparse.ArgumentParser(prog="jupyter_code_server")
    config.add_argument(
        "--version", action="version", version=f"%(prog)s: {__version__}"
    )
    config.add_argument(
        "--install", action="store_true", help="Install code-server and extensions"
    )
    config.add_argument(
        "--install-server", action="store_true", help="Install code-server"
    )
    config.add_argument(
        "--install-extensions", action="store_true", help="Install extensions"
    )
    config.add_argument(
        "--install-settings", action="store_true", help="Install settings"
    )
    config.add_argument(
        "--patch-tornado", action="store_true", help="Monkey patch tornado.websocket"
    )
    args = config.parse_args()

    if args.install or args.install_server:
        install_server()

    if args.install or args.install_settings:
        install_settings()

    if args.install or args.patch_tornado:
        patch_tornado()

    if args.install or args.install_extensions:
        install_extensions()
