import base64
from typing import Any, List, Optional

import ic
import requests
from ic.candid import Types

from pocket_ic.pocket_ic_server import PocketICServer


class PocketIC:
    def __init__(self) -> None:
        backend = PocketICServer()
        self.instance_id = backend.request_client.post(
            f"{backend.daemon_url}instances"
        ).text
        self.instance_url = f"{backend.daemon_url}instances/{self.instance_id}"
        self.request_client = requests.session()
        self.backend = backend
        self.sender = ic.Principal.anonymous()

    def anonymous_sender(self):
        self.sender = ic.Principal.anonymous()

    def set_sender(self, principal: ic.Principal):
        self.sender = principal

    def send_request(self, payload: Any) -> Any:
        result = self.request_client.post(self.instance_url, json=payload)
        if result.status_code != 200:
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

    def canister_update_call(
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

    def canister_query_call(
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

    def create_empty_canister(self, settings=None) -> ic.Principal:
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

        request_result = self.canister_update_call(
            None, "create_canister", ic.encode(payload)
        )
        candid = ic.decode(
            bytes(request_result), Types.Record({"canister_id": Types.Principal})
        )
        canister_id = candid[0]["value"]["canister_id"]
        return canister_id

    def install_canister(
        self,
        canister_id: ic.Principal,
        wasm_module: bytes,
        arg: list,
    ) -> list:
        install_code_argument = Types.Record(
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
                "type": install_code_argument,
                "value": {
                    "wasm_module": wasm_module,
                    "arg": ic.encode(arg),
                    "canister_id": canister_id.bytes,
                    "mode": {"install": None},
                },
            }
        ]

        request_result = self.canister_update_call(
            None, "install_code", ic.encode(payload)
        )
        candid = ic.decode(bytes(request_result))
        return candid

    def create_canister_with_candid(
        self,
        candid: str,
        wasm_module: bytes,
        init_args: list,
    ) -> ic.Canister:
        canister_id = self.create_empty_canister()
        canister = ic.Canister(self, canister_id, candid)

        canister_arguments = canister.actor["arguments"]
        if len(canister_arguments) == 1:
            type_ = canister_arguments[0]
            arg = [{"type": type_, "value": init_args}]
        elif len(canister_arguments) == 0:
            arg = []
        else:
            raise ValueError("This should not happen. Please check the candid file")

        self.install_canister(canister_id, wasm_module, arg)
        return canister

    def _get_ok_reply(self, request_result):
        if "Err" in request_result:
            raise ValueError(f'Request returned "Err": {request_result["Err"]}')
        if "Ok" in request_result:
            if "Reply" in request_result["Ok"]:
                return request_result["Ok"]["Reply"]
            raise ValueError(f'Request contains no key "Reply": {request_result["Ok"]}')
        raise ValueError(f"Malformed response: {request_result}")

    ############### for compatibility with ip-py's `Agent` class ##############

    def query_raw(
        self, canister_id, name, arguments, return_types, _effective_canister_id
    ):
        res = self.canister_query_call(canister_id, name, arguments)
        return ic.decode(bytes(res), return_types)

    def update_raw(
        self, canister_id, name, arguments, return_types, _effective_canister_id
    ):
        res = self.canister_update_call(canister_id, name, arguments)
        return ic.decode(bytes(res), return_types)

    ###########################################################################
