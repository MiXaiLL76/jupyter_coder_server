import tqdm
import tarfile
from subprocess import PIPE, STDOUT, Popen
import requests
import logging
import os
try:
    import jupyter_coder_server

    jupyter_coder_server_dir = os.path.dirname(jupyter_coder_server.__file__)
except ImportError:
    jupyter_coder_server_dir = "./jupyter_coder_server"

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger("jupyter_coder_server")
LOGGER.setLevel(logging.INFO)

def download(url: str, fname: str, chunk_size=1024):
    resp = requests.get(url, stream=True)
    total = int(resp.headers.get('content-length', 0))
    with open(str(fname), 'wb') as file, tqdm.tqdm(
        desc="Download to: " + str(fname),
        total=total,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for data in resp.iter_content(chunk_size=chunk_size):
            size = file.write(data)
            bar.update(size)

def untar(file : str, output_path : str = ""):
    with tarfile.open(name=str(file)) as tar:
        for member in tqdm.tqdm(iterable=tar.getmembers(), total=len(tar.getmembers()), desc="Untar from: " + str(file)):
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

def get_icon(name : str):
    return os.path.join(jupyter_coder_server_dir, "icons", f"{name}.svg")