import sys
import os
import unittest
import ic

# The example needs to have the module in its sys path, so we traverse
# up until we find the pocket_ic package.
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(os.path.dirname(script_dir)))

from pocket_ic import PocketIC, SubnetConfig

# This test suite is for testing inter-canister calls between a caller canister and a counter canister.

# Note: The inter-canister-calls example take from https://github.com/dfinity/examples/tree/master/rust/inter-canister-calls

class InterCanisterCallsTest(unittest.TestCase):
    def setUp(self) -> None:
        # This is run for every test individually.
        # We create a new PocketIC with a single NNS subnet.
        self.pic = PocketIC(SubnetConfig(nns=True))

        with open(
            os.path.join(script_dir, "caller.did"), "r", encoding="utf-8"
        ) as candid_file:
            candid = candid_file.read()

        with open(os.path.join(script_dir, "caller.wasm"), "rb") as wasm_file:
            wasm_module = wasm_file.read()

        # Install the caller canister on the NNS subnet.
        self.caller: ic.Canister = self.pic.create_and_install_canister_with_candid(
            candid, bytes(wasm_module)
        )

        with open(
            os.path.join(script_dir, "counter.did"), "r", encoding="utf-8"
        ) as candid_file:
            candid = candid_file.read()

        with open(os.path.join(script_dir, "counter.wasm"), "rb") as wasm_file:
            wasm_module = wasm_file.read()

        # Install the counter canister on the NNS subnet.
        self.counter: ic.Canister = self.pic.create_and_install_canister_with_candid(
            candid, bytes(wasm_module)
        )

        return super().setUp()

    def test_call_get_and_set(self):
        # Test setting the counter to a new value and getting the old value
        new_value = 42
        old_value = self.caller.call_get_and_set(self.counter.canister_id.to_str(), new_value)
        self.assertEqual(old_value, [0])  # Assuming the initial value is 0

    def test_set_then_get(self):
        # Test setting the counter and then getting the current value
        new_value = 7
        self.caller.set_then_get(self.counter.canister_id.to_str(), new_value)
        current_value = self.counter.get()
        self.assertEqual(current_value, [7])

    def test_call_increment(self):
        self.caller.set_then_get(self.counter.canister_id.to_str(), 7)
        # Test incrementing the counter
        self.caller.call_increment(self.counter.canister_id.to_str())
        current_value = self.counter.get()
        # Assuming the previous value was 7
        self.assertEqual(current_value, [8])  

    def test_call_get(self):
        self.caller.set_then_get(self.counter.canister_id.to_str(), 7)
        self.caller.call_increment(self.counter.canister_id.to_str())

        # Test getting the current counter value
        current_value = self.caller.call_get(self.counter.canister_id.to_str())
        # Assuming the previous value was 8
        self.assertEqual(current_value, [{'Ok':8}])

    def test_stubborn_set(self):
        # Test setting the counter value with retries
        new_value = 42
        result = self.caller.stubborn_set(self.counter.canister_id.to_str(), new_value)
        self.assertEqual(result[0], {'Ok':None})
        current_value = self.counter.get()
        self.assertEqual(current_value, [42])

if __name__ == "__main__":
    unittest.main()
