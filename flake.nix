{
  description = "PocketIC Python Libary";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    pocket-ic-darwin-gz = {
      url = "https://download.dfinity.systems/ic/80bcca3b3e9e79bd07af2747e9cffb0e50c6b868/openssl-static-binaries/x86_64-darwin/pocket-ic.gz";
      flake = false;
    };
    pocket-ic-linux-gz = {
      url = "https://download.dfinity.systems/ic/80bcca3b3e9e79bd07af2747e9cffb0e50c6b868/openssl-static-binaries/x86_64-linux/pocket-ic.gz";
      flake = false;
    };
  };

  outputs = { self, nixpkgs, flake-utils, pocket-ic-darwin-gz, pocket-ic-linux-gz }:
    flake-utils.lib.eachSystem [ "aarch64-darwin" "x86_64-darwin" "x86_64-linux" ] (system:
      let
        pkgs = import nixpkgs { inherit system; };

        pocket-ic = pkgs.callPackage ./pocket-ic.nix {
          inherit pocket-ic-darwin-gz pocket-ic-linux-gz;
        };

        overrides = pkgs.poetry2nix.defaultPoetryOverrides.extend
          (_final: prev:
            let
              addSetuptools = drv:
                drv.overridePythonAttrs
                  (
                    old: {
                      buildInputs = (old.buildInputs or [ ]) ++ [ prev.setuptools ];
                    }
                  );
            in
            {
              waiter = addSetuptools prev.waiter;
              ic-py = addSetuptools prev.ic-py;
            });

        pocketic-py = pkgs.poetry2nix.mkPoetryApplication {
          inherit projectDir overrides;
          propagatedBuildInputs = [ pocket-ic ];
        };

        projectDir = pkgs.lib.cleanSourceWith {
          name = "pocketic-py-src";
          src = ./.;
          # Filter out files not needed by the Python package:
          filter = path: _type:
            ! (pkgs.lib.hasSuffix ".nix" path ||
              pkgs.lib.hasSuffix "flake.lock" path ||
              pkgs.lib.hasSuffix ".envrc" path ||
              pkgs.lib.hasSuffix ".github" path ||
              pkgs.lib.hasSuffix ".gitignore" path);
        };

      in
      {
        packages.default = pocketic-py;

        packages.pocket-ic = pkgs.pocket-ic;

        devShells.default = pkgs.mkShell {
          packages = [
            pkgs.poetry
            pocketic-py
          ];
        };

        # so that we can format .nix code using: nix fmt
        formatter = pkgs.nixpkgs-fmt;
      }
    );
}
