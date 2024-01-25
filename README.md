# PocketIC Python: A Canister Testing Library

[PocketIC](https://github.com/dfinity/pocketic) is a local canister testing solution for the [Internet Computer](https://internetcomputer.org/).  
This testing library works together with the **PocketIC server**, allowing you to interact with your local IC instances and the canisters thereon. 

With PocketIC Python, you can test your canisters with just a few lines of code, either by interacting with an IC instance:

```python
from pocket_ic import PocketIC

pic = PocketIC()
canister_id = pic.create_canister()
pic.add_cycles(canister_id, 2_000_000_000_000)  # 2T cycles
pic.install_code(...)

# make canister calls
response = pic.update_call(canister_id, method="greet", ...)
assert(response == 'Hello, PocketIC!')
```
... or even directly with a canister object:
```python
my_canister = pic.create_and_install_canister_with_candid(...)
# call your canister methods with native Python syntax
response = my_canister.greet()
assert(response == 'Hello, PocketIC!')
```

## Getting Started

### Quickstart
* Download the latest **PocketIC server** from the [PocketIC repo](https://github.com/dfinity/pocketic).
* Leave the binary in your current working directory, or specify the path to the binary by setting the `POCKET_IC_BIN` environment variable before running your tests.
* Run `pip3 install pocket-ic` in your (virtual) environment to get the Python library. 
* Use `from pocket_ic import PocketIC` in your Python code and start testing!

### Examples

To see some working code, see the [examples/](https://github.com/dfinity/pocketic-py/tree/main/examples) folder, or check out the [how to use this library](https://github.com/dfinity/pocketic-py/blob/main/HOWTO.md) guide.
To run an example, clone this repo and run `python3 examples/counter_canister/counter_canister_test.py` from the repository's root directory.

## Documentation
* [How to use this library](https://github.com/dfinity/pocketic-py/blob/main/HOWTO.md)
* [PocketIC repo](https://github.com/dfinity/pocketic)
* [Why PocketIC](https://github.com/dfinity/pocketic#why-pocketic)
* [Changelog of PocketIC Python](https://github.com/dfinity/pocketic-py/blob/main/CHANGELOG.md)


## Contributing
See [CONTRIBUTING.md](https://github.com/dfinity/pocketic-py/blob/main/CONTRIBUTING.md)

