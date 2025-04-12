import requests
import os
import pathlib
import shutil
try:
    from jupyter_coder_server.utils import LOGGER, untar, download, get_icon
except ImportError:
    from utils import LOGGER, untar, download, get_icon

WEB_FILE_BROWSER_RELEASES = "https://api.github.com/repos/filebrowser/filebrowser/releases/{version}"
FILE_BROWSER_DATABASE = os.environ.get("FILE_BROWSER_DATABASE", "/tmp/filebrowser.db")
FILE_BROWSER_IMG_PROCESSORS = int(os.environ.get("FILE_BROWSER_IMG_PROCESSORS", "4"))

class WebFileBrowser():
    def __init__(self, version : str = "latest", install_dir : str = "~/.local"):
        self.WEB_FILE_BROWSER_VERSION = os.environ.get("WEB_FILE_BROWSER_VERSION", version)
        self.install_dir : pathlib.Path = pathlib.Path(os.environ.get("WEB_FILE_BROWSER_INSTALL_DIR", install_dir)).expanduser()

    def install_filebrowser(self):
        """
        https://filebrowser.org/installation
        """

        LOGGER.info(f"install_dir: {self.install_dir}")
        LOGGER.info(f"WEB_FILE_BROWSER_VERSION: {self.WEB_FILE_BROWSER_VERSION}")

        if self.WEB_FILE_BROWSER_VERSION.startswith("v"):
            api_link = WEB_FILE_BROWSER_RELEASES.format(version=f"tags/{self.WEB_FILE_BROWSER_VERSION}")
        else:
            api_link = WEB_FILE_BROWSER_RELEASES.format(version=self.WEB_FILE_BROWSER_VERSION)
        
        response = requests.get(api_link,
            headers={
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
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
        
        self.install_dir.joinpath("bin/filebrowser").symlink_to(output_path.joinpath("filebrowser"))

    def clean_up(self, full : bool = False):
        LOGGER.info("Clean up")
        files_to_remove = [
            self.install_dir.joinpath("bin/filebrowser")
        ]
        if full:
            files_to_remove.append(self.install_dir.joinpath("lib/file-browser"))
            
            for file in pathlib.Path("/tmp/").glob("*filebrowser.tar.gz"):
                files_to_remove.append(file)
            
        for file in files_to_remove:
            if file.exists():
                LOGGER.info(f"Remove {file}")
                if file.is_dir():
                    shutil.rmtree(file)
                else:
                    file.unlink()
    
    def full_install(self):
        self.install_filebrowser()
    
    @staticmethod
    def setup_proxy():
        return {
            "command": [
                "filebrowser",
                "--noauth",
                "--root=/home",
                "--baseurl=/vscode_server_fb",
                f"--database={FILE_BROWSER_DATABASE}",
                f"--img-processors={FILE_BROWSER_IMG_PROCESSORS}",
                "--address=0.0.0.0",
                "--port={port}",
            ],
            # "timeout": 10,
            "launcher_entry": {
                "title": "Web File Browser",
                "icon_path" : get_icon("filebrowser")
            },
        }