# jupyter_coder_server

[![PyPI](https://img.shields.io/pypi/v/jupyter-coder-server)](https://pypi.org/project/jupyter_coder_server)
[![PyPI Downloads](https://img.shields.io/pypi/dm/jupyter-coder-server.svg?label=PyPI%20downloads)](https://pypi.org/project/jupyter_coder_server/)

## Disclaimer

Many developers are forced to use jupyterlab\\jupyterhub during work, without the ability to use VSCODE.
Our comrades from [coder](https://github.com/coder) have done a great job to make it possible to use VSCODE through a browser.
My job is left to make these two technologies friends and provide the ability to quickly and conveniently launch both of these applications.

This library works in tandem with the [jupyter-server-proxy](https://github.com/jupyterhub/jupyter-server-proxy) library, which in turn allows you to create additional servers inside Jupyter.

| VSCode button                                                                                                               | Web Code Server (proxy)                                                                                                   |
| --------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| ![vscode_button](https://raw.githubusercontent.com/MiXaiLL76/jupyter_coder_server/refs/heads/main/assets/vscode_button.png) | ![vscode_proxy](https://raw.githubusercontent.com/MiXaiLL76/jupyter_coder_server/refs/heads/main/assets/vscode_proxy.png) |

## Install

Just run the installation from pypi and enjoy
**After installation, be sure to restart the server (if it is running in docker, then restart docker)**

```bash
pip install jupyter_coder_server
```

### Extra install

By default, this library installs the latest version of code-server on your device in the **~/.local/lib** directory

Installing a specific [version of code-server](https://github.com/coder/code-server/releases)

> To do this, you need to set env CODE_SERVER_VERSION
> CODE_SERVER_VERSION - lataset by default
> Since version search is controlled by github tags.

Installation example **tag_name "v4.99.1"**

```bash
CODE_SERVER_VERSION=v4.99.1 jupyter_coder_server --install
```

### CLI Commands

```bash
usage: jupyter_coder_server [-h] [--version] [--install] [--install-server] [--install-extensions] [--install-settings] [--install-filebrowser] [--patch-tornado] [--remove] [--remove-server] [--remove-filebrowser]

options:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  --install             Install coder-server, extensions, settings and Web File Browser
  --install-server      Install coder-server
  --install-extensions  Install extensions
  --install-settings    Install settings
  --install-filebrowser
                        Install Web File Browser
  --patch-tornado       Monkey patch tornado.websocket
  --remove              Remove coder-server and Web File Browser
  --remove-server       Remove coder-server
  --remove-filebrowser  Remove Web File Browser
```

## Requirements

1. Linux amd64
2. Installed CURL

For more details [see here](https://github.com/coder/code-server?tab=readme-ov-file#requirements)

## License

Since the [code-server](https://github.com/coder/code-server) project has an MIT license, I also use it in this project.

## Citation

```
@article{jupyter_coder_server,
title = {{jupyter_coder_server}: VSCODE integration in jupyter-lab},
author = {MiXaiLL76},
year = {2024}
}
```
