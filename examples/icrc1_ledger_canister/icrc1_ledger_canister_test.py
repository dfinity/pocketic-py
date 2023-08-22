import unittest
import ic as ic_py
from src.pocket_ic import PocketIC

class ICRC1Tests(unittest.TestCase):
    def setUp(self) -> None:
        # this is run for every test individually
        ic = PocketIC()
        sender = ic_py.Principal.anonymous()
        canister_id = ic.create_canister(sender)
        # cd rs/rosetta-api/icrc1/ledger ; bazel build :ledger_canister
        # with open('../../../bazel-bin/rs/rosetta-api/icrc1/ledger/ledger_canister.wasm', 'rb') as f:
        with open('ledger_canister.wasm', 'rb') as f:
            wasm_module = f.read()
        ic.install_icrc1_ledger_canister(None, canister_id, bytes(wasm_module))

        self.ic = ic
        self.sender = sender
        self.ledger_canister_id = canister_id
        return super().setUp()
    
    def test_get_name(self):
        res = self.ic.canister_query_call(self.sender, self.ledger_canister_id, 'icrc1_name', [])
        print('Token name:', self.extract_value(res))

    def test_get_decimals(self):
        res = self.ic.canister_query_call(self.sender, self.ledger_canister_id, 'icrc1_symbol', [])
        print('Token symbol:', self.extract_value(res))

    def test_get_fee(self):
        res = self.ic.canister_query_call(self.sender, self.ledger_canister_id, 'icrc1_fee', [])
        print('Token fee:', self.extract_value(res))

    def test_get_total_supply(self):
        res = self.ic.canister_query_call(self.sender, self.ledger_canister_id, 'icrc1_total_supply', [])
        print('Token total supply:', self.extract_value(res))

    def extract_value(self, res):
        r = res['Ok']['Reply']
        candid = ic_py.decode(bytes(r))
        return candid[0]['value']



if __name__ == "__main__":
    unittest.main()
