import os
import pathlib
import json
import sys
import shutil

try:
    from jupyter_coder_server.utils import (
        LOGGER,
        untar,
        download,
        start_cmd,
        get_icon,
        get_github_json,
    )
except ImportError:
    from .utils import LOGGER, untar, download, start_cmd, get_icon, get_github_json

CODE_SERVER_RELEASES = (
    "https://api.github.com/repos/coder/code-server/releases/{version}"
)

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


class CoderServer:
    def __init__(self, version: str = "latest", install_dir: str = "~/.local"):
        self.CODE_SERVER_VERSION = os.environ.get("CODE_SERVER_VERSION", version)
        self.install_dir: pathlib.Path = pathlib.Path(
            os.environ.get("CODE_SERVER_INSTALL_DIR", install_dir)
        ).expanduser()
        self.package_file: pathlib.Path = self.install_dir.joinpath(
            "lib/code-server/package.json"
        )

    def check_install(self):
        code_server_file = self.install_dir.joinpath("bin/code-server")
        LOGGER.info(f"code-server: {code_server_file}")
        if code_server_file.exists():
            LOGGER.info("code-server is already installed")
            return True
        else:
            LOGGER.warning("code-server is not installed")
            return False

    def install_server(self):
        """
        https://coder.com/docs/code-server/install
        """

        LOGGER.info(f"install_dir: {self.install_dir}")
        LOGGER.info(f"package_file: {self.package_file}")
        LOGGER.info(f"CODE_SERVER_VERSION: {self.CODE_SERVER_VERSION}")

        if self.CODE_SERVER_VERSION.startswith("v"):
            api_link = CODE_SERVER_RELEASES.format(
                version=f"tags/{self.CODE_SERVER_VERSION}"
            )
        else:
            api_link = CODE_SERVER_RELEASES.format(version=self.CODE_SERVER_VERSION)

        release_dict = get_github_json(api_link)

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

        if self.package_file.exists():
            LOGGER.warning("code-server is already installed")
            with open(self.package_file, "r") as f:
                package_json = json.load(f)
                installed_version = package_json["version"]
                LOGGER.info(f"installed_version: {installed_version}")
                if installed_version == latest_tag:
                    if self.install_dir.joinpath("bin/code-server").exists():
                        LOGGER.info("code-server is already up to date")
                        return
                else:
                    LOGGER.info(f"Try install version {latest_tag}")

        self.install_dir.joinpath("lib").mkdir(parents=True, exist_ok=True)
        self.install_dir.joinpath("bin").mkdir(parents=True, exist_ok=True)

        download_file = pathlib.Path("/tmp/").joinpath(download_url.split("/")[-1])

        if download_file.exists():
            LOGGER.info(f"{download_file} is already exists")
        else:
            LOGGER.info("Downloading code-server")
            download(download_url, download_file)

        self.clean_up()

        output_path = self.install_dir.joinpath("lib")
        valid_dir_name = f"code-server-{latest_tag}-linux-amd64"

        if not output_path.joinpath(valid_dir_name).exists():
            untar(download_file, output_path=str(self.install_dir.joinpath("lib")))
        else:
            LOGGER.info(f"code-server-{latest_tag}-linux-amd64 is already exists")

        symlink_path = self.install_dir.joinpath("lib/code-server")
        if symlink_path.exists():
            if symlink_path.is_symlink():
                symlink_path.unlink()
            else:
                shutil.rmtree(symlink_path)
        symlink_path.symlink_to(valid_dir_name)

        bin_symlink_path = self.install_dir.joinpath("bin/code-server")
        if bin_symlink_path.exists():
            if bin_symlink_path.is_symlink():
                bin_symlink_path.unlink()
            else:
                shutil.rmtree(bin_symlink_path)
        bin_symlink_path.symlink_to(
            output_path.joinpath(f"{valid_dir_name}/bin/code-server")
        )

    def install_extensions(self, extensions: list[str] = [], force: bool = False):
        """
        https://coder.com/docs/user-guides/workspace-access/vscode#adding-extensions-to-custom-images
        """
        code_server_string = [
            "code-server",
            "--disable-telemetry",
            "--disable-update-check",
            "--disable-workspace-trust",
            f"--extensions-dir {self.install_dir}/share/code-server/extensions",
            "--force" if force else "",
            "--install-extension",
            "{extension}",
        ]

        self.install_dir.joinpath("share/code-server/extensions").mkdir(
            parents=True, exist_ok=True
        )

        for extension in DEFAULT_EXTENSIONS + extensions:
            LOGGER.info(f"installing extension: {extension}")
            start_cmd(" ".join(code_server_string).format(extension=extension))

    def install_settings(self):
        for profile in ["User", "Machine"]:
            profile_dir = self.install_dir.joinpath(f"share/code-server/{profile}")
            profile_dir.mkdir(parents=True, exist_ok=True)

            settings_file = profile_dir.joinpath("settings.json")

            settings = {}
            if settings_file.exists():
                LOGGER.warning(f"settings.json allready exists for {profile}")

                with settings_file.open(encoding="UTF-8") as fd:
                    settings = json.load(fd)

            for key, value in DEFAULT_SETTINGS[profile].items():
                if key not in settings:
                    settings[key] = value

            with settings_file.open("w", encoding="UTF-8") as f:
                json.dump(settings, f, indent=4)

            LOGGER.info(f"settings.json for {profile} installed")

    def patch_tornado(self):
        from tornado import websocket

        if websocket._default_max_message_size == 10 * 1024 * 1024:
            LOGGER.info("monkey patch for tornado.websocket")

            data = pathlib.Path(websocket.__file__).read_text(encoding="UTF-8")
            data = data.replace(
                "_default_max_message_size = 10 * 1024 * 1024",
                "_default_max_message_size = 1024 * 1024 * 1024",
            )
            pathlib.Path(websocket.__file__).write_text(data, encoding="UTF-8")
            LOGGER.info("DONE!")

    def clean_up(self, full: bool = False):
        LOGGER.info(f"Clean up {self.__class__.__name__}")
        files_to_remove = [
            self.install_dir.joinpath("lib/code-server"),
            self.install_dir.joinpath("bin/code-server"),
        ]
        if full:
            files_to_remove.append(self.install_dir.joinpath("share/code-server"))

            for file in pathlib.Path("/tmp/").glob("code-server*"):
                files_to_remove.append(file)

            for file in self.install_dir.joinpath("lib").glob("code-server*"):
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
        self.install_server()
        self.install_settings()
        self.install_extensions()
        self.patch_tornado()

    @classmethod
    def setup_proxy(cls: "CoderServer"):
        if not cls().check_install():
            cls().full_install()

        return {
            "command": [
                "code-server",
                "--auth=none",
                "--app-name='Remote VSCode Server'",
                "--disable-telemetry",
                "--disable-update-check",
                "--disable-workspace-trust",
                "--bind-addr=0.0.0.0:{port}",
            ],
            # "timeout": 60,
            "launcher_entry": {
                "title": "VS Code",
                "icon_path": get_icon("vscode"),
            },
        }
