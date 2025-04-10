import os

try:
    import jupyter_coder_server

    jupyter_coder_server_dir = os.path.dirname(jupyter_coder_server.__file__)
except ImportError:
    jupyter_coder_server_dir = "./jupyter_coder_server"


def setup_jupyter_coder_server():
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
        "timeout": 10,
        "launcher_entry": {
            "title": "VS Code",
            "icon_path": os.path.join(jupyter_coder_server_dir, "icons", "vscode.svg"),
        },
    }


def setup_filebrowser():
    database_file = os.environ.get("FILE_BROWSER_DATABASE", "/tmp/filebrowser.db")
    img_processors = int(os.environ.get("FILE_BROWSER_IMG_PROCESSORS", "4"))

    return {
        "command": [
            "filebrowser",
            "--noauth",
            "--root=/home",
            "--baseurl=/vscode_server_fb",
            f"--database={database_file}",
            f"--img-processors={img_processors}",
            "--address=0.0.0.0",
            "--port={port}",
        ],
        # "timeout": 10,
        "launcher_entry": {
            "title": "Web File Browser",
            "icon_path": os.path.join(
                jupyter_coder_server_dir, "icons", "filebrowser.svg"
            ),
        },
    }
