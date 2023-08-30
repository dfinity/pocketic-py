"""
This module contains 'PocketIC', which is the only interface we expose to a test author.
"""
import base64
from typing import Any, List, Optional

import ic
from ic.candid import Types

from pocket_ic.pocket_ic_server import PocketICServer


class PocketIC:
    """
    An instance of this class represents an IC instance on the PocketIC server.

    The interface of this class is derived from the StateMachine testing framework,
    which presents a blocking API to the user.

    TODO: describe return types and error states
    """

    def __init__(self) -> None:
        self.server = PocketICServer()
        self.instance_id = self.server.new_instance()
        self.sender = ic.Principal.anonymous()

    def send_request(self, body: Any) -> Any:
        """Send a request to the IC.

        Args:
            body (Any): the payload for the IC request

        Returns:
            Any: a JSON encoded result, if the request contains a response
        """
        return self.server.send_request_to_instance(self.instance_id, body)

    def delete(self) -> None:
        """Deletes this PocketIC instance."""
        self.server.delete_instance(self.instance_id)

    def set_anonymous_sender(self) -> None:
        """Sets the new sender for all following calls to the IC to the anonymous principal."""
        self.sender = ic.Principal.anonymous()

    def set_sender(self, principal: ic.Principal) -> None:
        """Sets the new sender for all following calls to the IC to the specified principal.

        Args:
            principal (ic.Principal): the principal to make calls from
        """
        self.sender = principal

    def _get_root_key(self) -> List[int]:
        return self.send_request("RootKey")

    def get_time(self) -> dict:
        """Get the current time of the IC.

        Returns:
            dict: {'secs_since_epoch': ..., 'nanos_since_epoch': ...}
        """
        return self.send_request("Time")

    def tick(self) -> None:
        """Make the IC produce and progress by one block."""
        self.send_request("Tick")

    def check_canister_exists(self, canister_id: ic.Principal) -> bool:
        """Check whether the provided canister exists.

        Args:
            canister_id (ic.Principal): the ID of the canister

        Returns:
            bool: `True` if the canister exists, `False` otherwise
        """
        payload = {
            "CanisterExists": {
                "canister_id": base64.b64encode(canister_id.bytes).decode()
            }
        }
        return self.send_request(payload)

    def get_cycles_balance(self, canister_id: ic.Principal) -> int:
        """Get the cycles balance of a canister.

        Args:
            canister_id (ic.Principal): the ID of the canister

        Returns:
            int: the number of cycles the canister contains
        """
        payload = {
            "CyclesBalance": {
                "canister_id": base64.b64encode(canister_id.bytes).decode()
            }
        }
        return self.send_request(payload)

    def set_time(self, time_nanosec: int) -> None:
        """Sets the current time of the IC.

        Args:
            time_nanosec (int): the number of nanoseconds since epoch
        """
        payload = {
            "SetTime": {
                "secs_since_epoch": time_nanosec // 1_000_000_000,
                "nanos_since_epoch": time_nanosec % 1_000_000_000,
            }
        }
        self.send_request(payload)

    def advance_time(self, nanosecs: int) -> None:
        """Advance the time on the IC by some nanoseconds.

        Args:
            nanosecs (int): number of nanoseconds to be added to the current time
        """
        payload = {
            "AdvanceTime": {
                "secs": nanosecs // 1_000_000_000,
                "nanos": nanosecs % 1_000_000_000,
            }
        }
        return self.send_request(payload)

    def add_cycles(self, canister_id: ic.Principal, amount: int) -> int:
        """Add cycles to a specific canister.

        Args:
            canister_id (ic.Principal): the ID of the canister to add cycles to
            amount (int): amount of cycles to add to the canister (single cycles, NOT trillion cycles)

        Returns:
            int: the total amount of cycles the canister holds at after adding `amount`
        """
        payload = {
            "AddCycles": {
                "canister_id": base64.b64encode(canister_id.bytes).decode(),
                "amount": amount,
            }
        }
        return self.send_request(payload)

    def update_call(
        self,
        canister_id: Optional[ic.Principal],
        method: str,
        payload: bytes,
    ) -> list:
        """Makes an update call to a canister with the given ID. If the ID is not provided, calls the management canister.

        Args:
            canister_id (Optional[ic.Principal]): optional canister ID or `None` for management canister.
            method (str): the canister method to execute
            payload (dict): a candid encoded representation of the payload

        Returns:
            list: a list of candid objects
        """
        canister_id = canister_id if canister_id else ic.Principal.management_canister()
        body = {
            "CanisterUpdateCall": {
                "sender": base64.b64encode(self.sender.bytes).decode(),
                "canister_id": base64.b64encode(canister_id.bytes).decode(),
                "method": method,
                "arg": base64.b64encode(payload).decode(),
            }
        }
        res = self.send_request(body)
        return self._get_ok_reply(res)

    def query_call(
        self,
        canister_id: Optional[ic.Principal],
        method: str,
        payload: bytes,
    ) -> list:
        """Makes a query call to a canister with the given ID. If the ID is not provided, calls the management canister.

        Args:
            canister_id (Optional[ic.Principal]): optional canister ID or `None` for management canister.
            method (str): the canister method to execute
            payload (dict): a candid encoded representation of the payload

        Returns:
            list: a list of candid objects
        """
        canister_id = canister_id if canister_id else ic.Principal.management_canister()
        body = {
            "CanisterQueryCall": {
                "sender": base64.b64encode(self.sender.bytes).decode(),
                "canister_id": base64.b64encode(canister_id.bytes).decode(),
                "method": method,
                "arg": base64.b64encode(payload).decode(),
            }
        }
        res = self.send_request(body)
        return self._get_ok_reply(res)

    def create_canister(self, settings: list = None) -> ic.Principal:
        """Creates an empty canister.

        Args:
            settings (list, optional): optional list of settings, defaults to `None`

        Returns:
            ic.Principal: the canister ID of the new canister
        """
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

    def install_code(
        self,
        canister_id: ic.Principal,
        wasm_module: bytes,
        arg: list,
    ) -> None:
        """Installs WASM code to the given canister ID with arguments.

        Args:
            canister_id (ic.Principal): the target canister
            wasm_module (bytes): the wasm module as bytes
            arg (list): list of install arguments
        """
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

        self.update_call(None, "install_code", ic.encode(payload))

    def create_and_install_canister_with_candid(
        self,
        candid: str,
        wasm_module: bytes,
        init_args: dict,
    ) -> ic.Canister:
        """Creates a canister, installs the provided WASM with the given init arguments. Returns a canister object.
        For an example on how to use the canister object, see `/examples/ledger_canister_test.py`.

        Args:
            candid (str): a valid candid file describing the canister interface
            wasm_module (bytes): the canister wasm as bytes
            init_args (dict): the init args as required by the candid file

        Raises:
            ValueError: can be raised on invalid candid files

        Returns:
            ic.Canister: the canister object
        """
        canister_id = self.create_canister()
        canister = ic.Canister(self, canister_id, candid)

        canister_arguments = canister.actor["arguments"]
        if len(canister_arguments) == 0:
            arg = []
        elif len(canister_arguments) == 1:
            arg = [{"type": canister_arguments[0], "value": init_args}]
        else:
            raise ValueError("The candid file appears to be malformed")

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

    ############### For compatibility with ic-py's `ic.Agent` class;  #########
    ############### the `ic.Canister` interface requires these two methods. ###

    def query_raw(
        self, canister_id, name, arguments, return_types, _effective_canister_id
    ):
        """For compatibility with `ic-py`'s `Agent` class."""
        res = self.query_call(canister_id, name, arguments)
        return ic.decode(bytes(res), return_types)

    def update_raw(
        self, canister_id, name, arguments, return_types, _effective_canister_id
    ):
        """For compatibility with `ic-py`'s `Agent` class."""
        res = self.update_call(canister_id, name, arguments)
        return ic.decode(bytes(res), return_types)

    ###########################################################################
