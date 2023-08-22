import unittest
import ic as ic_py
from pocket_ic import PocketIC
from canister import Canister
from ic.candid import Types


Account = Types.Record({'owner': Types.Principal, 'subaccount': Types.Opt(Types.Vec(Types.Nat8))})
FeatureFlags = Types.Record({'icrc2': Types.Bool})
ArchiveOptions = Types.Record({
    'trigger_threshold': Types.Nat64,
    'num_blocks_to_archive': Types.Nat64,
    'node_max_memory_size_bytes': Types.Opt(Types.Nat64),
    'max_message_size_bytes': Types.Opt(Types.Nat64),
    'controller_id': Types.Principal,
    'cycles_for_archive_creation': Types.Opt(Types.Nat64),
    'max_transactions_per_response': Types.Opt(Types.Nat64)
})
MetadataValue = Types.Variant({'Nat': Types.Nat, 'Int': Types.Int, 'Text': Types.Text, 'Blob': Types.Vec(Types.Nat8)})
ChangeFeeCollector = Types.Variant({'Unset': Types.Null, 'SetTo': Account})
UpgradeArgs = Types.Record({
    'metadata': Types.Opt(Types.Vec(Types.Tuple(Types.Text, MetadataValue))),
    'token_name': Types.Opt(Types.Text),
    'token_symbol': Types.Opt(Types.Text),
    'transfer_fee': Types.Opt(Types.Nat),
    'change_fee_collector': Types.Opt(ChangeFeeCollector),
    'max_memo_length': Types.Opt(Types.Nat16),
    'feature_flags': Types.Opt(FeatureFlags),
    'maximum_number_of_accounts': Types.Opt(Types.Nat64),
    'accounts_overflow_trim_quantity': Types.Opt(Types.Nat64)

})
InitArgs = Types.Record({
    'minting_account': Account,
    'fee_collector_account': Types.Opt(Account),
    'initial_balances': Types.Vec(Types.Tuple(Account, Types.Nat)),
    'transfer_fee': Types.Nat,
    'decimals': Types.Opt(Types.Nat8),
    'token_name': Types.Text,
    'token_symbol': Types.Text,
    'metadata': Types.Vec(Types.Tuple(Types.Text, MetadataValue)),
    'archive_options': ArchiveOptions,
    'max_memo_length': Types.Opt(Types.Nat16),
    'feature_flags': Types.Opt(FeatureFlags),
    'maximum_number_of_accounts': Types.Opt(Types.Nat64),
    'accounts_overflow_trim_quantity': Types.Opt(Types.Nat64)
})
LedgerArg = Types.Variant({'Init': InitArgs, 'Upgrade': Types.Opt(UpgradeArgs)})

args = [{"type": LedgerArg,  "value": {
            "Init": {
                "decimals": [],
                "token_symbol": "MGC",
                "transfer_fee": 0,
                "metadata": [],
                "minting_account": {
                    "owner": ic_py.Principal.from_str('i3gqp-srkaa-aaaaa-aaaap-4ai').bytes,
                    "subaccount": []
                },
                "initial_balances": [
                    (
                        {
                            "owner": ic_py.Principal.from_str('ryjl3-tyaaa-aaaaa-aaaba-cai').bytes,
                            "subaccount": []
                        },
                        88_888
                    )
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
                    "controller_id": ic_py.Principal.from_str('2vxsx-fae').bytes
                },
                "max_memo_length": [],
                "token_name": "My great coin",
                "feature_flags": []
            }
        }}]
# bbs = bytes([68, 73, 68, 76, 24, 107, 2, 252, 184, 139, 132, 3, 1, 176, 206, 209, 132, 3, 18, 110, 2, 108, 9, 158, 254, 185, 164, 3, 3, 242, 199, 148, 174, 3, 4, 239, 206, 231, 128, 4, 5, 151, 170, 189, 187, 6, 10, 132, 132, 213, 192, 7, 10, 133, 241, 153, 244, 7, 11, 176, 215, 195, 146, 11, 15, 145, 201, 170, 254, 13, 3, 190, 163, 209, 195, 15, 16, 110, 113, 110, 125, 110, 6, 109, 7, 108, 2, 0, 113, 1, 8, 107, 4, 207, 137, 223, 1, 124, 193, 137, 238, 1, 125, 253, 210, 201, 223, 2, 9, 205, 241, 203, 190, 3, 113, 109, 123, 110, 120, 110, 12, 107, 2, 157, 131, 244, 106, 13, 201, 197, 241, 208, 3, 127, 108, 2, 179, 176, 218, 195, 3, 104, 173, 134, 202, 131, 5, 14, 110, 9, 110, 122, 110, 17, 108, 1, 199, 191, 231, 182, 11, 126, 108, 13, 194, 149, 169, 147, 1, 19, 158, 254, 185, 164, 3, 113, 242, 199, 148, 174, 3, 125, 239, 206, 231, 128, 4, 6, 174, 203, 235, 136, 4, 13, 178, 164, 218, 178, 5, 20, 151, 170, 189, 187, 6, 10, 132, 132, 213, 192, 7, 10, 130, 186, 190, 130, 8, 22, 161, 229, 247, 161, 10, 23, 176, 215, 195, 146, 11, 15, 145, 201, 170, 254, 13, 113, 190, 163, 209, 195, 15, 16, 110, 123, 109, 21, 108, 2, 0, 13, 1, 125, 110, 13, 108, 7, 158, 165, 129, 210, 1, 120, 178, 167, 194, 210, 3, 10, 164, 149, 165, 233, 6, 120, 224, 171, 134, 239, 8, 10, 228, 216, 204, 232, 11, 10, 147, 200, 230, 199, 12, 10, 222, 197, 216, 174, 14, 104, 1, 0, 1, 0, 3, 83, 84, 75, 144, 78, 0, 1, 10, 42, 0, 0, 0, 0, 0, 0, 0, 254, 1, 0, 1, 1, 10, 0, 0, 0, 0, 0, 0, 0, 2, 1, 1, 0, 128, 173, 226, 4, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 4, 0, 9, 83, 78, 83, 32, 84, 111, 107, 101, 110, 0])
# print('raw', ic.decode(bbs))
# print('raw with names and types', ic.decode(bbs, LedgerArg))

