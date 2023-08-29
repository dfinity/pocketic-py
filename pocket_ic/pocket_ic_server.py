"""
This module contains the 'PocketICServer', which starts or discovers a PocketIC server process.
"""

import os
import time
from typing import List
from tempfile import gettempdir
import requests

POCKET_IC_BIN = "pocket-ic"


class PocketICServer:
    """
    An object of this class represents a running PocketIC server. During instantiation,
    a running server is discovered, or a new one is launched from the PocketIC binary,
    which is assumed to be on the PATH.

    All tests within a testsuite should use the same server, so the service
    discovery mechanism uses the current process id. This means that only the first
    test will launch a server, while all subsequent tests will discover the running
    one.

    A 'PocketIC' instance uses a 'PocketICServer' instance to retrieve an instance id,
    and a corresponding URL.
    """

    def __init__(self) -> None:
        # Attempt to start the PocketIC server if it's not already running.
        pid = os.getpid()
        os.system(f"{POCKET_IC_BIN} --pid {pid} &")
        self.url = self._get_url(pid)
        self.request_client = requests.session()

    def _get_url(self, pid: int) -> str:
        tmp_dir = gettempdir()
        ready_file_path = f"{tmp_dir}/pocket_ic_{pid}.ready"
        port_file_path = f"{tmp_dir}/pocket_ic_{pid}.port"

        stop_at = time.time() + 10  # Wait for the ready file for 10 seconds

        while not os.path.exists(ready_file_path):
            if time.time() < stop_at:
                time.sleep(0.1)  # 100ms
            else:
                raise TimeoutError("PocketIC failed to start")

        if os.path.isfile(ready_file_path):
            with open(port_file_path, "r", encoding="utf-8") as port_file:
                port = port_file.readline().strip()
        else:
            raise ValueError(f"{ready_file_path} is not a file!")

        return f"http://127.0.0.1:{port}"

    def list_instances(self) -> List[str]:
        """Lists the currently running instances on the PocketIC Server.

        Returns:
            List[str]: a list of instance names
        """
        return self.request_client.get(f"{self.url}/instances").text.split(", ")
