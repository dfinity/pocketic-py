"""
This module contains `SubnetConfig` and `SubnetKind`, which are used to configure the
subnets of a PocketIC instance.
"""

from enum import Enum
import os


class SubnetKind(Enum):
    """The kind of subnet."""

    APPLICATION = "Application"
    BITCOIN = "Bitcoin"
    FIDUCIARY = "Fiduciary"
    II = "II"
    NNS = "NNS"
    SNS = "SNS"
    SYSTEM = "System"
    VERIFIED_APPLICATION = "VerifiedApplication"


class SubnetConfig:
    """The configuration of subnets for a PocketIC instance.

    `state_dir`:
        Use `state_dir=<empty_dir>` to store the state of the subnets in a given directory.
        This directory can be used later with `state_dir=<dir>` to load a previous state.
        Note that the provided path must be accessible for the PocketIC server process.
    """

    def __init__(
        self,
        application=0,
        bitcoin=False,
        fiduciary=False,
        ii=False,
        nns=False,
        sns=False,
        system=0,
        verified_application=0,
        state_dir: str | None = None,
    ) -> None:
        new = {"state_config": "New", "instruction_config": "Production"}
        self.application = [new] * application
        self.bitcoin = new if bitcoin else None
        self.fiduciary = new if fiduciary else None
        self.ii = new if ii else None
        self.nns = new if nns else None
        self.sns = new if sns else None
        self.system = [new] * system
        self.verified_application = [new] * verified_application
        self.state_dir = state_dir

    def __repr__(self) -> str:
        return f"SubnetConfigSet(application={self.application}, bitcoin={self.bitcoin}, fiduciary={self.fiduciary}, ii={self.ii}, nns={self.nns}, sns={self.sns}, system={self.system}, verified_application={self.verified_application})"

    def validate(self) -> None:
        """Validates the subnet configuration.

        Raises:
            ValueError: if no subnet and no state dir is configured
        """
        if not (
            self.bitcoin
            or self.fiduciary
            or self.ii
            or self.nns
            or self.sns
            or self.system
            or self.application
            or self.verified_application
            or len(os.listdir(self.state_dir)) != 0
        ):
            raise ValueError(
                "At least one subnet or a non-empty state directory must be configured."
            )

    def add_subnet_with_state(self, subnet_type: SubnetKind, state_dir_path: str):
        """Add a single subnet with state loaded form the given state directory.
        Note that the provided path must be accessible for the PocketIC server process.

        `state_dir` should point to a directory which is expected to have the following structure:

        state_dir/
         |-- backups
         |-- checkpoints
         |-- diverged_checkpoints
         |-- diverged_state_markers
         |-- fs_tmp
         |-- page_deltas
         |-- states_metadata.pbuf
         |-- tip
         |-- tmp
        """

        new_from_path = {
            "state_config": {"FromPath": state_dir_path},
            "instruction_config": "Production",
        }

        match subnet_type:
            case SubnetKind.APPLICATION:
                self.application.append(new_from_path)
            case SubnetKind.BITCOIN:
                self.bitcoin = new_from_path
            case SubnetKind.FIDUCIARY:
                self.fiduciary = new_from_path
            case SubnetKind.II:
                self.ii = new_from_path
            case SubnetKind.NNS:
                self.nns = new_from_path
            case SubnetKind.SNS:
                self.sns = new_from_path
            case SubnetKind.SYSTEM:
                self.system.append(new_from_path)
            case SubnetKind.VERIFIED_APPLICATION:
                self.verified_application.append(new_from_path)

    def _json(self) -> dict:
        return {
            "subnet_config_set": {
                "application": self.application,
                "bitcoin": self.bitcoin,
                "fiduciary": self.fiduciary,
                "ii": self.ii,
                "nns": self.nns,
                "sns": self.sns,
                "system": self.system,
                "verified_application": self.verified_application,
            },
            "state_dir": self.state_dir,
            "nonmainnet_features": False,
            "log_level": None,
            "bitcoind_addr": None,
        }
