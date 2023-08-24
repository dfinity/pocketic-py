{ lib, buildPythonPackage, hatchling }:

buildPythonPackage rec {
    pname = "pocketic";
    version = "0.0.1";
    format = "pyproject";

#   src = fetchPypi {
#     inherit pname version;
#     sha256 = "08fdd5ef7c96480ad11c12d472de21acd32359996f69a5259299b540feba4560";
#   };
    src = ./.;

    nativeBuildInputs = [
        hatchling
    ];

    doCheck = false;

    meta = with lib; {
        homepage = "https://github.com/dfinity/pocketic-py";
        description = "A Pocket IC canister testing library for Python";
        license = licenses.bsd3;
        maintainers = with maintainers; [ ];
    };
}
