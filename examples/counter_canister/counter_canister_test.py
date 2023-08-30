import sys
import os
import unittest
import ic

# The example needs to have the module in its sys path, so we traverse
# up until we find the pocket_ic package.
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(os.path.dirname(script_dir)))

from pocket_ic import PocketIC


class CounterCanisterTests(unittest.TestCase):
    def setUp(self) -> None:
        # This is being run for every test independently.
        self.pic = PocketIC()
        self.canister_id = self.pic.create_canister()
        self.pic.add_cycles(self.canister_id, 1_000_000_000_000_000_000)
        with open(os.path.join(script_dir, "counter.wasm"), "rb") as wasm_file:
            wasm_module = wasm_file.read()
        self.pic.install_code(self.canister_id, bytes(wasm_module), [])

        return super().setUp()

    def tearDown(self) -> None:
        # Delete the current PocketIC instance after the test has executed.
        self.pic.delete()
        return super().tearDown()

    def test_counter_canister(self):
        self.assertEqual(
            self.pic.update_call(self.canister_id, "read", ic.encode([])),
            [0, 0, 0, 0],
        )
        self.assertEqual(
            self.pic.update_call(self.canister_id, "write", ic.encode([])),
            [1, 0, 0, 0],
        )
        self.assertEqual(
            self.pic.update_call(self.canister_id, "write", ic.encode([])),
            [2, 0, 0, 0],
        )
        self.assertEqual(
            self.pic.update_call(self.canister_id, "read", ic.encode([])),
            [2, 0, 0, 0],
        )


if __name__ == "__main__":
    unittest.main()
