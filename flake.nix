{
  description = "PocketIC Python Library";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    pocket-ic-darwin-gz = {
      url = "https://github.com/dfinity/pocketic/releases/download/7.0.0/pocket-ic-x86_64-darwin.gz";
      flake = false;
    };
    pocket-ic-linux-gz = {
      url = "https://github.com/dfinity/pocketic/releases/download/7.0.0/pocket-ic-x86_64-linux.gz";
      flake = false;
    };
  };

  outputs = { self, nixpkgs, flake-utils, pocket-ic-darwin-gz, pocket-ic-linux-gz }:
    flake-utils.lib.eachSystem [ "aarch64-darwin" "x86_64-darwin" "x86_64-linux" ] (system:
      let
        pkgs = import nixpkgs { inherit system; };

        # PocketIC server binary:
        pocket-ic = pkgs.callPackage ./pocket-ic.nix {
          inherit pocket-ic-darwin-gz pocket-ic-linux-gz;
        };

        projectDir =
          # Filter out files not needed by the Python library:
          pkgs.lib.cleanSourceWith {
            name = "pocketic-py-src";
            src = ./.;
            filter = path: _type:
              ! (pkgs.lib.hasSuffix ".nix" path ||
                pkgs.lib.hasSuffix "flake.lock" path ||
                pkgs.lib.hasSuffix ".envrc" path ||
                pkgs.lib.hasSuffix ".github" path ||
                pkgs.lib.hasSuffix ".gitignore" path);
          };

        # PocketIC Python library. Since we use poetry to specify our
        # Python dependencies we use poetry2nix to translate the
        # pyproject.toml and poetry.lock files to a set of Nix
        # derivations, one for each dependency.
        pocketic-py = pkgs.poetry2nix.mkPoetryApplication {
          inherit projectDir;
          # Some dependencies of our library need some tweaks
          # to get them to build so we override them here.
          # Also see: https://github.com/nix-community/poetry2nix/blob/master/docs/edgecases.md
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
                # The following packages depend on setuptools which is
                # not automatically detected by poetry2nix so we
                # override them to add setuptools manually:
                waiter = addSetuptools prev.waiter;
                ic-py = addSetuptools prev.ic-py;
              });
          # The following lets the library depend on the binary.
          propagatedBuildInputs = [ pocket-ic ];
        };

        pytest = pkgs.python3Packages.pytest;
      in
      {
        packages.default = pocketic-py;

        packages.pocket-ic = pocket-ic;

        packages.dist = pkgs.runCommand "pocketic-py-dist" {
          nativeBuildInputs = [ pkgs.poetry ];
          inherit projectDir;
        } ''
          export HOME="$TMP"
          cp -r $projectDir/* .
          poetry build
          mv dist $out
        '';

        checks.default = pkgs.runCommand "pocketic-py-tests" {
          nativeBuildInputs = [ pytest pocketic-py pkgs.cacert];
          POCKET_IC_BIN = "${pocket-ic}/bin/pocket-ic";
          inherit projectDir;
        } ''
          pytest --override-ini=cache_dir=$TMP $projectDir | tee $out
        '';

        devShells.default = pkgs.mkShell {
          packages = [
            pkgs.poetry
            pocketic-py
            pytest
          ];
        };

        # so that we can format .nix code using: nix fmt
        formatter = pkgs.nixpkgs-fmt;
      }
    );
}
