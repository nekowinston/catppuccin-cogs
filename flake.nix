{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    poetry2nix = {
      url = "github:nix-community/poetry2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    pre-commit-hooks = {
      url = "github:cachix/pre-commit-hooks.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = {
    self,
    nixpkgs,
    flake-utils,
    poetry2nix,
    pre-commit-hooks,
  }:
    flake-utils.lib.eachDefaultSystem
    (
      system: let
        pkgs = nixpkgs.legacyPackages.${system};
      in {
        packages.default = pkgs.poetry2nix.mkPoetryApplication {
          projectDir = ./.;
          python = pkgs.python310;
          overrides = pkgs.poetry2nix.overrides.withDefaults (final: prev: {
            attrs = prev.pkgs.python3Packages.buildPythonPackage {
              pname = "attrs";
              version = "23.1.0";
              src = prev.pkgs.fetchurl {
                url = "https://files.pythonhosted.org/packages/f0/eb/fcb708c7bf5056045e9e98f62b93bd7467eb718b0202e7698eb11d66416c/attrs-23.1.0-py3-none-any.whl";
                sha256 = "012x6glahfkg28ncs726dcnbm76gib3j1861d8jv8byw5i9b8a0z";
              };
              format = "wheel";
              doCheck = false;
            };

            red-commons = prev.pkgs.python3Packages.buildPythonPackage {
              pname = "Red-Commons";
              version = "1.0.0";
              src = prev.pkgs.fetchurl {
                url = "https://files.pythonhosted.org/packages/39/7a/4afb80e4aa69fec9736159d2571db76e3546c6e3b4e8deefe0e55114526c/red_commons-1.0.0-py3-none-any.whl";
                sha256 = "0i5g4p5p5na27064x5vlh96iq85i1a0n12rzw2lckqp8pw5bf1vh";
              };
              format = "wheel";
              doCheck = false;
            };

            orjson = prev.orjson.override (old: {
              preferWheel = false;
              cargoDeps = old.cargoDeps.overrideAttrs (_: {
                hash = "sha256-OAF1qyHLy8c1o7FNKMwzuumq1bA7x1mFzSAS/Ml7M34=";
              });
            });
          });
        };

        devShells.default = pkgs.mkShell {
          inherit (self.checks.${system}.pre-commit-check) shellHook;
          packages = [
            poetry2nix.packages.${system}.poetry
          ];
        };

        checks = {
          pre-commit-check = pre-commit-hooks.lib.${system}.run {
            src = ./.;
            hooks.black.enable = true;
            hooks.isort.enable = true;
            hooks.pyright.enable = true;
          };
        };
      }
    );
}
