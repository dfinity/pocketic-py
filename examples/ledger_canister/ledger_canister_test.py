import sys
import os
import unittest
import ic

# The example needs to have the module in its sys path, so we traverse
# up until we find the pocket_ic package.
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(os.path.dirname(script_dir)))

from pocket_ic import PocketIC


class LedgerCanisterTests(unittest.TestCase):
    def setUp(self) -> None:
        # This is run for every test individually.
        self.pic = PocketIC()
        self.principal_a = ic.Principal.from_str("2222s-4iaaa-aaaaf-ax2uq-cai")
        self.principal_b = ic.Principal.from_str("zzyfr-6yaaa-aaaar-aklsa-cai")
        self.principal_minting = ic.Principal.from_str("i3gqp-srkaa-aaaaa-aaaap-4ai")

        with open(
            os.path.join(script_dir, "ledger.did"), "r", encoding="utf-8"
        ) as candid_file:
            candid = candid_file.read()

        init_args = {
            "Init": {
                "decimals": [],
                "token_symbol": "MYTOKEN",
                "transfer_fee": 0,
                "metadata": [],
                "minting_account": {
                    "owner": self.principal_minting.to_str(),
                    "subaccount": [],
                },
                "initial_balances": [
                    ({"owner": self.principal_a.to_str(), "subaccount": []}, 666),
                    ({"owner": self.principal_b.to_str(), "subaccount": []}, 420),
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
                "token_name": "My Token",
                "feature_flags": [],
            }
        }
        with open(os.path.join(script_dir, "ledger_canister.wasm"), "rb") as wasm_file:
            wasm_module = wasm_file.read()

        self.ledger: ic.Canister = self.pic.create_and_install_canister_with_candid(
            candid, wasm_module, init_args
        )
        return super().setUp()

    def tearDown(self) -> None:
        # Delete the current PocketIC instance after the test has executed.
        self.pic.delete()
        return super().tearDown()

    def test_get_name(self):
        res = self.ledger.icrc1_name()
        self.assertEqual(res, ["My Token"])

    def test_get_decimals(self):
        res = self.ledger.icrc1_symbol()
        self.assertEqual(res, ["MYTOKEN"])

    def test_get_fee(self):
        res = self.ledger.icrc1_fee()
        self.assertEqual(res, [0])

    def test_get_total_supply(self):
        res = self.ledger.icrc1_total_supply()
        self.assertEqual(res, [666 + 420])

    def test_get_transactions(self):
        self.pic.set_sender(self.principal_a)

        receiver = {"owner": self.principal_b.to_str(), "subaccount": []}
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

        self.pic.set_anonymous_sender()

        res = self.ledger.get_transactions({"start": 0, "length": 10})
        self.assertEqual(len(res[0]["archived_transactions"]), 1)

    def test_transfer(self):
        self.pic.set_sender(self.principal_a)

        receiver = {"owner": self.principal_b.to_str(), "subaccount": []}
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
        self.assertTrue("Ok" in res[0])

        self.pic.set_anonymous_sender()

        res = self.ledger.icrc1_balance_of(
            {"owner": self.principal_a.to_str(), "subaccount": []}
        )
        self.assertEqual(res, [666 - 42])
        res = self.ledger.icrc1_balance_of(
            {"owner": self.principal_b.to_str(), "subaccount": []}
        )
        self.assertEqual(res, [420 + 42])

    def test_get_balance_of(self):
        res = self.ledger.icrc1_balance_of(
            {"owner": self.principal_a.to_str(), "subaccount": []}
        )
        self.assertEqual(res, [666])


if __name__ == "__main__":
    unittest.main()
