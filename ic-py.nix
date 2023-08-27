{ lib, buildPythonPackage, fetchPypi, setuptools, wheel, httpx, ecdsa, cbor2, leb128, waiter, antlr4-python3-runtime, mnemonic }:

buildPythonPackage rec {
  pname = "ic-py";
  version = "1.0.1";
  format = "pyproject";

  src = fetchPypi {
    inherit pname version;
    hash = "sha256-1E0/TRJ+kozca4mOaNCKgmy0O7Gfr+bUKbr8dIONVck=";
  };

  nativeBuildInputs = [
    setuptools
    wheel
  ];

  propagatedBuildInputs = [
    httpx
    ecdsa
    cbor2
    leb128
    waiter
    antlr4-python3-runtime
    mnemonic
  ];

  pythonImportsCheck = [
    "ic"
  ];

  meta = {
    homepage = "https://github.com/rocklabs-io/ic-py";
    description = "Python Agent Library for the DFINITY Internet Computer";
    license = lib.licenses.mit;
  };
}
