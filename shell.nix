with import <nixpkgs> {};

(python311.withPackages (ps: with ps; [
  pylint
])).env
