# PocketIC: A Canister Testing Platform

PocketIC is a local testing platform for canisters on the [Internet Computer](https://internetcomputer.org/). 

PocketIC has two components: A server and an integration library. 

The **server** is built as part of the build process for the Internet Computer. It runs as local HTTP server which manages IC instances. Every test may request its own, independent IC instance and interact with it concurrently with other running tests. 

This PocketIC **library** provides a convenient Python frontend to interact with IC instances, while hiding the REST-API layer, the process lifetime etc. The test author simply interacts with either an IC instance...

```python
ic = PocketIC()
assert(ic.get_root_key() == MAINNET_ROOTKEY)
```

...or even directly with a canister object:

```python
ic = PocketIC()
counter_canister = ic.create_and_install_canister_with_candid(...)
counter_canister.inc()
assert(counter_canister.read() == 1)
```

For more detailed examples, see the section [below](#how-to-use-this-library) and the [examples](https://github.com/dfinity/pocketic-py/tree/main/examples).

## Installation

### PocketIC Binary

Download the latest stable PocketIC binary from the URL below:

Linux:
`https://download.dfinity.systems/ic/3f7ec0a56573e1e1408cb7b6fb5e6ddbb193cc7d/openssl-static-binaries/x86_64-linux/pocket-ic.gz`

MacOS:
`https://download.dfinity.systems/ic/3f7ec0a56573e1e1408cb7b6fb5e6ddbb193cc7d/openssl-static-binaries/x86_64-darwin/pocket-ic.gz`

Copy the binary to your preferred location, unpack it, make it executable and put it on the path. E.g.,
 
```bash
mkdir ~/opt
curl <url> --output ~/opt/pocket-ic.gz
gunzip ~/opt/pocket-ic.gz
chmod +x ~/opt/pocket-ic
export PATH="${HOME}/opt:${PATH}"
```

You can also add the last line to your `~/.bashrc` or `~/.zshrc`.

On macOS, run `xattr -dr com.apple.quarantine pocket-ic` in the directory where you have placed the binary file.
This step is needed to bypass the developer verification from Apple, and only needs to be run once.
Alternatively, you can open the `pocket-ic` binary by right clicking on it in the Finder and selecting "Open" from the drop-down menu.
Then, confirm opening this application by clicking "Open" again in the dialog that opened.

You can test that everything is working by calling `pocket-ic` from any folder;
PocketIC should start and tell you that you're missing the a required argument.

### PocketIC Testing Library (this)

This library is on PyPi, so you can install it using pip. For example, from your virtualenv:

```python3 -m pip install pocketic-py```

or get a .whl file from the [releases](https://github.com/dfinity/pocketic-py/releases) and call

```python3 -m pip install <file>.whl```

## How to use this library



See examples/
