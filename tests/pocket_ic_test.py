# pylint: disable=locally-disabled, missing-module-docstring, missing-class-docstring, missing-function-docstring, wrong-import-position

import sys
import os
import tempfile
import unittest
import ic
import gzip
import requests
import time

# The test needs to have the module in its sys path, so we traverse
# up until we find the pocket_ic package.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pocket_ic import PocketIC, SubnetKind, SubnetConfig


class PocketICTests(unittest.TestCase):
    def test_create_canister_with_id(self):
        pic = PocketIC(SubnetConfig(nns=True))
        canister_id = ic.Principal.from_str("rwlgt-iiaaa-aaaaa-aaaaa-cai")
        actual_canister_id = pic.create_canister(canister_id=canister_id)
        self.assertEqual(actual_canister_id.bytes, canister_id.bytes)

        # Creating a new canister with the same ID fails.
        with self.assertRaises(ValueError) as ex:
            pic.create_canister(canister_id=canister_id)
        self.assertIn(
            "CanisterAlreadyInstalled",
            ex.exception.args[0],
        )

        # Creating a new canister with any ID works, gets a new ID.
        new_canister_id = pic.create_canister()
        self.assertNotEqual(new_canister_id.bytes, canister_id.bytes)

        # Creating a canister with an ID that is not hosted by any subnet creates a new subnet containing the canister.
        canister_id = ic.Principal.from_str("zzztf-6qaaa-aaaah-qfsaa-cai")
        self.assertEqual(len(pic.topology()), 1)
        pic.create_canister(canister_id=canister_id)
        self.assertEqual(len(pic.topology()), 2)

    def test_large_config_and_deduplication(self):
        pic = PocketIC(
            SubnetConfig(
                application=2,
                bitcoin=True,
                fiduciary=True,
                ii=True,
                nns=True,
                sns=True,
                system=3,
            )
        )
        app_subnets = [
            k for k, v in pic.topology().items() if v == SubnetKind.APPLICATION
        ]
        self.assertEqual(len(app_subnets), 2)
        nns_subnets = [k for k, v in pic.topology().items() if v == SubnetKind.NNS]
        self.assertEqual(len(nns_subnets), 1)
        bitcoin_subnets = [
            k for k, v in pic.topology().items() if v == SubnetKind.BITCOIN
        ]
        self.assertEqual(len(bitcoin_subnets), 1)
        system_subnets = [
            k for k, v in pic.topology().items() if v == SubnetKind.SYSTEM
        ]
        self.assertEqual(len(system_subnets), 3)

    def test_install_canister_on_subnet_and_get_subnet_of_canister(self):
        pic = PocketIC(SubnetConfig(nns=True, application=1))
        nns_subnet = next(k for k, v in pic.topology().items() if v == SubnetKind.NNS)
        app_subnet = next(
            k for k, v in pic.topology().items() if v == SubnetKind.APPLICATION
        )
        nns_canister = pic.create_canister(subnet=nns_subnet)
        app_canister = pic.create_canister(subnet=app_subnet)

        self.assertEqual(pic.get_subnet(nns_canister).bytes, nns_subnet.bytes)
        self.assertEqual(pic.get_subnet(app_canister).bytes, app_subnet.bytes)

    def test_set_get_stable_memory_no_compression(self):
        pic = PocketIC()
        canister_id = pic.create_canister()
        pic.add_cycles(canister_id, 20_000_000_000_000)
        pic.install_code(canister_id, b"\x00\x61\x73\x6d\x01\x00\x00\x00", [])

        data = b"This will be stored in stable memory."
        pic.set_stable_memory(canister_id, data)
        memory = pic.get_stable_memory(canister_id)[: len(data)]
        self.assertEqual(memory, data)

    def test_set_get_stable_memory_with_compression(self):
        pic = PocketIC()
        canister_id = pic.create_canister()
        pic.add_cycles(canister_id, 20_000_000_000_000)
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
        pic = PocketIC()
        self.assertTrue(pic.get_root_key() is None)

        pic = PocketIC(SubnetConfig(nns=True))
        self.assertTrue(pic.get_root_key() is not None)

    def test_canister_exists(self):
        pic = PocketIC()
        canister_id = pic.create_canister()
        self.assertEqual(pic.check_canister_exists(canister_id), True)

    def test_canister_exists_negative(self):
        pic = PocketIC()
        canister_id = ic.Principal.anonymous()
        self.assertEqual(pic.check_canister_exists(canister_id), False)

    def test_call_empty_canister_throws(self):
        pic = PocketIC()
        canister_id = pic.create_canister()
        with self.assertRaises(ValueError) as ex:
            pic.query_call(canister_id, "foo", b"")
        self.assertIn(
            "CanisterWasmModuleNotFound",
            ex.exception.args[0],
        )

    def test_call_nonexistent_canister(self):
        pic = PocketIC()
        canister_id = ic.Principal.anonymous()
        with self.assertRaises(ConnectionError) as ex:
            pic.query_call(canister_id, "foo", b"")
        self.assertIn(
            "does not belong to any subnet",
            ex.exception.args[0],
        )

    def test_cycles_balance(self):
        pic = PocketIC()
        canister_id = pic.create_canister()
        initial_balance = pic.get_cycles_balance(canister_id)
        pic.add_cycles(canister_id, 6_666)
        self.assertEqual(pic.get_cycles_balance(canister_id), initial_balance + 6_666)

    def test_load_state(self):
        principal = ic.Principal.from_str(
            "6gvjz-uotju-2ngtj-u2ngt-ju2ng-tju2n-gtju2-ngtjv"
        )
        tmp_dir = tempfile.mkdtemp()

        config = SubnetConfig()
        config.add_subnet_with_state(SubnetKind.NNS, tmp_dir, principal)
        pic = PocketIC(subnet_config=config)

        (k, v) = list(pic.topology().items())[0]
        self.assertEqual(str(k), str(principal))
        self.assertEqual(v, SubnetKind.NNS)
        os.rmdir(tmp_dir)

    def test_http_gateway(self):
        """Test HTTP gateway with NNS subnet."""
        # Create a subnet configuration with an NNS subnet and an application subnet
        subnet_config = SubnetConfig(application=1, nns=True)
        pic = PocketIC(subnet_config=subnet_config)

        try:
            instance_url = pic.instance_url()

            # Check if root key is available (should be since we have NNS subnet)
            root_key = pic.get_root_key()
            self.assertIsNotNone(
                root_key, "Root key should be available with NNS subnet"
            )

            # Start HTTP gateway
            gateway_url = pic.start_http_gateway()

            # Test the gateway by making a request to the status endpoint
            status_url = f"{gateway_url}/api/v2/status"
            response = requests.get(status_url, timeout=5)

            self.assertEqual(
                response.status_code, 200, "HTTP gateway should return 200 status code"
            )
        finally:
            # Clean up
            pic.stop_live()

    def test_make_live(self):
        """Test that make_live creates an HTTP gateway and enables auto progress."""
        # Create a PocketIC instance with NNS subnet for HTTP gateway support
        pic = PocketIC(subnet_config=SubnetConfig(application=1, nns=True))
        try:
            # Call make_live with multiple retries
            url = None
            max_retries = 5
            last_error = None

            for i in range(max_retries):
                try:
                    url = pic.make_live()
                    break
                except Exception as e:
                    last_error = e
                    print(f"Retry {i+1}/{max_retries} failed: {str(e)}")
                    time.sleep(1)

            if url is None:
                self.fail(
                    f"Failed to make_live after {max_retries} retries. Last error: {last_error}"
                )

            # Verify that we got a valid URL
            self.assertTrue(url.startswith("http://"))

            # Only test URL accessibility if we have a gateway URL
            if hasattr(pic, "gateway_url") and "localhost" in url:
                # Verify that the URL is accessible with retries
                response = None
                for i in range(max_retries):
                    try:
                        response = requests.get(f"{url}/api/v2/status", timeout=2)
                        if response.status_code == 200:
                            break
                    except (
                        requests.exceptions.ConnectionError,
                        requests.exceptions.ReadTimeout,
                    ):
                        print(f"Connection retry {i+1}/{max_retries}")
                        time.sleep(1)

                if response is None or response.status_code != 200:
                    self.fail(
                        f"Could not connect to {url}/api/v2/status after {max_retries} retries"
                    )

            # Call make_live again and verify we get the same URL
            same_url = pic.make_live()
            self.assertEqual(url, same_url)
        finally:
            # Clean up
            pic.stop_live()

    def test_auto_progress(self):
        """Test that auto_progress enables automatic time updates."""
        # Create a PocketIC instance with NNS subnet for HTTP gateway support
        pic = PocketIC(subnet_config=SubnetConfig(application=1, nns=True))
        try:
            # Get the current time
            initial_time = pic.get_time()["nanos_since_epoch"]

            # Enable auto progress
            pic.auto_progress()

            # Wait a bit for time to advance
            time.sleep(1)

            # Get the time again
            new_time = pic.get_time()["nanos_since_epoch"]

            # Verify that time has advanced
            self.assertGreater(new_time, initial_time)
        finally:
            # Clean up if needed
            if hasattr(pic, "gateway_url"):
                pic.stop_live()

    def test_stop_live(self):
        """Test that stop_live stops the HTTP gateway and auto progress."""
        # Create a PocketIC instance with NNS subnet for HTTP gateway support
        pic = PocketIC(subnet_config=SubnetConfig(application=1, nns=True))
        try:
            # Start live mode with retries
            url = None
            max_retries = 5
            last_error = None

            for i in range(max_retries):
                try:
                    url = pic.make_live()
                    break
                except Exception as e:
                    last_error = e
                    print(f"Retry {i+1}/{max_retries} failed: {str(e)}")
                    time.sleep(1)

            if url is None:
                self.fail(
                    f"Failed to make_live after {max_retries} retries. Last error: {last_error}"
                )

            # Stop live mode
            pic.stop_live()

            # Verify that the gateway_url attribute is removed
            self.assertFalse(hasattr(pic, "gateway_url"))
        finally:
            # Make sure to clean up if test fails
            if hasattr(pic, "gateway_url"):
                pic.stop_live()


if __name__ == "__main__":
    unittest.main()
