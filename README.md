# PocketIC: A Canister Testing Platform

PocketIC is a local canister testing platform for the [Internet Computer](https://internetcomputer.org/).  
It consists of the PocketIC **binary**, which handles different IC instances, and a **Python library** (this repo) which allows you to interact with your local IC instances and the canisters thereon. 

With PocketIC, you can test your canisters with just a few lines of Python code, either by interacting with an IC instance:

```python
from pocket_ic import PocketIC

pic = PocketIC()
canister_id = pic.create_canister()

# use PocketIC to interact with your canisters
pic.add_cycles(canister_id, 1_000_000)
response = pic.update_call(canister_id, method="greeting", ...)
assert(response == 'Hello, PocketIC!')
```
... or even directly with a canister object:
```python
my_canister = pic.create_and_install_canister_with_candid(...)
# call your canister functions with native Python syntax
respone = my_canister.greeting()
assert(response == 'Hello, PocketIC!')
```

## Getting Started

### Quickstart
* Download the **PocketIC binary** for [Linux](https://download.dfinity.systems/ic/307d5847c1d2fe1f5e19181c7d0fcec23f4658b3/openssl-static-binaries/x86_64-linux/pocket-ic.gz) or [macOS](https://download.dfinity.systems/ic/307d5847c1d2fe1f5e19181c7d0fcec23f4658b3/openssl-static-binaries/x86_64-darwin/pocket-ic.gz), unzip and make it executable.
* Leave the binary in your current working directory, or specify an alternative path with the `POCKET_IC_BIN` environment variable.
* Run `python3 -m pip install pocket_ic` in your (virtual) environment to get the Python library. 
* Use `from pocket_ic import PocketIC` in your Python code and start testing!

For a more detailed installation guide, see [INSTALLATION.md](INSTALLATION.md).

### Examples

To see some working code, see the [examples](examples/) folder, or check out the [how to use this library](HOWTO.md) guide.
To run an example, clone this repo and run `python3 examples/counter_canister/counter_canister_test.py` from the repository's root directory.

## Documentation
* [Why PocketIC](WHY.md)
* [How to use this library](HOWTO.md)


## Contributing
See [CONTRIBUTING.md](CONTRIBUTING.md)

