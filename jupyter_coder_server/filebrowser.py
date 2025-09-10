import os
import pathlib
import shutil

try:
    from jupyter_coder_server.utils import (
        LOGGER,
        untar,
        download,
        get_icon,
        get_github_json,
    )
except ImportError:
    from .utils import LOGGER, untar, download, get_icon, get_github_json

WEB_FILE_BROWSER_RELEASES = (
    "https://api.github.com/repos/filebrowser/filebrowser/releases/{version}"
)
FILE_BROWSER_DATABASE = os.environ.get("FILE_BROWSER_DATABASE", "/tmp/filebrowser.db")
FILE_BROWSER_IMG_PROCESSORS = int(os.environ.get("FILE_BROWSER_IMG_PROCESSORS", "4"))
FILE_BROWSER_ROOT_PATH = os.environ.get("FILE_BROWSER_ROOT_PATH", "/")


def get_file_browser_base_url():
    """Get the base URL for file browser, considering Jupyter's base_url.

    Tries multiple methods to detect Jupyter's base_url:
    1. jupyter-lab --show-config-json | jq .ServerApp.base_url
    2. ps command to find ServerApp.base_url parameter
    3. JUPYTER_SERVER_URL environment variable (fallback)
    """
    import subprocess
    import json
    import re

    base_url = os.environ.get("FILE_BROWSER_BASE_URL", "/vscode_server_fb")
    jupyter_base = None

    # Method 1: Try jupyter config
    try:
        result = subprocess.run(
            ["jupyter-lab", "--show-config-json"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            config = json.loads(result.stdout)
            if "ServerApp" in config and "base_url" in config["ServerApp"]:
                server_base_url = config["ServerApp"]["base_url"]
                if server_base_url and server_base_url != "/":
                    jupyter_base = server_base_url.rstrip("/")
    except (
        subprocess.TimeoutExpired,
        json.JSONDecodeError,
        KeyError,
        FileNotFoundError,
    ):
        pass

    # Method 2: Try ps command if first method failed
    if jupyter_base is None:
        try:
            result = subprocess.run(
                ["ps", "axu"], capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                # Look for ServerApp.base_url in process arguments
                pattern = r"--ServerApp\.base_url=([^\s]+)"
                matches = re.findall(pattern, result.stdout)
                if matches:
                    server_base_url = matches[0]
                    if server_base_url and server_base_url != "/":
                        jupyter_base = server_base_url.rstrip("/")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

    # Method 3: Fallback to JUPYTER_SERVER_URL (original method)
    if jupyter_base is None:
        jupyter_server_url = os.environ.get("JUPYTER_SERVER_URL", "")
        if jupyter_server_url:
            from urllib.parse import urlparse

            parsed = urlparse(jupyter_server_url)
            if parsed.path and parsed.path != "/":
                jupyter_base = parsed.path.rstrip("/")

    # Construct final URL
    if jupyter_base:
        return f"{jupyter_base}{base_url}"

    return base_url


FILE_BROWSER_BASE_URL = get_file_browser_base_url()


class WebFileBrowser:
    def __init__(self, version: str = "latest", install_dir: str = "~/.local"):
        self.WEB_FILE_BROWSER_VERSION = os.environ.get(
            "WEB_FILE_BROWSER_VERSION", version
        )
        self.install_dir: pathlib.Path = pathlib.Path(
            os.environ.get("WEB_FILE_BROWSER_INSTALL_DIR", install_dir)
        ).expanduser()

    def check_install(self):
        filebrowser_file = self.install_dir.joinpath("bin/filebrowser")
        LOGGER.info(f"filebrowser: {filebrowser_file}")
        if filebrowser_file.exists():
            LOGGER.info("filebrowser is already installed")
            return True
        else:
            LOGGER.warning("filebrowser is not installed")
            return False

    def install_filebrowser(self):
        """
        https://filebrowser.org/installation
        """

        LOGGER.info(f"install_dir: {self.install_dir}")
        LOGGER.info(f"WEB_FILE_BROWSER_VERSION: {self.WEB_FILE_BROWSER_VERSION}")

        if self.WEB_FILE_BROWSER_VERSION.startswith("v"):
            api_link = WEB_FILE_BROWSER_RELEASES.format(
                version=f"tags/{self.WEB_FILE_BROWSER_VERSION}"
            )
        else:
            api_link = WEB_FILE_BROWSER_RELEASES.format(
                version=self.WEB_FILE_BROWSER_VERSION
            )

        release_dict = get_github_json(api_link)

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

        filebrowser_file = self.install_dir.joinpath("bin/filebrowser")
        LOGGER.info(f"filebrowser_file: {filebrowser_file}")

        if filebrowser_file.exists():
            LOGGER.warning("filebrowser_file is already installed")
            return

        self.install_dir.joinpath("bin").mkdir(parents=True, exist_ok=True)

        download_file = pathlib.Path("/tmp/").joinpath(download_url.split("/")[-1])

        if download_file.exists():
            LOGGER.info(f"{download_file} is already exists")
        else:
            LOGGER.info("Downloading filebrowser")
            download(download_url, download_file)

        self.clean_up()

        output_path = self.install_dir.joinpath("lib/file-browser")
        if not output_path.exists():
            untar(download_file, output_path=str(output_path))
        else:
            LOGGER.info(f"{output_path.stem} is already exists")

        bin_symlink_path = self.install_dir.joinpath("bin/filebrowser")
        if bin_symlink_path.exists():
            if bin_symlink_path.is_symlink():
                bin_symlink_path.unlink()
            else:
                shutil.rmtree(bin_symlink_path)
        bin_symlink_path.symlink_to(output_path.joinpath("filebrowser"))

    def clean_up(self, full: bool = False):
        LOGGER.info(f"Clean up {self.__class__.__name__}")
        files_to_remove = [self.install_dir.joinpath("bin/filebrowser")]
        if full:
            files_to_remove.append(self.install_dir.joinpath("lib/file-browser"))

            for file in pathlib.Path("/tmp/").glob("*filebrowser.tar.gz"):
                files_to_remove.append(file)

        for file in files_to_remove:
            if file.exists():
                LOGGER.info(f"Remove {file}")

                if file.is_symlink():
                    file.unlink()
                    continue

                if file.is_dir():
                    shutil.rmtree(file)
                else:
                    file.unlink()

    def full_install(self):
        self.install_filebrowser()

    @classmethod
    def setup_proxy(cls: "WebFileBrowser"):
        if not cls().check_install():
            cls().full_install()

        return {
            "command": [
                "filebrowser",
                "--noauth",
                f"--root={FILE_BROWSER_ROOT_PATH}",
                f"--baseurl={FILE_BROWSER_BASE_URL}",
                f"--database={FILE_BROWSER_DATABASE}",
                f"--img-processors={FILE_BROWSER_IMG_PROCESSORS}",
                "--address=0.0.0.0",
                "--port={port}",
            ],
            # "timeout": 10,
            "launcher_entry": {
                "title": "Web File Browser",
                "icon_path": get_icon("filebrowser"),
            },
        }
