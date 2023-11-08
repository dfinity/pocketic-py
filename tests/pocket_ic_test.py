# pylint: disable=locally-disabled, missing-module-docstring, missing-class-docstring, missing-function-docstring, wrong-import-position

import sys
import os
import unittest
import ic
import gzip

# The test needs to have the module in its sys path, so we traverse
# up until we find the pocket_ic package.

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pocket_ic import PocketIC, NNS, STANDARD


class PocketICTests(unittest.TestCase):
    def setUp(self) -> None:
        # This is being run for every test independently.
        self.pic = PocketIC()
        return super().setUp()

    def tearDown(self) -> None:
        # Delete the current PocketIC instance after the test has executed.
        del self.pic
        return super().tearDown()
    
    def test_basic_multi_subnet(self):
        config = [NNS, STANDARD]
        pic = PocketIC(config)
        id = pic.create_canister()

    def test_set_get_stable_memory_no_compression(self):
        canister_id = self.pic.create_canister()
        self.pic.install_code(canister_id, b"\x00\x61\x73\x6d\x01\x00\x00\x00", [])

        data = b"This will be stored in stable memory."
        self.pic.set_stable_memory(canister_id, data)
        memory = self.pic.get_stable_memory(canister_id)[:len(data)]
        self.assertEqual(memory, data)

    def test_set_get_stable_memory_with_compression(self):
        canister_id = self.pic.create_canister()
        self.pic.install_code(canister_id, b"\x00\x61\x73\x6d\x01\x00\x00\x00", [])

        text = b"This will be compressed and sent, the server will decompress it."
        compressed = gzip.compress(text)

        self.pic.set_stable_memory(canister_id, compressed, compression="gzip")
        memory = self.pic.get_stable_memory(canister_id)[:len(text)]
        self.assertEqual(memory, text)

    def test_time(self):
        self.pic.set_time(1704067199999999999)
        self.assertEqual(
            self.pic.get_time(),
            {"nanos_since_epoch": 1704067199999999999},
        )
        self.pic.advance_time(1_000_000_000)
        self.assertEqual(
            self.pic.get_time(),
            {"nanos_since_epoch": 1704067200999999999},
        )

    def test_delete_instance(self):
        pic = PocketIC()
        server = pic.server
        initial_num = server.list_instances().count('Deleted')
        del pic
        self.assertEqual(server.list_instances().count('Deleted'), initial_num + 1)

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
        initial_balance = self.pic.get_cycles_balance(canister_id)
        self.pic.add_cycles(canister_id, 6_666)
        self.assertEqual(self.pic.get_cycles_balance(canister_id), initial_balance + 6_666)


if __name__ == "__main__":
    unittest.main()
