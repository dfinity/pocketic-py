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
* Download the **PocketIC binary** for [Linux](https://download.dfinity.systems/ic/865a816108b31956bd449282e5803ce40007789f/openssl-static-binaries/x86_64-linux/pocket-ic.gz) or [macOS](https://download.dfinity.systems/ic/865a816108b31956bd449282e5803ce40007789f/openssl-static-binaries/x86_64-darwin/pocket-ic.gz).
* Make sure the binary is available through your `$PATH` variable; you can verify that everything works by calling `pocket-ic --help` from your terminal.
* Run `python3 -m pip install pocket_ic` in your (virtual) environment to get the Python library. 
* Use `from pocket_ic import PocketIC` in your Python code and start testing!

For a more detailed installation guide, see [INSTALLATION.md](INSTALLATION.md).

### Examples

To see some working code, see the [examples](examples/) folder, or check out the [how to use this library](HOWTO.md) guide.


## Documentation
* [Why PocketIC](WHY.md)
* [How to use this library](HOWTO.md)


## Contributing
See [CONTRIBUTING.md](CONTRIBUTING.md)

