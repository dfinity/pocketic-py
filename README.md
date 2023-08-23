# Pocket-IC: A canister testing platform

Pocket-IC is a local testing platform for canisters on the [Internet Computer](https://internetcomputer.org/). 

Pocket-IC has two components: A binary and a library. 

The **binary** is built as part of the build process for the Internet Computer. When you run the binary, you have a local server on which you can create and manipulate IC instances via a REST-API. Typically, every testcase requests its own IC instance and runs its requests in parallel to and independent of other IC instances. The server is capable of serving many concurrent tests, i.e., independent IC instances. 

This Pocket-IC **library** provides a Python frontend to communicate with the Pocket-IC server via REST-API. While you could use the REST-API directly, this library provides the following conveniences: 

- Server startup and teardown, port negotiation, ...
- Synchronous instance API
- Candid type conversion (due to [ic-py](https://github.com/rocklabs-io/ic-py))
- ...
## Installation

The latest stable Pocket-IC server can be downloaded from the URL below: 

`https://TODO<>/<>`

Copy the binary to your preferred location, make it executable and put it on the path. 


```bash title="Linux"
curl <url> --output ~/opt/pocket-ic-backend
chmod +x ~/opt/pocket-ic-backend
export PATH="${HOME}/opt:${PATH}"
```



## How to use this library



See examples/
