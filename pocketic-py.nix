{ lib, buildPythonPackage, hatchling, ic-py, requests, pocket-ic }:

buildPythonPackage rec {
  pname = "pocketic";
  version = "0.0.1";
  format = "pyproject";

  src = ./.;

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
    license = lib.licenses.bsd3;
  };
}
