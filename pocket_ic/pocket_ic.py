"""
This module contains `PocketIC`, which is the main interface exposed to the test author.
"""

import base64
import ic
from ic.candid import Types
from typing import Optional, Any
from pocket_ic.pocket_ic_server import PocketICServer
from pocket_ic.subnet_config import SubnetConfig, SubnetKind


class PocketIC:
    """
    An instance of this class represents an IC instance on the PocketIC server.

    The interface of this class is derived from the StateMachine testing framework,
    which presents a blocking API to the user.
    """

    def __init__(self, subnet_config: Optional[SubnetConfig] = None) -> None:
        """Creates a new PocketIC instance with an optional subnet configuration.

        Args:
            subnet_config (Optional[SubnetConfig], optional): the subnet configuration to use,
              defaults to one application subnet
        """
        self.server = PocketICServer()
        subnet_config = subnet_config if subnet_config else SubnetConfig(application=1)
        subnet_config.validate()
        self.instance_id = self.server.new_instance(subnet_config._json())
        self.sender = ic.Principal.anonymous()

    def __del__(self) -> None:
        """Deletes the instance from the PocketIC server."""
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

    def topology(self):
        """Returns the current topology of the PocketIC instance."""
        res = self._instance_get("read/topology")
        t = dict()
        subnets = res["subnet_configs"]
        for subnet_id, config in subnets.items():
            subnet_id = ic.Principal.from_str(subnet_id)
            subnet_kind = SubnetKind(config["subnet_kind"])
            t.update({subnet_id: subnet_kind})
        return t

    def get_root_key(self) -> Optional[bytes]:
        """Get the root key of the IC. If there is no NNS subnet, returns `None`.

        Returns:
            Optional[bytes]: the root key of the IC
        """
        nns_subnet = [k for k, v in self.topology().items() if v == SubnetKind.NNS]
        if not nns_subnet:
            return None
        body = {
            "subnet_id": base64.b64encode(nns_subnet[0].bytes).decode(),
        }
        return bytes(self._instance_post("read/pub_key", body))

    def get_time(self) -> dict:
        """Get the current time of the IC.

        Returns:
            dict: {'nanos_since_epoch': ...}
        """
        return self._instance_get("read/get_time")

    def set_time(self, time_nanosec: int) -> None:
        """Sets the current time of the IC.

        Args:
            time_nanosec (int): the number of nanoseconds since epoch
        """
        body = {
            "nanos_since_epoch": time_nanosec,
        }
        self._instance_post("update/set_time", body)

    def advance_time(self, nanosecs: int) -> None:
        """Advance the time on the IC by some nanoseconds.

        Args:
            nanosecs (int): number of nanoseconds to be added to the current time
        """
        new_time = self.get_time()["nanos_since_epoch"] + nanosecs
        self.set_time(new_time)

    def tick(self) -> None:
        """Make the IC produce and progress by one block."""
        self._instance_post("update/tick", {})

    def get_subnet(self, canister_id: ic.Principal) -> Optional[ic.Principal]:
        """Get the subnet ID of the subnet that contains the given canister.

        Args:
            canister_id (ic.Principal): the ID of the canister

        Returns:
            Optional[ic.Principal]: the ID of the subnet that contains the canister, or `None` if the canister does not exist
        """
        payload = {"canister_id": base64.b64encode(canister_id.bytes).decode()}
        res = self._instance_post("read/get_subnet", payload)
        if res:
            b = base64.b64decode(res["subnet_id"])
            return ic.Principal(b)
        return None

    def check_canister_exists(self, canister_id: ic.Principal) -> bool:
        """Check whether the provided canister exists.

        Args:
            canister_id (ic.Principal): the ID of the canister

        Returns:
            bool: `True` if the canister exists, `False` otherwise
        """
        return self.get_subnet(canister_id) is not None

    def get_cycles_balance(self, canister_id: ic.Principal) -> int:
        """Get the cycles balance of a canister.

        Args:
            canister_id (ic.Principal): the ID of the canister

        Returns:
            int: the number of cycles the canister contains
        """
        body = {"canister_id": base64.b64encode(canister_id.bytes).decode()}
        return self._instance_post("read/get_cycles", body)["cycles"]

    def add_cycles(self, canister_id: ic.Principal, amount: int) -> int:
        """Add cycles to a specific canister.

        Args:
            canister_id (ic.Principal): the ID of the canister to add cycles to
            amount (int): amount of cycles to add to the canister (single cycles, NOT trillion cycles)

        Returns:
            int: the total amount of cycles the canister holds at after adding `amount`
        """
        body = {
            "canister_id": base64.b64encode(canister_id.bytes).decode(),
            "amount": amount,
        }
        return self._instance_post("update/add_cycles", body)["cycles"]

    def get_stable_memory(self, canister_id: ic.Principal) -> bytes:
        """Gets the stable memory of a canister.

        Args:
            canister_id (ic.Principal): the ID of the canister

        Returns:
            bytes: the stable memory of the canister
        """
        body = {
            "canister_id": base64.b64encode(canister_id.bytes).decode(),
        }
        response = self._instance_post("read/get_stable_memory", body)
        return base64.b64decode(response["blob"])

    def set_stable_memory(
        self, canister_id: ic.Principal, data: bytes, compression=None
    ) -> None:
        """Sets the stable memory of a canister.

        Args:
            canister_id (ic.Principal): the ID of the canister
            data (bytes): the data to set
            compression (str, optional): optional gzip compression, defaults to `None`
        """
        blob_id = self.server.set_blob_store_entry(data, compression)
        body = {
            "canister_id": base64.b64encode(canister_id.bytes).decode(),
            "blob_id": base64.b64encode(bytes.fromhex(blob_id)).decode(),
        }

        self._instance_post("update/set_stable_memory", body)

    def update_call(
        self,
        canister_id: Optional[ic.Principal],
        method: str,
        payload: bytes,
    ) -> Any:
        """Makes an update call to a canister with the given ID. If the ID is not provided, calls the management canister.

        Args:
            canister_id (Optional[ic.Principal]): optional canister ID or `None` for management canister.
            method (str): the canister method to execute
            payload (dict): a candid encoded representation of the payload

        Returns:
            list: a list of candid objects
        """
        return self.update_call_with_effective_principal(
            canister_id, None, method, payload
        )

    def query_call(
        self,
        canister_id: Optional[ic.Principal],
        method: str,
        payload: bytes,
    ) -> Any:
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
            "sender": base64.b64encode(self.sender.bytes).decode(),
            "effective_principal": "None",
            "canister_id": base64.b64encode(canister_id.bytes).decode(),
            "method": method,
            "payload": base64.b64encode(payload).decode(),
        }

        submit_ingress_message_response = self._instance_post("read/query", body)
        return self._get_ok_data(submit_ingress_message_response)

    def create_canister(
        self,
        settings: Optional[list] = None,
        subnet: Optional[ic.Principal] = None,
        canister_id: Optional[ic.Principal] = None,
    ) -> ic.Principal:
        """Creates an empty canister.

        Args:
            settings (Optional[list], optional): optional list of settings, defaults to `None`
            subnet (Optional[ic.Principal], optional): optional subnet ID where to install the
                canister, defaults to `None`
            canister_id (Optional[ic.Principal], optional): optional canister ID of the canister
                to be created, defaults to `None`. Can only be used on Bitcoin, Fiduciary, II, SNS
                and NNS subnets

        Raises:
            ValueError: can be raised if the canister already exists, `canister_id` is
                not contained in any subnet, or if `canister_id` is on an application or
                system subnet

        Returns:
            ic.Principal: the ID of the created canister
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
                ),
                "specified_id": Types.Opt(Types.Principal),
            }
        )

        payload = [
            {
                "type": record,
                "value": {
                    "settings": [settings] if settings else [],
                    "specified_id": [canister_id.bytes] if canister_id else [],
                },
            }
        ]

        effective_principal = (
            {"SubnetId": base64.b64encode(subnet.bytes).decode()} if subnet else None
        )
        request_result = self.update_call_with_effective_principal(
            None,
            effective_principal,
            "provisional_create_canister_with_cycles",
            ic.encode(payload),
        )
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

        effective_principal = {
            "CanisterId": base64.b64encode(canister_id.bytes).decode()
        }
        self.update_call_with_effective_principal(
            None, effective_principal, "install_code", ic.encode(payload)
        )

    def create_and_install_canister_with_candid(
        self,
        candid: str,
        wasm_module: bytes,
        init_args: Optional[dict] = None,
        subnet: Optional[ic.Principal] = None,
    ) -> ic.Canister:
        """Creates a canister, charges it with 2T cycles and installs the provided WASM with the given init arguments.
        Returns a canister object. For an example on how to use the canister object,
        see `/examples/ledger_canister/ledger_canister_test.py`.

        Args:
            candid (str): a valid candid file describing the canister interface
            wasm_module (bytes): the canister wasm as bytes
            init_args (Optional[dict], optional): the init args as required by the candid file, defaults to `None`
            subnet (Optional[ic.Principal], optional): optional subnet ID where to install the
                canister, defaults to `None`

        Raises:
            ValueError: can be raised on invalid candid files

        Returns:
            ic.Canister: the canister object
        """
        canister_id = self.create_canister(subnet=subnet)
        canister = ic.Canister(self, canister_id, candid)

        canister_arguments = canister.actor["arguments"]
        if len(canister_arguments) == 0:
            arg = []
        elif len(canister_arguments) == 1:
            arg = [{"type": canister_arguments[0], "value": init_args}]
        else:
            raise ValueError("The candid file appears to be malformed")

        self.add_cycles(canister_id, 2_000_000_000_000)
        self.install_code(canister_id, wasm_module, arg)
        return canister

    def update_call_with_effective_principal(
        self,
        canister_id: Optional[ic.Principal],
        effective_principal: Optional[dict],
        method: str,
        payload: bytes,
    ):
        """Make an update call with the effective principal specified.

        Args:
            canister_id (Optional[ic.Principal]): canister ID of the canister to call. If
                `None`, calls the management canister.
            effective_principal (Optional[dict]): the effective principal to use. Either
                specify {"CanisterId": ...} or {"SubnetId": ...}, where the IDs are base64
                encoded, or `None`.
            method (str): the method to call
            payload (bytes): the candid encoded payload"""

        canister_id = canister_id if canister_id else ic.Principal.management_canister()
        effective_principal = effective_principal if effective_principal else "None"
        body = {
            "sender": base64.b64encode(self.sender.bytes).decode(),
            "effective_principal": effective_principal,
            "canister_id": base64.b64encode(canister_id.bytes).decode(),
            "method": method,
            "payload": base64.b64encode(payload).decode(),
        }

        submit_ingress_message = self._instance_post(
            "update/submit_ingress_message", body
        )
        ok = self._get_ok(submit_ingress_message)
        result = self._instance_post("update/await_ingress_message", ok)
        return self._get_ok_data(result)

    def _get_ok(self, request_result):
        if "Ok" in request_result:
            return request_result["Ok"]
        if "Err" in request_result:
            err = request_result["Err"]
            reject_code = err["reject_code"]
            reject_message = err["reject_message"]
            error_code = err["error_code"]
            msg = f"PocketIC returned a rejection error: reject code {reject_code}, reject message {reject_message}, error code {error_code}"
            raise ValueError(msg)
        raise ValueError(f"Malformed response: {request_result}")

    def _get_ok_data(self, request_result):
        result = self._get_ok(request_result)
        maybe_candid = base64.b64decode(result)
        # if we have a non-candid byte array, return that without decoding
        if maybe_candid.startswith(b"DIDL"):
            return maybe_candid
        return list(maybe_candid)

    def _instance_get(self, endpoint):
        """HTTP get requests for instance endpoints"""
        return self.server.instance_get(endpoint, self.instance_id)

    def _instance_post(self, endpoint, body):
        """HTTP post requests for instance endpoints"""
        return self.server.instance_post(endpoint, self.instance_id, body)

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
