import sys
import os

# the example needs to have the module in its sys path, so we traverse
# up until we find pocketic
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

import unittest
import ic
from pocket_ic import PocketIC


class CanisterTests(unittest.TestCase):
    def setUp(self) -> None:
        # this is being run for every test independently
        self.pic = PocketIC()
        return super().setUp()

    def test_counter_canister(self):
        canister_id = self.pic.create_empty_canister()

        self.assertEqual(canister_id.to_str(), "rwlgt-iiaaa-aaaaa-aaaaa-cai")
        self.assertEqual(
            self.pic.add_cycles(canister_id, 1_000_000_000_000_000_000),
            1_000_000_000_000_000_000,
        )

        with open("counter.wasm", "rb") as f:
            wasm_module = f.read()

        self.assertEqual(
            self.pic.install_canister(canister_id, bytes(wasm_module), []), []
        )

        self.assertEqual(
            self.pic.canister_update_call(canister_id, "read", ic.encode([])),
            [0, 0, 0, 0],
        )
        self.assertEqual(
            self.pic.canister_update_call(canister_id, "write", ic.encode([])),
            [1, 0, 0, 0],
        )
        self.assertEqual(
            self.pic.canister_update_call(canister_id, "write", ic.encode([])),
            [2, 0, 0, 0],
        )
        self.assertEqual(
            self.pic.canister_update_call(canister_id, "read", ic.encode([])),
            [2, 0, 0, 0],
        )


if __name__ == "__main__":
    unittest.main()
