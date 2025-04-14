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
