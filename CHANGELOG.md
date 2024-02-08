# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## 2.1.0 - 2024-02-8

### Added
- Added support for PocketIC server version 3.0.0
- Added with_nns_state to create an instance from existing NNS state


## 2.0.2 - 2024-01-25

### Fixed
- Fixed a bug in `create_and_install_canister_with_candid()` on application subnets by adding 2T cycles to the 
canister before installing a Wasm


## 2.0.1 - 2023-11-23

### Added
- Support for PocketIC server version 2.0.1

### Changed
- When the PocketIC binary is not found, the error now points to the PocketIC repo instead of the download link


## 2.0.0 - 2023-11-21

### Added
- Support for multiple subnets
- Support for cross-subnet canister calls
- Ability to mute the server's stdout/stderr streams by setting the `POCKET_IC_MUTE_SERVER` environment variable
- `__del__` method for PocketIC such that it gets collected automatically
- New `.topology` field returning a map of subnet IDs to subnet configurations
- New `get_subnet()` method to get the subnet of a canister
- new `update_call_with_effective_principal()` method to call a canister with an effective principal
- New class `SubnetConfig`
- New class `SubnetKind` to specify different kinds ob subnets

### Changed
- `create_canister()` takes optional parameters to specify a subnet ID or a desired canister ID
- constructor `PocketIC(subnet_config)` with a new optional `SubnetConfig` to create a PocketIC instance with a specified subnet topology
- new implementation for `get_root_key()`

### Removed
- `delete()` method, superseded by `__del__`


## 1.0.1 - 2023-10-13

### Fixed
- Fixed broken links on PyPi


## 1.0.0 - 2023-10-12

### Added
- Blocking REST-API: Encode IC-call in endpoint, not in body

## 0.1.0 - 2023-09-01

### Added
- Initial PocketIC Python release
