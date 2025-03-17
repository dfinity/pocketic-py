# How to use this Library

For concrete, working code, see [examples/](https://github.com/dfinity/pocketic-py/tree/main/examples).

This section assumes the following: 
- You have written a canister for the Internet Computer, in any language
    - You have a .wasm file ready, and possibly a .did (candid) file
- You want to write integration tests for your canister(s)
- You have followed the installation instructions 

## Using PocketIC Without a Testing Framework

It is straightforward to use PocketIC in a script or in the Python REPL. In a REPL session, the PocketIC server may shut down on you if it does not receive requests often enough to bump its time to live. In the future, we may add a keepalive launch mode to alleviate this. 

For scripts, you should know that whenever you run the `PocketIC()` constructor, the following happens:
- If no running PocketIC server is found, a new one is started. For one test *process*, there is only ever one running PocketIC server at a time. Most Python test frameworks run in a single process. 
- When the PocketIC server has been launched or discovered, the `PocketIC()` constructor requests a new instance. This instance is bound to the `PocketIC` object you get. 

The `PocketIC`'s interface closely resembles that of the [`StateMachine`](https://github.com/dfinity/test-state-machine-client), which itself is of course derived from the Internet Computer interface. 

You may share that `PocketIC` instance in your script however you like, and you may create as many instances as you need. However, it is often prudent to limit the scope of resources. One way to achieve this is the [unittest framework](#using-python-unittest). 

### Using Python `unittest`

We can use Python's unittest package to group similar test cases into classes which inherit from `unittest.TestCase`. Thus, we can define unittest's `setUp` and `tearDown` functions. **These will be run before and after *every* test method of the class!** So we benefit the most if we define a `setUp` to build up an initial state for as many test cases as possible. 

An alternative way is to use `setUpClass` and `tearDownClass` which are run once per class. In this case, all test methods share the IC instance(s) defined in `setUpClass`. 

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

## Using the Canister Interface 

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

If you need help with candid-encoding your `init_args`, canister call arguments and responses, check out the community developed [Python-agent](https://github.com/rocklabs-io/ic-py), which offers some useful candid functionality.

## Live Mode

PocketIC instances do not "make progress" by default, i.e., they do not execute any messages and time does not advance unless dedicated operations are triggered by separate requests. The "live" mode enabled by calling the function `PocketIC.make_live()` automates those steps by:

- Setting the current time as the PocketIC instance time
- Advancing time on the PocketIC instance regularly
- Creating an HTTP gateway that exposes the ICP's HTTP interface

This is particularly useful when you want to:
1. Test your canister with standard IC agents (like the JavaScript or Rust agents)
2. Test long-running processes that require time to advance automatically
3. Simulate a more realistic environment where messages are processed continuously

Here's how to use the live mode:

```python
from pocket_ic import PocketIC, SubnetConfig

# Create a PocketIC instance with NNS subnet (required for HTTP gateway functionality)
# The HTTP gateway requires an NNS subnet to function properly
pic = PocketIC(subnet_config=SubnetConfig(application=1, nns=True))

# Create a canister
canister_id = pic.create_canister()
pic.add_cycles(canister_id, 2_000_000_000_000)  # 2T cycles
pic.install_code(canister_id, wasm_module, [])

# Enable live mode - this creates an HTTP gateway and enables auto progress
# You can optionally specify a port to listen on: pic.make_live(listen_at=8000)
url = pic.make_live()

print(f"PocketIC instance is accessible at: {url}")

# Now you can interact with your canister using standard IC agents
# For example, using the JavaScript agent:
# agent = new HttpAgent({ host: url });
# agent.fetchRootKey();  # Only needed for local development
# const actor = Actor.createActor(idlFactory, { agent, canisterId });
# const result = await actor.greet();

# When done, stop live mode
pic.stop_live()
```

The `make_live()` function returns a URL that can be used to interact with the PocketIC instance using standard IC agents. This URL is also stored as the `gateway_url` attribute on the PocketIC instance.

If you call `make_live()` multiple times on the same PocketIC instance, it will return the same URL without creating a new HTTP gateway.

To stop the live mode, call `stop_live()`. This will stop the automatic time updates and round executions, and shut down the HTTP gateway.
