# Installation

## PocketIC Binary

Download the latest stable PocketIC binary from the URL below:

**Linux:**   
https://download.dfinity.systems/ic/71adba179679a1090baa26cadcceadec311f57b3/openssl-static-binaries/x86_64-linux/pocket-ic.gz

**macOS**:  
https://download.dfinity.systems/ic/71adba179679a1090baa26cadcceadec311f57b3/openssl-static-binaries/x86_64-darwin/pocket-ic.gz

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

You can test that everything is working by running `pocket-ic --help` from any folder;
PocketIC should start and display its help message.

## PocketIC Library (this repo)

This library is on PyPi, so you can install it using pip. For example, from your virtualenv:

```python3 -m pip install pocketic-py```

or download a .whl file from the [releases](https://github.com/dfinity/pocketic-py/releases) and call

```python3 -m pip install <file>.whl```