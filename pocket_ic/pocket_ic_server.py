import os
import subprocess
import time
import requests
from typing import List

POCKET_IC_BIN_PATH = "../../pocket_ic/pocket-ic"


class PocketICServer:
    def __init__(self) -> None:
        # attempt to start the PocketIC backend if it's not already running
        pid = os.getpid()
        subprocess.Popen([POCKET_IC_BIN_PATH, "--pid", f"{pid}"])
        daemon_url = self._get_daemon_url(pid)
        print(f'PocketIC running under "{daemon_url}"')

        self.request_client = requests.session()
        self.daemon_url = daemon_url

    def _get_daemon_url(self, pid: int) -> str:
        ready_file_path = f"/tmp/pocket_ic_{pid}.ready"
        port_file_path = f"/tmp/pocket_ic_{pid}.port"

        now = time.time()
        stop_at = now + 10  # wait for the ready file for 10 seconds
        while not os.path.exists(ready_file_path):
            if time.time() < stop_at:
                time.sleep(20 / 1000)
            else:
                raise TimeoutError("PocketIC failed to start")

        port = None
        if os.path.isfile(ready_file_path):
            with open(port_file_path, "r") as port_file:
                port = port_file.readline().strip()
        else:
            raise ValueError(f"{ready_file_path} is not a file!")

        return f"http://127.0.0.1:{port}/"

    def list_instances(self) -> List[str]:
        return self.request_client.get(f"{self.daemon_url}instances").text.split(", ")
