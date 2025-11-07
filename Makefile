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

# Function to download VSCode extension from open-vsx.org
# Usage: $(call download_extension,prefix,publisher,extension_name)
define download_extension
	@echo "Downloading $(2).$(3)..."
	test -f ext/$(1)-$(2).$(3).vsix || curl -sL -o ext/$(1)-$(2).$(3).vsix "$$(curl -sX GET https://open-vsx.org/api/$(2)/$(3) | jq -r '.downloads.universal // .downloads."linux-x64"')"
endef

build_ext:
	@echo "Creating ext directory..."
	mkdir -p -m 777 ext

	@echo "Downloading code-server and filebrowser..."
	test -f ext/code-server-4.105.1-linux-amd64.tar.gz || curl -sL -o ext/code-server-4.105.1-linux-amd64.tar.gz https://github.com/coder/code-server/releases/download/v4.105.1/code-server-4.105.1-linux-amd64.tar.gz
	test -f ext/linux-amd64-filebrowser.tar.gz || curl -sL -o ext/linux-amd64-filebrowser.tar.gz https://github.com/filebrowser/filebrowser/releases/download/v2.42.5/linux-amd64-filebrowser.tar.gz

	@echo "Downloading VSCode extensions in correct dependency order..."

	# Python dependencies first
	$(call download_extension,01,ms-python,vscode-python-envs)
	$(call download_extension,02,ms-python,debugpy)

	# Main Python extension
	$(call download_extension,03,ms-python,python)

	# Jupyter dependencies
	$(call download_extension,04,ms-toolsai,jupyter-keymap)
	$(call download_extension,05,ms-toolsai,vscode-jupyter-slideshow)
	$(call download_extension,06,ms-toolsai,vscode-jupyter-cell-tags)
	$(call download_extension,07,ms-toolsai,jupyter-renderers)

	# Main Jupyter extension
	$(call download_extension,08,ms-toolsai,jupyter)

	# Other extensions
	$(call download_extension,09,charliermarsh,ruff)
	$(call download_extension,10,Continue,continue)

	@echo "Creating ZIP archive..."
	cd ext && zip -r ../jupyter-coder-extensions.zip *

	@echo "Cleaning up ext directory..."
	rm -rf ext

	@echo "Done! Archive created: jupyter-coder-extensions.zip"
