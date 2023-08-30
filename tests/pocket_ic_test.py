# pylint: disable=locally-disabled, missing-module-docstring, missing-class-docstring, missing-function-docstring, wrong-import-position

import sys
import os
import unittest
import ic
import time

# The test needs to have the module in its sys path, so we traverse
# up until we find the pocket_ic package.

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pocket_ic import PocketIC


class PocketICTests(unittest.TestCase):
    def setUp(self) -> None:
        # This is being run for every test independently.
        self.pic = PocketIC()
        return super().setUp()

    def tearDown(self) -> None:
        # Delete the current PocketIC instance after the test has executed.
        self.pic.delete()
        return super().tearDown()

    def test_time(self):
        self.assertEqual(
            self.pic.get_time(),
            {"secs_since_epoch": 1620328630, "nanos_since_epoch": 0},
        )
        self.assertEqual(self.pic.set_time(1704067199999999999), None)
        self.assertEqual(
            self.pic.get_time(),
            {"secs_since_epoch": 1704067199, "nanos_since_epoch": 999999999},
        )
        self.assertEqual(self.pic.advance_time(1 * 1_000_000_000), None)
        self.assertEqual(
            self.pic.get_time(),
            {"secs_since_epoch": 1704067200, "nanos_since_epoch": 999999999},
        )

    def test_delete_instance(self):
        self.assertEqual(len(self.pic.server.list_instances()), 1)
        self.pic.delete()
        self.assertEqual(len(self.pic.server.list_instances()), 0)

    def test_tick(self):
        self.assertEqual(self.pic.tick(), None)

    def test_canister_exists(self):
        canister_id = self.pic.create_canister()
        self.assertEqual(self.pic.check_canister_exists(canister_id), True)

    def test_canister_exists_negative(self):
        canister_id = ic.Principal.from_str("rwlgt-iiaaa-aaaaa-aaaaa-cai")
        self.assertEqual(self.pic.check_canister_exists(canister_id), False)

    def test_cycles_balance(self):
        canister_id = self.pic.create_canister()
        self.pic.add_cycles(canister_id, 6_666)
        self.assertEqual(self.pic.get_cycles_balance(canister_id), 6_666)


if __name__ == "__main__":
    unittest.main()
