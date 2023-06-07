{
  description = "farbenfroh - web app for faerber";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    poetry2nix = {
      url = "github:nix-community/poetry2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    pre-commit-hooks.url = "github:cachix/pre-commit-hooks.nix";
    pre-commit-hooks.inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs = {
    self,
    flake-utils,
    nixpkgs,
    poetry2nix,
    pre-commit-hooks,
  }:
    flake-utils.lib.eachDefaultSystem
    (
      system: let
        pkgs = nixpkgs.legacyPackages.${system};
        inherit (poetry2nix.legacyPackages.${system}) mkPoetryApplication;
      in {
        packages = rec {
          catppuccin-cogs = mkPoetryApplication {
            # pname = "catppuccin-cogs";
            # src = ./.;
            # projectDir = ./.;
            # python = pkgs.python311;
            # doCheck = false;
            projectDir = self;
          };
          default = catppuccin-cogs;
        };

        devShells.default = pkgs.mkShell {
          packages = [
            poetry2nix.packages.${system}.poetry
          ];
        };

        checks = {
          pre-commit-check = pre-commit-hooks.lib.${system}.run {
            src = ./.;
            hooks = {
              black.enable = true;
              isort.enable = true;
            };
          };
        };
      }
    );
}
