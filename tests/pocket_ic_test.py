# pylint: disable=locally-disabled, missing-module-docstring, missing-class-docstring, missing-function-docstring, wrong-import-position

import sys
import os
import unittest

# The test needs to have the module in its sys path, so we traverse
# up until we find PocketIC.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pocket_ic import PocketIC


class PocketICTests(unittest.TestCase):
    def setUp(self) -> None:
        # This is being run for every test independently.
        self.pic = PocketIC()
        return super().setUp()

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

    def test_tick(self):
        self.assertEqual(self.pic._tick(), None)


if __name__ == "__main__":
    unittest.main()
