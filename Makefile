sdist:
	pipx run build --sdist .

format:
	pre-commit run --all-files

clean:
	rm -rf build dist *.egg-info jupyter_coder_server/*.egg-info node_modules .yarn
	pip3 uninstall jupyter_coder_server -y

remove_server:
	rm -rf ~/.local/share/code-server
	rm -rf ~/.local/lib/code-server*
	rm -rf ~/.local/bin/code-server
	rm -rf ~/.config/code-server
	rm -rf ~/.local/lib/file-browser
	rm -rf ~/.local/bin/filebrowser

install: sdist
	pip3 install dist/*

build_ext:
	@echo "Creating ext directory..."
	mkdir -p -m 777 ext

	@echo "Downloading code-server and filebrowser..."
	test -f ext/code-server-4.105.1-linux-amd64.tar.gz || curl -sL -o ext/code-server-4.105.1-linux-amd64.tar.gz https://github.com/coder/code-server/releases/download/v4.105.1/code-server-4.105.1-linux-amd64.tar.gz
	test -f ext/linux-amd64-filebrowser.tar.gz || curl -sL -o ext/linux-amd64-filebrowser.tar.gz https://github.com/filebrowser/filebrowser/releases/download/v2.42.5/linux-amd64-filebrowser.tar.gz

	@echo "Downloading VSCode extensions..."
	# ms-python.python
	test -f ext/ms-python.python.vsix || curl -sL -o ext/ms-python.python.vsix "$$(curl -sX GET https://open-vsx.org/api/ms-python/python | jq -r '.downloads.universal // .downloads."linux-x64"')"

	# ms-python.debugpy
	test -f ext/ms-python.debugpy.vsix || curl -sL -o ext/ms-python.debugpy.vsix "$$(curl -sX GET https://open-vsx.org/api/ms-python/debugpy | jq -r '.downloads.universal // .downloads."linux-x64"')"

	# ms-python.vscode-python-envs
	test -f ext/ms-python.vscode-python-envs.vsix || curl -sL -o ext/ms-python.vscode-python-envs.vsix "$$(curl -sX GET https://open-vsx.org/api/ms-python/vscode-python-envs | jq -r '.downloads.universal // .downloads."linux-x64"')"

	# ms-toolsai.jupyter
	test -f ext/ms-toolsai.jupyter.vsix || curl -sL -o ext/ms-toolsai.jupyter.vsix "$$(curl -sX GET https://open-vsx.org/api/ms-toolsai/jupyter | jq -r '.downloads.universal // .downloads."linux-x64"')"

	# ms-toolsai.vscode-jupyter-slideshow
	test -f ext/ms-toolsai.vscode-jupyter-slideshow.vsix || curl -sL -o ext/ms-toolsai.vscode-jupyter-slideshow.vsix "$$(curl -sX GET https://open-vsx.org/api/ms-toolsai/vscode-jupyter-slideshow | jq -r '.downloads.universal // .downloads."linux-x64"')"

	# ms-toolsai.jupyter-keymap
	test -f ext/ms-toolsai.jupyter-keymap.vsix || curl -sL -o ext/ms-toolsai.jupyter-keymap.vsix "$$(curl -sX GET https://open-vsx.org/api/ms-toolsai/jupyter-keymap | jq -r '.downloads.universal // .downloads."linux-x64"')"

	# ms-toolsai.vscode-jupyter-cell-tags
	test -f ext/ms-toolsai.vscode-jupyter-cell-tags.vsix || curl -sL -o ext/ms-toolsai.vscode-jupyter-cell-tags.vsix "$$(curl -sX GET https://open-vsx.org/api/ms-toolsai/vscode-jupyter-cell-tags | jq -r '.downloads.universal // .downloads."linux-x64"')"

	# ms-toolsai.jupyter-renderers
	test -f ext/ms-toolsai.jupyter-renderers.vsix || curl -sL -o ext/ms-toolsai.jupyter-renderers.vsix "$$(curl -sX GET https://open-vsx.org/api/ms-toolsai/jupyter-renderers | jq -r '.downloads.universal // .downloads."linux-x64"')"

	# charliermarsh.ruff
	test -f ext/charliermarsh.ruff.vsix || curl -sL -o ext/charliermarsh.ruff.vsix "$$(curl -sX GET https://open-vsx.org/api/charliermarsh/ruff | jq -r '.downloads.universal // .downloads."linux-x64"')"

	# Continue/continue
	test -f ext/Continue.continue.vsix || curl -sL -o ext/Continue.continue.vsix "$$(curl -sX GET https://open-vsx.org/api/Continue/continue | jq -r '.downloads.universal // .downloads."linux-x64"')"

	@echo "Creating ZIP archive..."
	cd ext && zip -r ../jupyter-coder-extensions.zip *

	@echo "Cleaning up ext directory..."
	rm -rf ext

	@echo "Done! Archive created: jupyter-coder-extensions.zip"
