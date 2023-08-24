import sys
import os

# the example needs to have the module in its sys path, so we traverse
# up until we find pocketic
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

import unittest
import ic as ic_py
from pocketic import PocketIC


class ICRC1Tests(unittest.TestCase):
    def setUp(self) -> None:
        # this is run for every test individually
        ic = PocketIC()

        with open("ledger.did", "r") as f:
            candid = f.read()
        init_args = {
            "Init": {
                "decimals": [],
                "token_symbol": "MGC",
                "transfer_fee": 0,
                "metadata": [],
                "minting_account": {
                    "owner": "i3gqp-srkaa-aaaaa-aaaap-4ai",
                    "subaccount": [],
                },
                "initial_balances": [
                    ({"owner": "ryjl3-tyaaa-aaaaa-aaaba-cai", "subaccount": []}, 88_888)
                ],
                "maximum_number_of_accounts": [],
                "accounts_overflow_trim_quantity": [],
                "fee_collector_account": [],
                "archive_options": {
                    "num_blocks_to_archive": 1,
                    "max_transactions_per_response": [],
                    "trigger_threshold": 1,
                    "max_message_size_bytes": [],
                    "cycles_for_archive_creation": [],
                    "node_max_memory_size_bytes": [],
                    "controller_id": "2vxsx-fae",
                },
                "max_memo_length": [],
                "token_name": "My great coin",
                "feature_flags": [],
            }
        }
        # cd rs/rosetta-api/icrc1/ledger ; bazel build :ledger_canister -> with open('../../../bazel-bin/rs/rosetta-api/icrc1/ledger/ledger_canister.wasm', 'rb') as f:
        with open("ledger_canister.wasm", "rb") as f:
            wasm_module = f.read()
        ledger = ic.create_canister_with_candid(candid, wasm_module, init_args)

        self.ledger = ledger
        return super().setUp()

    def test_get_name(self):
        res = self.canister.icrc1_name(None)
        print("Token name:", res)

    def test_get_decimals(self):
        res = self.canister.icrc1_symbol(None)
        print("Token symbol:", res)

    def test_get_fee(self):
        res = self.canister.icrc1_fee(None)
        print("Token fee:", res)

    def test_get_total_supply(self):
        res = self.canister.icrc1_total_supply(None)
        print("Token total supply:", res)

    def test_transfer(self):
        res = self.canister.icrc1_balance_of(
            None, {"owner": "ryjl3-tyaaa-aaaaa-aaaba-cai", "subaccount": []}
        )
        print("ryjl3-tyaaa-aaaaa-aaaba-cai has this many tokens: ", res)
        receiver = {"owner": "i3gqp-srkaa-aaaaa-aaaap-4ai", "subaccount": []}
        res = self.canister.icrc1_transfer(
            ic_py.Principal.from_str("ryjl3-tyaaa-aaaaa-aaaba-cai"),
            {
                "from_subaccount": [],
                "to": receiver,
                "amount": 42,
                "fee": [],
                "memo": [],
                "created_at_time": [],
            },
        )
        print("Transfer result:", res)
        res = self.canister.icrc1_balance_of(
            None, {"owner": "ryjl3-tyaaa-aaaaa-aaaba-cai", "subaccount": []}
        )
        print(
            "ryjl3-tyaaa-aaaaa-aaaba-cai has this many tokens after sending 42: ", res
        )

    def test_get_transactions(self):
        receiver = {"owner": "i3gqp-srkaa-aaaaa-aaaap-4ai", "subaccount": []}
        res = self.canister.icrc1_transfer(
            ic_py.Principal.from_str("ryjl3-tyaaa-aaaaa-aaaba-cai"),
            {
                "from_subaccount": [],
                "to": receiver,
                "amount": 42,
                "fee": [],
                "memo": [],
                "created_at_time": [],
            },
        )
        res = self.canister.get_transactions(None, {"start": 0, "length": 10})
        print("Transaction list:", res)

    def test_get_balance_of(self):
        res = self.canister.icrc1_balance_of(
            None, {"owner": "ryjl3-tyaaa-aaaaa-aaaba-cai", "subaccount": []}
        )
        print("ryjl3-tyaaa-aaaaa-aaaba-cai has this many tokens: ", res)

    # def test_get_balance_of_legacy(self):
    #     args = [{'type': Account, 'value':
    #                 {
    #                     "owner": ic_py.Principal.from_str('ryjl3-tyaaa-aaaaa-aaaba-cai').bytes,
    #                     "subaccount": []
    #                 }
    #             }]
    #     res = self.ic.canister_query_call(self.sender, self.canister_id, 'icrc1_balance_of', args)
    #     print('Balance', self.extract_value(res))


if __name__ == "__main__":
    unittest.main()