class ICRC1Tests(unittest.TestCase):
    def setUp(self) -> None:
        # this is run for every test individually
        ic = PocketIC()
        sender = ic_py.Principal.anonymous()
        canister_id = ic.create_canister(sender)
        
        with open('ledger.did', 'r') as f:
            candid = f.read()

        self.ledger_canister = Canister(ic, canister_id, candid)

        type_ = self.ledger_canister.actor['arguments'][0]
        value = {
            "Init": {
                "decimals": [],
                "token_symbol": "MGC",
                "transfer_fee": 0,
                "metadata": [],
                "minting_account": {
                    "owner": 'i3gqp-srkaa-aaaaa-aaaap-4ai',
                    "subaccount": []
                },
                "initial_balances": [
                    (
                        {
                            "owner": 'ryjl3-tyaaa-aaaaa-aaaba-cai',
                            "subaccount": []
                        },
                        88_888
                    )
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
                    "controller_id": '2vxsx-fae'
                },
                "max_memo_length": [],
                "token_name": "My great coin",
                "feature_flags": []
            }
        }
        
        arg = [{'type': type_, 'value': value}]
        # cd rs/rosetta-api/icrc1/ledger ; bazel build :ledger_canister
        # with open('../../../bazel-bin/rs/rosetta-api/icrc1/ledger/ledger_canister.wasm', 'rb') as f:
        with open('ledger_canister.wasm', 'rb') as f:
            wasm_module = f.read()
        
        ic.install_canister(None, canister_id, bytes(wasm_module), arg)

        return super().setUp()
    
    
    def test_get_name(self):
        res = self.ledger_canister.icrc1_name(None)
        print('Token name:', res)

    def test_get_decimals(self):
        res = self.ledger_canister.icrc1_symbol(None)
        print('Token symbol:', res)

    def test_get_fee(self):
        res = self.ledger_canister.icrc1_fee(None)
        print('Token fee:', res)

    def test_get_total_supply(self):
        res = self.ledger_canister.icrc1_total_supply(None)
        print('Token total supply:', res)

    def test_transfer(self):
        res = self.ledger_canister.icrc1_balance_of(None,
            {
                'owner': 'ryjl3-tyaaa-aaaaa-aaaba-cai',
                'subaccount': []
            }
        )
        print('ryjl3-tyaaa-aaaaa-aaaba-cai has this many tokens: ', res)
        receiver = {
            'owner': 'i3gqp-srkaa-aaaaa-aaaap-4ai',
            'subaccount': []
        }
        res = self.ledger_canister.icrc1_transfer(ic_py.Principal.from_str('ryjl3-tyaaa-aaaaa-aaaba-cai'),
            {
                'from_subaccount': [],
                'to': receiver,
                'amount': 42,
                'fee': [],
                'memo': [],
                'created_at_time': []
            }
        )
        print(res)
        res = self.ledger_canister.icrc1_balance_of(None, 
            {
                'owner': 'ryjl3-tyaaa-aaaaa-aaaba-cai',
                'subaccount': []
            }
        )
        print('ryjl3-tyaaa-aaaaa-aaaba-cai has this many tokens after sending 42: ', res)

    def test_get_transactions(self):
        receiver = {
            'owner': 'i3gqp-srkaa-aaaaa-aaaap-4ai',
            'subaccount': []
        }
        res = self.ledger_canister.icrc1_transfer(ic_py.Principal.from_str('ryjl3-tyaaa-aaaaa-aaaba-cai'),
            {
                'from_subaccount': [],
                'to': receiver,
                'amount': 42,
                'fee': [],
                'memo': [],
                'created_at_time': []
            }
        )   
        res = self.ledger_canister.get_transactions(None,
            {
                'start': 0,
                'length': 10
            }
        )
        print(res)

    def test_get_balance_of(self):
        res = self.ledger_canister.icrc1_balance_of(None,
            {
                'owner': 'ryjl3-tyaaa-aaaaa-aaaba-cai',
                'subaccount': []
            }
        )
        print('ryjl3-tyaaa-aaaaa-aaaba-cai has this many tokens: ', res)

    # def test_get_balance_of_legacy(self):
    #     args = [{'type': Account, 'value': 
    #                 {
    #                     "owner": ic_py.Principal.from_str('ryjl3-tyaaa-aaaaa-aaaba-cai').bytes,
    #                     "subaccount": []
    #                 }
    #             }]
    #     res = self.ic.canister_query_call(self.sender, self.ledger_canister_id, 'icrc1_balance_of', args)
    #     print('Balance', self.extract_value(res))


if __name__ == "__main__":
    unittest.main()
