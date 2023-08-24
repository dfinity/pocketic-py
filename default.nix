let
  pkgs = import <nixpkgs> {};

  env = (pkgs.python311.withPackages (ps: with ps; [
    pylint
    build
    ic-py==1.0.1
    requests==2.31.0

  ]));

  mypython = pkgs.python3.override {
    self = mypython;
    packageOverrides = pself: psuper: {
      pocketic = pself.callPackage ./pocketic.nix {};
    };
  };
in  
{
    linter = pkgs.runCommand "linter" {
        src = ./.;
        nativeBuildInputs = [
            env
        ];
    } ''
        HOME=$TMP pylint --recursive yes $src
        touch $out
    '';

    inherit mypython;
}
