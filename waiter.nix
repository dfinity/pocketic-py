{ lib, buildPythonPackage, fetchPypi, setuptools, wheel, multimethod }:

buildPythonPackage rec {
  pname = "waiter";
  version = "1.3";
  format = "pyproject";

  src = fetchPypi {
    inherit pname version;
    hash = "sha256-duXqMsVXtTQmixV/aNjDNErgc7nwnPlgvcVRWeUH0/8=";
  };

  nativeBuildInputs = [
    setuptools
    wheel
  ];

  propagatedBuildInputs = [
    multimethod
  ];

  meta = {
    homepage = "https://github.com/coady/waite";
    description = "Delayed iteration for polling and retries.";
    license = lib.licenses.asl20;
  };
}
