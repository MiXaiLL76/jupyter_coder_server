import tarfile
from subprocess import PIPE, STDOUT, Popen
import urllib.request
import urllib.error
import logging
import os
import json
import sys

try:
    import jupyter_coder_server
    from jupyter_coder_server.version import __version__

    jupyter_coder_server_dir = os.path.dirname(jupyter_coder_server.__file__)
except ImportError:
    jupyter_coder_server_dir = "./jupyter_coder_server"
    __version__ = "__dev__"

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger("jupyter_coder_server")
LOGGER.setLevel(logging.INFO)


def get_github_json(api_link: str):
    try:
        # Создаем запрос с заголовками
        request = urllib.request.Request(
            api_link,
            headers={
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )

        # Выполняем запрос
        with urllib.request.urlopen(request) as response:
            response_data = response.read().decode("utf-8")

        # Парсим JSON
        try:
            release_dict = json.loads(response_data)
            return release_dict
        except json.JSONDecodeError as e:
            LOGGER.error(f"Error parsing response: {response_data}")
            raise e

    except urllib.error.HTTPError as e:
        LOGGER.error(f"HTTP Error {e.code}: {e.reason}")
        raise e
    except urllib.error.URLError as e:
        LOGGER.error(f"URL Error: {e.reason}")
        raise e
    except Exception as e:
        LOGGER.error(f"Unexpected error: {e}")
        raise e


def download(url: str, fname: str, chunk_size=1024):
    import tqdm

    try:
        # Создаем запрос
        request = urllib.request.Request(url)

        # Открываем соединение
        with urllib.request.urlopen(request) as response:
            # Получаем размер файла из заголовков
            content_length = response.headers.get("content-length")
            total = int(content_length) if content_length else 0

            # Открываем файл для записи и создаем progress bar
            with open(str(fname), "wb") as file, tqdm.tqdm(
                desc="Download to: " + str(fname),
                total=total,
                unit="iB",
                unit_scale=True,
                unit_divisor=1024,
            ) as bar:
                # Читаем данные порциями
                while True:
                    data = response.read(chunk_size)
                    if not data:
                        break

                    size = file.write(data)
                    bar.update(size)

    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.reason}")
        raise e
    except urllib.error.URLError as e:
        print(f"URL Error: {e.reason}")
        raise e
    except Exception as e:
        print(f"Unexpected error during download: {e}")
        raise e


def untar(file: str, output_path: str = ""):
    import tqdm

    with tarfile.open(name=str(file)) as tar:
        for member in tqdm.tqdm(
            iterable=tar.getmembers(),
            total=len(tar.getmembers()),
            desc="Untar from: " + str(file),
        ):
            tar.extract(member=member, path=output_path)


def start_cmd(cmd: str):
    """
    Start cmd and yield decoded lines
    cmd: str
    """
    with Popen(
        cmd,
        shell=True,
        stdout=PIPE,
        stderr=STDOUT,
        cwd=None,
    ) as child_process:
        stdout_bufer = b""
        while True:
            stdout_byte = child_process.stdout.read(1)
            stdout_bufer += stdout_byte

            if (stdout_byte == b"\r") or (stdout_byte == b"\n"):
                LOGGER.info(stdout_bufer.decode("utf-8").strip())
                stdout_bufer = b""

            if stdout_byte == b"":
                break

        child_process.communicate()

        if child_process.returncode != 0:
            LOGGER.error(f"{cmd} failed!")


def get_icon(name: str):
    return os.path.join(jupyter_coder_server_dir, "icons", f"{name}.svg")


def install_labextensions():
    share_files = [
        "install.json",
        "package.json",
    ]
    etc_files = [
        "jupyter_coder_server.json",
    ]

    def rewrite_config(in_path, out_path):
        LOGGER.info(f"Rewrite config: {in_path} -> {out_path}")
        os.makedirs(os.path.dirname(out_path), exist_ok=True)

        with open(in_path, "r") as rf, open(out_path, "w") as wf:
            data = json.load(rf)
            if "version" in data:
                data["version"] = __version__
            json.dump(data, wf, indent=4)

    data_dir = os.path.dirname(os.path.dirname(sys.executable))

    for file in share_files:
        rewrite_config(
            os.path.join(jupyter_coder_server_dir, "labextensions", file),
            os.path.join(
                data_dir,
                "share",
                "jupyter",
                "labextensions",
                "jupyter_coder_server",
                file,
            ),
        )

    for file in etc_files:
        rewrite_config(
            os.path.join(jupyter_coder_server_dir, "labextensions", file),
            os.path.join(data_dir, "etc", "jupyter", "jupyter_server_config.d", file),
        )
