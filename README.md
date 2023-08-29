# PocketIC: A Canister Testing Platform

PocketIC is a local testing platform for canisters on the [Internet Computer](https://internetcomputer.org/). 

Using PocketIC requires two components: A server and an integration library. 

The **server** is compiled as part of the build process for the Internet Computer. It runs as local HTTP server which manages IC instances. Every test may request its own, _independent_ IC instance and interact with it concurrently with other running tests. 

This PocketIC **library** provides a convenient Python frontend to interact with IC instances, while hiding the REST-API layer, the process lifetime etc. The test author simply interacts with either an IC instance:

```python
ic = PocketIC()
assert(ic.get_root_key() == MAINNET_ROOTKEY)
```

...or even directly with a canister object:

```python
ic = PocketIC()
# Create a canister obj with the provided candid interface.
counter_canister = ic.create_and_install_canister_with_candid(...)  
counter_canister.inc()  
assert(counter_canister.read() == 1) 
```

For more detailed examples, see the section [below](#how-to-use-this-library) and the [examples](https://github.com/dfinity/pocketic-py/tree/main/examples).

## Installation

### PocketIC Binary

Download the latest stable PocketIC binary from the URL below:

Linux:  
`https://download.dfinity.systems/ic/80bcca3b3e9e79bd07af2747e9cffb0e50c6b868/openssl-static-binaries/x86_64-linux/pocket-ic.gz`

MacOS:  
`https://download.dfinity.systems/ic/80bcca3b3e9e79bd07af2747e9cffb0e50c6b868/openssl-static-binaries/x86_64-darwin/pocket-ic.gz`

Copy the binary to your preferred location, unpack it, make it executable and put it on the path. E.g.,
 
```bash
mkdir ~/opt
curl <url> --output ~/opt/pocket-ic.gz
gunzip ~/opt/pocket-ic.gz
chmod +x ~/opt/pocket-ic
export PATH="${HOME}/opt:${PATH}"
```

You can also add the last line to your `~/.bashrc` or `~/.zshrc`.

On macOS, run 

```bash
xattr -dr com.apple.quarantine pocket-ic
```

in the directory where you have placed the binary file.
This step is needed to bypass the developer verification from Apple, and only needs to be run once.
Alternatively, you can open the `pocket-ic` binary by right clicking on it in the Finder and selecting "Open" from the drop-down menu.
Then, confirm opening this application by clicking "Open" again in the dialog that opened.

You can test that everything is working by calling `pocket-ic` from any folder;
PocketIC should start and tell you that you're missing the a required argument.

### PocketIC Testing Library (this repository)

This library is on PyPi, so you can install it using pip. For example, from your virtualenv:

```python3 -m pip install pocketic-py```

or get a .whl file from the [releases](https://github.com/dfinity/pocketic-py/releases) and call

```python3 -m pip install <file>.whl```

## Why use PocketIC?

Canister developers have several options to test their software, but there are tradeoffs: 
- Install and test on the **mainnet**: The 'real' experience, but you pay with real cycles.
- The **replica** provided by DFX: You get the complete stack of a single IC node. But therefore, you get no cross- or multisubnet functionality, and never will. Replica is quite heavyweight too, because the nonessential components are not abstracted away. 
- **StateMachine** test: More lightweight than replica, because it *simulates* a subnet. But it launches a process for every test, it uses difficult-to-trace stdio-IPC, and it is only integrated with Rust. 

Enter **PocketIC**: 
- Built from mainnet components
- Lightweight: Abstracts away consensus and other nonessential components
- Runs as a service on your test system, and accepts HTTP/JSON. This enables:
    - Concurrent and independent IC instances
    - Multi-language support: Anyone can write an integration library against the PocketIC REST-API in any language
    - [Will support sharing of setup work between similar tests]
- [Will support saving and loading checkpoints]
- [Will support multi-subnet IC instances]

## How to use this library

This section assumes the following: 
- You have written a canister for the Internet Computer, in any language
    - You have a .wasm file ready, and possibly a .did (candid) file
- You want to write integration tests for your canister(s)
- You have followed the installation instructions 

### Using python unittest 

We use Python's unittest package to group similar test cases into classes which inherit from `unittest.TestCase`. Thus, we can define unittest's `setUp` and `tearDown` functions. **These will be run before and after *every* test method of the class!**. So we benefit the most if we define a `setUp` to build up an initial state for as many test cases as possible. 

In this example, we `setUp` by simply installing the canister. Individual test methods will only rely on the canister being installed, and continue from there:

```python
import unittest

class MyCanTest(unittest.TestCase):
    # Run for every test independently.
    def setUp(self):
        # Create a PocketIC instance. This will also launch a PocketIC server, 
        # if none is running yet.
        # We bind to self, so that methods can access this object.
        self.pic = PocketIC()
        # Create a new, empty canister and record its canister id.
        self.canister_id = self.pic.create_canister()
        self.pic.add_cycles(self.canister_id, 1_000_000_000_000_000_000)
        with open("counter.wasm", "rb") as wasm_file:
            wasm_module = wasm_file.read()
        # Install the actual wasm code in the empty canister.
        self.pic.install_code(self.canister_id, bytes(wasm_module), [])

    # This tests one aspect of the canister. Its initial state is the state after `setUp`. 
    def test_one(self):
        result = self.pic.update_call(self.canister_id, "read", ic.encode([]))
        self.assertEqual(result, [0, 0, 0, 0])
    
    # This tests another aspect of the canister. Its initial state is the state after `setUp`. 
    def test_two(self): 
        pass  # etc
    
```

When this example is run, the following events happen in this order: 
- `test_one` invokes `setUp`
    - `setUp` finds no running PocketIC server instance, so it launches one and discovers its port
    - The `PocketIC()` constructor requests a new instance from the PocketIC server
    - The server returns an instance id to the constructor, which completes and binds to `self.pic`
    - `setUp` completes
- `test_one` completes
- `test_two` invokes `setUp`
    - `setUp` finds a running PocketIC server instance and discovers its port
    - ... (continues like above, overwriting all `self.*` fields, and using a new, independent IC instance)
- etc.
- After the PocketIC server is idle for a while (30s), it shuts down.

TODO: Canister interface example

For more, see [examples/](https://github.com/dfinity/pocketic-py/tree/main/examples).
### Using pytest
Coming soon

### Using PocketIC without a test framework
Coming soon

