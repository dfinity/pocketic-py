# Pocket-IC: A canister testing platform

Pocket-IC is a local testing platform for canisters on the [Internet Computer](https://internetcomputer.org/). 

Pocket-IC has two components: A binary and a library. 

The **binary** is built as part of the build process for the Internet Computer. It runs a local HTTP server which manages IC instances. Every test may request its own, independent IC instance and interact with it concurrently with other running tests. 

This Pocket-IC **library** provides a convenient Python frontend to interact with IC instances, while hiding process management, REST-API calls to the server etc. The test author simply interacts with either an IC instance...

```python3
ic = PocketIC()
assert(ic.root_key() == MAINNET_ROOTKEY)
```

...or even directly with a canister object:

```python3 
ic = PocketIC()
counter_canister = ic.install_canister(...)
counter_canister.inc()
assert(counter_canister.get() == 1)
```

For more detailed examples, see the section [below](#how-to-use-this-library) and the [examples](https://github.com/dfinity/pocketic-py/tree/main/examples).

## Installation

The latest stable Pocket-IC binary can be downloaded from the URL below: 

`https://download.dfinity.systems/ic/80bcca3b3e9e79bd07af2747e9cffb0e50c6b868/openssl-static-binaries/x86_64-linux/pocket-ic.gz`

Copy the binary to your preferred location, make it executable and put it on the path. 

```bash title="Linux"
curl <url> --output ~/opt/pocket-ic-backend
chmod +x ~/opt/pocket-ic-backend
export PATH="${HOME}/opt:${PATH}"
```

This library can be found on PyPi, so you can install it using

```pip install pocketic-py```

or get a .whl file from the [releases](https://github.com/dfinity/pocketic-py/releases).

## How to use this library



See examples/
