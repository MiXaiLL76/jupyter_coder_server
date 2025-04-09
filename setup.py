import setuptools
from setuptools.command.install import install
from importlib.util import module_from_spec, spec_from_file_location


def readme():
    with open("README.md", encoding="utf-8") as f:
        content = f.read()
    return content


version_file = "jupyter_code_server/version.py"


def get_version():
    spec = spec_from_file_location("version", version_file)
    py = module_from_spec(spec)
    spec.loader.exec_module(py)
    return py.__version__, py.__author__


class PostInstallCommand(install):
    """Post-installation for installation mode."""

    def run(self):
        value = super().run()

        from jupyter_code_server.cli import install_all
        install_all()
        return value


__version__, __author__ = get_version()

setuptools.setup(
    name="jupyter_code_server",
    version=__version__,
    description="VSCODE integration in jupyter-lab",
    long_description=readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/MiXaiLL76/jupyter_code_server",
    author=__author__,
    author_email="mike.milos@yandex.ru",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.9",
    entry_points={
        "jupyter_serverproxy_servers": [
            # name = packagename:function_name
            "jupyter_code_server = jupyter_code_server:setup_jupyter_code_server",
        ],
        "console_scripts": ["jupyter_code_server = jupyter_code_server:main"],
    },
    install_requires=["jupyter-server-proxy"],
    cmdclass={
        "install": PostInstallCommand,
    },
)
