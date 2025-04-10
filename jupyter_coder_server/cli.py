import requests
import logging
import os
import pathlib
from tornado import websocket
import json
import argparse

try:
    from jupyter_coder_server.version import __version__
    from jupyter_coder_server.options import (
        CODE_SERVER_RELEASES,
        CODE_SERVER_VERSION,
        DEFAULT_EXTENSIONS,
        DEFAULT_SETTINGS,
        CODE_SERVER_INSTALL_DIR,
        FILE_BROWSER_RELEASES,
        FILE_BROWSER_VERSION,
    )
except ImportError:
    from options import (
        CODE_SERVER_RELEASES,
        CODE_SERVER_VERSION,
        DEFAULT_EXTENSIONS,
        DEFAULT_SETTINGS,
        CODE_SERVER_INSTALL_DIR,
        FILE_BROWSER_RELEASES,
        FILE_BROWSER_VERSION,
    )

    __version__ = "__dev__"

LOGGER = logging.getLogger("jupyter_coder_server")
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

    install_dir = pathlib.Path(os.path.expanduser(CODE_SERVER_INSTALL_DIR))
    package_file = install_dir.joinpath("lib/code-server/package.json")

    LOGGER.info(f"package_file: {package_file}")

    if package_file.exists():
        LOGGER.warning("code-server is already installed")
        with open(package_file, "r") as f:
            package_json = json.load(f)
            installed_version = package_json["version"]
            LOGGER.info(f"installed_version: {installed_version}")
            if installed_version == latest_tag:
                LOGGER.info("code-server is already up to date")
                if os.path.exists(f"{CODE_SERVER_INSTALL_DIR}/bin/code-server"):
                    return
            else:
                LOGGER.info("code-server is outdated")
                LOGGER.info("updating code-server")

    (install_dir / "lib").mkdir(parents=True, exist_ok=True)
    (install_dir / "lib").mkdir(parents=True, exist_ok=True)

    os.system(f"curl -fL {download_url} | tar -C {CODE_SERVER_INSTALL_DIR}/lib -xz")
    os.system(
        f"rm -rf {CODE_SERVER_INSTALL_DIR}/lib/code-server {CODE_SERVER_INSTALL_DIR}/bin/code-server"
    )
    os.system(
        f"mv {CODE_SERVER_INSTALL_DIR}/lib/code-server-{latest_tag}-linux-amd64 {CODE_SERVER_INSTALL_DIR}/lib/code-server"
    )
    os.system(
        f"ln -s {CODE_SERVER_INSTALL_DIR}/lib/code-server/bin/code-server {CODE_SERVER_INSTALL_DIR}/bin/code-server"
    )


def install_extensions():
    """
    https://coder.com/docs/user-guides/workspace-access/vscode#adding-extensions-to-custom-images
    """
    code_server_string = [
        "code-server",
        "--disable-telemetry",
        "--disable-update-check",
        "--disable-workspace-trust",
        f"--extensions-dir {CODE_SERVER_INSTALL_DIR}/share/code-server/extensions",
        "--install-extension",
        "{extension}",
    ]
    install_dir = pathlib.Path(os.path.expanduser(CODE_SERVER_INSTALL_DIR))
    (install_dir / "share/code-server/extensions").mkdir(parents=True, exist_ok=True)

    for extension in DEFAULT_EXTENSIONS:
        LOGGER.info(f"installing extension: {extension}")
        os.system(" ".join(code_server_string).format(extension=extension))


def install_settings():
    install_dir = pathlib.Path(os.path.expanduser(CODE_SERVER_INSTALL_DIR))

    for profile in ["User", "Machine"]:
        profile_dir = install_dir.joinpath(f"share/code-server/{profile}")
        profile_dir.mkdir(parents=True, exist_ok=True)

        settings_file = profile_dir.joinpath("settings.json")

        settings = {}
        if settings_file.exists():
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


def install_filebrowser():
    """
    https://filebrowser.org/installation
    """
    LOGGER.info(f"FILE_BROWSER_VERSION: {FILE_BROWSER_VERSION}")

    response = requests.get(
        FILE_BROWSER_RELEASES.format(version=FILE_BROWSER_VERSION),
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
        if assets["name"] == "linux-amd64-filebrowser.tar.gz":
            download_url = assets["browser_download_url"]
            LOGGER.info(f"download_url: {download_url}")
            break

    assert download_url is not None, "download_url is None"

    install_dir = pathlib.Path(os.path.expanduser(CODE_SERVER_INSTALL_DIR))
    filebrowser_file = install_dir.joinpath("bin/filebrowser")

    LOGGER.info(f"filebrowser_file: {filebrowser_file}")

    if filebrowser_file.exists():
        LOGGER.warning("filebrowser_file is already installed")
        return

    (install_dir / "bin" / "file-browser").mkdir(parents=True, exist_ok=True)

    os.system(
        f"rm -rf {CODE_SERVER_INSTALL_DIR}/bin/filebrowser {CODE_SERVER_INSTALL_DIR}/bin/file-browser/*"
    )
    os.system(
        f"curl -fL {download_url} | tar -C {CODE_SERVER_INSTALL_DIR}/bin/file-browser -xz"
    )
    os.system(
        f"ln -s {CODE_SERVER_INSTALL_DIR}/bin/file-browser/filebrowser {CODE_SERVER_INSTALL_DIR}/bin/filebrowser"
    )


def install_all():
    install_server()
    install_settings()
    patch_tornado()
    install_extensions()
    install_filebrowser()


def main():
    config = argparse.ArgumentParser(prog="jupyter_coder_server")
    config.add_argument(
        "--version", action="version", version=f"%(prog)s: {__version__}"
    )
    config.add_argument(
        "--install",
        action="store_true",
        help="Install code-server, extensions ad settings",
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
        "--install-filebrowser", action="store_true", help="Install Web File Browser"
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

    if args.install or args.install_filebrowser:
        install_filebrowser()
