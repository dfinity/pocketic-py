{
  description = "PocketIC Python Libary";

  inputs = {
    nixpkgs.url = "nixpkgs/release-23.05";
    flake-utils.url = "github:numtide/flake-utils";
    pocketic-darwin-gz = {
      url = "https://download.dfinity.systems/ic/80bcca3b3e9e79bd07af2747e9cffb0e50c6b868/openssl-static-binaries/x86_64-darwin/pocket-ic.gz";
      flake = false;
    };
    pocketic-linux-gz = {
      url = "https://download.dfinity.systems/ic/80bcca3b3e9e79bd07af2747e9cffb0e50c6b868/openssl-static-binaries/x86_64-linux/pocket-ic.gz";
      flake = false;
    };
  };

  outputs = { self, nixpkgs, flake-utils, pocketic-darwin-gz, pocketic-linux-gz }:
    flake-utils.lib.eachSystem [ "aarch64-darwin" /* "x86_64-darwin" "x86-64-linux" */ ] (system:
      let
        pkgs = import nixpkgs {
          inherit system;
          overlays = [
            (final: prev: {
              pythonPackagesExtensions = prev.pythonPackagesExtensions ++ [
                (python-final: python-prev: {
                  antlr4-python3-runtime = python-prev.antlr4-python3-runtime.override { antlr4 = final.antlr4_9; };
                  waiter = python-final.callPackage ./waiter.nix { };
                  ic-py = python-final.callPackage ./ic-py.nix { };
                  pocketic-py = python-final.callPackage ./pocketic-py.nix { };
                })
              ];
              pocket-ic = final.runCommand "pocket-ic"
                {
                  pocket_ic_gz = if final.stdenv.isDarwin then pocketic-darwin-gz else pocketic-linux-gz;
                } ''
                mkdir -p $out/bin
                gunzip < $pocket_ic_gz > $out/bin/pocket-ic
                chmod +x $out/bin/pocket-ic
                # test pocketic by running it
                $out/bin/pocket-ic --help
              '';
            })
          ];
        };
        py = pkgs.python3;

        pocketic-py = py.pkgs.pocketic-py;

        py-env = py.withPackages (ps: [
          ps.build
        ]);
      in
      {
        packages.default = pocketic-py;

        packages.pocketic-py-release = pkgs.stdenv.mkDerivation {
          name = "pocketic-py-release-${pocketic-py.version}";
          inherit (pocketic-py) src;
          nativeBuildInputs = [ py-env ];
          buildPhase = ''
            python -m build --outdir $out
          '';
        };

        devShells.default = pkgs.mkShell {
          inputsFrom = [ pocketic-py ];
        };
        # so that we can format .nix code using: nix fmt
        formatter = pkgs.nixpkgs-fmt;
      }
    );
}
