import base64
from typing import Any, List, Optional

import ic
import requests
from ic.candid import Types

from pocket_ic.pocket_ic_server import PocketICServer


class PocketIC:
    def __init__(self) -> None:
        self.server = PocketICServer()
        self.instance_id = self.server.request_client.post(
            f"{self.server.url}/instances"
        ).text
        self.instance_url = f"{self.server.url}/instances/{self.instance_id}"
        self.request_client = requests.session()
        self.sender = ic.Principal.anonymous()

    def set_anonymous_sender(self):
        self.sender = ic.Principal.anonymous()

    def set_sender(self, principal: ic.Principal):
        self.sender = principal

    def send_request(self, payload: Any) -> Any:
        result = self.request_client.post(self.instance_url, json=payload)
        if result.status_code != requests.codes.ok:
            raise ConnectionError(
                f'PocketIC HTTP request returned with status code {result.status_code}: "{result.reason}"'
            )
        return result.json()

    def get_root_key(self) -> List[int]:
        return self.send_request("RootKey")

    def get_time(self) -> dict:
        return self.send_request("Time")

    def tick(self) -> None:
        return self.send_request("Tick")

    def set_time(self, time_nanosec: int) -> None:
        payload = {
            "SetTime": {
                "secs_since_epoch": time_nanosec // 1_000_000_000,
                "nanos_since_epoch": time_nanosec % 1_000_000_000,
            }
        }
        return self.send_request(payload)

    def advance_time(self, nanosecs: int) -> None:
        payload = {
            "AdvanceTime": {
                "secs": nanosecs // 1_000_000_000,
                "nanos": nanosecs % 1_000_000_000,
            }
        }
        return self.send_request(payload)

    def add_cycles(self, canister_id: ic.Principal, amount: int) -> int:
        payload = {
            "AddCycles": {
                "canister_id": base64.b64encode(canister_id.bytes).decode(),
                "amount": amount,
            }
        }
        return self.send_request(payload)

    # Makes an update call to a canister with the given ID. If the ID is not provided, calls the management canister.
    def update_call(
        self,
        canister_id: Optional[ic.Principal],
        method: str,
        payload: dict,
    ):
        canister_id = canister_id if canister_id else ic.Principal.management_canister()
        payload = {
            "CanisterUpdateCall": {
                "sender": base64.b64encode(self.sender.bytes).decode(),
                "canister_id": base64.b64encode(canister_id.bytes).decode(),
                "method": method,
                "arg": base64.b64encode(payload).decode(),
            }
        }
        res = self.send_request(payload)
        return self._get_ok_reply(res)

    # Makes a query call to a canister with the given ID. If the ID is not provided, calls the management canister.
    def query_call(
        self,
        canister_id: Optional[ic.Principal],
        method: str,
        payload: dict,
    ):
        canister_id = canister_id if canister_id else ic.Principal.management_canister()
        payload = {
            "CanisterQueryCall": {
                "sender": base64.b64encode(self.sender.bytes).decode(),
                "canister_id": base64.b64encode(canister_id.bytes).decode(),
                "method": method,
                "arg": base64.b64encode(payload).decode(),
            }
        }
        res = self.send_request(payload)
        return self._get_ok_reply(res)

    # Creates an empty canister.
    def create_canister(self, settings=None) -> ic.Principal:
        record = Types.Record(
            {
                "settings": Types.Opt(
                    Types.Record(
                        {
                            "controllers": Types.Opt(Types.Vec(Types.Principal)),
                            "compute_allocation": Types.Opt(Types.Nat),
                            "memory_allocation": Types.Opt(Types.Nat),
                            "freezing_threshold": Types.Opt(Types.Nat),
                        }
                    )
                )
            }
        )
        payload = [
            {"type": record, "value": {"settings": settings if settings else []}}
        ]

        request_result = self.update_call(None, "create_canister", ic.encode(payload))
        candid = ic.decode(
            bytes(request_result), Types.Record({"canister_id": Types.Principal})
        )
        canister_id = candid[0]["value"]["canister_id"]
        return canister_id

    # Installs a WASM code to the canister with the given ID.
    def install_code(
        self,
        canister_id: ic.Principal,
        wasm_module: bytes,
        arg: list,
    ) -> list:
        install_code_arg = Types.Record(
            {
                "wasm_module": Types.Vec(Types.Nat8),
                "canister_id": Types.Principal,
                "arg": Types.Vec(Types.Nat8),
                "mode": Types.Variant(
                    {
                        "install": Types.Null,
                        "reinstall": Types.Null,
                        "upgrade": Types.Null,
                    }
                ),
            }
        )

        payload = [
            {
                "type": install_code_arg,
                "value": {
                    "wasm_module": wasm_module,
                    "arg": ic.encode(arg),
                    "canister_id": canister_id.bytes,
                    "mode": {"install": None},
                },
            }
        ]

        request_result = self.update_call(None, "install_code", ic.encode(payload))
        candid = ic.decode(bytes(request_result))  # TODO: is this the candid interface?
        return candid

    # Creates a canister, installs the provided WASM with the given init arguments. Returns a canister interface.
    def create_and_install_canister_with_candid(
        self,
        candid: str,
        wasm_module: bytes,
        init_args: list,
    ) -> ic.Canister:
        canister_id = self.create_canister()
        canister = ic.Canister(self, canister_id, candid)

        canister_arguments = canister.actor["arguments"]
        if len(canister_arguments) == 0:
            arg = []
        elif len(canister_arguments) == 1:
            type_ = canister_arguments[0]
            arg = [{"type": type_, "value": init_args}]
        else:
            raise ValueError("Is the Candid file correct?")

        self.install_code(canister_id, wasm_module, arg)
        return canister

    def _get_ok_reply(self, request_result):
        if "Ok" in request_result:
            if "Reply" in request_result["Ok"]:
                return request_result["Ok"]["Reply"]
            raise ValueError(f'Request contains no key "Reply": {request_result["Ok"]}')

        if "Err" in request_result:
            raise ValueError(f'Request returned "Err": {request_result["Err"]}')

        raise ValueError(f"Malformed response: {request_result}")

    ############### for compatibility with ic-py's `Agent` class ##############

    def query_raw(
        self, canister_id, name, arguments, return_types, _effective_canister_id
    ):
        res = self.query_call(canister_id, name, arguments)
        return ic.decode(bytes(res), return_types)

    def update_raw(
        self, canister_id, name, arguments, return_types, _effective_canister_id
    ):
        res = self.update_call(canister_id, name, arguments)
        return ic.decode(bytes(res), return_types)

    ###########################################################################
