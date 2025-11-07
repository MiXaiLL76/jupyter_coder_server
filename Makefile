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
	$(eval CODE_SERVER_VERSION := 4.105.1)
	$(eval FILEBROWSER_VERSION := 2.42.5)
	$(eval CONTAINER_NAME := code-server-ext-builder)

	@echo "Creating ext directory..."
	mkdir -p -m 777 ext/extensions

	@echo "Downloading code-server and filebrowser..."
	test -f ext/code-server-$(CODE_SERVER_VERSION)-linux-amd64.tar.gz || curl -sL -o ext/code-server-$(CODE_SERVER_VERSION)-linux-amd64.tar.gz https://github.com/coder/code-server/releases/download/v$(CODE_SERVER_VERSION)/code-server-$(CODE_SERVER_VERSION)-linux-amd64.tar.gz
	test -f ext/linux-amd64-filebrowser.tar.gz || curl -sL -o ext/linux-amd64-filebrowser.tar.gz https://github.com/filebrowser/filebrowser/releases/download/v$(FILEBROWSER_VERSION)/linux-amd64-filebrowser.tar.gz

	@echo "Starting Docker container for extension installation..."
	docker run -d --name $(CONTAINER_NAME) -v ./ext/extensions:/config/.local/share/code-server/extensions/ lscr.io/linuxserver/code-server:$(CODE_SERVER_VERSION)

	@echo "Waiting for container to be ready..."
	sleep 5

	@echo "Installing VSCode extensions in correct dependency order..."
	docker exec $(CONTAINER_NAME) /app/code-server/bin/code-server --install-extension ms-python.python
	docker exec $(CONTAINER_NAME) /app/code-server/bin/code-server --install-extension ms-toolsai.jupyter
	docker exec $(CONTAINER_NAME) /app/code-server/bin/code-server --install-extension charliermarsh.ruff
	docker exec $(CONTAINER_NAME) /app/code-server/bin/code-server --install-extension Continue.continue
	docker exec $(CONTAINER_NAME) chmod -R 777 /config/.local/share/code-server/extensions/

	@echo "Stopping and removing Docker container..."
	docker stop $(CONTAINER_NAME)
	docker rm $(CONTAINER_NAME)

	@echo "Creating ZIP archive..."
	rm -rf jupyter-coder-extensions.zip && cd ext && zip -r ../jupyter-coder-extensions.zip *

	@echo "Cleaning up ext directory..."
	rm -rf ext

	@echo "Done! Archive created: jupyter-coder-extensions.zip"
