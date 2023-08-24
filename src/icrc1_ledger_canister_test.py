import unittest
import ic
from pocket_ic import PocketIC


class ICRC1Tests(unittest.TestCase):
    def setUp(self) -> None:
        # this is run for every test individually
        pic = PocketIC()

        with open("ledger.did", "r") as candid_file:
            candid = candid_file.read()
        init_args = {
            "Init": {
                "decimals": [],
                "token_symbol": "MAT",
                "transfer_fee": 0,
                "metadata": [],
                "minting_account": {
                    "owner": "i3gqp-srkaa-aaaaa-aaaap-4ai",
                    "subaccount": [],
                },
                "initial_balances": [
                    ({"owner": "ryjl3-tyaaa-aaaaa-aaaba-cai", "subaccount": []}, 666)
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
                "token_name": "My Awesome Token",
                "feature_flags": [],
            }
        }
        with open("ledger_canister.wasm", "rb") as wasm_file:
            wasm_module = wasm_file.read()

        ledger = pic.create_canister_with_candid(candid, wasm_module, init_args)
        self.pic = pic
        self.ledger = ledger
        return super().setUp()

    def test_get_name(self):
        res = self.ledger.icrc1_name()
        self.assertEqual(res, ["My Awesome Token"])

    def test_get_decimals(self):
        res = self.ledger.icrc1_symbol()
        self.assertEqual(res, ["MAT"])

    def test_get_fee(self):
        res = self.ledger.icrc1_fee()
        self.assertEqual(res, [0])

    def test_get_total_supply(self):
        res = self.ledger.icrc1_total_supply()
        self.assertEqual(res, [666])

    def test_transfer(self):
        res = self.ledger.icrc1_balance_of(
            {"owner": "ryjl3-tyaaa-aaaaa-aaaba-cai", "subaccount": []}
        )
        self.assertEqual(res, [666])

        self.pic.set_sender(ic.Principal.from_str("ryjl3-tyaaa-aaaaa-aaaba-cai"))

        receiver = {"owner": "i3gqp-srkaa-aaaaa-aaaap-4ai", "subaccount": []}
        res = self.ledger.icrc1_transfer(
            {
                "from_subaccount": [],
                "to": receiver,
                "amount": 42,
                "fee": [],
                "memo": [],
                "created_at_time": [],
            },
        )
        self.assertEqual(res, [{"Ok": 1}])

        self.pic.anonymous_sender()

        res = self.ledger.icrc1_balance_of(
            {"owner": "ryjl3-tyaaa-aaaaa-aaaba-cai", "subaccount": []}
        )
        self.assertEqual(res, [666 - 42])

    def test_get_transactions(self):
        self.pic.set_sender(ic.Principal.from_str("ryjl3-tyaaa-aaaaa-aaaba-cai"))

        receiver = {"owner": "i3gqp-srkaa-aaaaa-aaaap-4ai", "subaccount": []}
        res = self.ledger.icrc1_transfer(
            {
                "from_subaccount": [],
                "to": receiver,
                "amount": 42,
                "fee": [],
                "memo": [],
                "created_at_time": [],
            },
        )

        self.pic.anonymous_sender()

        res = self.ledger.get_transactions({"start": 0, "length": 10})
        self.assertEqual(len(res[0]["archived_transactions"]), 1)

    def test_get_balance_of(self):
        res = self.ledger.icrc1_balance_of(
            {"owner": "ryjl3-tyaaa-aaaaa-aaaba-cai", "subaccount": []}
        )
        self.assertEqual(res, [666])


if __name__ == "__main__":
    unittest.main()
