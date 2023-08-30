"""
This module contains the 'PocketICServer', which starts or discovers a PocketIC server process.
"""

import os
import time
from typing import List, Any
from tempfile import gettempdir
import requests

BINARY_NAME = "pocket-ic"


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
        os.system(f"{BINARY_NAME} --pid {pid} &")
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

    def new_instance(self) -> str:
        """Creates a new PocketIC instance.

        Returns:
            str: the new instance ID
        """
        url = f"{self.url}/instances"
        response = self.request_client.post(url)
        self._check_response(response)
        return response.text

    def list_instances(self) -> List[str]:
        """Lists the currently running instances on the PocketIC Server.

        Returns:
            List[str]: a list of instance names
        """
        url = f"{self.url}/instances"
        response = self.request_client.get(url)
        self._check_response(response)
        return response.text.split(", ") if response.text else []

    def delete_instance(self, instance_id: str):
        """Deletes an instance from the PocketIC Server.

        Args:
            instance_id (str): the ID of the instance to delete
        """
        url = f"{self.url}/instances/{instance_id}/delete"
        response = self.request_client.delete(url)
        self._check_response(response)

    def send_request_to_instance(self, instance_id: str, body: Any) -> Any:
        """Send a request to a specific PocketIC instance.

        Args:
            instance_id (str): the instance ID
            body (Any): the payload for the IC request

        Returns:
            Any: a JSON encoded result, if the request contains a response
        """
        url = f"{self.url}/instances/{instance_id}"
        response = self.request_client.post(url, json=body)
        self._check_response(response)
        return response.json()

    def _check_response(self, response):
        """Checks the response from the PocketIC server.

        Args:
            response (Response): the response from a call made with `requests`

        Raises:
            ConnectionError: raised on response status codes != 200
        """
        if response.status_code != 200:
            raise ConnectionError(
                f'PocketIC Server returned status code {response.status_code}: "{response.reason}"'
            )
