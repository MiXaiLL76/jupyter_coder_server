sdist:
	pipx run build --sdist .

format:
	pre-commit run --all-files

clean:
	rm -rf build dist *.egg-info jupyter_code_server/*.egg-info
	pip3 uninstall jupyter_code_server -y

remove_server:
	rm -rf ~/.local/share/code-server
	rm -rf ~/.local/lib/code-server*
	rm -rf ~/.local/bin/code-server
	rm -rf ~/.config/code-server

install: sdist
	pip3 install dist/*
