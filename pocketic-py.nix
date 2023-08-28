{ lib, buildPythonPackage, hatchling, ic-py, requests, pocket-ic }:

buildPythonPackage rec {
  pname = "pocketic";
  version = "0.0.0";
  format = "pyproject";

  src = lib.cleanSourceWith {
    name = "pocketic-py-src";
    src = ./.;
    # Filter out files not needed by the Python package:
    filter = path: _type:
      ! (lib.hasSuffix ".nix" path ||
        lib.hasSuffix ".lock" path ||
        lib.hasSuffix ".envrc" path ||
        lib.hasSuffix ".github" path ||
        lib.hasSuffix ".gitignore" path);
  };

  nativeBuildInputs = [
    hatchling
  ];

  propagatedBuildInputs = [
    ic-py
    requests
    pocket-ic
  ];

  pythonImportsCheck = [
    "pocket_ic"
  ];

  meta = {
    homepage = "https://github.com/dfinity/pocketic-py";
    description = "A Pocket IC canister testing library for Python";
    license = lib.licenses.asl20;
  };
}
