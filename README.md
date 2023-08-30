# PocketIC: A Canister Testing Platform

PocketIC is a local testing platform for canisters on the [Internet Computer](https://internetcomputer.org/). 

Using PocketIC requires two components: A server and an integration library. 

The **server** is compiled as part of the build process for the Internet Computer. It runs as local HTTP server which manages IC instances. Every test may request its own, _independent_ IC instance and interact with it concurrently with other running tests. 

This PocketIC **library** provides a convenient Python frontend to interact with IC instances, while hiding the REST-API layer, the process lifetime etc. The test author simply interacts with either an IC instance:

```python
ic = PocketIC()
canister_id = ic.create_canister()
NUM_CYCLES = 1_000_000
ic.add_cycles(canister_id, NUM_CYCLES)
assert(ic.get_cycles_balance(canister_id) == NUM_CYCLES)
```

...or even directly with a canister object:

```python
ic = PocketIC()
# Create a canister obj with the provided candid interface.
counter_canister = ic.create_and_install_canister_with_candid(..., <candid_file>)  
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

or download a .whl file from the [releases](https://github.com/dfinity/pocketic-py/releases) and call

```python3 -m pip install <file>.whl```

## Why use PocketIC?

Canister developers have several options to test their software, but there are tradeoffs: 
- Install and test on the **mainnet**: The 'real' experience, but you pay with real cycles.
- The **replica** provided by DFX: You get the complete stack of a single IC node. But therefore, you get no cross- or multisubnet functionality, and never will. Replica is quite heavyweight too, because the nonessential components are not abstracted away. 
- **`StateMachine`** test: More lightweight than replica, because it *simulates* a subnet. But it launches a process for every test, it uses difficult-to-trace stdio-IPC, and it is only integrated with Rust. 

Enter **PocketIC**: 
- Built from mainnet components and based on the `StateMachine`
- Lightweight: Abstracts away consensus and other nonessential components
- Runs as a service on your test system, and accepts HTTP/JSON. This enables:
    - Concurrent and independent IC instances by default - sharing is *possible*
    - Multi-language support: Anyone can write an integration library against the PocketIC REST-API in any language
    - [Will support sharing of setup work between similar tests]
- [Will support saving and loading checkpoints]
- [Will support multi-subnet IC instances]

## How to use this library

For concrete, working code, see [examples/](https://github.com/dfinity/pocketic-py/tree/main/examples).

This section assumes the following: 
- You have written a canister for the Internet Computer, in any language
    - You have a .wasm file ready, and possibly a .did (candid) file
- You want to write integration tests for your canister(s)
- You have followed the installation instructions 

### Using PocketIC without a test framework

It is straightforward to use PocketIC in a script or in the Python REPL. In a REPL session, the PocketIC server may shut down on you if it does not receive requests often enough to bump its time to live. We may add a launch mode to alleviate this. 

For scripts, you should know that whenever you run the `PocketIC()` constructor, the following happens:
- If no running PocketIC server is found, a new one is started. For one test *process*, there is only ever one running PocketIC server at a time. Most python test frameworks run in a single process. 
- When the PocketIC server has been launched or discovered, the `PocketIC()` constructor requests a new instance. This instance is bound to the `PocketIC` object you get. 

The `PocketIC`'s interface closely resembles that of the [`StateMachine`](https://github.com/dfinity/test-state-machine-client), which itself is of course derived from the Internet Computer interface. 

You may share that `PocketIC` instance in your script however you like, and you may create as many instances as you need. However, it is often prudent to limit the scope of resources. One way to achieve this is the [unittest framework](#using-python-unittest). 

### Using Python unittest 

We can use Python's unittest package to group similar test cases into classes which inherit from `unittest.TestCase`. Thus, we can define unittest's `setUp` and `tearDown` functions. **These will be run before and after *every* test method of the class!** So we benefit the most if we define a `setUp` to build up an initial state for as many test cases as possible. 

In this example, we `setUp` by simply installing the canister. Individual test methods will only rely on the canister being installed, and continue from there:

```python
import unittest

class MyCanTest(unittest.TestCase):
    # Runs for every test independently.
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

---

Using the IC interface to create and call canisters is familiar to canister developers and resembles the real IC interface. 

However, due to Python's ease of reflection and the work of [RocketLab](https://github.com/rocklabs-io/ic-py), we offer a more convenient way to interact with your canisters. For this feature to work, you need a candid file which describes your canister's interface. 

```python
from pocket_ic import PocketIC

WASM_PATH = "./counter.wasm"
CANDID_PATH = "./counter.did"

candid = open(CANDID_PATH, "r", encoding="utf-8").read()
wasm = open(WASM_PATH, "r", encoding="utf-8").read()

# Some canisters require init_args for code installation. 
# These need to be candid encoded. See examples/ledger_canister/.
# For the counter canister, we can do without.
init_args = dict()

ic = PocketIC()
# Create a canister obj with the provided candid interface.
counter_canister = ic.create_and_install_canister_with_candid(candid, wasm, init_args)  
# The canister's candid specifies and `inc` method with no arguments, so we can just call it:
counter_canister.inc()  
# Similarly for a function called `read`, which returns a Nat:
assert(counter_canister.read() == 1) 
```

If you need help with candid-encoding your `init_args`, canister call arguments and responses, check out the (inofficial) [Python-agent](https://github.com/rocklabs-io/ic-py), which offers some useful candid functionality.


### Using pytest
Coming soon



