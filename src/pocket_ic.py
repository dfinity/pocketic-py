import base64
import os
import subprocess
import time
from typing import Any, List, Optional

import ic
import requests
from ic.candid import Types

POCKET_IC_BIN_PATH = "src/pocket_ic_binary"


class PocketIC:
    def __init__(self) -> None:
        backend = PocketICBackend()
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

    def canister_update_call(self, sender: Optional[ic.Principal], canister_id: Optional[ic.Principal], method: str, arg: dict):
        sender = sender if sender else ic.Principal.anonymous()
        canister_id = canister_id if canister_id else ic.Principal.management_canister()
        payload = {
            "CanisterUpdateCall": {
                "sender": base64.b64encode(sender.bytes).decode(),
                "canister_id": base64.b64encode(canister_id.bytes).decode(),
                "method": method,
                "arg": base64.b64encode(ic.encode(arg)).decode()
            }
        }
        return self.send_request(payload)
    
    def canister_query_call(self, sender: Optional[ic.Principal], canister_id: Optional[ic.Principal], method: str, arg: dict):
        sender = sender if sender else ic.Principal.anonymous()
        canister_id = canister_id if canister_id else ic.Principal.management_canister()
        payload = {
            "CanisterQueryCall": {
                "sender": base64.b64encode(sender.bytes).decode(),
                "canister_id": base64.b64encode(canister_id.bytes).decode(),
                "method": method,
                "arg": base64.b64encode(ic.encode(arg)).decode()
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
        arg = [{'type': record, 'value': {
            'settings': []
        }}]

        request_result = self.canister_update_call(sender, None, "create_canister", arg)
        ok_reply = request_result['Ok']['Reply']
        candid = ic.decode(bytes(ok_reply), Types.Record({'canister_id': Types.Principal}))
        canister_id = candid[0]['value']['canister_id']
        return canister_id

    def install_canister(self, sender: ic.Principal, canister_id: ic.Principal, wasm_module: bytes) -> list:
        install_code_argument = Types.Record({
            'wasm_module': Types.Vec(Types.Nat8),
            'canister_id': Types.Principal,
            'arg': Types.Vec(Types.Nat8),
            'mode': Types.Variant({'install': Types.Null, 'reinstall': Types.Null, 'upgrade': Types.Null}),
        })

        arg = [{'type': install_code_argument, 'value': {
                'wasm_module': wasm_module,
                'arg': [],
                'canister_id': canister_id.bytes,
                'mode': {'install': None}
            }
        }]

        request_result = self.canister_update_call(sender, None, "install_code", arg)
        ok_reply = request_result['Ok']['Reply']
        candid = ic.decode(bytes(ok_reply))
        return candid
    
    def install_icrc1_ledger_canister(self, sender: ic.Principal, canister_id: ic.Principal, wasm_module: bytes) -> list:
        Account = Types.Record({'owner': Types.Principal, 'subaccount': Types.Opt(Types.Vec(Types.Nat8))})
        FeatureFlags = Types.Record({'icrc2': Types.Bool})
        ArchiveOptions = Types.Record({
            'trigger_threshold': Types.Nat64,
            'num_blocks_to_archive': Types.Nat64,
            'node_max_memory_size_bytes': Types.Opt(Types.Nat64),
            'max_message_size_bytes': Types.Opt(Types.Nat64),
            'controller_id': Types.Principal,
            'cycles_for_archive_creation': Types.Opt(Types.Nat64),
            'max_transactions_per_response': Types.Opt(Types.Nat64)
        })
        MetadataValue = Types.Variant({'Nat': Types.Nat, 'Int': Types.Int, 'Text': Types.Text, 'Blob': Types.Vec(Types.Nat8)})
        ChangeFeeCollector = Types.Variant({'Unset': Types.Null, 'SetTo': Account})
        UpgradeArgs = Types.Record({
            'metadata': Types.Opt(Types.Vec(Types.Tuple(Types.Text, MetadataValue))),
            'token_name': Types.Opt(Types.Text),
            'token_symbol': Types.Opt(Types.Text),
            'transfer_fee': Types.Opt(Types.Nat),
            'change_fee_collector': Types.Opt(ChangeFeeCollector),
            'max_memo_length': Types.Opt(Types.Nat16),
            'feature_flags': Types.Opt(FeatureFlags),
            'maximum_number_of_accounts': Types.Opt(Types.Nat64),
            'accounts_overflow_trim_quantity': Types.Opt(Types.Nat64)

        })
        InitArgs = Types.Record({
            'minting_account': Account,
            'fee_collector_account': Types.Opt(Account),
            'initial_balances': Types.Vec(Types.Tuple(Account, Types.Nat)),
            'transfer_fee': Types.Nat,
            'decimals': Types.Opt(Types.Nat8),
            'token_name': Types.Text,
            'token_symbol': Types.Text,
            'metadata': Types.Vec(Types.Tuple(Types.Text, MetadataValue)),
            'archive_options': ArchiveOptions,
            'max_memo_length': Types.Opt(Types.Nat16),
            'feature_flags': Types.Opt(FeatureFlags),
            'maximum_number_of_accounts': Types.Opt(Types.Nat64),
            'accounts_overflow_trim_quantity': Types.Opt(Types.Nat64)
        })
        LedgerArg = Types.Variant({'Init': InitArgs, 'Upgrade': Types.Opt(UpgradeArgs)})

        # bbs = bytes([68, 73, 68, 76, 24, 107, 2, 252, 184, 139, 132, 3, 1, 176, 206, 209, 132, 3, 18, 110, 2, 108, 9, 158, 254, 185, 164, 3, 3, 242, 199, 148, 174, 3, 4, 239, 206, 231, 128, 4, 5, 151, 170, 189, 187, 6, 10, 132, 132, 213, 192, 7, 10, 133, 241, 153, 244, 7, 11, 176, 215, 195, 146, 11, 15, 145, 201, 170, 254, 13, 3, 190, 163, 209, 195, 15, 16, 110, 113, 110, 125, 110, 6, 109, 7, 108, 2, 0, 113, 1, 8, 107, 4, 207, 137, 223, 1, 124, 193, 137, 238, 1, 125, 253, 210, 201, 223, 2, 9, 205, 241, 203, 190, 3, 113, 109, 123, 110, 120, 110, 12, 107, 2, 157, 131, 244, 106, 13, 201, 197, 241, 208, 3, 127, 108, 2, 179, 176, 218, 195, 3, 104, 173, 134, 202, 131, 5, 14, 110, 9, 110, 122, 110, 17, 108, 1, 199, 191, 231, 182, 11, 126, 108, 13, 194, 149, 169, 147, 1, 19, 158, 254, 185, 164, 3, 113, 242, 199, 148, 174, 3, 125, 239, 206, 231, 128, 4, 6, 174, 203, 235, 136, 4, 13, 178, 164, 218, 178, 5, 20, 151, 170, 189, 187, 6, 10, 132, 132, 213, 192, 7, 10, 130, 186, 190, 130, 8, 22, 161, 229, 247, 161, 10, 23, 176, 215, 195, 146, 11, 15, 145, 201, 170, 254, 13, 113, 190, 163, 209, 195, 15, 16, 110, 123, 109, 21, 108, 2, 0, 13, 1, 125, 110, 13, 108, 7, 158, 165, 129, 210, 1, 120, 178, 167, 194, 210, 3, 10, 164, 149, 165, 233, 6, 120, 224, 171, 134, 239, 8, 10, 228, 216, 204, 232, 11, 10, 147, 200, 230, 199, 12, 10, 222, 197, 216, 174, 14, 104, 1, 0, 1, 0, 3, 83, 84, 75, 144, 78, 0, 1, 10, 42, 0, 0, 0, 0, 0, 0, 0, 254, 1, 0, 1, 1, 10, 0, 0, 0, 0, 0, 0, 0, 2, 1, 1, 0, 128, 173, 226, 4, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 4, 0, 9, 83, 78, 83, 32, 84, 111, 107, 101, 110, 0])
        # print('raw', ic.decode(bbs))
        # print('raw with names and types', ic.decode(bbs, LedgerArg))

        args = [{"type": LedgerArg,  "value": {
            "Init": {
                "decimals": [],
                "token_symbol": "MGC",
                "transfer_fee": 69_420,
                "metadata": [],
                "minting_account": {
                    "owner": ic.Principal.from_str('i3gqp-srkaa-aaaaa-aaaap-4ai').bytes,
                    "subaccount": []
                },
                "initial_balances": [
                    (
                        {
                            "owner": ic.Principal.from_str('ryjl3-tyaaa-aaaaa-aaaba-cai').bytes,
                            "subaccount": []
                        },
                        88_888
                    )
                ],
                "maximum_number_of_accounts": [],
                "accounts_overflow_trim_quantity": [],
                "fee_collector_account": [],
                "archive_options": {
                    "num_blocks_to_archive": 1,
                    "max_transactions_per_response": [],
                    "trigger_threshold": 1,
                    "max_message_size_bytes": [],
                    "cycles_for_archive_creation": [],
                    "node_max_memory_size_bytes": [],
                    "controller_id": ic.Principal.from_str('2vxsx-fae').bytes
                },
                "max_memo_length": [],
                "token_name": "My great coin",
                "feature_flags": []
            }
        }}]

        install_code_argument = Types.Record({
            'wasm_module': Types.Vec(Types.Nat8),
            'canister_id': Types.Principal,
            'arg': Types.Vec(Types.Nat8),
            'mode': Types.Variant({'install': Types.Null, 'reinstall': Types.Null, 'upgrade': Types.Null}),
        })
        
        arg = [{'type': install_code_argument, 'value': {
                'wasm_module': wasm_module,
                'arg': ic.encode(args),
                'canister_id': canister_id.bytes,
                'mode': {'install': None}
            }
        }]

        request_result = self.canister_update_call(sender, None, "install_code", arg)
        ok_reply = request_result['Ok']['Reply']
        candid = ic.decode(bytes(ok_reply))
        return candid


class PocketICBackend:
    def __init__(self) -> None:
        # attempt to start the PocketIC backend if it's not already running
        pid = os.getpid()
        subprocess.Popen([POCKET_IC_BIN_PATH, "--pid", f"{pid}"])
        daemon_url = self.get_daemon_url(pid)
        print(f'PocketIC running under "{daemon_url}"')

        self.request_client = requests.session()
        self.daemon_url = daemon_url

    def get_daemon_url(self, pid: int) -> str:
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
            with open(port_file_path) as port_file:
                port = port_file.readline().strip()
        else:
            raise ValueError(f"{ready_file_path} is not a file!")

        return f"http://127.0.0.1:{port}/"

    def list_instances(self) -> List[str]:
        return self.request_client.get(f"{self.daemon_url}instance").text.split(", ")
