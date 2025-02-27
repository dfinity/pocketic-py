# Contributing to PocketIC Python

We welcome contributions to the PocketIC Python library! If you have any questions or need help, please reach out to us on the [Forum](https://forum.dfinity.org/).
If you decide to contribute, we encourage you to announce it on the [Forum](https://forum.dfinity.org/)!

## Installation

Download the [PocketIC server](https://github.com/dfinity/pocketic?tab=readme-ov-file#download-the-pocketic-server) for your platform and place it in the repository root directory.

Next, set up a Python venv, activate it and install the dependencies:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Development

Running tests:
```bash
python3 tests/pocket_ic_test.py
```

Running examples:
```bash
# Ledger canister
python3 examples/ledger_canister/ledger_canister_test.py

# Counter canister
python3 examples/counter_canister/counter_canister_test.py
```
