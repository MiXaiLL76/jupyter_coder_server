import tqdm
import tarfile
from subprocess import PIPE, STDOUT, Popen
import requests
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


def download(url: str, fname: str, chunk_size=1024):
    resp = requests.get(url, stream=True)
    total = int(resp.headers.get("content-length", 0))
    with open(str(fname), "wb") as file, tqdm.tqdm(
        desc="Download to: " + str(fname),
        total=total,
        unit="iB",
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for data in resp.iter_content(chunk_size=chunk_size):
            size = file.write(data)
            bar.update(size)


def untar(file: str, output_path: str = ""):
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
