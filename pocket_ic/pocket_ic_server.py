import os
import subprocess
import time
import requests
from typing import List

POCKET_IC_BIN = "pocketic"


class PocketICServer:
    def __init__(self) -> None:
        # Attempt to start the PocketIC server if it's not already running.
        pid = os.getpid()
        subprocess.Popen([POCKET_IC_BIN, "--pid", f"{pid}"])
        self.url = self._get_url(pid)

        self.request_client = requests.session()

    def _get_url(self, pid: int) -> str:
        # TODO: Use `tempfile`
        ready_file_path = f"/tmp/pocket_ic_{pid}.ready"
        port_file_path = f"/tmp/pocket_ic_{pid}.port"

        stop_at = time.time() + 10  # Wait for the ready file for 10 seconds

        while not os.path.exists(ready_file_path):
            if time.time() < stop_at:
                time.sleep(0.1)  # 100ms
            else:
                raise TimeoutError("PocketIC failed to start")

        if os.path.isfile(ready_file_path):
            with open(port_file_path, "r") as port_file:
                port = port_file.readline().strip()
        else:
            raise ValueError(f"{ready_file_path} is not a file!")

        return f"http://127.0.0.1:{port}"

    def list_instances(self) -> List[str]:
        return self.request_client.get(f"{self.url}/instances").text.split(", ")
