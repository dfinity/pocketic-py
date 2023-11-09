# pylint: disable=locally-disabled, missing-module-docstring, missing-class-docstring, missing-function-docstring, wrong-import-position

import sys
import os
import unittest
import ic
import gzip

# The test needs to have the module in its sys path, so we traverse
# up until we find the pocket_ic package.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pocket_ic import PocketIC, SubnetKind, NNS, STANDARD


class PocketICTests(unittest.TestCase):
    def test_multiple_nns_subnets_are_deduplicated(self):
        subnet_config = [NNS, NNS]
        pic = PocketIC(subnet_config)
        self.assertEqual(len(pic.topology), 1)

    def test_install_canister_on_subnet_and_get_subnet_of_canister(self):
        subnet_config = [NNS, STANDARD]
        pic = PocketIC(subnet_config)
        nns_subnet = next(
            k for k, v in pic.topology.items() if v.subnet_kind == SubnetKind.NNS
        )
        app_subnet = next(
            k
            for k, v in pic.topology.items()
            if v.subnet_kind == SubnetKind.APPLICATION
        )
        nns_canister = pic.create_canister(subnet=nns_subnet)
        app_canister = pic.create_canister(subnet=app_subnet)

        self.assertEqual(
            pic.get_subnet_of_canister(nns_canister).bytes, nns_subnet.bytes
        )
        self.assertEqual(
            pic.get_subnet_of_canister(app_canister).bytes, app_subnet.bytes
        )

    def test_set_get_stable_memory_no_compression(self):
        pic = PocketIC()
        canister_id = pic.create_canister()
        pic.install_code(canister_id, b"\x00\x61\x73\x6d\x01\x00\x00\x00", [])

        data = b"This will be stored in stable memory."
        pic.set_stable_memory(canister_id, data)
        memory = pic.get_stable_memory(canister_id)[: len(data)]
        self.assertEqual(memory, data)

    def test_set_get_stable_memory_with_compression(self):
        pic = PocketIC()
        canister_id = pic.create_canister()
        pic.install_code(canister_id, b"\x00\x61\x73\x6d\x01\x00\x00\x00", [])

        text = b"This will be compressed and sent, the server will decompress it."
        compressed = gzip.compress(text)

        pic.set_stable_memory(canister_id, compressed, compression="gzip")
        memory = pic.get_stable_memory(canister_id)[: len(text)]
        self.assertEqual(memory, text)

    def test_time(self):
        pic = PocketIC()
        pic.set_time(1704067199999999999)
        self.assertEqual(
            pic.get_time(),
            {"nanos_since_epoch": 1704067199999999999},
        )
        pic.advance_time(1_000_000_000)
        self.assertEqual(
            pic.get_time(),
            {"nanos_since_epoch": 1704067200999999999},
        )

    def test_delete_instance(self):
        pic = PocketIC()
        server = pic.server
        initial_num = server.list_instances().count("Deleted")
        del pic
        self.assertEqual(server.list_instances().count("Deleted"), initial_num + 1)

    def test_tick(self):
        pic = PocketIC()
        self.assertEqual(pic.tick(), None)

    def test_get_root_key(self):
        pic = PocketIC([STANDARD])
        self.assertTrue(pic.get_root_key() is None)

        pic = PocketIC([NNS, STANDARD])
        self.assertTrue(pic.get_root_key() is not None)

    def test_canister_exists(self):
        pic = PocketIC()
        canister_id = pic.create_canister()
        self.assertEqual(pic.check_canister_exists(canister_id), True)

    def test_canister_exists_negative(self):
        pic = PocketIC()
        canister_id = ic.Principal.anonymous()
        self.assertEqual(pic.check_canister_exists(canister_id), False)

    def test_cycles_balance(self):
        pic = PocketIC()
        canister_id = pic.create_canister()
        initial_balance = pic.get_cycles_balance(canister_id)
        pic.add_cycles(canister_id, 6_666)
        self.assertEqual(pic.get_cycles_balance(canister_id), initial_balance + 6_666)


if __name__ == "__main__":
    unittest.main()
