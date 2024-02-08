"""
This module contains the 'PocketICServer', which starts or discovers a PocketIC server process.
"""

import os
import time
import requests
from typing import List, Tuple, Optional
from tempfile import gettempdir


HEADERS = {"processing-timeout-ms": "300000"}


class PocketICServer:
    """
    An object of this class represents a running PocketIC server. During instantiation,
    a running server is discovered, or a new one is launched from the PocketIC binary,
    which is assumed to be in your working directory or specified via the POCKET_IC_BIN
    environment variable.

    All tests within a testsuite should use the same server, so the service
    discovery mechanism uses the current process id. This means that only the first
    test will launch a server, while all subsequent tests will discover the running
    one.

    A 'PocketIC' instance uses a 'PocketICServer' instance to retrieve an instance id,
    and a corresponding URL.
    """

    def __init__(self) -> None:
        pid = os.getpid()
        if "POCKET_IC_BIN" in os.environ:
            bin_path = os.environ["POCKET_IC_BIN"]
        else:
            bin_path = "./pocket-ic"

        if not os.path.isfile(bin_path):
            raise FileNotFoundError(
                f"""Could not find the PocketIC binary.

The PocketIC binary could not be found at "{bin_path}". Please specify the path to the binary with the POCKET_IC_BIN environment variable, \
or place it in your current working directory (you are running PocketIC from {os.getcwd()}).

To download the binary, please visit https://github.com/dfinity/pocketic.
"""
            )

        # Attempt to start the PocketIC server if it's not already running.
        mute = (
            "1> /dev/null 2> /dev/null" if "POCKET_IC_MUTE_SERVER" in os.environ else ""
        )
        os.system(f"{bin_path} --pid {pid} {mute} &")
        self.url = self._get_url(pid)
        self.request_client = requests.session()

    def new_instance(self, subnet_config: dict) -> Tuple[int, dict]:
        """Creates a new PocketIC instance.

        Returns:
            str: the new instance ID
        """
        url = f"{self.url}/instances"
        response = self.request_client.post(url, headers=HEADERS, json=subnet_config)
        res = self._check_response(response)["Created"]
        return res["instance_id"], res["topology"]

    def list_instances(self) -> List[str]:
        """Lists the currently running instances on the PocketIC Server.

        Returns:
            List[str]: a list of instance names
        """
        url = f"{self.url}/instances"
        response = self.request_client.get(url, headers=HEADERS)
        response = self._check_response(response)
        return response

    def delete_instance(self, instance_id: int):
        """Deletes an instance from the PocketIC Server.

        Args:
            instance_id (int): the ID of the instance to delete
        """
        url = f"{self.url}/instances/{instance_id}"
        self.request_client.delete(url, headers=HEADERS)

    def instance_get(self, endpoint: str, instance_id: int):
        """HTTP get requests for instance endpoints"""
        url = f"{self.url}/instances/{instance_id}/{endpoint}"
        response = self.request_client.get(url, headers=HEADERS)
        return self._check_response(response)

    def instance_post(self, endpoint: str, instance_id: int, body: Optional[dict]):
        """HTTP post requests for instance endpoints"""
        url = f"{self.url}/instances/{instance_id}/{endpoint}"
        response = self.request_client.post(url, json=body, headers=HEADERS)
        return self._check_response(response)

    def set_blob_store_entry(self, blob: bytes, compression: Optional[str]) -> str:
        """Sets a blob store entry.

        Args:
            blob (bytes): the blob to set
            compression (str/None): "gzip" or None

        Returns:
            str: the blob store key
        """
        url = f"{self.url}/blobstore"
        if compression is None:
            response = self.request_client.post(url, data=blob, headers=HEADERS)
        elif compression == "gzip":
            headers = HEADERS | {"Content-Encoding": "gzip"}
            response = self.request_client.post(url, data=blob, headers=headers)
        else:
            raise ValueError('only "gzip" compression is supported')

        self._check_status_code(response)
        return response.text

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

    def _check_response(self, response):
        self._check_status_code(response)
        res_json = response.json()
        return res_json

    def _check_status_code(self, response):
        if response.status_code not in [200, 201, 202]:
            raise ConnectionError(
                f'PocketIC server returned status code {response.status_code}: "{response.reason}"'
            )
