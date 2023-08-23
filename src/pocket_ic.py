import base64
from typing import Any, List, Optional

import ic
import requests
from ic.candid import Types
from pocket_ic_server import PocketICServer


class PocketIC:
    def __init__(self) -> None:
        backend = PocketICServer()
        self.instance_id = backend.request_client.post(
            f"{backend.daemon_url}instance"
        ).text
        self.instance_url = f"{backend.daemon_url}instance/{self.instance_id}"
        self.request_client = requests.session()
        self.backend = backend

    def send_request(self, payload: Any) -> Any:
        result = self.request_client.post(self.instance_url, json=payload)
        if result.status_code != 200:
            raise ConnectionError(f"IC HTTP request returned with status code {result.status_code}, Error:\n{result.text}")
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

    def canister_update_call(self, sender: Optional[ic.Principal], canister_id: Optional[ic.Principal], method: str, payload: dict):
        sender = sender if sender else ic.Principal.anonymous()
        canister_id = canister_id if canister_id else ic.Principal.management_canister()
        payload = {
            "CanisterUpdateCall": {
                "sender": base64.b64encode(sender.bytes).decode(),
                "canister_id": base64.b64encode(canister_id.bytes).decode(),
                "method": method,
                "arg": base64.b64encode(ic.encode(payload)).decode()
            }
        }
        return self.send_request(payload)
    
    def canister_query_call(self, sender: Optional[ic.Principal], canister_id: Optional[ic.Principal], method: str, payload: dict):
        sender = sender if sender else ic.Principal.anonymous()
        canister_id = canister_id if canister_id else ic.Principal.management_canister()
        payload = {
            "CanisterQueryCall": {
                "sender": base64.b64encode(sender.bytes).decode(),
                "canister_id": base64.b64encode(canister_id.bytes).decode(),
                "method": method,
                "arg": base64.b64encode(ic.encode(payload)).decode()
            }
        }
        return self.send_request(payload)

    def create_canister(self, sender: ic.Principal) -> ic.Principal:
        record = Types.Record({'settings': Types.Opt(Types.Record(
                    {
                        'controllers': Types.Opt(Types.Vec(Types.Principal)),
                        'compute_allocation': Types.Opt(Types.Nat),
                        'memory_allocation': Types.Opt(Types.Nat),
                        'freezing_threshold': Types.Opt(Types.Nat),
                    }
                )
            )
        })
        payload = [{'type': record, 'value': {
            'settings': []
        }}]

        request_result = self.canister_update_call(sender, None, "create_canister", payload)
        ok_reply = self.get_ok_reply(request_result)
        candid = ic.decode(bytes(ok_reply), Types.Record({'canister_id': Types.Principal}))
        canister_id = candid[0]['value']['canister_id']
        return canister_id

    def install_canister(self, sender: ic.Principal, canister_id: ic.Principal, wasm_module: bytes, arg: list) -> list:
        install_code_argument = Types.Record({
            'wasm_module': Types.Vec(Types.Nat8),
            'canister_id': Types.Principal,
            'arg': Types.Vec(Types.Nat8),
            'mode': Types.Variant({'install': Types.Null, 'reinstall': Types.Null, 'upgrade': Types.Null}),
        })

        payload = [{'type': install_code_argument, 'value': {
                'wasm_module': wasm_module,
                'arg': ic.encode(arg),
                'canister_id': canister_id.bytes,
                'mode': {'install': None}
            }
        }]

        request_result = self.canister_update_call(sender, None, "install_code", payload)
        ok_reply = self.get_ok_reply(request_result)
        candid = ic.decode(bytes(ok_reply))
        return candid
    
    def get_ok_reply(self, request_result):
        if 'Err' in request_result:
            raise ValueError(f'Request returned "Err": {request_result["Err"]}')
        elif 'Ok' in request_result:
            if 'Reply' in request_result['Ok']:
                return request_result['Ok']['Reply']
            else:
                raise ValueError(f'Request contains no key "Reply": {request_result["Ok"]}')
        else:
            raise ValueError(f'Malformed response: {request_result}')

