# Why use PocketIC?

Canister developers have several options to test their software, but there are tradeoffs: 
- Install and test on the **mainnet**: The 'real' experience, but you pay with real cycles.
- The **replica** provided by DFX: You get the complete stack of a single IC node. But therefore, you get no cross- or multisubnet functionality, and likely never will. Replica is quite heavyweight too, because the nonessential components are not abstracted away. 
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
