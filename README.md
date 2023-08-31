# PocketIC: A Canister Testing Platform

PocketIC is a local canister testing platform for the [Internet Computer](https://internetcomputer.org/).  
It consists of the PocketIC **binary**, which handles different IC instances, and a **Python library** (this repo) which allows you to interact with your canisters and the IC itself.

With PocketIC, you can test your canisters with just a few lines of Python code:

```python
from pocket_ic import PocketIC

pic = PocketIC()
my_canister = pic.create_and_install_canister_with_candid(...)

# call your canister functions with native Python syntax
respone = my_canister.some_canister_function()
assert(response == 'Hello, World!')
```

## Getting Started

### Quickstart
* Download the **PocketIC binary** for [Linux](https://download.dfinity.systems/ic/71adba179679a1090baa26cadcceadec311f57b3/openssl-static-binaries/x86_64-linux/pocket-ic.gz) or [macOS](https://download.dfinity.systems/ic/71adba179679a1090baa26cadcceadec311f57b3/openssl-static-binaries/x86_64-darwin/pocket-ic.gz).
* Make sure the binary is available through your `$PATH` variable; you can verify that everything works by calling `pocket-ic --help` from your terminal.
* Run `pip3 install pocketic-py` to get the Python library. 
* Use `from pocket_ic import PocketIC` in your Python code and start testing!

For a more detailed installation guide, see [INSTALLATION.md](INSTALLATION.md).

### Examples

To see some working code, see the [examples](examples/) folder, or check out the [how to use this library](HOWTO.md) guide.


## Documentation
* [Why PocketIC](WHY.md)
* [How to use this library](HOWTO.md)


## Contributing to PocketIC
See [CONTRIBUTING.md](CONTRIBUTING.md)

