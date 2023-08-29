{ stdenv, lib, pocket-ic-darwin-gz, pocket-ic-linux-gz }:
stdenv.mkDerivation {
  name = "pocket-ic";
  pocket_ic_gz =
    if stdenv.isDarwin
    then pocket-ic-darwin-gz
    else pocket-ic-linux-gz;
  unpackPhase = ''
    mkdir -p $out/bin
    gunzip < $pocket_ic_gz > $out/bin/pocket-ic
    chmod +x $out/bin/pocket-ic
  '';
  preFixup =
    lib.optionalString (!stdenv.isDarwin)
      (
        let
          libPath = lib.makeLibraryPath [
            stdenv.cc.cc.lib # libstdc++.so.6
          ];
        in
        ''
          patchelf \
            --set-interpreter "$(cat $NIX_CC/nix-support/dynamic-linker)" \
            --set-rpath "${libPath}" \
            $out/bin/pocket-ic
        ''
      );
  doInstallCheck = true;
  preInstallCheck = ''
    $out/bin/pocket-ic --help
  '';
}
